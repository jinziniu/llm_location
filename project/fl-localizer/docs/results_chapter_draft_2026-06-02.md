# Results Chapter Draft

Date: 2026-06-02

This draft turns the current experiment outputs into a paper/thesis-ready results section. It separates in-sample pilot results, fresh validation, and the first frozen held-out validation.

## Main Claim

The main method is `Selective Evidence-Aware LLM Fault Localization`: focused hybrid retrieval first builds a file-level candidate pool, deterministic evidence rules decide which cases need LLM reranking, and one-shot DeepSeek rerank is applied only to selected cases. Non-selected cases fall back to the retrieval ranking.

The current results support three claims:

- LLM reranking improves developer-facing Top-k ranking when the faulty file is present in the candidate pool.
- Selective rerank can reduce LLM calls while preserving or improving Top-k metrics.
- Selector recall is now the main limitation: missed rerank opportunities, not selected-case rerank quality, explain the remaining held-out failures.

## Pilot Results

The Defects4J pilot covers six projects with 20 bugs each: `Lang`, `Math`, `Chart`, `Time`, `Closure`, and `Mockito`. These runs established the basic method and also exposed project-specific evidence needs.

| Project | Best Current Setting | Bugs | Top-1 | Top-3 | Top-5 | MRR |
|---|---|---:|---:|---:|---:|---:|
| Lang | BM25 + DeepSeek rerank | 20 | 0.95 | 1.00 | 1.00 | 0.9750 |
| Math | Hybrid/direct + compact evidence DeepSeek | 20 | 0.90 | 0.95 | 1.00 | 0.9350 |
| Chart | Focused hybrid/direct | 20 | 0.85 | 0.95 | 1.00 | 0.9040 |
| Time | Focused hybrid/direct + DeepSeek hard4 | 20 | 0.90 | 1.00 | 1.00 | 0.9500 |
| Closure | Focused hybrid/direct + DeepSeek hard8 + pass-chain/type-cycle rules | 20 | 0.40 | 0.80 | 1.00 | 0.6225 |
| Mockito | Focused hybrid/direct + tight selector9 DeepSeek | 20 | 0.65 | 1.00 | 1.00 | 0.8000 |

Interpretation:

- `Lang`, `Math`, `Chart`, and `Time` show that retrieval plus evidence-aware rerank can reach strong Top-5 performance on small Defects4J pilot slices.
- `Closure` and `Mockito` are harder and drove the selector and evidence-rule development.
- Pilot results are useful for method development, but fresh and held-out runs should carry more weight in the final validity discussion.

## Fresh And Held-Out Validation

The following table should be the primary Defects4J generalization table in the thesis. `Closure-21..60` and `Mockito-31..38` are fresh validations. `Closure-61..80` is the first explicitly frozen held-out protocol: the protocol was written before running the held-out set, and no selector/prompt/snippet tuning was applied based on its results.

| Dataset | Setting | Bugs | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Closure-21..60 | focused retrieval baseline | 40 | 0 | 0.3000 | 0.4250 | 0.5750 | 0.7250 | 0.4211 |
| Closure-21..60 | cost-control v3 + DeepSeek | 40 | 20 | 0.6000 | 0.8000 | 0.9750 | 1.0000 | 0.7348 |
| Closure-61..80 held-out | frozen retrieval baseline | 19 | 0 | 0.4737 | 0.4737 | 0.5789 | 0.7368 | 0.5344 |
| Closure-61..80 held-out | frozen cost-control v3 + DeepSeek | 19 | 6 | 0.6316 | 0.7368 | 0.7895 | 0.8947 | 0.7018 |
| Mockito-31..38 fresh | focused retrieval baseline | 8 | 0 | 0.1250 | 0.5000 | 0.7500 | 0.8750 | 0.3382 |
| Mockito-31..38 fresh | cost-control v2 + DeepSeek | 8 | 4 | 0.6250 | 1.0000 | 1.0000 | 1.0000 | 0.7500 |

Recommended thesis wording:

> On the frozen Closure-61..80 held-out slice, the focused retrieval baseline achieved Top-1 0.4737, Top-5 0.5789, Top-10 0.7368, and MRR 0.5344. The frozen selective rerank protocol selected 6 of 19 bugs for one-shot DeepSeek reranking. After merging reranked cases with retrieval fallback, Top-1 increased to 0.6316, Top-5 to 0.7895, Top-10 to 0.8947, and MRR to 0.7018. This indicates that the reranker provides useful ranking improvements under a selective invocation budget, while remaining misses are mainly due to selector false negatives.

## Closure Held-Out Detail

The held-out run selected 6/19 cases. All selected cases reached Top-3 after DeepSeek rerank.

| Bug | Selected | Selector Reason | Baseline Rank | Merged Rank |
|---|---|---|---:|---:|
| Closure-64 | yes | low score ratio | 4 | 2 |
| Closure-69 | yes | type-system pattern | 1 | 1 |
| Closure-70 | yes | type-system pattern | 14 | 3 |
| Closure-72 | yes | deep-specific direct hint | 12 | 1 |
| Closure-76 | yes | deep-specific direct hint | 18 | 1 |
| Closure-77 | yes | code-output pattern | 8 | 1 |

The selector covered 4 of the 8 baseline Top-5 failures: `Closure-70`, `Closure-72`, `Closure-76`, and `Closure-77`. It missed the other 4 baseline Top-5 failures: `Closure-61`, `Closure-65`, `Closure-67`, and `Closure-75`.

## Reporting Notes

- Report candidate Recall@20 and Recall@50 from retrieval baseline outputs, not merged selective-rerank outputs. The merged output is intentionally truncated to Top-10.
- Do not claim full Defects4J completion. The current evidence is a 120-bug main pilot plus fresh and held-out validations.
- Do not tune on `Closure-61..80`. Use its failures to define the next frozen protocol.
- Keep controlled agentic inspection and verifier results as RQ5 / ablation material, not as the main method.

## Source Artifacts

```text
docs/current_results_report.md
docs/experiment_design.md
docs/frozen_protocol_2026-06-01.md
docs/closure_heldout_61_80_validation_report.md
outputs/closure_heldout_61_80_hybrid_focused_direct_passchain_typesystem_top50_eval.json
outputs/closure_heldout_61_80_merged_deepseek_closure_cost_control_v3_s12_ctx12000_top50_eval.json
```
