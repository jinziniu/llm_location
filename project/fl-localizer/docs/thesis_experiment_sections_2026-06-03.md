# 论文实验正文拆分稿

日期：2026-06-08

本文档把 `docs/thesis_experiment_chapter_draft_2026-06-03.md` 进一步拆成论文正文可直接使用的小节。写作口径保持保守：本文完成的是 Defects4J pilot、fresh validation 和 Closure frozen held-out validation，不是全量 Defects4J。

## 4. 实验设计

### 4.1 实验目的

本文实验旨在评估一种面向文件级缺陷定位的 selective evidence-aware LLM rerank 方法。给定 bug report、失败测试、triggering tests、stack trace 和 buggy source files，系统输出最可能包含缺陷的文件排序。实验关注三个核心问题：第一，LLM rerank 是否能在传统检索方法基础上提升文件级定位效果；第二，选择性调用 LLM 是否能在降低 token 成本的同时保留主要准确率收益；第三，该方法是否能从 Defects4J benchmark 迁移到真实项目 bug records。

本文主方法由四个阶段组成：

```text
focused hybrid retrieval
-> deterministic evidence construction
-> selective rerank gate
-> one-shot DeepSeek rerank with retrieval fallback
```

其中 controlled agentic inspection 和 verifier rerank 不属于主方法。它们只作为扩展实验和消融实验，用于回答 RQ5。

### 4.2 数据集

实验数据分为 benchmark 数据和真实项目数据两类。

Benchmark 数据使用 Defects4J。当前实验完成了六个项目的 pilot，每个项目 20 个 bugs：

```text
Lang-20
Math-20
Chart-20
Time-20
Closure-20
Mockito-20
```

此外，本文补充了 Closure 和 Mockito 的 fresh / held-out validation：

| Dataset | Role | Size |
|---|---|---:|
| Closure-21..60 | fresh validation | 40 |
| Closure-61..100 | frozen held-out aggregate | 38 |
| Mockito-21..30 | fresh attempt | 9 usable |
| Mockito-31..38 | fresh validation | 8 |

Mockito 在当前 Defects4J checkout 中 active bugs 只有 `1..38`，已经全部被 pilot 和 fresh validation 覆盖，因此无法再构造新的 Mockito held-out slice。

真实项目数据包括：

| Dataset | Source | Size | Purpose |
|---|---|---:|---|
| AboutWork committed-60 | company bug logs | 60 | RQ4 real bug-log transfer; RQ5 extension |
| Easy Finance clean63 | git-history-derived records | 63 | RQ4 real repository transfer |
| Easy Finance strict62 | filtered git-history records | 62 | RQ5 agentic / verifier ablation |
| Defects4J RQ5 mini | diagnostic Defects4J cases | 10 | RQ5 benchmark-side ablation |

### 4.3 Baseline 与实验方法

本文比较以下方法：

| Method | Description |
|---|---|
| BM25 | 使用 bug report、失败测试、stack trace 等文本检索候选文件 |
| Focused hybrid retrieval | 在 BM25 基础上加入 stack trace、direct class hints、pass-chain/type-system 等 deterministic signals |
| One-shot DeepSeek rerank | 对候选文件和 evidence package 做一次 LLM rerank |
| Selective DeepSeek rerank | 只对 selector 认为困难或低置信的样例调用 LLM |
| Controlled agentic inspection | 在固定 candidate pool 内允许 LLM 使用有限工具检查文件 |
| Verifier rerank | 在 agent 输出后做独立 verifier pass |

主结果报告 selective one-shot DeepSeek rerank。Agentic 和 verifier 单独报告，不与主方法混合。

### 4.4 评价指标

本文使用文件级 Top-k accuracy 和 MRR：

```text
Top-k = whether any ground-truth file appears in the top-k files
MRR = average(1 / rank_of_first_correct_file)
```

对于多文件修改的 bug，当前指标采用 any-hit file-level definition：只要任一 ground-truth file 出现在 Top-k 中即算成功。该指标适合评价“开发者是否能在前几个文件中看到一个相关修复文件”，但可能高估多文件 bug 的完整定位能力，因此在有效性威胁中单独讨论。

此外，实验报告 LLM calls、token usage、runtime 和 selector selected fraction。对于 selective rerank，merged output 被截断为 Top-10，因此 Top-20 / Top-50 candidate recall 必须从 retrieval baseline 输出解释，不能从 merged Top-10 输出解释。

### 4.5 No-Leakage Protocol

实验严格区分输入信息和评价信息。允许进入 retrieval、selector 和 prompt 的信息包括 bug report、失败测试、triggering tests、stack trace、buggy source 和 deterministic evidence。Ground truth modified files、fixed commit、post-fix source 和 repair diff 只用于评价，不进入 prompt、selector 或 agent tools。

Closure `61..80` 和 `81..100` 均先写 frozen protocol，再运行数据构建、retrieval、selector、rerank 和 evaluation。前一轮 held-out error analysis 不反向修改后一轮 held-out protocol。

## 5. 实验结果

### 5.1 RQ1：LLM rerank 是否提升 Defects4J 文件级定位？

Defects4J pilot 显示，retrieval + LLM rerank 在六个项目上均能提升文件级定位表现。尤其在 Lang、Math、Chart 和 Time 上，当前最好结果均达到 Top-5 1.00。Closure 和 Mockito 更难，推动了 pass-chain、type-system、ByteBuddy/MockMaker 等 evidence rule 的设计。

| Project | Best Current Setting | Bugs | Top-1 | Top-3 | Top-5 | MRR |
|---|---|---:|---:|---:|---:|---:|
| Lang | BM25 + DeepSeek rerank | 20 | 0.95 | 1.00 | 1.00 | 0.9750 |
| Math | Hybrid/direct + compact evidence DeepSeek | 20 | 0.90 | 0.95 | 1.00 | 0.9350 |
| Chart | Focused hybrid/direct | 20 | 0.85 | 0.95 | 1.00 | 0.9040 |
| Time | Focused hybrid/direct + DeepSeek hard4 | 20 | 0.90 | 1.00 | 1.00 | 0.9500 |
| Closure | Focused hybrid/direct + DeepSeek hard8 + pass-chain/type-cycle rules | 20 | 0.40 | 0.80 | 1.00 | 0.6225 |
| Mockito | Focused hybrid/direct + tight selector9 DeepSeek | 20 | 0.65 | 1.00 | 1.00 | 0.8000 |

更保守的 frozen held-out 结果来自 Closure `61..100`。在 38 个 held-out bugs 上，selective DeepSeek 将 Top-5 从 0.6053 提升到 0.7632，MRR 从 0.5080 提升到 0.6513。

| Dataset | Setting | Bugs | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Closure-61..100 | frozen retrieval baseline | 38 | 0 | 0.3947 | 0.5263 | 0.6053 | 0.7105 | 0.5080 |
| Closure-61..100 | frozen cost-control v3 + DeepSeek | 38 | 11 | 0.5526 | 0.7105 | 0.7632 | 0.8421 | 0.6513 |

结论：LLM rerank 能提升文件级定位，但前提是候选池中包含真实缺陷文件。

### 5.2 RQ2：候选召回和 evidence 质量如何影响结果？

实验表明，当前失败主要来自三类原因。

第一类是 retrieval miss。如果真实文件不在 candidate pool 中，LLM rerank 无法恢复。例如 Closure frozen held-out aggregate 中 `Closure-98` 是 Top-50 retrieval miss。

第二类是 selector false negative。Closure `61..100` aggregate 中，baseline Top-5 failures 一共有 15 个，但 selector 只覆盖 6 个；baseline Top-10 failures 一共有 11 个，selector 只覆盖 5 个。这说明 selected-case rerank 本身有效，但 selector recall 仍不足。

第三类是 evidence/snippet 不足。Closure 的 pass-chain、type-system、code-output 规则，以及 Easy Finance 的 UI evidence v2 都表明，LLM rerank 的效果依赖于 prompt 中是否包含正确的代码片段和语义线索。

一个具体 pilot 例子是 `Closure-4`。真实文件 `NamedType.java` 已经在 retrieval candidate pool 中，但位于 rank 49；初始 rerank 没有选中它。修复 snippet scoring、压缩重复 `PrototypeObjectType.isSubtype` 栈帧，并在 prompt 中加入 type-cycle 规则后，`NamedType.java` 被 DeepSeek 提到 rank 2。这个例子说明问题不是“多调用一次 LLM”本身，而是 prompt 是否真正暴露了 `handleTypeCycle` 和 cycle warning 等关键证据。

需要注意，`Closure-4` 应作为 pilot method-evolution case，而不是 frozen held-out proof。主结论仍应优先使用 Closure `61..100` 的冻结 held-out aggregate。

### 5.3 RQ3：selective rerank 能否降低成本并保留收益？

可以。Closure frozen held-out aggregate 只调用 11/38 次 LLM：

```text
selected_fraction: 0.2895
total_tokens: 408568
avg_total_tokens_per_selected_case: 37142.55
total_duration_seconds: 178.838
avg_duration_seconds_per_selected_case: 16.258
```

在该调用预算下，Top-5 提升 +0.1579，Top-10 提升 +0.1316，MRR 提升 +0.1434。

AboutWork 和 Easy Finance 也支持 selective invocation 的成本收益。AboutWork committed-60 只选择 16/60 条调用 one-shot DeepSeek，使 Top-1 从 0.5667 提升到 0.7000，Top-3 从 0.8333 提升到 0.9500，MRR 从 0.7015 提升到 0.8117。Easy Finance clean63 只调用 10/63 次，使 Top-10 从 0.8730 提升到 1.0000。

### 5.4 RQ4：方法能否迁移到真实项目？

AboutWork 结果如下：

| Method | Selected Records | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 production top50 | 0 / 60 | 0.5667 | 0.8333 | 0.9167 | 0.9333 | 0.7015 |
| BM25 + selector_v3 + DeepSeek | 16 / 60 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 |

Easy Finance clean63 结果如下：

| Method | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 production top50 | 0 | 0.3968 | 0.7302 | 0.8730 | 0.8730 | 0.5684 |
| BM25 + selector_v1 | 10 | 0.4603 | 0.7778 | 0.9524 | 1.0000 | 0.6450 |
| BM25 + selector_v1 UI evidence v2 | 10 | 0.4921 | 0.8095 | 0.9841 | 1.0000 | 0.6729 |

这些结果说明，benchmark 中有效的 retrieval + selector + rerank 框架可以迁移到真实项目 bug records。但这些真实项目结果仍是 case study，selector 和 evidence strategy 是在当前样本上调出的，需要新增 bug logs 或新时间段 commit 验证泛化。AboutWork committed-60 的剩余两个 Top-10 miss 都是 selector false negative，而不是 selected-case DeepSeek 排序失败。

### 5.5 RQ5：agentic / verifier 是否优于 one-shot rerank？

当前没有证据表明它们优于 one-shot rerank。Easy Finance strict62 上结果如下：

| Method | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| one-shot UI evidence v2 | 9 | 0.5000 | 0.8226 | 1.0000 | 1.0000 | 0.6817 |
| controlled agentic s2 | 9 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6831 |
| agentic s2 + verifier | 9 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6804 |

Token cost:

```text
one-shot strict62: 226860
agentic s2: 250481
agentic + verifier: 331050
verifier extra: 80569
```

AboutWork committed-60 上也补跑了相同 selected set 的 agentic / verifier 扩展：

| Method | Selected Records | Model Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR | Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| one-shot DeepSeek | 16 / 60 | 16 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 519530 |
| agentic DeepSeek s2 | 16 / 60 | 40 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 440542 |
| agentic s2 + verifier | 16 / 60 | 56 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 589260 |

Agentic inspection 技术上可运行，但在 Easy Finance strict62、Defects4J diagnostic mini-benchmark 和 AboutWork committed-60 上都没有稳定超过 one-shot rerank。AboutWork-60 中 one-shot、agentic 和 agentic + verifier 的 per-bug correct rank 完全一致；verifier 额外增加 148718 tokens，但没有改善任何 aggregate 指标。因此当前 verifier 是 negative ablation，不应作为主方法。

## 6. 讨论

### 6.1 主要发现

第一，LLM rerank 适合做第二阶段排序，而不是替代 retrieval。实验反复显示，只要真实文件进入候选池，LLM 能利用 failure context 和 source evidence 改善文件排序。

第二，selective invocation 是成本控制关键。全量调用 LLM 成本高，且很多简单样例 retrieval 已经能排到 Top-1。Selector 的作用是把 LLM 预算集中到低置信、证据冲突或语义复杂的样例上。

第三，当前最重要的瓶颈已经从 BM25 排序转为 selector recall、candidate recall 和 evidence quality。Closure aggregate 中 selected-case rerank 很强，但 selector 未覆盖大量 baseline Top-5 failures。

第四，agentic/verifier 不应自动被认为更强。当前实验表明，更多推理步骤和更多 token 并不必然提高定位质量；如果 evidence 输入不干净，verifier 甚至可能放大 top-10 噪声。

### 6.2 错误分析

| Error Type | Representative Cases | Cause | Lesson |
|---|---|---|---|
| Recovered evidence/snippet miss | `Closure-4` pilot | Faulty file was present at candidate rank 49, but the original snippet omitted type-cycle evidence. | Evidence construction can determine whether one-shot rerank succeeds. |
| Selector false negative | `Closure-67`, `Closure-75`, `Closure-88`, `Closure-99` | Correct file was in candidate pool, but selector did not call LLM. | Selector recall is the main bottleneck. |
| Candidate retrieval miss | `Closure-98` | Correct file was outside retrieval Top-50. | Rerank cannot fix absent candidates. |
| Utility-file ambiguity | `Closure-61`, `Closure-75`, `Closure-94` | Failure context points to compiler passes, but fix touches `NodeUtil.java`. | Shared helper files need better non-oracle diagnostics. |
| Semantic pass-family mismatch | `Closure-67` | Direct hints name related passes, not the actual changed file. | Pass-family evidence needs out-of-sample validation. |
| Code-output evidence gap | `Closure-65` | `CodePrinter.java` ranked above `CodeGenerator.java`, but selector pattern did not fire. | Code-output selector is useful but too narrow. |
| Mockito selector generalization | `Mockito-26`, `Mockito-28` | Fresh slice exposed primitive default-value and injection exact-type patterns. | Diagnostic rules should remain hypotheses unless frozen. |
| Agentic cost without clear gain | Easy Finance strict62; Defects4J RQ5 mini; AboutWork-60 | Tool use did not improve evidence quality enough to beat one-shot. | Keep agentic as RQ5 extension, not main method. |
| Verifier over-correction / no-op | Easy Finance strict62 verifier; AboutWork-60 verifier | Verifier did not receive cleaner evidence than agent output, or reproduced the same ranking. | Current verifier is a negative ablation. |

Overall, remaining errors are not dominated by invalid model outputs. They concentrate around upstream retrieval, evidence construction, and selection. Selected cases are usually reranked successfully, but many hard cases are not selected. This motivates future work on non-oracle selector recall and candidate recall rather than simply adding more LLM reasoning steps.

### 6.3 实验设计是否合理

当前设计合理，原因是它清楚区分了三类证据：

- Pilot：用于说明方法可行性和发现项目特定 failure modes。
- Fresh validation：用于检查 selector/evidence 的初步泛化。
- Frozen held-out：用于提供较干净的主方法验证。

同时，方法边界清楚：主方法是 selective one-shot rerank，agentic/verifier 是 RQ5 扩展，不混入主结果。

需要保守处理的是结论范围。本文不能声称完成了全量 Defects4J，也不能声称方法已经在所有项目、所有语言上泛化。当前最强结论应基于 Closure frozen held-out aggregate 和真实项目 case studies。

## 7. 有效性威胁

### 7.1 内部有效性

Ground truth 来自 modified files/classes，可能包含非 root cause 修改。尤其在真实项目 git-history-derived cases 中，fix commit 可能同时包含重构、格式化或顺手修改。

当前 file-level metric 使用 any-hit definition。对于多文件 bug，只要命中任一 ground-truth file 即算成功，可能高估完整定位能力。

Prompt、snippet、selector 是方法的一部分，对 LLM 表现影响显著。Closure 和 Mockito pilot 中包含 targeted evidence add-ons，因此需要和 frozen held-out 主结果分开解释。

### 7.2 外部有效性

Defects4J 是 Java benchmark，不能直接代表其他语言、框架或工业项目。Closure 是当前 held-out 主体，因此 held-out 结论主要代表 Closure，不应自动推广到全部 Defects4J。

Mockito active bugs 只有 `1..38`，无法构造新的 Mockito held-out slice。Mockito 结果应写成 pilot + fresh validation，而不是 held-out benchmark。

AboutWork committed-60 和 Easy Finance 是真实项目 case studies，但样本量有限，且 selector/evidence 仍需新增样本验证。

### 7.3 构造有效性

文件级定位比方法级或行级定位更粗。Top-k accuracy 不能完全代表开发者真实调试成本。

Merged selective-rerank 输出被截断到 Top-10，因此 Top-20/Top-50 candidate recall 应从 retrieval baseline 报告，不能从 merged output 解读。

Token cost 会受到 prompt 缓存、模型版本、API 状态和上下文长度影响。

### 7.4 结论有效性

当前约完成 215 个 usable Defects4J records，但不是全量 Defects4J。Closure frozen held-out aggregate 支持主方法，但 selector recall 仍不足。Agentic/verifier 当前有 Easy Finance strict62、Defects4J diagnostic mini-benchmark 和 AboutWork committed-60 三组证据；其中 Defects4J mini 是按已知失败类别构造的诊断集，不是无偏 held-out 泛化估计。

## 8. 复现说明

核心脚本：

```text
scripts/build_defects4j_dataset.py
scripts/run_hybrid_retrieval.py
scripts/select_rerank_candidates.py
scripts/run_llm_rerank.py
scripts/merge_selective_rerank.py
scripts/evaluate_predictions.py
scripts/summarize_llm_usage.py
```

关键 protocol：

```text
docs/frozen_protocol_2026-06-01.md
docs/frozen_protocol_2026-06-02_closure_81_100.md
```

关键结果文档：

```text
docs/closure_heldout_61_80_validation_report.md
docs/closure_heldout_81_100_validation_report.md
docs/closure_frozen_heldout_61_100_summary.md
docs/thesis_experiment_chapter_draft_2026-06-03.md
```

复现需要本地 Defects4J checkout、对应 bug workspaces、DeepSeek API key，以及 frozen protocol 中固定的 retrieval、selector 和 rerank 参数。

## 9. 可直接放入论文摘要的实验结论

实验表明，selective evidence-aware LLM rerank 能在有限 LLM 调用下提升文件级缺陷定位效果。在 Closure frozen held-out aggregate 的 38 个 bugs 上，该方法只调用 11 次 LLM，将 Top-5 从 0.6053 提升到 0.7632，将 MRR 从 0.5080 提升到 0.6513。真实项目 AboutWork committed-60 和 Easy Finance 的 case studies 进一步表明，该 retrieval + selector + rerank 框架可以迁移到真实 bug records：AboutWork-60 只选择 16/60 条调用 DeepSeek，将 Top-1 从 0.5667 提升到 0.7000，将 MRR 从 0.7015 提升到 0.8117。当前主要限制是 selector recall、candidate recall 和 evidence quality；controlled agentic inspection 可运行但没有清晰优于 one-shot rerank，verifier 当前是负向消融结果。
