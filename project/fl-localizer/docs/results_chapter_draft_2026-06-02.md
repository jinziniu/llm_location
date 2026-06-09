# Results Chapter Draft

Date: 2026-06-08

This draft turns the current experiment outputs into a paper/thesis-ready results section. It separates in-sample pilot results, fresh validation, and frozen held-out validation.

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

The following table should be the primary Defects4J generalization table in the thesis. `Closure-21..60` and `Mockito-31..38` are fresh validations. `Closure-61..80` and `Closure-81..100` are explicitly frozen held-out protocols: each protocol was written before running the held-out set, and no selector/prompt/snippet tuning was applied based on its results.

| Dataset | Setting | Bugs | LLM Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Closure-21..60 | focused retrieval baseline | 40 | 0 | 0.3000 | 0.4250 | 0.5750 | 0.7250 | 0.4211 |
| Closure-21..60 | cost-control v3 + DeepSeek | 40 | 20 | 0.6000 | 0.8000 | 0.9750 | 1.0000 | 0.7348 |
| Closure-61..80 held-out | frozen retrieval baseline | 19 | 0 | 0.4737 | 0.4737 | 0.5789 | 0.7368 | 0.5344 |
| Closure-61..80 held-out | frozen cost-control v3 + DeepSeek | 19 | 6 | 0.6316 | 0.7368 | 0.7895 | 0.8947 | 0.7018 |
| Closure-81..100 held-out | frozen retrieval baseline | 19 | 0 | 0.3158 | 0.5789 | 0.6316 | 0.6842 | 0.4815 |
| Closure-81..100 held-out | frozen cost-control v3 + DeepSeek | 19 | 5 | 0.4737 | 0.6842 | 0.7368 | 0.7895 | 0.6009 |
| Closure-61..100 held-out aggregate | frozen retrieval baseline | 38 | 0 | 0.3947 | 0.5263 | 0.6053 | 0.7105 | 0.5080 |
| Closure-61..100 held-out aggregate | frozen cost-control v3 + DeepSeek | 38 | 11 | 0.5526 | 0.7105 | 0.7632 | 0.8421 | 0.6513 |
| Mockito-31..38 fresh | focused retrieval baseline | 8 | 0 | 0.1250 | 0.5000 | 0.7500 | 0.8750 | 0.3382 |
| Mockito-31..38 fresh | cost-control v2 + DeepSeek | 8 | 4 | 0.6250 | 1.0000 | 1.0000 | 1.0000 | 0.7500 |

Recommended thesis wording:

> On the frozen Closure-61..80 held-out slice, the focused retrieval baseline achieved Top-1 0.4737, Top-5 0.5789, Top-10 0.7368, and MRR 0.5344. The frozen selective rerank protocol selected 6 of 19 bugs for one-shot DeepSeek reranking. After merging reranked cases with retrieval fallback, Top-1 increased to 0.6316, Top-5 to 0.7895, Top-10 to 0.8947, and MRR to 0.7018. This indicates that the reranker provides useful ranking improvements under a selective invocation budget, while remaining misses are mainly due to selector false negatives.

> A second frozen Closure-81..100 held-out run showed the same pattern. The selector chose 5 of 19 bugs. Selected-case rerank reached Top-3 1.0000 and the merged result improved Top-1 from 0.3158 to 0.4737, Top-5 from 0.6316 to 0.7368, Top-10 from 0.6842 to 0.7895, and MRR from 0.4815 to 0.6009. This reinforces the selected-case rerank finding, while also exposing selector-recall and candidate-recall limits.

> Aggregating the two frozen Closure held-out slices gives 38 bugs. The selective protocol used 11 LLM calls and improved Top-1 from 0.3947 to 0.5526, Top-5 from 0.6053 to 0.7632, Top-10 from 0.7105 to 0.8421, and MRR from 0.5080 to 0.6513. This aggregate is the cleanest current Defects4J held-out result for the main method.

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

For the second held-out run, `Closure-81..100`, the selector selected 5/19 cases and covered 2/7 baseline Top-5 failures. It improved two hard cases substantially: `Closure-91` from rank 16 to rank 1 and `Closure-100` from rank 50 to rank 1. `Closure-98` was outside the retrieval Top-50 candidate pool, so rerank could not recover it.

## Reporting Notes

- Report candidate Recall@20 and Recall@50 from retrieval baseline outputs, not merged selective-rerank outputs. The merged output is intentionally truncated to Top-10.
- Do not claim full Defects4J completion. The current evidence is a 120-bug main pilot plus fresh and held-out validations.
- Do not tune on `Closure-61..80` or `Closure-81..100`. Use their failures to define later frozen protocols.
- Mockito has no unused active bugs after 38 in this Defects4J checkout; report it as pilot plus fresh validation, not separate held-out.
- Keep controlled agentic inspection and verifier results as RQ5 / ablation material, not as the main method.

## Real-Project Case Studies

The real-project case studies evaluate whether the same retrieval, selector, and
rerank framework transfers beyond Defects4J.

| Dataset | Method | Selected Records | Top-1 | Top-3 | Top-5 | Top-10 | MRR |
|---|---|---:|---:|---:|---:|---:|---:|
| AboutWork committed-60 | BM25 production top50 | 0 / 60 | 0.5667 | 0.8333 | 0.9167 | 0.9333 | 0.7015 |
| AboutWork committed-60 | BM25 + selector_v3 + DeepSeek | 16 / 60 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 |
| Easy Finance clean63 | BM25 production top50 | 0 / 63 | 0.3968 | 0.7302 | 0.8730 | 0.8730 | 0.5684 |
| Easy Finance clean63 | BM25 + selector_v1 UI evidence v2 | 10 / 63 | 0.4921 | 0.8095 | 0.9841 | 1.0000 | 0.6729 |

On AboutWork committed-60, the selector selected 16 of 60 records for one-shot
DeepSeek reranking. The merged result improved Top-1 from 0.5667 to 0.7000 and
MRR from 0.7015 to 0.8117. The two remaining Top-10 misses were both selector
false negatives, indicating that selector recall remains the main real-project
limitation.

## RQ5 Agentic And Verifier Ablation

The RQ5 extension compares one-shot reranking with controlled agentic inspection
and a verifier pass. AboutWork committed-60 confirms the same pattern observed
on Easy Finance strict62 and the Defects4J diagnostic mini-benchmark: agentic
inspection is technically runnable, but it does not improve over one-shot
reranking, and the verifier adds cost without improving correct ranks.

| Dataset | Method | Selected Records | Model Calls | Top-1 | Top-3 | Top-5 | Top-10 | MRR | Tokens |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| AboutWork committed-60 | one-shot DeepSeek | 16 / 60 | 16 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 519530 |
| AboutWork committed-60 | agentic DeepSeek s2 | 16 / 60 | 40 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 440542 |
| AboutWork committed-60 | agentic s2 + verifier | 16 / 60 | 56 | 0.7000 | 0.9500 | 0.9667 | 0.9667 | 0.8117 | 589260 |

The one-shot, agentic, and agentic + verifier runs have identical per-bug
correct ranks on all 60 AboutWork records. The verifier adds 148718 tokens and
196.194 seconds without changing aggregate metrics or per-bug ranks. This
supports reporting agentic/verifier as a negative or neutral ablation rather
than as the main method.

## Source Artifacts

```text
docs/current_results_report.md
docs/experiment_design.md
docs/frozen_protocol_2026-06-01.md
docs/frozen_protocol_2026-06-02_closure_81_100.md
docs/closure_heldout_61_80_validation_report.md
docs/closure_heldout_81_100_validation_report.md
docs/closure_frozen_heldout_61_100_summary.md
docs/aboutwork_committed_60_rerank_results_2026-06-08.md
docs/aboutwork_committed_60_agentic_verifier_results_2026-06-08.md
outputs/closure_heldout_61_80_hybrid_focused_direct_passchain_typesystem_top50_eval.json
outputs/closure_heldout_61_80_merged_deepseek_closure_cost_control_v3_s12_ctx12000_top50_eval.json
outputs/closure_heldout_81_100_hybrid_focused_direct_passchain_typesystem_top50_eval.json
outputs/closure_heldout_81_100_merged_deepseek_closure_cost_control_v3_s12_ctx12000_top50_eval.json
```
