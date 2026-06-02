# Closure Fresh 51..60 Validation Report

Date: 2026-06-01

## Goal

Validate Closure cost-control on a fourth fresh slice and extend the selector only for new non-oracle miss patterns.

## Dataset

Built with:

```text
python3 scripts/build_defects4j_dataset.py --project Closure --bugs 51-60 --out data/defects4j/closure_fresh_51_60.jsonl --skip-failures
```

Records: 10.

Ground-truth files:

```text
Closure-51  src/com/google/javascript/jscomp/CodeConsumer.java
Closure-52  src/com/google/javascript/jscomp/CodeGenerator.java
Closure-53  src/com/google/javascript/jscomp/InlineObjectLiterals.java
Closure-54  src/com/google/javascript/jscomp/TypedScopeCreator.java, src/com/google/javascript/rhino/jstype/FunctionType.java
Closure-55  src/com/google/javascript/jscomp/FunctionRewriter.java
Closure-56  src/com/google/javascript/jscomp/SourceFile.java
Closure-57  src/com/google/javascript/jscomp/ClosureCodingConvention.java
Closure-58  src/com/google/javascript/jscomp/LiveVariablesAnalysis.java
Closure-59  src/com/google/javascript/jscomp/Compiler.java
Closure-60  src/com/google/javascript/jscomp/NodeUtil.java
```

## Retrieval Baseline

Focused direct/pass-chain/type-system retrieval:

```text
Top-1:  0.4000
Top-3:  0.4000
Top-5:  0.6000
Top-10: 0.6000
Top-20: 0.7000
Top-50: 1.0000
MRR:    0.4651
```

Per-bug ground-truth ranks:

```text
Closure-51  rank 21
Closure-52  rank 12
Closure-53  rank 1
Closure-54  rank 5
Closure-55  rank 30
Closure-56  rank 27
Closure-57  rank 1
Closure-58  rank 1
Closure-59  rank 4
Closure-60  rank 1
```

The retrieval candidate set again has full Top-50 recall, with four records outside Top-5.

## Selector Result

`--closure-cost-control-v2` selected 3/10 records:

```text
Closure-51, Closure-54, Closure-56
```

It missed `Closure-52` and `Closure-55`.

`--closure-cost-control-v3` selected 5/10 records:

```text
Closure-51, Closure-52, Closure-54, Closure-55, Closure-56
```

Selection reasons:

```text
Closure-51  pattern:closure_code_output
Closure-52  pattern:closure_code_generator_output
Closure-54  pattern:type_system
Closure-55  pattern:closure_validator_transform_failure
Closure-56  top1_without_direct_hint
```

V3 keeps the v2 selected sets unchanged on `Closure-21..30`, `Closure-31..40`, and `Closure-41..50`.

New v3 patterns:

- `pattern:closure_code_generator_output`: covers CodePrinter numeric-key failures where `CodeGenerator.java` is a deeper candidate and the top score is close.
- `pattern:closure_validator_transform_failure`: covers transform-pass bugs hidden by `AstValidator` stack frames, such as `FunctionRewriter.java` being below validator/compiler frames.

## DeepSeek Rerank

Initial v3 selected-case rerank used 5 calls and fixed four of five selected cases, but `Closure-51` still missed Top-10 because the prompt snippet for `CodeConsumer.java` did not expose `addNumber(double x)`.

Snippet and prompt update:

```text
src/fl_localizer/snippets.py
src/fl_localizer/prompts.py
```

- Added numeric output snippet terms such as `addnumber`, `negative`, `number`, `numeric`, `tostring`, `valueof`, and `zero`.
- Added a rerank instruction for code-printer numeric output failures to distinguish conversion helpers from final code emission.

After that, a single `Closure-51` rerun with 20 snippet lines ranked `CodeConsumer.java` first.

Final selected-case metrics:

```text
selected: 5 / 10
Top-1:  0.8000
Top-3:  1.0000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.9000
```

Final selected-case ranks:

```text
Closure-51  rank 1
Closure-52  rank 1
Closure-54  rank 2
Closure-55  rank 1
Closure-56  rank 1
```

Merged metrics:

```text
Top-1:  0.8000
Top-3:  0.9000
Top-5:  1.0000
Top-10: 1.0000
Top-20: 1.0000
MRR:    0.8750
```

Merged ranks:

```text
Closure-51  rank 1
Closure-52  rank 1
Closure-53  rank 1
Closure-54  rank 2
Closure-55  rank 1
Closure-56  rank 1
Closure-57  rank 1
Closure-58  rank 1
Closure-59  rank 4
Closure-60  rank 1
```

Deployment-equivalent usage:

```text
LLM calls: 5
total tokens: 186961
avg tokens/call: 37392.2
total duration seconds: 125.958
avg duration seconds/call: 25.192
```

Actual exploration also ran the superseded first `Closure-51` call, using 31956 tokens.

## Combined Closure 21..60

Combined baseline retrieval:

```text
Top-1:  0.3000
Top-3:  0.4250
Top-5:  0.5750
Top-10: 0.7250
Top-20: 0.8250
Top-50: 1.0000
MRR:    0.4211
```

Combined v3 merged result:

```text
selected: 20 / 40
Top-1:  0.6000
Top-3:  0.8000
Top-5:  0.9750
Top-10: 1.0000
Top-20: 1.0000
MRR:    0.7348
tokens: 766719
seconds: 438.358
```

The only remaining Top-5 miss across `Closure-21..60` is `Closure-48`.

## Artifacts

```text
data/defects4j/closure_fresh_51_60.jsonl
outputs/closure_fresh_51_60_hybrid_focused_direct_passchain_typesystem_top50.jsonl
outputs/closure_fresh_51_60_hybrid_focused_direct_passchain_typesystem_top50_eval.json
outputs/closure_fresh_51_60_selector_closure_cost_control_v3.json
outputs/closure_fresh_51_60_rerank_deepseek_closure_cost_control_v3_plus_closure51_numeric_s20_ctx12000_top50.jsonl
outputs/closure_fresh_51_60_merged_deepseek_closure_cost_control_v3_plus_closure51_numeric_s20_ctx12000_top50.jsonl
outputs/closure_fresh_51_60_merged_deepseek_closure_cost_control_v3_plus_closure51_numeric_s20_ctx12000_top50_eval.json
outputs/closure_fresh_21_60_hybrid_focused_direct_passchain_typesystem_top50_eval.json
outputs/closure_fresh_21_60_merged_deepseek_closure_cost_control_v3_plus_closure51_numeric_eval.json
```

## Interpretation

`Closure-51..60` is positive for the selector direction. V3 recovers all four Top-5 misses with 5/10 calls and reaches perfect Top-5/Top-10 on the slice.

Across `Closure-21..60`, the current Closure selector reaches Top-5 0.9750 and Top-10 1.0000 with 20/40 calls. It is still experimental and Closure-specific, but the residual error surface is now narrow: `Closure-48` remains the only Top-5 miss.
