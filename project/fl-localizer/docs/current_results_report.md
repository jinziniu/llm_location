# Current Results Report: LLM-Assisted Fault Localization

生成日期：2026-05-27
更新日期：2026-06-02

结果整合版：

```text
docs/results_integration_2026-05-27.md
```

## 1. 摘要

当前项目已经完成一个可运行的文件级缺陷定位原型，并在 Defects4J 的 `Lang-20`、`Math-20`、`Chart-20`、`Time-20`、`Closure-20` 和 `Mockito-20` 上完成 pilot 实验。

实验结果显示，基于 DeepSeek 的 LLM rerank 能显著提升 BM25 baseline 的文件级定位效果：

| Project | Method | Bugs | Top-1 | Top-3 | Top-5 | MRR |
|---|---|---:|---:|---:|---:|---:|
| Lang | BM25 | 20 | 0.60 | 0.85 | 0.85 | 0.7383 |
| Lang | BM25 + DeepSeek rerank | 20 | 0.95 | 1.00 | 1.00 | 0.9750 |
| Math | BM25 | 20 | 0.35 | 0.55 | 0.65 | 0.4794 |
| Math | BM25 + DeepSeek rerank | 20 | 0.75 | 0.90 | 0.90 | 0.8250 |
| Math | Hybrid/direct + compact evidence DeepSeek | 20 | 0.90 | 0.95 | 1.00 | 0.9350 |
| Math | Focused hybrid/direct + selective DeepSeek | 20 | 0.90 | 0.90 | 1.00 | 0.9200 |
| Chart | BM25 | 20 | 0.35 | 0.60 | 0.60 | 0.4921 |
| Chart | Hybrid/direct | 20 | 0.50 | 0.70 | 0.80 | 0.6375 |
| Chart | Hybrid/direct + DeepSeek hard4 | 20 | 0.55 | 0.90 | 1.00 | 0.7392 |
| Chart | Focused hybrid/direct | 20 | 0.85 | 0.95 | 1.00 | 0.9040 |
| Time | BM25 | 20 | 0.15 | 0.65 | 0.75 | 0.4020 |
| Time | Focused hybrid/direct + test-prefix hints | 20 | 0.70 | 0.80 | 0.85 | 0.7800 |
| Time | Focused hybrid/direct + DeepSeek hard4 | 20 | 0.90 | 1.00 | 1.00 | 0.9500 |
| Closure | BM25 | 20 | 0.15 | 0.30 | 0.40 | 0.2808 |
| Closure | Focused hybrid/direct | 20 | 0.30 | 0.45 | 0.55 | 0.4323 |
| Closure | Focused hybrid/direct + DeepSeek hard8 | 20 | 0.40 | 0.70 | 0.90 | 0.5808 |
| Closure | Focused hybrid/direct + DeepSeek hard8 + pass-chain C13 | 20 | 0.40 | 0.75 | 0.95 | 0.5975 |
| Closure | Focused hybrid/direct + DeepSeek hard8 + pass-chain C13 + type-cycle C4 | 20 | 0.40 | 0.80 | 1.00 | 0.6225 |
| Mockito | Focused hybrid/direct | 20 | 0.35 | 0.55 | 0.65 | 0.4818 |
| Mockito | Focused hybrid/direct + diagnostic DeepSeek hard7 | 20 | 0.55 | 0.85 | 0.95 | 0.7033 |
| Mockito | Diagnostic DeepSeek hard7 + ByteBuddy M20 | 20 | 0.55 | 0.90 | 1.00 | 0.7200 |
| Mockito | Focused hybrid/direct + tight selector9 DeepSeek | 20 | 0.65 | 1.00 | 1.00 | 0.8000 |

主要结论：

- LLM rerank 对文件级 fault localization 有明显帮助。
- `Math` 比 `Lang` 更难，但 hybrid/direct retrieval 加 evidence-aware DeepSeek rerank 后，`Math-20` 已达到 Top-5 1.00。
- `Chart-20` 显示跨项目也有收益：hybrid/direct top-50 覆盖 20/20，targeted DeepSeek hard4 把 4 个困难样例全部拉进 Top-3。
- Focused stack retrieval 修复了 Chart 中无关 `MonthTests` section 污染 direct hints 的问题，使 Chart hybrid Top-1 从 0.50 提高到 0.85。
- selective rerank gate 可以把 Math 的 DeepSeek 调用从 20/20 降到 6/20，同时保持 Top-1 0.90 和 Top-5 1.00。
- `Time-20` 进一步验证了 targeted DeepSeek 的效果：只对 4 个 hard cases 调用 DeepSeek，就把 Time Top-3 / Top-5 提到 1.00。
- Joda-Time 的测试类命名使用 `TestXxx_*` 前缀，因此 test-prefix hint extraction 是必要的召回增强。
- `Closure-20` 明显更难：focused hybrid/direct 只有 Top-5 0.55，但 8 个 hard cases 加 2 个 targeted add-ons 后，整体 Top-5 提升到 1.00。
- `Closure-13` 原本是 focused hybrid top-200 miss；新增 pass-chain retrieval 后，`PeepholeOptimizationsPass.java` 进入候选池 rank 39，DeepSeek rerank 后达到 rank 3。
- `Closure-4` 原本是 rerank miss；snippet scoring、重复栈压缩和 type-cycle prompt rule 后，`NamedType.java` 从候选 rank 49 被 DeepSeek 提到 rank 2。
- `Mockito-20` 已接入 benchmark：focused hybrid/direct 的 Top-50 召回为 1.00，但 Top-5 只有 0.65，说明 LLM rerank 有足够候选池和明确优化空间。
- Mockito-specific pattern selector 覆盖 7/7 个 baseline Top-5 failures，选择 12/20；后续需要进一步收紧。
- Mockito hard7 diagnostic DeepSeek 将整体 Top-1/Top-3/Top-5 从 0.35/0.55/0.65 提升到 0.55/0.85/0.95，MRR 从 0.4818 提升到 0.7033。
- 针对 `Mockito-20` 增加 constructor/spy MockMaker evidence rule 后，`ByteBuddyMockMaker.java` 从 baseline rank 23 提升到 DeepSeek rank 3；最终 Mockito Top-5 达到 1.00。
- Mockito tight selector9 将 pattern selection 从 12/20 收紧到 9/20，并覆盖 baseline 全部 Top-3 misses。
- 补跑 `Mockito-3` 和 `Mockito-19` 后，Mockito 整体达到 Top-1 0.65、Top-3 1.00、Top-5 1.00、MRR 0.8000。
- Mockito tight selector9 运行时不使用 ground truth，但仍是在当前 Mockito-20 pilot 上调出的 in-sample 规则，需要 fresh bugs 验证泛化。
- Closure 上的宽泛 reference-hint expansion 会引入大量噪声，实验结果低于默认 focused retrieval，因此暂时不作为默认方法。
- 2026-06-01 已补充 fresh / held-out validation：Closure `21..60`、Mockito `31..38` 和 frozen held-out Closure `61..80` 均显示 selective rerank 能在较少调用下提升 Top-k，但 selector recall 仍是主要风险。
- 当前主要瓶颈从单纯 BM25 排序转为 candidate retrieval 质量、prompt 证据选择和 token 成本控制。
- 如果真实缺陷文件不在候选池内，LLM rerank 无法补救；因此扩大实验前应优先保证 top-50/top-80 召回。

## 1.1 Fresh / Held-Out Validation 更新

2026-06-01 后续实验把 Closure 和 Mockito 从 in-sample pilot 推进到 fresh / held-out 验证阶段。

| Dataset | Setting | Bugs | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Closure-21..60 | focused retrieval baseline | 40 | 0 | 0.3000 | 0.4250 | 0.5750 | 0.7250 | 0.4211 |
| Closure-21..60 | cost-control v3 + DeepSeek | 40 | 20 | 0.6000 | 0.8000 | 0.9750 | 1.0000 | 0.7348 |
| Closure-61..80 held-out | frozen retrieval baseline | 19 | 0 | 0.4737 | 0.4737 | 0.5789 | 0.7368 | 0.5344 |
| Closure-61..80 held-out | frozen cost-control v3 + DeepSeek | 19 | 6 | 0.6316 | 0.7368 | 0.7895 | 0.8947 | 0.7018 |
| Mockito-31..38 fresh | focused retrieval baseline | 8 | 0 | 0.1250 | 0.5000 | 0.7500 | 0.8750 | 0.3382 |
| Mockito-31..38 fresh | cost-control v2 + DeepSeek | 8 | 4 | 0.6250 | 1.0000 | 1.0000 | 1.0000 | 0.7500 |

关键解释：

- `Closure-21..60` 仍是 cost-control selector 逐步演化后的 fresh validation，不应写成完全冻结协议。
- `Closure-61..80` 是第一组明确 frozen protocol held-out run：先写 `docs/frozen_protocol_2026-06-01.md`，再运行数据构建、retrieval、selector、rerank 和 eval。
- `Closure-61..80` 的 selector 只选 6/19，selected cases 全部进入 Top-3；合并结果比 frozen retrieval baseline 明显提升。
- `Closure-61..80` 暴露了 selector false negatives：`Closure-61`、`Closure-65`、`Closure-67`、`Closure-75` 没有被选中，其中 `Closure-67` 和 `Closure-75` 是最重要的 remaining misses。
- merged selective rerank 输出是 Top-10 ranking，因此 Top-20/Top-50 candidate recall 应从 retrieval baseline 报告，不应从 merged output 解读。
- `Mockito-31..38` 是正向 fresh result，但 cost-control v2 仍是在之前 fresh behavior 后设计出的 experimental selector，需要再跑 held-out 才能作为稳定协议。

新增报告：

```text
docs/closure_heldout_61_80_validation_report.md
docs/frozen_protocol_2026-06-01.md
```

Proposal-aligned interpretation:

- 当前主方法应写作 `Selective Evidence-Aware LLM Fault Localization`。
- Defects4J 回答 benchmark 有效性问题，即 RQ1、RQ2、RQ3。
- AboutWork 和 Easy Finance 回答真实项目迁移问题，即 RQ4。
- Easy Finance strict62 上的 controlled agentic / verifier 结果回答 RQ5；当前结论是技术可行，但没有证明优于 one-shot rerank。
- Codex backend 已做 smoke test，但不再作为当前核心 RQ，只保留为后续工程对比。

## 2. 当前项目状态

已经完成：

- Defects4J 安装和本地环境配置。
- DeepSeek API 配置。
- `.env` 本地运行配置。
- Defects4J 数据集构建脚本。
- BM25 baseline。
- hybrid/direct retrieval。
- LLM rerank pipeline。
- evidence-aware compact rerank prompt。
- focused stack trace retrieval。
- selective rerank gate。
- DeepSeek provider。
- Codex backend smoke test（后续工程对比，不作为当前核心 RQ）。
- evaluator。
- token 和 runtime logging。
- worklog 记录机制。

当前项目目录中的主要脚本：

```text
scripts/build_defects4j_dataset.py
scripts/run_bm25.py
scripts/run_llm_rerank.py
scripts/run_hybrid_retrieval.py
scripts/select_rerank_candidates.py
scripts/merge_selective_rerank.py
scripts/evaluate_predictions.py
scripts/summarize_llm_usage.py
scripts/complete_rerank_output.py
```

## 3. 当前系统做了什么

系统输入一个 Defects4J bug，提取：

- 失败测试。
- triggering tests。
- stack trace。
- 源码文件。
- ground truth modified classes。

然后执行：

```text
Bug context + source files
-> BM25 retrieves candidate files
-> LLM reranks candidate files
-> evaluator compares prediction with ground truth files
```

系统输出：

- 每个 bug 的 ranked files。
- 每个 bug 的 correct rank。
- Top-1 / Top-3 / Top-5。
- MRR。
- LLM token usage。
- LLM runtime。
- invalid / duplicate / fallback 统计。

## 4. Lang-20 实验结果

数据文件：

```text
data/defects4j/lang_pilot_20.jsonl
```

输出文件：

```text
outputs/lang_pilot_20_bm25.jsonl
outputs/lang_pilot_20_bm25_eval.json
outputs/lang_pilot_20_bm25_top50.jsonl
outputs/lang_pilot_20_rerank_deepseek.jsonl
outputs/lang_pilot_20_rerank_deepseek_eval.json
```

BM25 top-10：

```text
bugs: 20
top_1_accuracy: 0.60
top_3_accuracy: 0.85
top_5_accuracy: 0.85
mrr: 0.7383333333333334
```

DeepSeek rerank：

```text
bugs: 20
top_1_accuracy: 0.95
top_3_accuracy: 1.0
top_5_accuracy: 1.0
mrr: 0.975
```

BM25 top-50 candidate coverage：

```text
Top1: 12 / 20
Top3: 17 / 20
Top5: 17 / 20
Top10: 19 / 20
Top20: 19 / 20
Top50: 20 / 20
```

关键观察：

- `Lang-20` 上 BM25 已经比较强，Top-5 达到 0.85。
- DeepSeek rerank 进一步把 Top-1 提到 0.95。
- top-50 覆盖 20/20，说明 Lang 这组样本中候选召回不是主要瓶颈。
- `Lang-17` 在 BM25 top-10 中没有命中，但真实文件在 top-50 内，DeepSeek rerank 后达到 rank 2。

## 5. Math-20 实验结果

数据文件：

```text
data/defects4j/math_pilot_20.jsonl
```

输出文件：

```text
outputs/math_pilot_20_bm25.jsonl
outputs/math_pilot_20_bm25_eval.json
outputs/math_pilot_20_bm25_top50.jsonl
outputs/math_pilot_20_rerank_deepseek.jsonl
outputs/math_pilot_20_rerank_deepseek_eval.json
outputs/math_pilot_20_rerank_deepseek_usage.json
```

BM25 top-10：

```text
bugs: 20
top_1_accuracy: 0.35
top_3_accuracy: 0.55
top_5_accuracy: 0.65
mrr: 0.4793650793650793
```

DeepSeek rerank：

```text
bugs: 20
top_1_accuracy: 0.75
top_3_accuracy: 0.90
top_5_accuracy: 0.90
mrr: 0.825
```

BM25 top-50 candidate coverage：

```text
Top1: 7 / 20
Top3: 11 / 20
Top5: 13 / 20
Top10: 16 / 20
Top20: 16 / 20
Top50: 18 / 20
```

DeepSeek usage：

```text
records: 20
total_duration_seconds: 304.237
avg_duration_seconds: 15.212
total_prompt_tokens: 398901
total_completion_tokens: 27839
total_tokens: 426740
avg_prompt_tokens: 19945.05
avg_completion_tokens: 1391.95
avg_total_tokens: 21337.0
```

Output validity：

```text
fallback_added_total: 0
invalid_total: 0
duplicate_total: 0
```

Rank changes：

```text
Math-1:  bm25=1    rerank=1
Math-2:  bm25=1    rerank=1
Math-3:  bm25=4    rerank=1
Math-4:  bm25=1    rerank=1
Math-5:  bm25=1    rerank=1
Math-6:  bm25=3    rerank=1
Math-7:  bm25=7    rerank=2
Math-8:  bm25=2    rerank=1
Math-9:  bm25=1    rerank=1
Math-10: bm25=3    rerank=2
Math-11: bm25=1    rerank=1
Math-12: bm25=None rerank=None
Math-13: bm25=1    rerank=1
Math-14: bm25=None rerank=1
Math-15: bm25=None rerank=None
Math-16: bm25=None rerank=1
Math-17: bm25=2    rerank=1
Math-18: bm25=6    rerank=1
Math-19: bm25=9    rerank=2
Math-20: bm25=4    rerank=1
```

关键观察：

- `Math` 对 BM25 更难，Top-1 只有 0.35。
- DeepSeek rerank 将 Top-1 提升到 0.75，将 Top-5 提升到 0.90。
- `Math-14` 和 `Math-16` 的真实文件不在 BM25 top-10 中，但在 top-50 中，DeepSeek rerank 后排到 rank 1。
- `Math-12` 和 `Math-15` 的真实文件不在 BM25 top-50 中，因此 rerank 失败属于 retrieval miss。
- 这说明当前系统的下一步重点应是增强 candidate generation。

## 6. 跨项目扩展结果

Chart、Time 和 Closure 的扩展实验说明：同一个 pipeline 在不同项目上的难度差异很大。

| Project | Best non-LLM retrieval | Targeted DeepSeek calls | Best merged Top-1 | Best merged Top-3 | Best merged Top-5 | Main bottleneck |
|---|---:|---:|---:|---:|---:|---|
| Chart-20 | 0.85 / 0.95 / 1.00 | 4 old-hard cases | 0.85 | 0.95 | 1.00 | Direct-hint noise before focused stack fix |
| Time-20 | 0.70 / 0.80 / 0.85 | 4 hard cases | 0.90 | 1.00 | 1.00 | `TestXxx_*` naming needs prefix hints |
| Closure-20 | 0.30 / 0.45 / 0.55 | 10 targeted cases | 0.40 | 0.80 | 1.00 | Remaining Top-1/Top-3 ranking errors |
| Mockito-20 | 0.35 / 0.55 / 0.65 | tight selector9 | 0.65 | 1.00 | 1.00 | Need fresh-bug validation |

Closure hard-case DeepSeek run:

```text
Closure-1:  focused_hybrid=22 -> deepseek=1
Closure-4:  focused_hybrid=49 -> deepseek=None
Closure-6:  focused_hybrid=10 -> deepseek=5
Closure-7:  focused_hybrid=6  -> deepseek=3
Closure-8:  focused_hybrid=25 -> deepseek=1
Closure-10: focused_hybrid=13 -> deepseek=4
Closure-12: focused_hybrid=34 -> deepseek=3
Closure-17: focused_hybrid=6  -> deepseek=2
```

Closure hard8 usage:

```text
records: 8
total_tokens: 262656
avg_total_tokens: 32832.0
total_duration_seconds: 136.645
avg_duration_seconds: 17.081
```

Closure pass-chain C13 add-on:

```text
pass-chain retrieval: Closure-13 None -> rank 39
DeepSeek rerank: Closure-13 rank 39 -> rank 3
tokens: 30637
duration_seconds: 35.081

merged hard8 + C13:
top_1_accuracy: 0.40
top_3_accuracy: 0.75
top_5_accuracy: 0.95
mrr: 0.5975
```

Closure 当前错误分析：

- `Closure-4` 原本是 rerank miss。修复 snippet scoring 和重复栈压缩后，`NamedType.java` 从 rank 49 候选被 DeepSeek 提到 rank 2。
- `Closure-13` 原本是 retrieval miss。pass-chain retrieval 通过 `DefaultPassConfig -> PeepholeOptimizationsPass` 把真实文件拉回候选池，DeepSeek 将其排到 rank 3。

Closure type-cycle C4 add-on:

```text
snippet fix: package/import-only snippet -> handleTypeCycle / Cycle detected snippet
stack fix: repeated PrototypeObjectType.isSubtype frames compacted
DeepSeek rerank: Closure-4 rank 49 -> rank 2
tokens: 32309
duration_seconds: 21.779

merged hard8 + C13 + C4:
top_1_accuracy: 0.40
top_3_accuracy: 0.80
top_5_accuracy: 1.00
mrr: 0.6225
```

Mockito hard7 diagnostic rerank:

```text
selection:
  baseline Top-5 failures
  Mockito-1, Mockito-7, Mockito-9, Mockito-12, Mockito-15, Mockito-17, Mockito-20

rerank-only hard7:
  Top-1: 0.5714
  Top-3: 0.8571
  Top-5: 0.8571
  MRR:   0.7143

merged Mockito-20:
  Top-1: 0.35 -> 0.55
  Top-3: 0.55 -> 0.85
  Top-5: 0.65 -> 0.95
  Top-10: 0.75 -> 0.95
  MRR:   0.4818 -> 0.7033

usage:
  records: 7
  total_tokens: 152020
  avg_total_tokens: 21717.14
  total_duration_seconds: 149.035
  avg_duration_seconds: 21.291
```

Mockito rank changes:

```text
Mockito-1   7 -> 1
Mockito-7  12 -> 1
Mockito-9  15 -> 2
Mockito-12 18 -> 1
Mockito-15 13 -> 2
Mockito-17 10 -> 1
Mockito-20 23 -> miss
```

Mockito-20 ByteBuddy add-on:

```text
prompt change:
  add Mockito @Spy/useConstructor rule to inspect MockMaker or bytecode creation classes

first retry:
  Mockito-20 rank 23 -> miss
  tokens: 26057
  duration_seconds: 25.158

second retry with explicit constructor/spy rule:
  Mockito-20 rank 23 -> rank 3
  tokens: 25568
  duration_seconds: 18.694

merged hard7 + M20 add-on:
  Top-1: 0.55
  Top-3: 0.90
  Top-5: 1.00
  Top-10: 1.00
  MRR:   0.7200
```

Mockito tight selector9:

```text
selector:
  selected 9 / 20
  selected ids:
    Mockito-1, Mockito-3, Mockito-7, Mockito-9, Mockito-12,
    Mockito-15, Mockito-17, Mockito-19, Mockito-20

coverage:
  baseline hard3 coverage: 9 / 9
  baseline hard5 coverage: 7 / 7
  extra selected beyond hard3: 0

new DeepSeek calls:
  Mockito-3:  rank 5 -> rank 1
  Mockito-19: rank 5 -> rank 1
  tokens: 41968
  duration_seconds: 22.542

merged tight selector9:
  Top-1: 0.65
  Top-3: 1.00
  Top-5: 1.00
  Top-10: 1.00
  MRR:   0.8000

deployment-equivalent usage:
  calls: 9
  total_tokens: 195100
  avg_total_tokens: 21677.8
  total_duration_seconds: 164.742
  avg_duration_seconds: 18.305
```

Important caveat:

- The older hard7 batch was diagnostic/oracle because it was selected from baseline Top-5 failures.
- The newer tight selector9 uses non-oracle input signals at runtime, but it is still fitted on this Mockito-20 pilot.
- The Top-20/Top-50 metrics on merged rerank outputs are output-level metrics over a top-10 list, not candidate-pool recall.

Mockito fresh validation 21..30:

```text
requested: Mockito-21..30
built: 9 records, skipped Mockito-21 due compile failure
focused hybrid/direct: Top-1 0.4444, Top-3 0.5556, Top-5 0.5556, MRR 0.5339
candidate Recall@50: 9 / 9
tight selector9 selected: 4 / 9
selected ids: Mockito-23, Mockito-25, Mockito-27, Mockito-29
Top-5 miss coverage: 2 / 4
diagnostic selector selected: 6 / 9
diagnostic Top-5 miss coverage: 4 / 4
```

Interpretation:

- Candidate recall is sufficient on fresh Mockito bugs, but the tight selector only partially generalizes.
- The selector missed `Mockito-26` primitive default values and `Mockito-28` InjectMocks exact type / ancestor matching.
- A diagnostic-only selector switch recovers these two cases, but it is not default production behavior.
- DeepSeek was intentionally not run on 21..30 because the selector needed a separate-slice sanity check.

Mockito fresh validation 31..38:

```text
requested: Mockito-31..38
built: 8 records
focused hybrid/direct: Top-1 0.1250, Top-3 0.5000, Top-5 0.7500, MRR 0.3382
candidate Recall@50: 8 / 8
tight selector9 selected: 5 / 8
selected ids: Mockito-32, Mockito-33, Mockito-35, Mockito-36, Mockito-37
Top-5 miss coverage: 2 / 2
diagnostic selector selected: same 5 / 8
cost-control v2 selected: 4 / 8
cost-control v2 ids: Mockito-32, Mockito-33, Mockito-36, Mockito-37
cost-control v2 Top-5 miss coverage: 2 / 2
```

Interpretation:

- Default tight selector covers all Top-5 failures in this second fresh slice.
- The two diagnostic patterns do not over-select on 31..38, but they also do not add coverage beyond default tight selector.
- Cost-control v2 reduces 31..38 selected cases from 5/8 to 4/8 while preserving Top-5 miss coverage.
- Across Mockito-1..20, 21..30, and 31..38, v2 selects 21/37 and covers 13/13 retrieval Top-5 failures. It is still experimental, not default.

## 7. 对比分析

Lang 和 Math 的差异很关键：

| Project | BM25 Top-1 | DeepSeek Top-1 | Absolute Gain | BM25 Top-50 Coverage |
|---|---:|---:|---:|---:|
| Lang | 0.60 | 0.95 | +0.35 | 20 / 20 |
| Math | 0.35 | 0.75 | +0.40 | 18 / 20 |

解释：

- 在 `Lang` 上，BM25 候选召回充足，LLM rerank 几乎可以把正确文件全部推到前列。
- 在 `Math` 上，BM25 baseline 明显更弱，但 LLM rerank 仍然有很强提升。
- `Math` 的剩余错误暴露了系统瓶颈：真实文件没进入候选池。

因此目前最稳妥的结论不是“LLM 可以单独完成 fault localization”，而是：

```text
LLM rerank can substantially improve file-level fault localization when the faulty file is included in the candidate pool.
The next limiting factor is candidate recall.
```

## 8. 当前成果的意义

这组结果已经支持一个清晰的研究方向：

- BM25 适合作为轻量级第一阶段检索器。
- LLM 适合作为第二阶段语义 reranker。
- 两阶段架构比直接让 LLM 看全部源码更可控。
- 失败样本可以被明确分类为 retrieval miss 或 rerank miss。
- token 和 runtime 已经被记录，后续可以做成本分析。

对论文而言，当前成果可以支撑一个 pilot study：

```text
We implemented a selective evidence-aware LLM reranking pipeline for file-level fault localization.
On six Defects4J pilot slices, focused retrieval plus selective LLM reranking improves file-level localization when the faulty file is present in the candidate pool.
AboutWork and Easy Finance provide early real-repository evidence that the same retrieval + selector + rerank pattern can transfer beyond benchmark data.
The remaining failures are increasingly dominated by candidate retrieval misses, weak evidence selection, and selector generalization rather than basic BM25 ranking alone.
```

## 9. 当前限制

样本规模限制：

- 当前完成 120 个 Defects4J bugs，来自 6 个项目，每个项目前 20 个 active bugs。
- 当前公司项目 case study 包括 AboutWork 39 条 committed bug logs 和 Easy Finance clean63 / strict62。
- 还不能声称对整个 Defects4J 都有效。

评价粒度限制：

- 当前是 file-level，不是 line-level。
- 自动修复通常还需要 method-level 或 line-level 定位。

多文件 bug 限制：

- 当前只要命中任一 ground-truth file 就算成功。
- 后续需要补充 all-file recall 和 partial recall。

候选池限制：

- 当前 rerank 依赖候选池召回，候选池可以来自 BM25 或 focused hybrid retrieval。
- 如果真实文件不在候选池中，LLM 无法成功；`Closure-13` 的修复正是先补候选池，再交给 DeepSeek rerank。

成本限制：

- Math-20 full compact evidence rerank 使用 536625 total tokens。
- Closure hard8 + C13 + C4 targeted rerank 共 10 次 DeepSeek 调用，平均每次约 32.6k tokens。
- Mockito hard7 diagnostic rerank 使用 152020 total tokens，平均每次约 21.7k tokens。
- Mockito final diagnostic output adds one successful M20 rule call with 25568 tokens; the failed M20 evidence retry used another 26057 tokens during development.
- Mockito tight selector9 deployment-equivalent estimate uses 9 calls and 195100 tokens, averaging about 21.7k tokens per selected bug.
- 扩大到全量 Defects4J 前需要优化 snippet 长度和候选数量。

模型版本限制：

- API 模型可能变化。
- 后续报告应记录 provider、model、日期和参数。

## 10. 下一步计划

第一优先级：验证 selector 泛化。

- 用 fresh Mockito bugs 验证 tight selector9，而不是继续在同一 20 个 bug 上调参。
- 用新增 AboutWork bug logs 验证 selector_v3。
- 用新增 Easy Finance bug logs 或新时间段 commit 验证 selector_v1 和 UI evidence v2。

第二优先级：把 diagnostic evidence 转成自动规则。

- 将 pass-chain / configuration-aware retrieval 从 Closure-13 的定点成功扩展成更稳的 gate，而不是默认影响所有 bug 的排序。
- 将 type-cycle prompt/snippet fix 从 Closure-4 的定点成功扩展成更稳的 gate。
- 将 Mockito constructor/spy MockMaker evidence rule 固化为 snippet/selector 策略。
- 保留 focused stack trace filtering 和 test-prefix hint extraction 作为默认 retrieval 增强。
- 暂不启用宽泛 reference-hint boost，因为 Closure 实验显示它会引入噪声。

第三优先级：继续扩大 benchmark 和真实项目 case study。

- `Mockito-20` 已完成 focused hybrid baseline、hard7 diagnostic DeepSeek、M20 ByteBuddy add-on 和 tight selector9。
- 对 Closure 再做一轮 retrieval diagnostic，而不是直接加大 LLM 调用量。
- 为 AboutWork 和 Easy Finance 补充新样本，形成 fitted pilot 与 fresh validation 的区分。
- 用同一套 evaluator 和 worklog 模板记录。

第四优先级：RQ5 agentic 再设计。

- 不再盲目增加 agent step。
- 只选择 one-shot 失败且 evidence 明显不足的样例做 controlled agentic inspection。
- verifier 只有在输入 evidence 更干净时再重跑；当前 verifier 是 negative ablation。

第五优先级：成本控制。

- 比较 `top_candidates=20/50/80`。
- 比较 `max_snippet_lines=6/12/18`。
- 找出准确率和 token 成本之间的平衡点。

第六优先级：论文整理。

- 写方法章节。
- 写实验设置章节。
- 写结果表和错误分析。
- 写 threats to validity。
- 设计真实项目 case study。

## 11. 阶段性结论

当前阶段已经证明：

```text
Retrieval + evidence construction + selective LLM rerank 是一个可行的软件缺陷定位方向。
```

在 `Lang-20`、`Math-20`、`Chart-20`、`Time-20`、`Closure-20` 和 `Mockito-20` 上，结果支持一个更清楚的结论：LLM rerank 很适合做第二阶段排序，但它必须建立在高召回候选池和高质量 evidence 之上。AboutWork 和 Easy Finance 进一步说明，该方法可以迁移到真实项目，但 selector 和 evidence rule 需要 fresh data 验证。

现阶段最重要的工程和研究问题已经转变为：

```text
How can we improve candidate recall and evidence selection before LLM reranking?
```

因此，下一阶段应重点把 Closure/Mockito-style hard-case 诊断转成更小、更准、非 oracle 的 selector，并继续改进候选证据质量。RQ5 的 agentic/verifier 暂时不作为主方法，而是作为受控扩展和消融实验。

## 12. AboutWork 公司项目 Case Study 更新

数据：

- 来源：`/Users/jin/capi_project/aboutwork/COMPANY_BUG_LOG.md`
- 可用 committed bug logs：39 条
- 后端样本：17 条
- 前端样本：22 条
- ground truth：fix commit touched files

Production-only BM25：

| Method | Selected LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 production | 0 / 39 | 0.5897 | 0.8462 | 0.9487 | 0.9487 | 0.7171 |
| BM25 + lowratio_t102 | 8 / 39 | 0.7179 | 0.9231 | 0.9744 | 0.9744 | 0.8150 |
| BM25 + lowratio_t103 | 11 / 39 | 0.7436 | 0.9231 | 1.0000 | 1.0000 | 0.8342 |
| BM25 + selector_v3 | 11 / 39 | 0.7692 | 1.0000 | 1.0000 | 1.0000 | 0.8675 |

当前最好结果：

```text
BM25 production + selector_v3 + DeepSeek rerank
selected: 11 / 39
Top-1:  0.7692
Top-3:  1.0000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.8675
tokens: 303537 total
```

selector_v3 使用的非 oracle 规则：

- BM25 Top1/Top2 score ratio <= `1.02`。
- 资产、员工上下文、UUID 等业务词和 Top1 文件路径出现明显 domain mismatch。
- Top1 是 management command，且文本是 attendance follow-up action-context 类问题。

结论：

- AboutWork 的真实项目数据已经足够做一个小型 case study。
- LLM rerank 不应该全量调用，选择性调用可以用约 28% 的样本覆盖大部分难例。
- `selector_v3` 是当前最好的公司项目策略，但它是在这 39 条日志上调出来的，后续需要用新增 bug logs 验证泛化能力。

## 13. Easy Finance 公司项目 Case Study 更新

数据：

- 来源：`/Users/jin/capi_project/easy_finance/` 的 backend/frontend git history
- clean committed records：63 条
- 后端样本：29 条
- 前端样本：34 条
- ground truth：fix commit touched files，排除了 1 条主要依赖新增文件的样本

Production-only BM25 + selector：

| Method | Selected LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 production | 0 / 63 | 0.3968 | 0.6825 | 0.8571 | 0.8730 | 0.5727 |
| BM25 + hard9 oracle | 9 / 63 | 0.4444 | 0.7778 | 0.9524 | 1.0000 | 0.6344 |
| BM25 + selector_v1 | 10 / 63 | 0.4603 | 0.7778 | 0.9524 | 1.0000 | 0.6450 |
| BM25 + selector_v1 UI evidence v2 | 10 / 63 | 0.4921 | 0.8095 | 0.9841 | 1.0000 | 0.6729 |

Strict62 sensitivity analysis：

| Method | Selected LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| BM25 production | 0 / 62 | 0.4032 | 0.6935 | 0.8710 | 0.8871 | 0.5810 |
| BM25 + selector_v1 UI evidence v2 | 9 / 62 | 0.5000 | 0.8226 | 1.0000 | 1.0000 | 0.6817 |
| BM25 + selector_v1 controlled agentic s2 | 9 / 62 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6831 |
| BM25 + selector_v1 agentic s2 + verifier | 9 / 62 | 0.5000 | 0.8065 | 1.0000 | 1.0000 | 0.6804 |

当前最好结果：

```text
BM25 production + selector_v1 UI evidence v2 + DeepSeek rerank
selected: 10 / 63
Top-1:  0.4921
Top-3:  0.8095
Top-5:  0.9841
Top-10: 1.0000
MRR:    0.6729
tokens: 250902 total
```

selector_v1 使用的非 oracle 规则：

- backend `reports` / `bookkeeping` area 与 Top1 文件路径不匹配。
- backend Top1 是 management command 噪声。
- backend admin invoice bug 但 Top1 是非 admin invoice 文件。
- frontend admin unreviewed count、chat history、admin user filtering、invoice currency、expense form、confirm loading 等业务词和 Top1 路径不匹配。

UI evidence v2 额外改进：

- 对 unreviewed count、button loading、currency display 自动扩展 snippet 关键词。
- 对 `useQuery`、`<Button>`、`isLoading/isPending/isSubmitting`、`currency: USD/EUR` 等代码行提高 evidence 权重。
- 收紧 loading 触发条件，避免 Easy Finance 模板里的泛化 expected behavior 污染 currency/display bug。

Controlled agentic pilot：

- 新增受控工具协议：`search_files`、`inspect_candidate`、`read_file_window`，只允许在 BM25 top-50 candidate pool 内行动。
- strict62 selector_v1 的 9 个样本上，agentic s2 单独结果为 Top-1 0.6667、Top-3 0.8889、Top-5 1.0000、MRR 0.8056。
- 合并回 62 条后，agentic s2 与 one-shot UI evidence v2 基本持平：MRR 0.6831 vs 0.6817，但 Top-3 较低且 tokens 较高。
- agentic s2 使用 250481 tokens，one-shot strict62 使用 226860 tokens；当前结论是 agent protocol 可运行，但还没有证明比 one-shot 更优。

Verifier ablation：

- 新增独立 verifier pass：只看 agent top-10、固定 snippets 和 prior observations，不允许调用工具。
- selected 9-case verifier 后结果为 Top-1 0.6667、Top-3 0.8889、Top-5 1.0000、MRR 0.7870。
- 合并 strict62 后为 Top-1 0.5000、Top-3 0.8065、Top-5 1.0000、MRR 0.6804，低于 agent-only 的 MRR 0.6831。
- verifier 额外消耗 80569 tokens；agent + verifier 总计 331050 tokens。因此当前 verifier 设计是负向 ablation，不作为主方法。

结论：

- Easy Finance clean63 已经可以作为第二个公司项目 case study。
- `selector_v1` 只调用 15.9% 的样本，Top-10 从 0.8730 提升到 1.0000。
- UI evidence v2 把 Top-5 从 0.9524 提升到 0.9841，目前只剩 1 条 Top-5 miss。
- strict62 敏感性分析排除了 `easyfinance-frontend-20250930-001` 这条 bug text 与实际 touched files 明显不一致的样本后，Top-5 和 Top-10 都达到 1.0000。
- controlled agentic inspection 可以作为 RQ5 pilot，但当前 Easy Finance strict62 上收益不明显，应优先作为对照实验或后续 verifier-loop 基线。
- 当前 verifier-loop 没有提升结果，说明独立验证需要更干净的证据选择策略，否则会放大 top-10 中的噪声候选。
- 这批 bug report 是从 git commit metadata 推断出来的，不如 AboutWork 手写 bug log 严格；结论应标注为 git-history-derived case study。
- `selector_v1` 和 UI evidence v2 都是在当前 63 条上调出来的 fitted case-study 策略，需要用新增 Easy Finance bug logs 验证泛化。
