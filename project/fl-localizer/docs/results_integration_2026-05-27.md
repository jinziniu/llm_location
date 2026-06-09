# Results Integration: LLM-Assisted Fault Localization

日期：2026-05-27
最后更新：2026-06-08

## 1. 当前结果一句话

当前系统已经在 6 个 Defects4J pilot 项目共 120 个 bug 上跑通文件级 fault localization pipeline。最佳阶段性结果显示：

```text
Best current Defects4J Top-5: 6/6 projects reach 1.00
Best current macro average:
  Top-1: 0.7750
  Top-3: 0.9500
  Top-5: 1.0000
  MRR:   0.8644
```

这不是最终部署结果，因为 Closure 和 Mockito 中有 targeted/diagnostic add-on；但它证明了当前方向成立：只要候选池召回足够且 evidence 质量可控，LLM rerank 可以显著提升文件级缺陷定位。

当前 proposal-aligned 方法应表述为：

```text
Selective Evidence-Aware LLM Fault Localization
```

主方法是 retrieval + evidence construction + selective one-shot DeepSeek rerank。controlled agentic inspection 和 verifier rerank 作为 RQ5 扩展/消融实验报告。

## 2. Defects4J 总表

| Project | Baseline / Retrieval | Best Current Method | LLM Calls | Top-1 | Top-3 | Top-5 | MRR |
|---|---|---|---:|---:|---:|---:|---:|
| Lang-20 | BM25 | BM25 + DeepSeek full rerank | 20 | 0.95 | 1.00 | 1.00 | 0.9750 |
| Math-20 | BM25 / hybrid | Hybrid/direct + compact evidence DeepSeek | 20 | 0.90 | 0.95 | 1.00 | 0.9350 |
| Chart-20 | Focused hybrid/direct | Focused hybrid/direct | 0 | 0.85 | 0.95 | 1.00 | 0.9040 |
| Time-20 | Focused hybrid/direct + test-prefix hints | Focused hybrid/direct + DeepSeek hard4 | 4 | 0.90 | 1.00 | 1.00 | 0.9500 |
| Closure-20 | Focused hybrid/direct | DeepSeek hard8 + pass-chain C13 + type-cycle C4 | 10 | 0.40 | 0.80 | 1.00 | 0.6225 |
| Mockito-20 | Focused hybrid/direct | Tight selector9 + DeepSeek | 9 | 0.65 | 1.00 | 1.00 | 0.8000 |

Macro average over the best current row for each project:

```text
Top-1: 0.7750
Top-3: 0.9500
Top-5: 1.0000
MRR:   0.8644
```

## 3. 关键提升链路

| Project | Starting Point | Best Current | Main Change |
|---|---:|---:|---|
| Lang | BM25 Top-5 0.85 | Top-5 1.00 | Full DeepSeek rerank |
| Math | BM25 Top-5 0.65 | Top-5 1.00 | Hybrid retrieval + compact evidence |
| Chart | BM25 Top-5 0.60 | Top-5 1.00 | Focused stack filtering fixes noisy direct hints |
| Time | Focused hybrid Top-5 0.85 | Top-5 1.00 | Test-prefix hints + hard4 rerank |
| Closure | Focused hybrid Top-5 0.55 | Top-5 1.00 | pass-chain retrieval + type-cycle snippet/prompt fix |
| Mockito | Focused hybrid Top-5 0.65 | Top-5 1.00 | Tight Mockito selector + MockMaker/ByteBuddy evidence |

## 4. Mockito 最新整合结果

Mockito baseline:

```text
Focused hybrid/direct:
  Top-1:  0.35
  Top-3:  0.55
  Top-5:  0.65
  Top-10: 0.75
  MRR:    0.4818
```

Mockito tight selector9 + DeepSeek:

```text
Top-1:  0.65
Top-3:  1.00
Top-5:  1.00
Top-10: 1.00
MRR:    0.8000
```

Rank changes for the hard cases:

```text
Mockito-1   7  -> 1
Mockito-7   12 -> 1
Mockito-9   15 -> 2
Mockito-12  18 -> 1
Mockito-15  13 -> 2
Mockito-17  10 -> 1
Mockito-19  5  -> 1
Mockito-20  23 -> 3
```

Important caveat:

- `Mockito-20` 最终命中依赖后验诊断后加入的 constructor/spy MockMaker evidence rule。
- tight selector9 运行时不使用 ground truth，但该规则是在当前 Mockito-20 pilot 上调出来的，仍需要新 bug 验证泛化。

Fresh validation update:

```text
Mockito-21..30 requested
Mockito-22..30 built successfully
Mockito-21 skipped due compile failure
```

Focused hybrid/direct on the 9 fresh records:

```text
Top-1: 0.4444
Top-3: 0.5556
Top-5: 0.5556
MRR:   0.5339
Recall@50: 9 / 9
```

Tight selector9 on fresh records:

```text
selected: 4 / 9
selected ids: Mockito-23, Mockito-25, Mockito-27, Mockito-29
Top-5 miss coverage: 2 / 4
```

Diagnostic selector on the same records:

```text
selected: 6 / 9
selected ids: Mockito-23, Mockito-25, Mockito-26, Mockito-27, Mockito-28, Mockito-29
Top-5 miss coverage: 4 / 4
```

Interpretation:

- Candidate recall remains good enough for reranking.
- The selector only partially generalizes: it misses `Mockito-26` primitive default values and `Mockito-28` InjectMocks exact type / ancestor matching.
- A diagnostic-only switch recovers these misses, but those patterns were derived from this slice and are not default production rules.
- DeepSeek was not run on this fresh slice because the diagnostic patterns needed a separate-slice sanity check first.

Second fresh validation slice:

```text
Mockito-31..38 requested
8 records built
focused hybrid/direct:
  Top-1: 0.1250
  Top-3: 0.5000
  Top-5: 0.7500
  Top-10: 0.8750
  Top-20: 1.0000
  Top-50: 1.0000
  MRR:   0.3382
```

Default tight selector9:

```text
selected: 5 / 8
selected ids: Mockito-32, Mockito-33, Mockito-35, Mockito-36, Mockito-37
Top-5 miss coverage: 2 / 2
```

Diagnostic selector:

```text
selected: same 5 / 8
```

Cost-control v2 selector:

```text
selected: 4 / 8
selected ids: Mockito-32, Mockito-33, Mockito-36, Mockito-37
Top-3 miss coverage: 4 / 4
Top-5 miss coverage: 2 / 2
```

Interpretation:

- The diagnostic patterns do not over-select on `Mockito-31..38`.
- Default tight selector9 covers all Top-5 failures on this second fresh slice.
- Cost-control v2 reduces the selected ratio from 62.5% to 50.0% on this slice while preserving miss coverage.
- Across Mockito pilot and fresh slices, cost-control v2 selects 21/37 cases and covers 13/13 retrieval Top-5 failures. It remains experimental and should not be reported as the final production selector yet.

DeepSeek follow-up on `Mockito-31..38` cost-control v2 selected set:

```text
selected ids: Mockito-32, Mockito-33, Mockito-36, Mockito-37
selected-case rerank:
  Top-1: 1.0000
  Top-3: 1.0000
  Top-5: 1.0000
  MRR:   1.0000

merged all 8 records:
  Top-1:  0.6250
  Top-3:  1.0000
  Top-5:  1.0000
  Top-10: 1.0000
  MRR:    0.7500
```

This is a positive fresh rerank result, but v2 remains an experimental selector.

Closure fresh validation update:

```text
Closure-21..30:
  records: 10
  focused direct/pass-chain retrieval:
    Top-1:  0.4000
    Top-3:  0.6000
    Top-5:  0.7000
    Top-10: 0.9000
    Top-50: 1.0000
    MRR:    0.5553

  default selector:
    selected: 7 / 10
    Top-5 miss coverage: 3 / 3

  selected DeepSeek rerank merged:
    Top-1:  1.0000
    Top-3:  1.0000
    Top-5:  1.0000
    Top-10: 1.0000
    MRR:    1.0000

  cost-control direct-rank 3..6 no-pattern selector:
    selected: 4 / 10
    Top-3 miss coverage: 4 / 4
    Top-5 miss coverage: 3 / 3
    merged Top-1: 0.8000
    merged Top-3: 1.0000
    merged Top-5: 1.0000
    merged MRR:   0.9000
```

Interpretation: Closure fresh rerank is strongly positive. The default selector reaches perfect metrics with 7/10 calls, while the direct-rank cost-control variant preserves Top-3/Top-5 1.0000 with 4/10 calls. Pass-chain hints did not improve aggregate retrieval metrics on this fresh slice.

Second Closure fresh validation:

```text
Closure-31..40:
  records: 10
  focused direct:
    Top-1:  0.2000
    Top-3:  0.3000
    Top-5:  0.4000
    Top-50: 0.8000
    MRR:    0.3185

  focused direct + pass-chain:
    Top-1:  0.2000
    Top-3:  0.3000
    Top-5:  0.4000
    Top-50: 0.9000
    MRR:    0.3208

  default selector:
    selected: 6 / 10
    Top-5 miss coverage: 4 / 6

  direct-rank 3..6 no-pattern selector:
    selected: 2 / 10
    Top-5 miss coverage: 1 / 6
```

Interpretation: `Closure-31..40` is a negative validation for the direct-rank cost-control rule. It also exposes a retrieval gap: `Closure-33` is missing from top50, and `Closure-35` is rank 18 but not selected.

Type-system follow-up for `Closure-31..40`:

```text
direct + pass-chain + type-system retrieval:
  Top-1:  0.2000
  Top-3:  0.3000
  Top-5:  0.5000
  Top-10: 0.8000
  Top-50: 1.0000
  MRR:    0.3486

key rank changes:
  Closure-33 PrototypeObjectType.java: top50 miss -> rank 12
  Closure-35 TypeInference.java:      rank 18 -> rank 4

type-system selector:
  selected: 8 / 10
  Top-3 miss coverage: 7 / 7
  Top-5 miss coverage: 5 / 5

merged DeepSeek result with hard2 wider-snippet replacement:
  Top-1:  0.3000
  Top-3:  0.5000
  Top-5:  0.9000
  Top-10: 1.0000
  MRR:    0.5025

merged DeepSeek result with singleton/getter snippet fix:
  Top-1:  0.4000
  Top-3:  0.6000
  Top-5:  1.0000
  Top-10: 1.0000
  MRR:    0.5900

closure cost-control v1:
  selected: Closure-33, Closure-36, Closure-37, Closure-39, Closure-40
  Top-1:  0.4000
  Top-3:  0.6000
  Top-5:  1.0000
  Top-10: 1.0000
  MRR:    0.5900

Closure-21..40 combined with closure cost-control v1:
  LLM calls: 9 / 20
  Top-1:  0.6000
  Top-3:  0.8000
  Top-5:  1.0000
  Top-10: 1.0000
  MRR:    0.7450
```

Interpretation: type-system retrieval fixes the candidate recall problem, and the singleton/getter snippet fix turns `Closure-36` from a rank-8 evidence failure into rank 1. `--closure-cost-control-v1` preserves Top-3/Top-5/Top-10 on both Closure fresh slices with 9/20 calls, but remains experimental until tested on more Closure bugs.

Third Closure fresh validation:

```text
Closure-41..50:
  records: 10
  focused direct + pass-chain + type-system retrieval:
    Top-1:  0.2000
    Top-3:  0.4000
    Top-5:  0.5000
    Top-10: 0.6000
    Top-20: 0.8000
    Top-50: 1.0000
    MRR:    0.3154

  closure cost-control v1:
    selected: Closure-41, Closure-42, Closure-48, Closure-49
    Top-5 miss coverage: 3 / 5

  closure cost-control v2:
    selected: Closure-41, Closure-42, Closure-44, Closure-45, Closure-48, Closure-49
    Top-5 miss coverage: 5 / 5

  merged DeepSeek result:
    Top-1:  0.4000
    Top-3:  0.7000
    Top-5:  0.9000
    Top-10: 1.0000
    MRR:    0.5742

  remaining Top-5 miss:
    Closure-48, TypedScopeCreator.java, merged rank 8

Closure-21..50 combined with closure cost-control v2:
  LLM calls: 15 / 30
  Top-1:  0.5333
  Top-3:  0.7667
  Top-5:  0.9667
  Top-10: 1.0000
  Top-20: 1.0000
  MRR:    0.6881
```

Interpretation: `--closure-cost-control-v2` keeps the v1 selected sets unchanged on `Closure-21..40`, adds code-output and deep-specific-direct-hint coverage for `Closure-41..50`, and reaches Top-5 0.9667 / Top-10 1.0000 across `Closure-21..50` with 15/30 calls. The only remaining Top-5 miss is `Closure-48`, where wider property/prototype evidence still left `TypedScopeCreator.java` behind `TypeCheck.java` and `TypeInference.java`.

Fourth Closure fresh validation:

```text
Closure-51..60:
  records: 10
  focused direct + pass-chain + type-system retrieval:
    Top-1:  0.4000
    Top-3:  0.4000
    Top-5:  0.6000
    Top-10: 0.6000
    Top-20: 0.7000
    Top-50: 1.0000
    MRR:    0.4651

  closure cost-control v2:
    selected: Closure-51, Closure-54, Closure-56
    Top-5 miss coverage: 2 / 4

  closure cost-control v3:
    selected: Closure-51, Closure-52, Closure-54, Closure-55, Closure-56
    Top-5 miss coverage: 4 / 4

  merged DeepSeek result:
    Top-1:  0.8000
    Top-3:  0.9000
    Top-5:  1.0000
    Top-10: 1.0000
    Top-20: 1.0000
    MRR:    0.8750

Closure-21..60 combined with closure cost-control v3:
  LLM calls: 20 / 40
  Top-1:  0.6000
  Top-3:  0.8000
  Top-5:  0.9750
  Top-10: 1.0000
  Top-20: 1.0000
  MRR:    0.7348
```

Interpretation: `--closure-cost-control-v3` keeps all earlier selected sets unchanged, adds numeric code-output and validator-hidden-transform coverage for `Closure-51..60`, and reaches Top-5 0.9750 / Top-10 1.0000 across `Closure-21..60`. The only remaining Top-5 miss is still `Closure-48`.

## 5. 成本整合

| Experiment | LLM Calls | Total Tokens | Avg Tokens / Call | Total Seconds | Avg Seconds / Call |
|---|---:|---:|---:|---:|---:|
| Math-20 full compact evidence | 20 | 536625 | 26831.3 | - | - |
| Math-20 selective rerank | 6 | about 188355 | about 31392.5 | - | - |
| Time-20 hard4 | 4 | about 117138 | 29284.5 | about 73.2 | 18.312 |
| Closure hard8 + C13 + C4 | 10 | 325602 | 32560.2 | about 193.5 | 19.351 |
| Closure fresh 21..30 default selector | 7 | 275689 | 39384.1 | 114.110 | 16.301 |
| Closure fresh 21..30 direct-rank cost-control | 4 | 159898 | 39974.5 | 65.553 | 16.388 |
| Closure fresh 31..40 type-system selector + snippetfix | 8 | 284148 | 35518.5 | 163.655 | 20.457 |
| Closure fresh 31..40 closure cost-control v1 + snippetfix | 5 | 176983 | 35396.6 | 111.245 | 22.249 |
| Closure fresh 21..40 closure cost-control v1 | 9 | 336881 | 37431.2 | 176.798 | 19.644 |
| Closure fresh 41..50 closure cost-control v2 | 6 | 242877 | 40479.5 | 135.602 | 22.600 |
| Closure fresh 21..50 closure cost-control v2 | 15 | 579758 | 38650.5 | 312.400 | 20.827 |
| Closure fresh 51..60 closure cost-control v3 + numeric snippet | 5 | 186961 | 37392.2 | 125.958 | 25.192 |
| Closure fresh 21..60 closure cost-control v3 | 20 | 766719 | 38336.0 | 438.358 | 21.918 |
| Mockito tight selector9 | 9 | 195100 | 21677.8 | 164.742 | 18.305 |
| Mockito fresh 31..38 cost-control v2 | 4 | 99326 | 24831.5 | 70.298 | 17.575 |
| AboutWork committed-60 selector_v3 one-shot | 16 | 519530 | 32470.6 | 336.034 | 21.002 |
| AboutWork committed-60 agentic s2 | 16 selected / 40 model calls | 440542 | 27533.9 | 339.600 | 21.225 |
| AboutWork committed-60 agentic s2 + verifier | 16 selected / 56 model calls | 589260 | 36828.8 | 535.794 | 33.487 |
| Easy Finance clean63 selector_v1 UI evidence v2 | 10 | 250902 | 25090.2 | - | - |
| Easy Finance strict62 one-shot selector_v1 UI evidence v2 | 9 | 226860 | 25206.7 | - | - |
| Easy Finance strict62 agentic s2 | 9 | 250481 | 27831.2 | - | - |
| Easy Finance strict62 agentic s2 + verifier | 9 | 331050 | 36783.3 | - | - |

Development note:

- Mockito M20 有一次失败的 evidence retry，额外使用 26057 tokens。上表的 Mockito 195100 tokens 是 tight selector9 的 deployment-equivalent usage estimate，排除了被后续 ByteBuddy rule 替代的旧 M20 miss 调用。
- Closure fresh 31..40 的表中数字是 deployment-equivalent estimate：最终配置使用 6 个原 selector 调用、`Closure-33` hard2 调用、`Closure-36` snippet-fix 调用。实际探索额外跑过旧 hard2 diagnostic。
- Closure fresh 41..50 的 v2 表中数字是 deployment-equivalent usage；实际探索额外跑过一次 `Closure-48` property/prototype diagnostic，使用 43436 tokens，未合入最终结果。
- Closure fresh 51..60 的 v3 表中数字是 deployment-equivalent usage；实际探索额外跑过一次被 numeric-snippet rerun 替代的 `Closure-51` 调用，使用 31956 tokens。
- Closure cost-control v3 已在 `Closure-21..30`、`Closure-31..40`、`Closure-41..50`、`Closure-51..60` 四个 fresh slice 上回归，但仍应标注为 Closure-only experimental selector。

## 6. AboutWork Case Study

AboutWork 是公司真实 bug log 数据集，不是公开 benchmark。

```text
records: 60 committed bug logs
backend: 35
frontend: 25
```

当前结果：

| Method | Selected Records | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 production top50 | 0 / 60 | 0.5667 | 0.8333 | 0.9167 | 0.9333 | 0.7015 |
| BM25 + selector_v3 + DeepSeek | 16 / 60 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 |

RQ5 extension:

| Method | Selected Records | Model Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR | Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| one-shot DeepSeek | 16 / 60 | 16 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 519530 |
| agentic DeepSeek s2 | 16 / 60 | 40 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 440542 |
| agentic s2 + verifier | 16 / 60 | 56 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 589260 |

意义：

- 证明这套 pipeline 不只适用于 Defects4J Java benchmark。
- 真实项目里 selective rerank 也有效：只选择 16/60 条调用 DeepSeek，就把 Top-1 从 0.5667 提升到 0.7000，把 MRR 从 0.7015 提升到 0.8117。
- AboutWork-60 剩余两个 Top-10 miss 都是 selector false negative，说明真实项目的下一步瓶颈是 selector recall。
- Agentic 和 verifier 已补跑：agentic 与 one-shot 的 per-bug correct rank 完全一致；verifier 额外消耗 148718 tokens 但不改善结果。
- `selector_v3` 仍需要后续新 bug log 验证泛化。

## 7. Easy Finance Case Study

Easy Finance 是真实项目 git-history-derived case study，包含 backend/frontend 修复提交构造出的 bug records。

当前主要数据版本：

```text
clean63
strict62
```

clean63 当前结果：

| Method | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 production top50 | 0 / 63 | 0.3968 | 0.7302 | 0.8730 | 0.8730 | 0.5684 |
| BM25 + selector_v1 | 10 / 63 | 0.4603 | 0.7778 | 0.9524 | 1.0000 | 0.6450 |
| BM25 + selector_v1 UI evidence v2 | 10 / 63 | 0.4921 | 0.8095 | 0.9841 | 1.0000 | 0.6729 |

strict62 RQ5 result:

| Method | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 + selector_v1 UI evidence v2 | 9 / 62 | 0.5000 | 0.8226 | 1.0000 | 1.0000 | 0.6817 |
| BM25 + selector_v1 controlled agentic s2 | 9 / 62 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6831 |
| BM25 + selector_v1 agentic s2 + verifier | 9 / 62 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6804 |

意义：

- Easy Finance 支持 RQ4：公司真实 repo 场景下，selector + one-shot LLM rerank 仍能提升 BM25。
- UI evidence v2 是当前 Easy Finance 主结果。
- controlled agentic inspection 技术上可运行，但没有清晰超过 one-shot UI evidence。
- verifier 当前是 negative ablation：增加成本但不提升合并结果。
- 该数据来自 commit metadata 推断，ground truth 可能受重构、格式化、顺手修改影响，论文中应标注为 git-history-derived case study。

## 8. 当前可写进报告的结论

1. LLM rerank 适合做第二阶段 fault localization，而不是替代候选生成器。
2. 候选池召回是上限；真实文件不在候选池时，LLM 无法补救。
3. Prompt evidence 质量非常关键。Closure-4、Mockito-20 和 Closure-36 都说明，真实文件在候选池内仍可能因为 snippet 证据差而被漏掉。
4. Selective rerank 是成本控制关键。Math、Time、Closure、Mockito、AboutWork committed-60 和 Easy Finance 都支持 targeted 调用优于无脑全量调用。
5. 当前最强结果里 Mockito 已经有一个非 oracle tight selector，但仍是 in-sample 拟合；Closure 的 add-on 也还需要转成非 oracle selector。
6. RQ5 当前是条件性/负向结果：controlled agentic inspection 可运行但不稳定优于 one-shot，verifier 当前设计不应作为主方法。

## 9. 下一步最合理工作

1. 用 fresh Mockito bugs 验证 tight selector9 是否泛化。
2. 把 Mockito constructor/spy MockMaker evidence rule 固化为默认 snippet/selector 策略。
3. 继续用新 Closure bug 验证 `closure_cost_control_v1`，再决定是否作为 Closure 主 selector。
4. 继续用后续新增 AboutWork / Easy Finance 样本验证 selector_v3、selector_v1 和 UI evidence v2 的泛化。
5. 针对 one-shot 明确失败且 evidence 明显不足的 case 重设 agentic inspection，而不是盲目增加 agent step。
6. 当前实验已足够进入论文 Results、Discussion 和 Threats to Validity 写作收口。
