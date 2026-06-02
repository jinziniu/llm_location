# Fresh Validation Plan for Selective Evidence-Aware Fault Localization

日期：2026-05-31

## 1. 目的

当前 Defects4J、AboutWork 和 Easy Finance 结果已经证明主方向可行，但多个 selector 和 evidence rules 是在 pilot 数据上调出来的。下一步不能继续只在同一批样本上优化，否则论文里会被质疑 overfitting。

本计划目标是用 fresh validation 检查：

- Mockito tight selector9 是否能泛化到未调参 bugs。
- Closure pass-chain / type-cycle 规则能否转成非 oracle gate。
- AboutWork selector_v3 是否能泛化到新增公司 bug logs。
- Easy Finance selector_v1 + UI evidence v2 是否能泛化到新增 commits 或新时间段 bug records。
- RQ5 agentic inspection 是否只在 one-shot 失败且 evidence 不足的 case 上有价值。

## 2. 方法边界

主方法：

```text
retrieval -> evidence construction -> selector -> one-shot DeepSeek rerank
```

扩展方法：

```text
controlled agentic inspection
agentic + verifier
```

实验原则：

- Fresh validation 不能根据新样本 ground truth 调 selector。
- Ground truth、fixed commit diff、post-fix code 只用于 evaluation。
- 先跑 retrieval 和 selector，再决定是否调用 LLM。
- 先报告 selector selected ratio 和 candidate recall，再报告 rerank 效果。
- Agentic/verifier 只跑 one-shot 明确失败且 evidence 不足的样例。

## 3. Validation Set 设计

### 3.1 Mockito Fresh Bugs

推荐第一批：

```text
Mockito-21..30
```

原因：

- Mockito-1..20 已用于 tight selector9 调参。
- Mockito active bugs 至少到 38，可以先取 21..30 作为 10-bug fresh slice。
- 先做 10 条，控制 checkout/test 和 LLM 成本。

目标：

- 检查 tight selector9 的 selected ratio。
- 检查 selected cases 是否覆盖 baseline Top-3 / Top-5 miss。
- 检查 MockMaker/ByteBuddy evidence rule 是否只在相关 case 触发。

建议命令：

```bash
python3 scripts/build_defects4j_dataset.py \
  --project Mockito \
  --bugs 21-30 \
  --out data/defects4j/mockito_fresh_21_30.jsonl \
  --skip-failures

python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/mockito_fresh_21_30.jsonl \
  --out outputs/mockito_fresh_21_30_hybrid_focused_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints

python3 scripts/evaluate_predictions.py \
  --bugs data/defects4j/mockito_fresh_21_30.jsonl \
  --pred outputs/mockito_fresh_21_30_hybrid_focused_direct_top50.jsonl \
  --per-bug \
  > outputs/mockito_fresh_21_30_hybrid_focused_direct_top50_eval.json

python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/mockito_fresh_21_30.jsonl \
  --pred outputs/mockito_fresh_21_30_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_fresh_21_30_tight_selector.json \
  --mockito-tight-patterns
```

只有 selector 结果合理时再调用 DeepSeek：

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/mockito_fresh_21_30.jsonl \
  --bm25 outputs/mockito_fresh_21_30_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_fresh_21_30_rerank_deepseek_tight_selector.jsonl \
  --provider deepseek \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 6 \
  --bug-ids <selected_ids>
```

通过标准：

- Retrieval Recall@50 接近 1.00。
- Selector 不应选择过多样本，目标 selected ratio 不超过 50%。
- 如果 baseline Top-5 miss 存在，selector 应覆盖大部分 miss。
- 合并 rerank 后 Top-3 / Top-5 应高于 retrieval baseline。

### 3.2 Closure Rule Validation

推荐第一批：

```text
Closure-21..30
```

目标：

- 不再手动指定 Closure-13 / Closure-4。
- 检查 pass-chain 和 type-cycle rules 是否能在新 bugs 中自动触发。
- 如果没有触发，也要记录为有效结果，说明规则是 narrow gate，不是泛化 boost。

建议先只跑 retrieval 和 selector：

```bash
python3 scripts/build_defects4j_dataset.py \
  --project Closure \
  --bugs 21-30 \
  --out data/defects4j/closure_fresh_21_30.jsonl \
  --skip-failures

python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/closure_fresh_21_30.jsonl \
  --out outputs/closure_fresh_21_30_hybrid_focused_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints \
  --force-pass-chain-hints

python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/closure_fresh_21_30.jsonl \
  --pred outputs/closure_fresh_21_30_hybrid_focused_direct_top50.jsonl \
  --out outputs/closure_fresh_21_30_selector.json
```

通过标准：

- pass-chain / type-cycle 规则只在 evidence 明确时触发。
- 如果触发，检查是否改善 candidate recall 或 rerank rank。
- 如果不触发，不能强行扩大规则；记录为规则覆盖范围有限。

### 3.3 AboutWork Fresh Logs

当前 AboutWork 只有 39 条 committed logs，selector_v3 是 fitted case-study 策略。fresh validation 需要新增同事记录或后续真实 bug logs。

最小验证集：

```text
10 new committed bug logs
```

执行顺序：

```text
append logs -> build dataset -> BM25 production -> selector_v3 -> selected rerank -> merge -> evaluate
```

通过标准：

- selector_v3 selected ratio 维持在 20% 到 40%。
- Top-3 / Top-5 相比 BM25 production 提升。
- domain mismatch rules 不应大量误选无关样本。

### 3.4 Easy Finance Fresh Commits

当前 Easy Finance clean63 / strict62 是 git-history-derived case study，selector_v1 和 UI evidence v2 已经在该数据上调过。

推荐 fresh validation：

```text
new commits after current extraction window
or a held-out slice not used during selector tuning
```

通过标准：

- UI evidence v2 仍能提升 Top-3 / Top-5。
- `loading`、`currency`、`admin users` 等 frontend rules 不应互相污染。
- strict filtering 前后要分别报告，避免数据清洗后只保留容易样本。

## 4. RQ5 Agentic 再设计

当前 Easy Finance strict62 结论：

```text
one-shot UI evidence v2: MRR 0.6817
agentic s2:            MRR 0.6831
agentic + verifier:    MRR 0.6804
```

这说明 agentic 可以运行，但没有明显优于 one-shot。下一轮不要扩大到全部 selected cases，而是只选：

- one-shot Top-3 miss。
- 真实文件在 candidate pool 内。
- one-shot snippet 明显没有覆盖关键方法/组件。
- agent 工具可以通过 search/read 访问到缺失 evidence。

通过标准：

- Agentic 在 targeted failure set 上提升 MRR。
- Token 成本增长有明确收益解释。
- Verifier 只有在 agent top-10 evidence 更干净时才重跑。

## 5. 报告格式

每个 fresh validation 都按同一结构写入 worklog：

```text
Goal
Dataset
Commands
Outputs
Selector selected ratio
Retrieval baseline metrics
Rerank merged metrics
Cost
Failure analysis
Decision: keep / revise / discard rule
```

最终结果表必须分开：

- Main method: selective one-shot rerank。
- Extension: controlled agentic inspection。
- Ablation: verifier / snippet variants。
- Diagnostic: manual or fitted pilot add-ons。

## 6. 当前推荐下一步

已完成第一轮 Mockito fresh 21..30 的 non-LLM 部分：

```text
build dataset -> focused hybrid retrieval -> evaluate -> tight selector report
```

结果显示 selector 只覆盖 2/4 个 Top-5 failures，因此暂不调用 DeepSeek。

新的推荐下一步：

```text
Do diagnostic-only selector analysis for:
- Mockito primitive default values
- Mockito InjectMocks exact type / ancestor matching
```

This diagnostic analysis has now been run.

Result:

- On `Mockito-21..30`, diagnostic patterns recover the two missed Top-5 failures.
- On `Mockito-31..38`, diagnostic patterns do not select any additional cases beyond the default tight selector.
- Default tight selector covers all Top-5 failures in `Mockito-31..38`, but selects 5/8 cases.

Updated recommendation:

```text
Do not promote diagnostic patterns or cost-control v2 to default yet.
If spending LLM calls next, use Mockito-31..38 cost-control v2 selected set:
Mockito-32, Mockito-33, Mockito-36, Mockito-37
```

The current experimental cost-control v2 selector selects 21/37 cases across `Mockito-1..20`, `Mockito-21..30`, and `Mockito-31..38`, while covering 13/13 retrieval Top-5 failures. This is better than pattern-only tight selector on fresh coverage and cheaper than the broader full no-top1 diagnostic selector, but it still needs more validation before becoming the default method.
