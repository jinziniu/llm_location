# Error Analysis Table

Date: 2026-06-03

This document summarizes the main remaining failure modes after the current Defects4J, AboutWork, Easy Finance, agentic, and verifier experiments. It also includes one recovered pilot case to show how evidence-rule evolution changed the method. It is intended to be inserted into the thesis discussion section.

## Compact Error Analysis

| Error Type | Representative Cases | Observed Cause | Impact | Next Action |
|---|---|---|---|---|
| Recovered pilot evidence/snippet miss | `Closure-4` | `NamedType.java` was present at candidate rank 49, but the original prompt did not expose `handleTypeCycle` or the cycle warning text, and repeated subtype stack frames dominated the evidence. | After snippet scoring, stack compression, and the type-cycle prompt rule, `NamedType.java` moved to DeepSeek rank 2. | Report as pilot method-evolution evidence; do not treat it as frozen held-out proof. |
| Selector false negative | `Closure-67`, `Closure-75`, `Closure-88`, `Closure-99` | The faulty file was in the retrieval candidate pool, but selector rules did not trigger an LLM rerank. | Correct file stayed outside Top-5/Top-10 in merged output. | Improve selector recall in a new frozen protocol; do not tune existing held-out results. |
| Candidate retrieval miss | `Closure-98` | The faulty file was not present in retrieval Top-50. | LLM rerank could not recover the bug regardless of prompt quality. | Improve focused retrieval and candidate recall before rerank. |
| Utility-file ambiguity | `Closure-61`, `Closure-75`, `Closure-94` | Failing tests pointed to compiler passes or generic infrastructure, while the actual change was in `NodeUtil.java`. | Selector treated direct-hint top candidates as safe and skipped rerank. | Add utility-file diagnostics only in a later frozen protocol. |
| Semantic pass-family mismatch | `Closure-67` | Direct hints named related optimization passes, but not the actual changed file `AnalyzePrototypeProperties.java`. | True file stayed deep in the candidate ranking. | Add non-oracle pass-family evidence and validate on a new held-out slice. |
| Code-output evidence gap | `Closure-65` | `CodePrinter.java` ranked above `CodeGenerator.java`, but the existing code-output selector pattern did not fire. | Correct file remained rank 8. | Broaden code-output evidence cautiously and validate out of sample. |
| Type-system / Mockito selector generalization | `Mockito-26`, `Mockito-28` in fresh 21..30 diagnostics | Tight Mockito selector missed primitive default-value and exact-type/ancestor injection patterns. | Earlier fresh slice had partial selector coverage. | Keep diagnostic patterns as hypotheses; avoid claiming frozen Mockito validation. |
| Verifier over-correction / no improvement | Easy Finance strict62 verifier; Defects4J RQ5 mini verifier | Verifier consumed agent top-10 candidates and fixed snippets, but did not receive cleaner evidence than the agentic output. In Defects4J mini, it also could not recover `Math-12` after agentic dropped the true file from top10. | Easy Finance MRR dropped from 0.6831 agent-only to 0.6804 with verifier. Defects4J mini stayed exactly flat against agentic at Top1 0.3000 / Top3 0.6000 / Top5 0.6000 / MRR 0.4768, with 112181 extra tokens. | Treat verifier as negative ablation; redesign only if verifier receives broader or cleaner evidence than the agent output. |
| Agentic cost without clear gain | Easy Finance strict62 agentic s2; Defects4J RQ5 mini agentic | Agentic inspection could search/read candidate files, but extra steps did not reliably improve evidence selection. In Defects4J mini, agentic regressed `Math-12`, `Closure-4`, `Closure-13`, and `Mockito-28` relative to one-shot. | Easy Finance was roughly flat with higher token cost. Defects4J mini fell from one-shot MRR 0.5644 to agentic MRR 0.4768 while using 441952 tokens versus 345937. | Keep as RQ5 extension; do not include in main method. |
| Case-study ground-truth noise | Easy Finance git-history-derived records | Fix commits may include touched files that are not root cause, or bug text may not match actual changed files. | Metrics can understate or overstate real localization quality. | Report as case study; validate with curated future bug logs. |

## Paper-Ready Paragraph

The remaining errors are not dominated by invalid LLM outputs. Instead, they concentrate around upstream retrieval, evidence construction, and selection. `Closure-4` is a recovered pilot example: the faulty file was present in the candidate pool, but rerank succeeded only after type-cycle evidence reached the prompt. In the Closure frozen held-out aggregate, selected cases were usually reranked successfully, but the selector covered only 6 of 15 baseline Top-5 failures. Several misses were selector false negatives where the correct file was present but not selected for reranking, while `Closure-98` was a candidate-retrieval miss outside Top-50. Utility files such as `NodeUtil.java` and semantically related compiler passes are particularly difficult because failure traces often point to the pass that exposes the bug rather than the shared helper or analysis file that must be changed. The RQ5 experiments show a different failure mode: adding agentic inspection or verifier rerank increases cost but does not necessarily improve evidence quality. On the Defects4J diagnostic mini-benchmark, one-shot rerank achieved Top1 0.4000 / Top3 0.7000 / MRR 0.5644, while agentic dropped to Top1 0.3000 / Top3 0.6000 / MRR 0.4768 and verifier made no correction. Therefore these components should remain ablations rather than the main method.

## Short Thesis Table

| Category | Count / Evidence | Main Lesson |
|---|---|---|
| Recovered pilot evidence miss | `Closure-4`: `NamedType.java` rank 49 -> rerank rank 2 | Evidence quality can recover candidate-present cases. |
| Closure frozen Top-5 failures | 15 baseline failures, 6 selected | Selector recall is the main bottleneck. |
| Closure retrieval misses | `Closure-98` | Rerank cannot fix absent candidates. |
| Selected-case rerank | selected held-out cases all reached Top-3 across both Closure held-out slices | Rerank works when selected and candidate is present. |
| RQ5 agentic/verifier | Easy Finance strict62 and Defects4J RQ5 mini | Agentic is feasible but not better than one-shot; verifier is currently a negative ablation. |
