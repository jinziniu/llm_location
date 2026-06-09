# AboutWork Committed-60 Selective Rerank Results

Date: 2026-06-08

This note records the rerun of the AboutWork real-project experiment after
updating the dataset to `committed-60`.

## Protocol

Dataset:

```text
data/aboutwork/aboutwork_committed_60.jsonl
```

Retrieval baseline:

```text
outputs/aboutwork_committed_60_bm25_top50.jsonl
outputs/aboutwork_committed_60_bm25_top50_eval.json
```

Selector:

```text
scripts/select_aboutwork_rerank_candidates.py
score_ratio_threshold = 1.02
selected = 16 / 60
selected_fraction = 0.2667
```

The selector is non-oracle. It uses BM25 confidence ratio, simple business-domain
mismatch checks, and a narrow management-command noise rule. It does not read
ground truth files or fixed diffs.

LLM rerank:

```text
provider: deepseek
model: deepseek-v4-flash
top_candidates: 50
top_output: 10
include_retrieval_evidence: true
```

Final merged output:

```text
outputs/aboutwork_committed_60_bm25_plus_deepseek_selector_v3.jsonl
outputs/aboutwork_committed_60_bm25_plus_deepseek_selector_v3_eval.json
```

The merged output keeps Top-10 predictions. Top-50 should be read from the BM25
retrieval baseline, not from the merged rerank output.

## Aggregate Results

| Method | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | Top-50 | MRR |
|---|---:|---:|---:|---:|---:|---:|---:|
| BM25 production top50 | 0 / 60 | 0.5667 | 0.8333 | 0.9167 | 0.9333 | 1.0000 | 0.7015 |
| BM25 + selector_v3 + DeepSeek | 16 / 60 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | n/a | 0.8117 |

Delta over BM25:

| Metric | Delta |
|---|---:|
| Top-1 | +0.1333 |
| Top-3 | +0.1167 |
| Top-5 | +0.0500 |
| Top-10 | +0.0333 |
| MRR | +0.1102 |

## Selected-Case Behavior

On the 16 selected cases only:

| Subset | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---:|---:|---:|---:|---:|
| BM25 selected subset | 7 / 16 | 9 / 16 | 13 / 16 | 14 / 16 | 0.5486 |
| DeepSeek selected subset | 15 / 16 | 16 / 16 | 16 / 16 | 16 / 16 | 0.9688 |

Rank changes on selected cases:

| Bug ID | BM25 Rank | DeepSeek Rank |
|---|---:|---:|
| `aboutwork-20260526-008` | 7 | 1 |
| `aboutwork-20260520-001` | 5 | 2 |
| `aboutwork-20260505-002` | 5 | 1 |
| `aboutwork-20260514-003` | 37 | 1 |
| `aboutwork-20251217-001` | 4 | 1 |
| `aboutwork-20260417-001` | 3 | 1 |
| `aboutwork-20260327-003` | 3 | 1 |
| `aboutwork-20260312-001` | 11 | 1 |
| `aboutwork-20260130-001` | 5 | 1 |

Summary:

- Top-1 gains: 8 cases.
- Top-3 gains: 7 cases.
- Top-5 gains: 3 cases.
- Top-10 gains: 2 cases.
- No selected case regressed out of Top-10.

## Remaining Errors

| Bug ID | Ground Truth | BM25 Rank | Final Rank | Error Type |
|---|---|---:|---:|---|
| `aboutwork-20260528-002` | `backend/chatbot_v2/planning.py` | 14 | n/a | selector false negative; chatbot management/orchestrator files dominated lexical evidence |
| `aboutwork-20260603-001` | `backend/opensearch/connectors.py` | 26 | n/a | selector false negative; Bedrock/LLM failure wording pulled retrieval toward chatbot orchestration and settings |

Both remaining Top-10 misses were not sent to DeepSeek. This makes selector
recall the main remaining weakness for AboutWork-60.

## LLM Usage

```text
records: 16
total_tokens: 519530
total_prompt_tokens: 486579
total_completion_tokens: 32951
avg_total_tokens: 32470.62
total_duration_seconds: 336.034
avg_duration_seconds: 21.002
```

Usage file:

```text
outputs/aboutwork_committed_60_rerank_deepseek_selector_v3_usage.json
```

## RQ5 Agentic / Verifier Extension

After the one-shot rerank run, the same 16 selected cases were also rerun with
controlled agentic inspection and verifier rerank.

| Method | Selected Records | Model Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR | Total Tokens |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BM25 + selector_v3 + one-shot DeepSeek | 16 / 60 | 16 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 519530 |
| BM25 + selector_v3 + agentic DeepSeek s2 | 16 / 60 | 40 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 440542 |
| BM25 + selector_v3 + agentic s2 + verifier | 16 / 60 | 56 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 589260 |

The one-shot, agentic, and agentic + verifier runs have identical correct ranks
on all 60 records. The verifier adds 148718 tokens and 196.194 seconds without
changing aggregate metrics or per-bug correct ranks.

Detailed RQ5 note:

```text
docs/aboutwork_committed_60_agentic_verifier_results_2026-06-08.md
```

## Interpretation

AboutWork committed-60 is now the current real-project AboutWork result for
RQ4. The expanded dataset is larger than the earlier committed-39 case study and
keeps the same non-oracle selector family. Selective DeepSeek rerank improves all
reported Top-k metrics and MRR over BM25 while calling the LLM on only 26.7% of
the records.

The main remaining limitation is selector recall, not selected-case reranking:
DeepSeek fixed all selected cases into Top-3, but two unselected cases remained
outside Top-10.

The RQ5 extension does not change the main conclusion. Agentic inspection is
workable, but it does not improve over one-shot rerank on AboutWork-60; verifier
is again a negative ablation.
