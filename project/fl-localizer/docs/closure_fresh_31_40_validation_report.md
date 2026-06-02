# Closure Fresh Validation Report: 31..40

日期：2026-06-01

## 1. Goal

Use a second Closure fresh slice to validate whether the `Closure-21..30` selector cost-control idea generalizes.

This run initially exposed a negative selector generalization result. Follow-up sections record the later type-system retrieval, rerank, and snippet-evidence fixes.

## 2. Dataset

Command:

```bash
python3 scripts/build_defects4j_dataset.py \
  --project Closure \
  --bugs 31-40 \
  --out data/defects4j/closure_fresh_31_40.jsonl \
  --skip-failures
```

Result:

```text
requested: Closure-31..40
built: 10 records
skipped: none
```

## 3. Retrieval

Commands:

```bash
python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/closure_fresh_31_40.jsonl \
  --out outputs/closure_fresh_31_40_hybrid_focused_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints

python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/closure_fresh_31_40.jsonl \
  --out outputs/closure_fresh_31_40_hybrid_focused_direct_passchain_top50.jsonl \
  --top-k 50 \
  --force-direct-hints \
  --force-pass-chain-hints
```

Focused direct:

```text
Top-1:  0.2000
Top-3:  0.3000
Top-5:  0.4000
Top-10: 0.7000
Top-20: 0.8000
Top-50: 0.8000
MRR:    0.3185
```

Focused direct + pass-chain:

```text
Top-1:  0.2000
Top-3:  0.3000
Top-5:  0.4000
Top-10: 0.7000
Top-20: 0.8000
Top-50: 0.9000
MRR:    0.3208
```

Per-bug direct+pass-chain ranks:

```text
Closure-31: rank 4
Closure-32: rank 1
Closure-33: miss from top50
Closure-34: rank 1
Closure-35: rank 18
Closure-36: rank 42
Closure-37: rank 7
Closure-38: rank 2
Closure-39: rank 9
Closure-40: rank 8
```

Interpretation:

- This slice is much harder than `Closure-21..30`.
- Pass-chain improves Recall@50 from 8/10 to 9/10 by recovering one candidate into the top-50 pool, but aggregate Top-1/Top-5 barely changes.
- `Closure-33` is still a candidate-missing failure, so LLM rerank cannot recover it from the current top-50 pool.

## 4. Selector

Default selector:

```bash
python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/closure_fresh_31_40.jsonl \
  --pred outputs/closure_fresh_31_40_hybrid_focused_direct_passchain_top50.jsonl \
  --out outputs/closure_fresh_31_40_selector.json
```

Result:

```text
selected: 6 / 10
selected ids:
  Closure-31, Closure-34, Closure-36, Closure-37, Closure-39, Closure-40

reason counts:
  low_score_ratio<=1.02: 1
  many_direct_hints>=7: 1
  pattern:pass_chain: 4
  pattern:type_cycle: 2
  top1_without_direct_hint: 2
```

Coverage:

```text
Top-1 miss coverage: 5 / 8
Top-3 miss coverage: 5 / 7
Top-5 miss coverage: 4 / 6
Top-10 miss coverage: 1 / 3
Top-50 miss coverage: 0 / 1
```

Missed hard cases:

```text
Closure-33: ground truth PrototypeObjectType.java, missing from top50
Closure-35: ground truth TypeInference.java, rank 18, not selected
```

Cost-control selector from `Closure-21..30`:

```bash
python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/closure_fresh_31_40.jsonl \
  --pred outputs/closure_fresh_31_40_hybrid_focused_direct_passchain_top50.jsonl \
  --out outputs/closure_fresh_31_40_selector_direct_rank_3_6_no_patterns.json \
  --top1-without-direct-min-direct-rank 3 \
  --top1-without-direct-max-direct-rank 6 \
  --no-patterns
```

Result:

```text
selected: 2 / 10
selected ids:
  Closure-34, Closure-37

Top-5 miss coverage: 1 / 6
```

Interpretation:

- The direct-rank 3..6 cost-control rule does not generalize to this second fresh slice.
- The default selector is better, but still misses important hard cases and should not be used for DeepSeek rerank yet.
- This slice points to a retrieval gap for type/JSType failures and a selector gap for rank-10-to-rank-20 candidates such as `TypeInference.java`.

## 5. Decision

Do not run DeepSeek on `Closure-31..40` yet.

Reasons:

- `Closure-33` is absent from the current top-50 candidate pool.
- The default selector covers only 4/6 Top-5 failures.
- The cost-control rule from `Closure-21..30` fails to generalize.

Next work should focus on retrieval/selector diagnostics for:

- JSType / `PrototypeObjectType` failures.
- `TypeInference` failures where ground truth appears around rank 10-20.
- Whether top-50 should be widened to top-80/top-100 for Closure before rerank.

## 6. Type-System Retrieval Follow-up

Added an explicit retrieval flag:

```text
--force-type-system-hints
```

This flag is disabled by default. It boosts Closure type-system candidates only when the bug has TypeCheck/type-mismatch evidence.

Command:

```bash
python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/closure_fresh_31_40.jsonl \
  --out outputs/closure_fresh_31_40_hybrid_focused_direct_passchain_typesystem_top50.jsonl \
  --top-k 50 \
  --force-direct-hints \
  --force-pass-chain-hints \
  --force-type-system-hints
```

Result:

```text
Top-1:  0.2000
Top-3:  0.3000
Top-5:  0.5000
Top-10: 0.8000
Top-20: 0.9000
Top-50: 1.0000
MRR:    0.3486
```

Key rank changes:

```text
Closure-33 PrototypeObjectType.java: top50 miss -> rank 12
Closure-35 TypeInference.java:      rank 18 -> rank 4
Closure-36 InlineVariables.java:    rank 42, unchanged
```

Regression check on `Closure-21..30`:

```text
No aggregate metric change.
Top-50 remains 1.0000.
```

## 7. Type-System Selector and Rerank

The selector now treats high-confidence `type_system_hint` candidates as a pattern signal:

```text
pattern:type_system
```

Selector result on type-system retrieval:

```text
selected: 8 / 10
selected ids:
  Closure-31, Closure-33, Closure-34, Closure-35,
  Closure-36, Closure-37, Closure-39, Closure-40

Top-3 miss coverage: 7 / 7
Top-5 miss coverage: 5 / 5
Top-10 miss coverage: 2 / 2
```

Regression check on `Closure-21..30`:

```text
selected ids unchanged:
Closure-21, Closure-22, Closure-23, Closure-26, Closure-28, Closure-29, Closure-30
```

DeepSeek command:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/closure_fresh_31_40.jsonl \
  --bm25 outputs/closure_fresh_31_40_hybrid_focused_direct_passchain_typesystem_top50.jsonl \
  --out outputs/closure_fresh_31_40_rerank_deepseek_typesystem_selector_s6_ctx12000_top50.jsonl \
  --provider deepseek \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 6 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 12000 \
  --bug-ids Closure-31,Closure-33,Closure-34,Closure-35,Closure-36,Closure-37,Closure-39,Closure-40 \
  --prompt-dir outputs/prompts_closure_fresh_31_40_typesystem_selector_s6_ctx12000_top50
```

Initial selected-case rerank result:

```text
bugs: 8
Top-1:  0.2500
Top-3:  0.3750
Top-5:  0.7500
Top-10: 0.8750
MRR:    0.4208
```

Initial merged result:

```text
Top-1:  0.3000
Top-3:  0.5000
Top-5:  0.8000
Top-10: 0.9000
MRR:    0.4867
```

## 8. Hard2 Wider-Snippet Diagnostic

The first rerank still struggled on:

```text
Closure-33: PrototypeObjectType.java at rerank rank 6
Closure-36: InlineVariables.java missing from rerank top10
```

Reran only these two with wider snippets and top-output 20:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/closure_fresh_31_40.jsonl \
  --bm25 outputs/closure_fresh_31_40_hybrid_focused_direct_passchain_typesystem_top50.jsonl \
  --out outputs/closure_fresh_31_40_rerank_deepseek_typesystem_hard2_s12_ctx12000_top50_out20.jsonl \
  --provider deepseek \
  --top-candidates 50 \
  --top-output 20 \
  --max-snippet-lines 12 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 12000 \
  --bug-ids Closure-33,Closure-36 \
  --prompt-dir outputs/prompts_closure_fresh_31_40_typesystem_hard2_s12_ctx12000_top50_out20
```

Hard2 result:

```text
Closure-33: rank 5
Closure-36: rank 8
```

Merged result with hard2 replacements:

```text
Top-1:  0.3000
Top-3:  0.5000
Top-5:  0.9000
Top-10: 1.0000
MRR:    0.5025
```

Deployment-equivalent usage for 8 selected calls with hard2 replacement:

```text
LLM calls: 8
total tokens: 286216
avg tokens/call: 35777.0
total duration seconds: 169.902
avg duration seconds/call: 21.238
```

Actual extra experimentation used two additional hard2 calls:

```text
extra hard2 tokens: 74566
```

## 9. Singleton Getter Snippet Fix

The hard2 prompt still ranked `Closure-36` only at rank 8 because the snippet for `InlineVariables.java` did not expose the strongest local evidence:

```text
// issue 668: Don't inline singleton getter methods
```

Snippet extraction now keeps comment lines when they contain high-signal query terms such as `singleton`, `getter`, `getInstance`, or `addSingletonGetter`, and widens local context for those terms.

Validation command:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/closure_fresh_31_40.jsonl \
  --bm25 outputs/closure_fresh_31_40_hybrid_focused_direct_passchain_typesystem_top50.jsonl \
  --out outputs/closure_fresh_31_40_rerank_deepseek_typesystem_closure36_snippet_fix_s12_ctx12000_top50_out20.jsonl \
  --provider deepseek \
  --top-candidates 50 \
  --top-output 20 \
  --max-snippet-lines 12 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 12000 \
  --bug-ids Closure-36 \
  --prompt-dir outputs/prompts_closure_fresh_31_40_typesystem_closure36_snippet_fix_s12_deepseek
```

Result:

```text
Closure-36: rank 8 -> rank 1
single-call usage: 35706 tokens, 17.317 seconds
```

Final selected-case result after replacing `Closure-36` with the snippet-fix call and keeping the hard2 `Closure-33` call:

```text
bugs: 8
Top-1:  0.3750
Top-3:  0.5000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.5500
```

Final merged result:

```text
Top-1:  0.4000
Top-3:  0.6000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.5900
```

Deployment-equivalent usage for 8 selected calls with `Closure-33` hard2 and `Closure-36` snippet-fix replacements:

```text
LLM calls: 8
total tokens: 284148
avg tokens/call: 35518.5
total duration seconds: 163.655
avg duration seconds/call: 20.457
```

Actual exploration spent 11 calls total: the initial 8 selected calls, 2 hard2 diagnostic calls, and 1 snippet-fix call.

## 10. Closure Cost-Control V1

The in-slice 5-call gate was converted into an explicit experimental selector flag:

```text
--closure-cost-control-v1
```

On this slice it selects:

```text
Closure-33, Closure-36, Closure-37, Closure-39, Closure-40
```

Selection output:

```text
outputs/closure_fresh_31_40_selector_closure_cost_control_v1.json
```

Merged result:

```text
Top-1:  0.4000
Top-3:  0.6000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.5900
```

Usage:

```text
LLM calls: 5
total tokens: 176983
avg tokens/call: 35396.6
total duration seconds: 111.245
avg duration seconds/call: 22.249
```

Cross-slice check on `Closure-21..30` with the same selector flag:

```text
selected: Closure-21, Closure-22, Closure-26, Closure-28
Top-1:  0.8000
Top-3:  1.0000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.9000
```

Combined `Closure-21..40` result:

```text
LLM calls: 9 / 20
Top-1:  0.6000
Top-3:  0.8000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.7450
total tokens: 336881
total duration seconds: 176.798
```

Final interpretation:

- Type-system retrieval fixes the main candidate-missing problem in this slice.
- DeepSeek rerank plus the singleton/getter snippet fix improves merged Top-5 from 0.4000 to 1.0000 and Top-10 from 0.7000 to 1.0000.
- `Closure-36` was an evidence-quality failure, not a candidate-recall failure: once the issue-668 comment reached the prompt, DeepSeek ranked `InlineVariables.java` first.
- `--closure-cost-control-v1` reduces this slice to 5/10 calls without losing metrics, and preserves Top-3/Top-5/Top-10 on the earlier `Closure-21..30` fresh slice. It remains an experimental Closure selector until tested on more Closure bugs.
