# 论文摘要、引言与结论草稿

日期：2026-06-08

本文档为论文前后文草稿，和方法章节、实验章节保持同一口径：本文完成的是文件级缺陷定位实验，不是自动修复；完成的是 Defects4J pilot、fresh validation、Closure frozen held-out validation 和真实项目 case study，不是全量 Defects4J。

## 中文摘要草稿

软件缺陷定位是自动调试和自动修复前的重要步骤。传统基于文本检索的缺陷定位方法成本低、可复现性强，但在失败信息与真实修改文件之间存在语义间隔时容易受到噪声影响。大语言模型具有较强的语义理解能力，但直接让模型处理整个仓库会带来上下文、成本和可控性问题。

本文提出一种 selective evidence-aware LLM fault localization 方法，用于文件级缺陷定位。该方法首先使用 BM25 和 focused hybrid retrieval 生成候选文件集合，再构造包含 bug report、失败测试、stack trace、检索证据和源码片段的 evidence package。随后，non-oracle selector 只对低置信或语义复杂的样例调用 one-shot DeepSeek rerank；未选中的样例直接使用检索排序作为 fallback。Controlled agentic inspection 和 verifier rerank 作为扩展实验和消融实验单独分析，不作为主方法。

实验在 Defects4J、AboutWork 和 Easy Finance 上进行。Defects4J 部分包括 120 个 pilot bugs、Closure `21..60` fresh validation、Closure `61..100` frozen held-out aggregate，以及 Mockito fresh validation。当前最干净的 benchmark 主结果来自 Closure `61..100`：在 38 个 frozen held-out bugs 上，selective rerank 只调用 11 次 LLM，将 Top-5 从 0.6053 提升到 0.7632，将 MRR 从 0.5080 提升到 0.6513。真实项目 case study 中，AboutWork committed-60 只选择 16/60 条调用 DeepSeek，将 Top-1 从 0.5667 提升到 0.7000，将 MRR 从 0.7015 提升到 0.8117；Easy Finance clean63 的 Top-10 从 0.8730 提升到 1.0000。

错误分析表明，当前主要瓶颈不是 LLM 输出格式错误，而是 candidate recall、selector recall 和 evidence quality。`Closure-98` 表明真实文件不在候选池时 rerank 无法恢复；`Closure-4` 表明当真实文件已在候选池中但 evidence 缺失时，改进 snippet 和 prompt 可以显著改善 rerank。RQ5 实验显示，controlled agentic inspection 技术上可运行，但在 Easy Finance strict62、Defects4J diagnostic mini-benchmark 和 AboutWork committed-60 上都没有清晰优于 one-shot rerank；verifier 在当前设计下增加 token 成本但未提升 MRR 或 per-bug correct rank。总体而言，本文结果支持一个保守结论：当候选召回充分且 evidence construction 暴露关键信号时，selective evidence-aware LLM rerank 能以有限 LLM 调用改善文件级缺陷定位。

## English Abstract Draft

Fault localization is a prerequisite for automated debugging and program repair. Traditional retrieval-based approaches are inexpensive and reproducible, but they often struggle when failure evidence and the actual modified file are connected by indirect semantic relations. Large language models can reason over richer context, yet applying them directly to an entire repository is expensive and difficult to control.

This thesis proposes selective evidence-aware LLM fault localization for file-level fault localization. The method first uses BM25 and focused hybrid retrieval to construct a candidate file pool, then builds deterministic evidence packages containing bug reports, failing tests, stack traces, retrieval evidence, and source snippets. A non-oracle selector invokes one-shot DeepSeek reranking only for low-confidence or semantically complex cases; non-selected cases fall back to the retrieval ranking. Controlled agentic inspection and verifier reranking are evaluated separately as extensions and ablations, not as the main method.

The evaluation covers Defects4J, AboutWork, and Easy Finance. The Defects4J part includes a 120-bug pilot, Closure `21..60` fresh validation, a Closure `61..100` frozen held-out aggregate, and Mockito fresh validation. The strongest benchmark result is the Closure `61..100` frozen held-out aggregate: on 38 held-out bugs, selective reranking uses 11 LLM calls and improves Top-5 from 0.6053 to 0.7632 and MRR from 0.5080 to 0.6513. In real-project case studies, AboutWork committed-60 selects 16 of 60 records for DeepSeek and improves Top-1 from 0.5667 to 0.7000 and MRR from 0.7015 to 0.8117; Easy Finance clean63 improves Top-10 from 0.8730 to 1.0000.

The error analysis shows that remaining failures are dominated by candidate recall, selector recall, and evidence quality rather than invalid LLM outputs. `Closure-98` shows that reranking cannot recover absent candidates, while `Closure-4` shows that candidate-present failures can be recovered when type-cycle evidence reaches the prompt. The RQ5 experiments show that controlled agentic inspection is feasible but not clearly better than one-shot reranking across Easy Finance strict62, the Defects4J diagnostic mini-benchmark, and AboutWork committed-60; the current verifier is a negative ablation. Overall, the results support the conservative conclusion that selective evidence-aware LLM reranking can improve file-level fault localization with limited LLM calls when candidate recall is sufficient and evidence construction exposes useful signals.

## 引言草稿

缺陷定位旨在回答“bug 在哪里”。在开发者修复缺陷或自动修复系统生成补丁之前，系统首先需要将注意力集中到少量可能包含缺陷的文件、方法或代码行上。定位质量直接影响后续调试效率和修复搜索空间。本文关注文件级缺陷定位：给定 bug report、失败测试、stack trace 和 buggy source snapshot，系统输出最可能包含缺陷的源文件排序。

现有文本检索方法通常具有较低成本和较好可复现性。例如 BM25 可以基于失败消息、测试名称和栈信息快速检索候选文件。然而，真实缺陷中经常存在间接关系：失败栈帧可能指向抛出异常的位置，而修复文件位于上游状态管理或辅助工具类；测试名称可能指向 compiler pass，而真实修改发生在共享 helper file；UI bug 描述可能提到页面行为，而修复位于具体 query、mutation 或 formatting owner。这些情况使单纯词面检索难以稳定排序。

大语言模型为缺陷定位提供了新的机会。模型可以同时考虑 bug 描述、失败上下文、候选文件摘要和源码片段，进而判断哪个文件更可能解释失败行为。但直接将整个仓库交给模型既不现实，也难以复现：上下文窗口有限、token 成本高、输出可能包含不存在的文件，而且模型可能受到噪声代码片段干扰。因此，本文采用两阶段思路：先用检索方法构造高召回候选池，再在受控 evidence 上选择性调用 LLM rerank。

本文提出 selective evidence-aware LLM fault localization。该方法包含 focused hybrid retrieval、deterministic evidence construction、selective rerank gate 和 one-shot LLM rerank with retrieval fallback。Selector 使用非 oracle 信号决定是否调用 LLM，包括 score gap、direct hint、pass-chain、type-cycle、state-reset、Mockito construction/injection 以及前端 UI evidence 等。整个流程不允许 ground truth、fixed diff 或 post-fix source 进入 prompt、selector 或 agent tools。

本文实验表明，该方法在 Defects4J 和真实项目 case study 上均能改善文件级排序。尤其在 Closure `61..100` frozen held-out aggregate 上，该方法只调用 11/38 次 LLM，将 Top-5 从 0.6053 提升到 0.7632，将 MRR 从 0.5080 提升到 0.6513。在 AboutWork committed-60 上，该方法只选择 16/60 条调用 DeepSeek，将 Top-1 从 0.5667 提升到 0.7000，将 MRR 从 0.7015 提升到 0.8117。同时，实验也揭示了方法边界：如果真实文件不在 candidate pool 中，LLM rerank 无法恢复；如果 selector 没有选择 hard case，则该样例会回退到 retrieval ranking；如果 snippet 没有暴露关键证据，模型也可能无法正确排序。Controlled agentic inspection 和 verifier rerank 在本文当前实验中没有证明优于 one-shot rerank，因此只作为扩展与消融讨论。

## 贡献草稿

本文主要贡献如下：

1. 提出一种 selective evidence-aware LLM fault localization 方法，将 focused retrieval、deterministic evidence construction、non-oracle selector 和 one-shot LLM rerank 结合起来，用于文件级缺陷定位。

2. 构建了一个可复现的实验 pipeline，覆盖 Defects4J benchmark、真实 bug-log 数据 AboutWork，以及 git-history-derived Easy Finance case study，并记录 token usage、runtime、selector selected fraction 和 per-bug rank changes。

3. 在 Defects4J 上完成 120-bug pilot、Closure fresh validation、Closure `61..100` frozen held-out validation 和 Mockito fresh validation。最强 benchmark 结果显示，在 38 个 Closure frozen held-out bugs 上，selective rerank 只调用 11 次 LLM，将 Top-5 从 0.6053 提升到 0.7632，将 MRR 从 0.5080 提升到 0.6513。

4. 在 AboutWork committed-60 和 Easy Finance 上进行真实项目 case study，初步验证 retrieval + selector + rerank 框架可以迁移到真实 bug records。AboutWork-60 结果显示，selector_v3 + one-shot DeepSeek 将 Top-1 从 0.5667 提升到 0.7000，将 MRR 从 0.7015 提升到 0.8117；同时明确这些结果仍需新增日志或新时间段 commit 验证泛化。

5. 通过错误分析区分 candidate retrieval miss、selector false negative、evidence/snippet miss、utility-file ambiguity 和 RQ5 agentic/verifier cost 等 failure modes，指出当前主要瓶颈是 candidate recall、selector recall 和 evidence quality，而不是简单缺少更多 LLM 推理步骤。

6. 对 controlled agentic inspection 和 verifier rerank 进行 RQ5 扩展实验。Easy Finance strict62、Defects4J diagnostic mini-benchmark 和 AboutWork committed-60 的结果均显示 agentic 技术上可行但未清晰优于 one-shot rerank，verifier 当前是 negative ablation，为后续研究提供了反例和设计边界。

## 结论草稿

本文研究了 selective evidence-aware LLM rerank 在文件级缺陷定位中的作用。实验结果表明，LLM rerank 适合作为第二阶段排序器，而不是替代 retrieval。只要 candidate pool 包含真实缺陷文件，并且 evidence package 暴露了有用信号，one-shot LLM rerank 可以改善 Top-k 和 MRR。

当前最强 benchmark 结果来自 Closure `61..100` frozen held-out aggregate。在 38 个 held-out bugs 上，selective rerank 调用 11 次 LLM，将 Top-1 从 0.3947 提升到 0.5526，Top-5 从 0.6053 提升到 0.7632，Top-10 从 0.7105 提升到 0.8421，MRR 从 0.5080 提升到 0.6513。AboutWork committed-60 和 Easy Finance 的 case studies 进一步表明，该 retrieval + selector + rerank 框架可以迁移到真实项目 bug records。

同时，本文结果也给出了清晰限制。LLM rerank 无法补救 candidate retrieval miss，例如 `Closure-98`；selector false negative 会使 hard case 未被 rerank；evidence/snippet 质量会直接影响 LLM 是否能识别真实文件，例如 `Closure-4`。Controlled agentic inspection 和 verifier rerank 并未在当前实验中超过 one-shot rerank，因此不应作为主方法。

总体而言，本文支持一个保守结论：selective evidence-aware LLM rerank 能以有限 LLM 调用改善文件级缺陷定位，但其效果依赖 candidate recall、selector recall 和 evidence quality。未来工作应优先改进 non-oracle selector recall、候选召回和 evidence construction，而不是简单增加 LLM 推理步骤。

## 未来工作草稿

后续工作可以从四个方向展开。

第一，改进 candidate recall。当前 retrieval miss 仍是 rerank 无法补救的硬上限。后续可以在新的 frozen protocol 中验证更稳健的 pass-chain、type-system、utility-file 和 code-output retrieval signals。

第二，改进 non-oracle selector recall。Closure frozen held-out aggregate 中 selector 只覆盖 6/15 个 baseline Top-5 failures。未来 selector 应在不使用 ground truth、fixed diff 或 post-fix source 的前提下，提高对 hard cases 的覆盖。

第三，改进 evidence construction。`Closure-4` 表明，候选文件存在但 snippet 未暴露关键方法时，LLM rerank 仍可能失败。后续可以系统研究 snippet selection、stack trace compaction、test source context 和 domain-specific high-signal terms 对 rerank 的影响。

第四，重新设计 agentic / verifier。当前 agentic inspection 可运行，但在 Easy Finance、Defects4J diagnostic mini-benchmark 和 AboutWork-60 上都没有稳定超过 one-shot；verifier 是 negative ablation。未来如果继续研究，应只针对 one-shot 失败且 evidence 明显不足的 case，并确保 verifier 接收比 agent output 更干净、更聚焦的证据。

## 不应主张的内容

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
