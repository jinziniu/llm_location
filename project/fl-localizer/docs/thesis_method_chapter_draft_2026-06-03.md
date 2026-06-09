# 论文方法章节草稿

日期：2026-06-03

本章描述本文提出的 selective evidence-aware LLM fault localization 方法。该方法面向文件级缺陷定位：给定 bug report、失败测试、stack trace 和 buggy source snapshot，输出最可能包含缺陷的源文件排序。方法目标不是替代检索阶段，而是在高召回候选池上用受控 evidence 和选择性 LLM rerank 改善排序质量。

## 3.1 问题定义

给定一个 bug record `b`，其输入包括：

```text
bug report / issue text
test failure message
triggering tests
stack trace
buggy source files
runtime or domain context when available
```

系统输出一个文件排序：

```text
R_b = [f_1, f_2, ..., f_k]
```

评价时，如果任一 ground-truth modified file 出现在 Top-k 中，则该 bug 在 Top-k 上命中。Ground truth modified files、fixed commit、post-fix source 和 repair diff 只用于评价，不进入 retrieval、selector、prompt 或 agent tools。

## 3.2 方法概览

本文方法由五个主步骤组成：

```text
bug source collection
-> focused hybrid retrieval
-> deterministic evidence construction
-> selective rerank gate
-> one-shot LLM rerank with retrieval fallback
```

其中 controlled agentic inspection 和 verifier rerank 不属于主方法。它们只作为扩展实验和消融实验用于回答 RQ5。

算法 3-1 给出主流程。

```text
Algorithm 3-1: Selective Evidence-Aware LLM Fault Localization

Input:
  bug record b
  buggy source files S
  top candidate budget K
  output size N

Output:
  ranked file list R

1. q <- build_query(b)
2. C <- focused_hybrid_retrieval(q, S, K)
3. E <- build_evidence_package(b, C)
4. selected <- selector(b, C, E)
5. if selected:
       L <- one_shot_llm_rerank(b, C, E, N)
       R <- normalize_and_merge(L, C, N)
   else:
       R <- top N files from C
6. return R
```

## 3.3 Candidate Retrieval

第一阶段使用 BM25 和 focused hybrid retrieval 生成候选文件集合。BM25 查询由 bug report、失败测试、triggering tests、stack trace 和可用的 runtime/domain context 拼接而成。每个源文件被索引为一个文档，文档内容包含文件路径、包名、类名、方法名和源码文本。

Focused hybrid retrieval 在 BM25 之上加入 deterministic signals：

| Signal | Purpose |
|---|---|
| stack trace class matching | 提高栈帧相关文件召回 |
| triggering test matching | 捕获测试类和被测类关系 |
| exception / method / class name extraction | 利用失败消息中的直接线索 |
| identifier overlap | 捕获 bug text 与源码标识符重合 |
| direct file/path hint | 提升明确命名的候选文件 |
| relevant failure-section filtering | 降低无关测试 section 对 retrieval 的污染 |
| pass-chain / type-system hints | 处理 Closure compiler pass 与 type-system hard cases |

该阶段的核心作用是提供 rerank 上限。如果真实文件不在候选池中，后续 LLM rerank 无法恢复。因此本文在实验中单独报告 retrieval baseline 和候选召回，并在错误分析中区分 retrieval miss 与 rerank miss。

## 3.4 Evidence Construction

LLM 不直接读取整个仓库，而是接收固定大小的 evidence package。每个候选文件的 evidence 包括：

```text
retrieval rank and score
file path
package
class names
method names
deterministic retrieval evidence
source snippet
```

Bug 级 evidence 包括：

```text
bug report text
test failure
triggering tests
compacted stack trace
optional triggering test source context
```

### 3.4.1 Snippet Selection

Snippet selection 根据 bug query、stack trace、candidate path 和 high-signal terms 选择最相关的源码片段。其目标是避免两类失败：

- 真实相关方法没有进入 prompt，导致 LLM 无法识别候选文件。
- 重复栈帧、大型工具类片段或无关注释污染 prompt。

例如在 `Closure-4` pilot 中，真实文件 `NamedType.java` 已在候选池 rank 49，但初始 snippet 没有暴露 `handleTypeCycle` 和 cycle warning text。加入 type-cycle high-signal terms、重复栈压缩和 prompt rule 后，`NamedType.java` 被 DeepSeek rerank 到 rank 2。该案例说明 evidence construction 是方法的一部分，而不是单纯的 prompt 美化。

### 3.4.2 Stack Trace Compaction

对于重复栈帧，系统只保留少量连续重复帧，并插入 omission marker。这样可以避免像 recursive subtype / cycle failure 中的大量重复栈帧占据上下文窗口，导致模型只关注 downstream symptom，而忽略 lower-ranked resolver 或 helper file。

## 3.5 Selective Rerank Gate

为了控制 LLM 成本，系统不默认对所有 bug 调用 LLM。Selector 使用 non-oracle signals 判断一个 retrieval result 是否需要 LLM rerank。

主要 selector signals 包括：

| Signal | Motivation |
|---|---|
| low score ratio / small score gap | top candidates 置信度接近 |
| top-1 without direct hint | top-1 缺少明确 stack/test/path 支持 |
| many direct hints | failure context 同时指向多个文件，存在歧义 |
| pass-chain pattern | compiler configuration / pass chain 可能指向 lower-ranked pass implementation |
| type-cycle / type-system pattern | recursive type、inheritance、StackOverflowError 等可能需要 resolver/helper file |
| state-reset pattern | clone、reseed、serialization、state consistency failure 可能需要 lower-ranked state owner |
| Mockito construction / injection patterns | MockMaker / bytecode creation file 可能比 annotation/configuration caller 更关键 |
| frontend UI evidence patterns | page/container owner 可能比 generic component 更关键 |

Selector 必须满足 no-leakage 约束：不能使用 ground truth rank、modified files、fixed diff 或 post-fix source。它只能使用 bug text、stack trace、retrieval scores、candidate evidence 和源码片段中的 pre-fix 信息。

## 3.6 One-Shot LLM Rerank

对于被 selector 选中的 bug，系统调用一次 DeepSeek rerank。Prompt 包含 bug payload、候选文件 evidence 和严格输出 schema。系统指令强调：

```text
Use only the information in this prompt.
Do not use fixing commit, patch, changed files, or ground truth.
Do not assume the original retrieval rank is correct.
Every returned file must be selected from candidate_files.
Return strict JSON only.
```

在 evidence mode 下，prompt 还加入 domain-specific guidance，例如：

- 对 recursive type、inheritance、cycle-detected、StackOverflowError failures，考虑 lower-ranked resolver 或 placeholder type classes。
- 对 code-printer numeric output failures，区分 parser/conversion helpers 与 final code-emission class。
- 对 Mockito constructor / spy / MockMaker failures，检查决定 mock instance 创建方式的 bytecode creation classes。
- 对 frontend loading、count、currency、API-backed UI bugs，优先检查拥有 query、mutation、state、route 或 display formatting 的 page/container file。

LLM 返回的 JSON 排序格式为：

```json
{
  "ranked_files": [
    {
      "rank": 1,
      "file": "src/main/java/...",
      "confidence": 0.0,
      "reason": "short evidence-based explanation"
    }
  ]
}
```

## 3.7 Output Normalization And Retrieval Fallback

LLM 输出经过规范化处理：

- 解析 JSON。
- 移除不在 candidate pool 中的文件。
- 去除重复文件。
- 保留前 `N` 个有效文件。
- 如果 LLM 输出不足，则按 retrieval ranking fallback 补齐。

该步骤保证最终输出始终是 candidate pool 内的合法文件排序。对于 selector 未选中的 bug，系统直接使用 retrieval top-N 作为最终结果。

## 3.8 RQ5 Extensions: Agentic And Verifier

Controlled agentic inspection 是扩展实验。它允许模型在固定 candidate pool 内使用有限工具进行 search/read/inspect，再输出最终 JSON ranking。它不允许访问 ground truth、fixed diff 或 post-fix source。

Verifier rerank 是 agentic 之后的独立检查步骤。它接收 bug report、agent top-10、固定 snippets 和 prior observations，再输出最终排序。

当前 Easy Finance strict62、Defects4J diagnostic mini-benchmark 和 AboutWork committed-60 结果显示，agentic inspection 技术上可运行，但没有清晰超过 one-shot evidence-aware rerank；verifier 增加 token 成本但没有提升 MRR 或 per-bug correct rank。因此二者只作为 RQ5 extension / ablation，不作为主方法。

## 3.9 方法特点与限制

本文方法的核心特点是：

- retrieval 和 LLM rerank 分工明确；
- LLM 只处理候选文件，不直接探索整个仓库；
- evidence construction 显式控制 prompt 中的代码和上下文；
- selector 控制 LLM 调用成本；
- retrieval fallback 保证输出合法且可评价；
- no-leakage protocol 明确区分输入和评价信息。

方法限制包括：

- 如果真实文件不在 candidate pool 中，LLM rerank 无法恢复；
- selector false negative 会让 hard case 直接回退到 retrieval ranking；
- snippet selection 会影响 LLM 排序质量；
- 文件级定位仍比 method-level 或 line-level 定位更粗；
- domain-specific evidence rule 需要 fresh 或 frozen validation，不能只凭 pilot case 过度主张泛化。
