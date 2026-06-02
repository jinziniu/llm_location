# Closure Cost-Control V3 Report

Date: 2026-06-01

## Goal

Extend the Closure-only cost-control selector from three fresh slices to four fresh slices while preserving the earlier selected sets.

## Selector

Implemented in:

```text
scripts/select_rerank_candidates.py
```

Flag:

```text
--closure-cost-control-v3
```

V3 keeps v2 behavior and adds two non-oracle Closure patterns:

- `pattern:closure_code_generator_output`: selects CodePrinter numeric-key output failures when `CodeGenerator.java` is present deeper in the candidate list and the top scores are close.
- `pattern:closure_validator_transform_failure`: selects transform-pass failures where an `AstValidator`/validator frame is the top candidate but a transform pass such as `FunctionRewriter.java` is a deeper direct-hint candidate.

Additional evidence support:

```text
src/fl_localizer/snippets.py
src/fl_localizer/prompts.py
```

- Numeric output snippets now preserve `addNumber`, negative/zero, `toString`, and value-conversion evidence.
- The rerank prompt now includes a code-printer numeric-output rule.

## Selected Sets

```text
Closure-21..30:
Closure-21, Closure-22, Closure-26, Closure-28

Closure-31..40:
Closure-33, Closure-36, Closure-37, Closure-39, Closure-40

Closure-41..50:
Closure-41, Closure-42, Closure-44, Closure-45, Closure-48, Closure-49

Closure-51..60:
Closure-51, Closure-52, Closure-54, Closure-55, Closure-56
```

V3 is unchanged from v2 on `Closure-21..50`.

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

Closure-51..60, 5 / 10 calls:
Top-1:  0.8000
Top-3:  0.9000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.8750
tokens: 186961
seconds: 125.958

Closure-21..60 combined, 20 / 40 calls:
Top-1:  0.6000
Top-3:  0.8000
Top-5:  0.9750
Top-10: 1.0000
Top-20: 1.0000
MRR:    0.7348
tokens: 766719
seconds: 438.358
```

Baseline retrieval on `Closure-21..60`:

```text
Top-1:  0.3000
Top-3:  0.4250
Top-5:  0.5750
Top-10: 0.7250
Top-20: 0.8250
Top-50: 1.0000
MRR:    0.4211
```

## Known Residual

`Closure-48` remains the only Top-5 miss:

```text
baseline rank: 15
v2/v3 merged rank: 8
wider property/prototype diagnostic rank: 9
```

This remains an attribution ambiguity where the model prefers `TypeCheck.java` and `TypeInference.java` over `TypedScopeCreator.java`.

## Artifacts

```text
outputs/closure_fresh_51_60_selector_closure_cost_control_v3.json
outputs/closure_fresh_51_60_merged_deepseek_closure_cost_control_v3_plus_closure51_numeric_s20_ctx12000_top50_eval.json
outputs/closure_fresh_21_60_hybrid_focused_direct_passchain_typesystem_top50_eval.json
outputs/closure_fresh_21_60_merged_deepseek_closure_cost_control_v3_plus_closure51_numeric_eval.json
```

## Interpretation

V3 is the strongest Closure cost-control variant so far: 20/40 calls, Top-5 0.9750, and Top-10 1.0000 across four fresh slices.

It should still be described as an experimental Closure-only selector. The validation set is broader, but the selector is still shaped around Closure-specific retrieval and failure patterns.
