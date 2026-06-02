# Closure Cost-Control V2 Report

Date: 2026-06-01

## Goal

Extend the Closure-only cost-control selector from `Closure-21..40` to `Closure-41..50` without increasing calls on the earlier fresh slices.

## Selector

Implemented in:

```text
scripts/select_rerank_candidates.py
```

Flag:

```text
--closure-cost-control-v2
```

The selector is non-oracle at runtime. It uses bug/test text, retrieval scores, direct-hint metadata, pass-chain/type-system pattern signals, and file names from the retrieved candidate list.

V2 keeps the v1 logic and adds two Closure-specific patterns:

- `pattern:closure_code_output`: selects code-printer/code-output failures when a code-output file is a plausible retrieved candidate. A score-ratio guard avoids selecting stable earlier cases.
- `pattern:closure_deep_specific_direct_hint`: selects cases where a generic top file wins while a more specific direct-hint candidate appears deeper in the top-20 with a close score.

Snippet and prompt-evidence support was also extended for property/prototype declarations:

```text
src/fl_localizer/snippets.py
scripts/run_llm_rerank.py
```

This helped expose `TypedScopeCreator` property-declaration evidence, but did not fix the final `Closure-48` attribution miss.

## Selected Sets

```text
Closure-21..30:
Closure-21, Closure-22, Closure-26, Closure-28

Closure-31..40:
Closure-33, Closure-36, Closure-37, Closure-39, Closure-40

Closure-41..50:
Closure-41, Closure-42, Closure-44, Closure-45, Closure-48, Closure-49
```

V2 is unchanged from v1 on `Closure-21..30` and `Closure-31..40`.

## Results

```text
Closure-21..30, 4 / 10 calls:
Top-1:  0.8000
Top-3:  1.0000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.9000
tokens: 159898
seconds: 65.553

Closure-31..40, 5 / 10 calls:
Top-1:  0.4000
Top-3:  0.6000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.5900
tokens: 176983
seconds: 111.245

Closure-41..50, 6 / 10 calls:
Top-1:  0.4000
Top-3:  0.7000
Top-5:  0.9000
Top-10: 1.0000
MRR:    0.5742
tokens: 242877
seconds: 135.602

Closure-21..50 combined, 15 / 30 calls:
Top-1:  0.5333
Top-3:  0.7667
Top-5:  0.9667
Top-10: 1.0000
Top-20: 1.0000
MRR:    0.6881
tokens: 579758
seconds: 312.400
```

Baseline retrieval on `Closure-21..50`:

```text
Top-1:  0.2667
Top-3:  0.4333
Top-5:  0.5667
Top-10: 0.7667
Top-20: 0.8667
Top-50: 1.0000
MRR:    0.4064
```

## Known Residual

`Closure-48` remains outside Top-5 after rerank:

```text
baseline rank: 15
v2 merged rank: 8
wider property/prototype diagnostic rank: 9
```

The diagnostic consumed 43436 extra tokens and was not merged. The model over-ranks `TypeCheck.java` and `TypeInference.java`; this looks like an attribution ambiguity rather than missing candidate recall or missing snippet evidence.

## Artifacts

```text
outputs/closure_fresh_21_30_selector_closure_cost_control_v1.json
outputs/closure_fresh_31_40_selector_closure_cost_control_v1.json
outputs/closure_fresh_41_50_selector_closure_cost_control_v2.json
outputs/closure_fresh_21_50_hybrid_focused_direct_passchain_typesystem_top50_eval.json
outputs/closure_fresh_21_50_merged_deepseek_closure_cost_control_v2_eval.json
```

## Interpretation

V2 is the strongest Closure cost-control variant so far: 15/30 calls, Top-5 0.9667, and Top-10 1.0000 across three fresh slices.

It should still be described as an experimental Closure-only selector. The rule has broader validation than v1, but it is still shaped around Closure fresh evidence and has one unresolved Top-5 miss.
