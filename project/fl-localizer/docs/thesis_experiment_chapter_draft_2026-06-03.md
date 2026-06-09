# 论文实验章节草稿：Selective Evidence-Aware LLM Fault Localization

日期：2026-06-08

本文档用于直接拆分到论文的实验设计、实验结果、RQ 回答、有效性威胁和复现说明章节。当前口径是：主实验已经足够支撑论文初稿，但不能声称完成了全量 Defects4J。

## 1. 实验目标

本实验研究文件级缺陷定位问题。给定一个 bug 的失败测试、stack trace、bug report、运行上下文和源码文件集合，系统输出最可能包含缺陷的文件排序。

本文方法称为：

```text
Selective Evidence-Aware LLM Fault Localization
```

方法流程为：

```text
bug context
-> BM25 / focused hybrid retrieval
-> deterministic evidence construction
-> selector decides whether to invoke LLM
-> one-shot DeepSeek rerank for selected cases
-> retrieval fallback for non-selected cases
-> file-level evaluation
```

Controlled agentic inspection 和 verifier rerank 不属于主方法，只作为 RQ5 扩展实验与消融实验。

## 2. 研究问题

RQ1：与 BM25 和 focused hybrid retrieval baseline 相比，LLM rerank 是否能提升 Defects4J 上的文件级 fault localization 效果？

RQ2：候选召回质量和 evidence 质量如何影响 LLM rerank？剩余失败主要来自 retrieval miss、selector false negative、snippet/evidence 问题，还是模型排序错误？

RQ3：selective rerank 能否减少 LLM 调用量、token 成本和运行时间，同时保留 Top-k 与 MRR 的主要收益？

RQ4：该方法能否从 Defects4J benchmark 迁移到真实项目数据，包括 AboutWork bug logs 和 Easy Finance git-history-derived bug records？

RQ5：controlled agentic inspection 和 verifier rerank 是否能在 one-shot rerank 之上进一步提升定位效果？如果不能，额外成本和失败原因是什么？

## 3. 数据集与实验范围

| Dataset | Role | Size | Status |
|---|---|---:|---|
| Defects4J pilot | 方法开发与跨项目 pilot | 120 bugs | completed |
| Closure-21..60 | fresh validation | 40 bugs | completed |
| Closure-61..100 | frozen held-out aggregate | 38 bugs | completed |
| Mockito fresh | selector validation | 17 usable bugs | completed |
| AboutWork committed-60 | real bug-log case study | 60 records | completed |
| Easy Finance clean63 / strict62 | real git-history case study + RQ5 | 63 / 62 records | completed |

Defects4J pilot 包含：

```text
Lang-20
Math-20
Chart-20
Time-20
Closure-20
Mockito-20
```

Mockito 在当前 Defects4J checkout 中 active bugs 只有 `1..38`，已经被 pilot 和 fresh validation 覆盖。因此没有新的 Mockito held-out slice 可跑。Closure 的 `61..100` 是当前最干净的 frozen held-out 主结果。

## 4. No-Leakage 规则

实验中严格区分输入信息和评价信息：

- 允许进入 retrieval / selector / prompt：bug report、失败测试、triggering tests、stack trace、buggy source、运行上下文、candidate file evidence。
- 只允许用于评价：ground truth modified classes/files、fixed commit、post-fix code、repair diff。
- selector 必须是 non-oracle，不能根据真实 rank、ground truth 或 fixed diff 决定是否调用 LLM。

`Closure-61..80` 和 `Closure-81..100` 都先写 frozen protocol，再运行 dataset build、retrieval、selector、rerank 和 evaluation。前一组 held-out 的 error analysis 没有反向修改后一组协议。

## 5. 主要结果

### 5.1 Defects4J Pilot

| Project | Best Current Setting | Bugs | Top-1 | Top-3 | Top-5 | MRR |
|---|---|---:|---:|---:|---:|---:|
| Lang | BM25 + DeepSeek rerank | 20 | 0.95 | 1.00 | 1.00 | 0.9750 |
| Math | Hybrid/direct + compact evidence DeepSeek | 20 | 0.90 | 0.95 | 1.00 | 0.9350 |
| Chart | Focused hybrid/direct | 20 | 0.85 | 0.95 | 1.00 | 0.9040 |
| Time | Focused hybrid/direct + DeepSeek hard4 | 20 | 0.90 | 1.00 | 1.00 | 0.9500 |
| Closure | Focused hybrid/direct + DeepSeek hard8 + pass-chain/type-cycle rules | 20 | 0.40 | 0.80 | 1.00 | 0.6225 |
| Mockito | Focused hybrid/direct + tight selector9 DeepSeek | 20 | 0.65 | 1.00 | 1.00 | 0.8000 |

Pilot 结果说明，LLM rerank 在多个 Defects4J 项目上都能提升文件级排序，尤其当候选池包含真实文件时，Top-5 改进明显。但这些 pilot 包含项目特定诊断和 targeted add-ons，因此主要用于方法开发和初步验证。

### 5.2 Fresh And Frozen Validation

| Dataset | Setting | Bugs | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Closure-21..60 | focused retrieval baseline | 40 | 0 | 0.3000 | 0.4250 | 0.5750 | 0.7250 | 0.4211 |
| Closure-21..60 | cost-control v3 + DeepSeek | 40 | 20 | 0.6000 | 0.8000 | 0.9750 | 1.0000 | 0.7348 |
| Closure-61..100 held-out | frozen retrieval baseline | 38 | 0 | 0.3947 | 0.5263 | 0.6053 | 0.7105 | 0.5080 |
| Closure-61..100 held-out | frozen cost-control v3 + DeepSeek | 38 | 11 | 0.5526 | 0.7105 | 0.7632 | 0.8421 | 0.6513 |
| Mockito-31..38 fresh | focused retrieval baseline | 8 | 0 | 0.1250 | 0.5000 | 0.7500 | 0.8750 | 0.3382 |
| Mockito-31..38 fresh | cost-control v2 + DeepSeek | 8 | 4 | 0.6250 | 1.0000 | 1.0000 | 1.0000 | 0.7500 |

Closure frozen held-out aggregate 是当前最干净的 Defects4J 主结果。它覆盖 `Closure-61..100` 的 38 个 usable bugs，selector 只调用 11 次 DeepSeek，Top-5 从 0.6053 提升到 0.7632，Top-10 从 0.7105 提升到 0.8421，MRR 从 0.5080 提升到 0.6513。

### 5.3 Cost And Selector Coverage

Closure frozen held-out aggregate:

```text
records: 38
selected: 11
selected_fraction: 0.2895
total_tokens: 408568
avg_total_tokens_per_selected_case: 37142.55
total_duration_seconds: 178.838
avg_duration_seconds_per_selected_case: 16.258
```

Selector coverage:

```text
baseline Top-5 failures: 15
selected among Top-5 failures: 6
baseline Top-10 failures: 11
selected among Top-10 failures: 5
retrieval Top-50 miss: Closure-98
```

解释：selected-case rerank 很强，但 selector recall 仍是主要瓶颈。`Closure-98` 是 candidate retrieval miss，真实文件没有进入 Top-50，LLM rerank 无法补救。

### 5.4 Real-Project Case Studies

AboutWork committed-60:

| Method | Selected Records | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 production top50 | 0 / 60 | 0.5667 | 0.8333 | 0.9167 | 0.9333 | 0.7015 |
| BM25 + selector_v3 + DeepSeek | 16 / 60 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 |

Easy Finance clean63:

| Method | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 production top50 | 0 | 0.3968 | 0.7302 | 0.8730 | 0.8730 | 0.5684 |
| BM25 + selector_v1 | 10 | 0.4603 | 0.7778 | 0.9524 | 1.0000 | 0.6450 |
| BM25 + selector_v1 UI evidence v2 | 10 | 0.4921 | 0.8095 | 0.9841 | 1.0000 | 0.6729 |

这些结果支持 RQ4：benchmark 中有效的 retrieval + selector + LLM rerank 模式可以迁移到真实项目。但 AboutWork 和 Easy Finance 的 selector 都是在当前数据上调出的 fitted case-study 策略，需要新增 bug logs 或新时间段 commit 验证泛化。AboutWork committed-60 中剩余两个 Top-10 miss 都是 selector false negative，说明真实项目上的下一步瓶颈仍是 selector recall。

### 5.5 Agentic And Verifier

Easy Finance strict62:

| Method | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| one-shot UI evidence v2 | 9 | 0.5000 | 0.8226 | 1.0000 | 1.0000 | 0.6817 |
| controlled agentic s2 | 9 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6831 |
| agentic s2 + verifier | 9 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6804 |

Token cost:

```text
one-shot strict62: 226860 tokens
agentic s2: 250481 tokens
agentic + verifier: 331050 tokens
verifier extra: 80569 tokens
```

Defects4J diagnostic mini-benchmark 进一步给出 benchmark-side RQ5 证据：one-shot DeepSeek 达到 Top-1 0.4000、Top-3 0.7000、Top-5 0.8000、MRR 0.5644；agentic DeepSeek 降到 Top-1 0.3000、Top-3 0.6000、Top-5 0.6000、MRR 0.4768；agentic + verifier 与 agentic 完全持平但总 token 达到 554133。

AboutWork committed-60 上也补跑了 agentic / verifier：

| Method | Selected Records | Model Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR | Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| one-shot DeepSeek | 16 / 60 | 16 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 519530 |
| agentic DeepSeek s2 | 16 / 60 | 40 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 440542 |
| agentic s2 + verifier | 16 / 60 | 56 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 589260 |

RQ5 结论是条件性/负向结果：controlled agentic inspection 技术上可运行，但 Easy Finance strict62、Defects4J diagnostic mini-benchmark 和 AboutWork committed-60 都没有证明它超过 one-shot rerank；verifier 增加 token 成本但没有提升 MRR 或 per-bug correct rank。因此 agentic/verifier 应作为扩展和消融讨论，不应作为主方法。

## 6. RQ 回答

### RQ1：LLM rerank 是否提升 Defects4J 文件级定位？

是，但前提是候选池中包含真实缺陷文件。Pilot 中多个项目达到 Top-5 1.00。更保守的 held-out 结果也支持正向结论：Closure frozen held-out aggregate 中，selective DeepSeek 将 Top-5 从 0.6053 提升到 0.7632，MRR 从 0.5080 提升到 0.6513。

### RQ2：候选召回和 evidence 质量如何影响结果？

影响很大。当前失败不再只是 BM25 排序弱，而是集中在三个位置：

- candidate retrieval miss：例如 `Closure-98` 不在 Top-50，LLM 无法补救。
- selector false negative：Closure aggregate 中 selector 只覆盖 6/15 个 baseline Top-5 failures。
- evidence/snippet 质量：Closure 的 type-cycle、pass-chain、code-output、UI evidence 等实验表明，相关 snippet 和 domain evidence 直接影响 rerank 是否能识别真实文件。

`Closure-4` 是一个清楚的 pilot 例子：真实文件 `NamedType.java` 原本就在候选池中，但只在 rank 49；初始 rerank 没有选中它。修复 snippet scoring、压缩重复 `PrototypeObjectType.isSubtype` 栈帧，并加入 type-cycle prompt rule 后，`NamedType.java` 被 DeepSeek 提到 rank 2。这说明 rerank 失败不一定来自模型无法推理，也可能来自 evidence package 没有暴露 `handleTypeCycle` 和 cycle warning 等关键信号。该例子只能作为 pilot method-evolution evidence，不能替代 Closure `61..100` frozen held-out 主结果。

### RQ3：selective rerank 是否能减少成本并保留收益？

可以。Closure frozen held-out 中只调用 11/38 次 LLM，却带来 Top-5 +0.1579 和 MRR +0.1434。AboutWork committed-60 只选择 16/60 条调用 DeepSeek，将 Top-1 从 0.5667 提升到 0.7000，将 MRR 从 0.7015 提升到 0.8117。Easy Finance clean63 只调用 10/63 次，将 Top-10 提升到 1.0000。

但 selector recall 是主要风险。当前结果支持 selective rerank 的成本收益，但也说明 selector 需要进一步泛化验证。

### RQ4：方法能否迁移到真实项目？

初步可以。AboutWork 和 Easy Finance 都显示 selector + one-shot LLM rerank 能提升真实项目 bug records 的 Top-k 和 MRR。

但结论必须保守：AboutWork committed-60 和 Easy Finance 都是 case study，且 selector/evidence 是在当前样本上调出的。它们支持迁移可行性，不构成强泛化证明。

### RQ5：agentic / verifier 是否优于 one-shot？

目前没有。Easy Finance strict62 上，controlled agentic s2 与 one-shot 基本持平，token 成本更高；verifier 额外消耗 80569 tokens，但 MRR 从 agent-only 的 0.6831 降到 0.6804。Defects4J diagnostic mini-benchmark 上，one-shot MRR 为 0.5644，而 agentic 和 agentic+verifier 都是 0.4768。AboutWork committed-60 上，one-shot、agentic 和 agentic+verifier 的 per-bug correct rank 完全一致，verifier 额外消耗 148718 tokens 但不改善结果。当前 verifier 是 negative ablation。

## 7. 有效性威胁

### 7.0 错误分析摘要

| Error Type | Representative Cases | Cause | Lesson |
|---|---|---|---|
| Recovered evidence/snippet miss | `Closure-4` pilot | Correct file was present at candidate rank 49, but the original evidence package omitted type-cycle signals. | Snippet and prompt quality can decide whether one-shot rerank succeeds. |
| Selector false negative | `Closure-67`, `Closure-75`, `Closure-88`, `Closure-99` | Correct file was in candidate pool, but selector did not call LLM. | Selector recall is the main bottleneck. |
| Candidate retrieval miss | `Closure-98` | Correct file was outside retrieval Top-50. | Rerank cannot fix absent candidates. |
| Utility-file ambiguity | `Closure-61`, `Closure-75`, `Closure-94` | Failure context points to compiler passes, but fix touches `NodeUtil.java`. | Shared helper files need better diagnostics. |
| Code-output evidence gap | `Closure-65` | `CodePrinter.java` ranked above `CodeGenerator.java`, but selector pattern did not fire. | Code-output selector is useful but too narrow. |
| Agentic/verifier cost | Easy Finance strict62; Defects4J RQ5 mini; AboutWork committed-60 | More LLM steps did not improve evidence quality or per-bug correct ranks. | Keep as RQ5 ablation, not main method. |

### 内部有效性

- Ground truth 来自 modified files/classes，可能包含非 root cause 修改。
- 多文件 bug 当前采用 any-hit file-level metric，命中任一 ground-truth file 即算成功，可能高估结果。
- Selector、prompt 和 snippet strategy 是方法的一部分，对 LLM 表现影响很大。
- Closure / Mockito pilot 中包含 targeted evidence add-ons，需要和 frozen held-out 主结果区分。
- 公司项目数据的 ground truth 可能受到重构、格式化或顺手修改影响。

### 外部有效性

- Defects4J 是 Java benchmark，不能直接代表其他语言、框架或工业代码库。
- Closure 是当前 held-out 主体，held-out 结论不能自动推广到所有 Defects4J 项目。
- Mockito 没有新的 unused active bugs 可做 held-out，因此只能作为 pilot + fresh validation。
- AboutWork committed-60 和 Easy Finance 是项目级 case study，样本量有限。
- DeepSeek API 模型版本可能变化，影响复现。

### 构造有效性

- 文件级定位比方法级、语句级或补丁定位更粗。
- Top-k accuracy 不能完全代表开发者真实调试成本。
- Merged selective-rerank 输出被截断到 Top-10，因此 Top-20/Top-50 candidate recall 应从 retrieval baseline 报告，不能从 merged output 解读。
- Token cost 与 prompt 缓存、模型版本、API 状态相关。

### 结论有效性

- 当前已完成约 215 个 usable Defects4J records，但不是全量 Defects4J。
- Closure frozen held-out aggregate 支持主方法，但 selector recall 仍不足。
- 公司项目结果是 case-study evidence，不能作为广泛工业泛化证明。
- Agentic/verifier 目前有 Easy Finance strict62、Defects4J diagnostic mini-benchmark 和 AboutWork committed-60 三组证据；其中 Defects4J mini 是诊断集，不是无偏 held-out 泛化估计。

## 8. 不应主张的内容

不要写：

```text
We completed all Defects4J experiments.
The method is proven to work across all projects.
Agentic/verifier improves over one-shot rerank.
The selector is fully generalized.
```

可以写：

```text
We completed a 120-bug Defects4J pilot, additional fresh validation, and a frozen Closure held-out validation over 38 bugs.
The results show that selective evidence-aware LLM reranking improves file-level localization when candidate recall is sufficient.
The main remaining limitations are selector recall, candidate recall, and evidence quality.
Controlled agentic inspection is feasible but not yet clearly better than one-shot rerank; verifier is currently a negative ablation.
```

## 9. 复现说明

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

Closure frozen held-out protocol:

```text
docs/frozen_protocol_2026-06-01.md
docs/frozen_protocol_2026-06-02_closure_81_100.md
```

关键输出：

```text
outputs/closure_heldout_61_80_hybrid_focused_direct_passchain_typesystem_top50_eval.json
outputs/closure_heldout_61_80_merged_deepseek_closure_cost_control_v3_s12_ctx12000_top50_eval.json
outputs/closure_heldout_81_100_hybrid_focused_direct_passchain_typesystem_top50_eval.json
outputs/closure_heldout_81_100_merged_deepseek_closure_cost_control_v3_s12_ctx12000_top50_eval.json
docs/closure_frozen_heldout_61_100_summary.md
```

复现时需要：

- 本地 Defects4J checkout 和对应 workspaces。
- DeepSeek API key。
- 固定 protocol 文件中的 selector 和 rerank 参数。
- 明确区分 retrieval candidate recall 与 merged Top-10 输出指标。

## 10. 总结

当前实验设计是合理的，足以支撑论文主实验初稿。最强的可报告主结果是 Closure frozen held-out aggregate：38 个 held-out bugs，11 次 LLM 调用，Top-5 从 0.6053 提升到 0.7632，MRR 从 0.5080 提升到 0.6513。

论文结论应聚焦于：

```text
Selective evidence-aware LLM rerank can improve file-level fault localization with limited LLM calls,
provided that candidate retrieval contains the faulty file and evidence construction exposes useful signals.
```

同时要明确：当前主要瓶颈是 selector recall、candidate recall 和 evidence quality，而不是单纯缺少更多 LLM 推理步骤。
