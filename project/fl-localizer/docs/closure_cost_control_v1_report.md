# Closure Cost-Control V1 Report

日期：2026-06-01

## Goal

Reduce Closure selective rerank calls while preserving the strong Top-3/Top-5/Top-10 results from the `Closure-21..30` and `Closure-31..40` fresh validation slices.

## Selector

Implemented in:

```text
scripts/select_rerank_candidates.py
```

Flag:

```text
--closure-cost-control-v1
```

The selector is non-oracle at runtime. It uses only bug/test text, retrieval scores, direct-hint metadata, and pattern signals.

Rule summary:

- Keep low score-ratio only when the top-1 file lacks a direct hint.
- Keep `top1_without_direct_hint` when the first direct-hint candidate is missing or rank >= 3.
- Keep records with high direct-hint count.
- Keep pass-chain records when top-1 lacks a direct hint, direct-hint count is high, or score ratio >= 1.40.
- Keep type-system records when score ratio <= 1.10 or top-1 lacks a direct hint.
- Keep type-cycle records when top-1 lacks a direct hint.

## Results

```text
Closure-21..30:
selected: 4 / 10
ids: Closure-21, Closure-22, Closure-26, Closure-28
Top-1:  0.8000
Top-3:  1.0000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.9000
tokens: 159898
seconds: 65.553

Closure-31..40:
selected: 5 / 10
ids: Closure-33, Closure-36, Closure-37, Closure-39, Closure-40
Top-1:  0.4000
Top-3:  0.6000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.5900
tokens: 176983
seconds: 111.245

Closure-21..40 combined:
selected: 9 / 20
Top-1:  0.6000
Top-3:  0.8000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.7450
tokens: 336881
seconds: 176.798
```

Baseline retrieval on `Closure-21..40`:

```text
Top-1:  0.3000
Top-3:  0.4500
Top-5:  0.6000
Top-10: 0.8500
MRR:    0.4520
```

## Artifacts

```text
outputs/closure_fresh_21_30_selector_closure_cost_control_v1.json
outputs/closure_fresh_31_40_selector_closure_cost_control_v1.json
outputs/closure_fresh_21_40_hybrid_focused_direct_passchain_typesystem_top50_eval.json
outputs/closure_fresh_21_40_merged_deepseek_closure_cost_control_v1_eval.json
```

## Interpretation

`closure_cost_control_v1` preserves Top-3/Top-5/Top-10 on both fresh Closure slices while reducing calls from the broader 15/20 selected-case setup to 9/20 calls.

It should still be described as an experimental Closure-only selector. The rule was shaped using the current Closure fresh validation evidence and needs additional fresh Closure bugs before being treated as the final Closure strategy.
