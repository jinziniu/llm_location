# Closure Fresh Validation Report: 21..30

日期：2026-06-01

## 1. Goal

Validate Closure-specific retrieval and selector behavior on a fresh slice:

```text
Closure-21..30
```

The main questions:

- Does focused hybrid/direct retrieval still keep ground truth in the top-50 candidate pool?
- Does `--force-pass-chain-hints` improve fresh retrieval beyond direct hints?
- Does the default selector cover retrieval Top-5 failures?
- If selected cases are reranked with DeepSeek, does the merged result improve?

## 2. Dataset

Command:

```bash
python3 scripts/build_defects4j_dataset.py \
  --project Closure \
  --bugs 21-30 \
  --out data/defects4j/closure_fresh_21_30.jsonl \
  --skip-failures
```

Result:

```text
requested: Closure-21..30
built: 10 records
skipped: none
```

## 3. Retrieval

Commands:

```bash
python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/closure_fresh_21_30.jsonl \
  --out outputs/closure_fresh_21_30_hybrid_focused_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints

python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/closure_fresh_21_30.jsonl \
  --out outputs/closure_fresh_21_30_hybrid_focused_direct_passchain_top50.jsonl \
  --top-k 50 \
  --force-direct-hints \
  --force-pass-chain-hints
```

Focused direct and direct+pass-chain produced the same file-level metrics on this slice:

```text
bugs: 10
Top-1:  0.4000
Top-3:  0.6000
Top-5:  0.7000
Top-10: 0.9000
Top-20: 0.9000
Top-50: 1.0000
MRR:    0.5553
```

Per-bug baseline ranks:

```text
Closure-21: rank 6
Closure-22: rank 6
Closure-23: rank 1
Closure-24: rank 1
Closure-25: rank 1
Closure-26: rank 5
Closure-27: rank 1
Closure-28: rank 50
Closure-29: rank 2
Closure-30: rank 2
```

Interpretation:

- Candidate recall@50 is sufficient for rerank: 10/10 ground-truth files are present.
- Pass-chain hints did not change the aggregate metric on this fresh slice.
- The main hard case is `Closure-28`, where the correct file appears only at rank 50.

## 4. Selector

Default selector on direct+pass-chain predictions:

```bash
python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/closure_fresh_21_30.jsonl \
  --pred outputs/closure_fresh_21_30_hybrid_focused_direct_passchain_top50.jsonl \
  --out outputs/closure_fresh_21_30_selector.json
```

Result:

```text
selected: 7 / 10
selected ids:
  Closure-21, Closure-22, Closure-23, Closure-26, Closure-28, Closure-29, Closure-30

reason counts:
  top1_without_direct_hint: 6
  low_score_ratio<=1.02: 1
  pattern:pass_chain: 1
```

Coverage:

```text
Top-1 miss coverage: 6 / 6
Top-3 miss coverage: 4 / 4
Top-5 miss coverage: 3 / 3
```

Tighter selector without `top1_without_direct_hint`:

```bash
python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/closure_fresh_21_30.jsonl \
  --pred outputs/closure_fresh_21_30_hybrid_focused_direct_passchain_top50.jsonl \
  --out outputs/closure_fresh_21_30_selector_no_top1_without_direct.json \
  --no-top1-without-direct
```

Result:

```text
selected: 2 / 10
selected ids:
  Closure-23, Closure-28
```

Interpretation:

- The default selector covers all retrieval misses, but selected ratio is high at 70%.
- The tighter selector is too conservative for this slice because it misses `Closure-21` and `Closure-22`, both Top-5 failures.
- `pattern:pass_chain` selected `Closure-23`, but that bug was already rank 1, so pass-chain did not contribute a fresh hard-case recovery here.

## 5. DeepSeek Rerank

Rerank command:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/closure_fresh_21_30.jsonl \
  --bm25 outputs/closure_fresh_21_30_hybrid_focused_direct_passchain_top50.jsonl \
  --out outputs/closure_fresh_21_30_rerank_deepseek_default_selector_s6_ctx12000_top50.jsonl \
  --provider deepseek \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 6 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 12000 \
  --bug-ids Closure-21,Closure-22,Closure-23,Closure-26,Closure-28,Closure-29,Closure-30 \
  --prompt-dir outputs/prompts_closure_fresh_21_30_default_selector_s6_ctx12000_top50
```

Selected-case rerank result:

```text
bugs: 7
Top-1: 1.0000
Top-3: 1.0000
Top-5: 1.0000
Top-10: 1.0000
MRR:   1.0000
```

Every selected case moved to rank 1:

```text
Closure-21: rank 1
Closure-22: rank 1
Closure-23: rank 1
Closure-26: rank 1
Closure-28: rank 1
Closure-29: rank 1
Closure-30: rank 1
```

Merged result over all 10 records:

```text
Top-1:  1.0000
Top-3:  1.0000
Top-5:  1.0000
Top-10: 1.0000
MRR:    1.0000
```

Compared with focused hybrid/direct:

```text
Top-1:  0.4000 -> 1.0000
Top-3:  0.6000 -> 1.0000
Top-5:  0.7000 -> 1.0000
Top-10: 0.9000 -> 1.0000
MRR:    0.5553 -> 1.0000
```

Usage:

```text
LLM calls: 7
total tokens: 275689
avg tokens/call: 39384.1
total duration seconds: 114.110
avg duration seconds/call: 16.301
```

## 6. Decision

This is a strong positive fresh-validation result for evidence-aware DeepSeek reranking on Closure:

- Retrieval recall@50 is good enough.
- The default selector covers all Top-5 failures.
- DeepSeek rerank moves all selected fresh cases to rank 1.

But the selector is not cost-optimal:

- It selects 7/10 records.
- The pass-chain pattern did not recover a fresh miss in this slice.
- `top1_without_direct_hint` is doing most of the useful coverage, but it is broad.

Next Closure work should focus on reducing selected ratio while preserving coverage of `Closure-21`, `Closure-22`, and `Closure-28` style failures.

## 7. Cost-Control Follow-up

Added optional selector controls:

```text
--top1-without-direct-min-direct-rank
--top1-without-direct-max-direct-rank
```

These do not change default behavior. They only constrain `top1_without_direct_hint` when explicitly passed.

Cost-control selector command:

```bash
python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/closure_fresh_21_30.jsonl \
  --pred outputs/closure_fresh_21_30_hybrid_focused_direct_passchain_top50.jsonl \
  --out outputs/closure_fresh_21_30_selector_direct_rank_3_6_no_patterns.json \
  --top1-without-direct-min-direct-rank 3 \
  --top1-without-direct-max-direct-rank 6 \
  --no-patterns
```

Result:

```text
selected: 4 / 10
selected ids:
  Closure-21, Closure-22, Closure-26, Closure-28

Top-3 miss coverage: 4 / 4
Top-5 miss coverage: 3 / 3
```

This selector avoids reranking:

```text
Closure-23: already rank 1
Closure-29: already rank 2
Closure-30: already rank 2
```

Merged result using the existing DeepSeek outputs for the 4 selected bugs:

```text
Top-1:  0.8000
Top-3:  1.0000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.9000
```

Estimated usage for the 4 selected calls:

```text
LLM calls: 4
total tokens: 159898
avg tokens/call: 39974.5
total duration seconds: 65.553
avg duration seconds/call: 16.388
```

Comparison:

| Method | LLM calls | Top-1 | Top-3 | Top-5 | MRR |
|---|---:|---:|---:|---:|---:|
| Focused direct/pass-chain | 0 | 0.4000 | 0.6000 | 0.7000 | 0.5553 |
| Default selector + DeepSeek | 7 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Direct-rank 3..6 no-pattern selector + DeepSeek | 4 | 0.8000 | 1.0000 | 1.0000 | 0.9000 |

Decision:

- The 4-call selector is a better cost-control candidate for Closure fresh reporting.
- The 7-call selector is useful as an upper-bound selected-rerank result.
- The direct-rank window rule needs another held-out Closure slice before being treated as a stable production selector.
