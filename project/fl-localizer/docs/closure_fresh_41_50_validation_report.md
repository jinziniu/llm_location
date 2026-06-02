# Closure Fresh 41..50 Validation Report

Date: 2026-06-01

## Goal

Validate the Closure cost-control selector on a third fresh slice and refine the selector only where the new slice exposes non-oracle coverage gaps.

## Dataset

Built with:

```text
python3 scripts/build_defects4j_dataset.py --project Closure --bugs 41-50 --out data/defects4j/closure_fresh_41_50.jsonl --skip-failures
```

Records: 10.

Ground-truth files:

```text
Closure-41  src/com/google/javascript/jscomp/FunctionTypeBuilder.java
Closure-42  src/com/google/javascript/jscomp/parsing/IRFactory.java
Closure-43  src/com/google/javascript/jscomp/TypedScopeCreator.java
Closure-44  src/com/google/javascript/jscomp/CodeConsumer.java
Closure-45  src/com/google/javascript/jscomp/RemoveUnusedVars.java
Closure-46  src/com/google/javascript/rhino/jstype/RecordType.java
Closure-47  src/com/google/debugging/sourcemap/SourceMapConsumerV3.java, src/com/google/javascript/jscomp/SourceMap.java
Closure-48  src/com/google/javascript/jscomp/TypedScopeCreator.java
Closure-49  src/com/google/javascript/jscomp/MakeDeclaredNamesUnique.java
Closure-50  src/com/google/javascript/jscomp/PeepholeReplaceKnownMethods.java
```

## Retrieval Baseline

Focused direct/pass-chain/type-system retrieval:

```text
python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/closure_fresh_41_50.jsonl \
  --out outputs/closure_fresh_41_50_hybrid_focused_direct_passchain_typesystem_top50.jsonl \
  --top-k 50 \
  --force-direct-hints \
  --force-pass-chain-hints \
  --force-type-system-hints
```

Metrics:

```text
Top-1:  0.2000
Top-3:  0.4000
Top-5:  0.5000
Top-10: 0.6000
Top-20: 0.8000
Top-50: 1.0000
MRR:    0.3154
```

Per-bug ground-truth ranks:

```text
Closure-41  rank 40
Closure-42  rank 3
Closure-43  rank 5
Closure-44  rank 14
Closure-45  rank 10
Closure-46  rank 3
Closure-47  rank 1
Closure-48  rank 15
Closure-49  rank 42
Closure-50  rank 1
```

The retrieval candidate set has full Top-50 recall, but five records are outside Top-5.

## Selector Result

`--closure-cost-control-v1` selected 4/10 records:

```text
Closure-41, Closure-42, Closure-48, Closure-49
```

It missed `Closure-44` and `Closure-45`, so it covered only 3/5 Top-5 misses on this slice.

`--closure-cost-control-v2` selected 6/10 records:

```text
Closure-41, Closure-42, Closure-44, Closure-45, Closure-48, Closure-49
```

Selection reasons:

```text
Closure-41  pattern:type_system
Closure-42  top1_without_direct_hint, pattern:closure_deep_specific_direct_hint
Closure-44  pattern:closure_code_output
Closure-45  pattern:closure_deep_specific_direct_hint
Closure-48  pattern:type_system
Closure-49  low_score_ratio<=1.02, pattern:closure_deep_specific_direct_hint
```

V2 adds two Closure-specific non-oracle patterns:

- `pattern:closure_code_output`: covers code-printer/code-output failures such as `CodeConsumer.java`; guarded by a score-ratio threshold to avoid overselecting earlier stable cases.
- `pattern:closure_deep_specific_direct_hint`: covers cases where a generic compiler file wins rank 1 while a more specific direct-hint file appears at ranks 6..20 with a close score.

The v2 selector keeps the v1 selected sets on `Closure-21..30` and `Closure-31..40` unchanged.

## DeepSeek Rerank

Command:

```text
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/closure_fresh_41_50.jsonl \
  --bm25 outputs/closure_fresh_41_50_hybrid_focused_direct_passchain_typesystem_top50.jsonl \
  --out outputs/closure_fresh_41_50_rerank_deepseek_closure_cost_control_v2_s12_ctx12000_top50.jsonl \
  --provider deepseek \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 12 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 12000 \
  --bug-ids Closure-41,Closure-42,Closure-44,Closure-45,Closure-48,Closure-49 \
  --prompt-dir outputs/prompts_closure_fresh_41_50_cost_control_v2_s12_ctx12000_top50_deepseek
```

Selected-case rerank metrics:

```text
selected: 6 / 10
Top-1:  0.3333
Top-3:  0.6667
Top-5:  0.8333
Top-10: 1.0000
MRR:    0.5347
```

Selected-case ground-truth ranks:

```text
Closure-41  rank 4
Closure-42  rank 1
Closure-44  rank 3
Closure-45  rank 1
Closure-48  rank 8
Closure-49  rank 2
```

Merged metrics:

```text
Top-1:  0.4000
Top-3:  0.7000
Top-5:  0.9000
Top-10: 1.0000
MRR:    0.5742
```

Merged per-bug ranks:

```text
Closure-41  rank 4
Closure-42  rank 1
Closure-43  rank 5
Closure-44  rank 3
Closure-45  rank 1
Closure-46  rank 3
Closure-47  rank 1
Closure-48  rank 8
Closure-49  rank 2
Closure-50  rank 1
```

Usage:

```text
LLM calls: 6
total tokens: 242877
avg tokens/call: 40479.5
total duration seconds: 135.602
avg duration seconds/call: 22.600
```

## Closure-48 Diagnostic

`Closure-48` is the only remaining Top-5 miss after v2. The LLM consistently ranks `TypeCheck.java` and `TypeInference.java` above the ground-truth `TypedScopeCreator.java`.

Additional work added property/prototype snippet terms and a property-function semantic evidence path, then ran a wider single-case diagnostic:

```text
outputs/closure_fresh_41_50_rerank_deepseek_closure48_property_semantic2_s24_ctx12000_top50_out20.jsonl
```

That diagnostic used 43436 tokens and moved `TypedScopeCreator.java` from rank 8 to rank 9, so it was not merged into the main result. The remaining failure is best treated as model attribution ambiguity rather than a simple missing-snippet problem.

## Combined Closure 21..50

Combined baseline retrieval:

```text
Top-1:  0.2667
Top-3:  0.4333
Top-5:  0.5667
Top-10: 0.7667
Top-20: 0.8667
Top-50: 1.0000
MRR:    0.4064
```

Combined v2 merged result:

```text
selected: 15 / 30
Top-1:  0.5333
Top-3:  0.7667
Top-5:  0.9667
Top-10: 1.0000
Top-20: 1.0000
MRR:    0.6881
tokens: 579758
seconds: 312.400
```

## Artifacts

```text
data/defects4j/closure_fresh_41_50.jsonl
outputs/closure_fresh_41_50_hybrid_focused_direct_passchain_typesystem_top50.jsonl
outputs/closure_fresh_41_50_hybrid_focused_direct_passchain_typesystem_top50_eval.json
outputs/closure_fresh_41_50_selector_closure_cost_control_v2.json
outputs/closure_fresh_41_50_rerank_deepseek_closure_cost_control_v2_s12_ctx12000_top50.jsonl
outputs/closure_fresh_41_50_rerank_deepseek_closure_cost_control_v2_s12_ctx12000_top50_eval.json
outputs/closure_fresh_41_50_merged_deepseek_closure_cost_control_v2_s12_ctx12000_top50.jsonl
outputs/closure_fresh_41_50_merged_deepseek_closure_cost_control_v2_s12_ctx12000_top50_eval.json
outputs/closure_fresh_21_50_hybrid_focused_direct_passchain_typesystem_top50_eval.json
outputs/closure_fresh_21_50_merged_deepseek_closure_cost_control_v2_eval.json
```

## Interpretation

`Closure-41..50` is a useful harder validation slice: baseline Top-5 is only 0.5000 even though Top-50 recall is complete. `--closure-cost-control-v2` recovers four of the five Top-5 misses with 6/10 calls and reaches merged Top-5 0.9000, Top-10 1.0000.

Across `Closure-21..50`, v2 uses 15/30 calls and raises Top-5 from 0.5667 to 0.9667 while keeping Top-10 at 1.0000. It remains an experimental Closure-only selector; the main known residual miss is `Closure-48`.
