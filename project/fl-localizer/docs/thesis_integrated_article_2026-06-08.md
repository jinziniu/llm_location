# Selective Evidence-Aware LLM Fault Localization：文件级缺陷定位实验整合稿

日期：2026-06-08

本文档整合当前项目中的方法、实验设计、实验结果、RQ 回答、错误分析和有效性威胁。写作口径保持保守：本文研究的是文件级缺陷定位，不是自动修复；实验覆盖 Defects4J pilot、fresh validation、Closure frozen held-out validation 和真实项目 case studies，不声称完成全量 Defects4J。

## 摘要

软件缺陷定位是自动调试和自动修复前的重要步骤。传统基于文本检索的缺陷定位方法成本低、可复现性强，但当失败信息与真实修改文件之间存在间接语义关系时，单纯词面匹配容易受到噪声影响。大语言模型具有较强的语义理解能力，但直接让模型处理整个仓库会带来上下文、成本、可控性和复现性问题。

本文提出一种 selective evidence-aware LLM fault localization 方法，用于文件级缺陷定位。该方法首先使用 BM25 和 focused hybrid retrieval 构造候选文件集合，再构造包含 bug report、失败测试、stack trace、检索证据和源码片段的 evidence package。随后，non-oracle selector 只对低置信或语义复杂样例调用 one-shot DeepSeek rerank；未选中的样例直接使用检索排序作为 fallback。Controlled agentic inspection 和 verifier rerank 作为扩展实验和消融实验单独分析，不作为主方法。

实验在 Defects4J、AboutWork 和 Easy Finance 上进行。Defects4J 部分包括 120 个 pilot bugs、Closure `21..60` fresh validation、Closure `61..100` frozen held-out aggregate，以及 Mockito fresh validation。当前最干净的 benchmark 主结果来自 Closure `61..100`：在 38 个 frozen held-out bugs 上，selective rerank 只调用 11 次 LLM，将 Top-5 从 0.6053 提升到 0.7632，将 MRR 从 0.5080 提升到 0.6513。真实项目 case study 中，AboutWork committed-60 只选择 16/60 条调用 DeepSeek，将 Top-1 从 0.5667 提升到 0.7000，将 MRR 从 0.7015 提升到 0.8117；Easy Finance clean63 的 Top-10 从 0.8730 提升到 1.0000。

错误分析表明，当前主要瓶颈不是 LLM 输出格式错误，而是 candidate recall、selector recall 和 evidence quality。`Closure-98` 表明真实文件不在候选池时 rerank 无法恢复；`Closure-4` 表明当真实文件已在候选池中但 evidence 缺失时，改进 snippet 和 prompt 可以显著改善 rerank。RQ5 实验显示，controlled agentic inspection 技术上可运行，但在 Easy Finance strict62、Defects4J diagnostic mini-benchmark 和 AboutWork committed-60 上都没有清晰优于 one-shot rerank；verifier 在当前设计下增加 token 成本但未提升 MRR 或 per-bug correct rank。总体而言，本文结果支持一个保守结论：当候选召回充分且 evidence construction 暴露关键信号时，selective evidence-aware LLM rerank 能以有限 LLM 调用改善文件级缺陷定位。

关键词：缺陷定位；大语言模型；BM25；rerank；Defects4J；真实项目 case study

## 1. 引言

缺陷定位旨在回答“bug 在哪里”。在开发者修复缺陷或自动修复系统生成补丁之前，系统首先需要将注意力集中到少量可能包含缺陷的文件、方法或代码行上。定位质量直接影响后续调试效率和修复搜索空间。本文关注文件级缺陷定位：给定 bug report、失败测试、stack trace 和 buggy source snapshot，系统输出最可能包含缺陷的源文件排序。

现有文本检索方法通常具有较低成本和较好可复现性。例如 BM25 可以基于失败消息、测试名称和栈信息快速检索候选文件。然而，真实缺陷中经常存在间接关系：失败栈帧可能指向抛出异常的位置，而修复文件位于上游状态管理或辅助工具类；测试名称可能指向 compiler pass，而真实修改发生在共享 helper file；UI bug 描述可能提到页面行为，而修复位于具体 query、mutation 或 formatting owner。这些情况使单纯词面检索难以稳定排序。

大语言模型为缺陷定位提供了新的机会。模型可以同时考虑 bug 描述、失败上下文、候选文件摘要和源码片段，进而判断哪个文件更可能解释失败行为。但直接将整个仓库交给模型既不现实，也难以复现：上下文窗口有限、token 成本高、输出可能包含不存在的文件，而且模型可能受到噪声代码片段干扰。因此，本文采用两阶段思路：先用检索方法构造高召回候选池，再在受控 evidence 上选择性调用 LLM rerank。

本文提出 selective evidence-aware LLM fault localization。该方法包含 focused hybrid retrieval、deterministic evidence construction、selective rerank gate 和 one-shot LLM rerank with retrieval fallback。Selector 使用非 oracle 信号决定是否调用 LLM，包括 score gap、direct hint、pass-chain、type-cycle、state-reset、Mockito construction/injection 以及前端 UI evidence 等。整个流程不允许 ground truth、fixed diff 或 post-fix source 进入 prompt、selector 或 agent tools。

本文贡献如下：

1. 提出一种 selective evidence-aware LLM fault localization 方法，将 focused retrieval、deterministic evidence construction、non-oracle selector 和 one-shot LLM rerank 结合起来，用于文件级缺陷定位。
2. 构建了一个可复现的实验 pipeline，覆盖 Defects4J benchmark、真实 bug-log 数据 AboutWork，以及 git-history-derived Easy Finance case study，并记录 token usage、runtime、selector selected fraction 和 per-bug rank changes。
3. 在 Defects4J 上完成 120-bug pilot、Closure fresh validation、Closure `61..100` frozen held-out validation 和 Mockito fresh validation。最强 benchmark 结果显示，在 38 个 Closure frozen held-out bugs 上，selective rerank 只调用 11 次 LLM，将 Top-5 从 0.6053 提升到 0.7632，将 MRR 从 0.5080 提升到 0.6513。
4. 在 AboutWork committed-60 和 Easy Finance 上进行真实项目 case study，初步验证 retrieval + selector + rerank 框架可以迁移到真实 bug records。AboutWork-60 结果显示，selector_v3 + one-shot DeepSeek 将 Top-1 从 0.5667 提升到 0.7000，将 MRR 从 0.7015 提升到 0.8117。
5. 通过错误分析区分 candidate retrieval miss、selector false negative、evidence/snippet miss、utility-file ambiguity 和 RQ5 agentic/verifier cost 等 failure modes，指出当前主要瓶颈是 candidate recall、selector recall 和 evidence quality，而不是简单缺少更多 LLM 推理步骤。
6. 对 controlled agentic inspection 和 verifier rerank 进行 RQ5 扩展实验。Easy Finance strict62、Defects4J diagnostic mini-benchmark 和 AboutWork committed-60 的结果均显示 agentic 技术上可行但未清晰优于 one-shot rerank，verifier 当前是 negative ablation。

## 2. 方法

### 2.1 问题定义

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

### 2.2 方法流程

本文方法由五个主步骤组成：

```text
bug source collection
-> focused hybrid retrieval
-> deterministic evidence construction
-> selective rerank gate
-> one-shot LLM rerank with retrieval fallback
```

算法流程如下：

```text
Algorithm: Selective Evidence-Aware LLM Fault Localization

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

Controlled agentic inspection 和 verifier rerank 不属于主方法。它们只作为扩展实验和消融实验用于回答 RQ5。

### 2.3 Candidate Retrieval

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

### 2.4 Evidence Construction

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

Snippet selection 根据 bug query、stack trace、candidate path 和 high-signal terms 选择最相关的源码片段。其目标是避免两类失败：真实相关方法没有进入 prompt，导致 LLM 无法识别候选文件；重复栈帧、大型工具类片段或无关注释污染 prompt。

例如在 `Closure-4` pilot 中，真实文件 `NamedType.java` 已在候选池 rank 49，但初始 snippet 没有暴露 `handleTypeCycle` 和 cycle warning text。加入 type-cycle high-signal terms、重复栈压缩和 prompt rule 后，`NamedType.java` 被 DeepSeek rerank 到 rank 2。该案例说明 evidence construction 是方法的一部分，而不是单纯的 prompt 美化。

### 2.5 Selective Rerank Gate

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

### 2.6 One-Shot LLM Rerank

对于被 selector 选中的 bug，系统调用一次 DeepSeek rerank。Prompt 包含 bug payload、候选文件 evidence 和严格输出 schema。系统指令强调：

```text
Use only the information in this prompt.
Do not use fixing commit, patch, changed files, or ground truth.
Do not assume the original retrieval rank is correct.
Every returned file must be selected from candidate_files.
Return strict JSON only.
```

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

LLM 输出经过规范化处理：解析 JSON、移除不在 candidate pool 中的文件、去除重复文件、保留前 `N` 个有效文件。如果 LLM 输出不足，则按 retrieval ranking fallback 补齐。对于 selector 未选中的 bug，系统直接使用 retrieval top-N 作为最终结果。

## 3. 实验设计

### 3.1 研究问题

本文围绕五个研究问题展开：

| RQ | Question |
|---|---|
| RQ1 | 与 BM25 和 focused hybrid retrieval baseline 相比，LLM rerank 是否能提升 Defects4J 文件级定位效果？ |
| RQ2 | 候选召回质量和 evidence 质量如何影响 LLM rerank？剩余失败主要来自 retrieval miss、selector false negative、snippet/evidence 问题，还是模型排序错误？ |
| RQ3 | selective rerank 能否减少 LLM 调用量、token 成本和运行时间，同时保留 Top-k 与 MRR 收益？ |
| RQ4 | 该方法能否从 Defects4J benchmark 迁移到 AboutWork 和 Easy Finance 等真实项目数据？ |
| RQ5 | controlled agentic inspection 和 verifier rerank 是否能在 one-shot rerank 之上进一步提升定位效果？ |

### 3.2 数据集

表 1 给出实验数据范围。Defects4J pilot 用于方法开发和跨项目初步验证；Closure `61..100` frozen held-out aggregate 是当前最干净的 benchmark 主结果；AboutWork 和 Easy Finance 用于真实项目迁移 case study。

表 1：实验数据集

| Dataset | Role | Size | Thesis Use |
|---|---|---:|---|
| Defects4J pilot | 方法开发与 pilot validation | 120 bugs | pilot result |
| Closure-21..60 | fresh validation | 40 bugs | selector/rule validation |
| Closure-61..100 | frozen held-out aggregate | 38 bugs | main benchmark result |
| Mockito-21..30 | fresh attempt | 9 usable bugs | diagnostics / fresh validation |
| Mockito-31..38 | fresh validation | 8 bugs | fresh validation |
| AboutWork committed-60 | real bug-log case study | 60 records | RQ4; RQ5 extension |
| Easy Finance clean63 | real git-history case study | 63 records | RQ4 |
| Easy Finance strict62 | filtered real git-history case study | 62 records | RQ5 |
| Defects4J RQ5 mini | diagnostic extension benchmark | 10 bugs | RQ5 |

当前约完成 215 个 usable Defects4J records。Mockito 在当前 Defects4J checkout 中 active bugs 只有 `1..38`，已经被 pilot 和 fresh validation 覆盖，因此不能再构造新的 Mockito held-out slice。

### 3.3 No-Leakage Protocol

实验严格区分输入信息和评价信息。允许进入 retrieval、selector、prompt 和 agent tools 的信息包括 bug report、失败测试、triggering tests、stack trace、buggy source 和 deterministic candidate evidence。Ground truth modified files、fixed commit、post-fix source 和 repair diff 只用于评价，不进入 prompt、selector 或 agent tools。

Closure `61..80` 和 `81..100` 均先写 frozen protocol，再运行 dataset build、retrieval、selector、rerank 和 evaluation。前一组 held-out error analysis 不反向修改后一组 held-out protocol。

### 3.4 评价指标

本文使用文件级 Top-k accuracy 和 MRR：

```text
Top-k = whether any ground-truth file appears in the top-k files
MRR = average(1 / rank_of_first_correct_file)
```

对于多文件 bug，当前采用 any-hit file-level definition：只要任一 ground-truth file 出现在 Top-k 中即算成功。该定义适合衡量开发者是否能在前几个文件中看到相关修复文件，但可能高估多文件 bug 的完整定位能力，因此在有效性威胁中单独讨论。

对于 selective rerank，merged output 被截断到 Top-10。因此 Top-20 / Top-50 candidate recall 必须从 retrieval baseline 输出解释，不能从 merged Top-10 输出解读。

## 4. 实验结果

### 4.1 RQ1：Defects4J 上 LLM Rerank 是否提升定位效果？

表 2 展示六个 Defects4J pilot 项目的当前最好结果。Pilot 结果说明，LLM rerank 能作为第二阶段排序器改善文件级定位，尤其在候选池包含真实文件时效果明显。Closure 和 Mockito 更难，它们推动了 pass-chain、type-cycle、ByteBuddy / MockMaker 等 evidence rule 的设计。

表 2：Defects4J pilot 当前最好结果

| Project | Best Current Setting | Bugs | Top-1 | Top-3 | Top-5 | MRR |
|---|---|---:|---:|---:|---:|---:|
| Lang | BM25 + DeepSeek rerank | 20 | 0.95 | 1.00 | 1.00 | 0.9750 |
| Math | Hybrid/direct + compact evidence DeepSeek | 20 | 0.90 | 0.95 | 1.00 | 0.9350 |
| Chart | Focused hybrid/direct | 20 | 0.85 | 0.95 | 1.00 | 0.9040 |
| Time | Focused hybrid/direct + DeepSeek hard4 | 20 | 0.90 | 1.00 | 1.00 | 0.9500 |
| Closure | Focused hybrid/direct + DeepSeek hard8 + pass-chain/type-cycle rules | 20 | 0.40 | 0.80 | 1.00 | 0.6225 |
| Mockito | Focused hybrid/direct + tight selector9 DeepSeek | 20 | 0.65 | 1.00 | 1.00 | 0.8000 |

这些 pilot 包含 targeted evidence add-ons，因此不作为最终泛化证明。更保守的 benchmark 结论来自 Closure frozen held-out aggregate。

表 3：Closure frozen held-out aggregate

| Dataset | Setting | Bugs | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Closure-61..100 | frozen retrieval baseline | 38 | 0 | 0.3947 | 0.5263 | 0.6053 | 0.7105 | 0.5080 |
| Closure-61..100 | frozen cost-control v3 + DeepSeek | 38 | 11 | 0.5526 | 0.7105 | 0.7632 | 0.8421 | 0.6513 |

在 Closure `61..100` 的 38 个 frozen held-out bugs 上，selective DeepSeek 将 Top-1 从 0.3947 提升到 0.5526，Top-5 从 0.6053 提升到 0.7632，MRR 从 0.5080 提升到 0.6513。因此，RQ1 的回答是：LLM rerank 能提升 Defects4J 文件级定位，但前提是候选池包含真实缺陷文件。

### 4.2 RQ2：候选召回和 Evidence 质量如何影响结果？

当前剩余失败主要集中在三类上游问题。

第一类是 candidate retrieval miss。如果真实文件不在 candidate pool 中，LLM rerank 无法恢复。例如 `Closure-98` 是 Closure frozen held-out aggregate 中的 Top-50 retrieval miss。

第二类是 selector false negative。Closure `61..100` aggregate 中，baseline Top-5 failures 一共有 15 个，但 selector 只覆盖 6 个；baseline Top-10 failures 一共有 11 个，selector 只覆盖 5 个。这说明 selected-case rerank 本身有效，但 selector recall 仍不足。

第三类是 evidence/snippet 不足。`Closure-4` 是一个清楚的 pilot 例子：真实文件 `NamedType.java` 已经在候选池中，但位于 rank 49；初始 rerank 没有选中它。修复 snippet scoring、压缩重复 `PrototypeObjectType.isSubtype` 栈帧，并加入 type-cycle prompt rule 后，`NamedType.java` 被 DeepSeek 提到 rank 2。该例子说明 rerank 失败不一定来自模型无法推理，也可能来自 evidence package 没有暴露 `handleTypeCycle` 和 cycle warning 等关键信号。它应作为 pilot method-evolution evidence，而不是 frozen held-out proof。

### 4.3 RQ3：Selective Rerank 是否降低成本并保留收益？

Closure frozen held-out aggregate 只调用 11/38 次 LLM：

```text
selected_fraction: 0.2895
total_tokens: 408568
avg_total_tokens_per_selected_case: 37142.55
total_duration_seconds: 178.838
avg_duration_seconds_per_selected_case: 16.258
```

在该预算下，Top-5 提升 +0.1579，Top-10 提升 +0.1316，MRR 提升 +0.1434。

真实项目 case study 也支持 selective invocation 的成本收益。AboutWork committed-60 只选择 16/60 条调用 one-shot DeepSeek，使 Top-1 从 0.5667 提升到 0.7000，Top-3 从 0.8333 提升到 0.9500，MRR 从 0.7015 提升到 0.8117。Easy Finance clean63 只调用 10/63 次，使 Top-10 从 0.8730 提升到 1.0000。因此，RQ3 的回答是：selective rerank 能以有限 LLM 调用保留主要准确率收益，但 selector recall 是主要风险。

### 4.4 RQ4：方法能否迁移到真实项目？

表 4 展示两个真实项目 case study。AboutWork 使用真实 bug logs；Easy Finance 使用 git-history-derived records。

表 4：真实项目 case study

| Dataset | Method | Selected Records | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---|---:|---:|---:|---:|---:|---:|
| AboutWork committed-60 | BM25 production top50 | 0 / 60 | 0.5667 | 0.8333 | 0.9167 | 0.9333 | 0.7015 |
| AboutWork committed-60 | BM25 + selector_v3 + DeepSeek | 16 / 60 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 |
| Easy Finance clean63 | BM25 production top50 | 0 / 63 | 0.3968 | 0.7302 | 0.8730 | 0.8730 | 0.5684 |
| Easy Finance clean63 | BM25 + selector_v1 UI evidence v2 | 10 / 63 | 0.4921 | 0.8095 | 0.9841 | 1.0000 | 0.6729 |

这些结果说明，benchmark 中有效的 retrieval + selector + rerank 框架可以迁移到真实项目 bug records。但该结论必须保守：AboutWork 和 Easy Finance 仍是 case studies，且 selector/evidence strategy 是在当前样本上调出的。它们支持迁移可行性，不构成强泛化证明。AboutWork committed-60 的剩余两个 Top-10 miss 都是 selector false negative，说明真实项目上的主要瓶颈仍是 selector recall。

### 4.5 RQ5：Agentic / Verifier 是否优于 One-Shot？

表 5 展示 Easy Finance strict62 上的 RQ5 ablation。

表 5：Agentic / verifier ablation on Easy Finance strict62

| Method | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR | Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| one-shot UI evidence v2 | 9 | 0.5000 | 0.8226 | 1.0000 | 1.0000 | 0.6817 | 226860 |
| controlled agentic s2 | 9 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6831 | 250481 |
| agentic s2 + verifier | 9 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6804 | 331050 |

表 6 进一步在 Defects4J 上做一个 diagnostic mini-benchmark。该 mini-benchmark 包含 10 个已知诊断类别 case，包括 state-reset evidence、type-cycle evidence、pass-chain retrieval boundary、selector false negative、utility-file ambiguity、retrieval boundary negative 和 Mockito pattern generalization。该结果用于回答 RQ5 的扩展行为，不替代 Closure `61..100` frozen held-out 主结果。

表 6：Agentic / verifier ablation on Defects4J diagnostic mini-benchmark

| Method | API Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR | Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| retrieval baseline top50 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.2000 | 0.0534 | 0 |
| one-shot DeepSeek | 10 | 0.4000 | 0.7000 | 0.8000 | 0.9000 | 0.5644 | 345937 |
| agentic DeepSeek | 32 | 0.3000 | 0.6000 | 0.6000 | 0.8000 | 0.4768 | 441952 |
| agentic + verifier DeepSeek | 42 | 0.3000 | 0.6000 | 0.6000 | 0.8000 | 0.4768 | 554133 |

Defects4J mini-benchmark 的 per-bug rank 显示，one-shot 在 `Math-14`、`Closure-65`、`Mockito-26`、`Mockito-28` 上达到 rank 1，在 `Closure-13` 上达到 rank 3，在 `Closure-67` 和 `Closure-75` 上达到 rank 2。Agentic inspection 没有新增成功，反而将 `Math-12` 从 one-shot rank 9 降到 top10 miss，并将 `Closure-4`、`Closure-13`、`Mockito-28` 往后排。Verifier 额外消耗 112181 tokens，但输出与 agentic 相同。

表 7 在 AboutWork committed-60 上补充同一结论。为避免混淆，表中区分 selected records 和 model calls：one-shot 每条一次模型调用，agentic 每条可能包含多步工具决策和最终排序，verifier 是额外检查 pass。

表 7：Agentic / verifier ablation on AboutWork committed-60

| Method | Selected Records | Model Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR | Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| one-shot DeepSeek | 16 / 60 | 16 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 519530 |
| agentic DeepSeek s2 | 16 / 60 | 40 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 440542 |
| agentic s2 + verifier | 16 / 60 | 56 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 589260 |

AboutWork-60 上 one-shot、agentic 和 agentic + verifier 的 per-bug correct rank 完全一致。Verifier 额外消耗 148718 tokens 和 196.194 秒，但没有改善任何 aggregate 指标或 per-bug rank。

因此，RQ5 的回答是：controlled agentic inspection 技术上可运行，并能产生可分析 trace；但 Easy Finance strict62、Defects4J diagnostic mini-benchmark 和 AboutWork committed-60 都没有证明 agentic / verifier 优于 one-shot rerank。Verifier 在当前设计下是 negative ablation，不应作为主方法。

## 5. 讨论

### 5.1 主要发现

第一，LLM rerank 适合做第二阶段排序，而不是替代 retrieval。实验反复显示，只要真实文件进入候选池，LLM 能利用 failure context 和 source evidence 改善文件排序。

第二，selective invocation 是成本控制关键。全量调用 LLM 成本高，且很多简单样例 retrieval 已经能排到 Top-1。Selector 的作用是把 LLM 预算集中到低置信、证据冲突或语义复杂的样例上。

第三，当前最重要的瓶颈已经从 BM25 排序转为 selector recall、candidate recall 和 evidence quality。Closure aggregate 中 selected-case rerank 很强，但 selector 未覆盖大量 baseline Top-5 failures。AboutWork-60 中剩余 Top-10 miss 也都是 selector false negative。

第四，更多 LLM 推理步骤并不必然提高定位质量。AboutWork-60 中 one-shot、agentic 和 agentic + verifier 的 per-bug correct rank 完全一致；Defects4J mini-benchmark 中 agentic 甚至相对 one-shot 退化。当前证据不支持把 agentic/verifier 作为主方法。

### 5.2 错误分析

表 8 总结当前主要错误类型。

表 8：错误分析摘要

| Error Type | Representative Cases | Cause | Lesson |
|---|---|---|---|
| Recovered evidence/snippet miss | `Closure-4` pilot | Faulty file was present at candidate rank 49, but the original snippet omitted type-cycle evidence. | Evidence construction can determine whether one-shot rerank succeeds. |
| Selector false negative | `Closure-67`, `Closure-75`, `Closure-88`, `Closure-99`; AboutWork-60 final misses | Correct file was in candidate pool, but selector did not call LLM. | Selector recall is the main bottleneck. |
| Candidate retrieval miss | `Closure-98` | Correct file was outside retrieval Top-50. | Rerank cannot fix absent candidates. |
| Utility-file ambiguity | `Closure-61`, `Closure-75`, `Closure-94` | Failure context points to compiler passes, but fix touches `NodeUtil.java`. | Shared helper files need better non-oracle diagnostics. |
| Code-output evidence gap | `Closure-65` | `CodePrinter.java` ranked above `CodeGenerator.java`, but selector pattern did not fire. | Code-output selector is useful but too narrow. |
| Agentic/verifier cost | Easy Finance strict62; Defects4J RQ5 mini; AboutWork committed-60 | More LLM steps did not improve evidence quality or per-bug correct ranks. | Keep as RQ5 ablation, not main method. |

这些错误并不主要来自 LLM 输出格式无效或模型完全无法排序，而是集中在上游 retrieval、evidence construction 和 selector coverage。后续如果继续补强实验，应优先改进 non-oracle selector recall 和 candidate recall，而不是简单增加推理步骤。

## 6. 有效性威胁

### 6.1 内部有效性

Ground truth 来自 modified files/classes，可能包含非 root cause 修改。尤其在真实项目 git-history-derived cases 中，fix commit 可能同时包含重构、格式化或顺手修改。Prompt、snippet 和 selector 也是方法的一部分，对 LLM 表现影响显著。Closure 和 Mockito pilot 中包含 targeted evidence add-ons，因此需要和 frozen held-out 主结果分开解释。

### 6.2 构造有效性

当前指标是文件级 Top-k，而不是方法级、语句级或补丁级定位。对于多文件 bug，本文使用 any-hit file-level definition，可能高估完整定位能力。Merged selective-rerank 输出被截断到 Top-10，因此 Top-20 / Top-50 candidate recall 应从 retrieval baseline 报告。

### 6.3 外部有效性

Defects4J 是 Java benchmark，不能直接代表其他语言或工业项目。Closure 是当前 held-out 主体，因此 held-out 结论主要代表 Closure，不应自动推广到全部 Defects4J。AboutWork committed-60 和 Easy Finance 是真实项目 case studies，但样本量有限，且 selector/evidence 仍需新增样本验证。

### 6.4 结论有效性

当前约完成 215 个 usable Defects4J records，但不是全量 Defects4J。Closure frozen held-out aggregate 支持主方法，但 selector recall 仍不足。Agentic/verifier 当前有 Easy Finance strict62、Defects4J diagnostic mini-benchmark 和 AboutWork committed-60 三组证据；其中 Defects4J mini 是按已知失败类别构造的诊断集，不是无偏 held-out 泛化估计。

## 7. 复现说明

核心脚本如下：

```text
scripts/build_defects4j_dataset.py
scripts/run_hybrid_retrieval.py
scripts/select_rerank_candidates.py
scripts/run_llm_rerank.py
scripts/run_agentic_rerank.py
scripts/run_verifier_rerank.py
scripts/merge_selective_rerank.py
scripts/evaluate_predictions.py
scripts/summarize_llm_usage.py
```

关键 protocol 和结果文档如下：

```text
docs/frozen_protocol_2026-06-01.md
docs/frozen_protocol_2026-06-02_closure_81_100.md
docs/closure_heldout_61_80_validation_report.md
docs/closure_heldout_81_100_validation_report.md
docs/closure_frozen_heldout_61_100_summary.md
docs/aboutwork_committed_60_rerank_results_2026-06-08.md
docs/aboutwork_committed_60_agentic_verifier_results_2026-06-08.md
```

复现需要本地 Defects4J checkout、对应 bug workspaces、DeepSeek API key，以及 frozen protocol 中固定的 retrieval、selector 和 rerank 参数。

## 8. 结论

本文研究了 selective evidence-aware LLM rerank 在文件级缺陷定位中的作用。实验结果表明，LLM rerank 适合作为第二阶段排序器，而不是替代 retrieval。只要 candidate pool 包含真实缺陷文件，并且 evidence package 暴露了有用信号，one-shot LLM rerank 可以改善 Top-k 和 MRR。

当前最强 benchmark 结果来自 Closure `61..100` frozen held-out aggregate。在 38 个 held-out bugs 上，selective rerank 调用 11 次 LLM，将 Top-1 从 0.3947 提升到 0.5526，Top-5 从 0.6053 提升到 0.7632，Top-10 从 0.7105 提升到 0.8421，MRR 从 0.5080 提升到 0.6513。AboutWork committed-60 和 Easy Finance 的 case studies 进一步表明，该 retrieval + selector + rerank 框架可以迁移到真实项目 bug records。

同时，本文结果也给出了清晰限制。LLM rerank 无法补救 candidate retrieval miss，例如 `Closure-98`；selector false negative 会使 hard case 未被 rerank；evidence/snippet 质量会直接影响 LLM 是否能识别真实文件，例如 `Closure-4`。Controlled agentic inspection 和 verifier rerank 并未在当前实验中超过 one-shot rerank，因此不应作为主方法。

总体而言，本文支持一个保守结论：selective evidence-aware LLM rerank 能以有限 LLM 调用改善文件级缺陷定位，但其效果依赖 candidate recall、selector recall 和 evidence quality。未来工作应优先改进 non-oracle selector recall、候选召回和 evidence construction，而不是简单增加 LLM 推理步骤。

## 9. 不应主张的内容

论文中不应写：

```text
本文完成了全量 Defects4J 实验。
本文方法已经证明可泛化到所有项目和语言。
Selector 已经完全泛化。
Agentic/verifier 优于 one-shot rerank。
```

论文中可以写：

```text
本文完成了 120-bug Defects4J pilot、additional fresh validation，以及 38-bug Closure frozen held-out validation。
当 candidate recall 充分且 evidence construction 暴露有用信号时，selective evidence-aware LLM rerank 可以改善文件级缺陷定位。
当前主要限制是 candidate recall、selector recall 和 evidence quality。
Controlled agentic inspection 技术上可行但未清晰优于 one-shot rerank；verifier 当前是 negative ablation。
```
