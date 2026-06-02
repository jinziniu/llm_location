# Mockito Fresh Validation Report: 31..38

日期：2026-05-31

## 1. Goal

Validate the Mockito selector on a second fresh slice after adding diagnostic-only pattern signals for the failure families observed in `Mockito-21..30`.

This run also stops before DeepSeek calls. The goal is to check selector behavior, not to optimize final LLM accuracy.

## 2. Dataset

Requested and built:

```text
Mockito-31..38
8 records
```

Output:

```text
data/defects4j/mockito_fresh_31_38.jsonl
```

## 3. Commands

Dataset build:

```bash
python3 scripts/build_defects4j_dataset.py \
  --project Mockito \
  --bugs 31-38 \
  --out data/defects4j/mockito_fresh_31_38.jsonl \
  --skip-failures
```

Focused hybrid retrieval:

```bash
python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/mockito_fresh_31_38.jsonl \
  --out outputs/mockito_fresh_31_38_hybrid_focused_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints
```

Evaluation:

```bash
python3 scripts/evaluate_predictions.py \
  --bugs data/defects4j/mockito_fresh_31_38.jsonl \
  --pred outputs/mockito_fresh_31_38_hybrid_focused_direct_top50.jsonl \
  --per-bug \
  --ks 1,3,5,10,20,50 \
  --out outputs/mockito_fresh_31_38_hybrid_focused_direct_top50_eval.json
```

Default tight selector:

```bash
python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/mockito_fresh_31_38.jsonl \
  --pred outputs/mockito_fresh_31_38_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_fresh_31_38_tight_selector.json \
  --mockito-tight-patterns
```

Diagnostic selector:

```bash
python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/mockito_fresh_31_38.jsonl \
  --pred outputs/mockito_fresh_31_38_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_fresh_31_38_tight_selector_with_diagnostics.json \
  --mockito-tight-patterns \
  --mockito-diagnostic-patterns
```

## 4. Retrieval Baseline

Focused hybrid/direct top50 result:

```text
bugs: 8
Top-1:  0.1250
Top-3:  0.5000
Top-5:  0.7500
Top-10: 0.8750
Top-20: 1.0000
Top-50: 1.0000
MRR:    0.3382
```

Per-bug rank:

| Bug | Correct rank | Top-5 |
|---|---:|---|
| Mockito-31 | 1 | yes |
| Mockito-32 | 4 | yes |
| Mockito-33 | 16 | no |
| Mockito-34 | 3 | yes |
| Mockito-35 | 3 | yes |
| Mockito-36 | 7 | no |
| Mockito-37 | 4 | yes |
| Mockito-38 | 3 | yes |

Interpretation:

- Candidate recall@50 is again sufficient for reranking.
- The fresh slice contains two Top-5 failures: `Mockito-33` and `Mockito-36`.

## 5. Default Tight Selector

Selected:

```text
Mockito-32, Mockito-33, Mockito-35, Mockito-36, Mockito-37
```

Summary:

```text
records: 8
selected: 5
selected_fraction: 0.6250
Top-3 miss coverage: 4 / 4
Top-5 miss coverage: 2 / 2
```

Reason counts:

```text
low_score_ratio<=1.02: 1
many_direct_hints>=7: 2
pattern:mockito_invocation_varargs: 1
top1_without_direct_hint: 3
```

Interpretation:

- The selector covers all Top-5 failures in this slice.
- The selected ratio is high, so this is not yet a cost-optimal selector.
- This slice does not require the two new diagnostic patterns to cover failures.

## 6. Diagnostic Selector

With `--mockito-diagnostic-patterns`:

```text
selected: 5 / 8
selected ids: Mockito-32, Mockito-33, Mockito-35, Mockito-36, Mockito-37
```

The diagnostic selector selected exactly the same cases as the default tight selector.

Interpretation:

- The two diagnostic patterns did not over-select on `Mockito-31..38`.
- This is a positive sanity check, but not enough to promote the patterns to default behavior.
- More evidence is needed before calling these production selector rules.

## 7. Hard Case Notes

### Mockito-33

Ground truth:

```text
src/org/mockito/internal/invocation/InvocationMatcher.java
```

Focused hybrid rank:

```text
16
```

The bug concerns inherited generics and polymorphic calls. The current selector catches it through low score ratio and many direct hints, not through the new diagnostic patterns.

### Mockito-36

Ground truth:

```text
src/org/mockito/internal/invocation/Invocation.java
```

Focused hybrid rank:

```text
7
```

The bug concerns calling real methods on interfaces. The current selector catches it through many direct hints.

## 8. Decision

Do not promote the diagnostic patterns to default production behavior yet.

Current conclusion:

- `Mockito-21..30`: diagnostic patterns recover two selector misses.
- `Mockito-31..38`: diagnostic patterns do not over-select, but also do not add coverage beyond default tight selector.
- Default tight selector covers all Top-5 failures on `Mockito-31..38`, but selected ratio is 62.5%.

Next:

- If running DeepSeek, the defensible selected set for `Mockito-31..38` is the default tight selector set of 5 cases.
- For method development, the next improvement should reduce selected ratio without losing Top-5 miss coverage.

## 9. Cost-Control v2 Follow-up

Added an experimental selector switch:

```text
--mockito-cost-control-v2
```

Recommended experimental command:

```bash
python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/mockito_fresh_31_38.jsonl \
  --pred outputs/mockito_fresh_31_38_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_fresh_31_38_tight_cost_control_v2_selector.json \
  --mockito-tight-patterns \
  --mockito-diagnostic-patterns \
  --mockito-cost-control-v2 \
  --score-ratio-threshold 0 \
  --direct-hint-count-threshold 0 \
  --no-top1-without-direct
```

Result on `Mockito-31..38`:

```text
selected: 4 / 8
selected ids: Mockito-32, Mockito-33, Mockito-36, Mockito-37
Top-3 miss coverage: 4 / 4
Top-5 miss coverage: 2 / 2
```

Comparison:

```text
default tight selector with diagnostics: 5 / 8 selected
cost-control v2: 4 / 8 selected
```

Interpretation:

- v2 removes one selected Top-5-success case while preserving Top-5 miss coverage.
- It is still experimental and should not become default until validated beyond these slices.

## 10. DeepSeek Rerank Follow-up

Date:

```text
2026-06-01
```

The cost-control v2 selected set was reranked with DeepSeek:

```text
Mockito-32, Mockito-33, Mockito-36, Mockito-37
```

Command:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/mockito_fresh_31_38.jsonl \
  --bm25 outputs/mockito_fresh_31_38_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_fresh_31_38_rerank_deepseek_cost_control_v2_s6_ctx12000_top50.jsonl \
  --provider deepseek \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 6 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 12000 \
  --bug-ids Mockito-32,Mockito-33,Mockito-36,Mockito-37 \
  --prompt-dir outputs/prompts_mockito_fresh_31_38_cost_control_v2_s6_ctx12000_top50
```

Selected-case result:

```text
bugs: 4
Top-1: 1.0000
Top-3: 1.0000
Top-5: 1.0000
Top-10: 1.0000
MRR:   1.0000
```

Every selected case moved to rank 1:

```text
Mockito-32: rank 1
Mockito-33: rank 1
Mockito-36: rank 1
Mockito-37: rank 1
```

Merged result over all 8 records:

```text
Top-1:  0.6250
Top-3:  1.0000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.7500
```

Compared with focused hybrid/direct:

```text
Top-1:  0.1250 -> 0.6250
Top-3:  0.5000 -> 1.0000
Top-5:  0.7500 -> 1.0000
Top-10: 0.8750 -> 1.0000
MRR:    0.3382 -> 0.7500
```

Usage:

```text
LLM calls: 4
total tokens: 99326
avg tokens/call: 24831.5
total duration seconds: 70.298
avg duration seconds/call: 17.575
```

Interpretation:

- This is a positive fresh-validation rerank result: the selector chose 4/8 cases, covered the 2/2 Top-5 failures, and all selected cases became rank 1 after DeepSeek.
- The result supports targeted reranking on fresh Mockito bugs, but cost-control v2 is still experimental because it was derived after earlier fresh-slice diagnostics.
