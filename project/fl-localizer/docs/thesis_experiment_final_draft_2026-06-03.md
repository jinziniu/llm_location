# 论文实验章节定稿草案

日期：2026-06-08

本章评估本文提出的 selective evidence-aware LLM fault localization 方法。实验目标不是完成全量 Defects4J，而是在可复现 benchmark、fresh / frozen validation 和真实项目 case study 上回答：LLM rerank 是否能改善文件级缺陷定位、选择性调用是否能控制成本，以及 agentic / verifier 是否值得作为主方法。

## 4. 实验设计

### 4.1 研究问题

本文围绕五个研究问题展开：

| RQ | Question |
|---|---|
| RQ1 | 与 BM25 和 focused hybrid retrieval baseline 相比，LLM rerank 是否能提升 Defects4J 文件级定位效果？ |
| RQ2 | 候选召回质量和 evidence 质量如何影响 LLM rerank？剩余失败主要来自 retrieval miss、selector false negative、snippet/evidence 问题，还是模型排序错误？ |
| RQ3 | selective rerank 能否减少 LLM 调用量、token 成本和运行时间，同时保留 Top-k 与 MRR 收益？ |
| RQ4 | 该方法能否从 Defects4J benchmark 迁移到 AboutWork 和 Easy Finance 等真实项目数据？ |
| RQ5 | controlled agentic inspection 和 verifier rerank 是否能在 one-shot rerank 之上进一步提升定位效果？ |

### 4.2 方法边界

本文主方法是 selective one-shot rerank。流程如下：

```text
bug context
-> focused hybrid retrieval
-> deterministic evidence construction
-> selective rerank gate
-> one-shot DeepSeek rerank for selected cases
-> retrieval fallback for non-selected cases
-> file-level evaluation
```

Controlled agentic inspection 和 verifier rerank 不属于主方法。它们只作为 RQ5 的扩展实验和消融实验单独报告。

### 4.3 数据集

表 4-1 给出实验数据范围。Defects4J pilot 用于方法开发和跨项目初步验证；Closure `61..100` frozen held-out aggregate 是当前最干净的 benchmark 主结果；AboutWork 和 Easy Finance 用于真实项目迁移 case study。

表 4-1：实验数据集

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

### 4.4 No-Leakage Protocol

实验严格区分输入信息和评价信息。允许进入 retrieval、selector、prompt 和 agent tools 的信息包括 bug report、失败测试、triggering tests、stack trace、buggy source 和 deterministic candidate evidence。Ground truth modified files、fixed commit、post-fix source 和 repair diff 只用于评价，不进入 prompt、selector 或 agent tools。

Closure `61..80` 和 `81..100` 均先写 frozen protocol，再运行 dataset build、retrieval、selector、rerank 和 evaluation。前一组 held-out error analysis 不反向修改后一组 held-out protocol。

### 4.5 评价指标

本文使用文件级 Top-k accuracy 和 MRR：

```text
Top-k = whether any ground-truth file appears in the top-k files
MRR = average(1 / rank_of_first_correct_file)
```

对于多文件 bug，当前采用 any-hit file-level definition：只要任一 ground-truth file 出现在 Top-k 中即算成功。该定义适合衡量开发者是否能在前几个文件中看到相关修复文件，但可能高估多文件 bug 的完整定位能力，因此在有效性威胁中单独讨论。

对于 selective rerank，merged output 被截断到 Top-10。因此 Top-20 / Top-50 candidate recall 必须从 retrieval baseline 输出解释，不能从 merged Top-10 输出解读。

## 5. 实验结果

### 5.1 RQ1：Defects4J 上 LLM Rerank 是否提升定位效果？

表 5-1 展示六个 Defects4J pilot 项目的当前最好结果。Pilot 结果说明，LLM rerank 能作为第二阶段排序器改善文件级定位，尤其在候选池包含真实文件时效果明显。Closure 和 Mockito 更难，它们推动了 pass-chain、type-cycle、ByteBuddy / MockMaker 等 evidence rule 的设计。

表 5-1：Defects4J pilot 当前最好结果

| Project | Best Current Setting | Bugs | Top-1 | Top-3 | Top-5 | MRR |
|---|---|---:|---:|---:|---:|---:|
| Lang | BM25 + DeepSeek rerank | 20 | 0.95 | 1.00 | 1.00 | 0.9750 |
| Math | Hybrid/direct + compact evidence DeepSeek | 20 | 0.90 | 0.95 | 1.00 | 0.9350 |
| Chart | Focused hybrid/direct | 20 | 0.85 | 0.95 | 1.00 | 0.9040 |
| Time | Focused hybrid/direct + DeepSeek hard4 | 20 | 0.90 | 1.00 | 1.00 | 0.9500 |
| Closure | Focused hybrid/direct + DeepSeek hard8 + pass-chain/type-cycle rules | 20 | 0.40 | 0.80 | 1.00 | 0.6225 |
| Mockito | Focused hybrid/direct + tight selector9 DeepSeek | 20 | 0.65 | 1.00 | 1.00 | 0.8000 |

这些 pilot 包含 targeted evidence add-ons，因此不作为最终泛化证明。更保守的 benchmark 结论来自 Closure frozen held-out aggregate。

表 5-2：Closure frozen held-out aggregate

| Dataset | Setting | Bugs | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Closure-61..100 | frozen retrieval baseline | 38 | 0 | 0.3947 | 0.5263 | 0.6053 | 0.7105 | 0.5080 |
| Closure-61..100 | frozen cost-control v3 + DeepSeek | 38 | 11 | 0.5526 | 0.7105 | 0.7632 | 0.8421 | 0.6513 |

在 Closure `61..100` 的 38 个 frozen held-out bugs 上，selective DeepSeek 将 Top-1 从 0.3947 提升到 0.5526，Top-5 从 0.6053 提升到 0.7632，MRR 从 0.5080 提升到 0.6513。因此，RQ1 的回答是：LLM rerank 能提升 Defects4J 文件级定位，但前提是候选池包含真实缺陷文件。

### 5.2 RQ2：候选召回和 Evidence 质量如何影响结果？

当前剩余失败主要集中在三类上游问题。

第一类是 candidate retrieval miss。如果真实文件不在 candidate pool 中，LLM rerank 无法恢复。例如 `Closure-98` 是 Closure frozen held-out aggregate 中的 Top-50 retrieval miss。

第二类是 selector false negative。Closure `61..100` aggregate 中，baseline Top-5 failures 一共有 15 个，但 selector 只覆盖 6 个；baseline Top-10 failures 一共有 11 个，selector 只覆盖 5 个。这说明 selected-case rerank 本身有效，但 selector recall 仍不足。

第三类是 evidence/snippet 不足。`Closure-4` 是一个清楚的 pilot 例子：真实文件 `NamedType.java` 已经在候选池中，但位于 rank 49；初始 rerank 没有选中它。修复 snippet scoring、压缩重复 `PrototypeObjectType.isSubtype` 栈帧，并加入 type-cycle prompt rule 后，`NamedType.java` 被 DeepSeek 提到 rank 2。该例子说明 rerank 失败不一定来自模型无法推理，也可能来自 evidence package 没有暴露 `handleTypeCycle` 和 cycle warning 等关键信号。它应作为 pilot method-evolution evidence，而不是 frozen held-out proof。

### 5.3 RQ3：Selective Rerank 是否降低成本并保留收益？

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

### 5.4 RQ4：方法能否迁移到真实项目？

表 5-3 展示两个真实项目 case study。AboutWork 使用真实 bug logs；Easy Finance 使用 git-history-derived records。

表 5-3：真实项目 case study

| Dataset | Method | Selected Records | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---|---:|---:|---:|---:|---:|---:|
| AboutWork committed-60 | BM25 production top50 | 0 / 60 | 0.5667 | 0.8333 | 0.9167 | 0.9333 | 0.7015 |
| AboutWork committed-60 | BM25 + selector_v3 + DeepSeek | 16 / 60 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 |
| Easy Finance clean63 | BM25 production top50 | 0 / 63 | 0.3968 | 0.7302 | 0.8730 | 0.8730 | 0.5684 |
| Easy Finance clean63 | BM25 + selector_v1 UI evidence v2 | 10 / 63 | 0.4921 | 0.8095 | 0.9841 | 1.0000 | 0.6729 |

这些结果说明，benchmark 中有效的 retrieval + selector + rerank 框架可以迁移到真实项目 bug records。但该结论必须保守：AboutWork 和 Easy Finance 仍是 case studies，且 selector/evidence strategy 是在当前样本上调出的。它们支持迁移可行性，不构成强泛化证明。AboutWork committed-60 的剩余两个 Top-10 miss 都是 selector false negative，说明真实项目上的主要瓶颈仍是 selector recall。

### 5.5 RQ5：Agentic / Verifier 是否优于 One-Shot？

表 5-4 展示 Easy Finance strict62 上的 RQ5 ablation。

表 5-4：Agentic / verifier ablation on Easy Finance strict62

| Method | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR | Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| one-shot UI evidence v2 | 9 | 0.5000 | 0.8226 | 1.0000 | 1.0000 | 0.6817 | 226860 |
| controlled agentic s2 | 9 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6831 | 250481 |
| agentic s2 + verifier | 9 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6804 | 331050 |

表 5-5 进一步在 Defects4J 上做一个 diagnostic mini-benchmark。该 mini-benchmark 包含 10 个已知诊断类别 case，包括 state-reset evidence、type-cycle evidence、pass-chain retrieval boundary、selector false negative、utility-file ambiguity、retrieval boundary negative 和 Mockito pattern generalization。该结果用于回答 RQ5 的扩展行为，不替代 Closure `61..100` frozen held-out 主结果。

表 5-5：Agentic / verifier ablation on Defects4J diagnostic mini-benchmark

| Method | API Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR | Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| retrieval baseline top50 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.2000 | 0.0534 | 0 |
| one-shot DeepSeek | 10 | 0.4000 | 0.7000 | 0.8000 | 0.9000 | 0.5644 | 345937 |
| agentic DeepSeek | 32 | 0.3000 | 0.6000 | 0.6000 | 0.8000 | 0.4768 | 441952 |
| agentic + verifier DeepSeek | 42 | 0.3000 | 0.6000 | 0.6000 | 0.8000 | 0.4768 | 554133 |

Defects4J mini-benchmark 的 per-bug rank 显示，one-shot 在 `Math-14`、`Closure-65`、`Mockito-26`、`Mockito-28` 上达到 rank 1，在 `Closure-13` 上达到 rank 3，在 `Closure-67` 和 `Closure-75` 上达到 rank 2。Agentic inspection 没有新增成功，反而将 `Math-12` 从 one-shot rank 9 降到 top10 miss，并将 `Closure-4`、`Closure-13`、`Mockito-28` 往后排。Verifier 额外消耗 112181 tokens，但输出与 agentic 相同。

表 5-6 在 AboutWork committed-60 上补充同一结论。为避免混淆，表中区分 selected records 和 model calls：one-shot 每条一次模型调用，agentic 每条可能包含多步工具决策和最终排序，verifier 是额外检查 pass。

表 5-6：Agentic / verifier ablation on AboutWork committed-60

| Method | Selected Records | Model Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR | Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| one-shot DeepSeek | 16 / 60 | 16 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 519530 |
| agentic DeepSeek s2 | 16 / 60 | 40 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 440542 |
| agentic s2 + verifier | 16 / 60 | 56 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 589260 |

AboutWork-60 上 one-shot、agentic 和 agentic + verifier 的 per-bug correct rank 完全一致。Verifier 额外消耗 148718 tokens 和 196.194 秒，但没有改善任何 aggregate 指标或 per-bug rank。

因此，RQ5 的回答是：controlled agentic inspection 技术上可运行，并能产生可分析 trace；但 Easy Finance strict62、Defects4J diagnostic mini-benchmark 和 AboutWork committed-60 都没有证明 agentic / verifier 优于 one-shot rerank。Verifier 在当前设计下是 negative ablation，不应作为主方法。

## 6. 讨论

### 6.1 主要发现

第一，LLM rerank 适合做第二阶段排序，而不是替代 retrieval。实验反复显示，只要真实文件进入候选池，LLM 能利用 failure context 和 source evidence 改善文件排序。

第二，selective invocation 是成本控制关键。全量调用 LLM 成本高，且很多简单样例 retrieval 已经能排到 Top-1。Selector 的作用是把 LLM 预算集中到低置信、证据冲突或语义复杂的样例上。

第三，当前最重要的瓶颈已经从 BM25 排序转为 selector recall、candidate recall 和 evidence quality。Closure aggregate 中 selected-case rerank 很强，但 selector 未覆盖大量 baseline Top-5 failures。

第四，更多 LLM 推理步骤并不必然提高定位质量。如果 evidence 输入不干净，verifier 甚至可能放大 top-10 中的噪声候选。

### 6.2 错误分析

表 6-1 总结当前主要错误类型。

表 6-1：错误分析摘要

| Error Type | Representative Cases | Cause | Lesson |
|---|---|---|---|
| Recovered evidence/snippet miss | `Closure-4` pilot | Faulty file was present at candidate rank 49, but the original snippet omitted type-cycle evidence. | Evidence construction can determine whether one-shot rerank succeeds. |
| Selector false negative | `Closure-67`, `Closure-75`, `Closure-88`, `Closure-99` | Correct file was in candidate pool, but selector did not call LLM. | Selector recall is the main bottleneck. |
| Candidate retrieval miss | `Closure-98` | Correct file was outside retrieval Top-50. | Rerank cannot fix absent candidates. |
| Utility-file ambiguity | `Closure-61`, `Closure-75`, `Closure-94` | Failure context points to compiler passes, but fix touches `NodeUtil.java`. | Shared helper files need better non-oracle diagnostics. |
| Code-output evidence gap | `Closure-65` | `CodePrinter.java` ranked above `CodeGenerator.java`, but selector pattern did not fire. | Code-output selector is useful but too narrow. |
| Agentic/verifier cost | Easy Finance strict62; Defects4J RQ5 mini; AboutWork committed-60 | More LLM steps did not improve evidence quality or per-bug correct ranks. | Keep as RQ5 ablation, not main method. |

这些错误并不主要来自 LLM 输出格式无效或模型完全无法排序，而是集中在上游 retrieval、evidence construction 和 selector coverage。后续如果继续补强实验，应优先改进 non-oracle selector recall 和 candidate recall，而不是简单增加推理步骤。

## 7. 有效性威胁

内部有效性方面，ground truth 来自 modified files/classes，可能包含非 root cause 修改。尤其在真实项目 git-history-derived cases 中，fix commit 可能同时包含重构、格式化或顺手修改。Prompt、snippet 和 selector 也是方法的一部分，对 LLM 表现影响显著。Closure 和 Mockito pilot 中包含 targeted evidence add-ons，因此需要和 frozen held-out 主结果分开解释。

构造有效性方面，当前指标是文件级 Top-k，而不是方法级、语句级或补丁级定位。对于多文件 bug，本文使用 any-hit file-level definition，可能高估完整定位能力。Merged selective-rerank 输出被截断到 Top-10，因此 Top-20 / Top-50 candidate recall 应从 retrieval baseline 报告。

外部有效性方面，Defects4J 是 Java benchmark，不能直接代表其他语言或工业项目。Closure 是当前 held-out 主体，因此 held-out 结论主要代表 Closure，不应自动推广到全部 Defects4J。AboutWork committed-60 和 Easy Finance 是真实项目 case studies，但样本量有限，且 selector/evidence 仍需新增样本验证。

结论有效性方面，当前约完成 215 个 usable Defects4J records，但不是全量 Defects4J。Closure frozen held-out aggregate 支持主方法，但 selector recall 仍不足。Agentic/verifier 当前有 Easy Finance strict62、Defects4J diagnostic mini-benchmark 和 AboutWork committed-60 三组证据；其中 Defects4J mini 是按已知失败类别构造的诊断集，不是无偏 held-out 泛化估计。

## 8. 复现说明

核心脚本如下：

```text
scripts/build_defects4j_dataset.py
scripts/run_hybrid_retrieval.py
scripts/select_rerank_candidates.py
scripts/run_llm_rerank.py
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
docs/thesis_consistency_review_2026-06-03.md
```

复现需要本地 Defects4J checkout、对应 bug workspaces、DeepSeek API key，以及 frozen protocol 中固定的 retrieval、selector 和 rerank 参数。

## 9. 小结

实验表明，selective evidence-aware LLM rerank 能在有限 LLM 调用下提升文件级缺陷定位效果。在 Closure frozen held-out aggregate 的 38 个 bugs 上，该方法只调用 11 次 LLM，将 Top-5 从 0.6053 提升到 0.7632，将 MRR 从 0.5080 提升到 0.6513。真实项目 AboutWork committed-60 和 Easy Finance 的 case studies 进一步表明，该 retrieval + selector + rerank 框架可以迁移到真实 bug records：AboutWork-60 只选择 16/60 条调用 DeepSeek，将 Top-1 从 0.5667 提升到 0.7000，将 MRR 从 0.7015 提升到 0.8117。当前主要限制是 selector recall、candidate recall 和 evidence quality；controlled agentic inspection 可运行但没有清晰优于 one-shot rerank，verifier 当前是负向消融结果。
