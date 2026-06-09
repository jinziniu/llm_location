# 论文相关工作草稿

日期：2026-06-03

本文档是相关工作章节草稿。引用目前使用占位符，后续应集中替换为正式 BibTeX key。为避免过度主张，本章只比较方法类别和研究问题，不声称本文全面超过所有已有方法。

## 2.1 缺陷定位任务

缺陷定位旨在从程序和失败信息中找出最可能包含缺陷的代码位置，是自动调试和自动修复的重要前置步骤。已有研究通常按照定位粒度区分为文件级、方法级、语句级和补丁级定位。文件级定位粒度较粗，但适合在调试早期缩小搜索空间，也适合作为自动修复系统的候选文件筛选阶段 [FL-SURVEY].

本文关注文件级缺陷定位。与方法级或语句级定位相比，文件级 Top-k 更接近“开发者首先应该打开哪些文件”的使用场景，但不能直接等价于完整修复定位能力。因此本文在实验中采用 file-level Top-k 和 MRR，并在有效性威胁中说明 any-hit multi-file metric 的限制。

## 2.2 基于频谱和测试信息的缺陷定位

Spectrum-Based Fault Localization (SBFL) 利用测试通过/失败与语句覆盖信息计算怀疑度，例如 Ochiai、Tarantula 等方法 [SBFL-OCHIAI] [SBFL-TARANTULA]。这类方法具有较强可解释性，适合具备覆盖率数据的场景，但需要执行测试并收集覆盖信息。对于真实项目 bug logs、commit-derived records 或缺少稳定测试覆盖的场景，SBFL 的使用成本可能较高。

本文方法不依赖覆盖率数据，而是使用 bug report、失败测试、stack trace 和源码快照构造 retrieval 和 evidence package。它可以和 SBFL 互补：SBFL 分数可以作为未来 focused retrieval 的 deterministic signal，但不是本文当前实验的必要输入。

## 2.3 基于信息检索的缺陷定位

Information Retrieval based Fault Localization (IRFL) 将 bug report、失败消息、测试名称或 stack trace 转换为查询，再使用 BM25、TF-IDF 或向量检索对源文件排序 [IRFL-BM25] [IRFL-SURVEY]。IRFL 的优点是实现简单、成本低、可复现性强，适合在大仓库中快速生成候选文件。缺点是它主要依赖词面匹配，容易受命名不一致、间接调用关系和噪声栈帧影响。

本文沿用 IRFL 作为第一阶段候选生成器，但不止于 BM25。Focused hybrid retrieval 在 BM25 上加入 stack trace class matching、triggering test matching、direct file/path hints、pass-chain hints、type-system hints 和 domain-specific evidence。实验结果也说明 candidate recall 是 LLM rerank 的上限：当 `Closure-98` 的真实文件不在 Top-50 candidate pool 中时，rerank 无法恢复。

## 2.4 学习式和神经缺陷定位

近年来也有工作使用机器学习或深度学习方法学习 bug report 与代码之间的匹配关系，或使用上下文表示、代码表示和排序模型改进缺陷定位 [LEARNING-FL] [DEEP-FL]. 这类方法可以捕获比词面检索更丰富的语义关系，但通常需要训练数据、模型选择和跨项目泛化验证。

本文使用现成 LLM 作为第二阶段 reranker，而不是训练新的端到端定位模型。这样做的好处是工程成本较低，可以直接利用 LLM 的语义判断能力；同时也带来成本、上下文长度和输出可控性问题。因此本文采用 selective invocation、evidence construction 和 retrieval fallback 控制风险。

## 2.5 LLM 在软件工程中的应用

大语言模型已经被广泛用于代码生成、程序修复、测试生成、代码解释和调试辅助 [LLM4SE-SURVEY] [APR-LLM]. 在缺陷定位任务中，LLM 可以综合 bug report、失败测试、stack trace 和源码片段，判断候选文件是否能解释失败行为。然而，直接让 LLM 在整个仓库中自由定位存在三个问题：上下文窗口有限、token 成本高、输出可能包含不存在或不可评价的文件。

本文将 LLM 限制在 retrieval candidate pool 上，并要求模型返回 candidate pool 内的严格 JSON 排序。LLM 输出经过 normalization：过滤候选池外文件、去重，并用 retrieval fallback 补齐不足结果。这样既利用 LLM 的语义 rerank 能力，又保持输出可评价和成本可控。

## 2.6 Evidence-Aware Prompting

LLM rerank 的效果高度依赖 prompt 中的 evidence 质量。已有 LLM 调试和代码理解工作通常强调上下文选择、相关代码片段、调用关系和失败信息的重要性 [LLM-DEBUGGING] [CONTEXT-SELECTION]. 如果 prompt 中缺少关键方法或包含大量噪声，即使模型本身具备推理能力，也可能无法正确排序。

本文将 evidence construction 作为方法核心组成部分。每个候选文件只暴露固定大小的 source snippet、method names、class names 和 retrieval evidence。`Closure-4` 是典型例子：真实文件 `NamedType.java` 已在候选池中，但初始 snippet 没有暴露 `handleTypeCycle` 和 cycle warning text；改进 snippet scoring、重复栈压缩和 type-cycle prompt rule 后，`NamedType.java` 被 rerank 到 rank 2。该结果说明，定位失败有时来自 evidence 缺失，而不是 LLM 无法推理。

## 2.7 选择性调用与成本控制

LLM 推理成本高，且许多简单 bug 已经能由 retrieval baseline 排到前列。因此，对所有样例全量调用 LLM 不是最经济的设计。已有系统通常通过缓存、候选压缩、分阶段检索或 confidence gating 控制 LLM 成本 [LLM-COST] [CASCADE-RANKING].

本文使用 non-oracle selector 选择需要 LLM rerank 的样例。Selector 使用 retrieval score gap、top-1 direct hint、direct-hint count、pass-chain、type-cycle、state-reset、Mockito construction/injection 和 frontend UI patterns 等信号，但不能使用 ground truth、fixed diff 或 post-fix source。在 Closure `61..100` frozen held-out aggregate 中，selector 只调用 11/38 次 LLM，将 Top-5 从 0.6053 提升到 0.7632，将 MRR 从 0.5080 提升到 0.6513。这说明 selective rerank 可以保留主要收益，但错误分析也显示 selector recall 仍是主要瓶颈。

## 2.8 Agentic Debugging 与 Verifier

Agentic debugging 允许模型通过搜索、读取文件和迭代观察来补充上下文 [AGENTIC-SE] [LLM-AGENTS]. 这种方式理论上可以弥补 one-shot prompt evidence 不足，但也会增加 token 成本、工具调用复杂度和实验不确定性。Verifier 或 critic pass 则试图在已有候选排序上进行二次检查 [LLM-VERIFIER].

本文将 controlled agentic inspection 和 verifier rerank 作为 RQ5 扩展实验，而不是主方法。Easy Finance strict62 显示，agentic inspection 技术上可运行，但与 one-shot UI evidence v2 基本持平且 token 成本更高；verifier 额外消耗 80569 tokens，但 MRR 低于 agent-only。Defects4J diagnostic mini-benchmark 进一步显示，one-shot rerank 的 MRR 为 0.5644，而 agentic 和 agentic+verifier 均为 0.4768；verifier 额外消耗 112181 tokens 但没有修复 agentic 退化。因此当前 verifier 是 negative ablation。该结果提醒我们，更多 LLM 步骤不必然带来更好定位；如果 evidence 输入仍然噪声较大，verifier 可能放大 top-10 噪声候选。

## 2.9 Benchmarks 与实验有效性

Defects4J 是 Java 缺陷定位和自动修复研究中常用 benchmark [DEFECTS4J]. 它提供可复现的 buggy/fixed versions、测试和 ground truth 修改信息。但单一 benchmark 不一定代表所有语言、框架或工业项目。真实项目 bug logs 和 commit-derived records 可以补充外部有效性，但也会引入 ground truth 噪声和样本量限制。

本文同时使用 Defects4J 和两个真实项目 case studies。Defects4J 部分包括 120-bug pilot、Closure fresh validation、Closure `61..100` frozen held-out aggregate 和 Mockito fresh validation。AboutWork 和 Easy Finance 用于验证真实项目迁移可能性。本文不声称完成全量 Defects4J，也不声称结果已经泛化到所有项目；最强 benchmark 结论来自 Closure `61..100` frozen held-out aggregate。

## 2.10 本文与已有工作的区别

与传统 IRFL 相比，本文不是只依赖词面检索，而是在 retrieval candidate pool 上构造 evidence，并使用 LLM 做第二阶段语义 rerank。

与端到端学习式缺陷定位相比，本文不训练新的定位模型，而是使用 deterministic retrieval、non-oracle selector 和 one-shot LLM rerank 组成可复现 pipeline。

与直接使用 LLM 进行自由仓库探索的方法相比，本文限制 LLM 只在 candidate pool 内排序，并通过 JSON schema、normalization 和 retrieval fallback 保证输出合法。

与 agentic debugging 方法相比，本文将 agentic / verifier 作为 RQ5 扩展实验。当前结果不支持将其作为主方法，反而说明在 evidence 输入不够干净时，更多 LLM 步骤可能增加成本但不提高定位质量。

因此，本文的核心定位是：在检索候选池和受控 evidence 的基础上，选择性调用 LLM rerank，以有限成本改善文件级缺陷定位，并系统分析 candidate recall、selector recall 和 evidence quality 对结果的影响。

## 引用占位清单

后续需要补 BibTeX 的占位符：

```text
[FL-SURVEY] fault localization survey
[SBFL-OCHIAI] Ochiai / spectrum-based fault localization
[SBFL-TARANTULA] Tarantula / spectrum-based fault localization
[IRFL-BM25] information retrieval based fault localization with BM25 or similar retrieval
[IRFL-SURVEY] IR-based bug localization survey
[LEARNING-FL] learning-based fault localization
[DEEP-FL] deep learning based bug localization
[LLM4SE-SURVEY] LLM for software engineering survey
[APR-LLM] LLM-based automated program repair
[LLM-DEBUGGING] LLM-based debugging / fault localization
[CONTEXT-SELECTION] context selection or retrieval-augmented code reasoning
[LLM-COST] cost control for LLM systems
[CASCADE-RANKING] cascade ranking / selective invocation
[AGENTIC-SE] agentic software engineering
[LLM-AGENTS] LLM agents with tools
[LLM-VERIFIER] verifier / critic models for code tasks
[DEFECTS4J] Defects4J benchmark
```
