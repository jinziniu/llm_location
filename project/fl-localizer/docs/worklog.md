# Worklog

This file records experiment progress, commands, outputs, and observations. Future experiment runs should append a new entry here.

## 2026-05-25

### Environment Setup

Installed and initialized Defects4J under:

```text
/Users/jin/llm_location/project/defects4j
```

Created environment helper:

```text
/Users/jin/llm_location/project/defects4j-env.sh
```

Verified:

```bash
source /Users/jin/llm_location/project/defects4j-env.sh
defects4j pids
defects4j info -p Lang -b 1
```

Notes:

- Defects4J 3.0.1 is initialized.
- Java 11, Subversion, wget, and local Perl dependencies are available.
- `tests.trigger.cause` is not an available Defects4J export property in this setup.
- Stack traces are read from the checkout-local `failing_tests` file.

### Lang-1 Smoke Test

Checked out and tested `Lang-1b`.

Result:

```text
Failing tests: 1
  - org.apache.commons.lang3.math.NumberUtilsTest::TestLang747
```

Exported metadata:

```text
classes.modified:
org.apache.commons.lang3.math.NumberUtils

tests.trigger:
org.apache.commons.lang3.math.NumberUtilsTest::TestLang747
```

### Dataset Builder MVP

Created `project/fl-localizer`.

Key files:

```text
scripts/build_defects4j_dataset.py
src/fl_localizer/schema.py
```

Generated:

```text
data/defects4j/lang_1.jsonl
```

Record includes:

- bug id
- report id and URL
- buggy/fixed commit ids
- triggering test
- stack trace from `failing_tests`
- source directory
- file-level ground truth

### BM25 Baseline MVP

Implemented:

```text
src/fl_localizer/indexer.py
src/fl_localizer/bm25.py
src/fl_localizer/evaluation.py
scripts/run_bm25.py
scripts/evaluate_predictions.py
```

Initial full-stack-trace query placed `Lang-1` correct file at rank 5 due to JDK/JUnit/Ant stack noise.

Updated query construction to keep exception information and application stack frames while filtering framework frames.

`Lang-1` result after filtering:

```text
Top-1: 1.0
Top-3: 1.0
Top-5: 1.0
MRR:   1.0
```

### Lang-5 BM25 Pilot

Generated:

```text
data/defects4j/lang_pilot_5.jsonl
outputs/lang_pilot_5_bm25.jsonl
```

Result:

```text
bugs: 5
Top-1: 0.60
Top-3: 1.00
Top-5: 1.00
MRR:   0.80
```

Per-bug ranks:

```text
Lang-1  rank 1
Lang-3  rank 1
Lang-4  rank 2
Lang-5  rank 1
Lang-6  rank 2
```

Observation:

- BM25 is a useful file-level baseline.
- Several failures are facade/helper ranking issues, e.g. `StringEscapeUtils` ranked above lower-level translate classes.

### Lang-10 BM25 Pilot

Generated:

```text
data/defects4j/lang_pilot_10.jsonl
outputs/lang_pilot_10_bm25.jsonl
outputs/lang_pilot_10_bm25_eval.json
```

Result:

```text
bugs: 10
Top-1: 0.60
Top-3: 1.00
Top-5: 1.00
MRR:   0.80
```

Added `--first-active` support to `build_defects4j_dataset.py` so active bug ids can be selected directly from `active-bugs.csv`.

### Lang-20 BM25 Pilot

Generated:

```text
data/defects4j/lang_pilot_20.jsonl
outputs/lang_pilot_20_bm25.jsonl
outputs/lang_pilot_20_bm25_eval.json
outputs/lang_pilot_20_bm25_top50.jsonl
```

BM25 top-10 result:

```text
bugs: 20
Top-1: 0.60
Top-3: 0.85
Top-5: 0.85
MRR:   0.7383333333333334
```

BM25 top-50 recall analysis:

```text
Top-1   12/20
Top-3   17/20
Top-5   17/20
Top-10  19/20
Top-20  19/20
Top-50  20/20
```

Low-rank cases:

```text
Lang-14 rank 10  gt=StringUtils.java
Lang-15 rank 6   gt=TypeUtils.java
Lang-17 rank 24  gt=CharSequenceTranslator.java
```

Observation:

- BM25 top-50 provides full recall for this pilot.
- LLM reranking should use top-50 candidates for hard cases such as `Lang-17`.

### LLM Reranker

Implemented:

```text
src/fl_localizer/prompts.py
src/fl_localizer/snippets.py
src/fl_localizer/llm_client.py
scripts/run_llm_rerank.py
```

Supported providers:

```text
dry-run
deepseek
codex
```

Environment files:

```text
.env
.env.example
docs/env.md
```

DeepSeek configuration is loaded from `.env`.

Prompt construction rules:

- include bug report id/text, triggering tests, stack trace, BM25 rank/score, source summaries/snippets
- do not include ground truth, fixing commit diff, fixed code, or `classes.modified`

### Codex Backend Smoke Test

Ran a single `Lang-1` Codex backend rerank smoke test.

Output:

```text
outputs/lang_pilot_20_rerank_codex_smoke.jsonl
```

Result:

```text
Lang-1 correct rank: 1
```

Note:

- Codex backend required escalated execution because the sandbox blocked app-server client initialization.

### DeepSeek Reranker Smoke Test

Ran DeepSeek on first 3 Lang bugs:

```text
outputs/lang_pilot_20_rerank_deepseek_smoke.jsonl
```

Result:

```text
bugs: 3
Top-1: 1.00
Top-3: 1.00
Top-5: 1.00
MRR:   1.00
```

Observation:

- DeepSeek returned valid JSON for the smoke run.
- `Lang-4` improved from BM25 rank 2 to DeepSeek rank 1.

### DeepSeek Lang-20 Full Rerank

Ran DeepSeek Flash over Lang-20 using BM25 top-50 candidates:

```text
outputs/lang_pilot_20_rerank_deepseek.jsonl
outputs/lang_pilot_20_rerank_deepseek_eval.json
```

Result:

```text
Method           Top-1  Top-3  Top-5  MRR
BM25             0.60   0.85   0.85   0.7383333333333334
DeepSeek rerank  0.95   1.00   1.00   0.975
```

Improved cases:

```text
Lang-4   BM25 rank 2  -> DeepSeek rank 1
Lang-6   BM25 rank 2  -> DeepSeek rank 1
Lang-7   BM25 rank 2  -> DeepSeek rank 1
Lang-8   BM25 rank 2  -> DeepSeek rank 1
Lang-14  BM25 rank 10 -> DeepSeek rank 1
Lang-15  BM25 rank 6  -> DeepSeek rank 1
Lang-17  BM25 rank 24 -> DeepSeek rank 2
Lang-19  BM25 rank 2  -> DeepSeek rank 1
```

Observation:

- DeepSeek Flash substantially improves file-level ranking on this pilot.
- `Lang-17` remains the only non-Top-1 case; it is useful as qualitative analysis because the model ranks facade/API file `StringEscapeUtils.java` above the true lower-level file `CharSequenceTranslator.java`.

### Reranker Output Validation

Added validation and completion logic:

```text
scripts/complete_rerank_output.py
```

Updated reranker behavior:

- filter model files that are not in the candidate set
- remove duplicate returned files
- append BM25 fallback files until top-k output is complete
- record metadata:
  - `candidate_count`
  - `requested_output_count`
  - `llm_returned_count`
  - `valid_llm_count`
  - `fallback_added_count`
  - `invalid_files`
  - `duplicate_files`

Completed DeepSeek output:

```text
outputs/lang_pilot_20_rerank_deepseek_completed.jsonl
outputs/lang_pilot_20_rerank_deepseek_completed_eval.json
```

Completed result:

```text
Top-1: 0.95
Top-3: 1.00
Top-5: 1.00
MRR:   0.975
```

Notable validation finding:

```text
Lang-17 invalid file returned by model:
src/main/java/org/apache/commons/lang3/text/translate/CodePointTranslator.java
```

This file was not in the BM25 top-50 candidate set, so it was filtered out before evaluation.

### Current Status

Completed:

- Benchmark MVP
- Lang-20 pilot dataset
- BM25 baseline
- DeepSeek reranker
- Reranker validation/fallback

Not completed:

- cross-project benchmark expansion
- token/cost/runtime logging
- repeated-run stability
- verifier agent
- company/Capstone case study

Recommended next step:

1. Add token/cost/runtime logging to LLM calls.
2. Expand benchmark to another Defects4J project, such as `Math-20` or `Chart-20`.

### LLM Runtime and Token Logging

Added per-call LLM metadata to reranker outputs:

```text
prompt_chars
response_chars
llm_duration_seconds
token_usage
```

For DeepSeek, `token_usage` is taken from the API response `usage` object and may include:

```text
prompt_tokens
completion_tokens
total_tokens
prompt_cache_hit_tokens
prompt_cache_miss_tokens
completion_tokens_details.reasoning_tokens
```

Updated files:

```text
src/fl_localizer/llm_client.py
scripts/run_llm_rerank.py
```

Added usage summary script:

```text
scripts/summarize_llm_usage.py
```

Ran one DeepSeek logging smoke test:

```text
outputs/lang_pilot_20_rerank_deepseek_logging_smoke.jsonl
outputs/lang_pilot_20_rerank_deepseek_logging_smoke_usage.json
```

Smoke result:

```text
bug: Lang-1
provider: deepseek
model: deepseek-v4-flash
correct rank: 1
duration: 9.797 seconds
prompt tokens: 8242
completion tokens: 839
total tokens: 9081
prompt cache hit tokens: 8192
prompt cache miss tokens: 50
```

Usage summary:

```text
records: 1
avg_duration_seconds: 9.797
avg_prompt_tokens: 8242.0
avg_completion_tokens: 839.0
avg_total_tokens: 9081.0
```

Observation:

- DeepSeek returns usable token accounting, including cache hit/miss information.
- Future full LLM runs should use the updated reranker so token and runtime metadata are recorded directly.

## 2026-05-25 Math-20 Expansion Experiment

Goal:

- Expand the pilot beyond `Lang-20` to a second Defects4J project.
- Use the same BM25 plus DeepSeek rerank pipeline so results are comparable.
- Record retrieval coverage, rerank accuracy, runtime, and token usage.

Dataset:

```text
data/defects4j/math_pilot_20.jsonl
```

This contains the first 20 active Math bugs:

```text
Math-1 ... Math-20
```

BM25 outputs:

```text
outputs/math_pilot_20_bm25.jsonl
outputs/math_pilot_20_bm25_eval.json
outputs/math_pilot_20_bm25_top50.jsonl
```

BM25 top-10 evaluation:

```text
bugs: 20
top_1_accuracy: 0.35
top_3_accuracy: 0.55
top_5_accuracy: 0.65
mrr: 0.4793650793650793
```

BM25 top-50 candidate coverage, counting a hit when any ground-truth file appears:

```text
Top1: 7 / 20
Top3: 11 / 20
Top5: 13 / 20
Top10: 16 / 20
Top20: 16 / 20
Top50: 18 / 20
```

Low-rank or missed ground-truth files:

```text
Math-7:  rank=7
Math-12: rank=None
Math-14: rank=24
Math-15: rank=None
Math-16: rank=31
Math-18: rank=6
Math-19: rank=9
```

DeepSeek rerank command:

```text
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/math_pilot_20.jsonl \
  --bm25 outputs/math_pilot_20_bm25_top50.jsonl \
  --out outputs/math_pilot_20_rerank_deepseek.jsonl \
  --provider deepseek \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 12
```

DeepSeek rerank outputs:

```text
outputs/math_pilot_20_rerank_deepseek.jsonl
outputs/math_pilot_20_rerank_deepseek_eval.json
outputs/math_pilot_20_rerank_deepseek_usage.json
```

DeepSeek rerank evaluation:

```text
bugs: 20
top_1_accuracy: 0.75
top_3_accuracy: 0.9
top_5_accuracy: 0.9
mrr: 0.825
```

Rank changes:

```text
Math-1:  bm25=1    rerank=1
Math-2:  bm25=1    rerank=1
Math-3:  bm25=4    rerank=1
Math-4:  bm25=1    rerank=1
Math-5:  bm25=1    rerank=1
Math-6:  bm25=3    rerank=1
Math-7:  bm25=7    rerank=2
Math-8:  bm25=2    rerank=1
Math-9:  bm25=1    rerank=1
Math-10: bm25=3    rerank=2
Math-11: bm25=1    rerank=1
Math-12: bm25=None rerank=None
Math-13: bm25=1    rerank=1
Math-14: bm25=None rerank=1
Math-15: bm25=None rerank=None
Math-16: bm25=None rerank=1
Math-17: bm25=2    rerank=1
Math-18: bm25=6    rerank=1
Math-19: bm25=9    rerank=2
Math-20: bm25=4    rerank=1
```

Usage summary:

```text
records: 20
total_duration_seconds: 304.237
avg_duration_seconds: 15.212
total_prompt_tokens: 398901
total_completion_tokens: 27839
total_tokens: 426740
avg_prompt_tokens: 19945.05
avg_completion_tokens: 1391.95
avg_total_tokens: 21337.0
```

Output validity:

```text
fallback_added_total: 0
invalid_total: 0
duplicate_total: 0
```

Observations:

- Math is a harder project for the current BM25 retriever than Lang.
- DeepSeek rerank still gives a large improvement when the true file is inside the top-50 candidate pool.
- `Math-14` and `Math-16` show useful deep-candidate recovery: they were outside BM25 top-10 but inside top-50, then reranked to rank 1.
- `Math-12` and `Math-15` are retrieval failures because the true file was absent from BM25 top-50.
- The current reranker is promising, but full-scale experiments need a retrieval improvement or hybrid candidate expansion to reduce top-50 misses.
- Math prompts are larger than Lang prompts. This run averaged about 21.3k tokens per bug, so token budgeting matters before scaling to all Defects4J bugs.

Recommended next step:

1. Add or test a stronger candidate retrieval stage for cases like `Math-12` and `Math-15`.
2. Run `Chart-20` or `Closure-20` with the same logging to see whether the Math behavior is project-specific.
3. Add a summary table script that compares BM25, DeepSeek rerank, and Codex backend across projects.

## 2026-05-26 Hybrid Retrieval Experiment on Math-20

Goal:

- Improve candidate recall before LLM reranking.
- Test whether the previous Math retrieval misses, especially `Math-12` and `Math-15`, can be recovered without using ground truth.
- Compare four Math-20 variants:
  - BM25 top-10 evaluation.
  - Hybrid retrieval top-50 evaluation.
  - BM25 top-50 + DeepSeek rerank.
  - Hybrid top-50 + DeepSeek rerank.

Implementation:

Added a hybrid retrieval script:

```text
scripts/run_hybrid_retrieval.py
```

The hybrid retriever keeps BM25 as the base score and adds non-ground-truth evidence:

```text
triggering test source context
stack project frames
test-class-to-source-class hints, e.g. FastMathTest -> FastMath
identifier overlap between test/runtime context and source files
```

The script intentionally writes a separate prediction file and does not replace the BM25 baseline.

Hybrid retrieval command:

```text
python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/math_pilot_20.jsonl \
  --out outputs/math_pilot_20_hybrid_top50.jsonl \
  --top-k 50
```

Hybrid retrieval outputs:

```text
outputs/math_pilot_20_hybrid_top50.jsonl
outputs/math_pilot_20_hybrid_top50_eval.json
```

Candidate coverage comparison:

```text
BM25 top-50:
Top1: 7 / 20
Top3: 11 / 20
Top5: 13 / 20
Top10: 16 / 20
Top20: 16 / 20
Top50: 18 / 20

Hybrid top-50:
Top1: 15 / 20
Top3: 17 / 20
Top5: 18 / 20
Top10: 18 / 20
Top20: 19 / 20
Top50: 20 / 20
```

Hybrid retrieval evaluation:

```text
bugs: 20
top_1_accuracy: 0.75
top_3_accuracy: 0.85
top_5_accuracy: 0.9
mrr: 0.8140050062578222
```

Important retrieval changes:

```text
Math-12: BM25 rank=None -> hybrid rank=47
Math-15: BM25 rank=None -> hybrid rank=1
Math-16: BM25 rank=31   -> hybrid rank=1
Math-18: BM25 rank=6    -> hybrid rank=1
Math-19: BM25 rank=9    -> hybrid rank=1
```

Remaining low-rank cases after hybrid retrieval:

```text
Math-12: rank=47
Math-14: rank=17
```

Hybrid + DeepSeek rerank command:

```text
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/math_pilot_20.jsonl \
  --bm25 outputs/math_pilot_20_hybrid_top50.jsonl \
  --out outputs/math_pilot_20_rerank_deepseek_hybrid.jsonl \
  --provider deepseek \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 12
```

Hybrid + DeepSeek outputs:

```text
outputs/math_pilot_20_rerank_deepseek_hybrid.jsonl
outputs/math_pilot_20_rerank_deepseek_hybrid_eval.json
outputs/math_pilot_20_rerank_deepseek_hybrid_usage.json
```

Overall Math-20 comparison:

```text
BM25:
top_1_accuracy: 0.35
top_3_accuracy: 0.55
top_5_accuracy: 0.65
mrr: 0.4793650793650793

Hybrid retrieval:
top_1_accuracy: 0.75
top_3_accuracy: 0.85
top_5_accuracy: 0.9
mrr: 0.8140050062578222

BM25 + DeepSeek rerank:
top_1_accuracy: 0.75
top_3_accuracy: 0.9
top_5_accuracy: 0.9
mrr: 0.825

Hybrid + DeepSeek rerank:
top_1_accuracy: 0.85
top_3_accuracy: 0.9
top_5_accuracy: 0.95
mrr: 0.885
```

Rank comparison:

```text
Math-1:  bm25=1    hybrid=1  ds_bm25=1    ds_hybrid=1
Math-2:  bm25=1    hybrid=1  ds_bm25=1    ds_hybrid=1
Math-3:  bm25=4    hybrid=1  ds_bm25=1    ds_hybrid=1
Math-4:  bm25=1    hybrid=2  ds_bm25=1    ds_hybrid=1
Math-5:  bm25=1    hybrid=1  ds_bm25=1    ds_hybrid=1
Math-6:  bm25=3    hybrid=1  ds_bm25=1    ds_hybrid=1
Math-7:  bm25=7    hybrid=1  ds_bm25=2    ds_hybrid=2
Math-8:  bm25=2    hybrid=1  ds_bm25=1    ds_hybrid=1
Math-9:  bm25=1    hybrid=1  ds_bm25=1    ds_hybrid=1
Math-10: bm25=3    hybrid=5  ds_bm25=2    ds_hybrid=1
Math-11: bm25=1    hybrid=1  ds_bm25=1    ds_hybrid=1
Math-12: bm25=None hybrid=47 ds_bm25=None ds_hybrid=None
Math-13: bm25=1    hybrid=1  ds_bm25=1    ds_hybrid=1
Math-14: bm25=None hybrid=17 ds_bm25=1    ds_hybrid=5
Math-15: bm25=None hybrid=1  ds_bm25=None ds_hybrid=1
Math-16: bm25=None hybrid=1  ds_bm25=1    ds_hybrid=1
Math-17: bm25=2    hybrid=2  ds_bm25=1    ds_hybrid=1
Math-18: bm25=6    hybrid=1  ds_bm25=1    ds_hybrid=1
Math-19: bm25=9    hybrid=1  ds_bm25=2    ds_hybrid=1
Math-20: bm25=4    hybrid=1  ds_bm25=1    ds_hybrid=1
```

Hybrid + DeepSeek usage:

```text
records: 20
total_duration_seconds: 250.051
avg_duration_seconds: 12.503
total_prompt_tokens: 419145
total_completion_tokens: 23311
total_tokens: 442456
avg_prompt_tokens: 20957.25
avg_completion_tokens: 1165.55
avg_total_tokens: 22122.8
```

Hybrid + DeepSeek output validity:

```text
records: 20
fallback_added_total: 98
invalid_total: 1
duplicate_total: 1
```

Observation:

- Hybrid retrieval successfully fixed the previous candidate recall problem at top-50 on Math-20.
- `Math-15` changed from a BM25 retrieval miss to a rank-1 hit because `FastMathTest` gives a strong source-class hint for `FastMath`.
- `Math-12` changed from retrieval miss to rerank miss: the true file `BitsStreamGenerator.java` entered the candidate pool at rank 47, but DeepSeek did not choose it for top-10.
- Hybrid retrieval alone is already competitive with BM25 + DeepSeek rerank on Math-20.
- Hybrid + DeepSeek gives the best Math-20 result so far: Top-1 0.85, Top-5 0.95, MRR 0.885.
- DeepSeek often returned fewer than 10 valid files in the hybrid run, causing more BM25 fallback fill than the previous BM25-candidate rerank run.
- The next rerank improvement should pass test-source evidence and hybrid retrieval reasons into the prompt, especially for deep candidates like `Math-12`.

Recommended next step:

1. Add evidence-aware rerank prompts that include triggering test source excerpts and hybrid candidate reasons.
2. Re-run a targeted Math-12/Math-14 check before spending a full 20-bug DeepSeek run.
3. After that, run `Chart-20` with BM25, hybrid retrieval, and hybrid + DeepSeek.

## 2026-05-26 Evidence-Aware Rerank Targeted Experiment

Goal:

- Improve reranking for the remaining hard Math cases without immediately spending a full 20-bug LLM run.
- Focus on `Math-12` and `Math-14`.
- Test whether adding triggering test source context and hybrid retrieval evidence helps DeepSeek reason about deep candidates.

Implementation changes:

Updated rerank prompt construction:

```text
src/fl_localizer/prompts.py
scripts/run_llm_rerank.py
```

Added reranker options:

```text
--bug-ids
--include-retrieval-evidence
--include-test-context
--max-test-context-chars
```

Prompt changes:

- The prompt now tells the model that lower-ranked candidates may still be correct.
- The model is asked to return exactly `top_output` files, reducing BM25 fallback fill.
- Optional triggering test source context can be included.
- Optional retrieval evidence can be included for each candidate:

```text
retrieval method
bm25_score
test_context_score
direct_boost
identifier_boost
retrieval reasons
```

Added a root-cause rule for stack traces:

```text
Distinguish the generic frame where an exception is thrown from the upstream file
that made the bad allocation, state transition, or validation decision.
```

Also updated hybrid retrieval:

```text
scripts/run_hybrid_retrieval.py
```

Added:

```text
--force-direct-hints
```

This keeps files that directly match stack/test class hints inside the top-k candidate pool. This was needed because `Math-14` had `Weight.java` at rank 59 in hybrid top-200, so it was absent from the previous top-50 rerank pool.

Dry-run prompt check:

```text
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/math_pilot_20.jsonl \
  --bm25 outputs/math_pilot_20_hybrid_top50.jsonl \
  --out outputs/math_pilot_20_rerank_evidence_dryrun_math12_14.jsonl \
  --provider dry-run \
  --bug-ids Math-12,Math-14 \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 14 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 12000 \
  --prompt-dir outputs/prompts_evidence
```

Dry-run observations:

```text
Math-12 prompt chars: 111313
Math-12 test source context chars: 4101
Math-14 prompt chars: 116353
Math-14 test source context chars: 12015
```

`Math-12` prompt includes the important `testDistributionClone` source context:

```text
distribution.reseedRandomGenerator(123)
distribution.sample()
final RealDistribution cloned = deepClone()
final double s1 = distribution.sample()
final double s2 = cloned.sample()
Assert.assertEquals(s1, s2, 0d)
```

First targeted DeepSeek command:

```text
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/math_pilot_20.jsonl \
  --bm25 outputs/math_pilot_20_hybrid_top50.jsonl \
  --out outputs/math_pilot_20_rerank_deepseek_hybrid_evidence_math12_14.jsonl \
  --provider deepseek \
  --bug-ids Math-12,Math-14 \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 14 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 12000 \
  --prompt-dir outputs/prompts_evidence
```

First targeted result:

```text
Math-12: previous ds_hybrid=None -> evidence-aware rank=5
Math-14: previous ds_hybrid=5    -> evidence-aware rank=8
```

Usage:

```text
records: 2
total_duration_seconds: 39.185
avg_duration_seconds: 19.593
total_prompt_tokens: 62003
total_completion_tokens: 4111
total_tokens: 66114
avg_total_tokens: 33057.0
```

Interpretation:

- Evidence-aware prompt helped `Math-12`: `BitsStreamGenerator.java` moved from not returned to rank 5.
- Evidence-aware prompt hurt `Math-14`: DeepSeek over-prioritized stack frames such as `MatrixUtils` and `BlockRealMatrix`, while the actual `Weight.java` file was missing from top-50 candidates.

Direct-hint candidate pool command:

```text
python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/math_pilot_20.jsonl \
  --out outputs/math_pilot_20_hybrid_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints
```

Direct-hint candidate pool observations:

```text
Math-14 direct_class_hints:
BlockRealMatrix
CurveFitter
MatrixUtils
PolynomialFitter
Weight

Math-14 Weight.java rank:
src/main/java/org/apache/commons/math3/optim/nonlinear/vector/Weight.java -> rank 49
src/main/java/org/apache/commons/math3/optimization/Weight.java -> rank 50
```

The aggregate hybrid retrieval metrics did not change because `Math-14` already had another ground-truth file in top-50:

```text
top_1_accuracy: 0.75
top_3_accuracy: 0.85
top_5_accuracy: 0.9
mrr: 0.8140050062578222
```

Second targeted DeepSeek command for `Math-14`:

```text
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/math_pilot_20.jsonl \
  --bm25 outputs/math_pilot_20_hybrid_direct_top50.jsonl \
  --out outputs/math_pilot_20_rerank_deepseek_hybrid_direct_evidence_math14.jsonl \
  --provider deepseek \
  --bug-ids Math-14 \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 14 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 12000 \
  --prompt-dir outputs/prompts_evidence_direct
```

Second targeted result:

```text
Math-14: direct-hint evidence-aware rank=1
```

DeepSeek ranked:

```text
rank 1: src/main/java/org/apache/commons/math3/optim/nonlinear/vector/Weight.java
```

Usage:

```text
records: 1
duration_seconds: 29.297
prompt_tokens: 31963
completion_tokens: 3236
total_tokens: 35199
```

Merged targeted output:

```text
outputs/math_pilot_20_rerank_deepseek_hybrid_direct_evidence_math12_14.jsonl
outputs/math_pilot_20_rerank_deepseek_hybrid_direct_evidence_math12_14_eval.json
outputs/math_pilot_20_rerank_deepseek_hybrid_direct_evidence_math12_14_usage.json
```

Merged targeted evaluation:

```text
bugs: 2
top_1_accuracy: 0.5
top_3_accuracy: 0.5
top_5_accuracy: 1.0
mrr: 0.6

Math-12: rank=5
Math-14: rank=1
```

Observations:

- The evidence-aware prompt fixed the output-format/fallback issue for targeted runs: both DeepSeek calls returned 10 valid files and had zero fallback fill.
- `Math-12` still needs better ranking because the true file is only rank 5, but this is a clear improvement over not being returned.
- `Math-14` shows that candidate pool composition matters as much as prompt quality. Once `Weight.java` was included, DeepSeek selected it as rank 1.
- The next full Math-20 run should use `hybrid_direct_top50` plus evidence-aware rerank, but it will cost roughly 30k to 35k tokens per bug unless prompt size is reduced.

Recommended next step:

1. Reduce evidence prompt size before full 20-bug rerun.
2. Add a prompt-budget ablation, for example 6 or 10 snippet lines and 4000 to 8000 test-context chars.
3. Then run full Math-20 with direct-hint hybrid retrieval and evidence-aware rerank.

## 2026-05-26 14:38 CEST - Math-20 compact evidence rerank

Goal:

- Return to the dataset experiments and validate whether the evidence-aware DeepSeek reranker can be made cheaper before running the full Math-20 set.
- Keep `Math-14` fixed with the direct-hint candidate pool while recovering `Math-12`.

Prompt-budget dry runs:

```text
input candidates: outputs/math_pilot_20_hybrid_direct_top50.jsonl
target bugs: Math-12,Math-14
top_candidates: 50
top_output: 10
```

Configuration A:

```text
max_snippet_lines: 8
max_test_context_chars: 6000
output: outputs/math_pilot_20_rerank_evidence_dryrun_math12_14_s8_ctx6000.jsonl
prompt_dir: outputs/prompts_evidence_s8_ctx6000

Math-12 prompt chars: 98769
Math-14 prompt chars: 94977
```

Configuration B:

```text
max_snippet_lines: 6
max_test_context_chars: 4000
output: outputs/math_pilot_20_rerank_evidence_dryrun_math12_14_s6_ctx4000.jsonl
prompt_dir: outputs/prompts_evidence_s6_ctx4000

Math-12 prompt chars: 92870
Math-14 prompt chars: 86913
```

Both compact prompts retained the key failing-test evidence:

```text
Math-12: testDistributionClone, reseedRandomGenerator, distribution.sample, deepClone
Math-14: new Weight(weights), createRealMatrix, Weight.java
```

Targeted DeepSeek ablation:

```text
s6_ctx4000:
  output: outputs/math_pilot_20_rerank_deepseek_hybrid_direct_evidence_math12_14_s6_ctx4000.jsonl
  eval: outputs/math_pilot_20_rerank_deepseek_hybrid_direct_evidence_math12_14_s6_ctx4000_eval.json
  result: Math-12=None, Math-14=1
  total_tokens: 53023
  avg_total_tokens: 26511.5
  duration_seconds: 39.757

s8_ctx6000:
  output: outputs/math_pilot_20_rerank_deepseek_hybrid_direct_evidence_math12_14_s8_ctx6000.jsonl
  eval: outputs/math_pilot_20_rerank_deepseek_hybrid_direct_evidence_math12_14_s8_ctx6000_eval.json
  result: Math-12=None, Math-14=1
  total_tokens: 61288
  avg_total_tokens: 30644.0
  duration_seconds: 83.789
```

Observation:

- Shrinking snippets and test context preserved `Math-14`, but `Math-12` regressed from rank 5 to not returned.
- Inspecting `BitsStreamGenerator.java` showed that the prompt included method names such as `clear`, `nextGaussian`, and `setSeed`, but the model still over-prioritized the distribution classes.

Prompt rule change:

```text
file: src/fl_localizer/prompts.py
added evidence rule:
For clone, serialization, reseed, repeated sample, or state consistency failures, consider lower-ranked helper classes that manage cached state, seeds, random generators, clear/reset methods, or value sequences.
```

Verification:

```text
python3 -m py_compile src/fl_localizer/prompts.py scripts/run_llm_rerank.py
```

Targeted state-rule rerun:

```text
output: outputs/math_pilot_20_rerank_deepseek_hybrid_direct_evidence_math12_s6_ctx4000_state_rule.jsonl
eval: outputs/math_pilot_20_rerank_deepseek_hybrid_direct_evidence_math12_s6_ctx4000_state_rule_eval.json

Math-12 rank: 5
top_1_accuracy: 0.0
top_3_accuracy: 0.0
top_5_accuracy: 1.0
mrr: 0.2

total_tokens: 27531
prompt_tokens: 25289
completion_tokens: 2242
duration_seconds: 22.797
valid_llm_count: 10
fallback_added_count: 0
invalid_files: 0
```

Full Math-20 command:

```text
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/math_pilot_20.jsonl \
  --bm25 outputs/math_pilot_20_hybrid_direct_top50.jsonl \
  --out outputs/math_pilot_20_rerank_deepseek_hybrid_direct_evidence_s6_ctx4000_state_rule.jsonl \
  --provider deepseek \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 6 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 4000 \
  --prompt-dir outputs/prompts_evidence_s6_ctx4000_state_rule_full
```

Full Math-20 outputs:

```text
predictions: outputs/math_pilot_20_rerank_deepseek_hybrid_direct_evidence_s6_ctx4000_state_rule.jsonl
eval: outputs/math_pilot_20_rerank_deepseek_hybrid_direct_evidence_s6_ctx4000_state_rule_eval.json
usage: outputs/math_pilot_20_rerank_deepseek_hybrid_direct_evidence_s6_ctx4000_state_rule_usage.json
prompt_dir: outputs/prompts_evidence_s6_ctx4000_state_rule_full
```

Full Math-20 result:

```text
bugs: 20
top_1_accuracy: 0.90
top_3_accuracy: 0.95
top_5_accuracy: 1.00
mrr: 0.935
```

Comparison:

```text
bm25:                top1=0.35 top3=0.55 top5=0.65 mrr=0.479
hybrid:              top1=0.75 top3=0.85 top5=0.90 mrr=0.814
hybrid_direct:       top1=0.75 top3=0.85 top5=0.90 mrr=0.814
ds_bm25:             top1=0.75 top3=0.90 top5=0.90 mrr=0.825
ds_hybrid:           top1=0.85 top3=0.90 top5=0.95 mrr=0.885
ds_compact_evidence: top1=0.90 top3=0.95 top5=1.00 mrr=0.935
```

Per-bug rank comparison:

```text
bug_id,bm25,hybrid_direct,ds_hybrid,ds_compact
Math-1,1,1,1,1
Math-2,1,1,1,1
Math-3,4,1,1,1
Math-4,1,2,1,1
Math-5,1,1,1,1
Math-6,3,1,1,1
Math-7,7,1,2,1
Math-8,2,1,1,1
Math-9,1,1,1,1
Math-10,3,5,1,2
Math-11,1,1,1,1
Math-12,None,47,None,5
Math-13,1,1,1,1
Math-14,None,17,5,1
Math-15,None,1,1,1
Math-16,None,1,1,1
Math-17,2,2,1,1
Math-18,6,1,1,1
Math-19,9,1,1,1
Math-20,4,1,1,1
```

Usage:

```text
records: 20
total_duration_seconds: 430.318
avg_duration_seconds: 21.516
total_prompt_tokens: 493116
total_completion_tokens: 43509
total_tokens: 536625
avg_prompt_tokens: 24655.8
avg_completion_tokens: 2175.45
avg_total_tokens: 26831.25
```

Output validity:

```text
records: 20
fallback_added_total: 2
invalid_total: 2
duplicate_total: 0

Math-11:
  valid_llm_count: 8
  fallback_added_count: 2
  invalid_files:
    - src/main/java/org/apache/commons/math3/linear/EigenDecomposition.java
    - src/main/java/org/apache/commons/math3/linear/Array2DRowRealMatrix.java
```

Main interpretation:

- This is the current best Math-20 result: every bug has the ground-truth file in Top-5.
- The retrieval plus rerank pipeline is now doing three useful things:
  - Hybrid/direct candidate generation recovers candidate files that BM25 misses.
  - Evidence-aware prompting lets DeepSeek select upstream files rather than only stack-frame files.
  - The state-consistency rule recovers `Math-12` into Top-5.
- Remaining ranking errors:
  - `Math-10`: `DerivativeStructure.java` is ranked 1 and true file `DSCompiler.java` is rank 2. The model follows the direct failing-test entry point before the lower-level implementation.
  - `Math-12`: true file `BitsStreamGenerator.java` is rank 5. The model still overweights distribution classes even after the state-consistency rule.
- Cost is still high: about 26.8k tokens per bug on average. This is acceptable for a pilot but should be reduced before scaling to larger datasets.

Recommended next step:

1. Run the same compact evidence configuration on another Defects4J project sample, preferably `Chart-20` or `Time-20`, to check cross-project generalization.
2. Add a small reranker calibration rule for "direct API wrapper vs lower-level implementation" and test it only on `Math-10` before a full rerun.
3. Add a cheaper candidate-pruning stage, for example hybrid top-30 plus forced direct hints, and compare against this top-50 result.

## 2026-05-26 14:54 CEST - Chart-20 cross-project expansion

Goal:

- Expand beyond `Math-20` and test whether the hybrid/direct retrieval plus compact evidence rerank design generalizes to another Defects4J project.
- Avoid a full 20-bug DeepSeek run at first; use baseline retrieval to identify hard cases, then run targeted rerank.

Dataset command:

```text
python3 scripts/build_defects4j_dataset.py \
  --project Chart \
  --first-active 20 \
  --out data/defects4j/chart_pilot_20.jsonl
```

Dataset validation:

```text
records: 20
first_bug: Chart-1
last_bug: Chart-20
missing_stack: 0
missing_ground_truth: 0
```

Retrieval commands:

```text
python3 scripts/run_bm25.py \
  --bugs data/defects4j/chart_pilot_20.jsonl \
  --out outputs/chart_pilot_20_bm25_top50.jsonl \
  --top-k 50

python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/chart_pilot_20.jsonl \
  --out outputs/chart_pilot_20_hybrid_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints
```

Evaluation outputs:

```text
outputs/chart_pilot_20_bm25_top50_eval.json
outputs/chart_pilot_20_hybrid_direct_top50_eval.json
```

Retrieval baseline results:

```text
bm25_top50:
  top_1_accuracy: 0.35
  top_3_accuracy: 0.60
  top_5_accuracy: 0.60
  mrr: 0.492
  recall@50: 19/20
  miss@50: Chart-2

hybrid_direct_top50:
  top_1_accuracy: 0.50
  top_3_accuracy: 0.70
  top_5_accuracy: 0.80
  mrr: 0.637
  recall@50: 20/20
```

Hybrid/direct top-k coverage:

```text
top1: 10/20
top3: 14/20
top5: 16/20
top10: 17/20
top20: 19/20
top50: 20/20
```

Hard cases selected for targeted rerank:

```text
Chart-3:  hybrid_direct rank=7
Chart-6:  hybrid_direct rank=16
Chart-15: hybrid_direct rank=28
Chart-20: hybrid_direct rank=17
```

Dry-run command:

```text
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/chart_pilot_20.jsonl \
  --bm25 outputs/chart_pilot_20_hybrid_direct_top50.jsonl \
  --out outputs/chart_pilot_20_rerank_evidence_dryrun_hard4_s6_ctx4000.jsonl \
  --provider dry-run \
  --bug-ids Chart-3,Chart-6,Chart-15,Chart-20 \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 6 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 4000 \
  --prompt-dir outputs/prompts_chart_evidence_hard4_s6_ctx4000
```

Dry-run prompt sizes:

```text
Chart-3:  prompt_chars=85988, test_context=4015
Chart-6:  prompt_chars=93534, test_context=4015
Chart-15: prompt_chars=90541, test_context=3977
Chart-20: prompt_chars=89849, test_context=4015
```

Targeted DeepSeek command:

```text
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/chart_pilot_20.jsonl \
  --bm25 outputs/chart_pilot_20_hybrid_direct_top50.jsonl \
  --out outputs/chart_pilot_20_rerank_deepseek_hybrid_direct_evidence_hard4_s6_ctx4000.jsonl \
  --provider deepseek \
  --bug-ids Chart-3,Chart-6,Chart-15,Chart-20 \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 6 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 4000 \
  --prompt-dir outputs/prompts_chart_evidence_hard4_s6_ctx4000_deepseek
```

Targeted DeepSeek outputs:

```text
predictions: outputs/chart_pilot_20_rerank_deepseek_hybrid_direct_evidence_hard4_s6_ctx4000.jsonl
eval: outputs/chart_pilot_20_rerank_deepseek_hybrid_direct_evidence_hard4_s6_ctx4000_eval.json
usage: outputs/chart_pilot_20_rerank_deepseek_hybrid_direct_evidence_hard4_s6_ctx4000_usage.json
```

Targeted DeepSeek result:

```text
bugs: 4
top_1_accuracy: 0.25
top_3_accuracy: 1.00
top_5_accuracy: 1.00
mrr: 0.583

Chart-3:  hybrid_direct=7  -> deepseek=2
Chart-6:  hybrid_direct=16 -> deepseek=1
Chart-15: hybrid_direct=28 -> deepseek=3
Chart-20: hybrid_direct=17 -> deepseek=2
```

Usage:

```text
records: 4
total_duration_seconds: 76.507
avg_duration_seconds: 19.127
total_prompt_tokens: 100382
total_completion_tokens: 7770
total_tokens: 108152
avg_prompt_tokens: 25095.5
avg_total_tokens: 27038.0
```

Output validity:

```text
records: 4
fallback_added_total: 0
invalid_total: 0
duplicate_total: 0
```

Merged evaluation:

```text
merged_predictions: outputs/chart_pilot_20_hybrid_direct_plus_deepseek_hard4.jsonl
merged_eval: outputs/chart_pilot_20_hybrid_direct_plus_deepseek_hard4_eval.json

top_1_accuracy: 0.55
top_3_accuracy: 0.90
top_5_accuracy: 1.00
mrr: 0.739
```

Comparison:

```text
chart_bm25:                  top1=0.35 top3=0.60 top5=0.60 mrr=0.492
chart_hybrid_direct:         top1=0.50 top3=0.70 top5=0.80 mrr=0.637
chart_hybrid_plus_ds_hard4:  top1=0.55 top3=0.90 top5=1.00 mrr=0.739
math_ds_compact:             top1=0.90 top3=0.95 top5=1.00 mrr=0.935
```

Main interpretation:

- `Chart-20` confirms the retrieval problem seen in `Math-20`: BM25 alone misses useful candidates, while hybrid/direct recovers all ground-truth files into top-50.
- Targeted DeepSeek rerank is effective on the four hard Chart cases: all four move into Top-3, and one moves to Top-1.
- Chart is still harder than Math for Top-1. Several failures involve misleading direct evidence, for example `Month.java` appearing as a strong candidate across unrelated Chart failures.
- This supports a staged strategy for scaling: run hybrid/direct retrieval first, then spend LLM calls on low-confidence or outside-Top-5 cases instead of every bug.

Recommended next step:

1. Add a confidence gate for selective LLM rerank: only call DeepSeek when hybrid/direct rank is outside Top-5 or when the top scores are close.
2. Run full Chart-20 DeepSeek only if we need an apples-to-apples full-rerank comparison with Math; estimated cost is roughly 20 * 27k tokens.
3. Reduce noisy direct hints such as unrelated `Month` matches before expanding to Time/Closure.

## 2026-05-26 15:08 CEST - Focused stack retrieval and selective rerank gate

Goal:

- Fix noisy direct hints in `Chart-20`, where unrelated failing-test sections caused `Month.java` to be over-ranked across many bugs.
- Add a reusable selective rerank gate so DeepSeek is called only for low-confidence hybrid results.

Code changes:

```text
scripts/run_hybrid_retrieval.py
  - added focused_stack_trace(record)
  - build_query now uses only the stack section matching test_failure / triggering_tests
  - collect_test_context, collect_direct_class_hints, and collect_identifier_terms now use focused stack trace

scripts/select_rerank_candidates.py
  - new script
  - selects candidates when top1_score/top2_score <= 1.02, top-1 has no direct hint, or direct_hint_count >= 7

scripts/merge_selective_rerank.py
  - new script
  - merges baseline predictions with rerank predictions only for selected bug ids
```

Verification:

```text
python3 -m py_compile \
  scripts/run_hybrid_retrieval.py \
  scripts/select_rerank_candidates.py \
  scripts/merge_selective_rerank.py
```

Focused retrieval commands:

```text
python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/chart_pilot_20.jsonl \
  --out outputs/chart_pilot_20_hybrid_focused_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints

python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/math_pilot_20.jsonl \
  --out outputs/math_pilot_20_hybrid_focused_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints
```

Focused retrieval evaluations:

```text
outputs/chart_pilot_20_hybrid_focused_direct_top50_eval.json
outputs/math_pilot_20_hybrid_focused_direct_top50_eval.json
```

Focused retrieval result:

```text
chart_old_hybrid:     top1=0.50 top3=0.70 top5=0.80 mrr=0.637
chart_focused_hybrid: top1=0.85 top3=0.95 top5=1.00 mrr=0.904

math_old_hybrid:      top1=0.75 top3=0.85 top5=0.90 mrr=0.814
math_focused_hybrid:  top1=0.75 top3=0.85 top5=0.90 mrr=0.814
```

Key observation:

- The Chart `Month` hint appeared in all 20 old hybrid records.
- After focusing stack trace sections, `Month` disappeared from the top direct-hint frequency list.
- Chart improved sharply without any new LLM call.
- Math was unchanged, so the focused-stack fix does not break the previous Math behavior.

Focused Chart rank changes:

```text
Chart-1:  2  -> 1
Chart-3:  7  -> 1
Chart-6:  16 -> 1
Chart-7:  5  -> 1
Chart-9:  2  -> 1
Chart-10: 2  -> 1
Chart-12: 2  -> 1
Chart-15: 28 -> 3
Chart-20: 17 -> 2
```

Selective gate commands:

```text
python3 scripts/select_rerank_candidates.py \
  --pred outputs/math_pilot_20_hybrid_focused_direct_top50.jsonl \
  --out outputs/math_pilot_20_hybrid_focused_selective_gate_t102_h7.json

python3 scripts/select_rerank_candidates.py \
  --pred outputs/chart_pilot_20_hybrid_focused_direct_top50.jsonl \
  --out outputs/chart_pilot_20_hybrid_focused_selective_gate_t102_h7.json
```

Selected bug ids:

```text
Math selected 6/20:
Math-4,Math-6,Math-12,Math-13,Math-14,Math-17

Chart selected 2/20:
Chart-4,Chart-20
```

Selective merge commands:

```text
python3 scripts/merge_selective_rerank.py \
  --baseline outputs/math_pilot_20_hybrid_focused_direct_top50.jsonl \
  --rerank outputs/math_pilot_20_rerank_deepseek_hybrid_direct_evidence_s6_ctx4000_state_rule.jsonl \
  --selection outputs/math_pilot_20_hybrid_focused_selective_gate_t102_h7.json \
  --out outputs/math_pilot_20_hybrid_focused_selective_deepseek_t102_h7.jsonl \
  --top-output 10

python3 scripts/merge_selective_rerank.py \
  --baseline outputs/chart_pilot_20_hybrid_focused_direct_top50.jsonl \
  --rerank outputs/chart_pilot_20_rerank_deepseek_hybrid_direct_evidence_hard4_s6_ctx4000.jsonl \
  --selection outputs/chart_pilot_20_hybrid_focused_selective_gate_t102.json \
  --out outputs/chart_pilot_20_hybrid_focused_selective_deepseek_t102.jsonl \
  --top-output 10
```

Selective evaluation outputs:

```text
outputs/math_pilot_20_hybrid_focused_selective_deepseek_t102_eval.json
outputs/math_pilot_20_hybrid_focused_selective_deepseek_t102_h7_eval.json
outputs/chart_pilot_20_hybrid_focused_selective_deepseek_t102_eval.json
outputs/math_t102_selective_usage_estimate.json
outputs/math_t102_h7_selective_usage_estimate.json
outputs/chart_t102_selective_usage_estimate.json
```

Selective result:

```text
math_focused_hybrid:  top1=0.75 top3=0.85 top5=0.90 mrr=0.814
math_selective_t102: top1=0.90 top3=0.90 top5=1.00 mrr=0.920
math_selective_h7:   top1=0.90 top3=0.90 top5=1.00 mrr=0.920
math_full_ds:        top1=0.90 top3=0.95 top5=1.00 mrr=0.935

chart_focused_hybrid:  top1=0.85 top3=0.95 top5=1.00 mrr=0.904
chart_selective_t102: top1=0.85 top3=0.95 top5=1.00 mrr=0.904
```

Selective usage estimate:

```text
Math selective:
  records: 6
  total_tokens: 188355
  avg_total_tokens: 31392.5
  total_duration_seconds: 147.944

Chart selective:
  records: 1
  total_tokens: 27149
  avg_total_tokens: 27149.0
  total_duration_seconds: 23.652
```

Threshold sweep for Math:

```text
threshold,selected,top1,top3,top5,mrr,tokens
1.01,3,0.80,0.85,0.95,0.845,108980
1.02,5,0.90,0.90,1.00,0.920,162319
1.03,6,0.90,0.90,1.00,0.920,188355
1.05,7,0.90,0.90,1.00,0.920,213682
1.40,15,0.90,0.95,1.00,0.935,412898
```

Main interpretation:

- The focused-stack fix is currently the highest-impact non-LLM improvement: it turns Chart focused hybrid into a strong baseline with Top-5 1.00.
- The selective gate keeps most of the Math DeepSeek benefit while using only 6/20 LLM calls.
- Compared with full Math DeepSeek compact evidence rerank, selective rerank preserves Top-1 and Top-5 but loses one Top-3 hit: `Math-10` remains rank 5 instead of rank 2.
- Full Math DeepSeek used 536625 total tokens; selective Math h7 uses an estimated 188355 tokens, about a 65% reduction.

Recommended next step:

1. Use focused hybrid/direct as the default candidate generator for future projects.
2. Use selective gate threshold 1.02 and direct-hint-count threshold 7 for pilot scaling.
3. Run `Time-20` focused hybrid next, then only call DeepSeek for selected low-confidence bugs.

## 2026-05-26 15:32 CEST - Time-20 focused retrieval and targeted DeepSeek

Goal:

- Expand to a fourth Defects4J project using the current default flow.
- Validate focused hybrid retrieval and targeted DeepSeek on `Time-20`.

Dataset command:

```text
python3 scripts/build_defects4j_dataset.py \
  --project Time \
  --first-active 20 \
  --out data/defects4j/time_pilot_20.jsonl
```

Dataset validation:

```text
records: 20
first_bug: Time-1
last_bug: Time-20
missing_stack: 0
missing_ground_truth: 0
```

Initial retrieval commands:

```text
python3 scripts/run_bm25.py \
  --bugs data/defects4j/time_pilot_20.jsonl \
  --out outputs/time_pilot_20_bm25_top50.jsonl \
  --top-k 50

python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/time_pilot_20.jsonl \
  --out outputs/time_pilot_20_hybrid_focused_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints
```

Initial Time result:

```text
time_bm25:        top1=0.15 top3=0.65 top5=0.75 mrr=0.402
time_focused_old: top1=0.65 top3=0.75 top5=0.80 mrr=0.735
```

Additional retrieval fix:

```text
scripts/run_hybrid_retrieval.py
  - added Test* prefix handling for test class names
  - examples:
    TestPartial_Constructors -> Partial
    TestMutableDateTime_Adds -> MutableDateTime
    TestDateTimeFormatterBuilder -> DateTimeFormatterBuilder
```

Updated focused retrieval command:

```text
python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/time_pilot_20.jsonl \
  --out outputs/time_pilot_20_hybrid_focused_testhint_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints
```

Updated focused retrieval result:

```text
time_bm25:             top1=0.15 top3=0.65 top5=0.75 mrr=0.402
time_focused_old:      top1=0.65 top3=0.75 top5=0.80 mrr=0.735
time_focused_testhint: top1=0.70 top3=0.80 top5=0.85 mrr=0.780
```

Focused test-hint top-k coverage:

```text
top1: 14/20 misses=Time-3,Time-10,Time-13,Time-14,Time-19,Time-20
top3: 16/20 misses=Time-3,Time-10,Time-13,Time-14
top5: 17/20 misses=Time-3,Time-13,Time-14
top10: 20/20
top20: 20/20
top50: 20/20
```

Targeted hard cases:

```text
Time-3:  focused_hybrid rank=8
Time-10: focused_hybrid rank=4
Time-13: focused_hybrid rank=9
Time-14: focused_hybrid rank=9
```

Dry-run prompt sizes:

```text
Time-3:  prompt_chars=98228,  test_context=4015
Time-10: prompt_chars=92731,  test_context=4015
Time-13: prompt_chars=84073,  test_context=3708
Time-14: prompt_chars=113649, test_context=4015
```

Targeted DeepSeek command:

```text
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/time_pilot_20.jsonl \
  --bm25 outputs/time_pilot_20_hybrid_focused_testhint_direct_top50.jsonl \
  --out outputs/time_pilot_20_rerank_deepseek_hybrid_focused_testhint_evidence_hard4_s6_ctx4000.jsonl \
  --provider deepseek \
  --bug-ids Time-3,Time-10,Time-13,Time-14 \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 6 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 4000 \
  --prompt-dir outputs/prompts_time_evidence_hard4_s6_ctx4000_deepseek
```

Targeted DeepSeek result:

```text
bugs: 4
top_1_accuracy: 1.00
top_3_accuracy: 1.00
top_5_accuracy: 1.00
mrr: 1.000

Time-3:  focused_hybrid=8 -> deepseek=1
Time-10: focused_hybrid=4 -> deepseek=1
Time-13: focused_hybrid=9 -> deepseek=1
Time-14: focused_hybrid=9 -> deepseek=1
```

Usage:

```text
records: 4
total_duration_seconds: 73.249
avg_duration_seconds: 18.312
total_prompt_tokens: 109699
total_completion_tokens: 7439
total_tokens: 117138
avg_total_tokens: 29284.5
```

Output validity:

```text
records: 4
fallback_added_total: 0
invalid_total: 0
duplicate_total: 0
```

Merged Time-20 output:

```text
merged_predictions: outputs/time_pilot_20_hybrid_focused_testhint_plus_deepseek_hard4.jsonl
merged_eval: outputs/time_pilot_20_hybrid_focused_testhint_plus_deepseek_hard4_eval.json
```

Merged Time-20 result:

```text
top_1_accuracy: 0.90
top_3_accuracy: 1.00
top_5_accuracy: 1.00
mrr: 0.950
```

Cross-project comparison after this run:

```text
math_selective_h7:   top1=0.90 top3=0.90 top5=1.00 mrr=0.920
chart_focused:       top1=0.85 top3=0.95 top5=1.00 mrr=0.904
time_plus_ds_hard4:  top1=0.90 top3=1.00 top5=1.00 mrr=0.950
```

Main interpretation:

- `Time-20` confirms the same pattern as Math and Chart: focused retrieval gets all ground truth files into top-10/top-50, and targeted DeepSeek can move hard cases to rank 1.
- Test-class naming matters. Joda-Time uses `TestXxx_*` names, so test-prefix hint extraction is necessary.
- The hard4 DeepSeek run was very cost-effective: only 4 calls produced a full Time-20 Top-5 of 1.00 and Top-3 of 1.00.

Recommended next step:

1. Update the current results report with Time-20.
2. Use the Time hard cases to improve automatic gate selection, because `Time-13` is still not selected by the current h7 gate.
3. Next project candidate: `Closure-20`, but run focused retrieval first before any LLM calls.

## 2026-05-26 16:25 CEST - Closure-20 retrieval and targeted DeepSeek

Goal:

- Expand the dataset experiments to `Closure-20`.
- Run BM25 and focused hybrid retrieval before spending LLM calls.
- Use targeted DeepSeek only on hard Closure cases.
- Diagnose whether Closure failures are retrieval misses, rerank misses, or noisy-evidence failures.

Dataset:

```text
dataset: data/defects4j/closure_pilot_20.jsonl
records: 20
missing stack traces: 0
missing ground truth: 0

first_bug: Closure-1
last_bug: Closure-20
```

Initial examples:

```text
Closure-1: test=CommandLineRunnerTest::testSimpleModeLeavesUnusedParams
           gt=src/com/google/javascript/jscomp/RemoveUnusedVars.java

Closure-2: test=TypeCheckTest::testBadInterfaceExtendsNonExistentInterfaces
           gt=src/com/google/javascript/jscomp/TypeCheck.java

Closure-3: test=FlowSensitiveInlineVariablesTest::testDoNotInlineCatchExpression1a
           gt=src/com/google/javascript/jscomp/FlowSensitiveInlineVariables.java
```

BM25 baseline:

```text
predictions: outputs/closure_pilot_20_bm25_top50.jsonl
eval: outputs/closure_pilot_20_bm25_top50_eval.json

top_1_accuracy: 0.15
top_3_accuracy: 0.30
top_5_accuracy: 0.40
mrr: 0.2808
recall@50: 17 / 20
miss@50: Closure-8, Closure-12, Closure-13
```

Focused hybrid/direct retrieval:

```text
predictions: outputs/closure_pilot_20_hybrid_focused_direct_top50.jsonl
eval: outputs/closure_pilot_20_hybrid_focused_direct_top50_eval.json

top_1_accuracy: 0.30
top_3_accuracy: 0.45
top_5_accuracy: 0.55
mrr: 0.4323

top1 coverage: 6 / 20
top3 coverage: 9 / 20
top5 coverage: 11 / 20
top10 coverage: 14 / 20
top20 coverage: 15 / 20
top50 coverage: 19 / 20
miss@50: Closure-13
```

Selective gate diagnostic:

```text
gate: top1/top2 <= 1.02 OR no direct hint OR direct_hint_count >= 7
selected: 8 / 20
file: outputs/closure_pilot_20_hybrid_focused_selective_gate_t102_h7.json

selected bugs:
Closure-1, Closure-3, Closure-5, Closure-7, Closure-8, Closure-12, Closure-13, Closure-18
```

Top-200 retrieval diagnostic:

```text
predictions: outputs/closure_pilot_20_hybrid_focused_direct_top200.jsonl
eval: outputs/closure_pilot_20_hybrid_focused_direct_top200_eval.json

recall@50: 19 / 20
recall@80: 19 / 20
recall@100: 19 / 20
recall@150: 19 / 20
recall@200: 19 / 20
miss@200: Closure-13
```

Closure-13 diagnostic:

```text
failing test: IntegrationTest::testIssue787
ground truth: src/com/google/javascript/jscomp/PeepholeOptimizationsPass.java

The focused hybrid retriever does not recover the true file even at top-200.
DefaultPassConfig.java, which references PeepholeOptimizationsPass, appears around rank 7,
but the actual pass implementation file is still absent.
```

This is a true retrieval miss for the current method, not an LLM rerank failure.

Prompt-size dry run:

```text
dryrun s6_ctx4000: outputs/closure_pilot_20_rerank_evidence_dryrun_hard8_s6_ctx4000.jsonl
avg_prompt_chars: 121621.8

dryrun s4_ctx3000: outputs/closure_pilot_20_rerank_evidence_dryrun_hard8_s4_ctx3000.jsonl
avg_prompt_chars: 115478.2
```

Targeted DeepSeek hard8:

```text
input_candidates: outputs/closure_pilot_20_hybrid_focused_direct_top50.jsonl
output: outputs/closure_pilot_20_rerank_deepseek_hybrid_focused_evidence_hard8_s4_ctx3000.jsonl
eval: outputs/closure_pilot_20_rerank_deepseek_hybrid_focused_evidence_hard8_s4_ctx3000_eval.json
usage: outputs/closure_pilot_20_rerank_deepseek_hybrid_focused_evidence_hard8_s4_ctx3000_usage.json

bug_ids:
Closure-1,Closure-4,Closure-6,Closure-7,Closure-8,Closure-10,Closure-12,Closure-17
```

Targeted DeepSeek result:

```text
bugs: 8
top_1_accuracy: 0.25
top_3_accuracy: 0.625
top_5_accuracy: 0.875
mrr: 0.452

Closure-1:  focused_hybrid=22 -> deepseek=1
Closure-4:  focused_hybrid=49 -> deepseek=None
Closure-6:  focused_hybrid=10 -> deepseek=5
Closure-7:  focused_hybrid=6  -> deepseek=3
Closure-8:  focused_hybrid=25 -> deepseek=1
Closure-10: focused_hybrid=13 -> deepseek=4
Closure-12: focused_hybrid=34 -> deepseek=3
Closure-17: focused_hybrid=6  -> deepseek=2
```

Usage:

```text
records: 8
total_duration_seconds: 136.645
avg_duration_seconds: 17.081
total_prompt_tokens: 249434
total_completion_tokens: 13222
total_tokens: 262656
avg_total_tokens: 32832.0
```

Output validity:

```text
fallback_added_total: 1
invalid_total: 1
duplicate_total: 0

Closure-12 invalid file:
src/com/google/javascript/jscomp/Node.java
```

Merged Closure-20 output:

```text
merged_predictions: outputs/closure_pilot_20_hybrid_focused_plus_deepseek_hard8.jsonl
merged_eval: outputs/closure_pilot_20_hybrid_focused_plus_deepseek_hard8_eval.json
```

Merged Closure-20 result:

```text
top_1_accuracy: 0.40
top_3_accuracy: 0.70
top_5_accuracy: 0.90
mrr: 0.5808
```

Remaining Top-5 failures:

```text
Closure-4: rerank miss. The true file is in the candidate pool, but DeepSeek over-ranked direct type-system stack frames.
Closure-13: retrieval miss. The true file is absent even from focused hybrid top-200.
```

Reference-hint expansion ablation:

```text
predictions: outputs/closure_pilot_20_hybrid_focused_direct_reference_top50.jsonl
eval: outputs/closure_pilot_20_hybrid_focused_direct_reference_top50_eval.json

top_1_accuracy: 0.35
top_3_accuracy: 0.50
top_5_accuracy: 0.55
mrr: 0.4308
```

Interpretation:

- Broadly boosting every referenced class is too noisy for Closure.
- It did not recover `Closure-13`.
- It degraded several previously good focused-hybrid ranks by promoting large numbers of indirectly referenced classes.
- This mode should stay off by default unless it is replaced by a more precise pass-chain or configuration-aware retrieval rule.

Cross-project comparison after this run:

```text
math_selective_h7:      top1=0.90 top3=0.90 top5=1.00 mrr=0.920
chart_focused:          top1=0.85 top3=0.95 top5=1.00 mrr=0.904
time_plus_ds_hard4:     top1=0.90 top3=1.00 top5=1.00 mrr=0.950
closure_plus_ds_hard8:  top1=0.40 top3=0.70 top5=0.90 mrr=0.581
```

Main interpretation:

- Closure is much harder than Lang, Math, Chart, and Time for the current retrieval design.
- Targeted DeepSeek still gives a clear gain on Closure: Top-5 rises from 0.55 to 0.90 after only 8 LLM calls.
- The remaining failures are now informative:
  - `Closure-4` needs better rerank evidence for recursive type-hierarchy bugs.
  - `Closure-13` needs stronger retrieval for compiler pass chains and config-to-pass references.
- The next Closure step should improve candidate generation before spending another full DeepSeek run.

Recommended next step:

1. Add a precise pass-chain retrieval feature for Closure cases where tests mention integration behavior but the defect is in a compiler pass implementation.
2. Re-test only `Closure-13` retrieval first.
3. Add a rerank evidence rule for recursive type-system stack traces and re-test only `Closure-4`.
4. Then expand to `Mockito-20` if Closure diagnostics do not require larger architectural changes.

## 2026-05-26 17:05 CEST - Closure-13 pass-chain retrieval add-on

Goal:

- Fix the remaining `Closure-13` retrieval miss without using ground truth in the prompt.
- Test whether compiler pass-chain evidence can recover files that are not directly named by the failing integration test or stack trace.
- Avoid the broad reference-hint failure from the previous experiment.

Implementation:

- Added optional `--force-pass-chain-hints` to `scripts/run_hybrid_retrieval.py`.
- The rule only reads high-ranked `*PassConfig` source files.
- It extracts constructor targets such as `new PeepholeOptimizationsPass(...)`.
- It treats the pass-chain result as candidate-pool inclusion, not primary ranking.
- Inserted pass-chain candidates at the bottom of the top-50 pool so existing top ranks are preserved.
- Added `pass_chain_boost` to rerank prompt retrieval evidence in `scripts/run_llm_rerank.py`.

Important distinction:

```text
Broad reference hints:
  Boost many referenced classes from many high-ranked files.
  Result: noisy and harmful on Closure.

Pass-chain hints:
  Only follow compiler pass config construction chains.
  Result: recovers Closure-13 without changing other top ranks.
```

Pass-chain retrieval command:

```text
python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/closure_pilot_20.jsonl \
  --out outputs/closure_pilot_20_hybrid_focused_passchain_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints \
  --force-pass-chain-hints
```

Pass-chain retrieval result:

```text
eval: outputs/closure_pilot_20_hybrid_focused_passchain_direct_top50_eval.json

top_1_accuracy: 0.30
top_3_accuracy: 0.45
top_5_accuracy: 0.55
mrr: 0.4336

Only changed rank:
Closure-13: None -> 39
```

Closure-13 recovered candidate:

```text
rank: 39
file: src/com/google/javascript/jscomp/PeepholeOptimizationsPass.java
reason: pass_chain_hint:DefaultPassConfig->PeepholeOptimizationsPass
pass_chain_boost: 1380.0
```

This means the candidate-pool recall problem is fixed for `Closure-13`, while the first-stage top-k metrics remain effectively the same as focused hybrid retrieval.

DeepSeek add-on for Closure-13:

```text
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/closure_pilot_20.jsonl \
  --bm25 outputs/closure_pilot_20_hybrid_focused_passchain_direct_top50.jsonl \
  --out outputs/closure_pilot_20_rerank_deepseek_hybrid_focused_passchain_evidence_c13_s4_ctx3000.jsonl \
  --provider deepseek \
  --bug-ids Closure-13 \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 4 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 3000 \
  --prompt-dir outputs/prompts_closure_passchain_c13_s4_ctx3000_deepseek
```

DeepSeek result:

```text
eval: outputs/closure_pilot_20_rerank_deepseek_hybrid_focused_passchain_evidence_c13_s4_ctx3000_eval.json

Closure-13:
retrieval rank: 39
deepseek rank: 3
top_3: true
top_5: true

rank 1: PeepholeSubstituteAlternateSyntax.java
rank 2: PeepholeFoldConstants.java
rank 3: PeepholeOptimizationsPass.java
```

Usage:

```text
prompt_chars: 102757
duration_seconds: 35.081
prompt_tokens: 27428
completion_tokens: 3209
total_tokens: 30637
invalid_files: 0
fallback_added: 0
```

Merged Closure-20 output:

```text
selection: outputs/closure_passchain_c13_selection.json
merged_predictions: outputs/closure_pilot_20_hybrid_focused_plus_deepseek_hard8_passchain_c13.jsonl
merged_eval: outputs/closure_pilot_20_hybrid_focused_plus_deepseek_hard8_passchain_c13_eval.json
```

Merged Closure-20 result:

```text
previous hard8:
top_1_accuracy: 0.40
top_3_accuracy: 0.70
top_5_accuracy: 0.90
mrr: 0.5808

hard8 + pass-chain C13:
top_1_accuracy: 0.40
top_3_accuracy: 0.75
top_5_accuracy: 0.95
mrr: 0.5975
```

Combined Closure targeted LLM usage:

```text
hard8 total_tokens: 262656
C13 total_tokens: 30637
combined total_tokens: 293293
targeted calls: 9
avg tokens per call: 32588.1
combined duration_seconds: 171.726
avg duration per call: 19.081
```

Interpretation:

- `Closure-13` is no longer a pure retrieval miss after pass-chain retrieval.
- The model still ranks two direct transformation classes above the true orchestration pass, so this is a Top-3 recovery rather than Top-1.
- The remaining full Closure Top-5 miss is now mainly `Closure-4`, a rerank miss around recursive type-system evidence.
- Pass-chain retrieval should remain gated. It is useful for Closure integration/pass-chain cases but should not replace focused hybrid ordering globally.

Recommended next step:

1. Diagnose `Closure-4` with a type-hierarchy / recursive stack prompt rule.
2. Keep pass-chain retrieval as a candidate-pool inclusion feature.
3. Do not re-run full Closure DeepSeek until `Closure-4` has a targeted fix.

## 2026-05-26 17:36 CEST - Closure-4 type-cycle rerank fix

Goal:

- Fix the remaining Closure Top-5 miss after the pass-chain `Closure-13` add-on.
- Diagnose why DeepSeek missed `Closure-4` even though the true file was in the candidate pool.
- Test a targeted prompt/snippet improvement before any full Closure rerun.

Initial state:

```text
bug: Closure-4
failing tests:
  TypeCheckTest::testImplementsExtendsLoop
  TypeCheckTest::testImplementsLoop
  TypeCheckTest::testConversionFromInterfaceToRecursiveConstructor

ground truth file: src/com/google/javascript/rhino/jstype/NamedType.java
focused hybrid rank: 49
previous DeepSeek rank: None
```

Failure pattern:

```text
expected: Parse error. Cycle detected in inheritance chain of type T/F/MyType
actual: can only implement interfaces
additional failure: StackOverflowError
repeated stack frame: PrototypeObjectType.isSubtype(...)
```

Previous DeepSeek behavior:

```text
rank 1: PrototypeObjectType.java
rank 2: FunctionType.java
rank 3: InstanceObjectType.java
rank 4: JSTypeRegistry.java
rank 5: ObjectType.java
...
NamedType.java: not returned
```

Diagnosis:

- `NamedType.java` was present in the top-50 candidate pool but had weak prompt evidence.
- Its `relevant_snippet` was only package/import lines:

```text
39:
40: package com.google.javascript.rhino.jstype;
41:
42: import com.google.common.base.Preconditions;
```

- The snippet extractor selected generic tokens such as `google`, `java`, `javascript`, and `jstype` before high-signal terms like `cycle`.
- The full stack trace also repeated `PrototypeObjectType.isSubtype` over 1000 times, which likely over-weighted downstream stack frames.

Code changes:

```text
src/fl_localizer/snippets.py
  - Added generic package/framework tokens to STOP_TOKENS.
  - Added HIGH_SIGNAL_TERMS such as cycle, inheritance, recursive, implements, extends, StackOverflowError.
  - Changed snippet selection from first-match ordering to scored high-signal line selection.

src/fl_localizer/prompts.py
  - Added a type-cycle evidence rule.
  - Added stack trace compaction for consecutive repeated stack frames.
```

New prompt evidence for `NamedType.java`:

```text
237:     if (value != null && value.isFunctionType() &&
238:         (value.isConstructor() || value.isInterface())) {
239:       FunctionType functionType = value.toMaybeFunctionType();
...
312:   private void handleTypeCycle(ErrorReporter t) {
313:     setReferencedType(
314:         registry.getNativeObjectType(JSTypeNative.UNKNOWN_TYPE));
315:     t.warning("Cycle detected in inheritance chain of type " + reference,
```

Prompt dry run:

```text
output: outputs/closure_pilot_20_rerank_evidence_dryrun_c4_typecycle_s8_ctx4000_compactstack.jsonl
prompt: outputs/prompts_closure_c4_typecycle_s8_ctx4000_compactstack/Closure-4_rerank_prompt.json

prompt_chars: 110064
previous uncompressed prompt_chars: 212629
stack compaction: repeated PrototypeObjectType.isSubtype frames omitted 1016 time(s)
```

Targeted DeepSeek command:

```text
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/closure_pilot_20.jsonl \
  --bm25 outputs/closure_pilot_20_hybrid_focused_direct_top50.jsonl \
  --out outputs/closure_pilot_20_rerank_deepseek_hybrid_focused_typecycle_c4_s8_ctx4000_compactstack.jsonl \
  --provider deepseek \
  --bug-ids Closure-4 \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 8 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 4000 \
  --prompt-dir outputs/prompts_closure_c4_typecycle_s8_ctx4000_compactstack_deepseek
```

Targeted DeepSeek result:

```text
eval: outputs/closure_pilot_20_rerank_deepseek_hybrid_focused_typecycle_c4_s8_ctx4000_compactstack_eval.json

Closure-4:
retrieval rank: 49
deepseek rank: 2
top_3: true
top_5: true

rank 1: FunctionType.java
rank 2: NamedType.java
rank 3: ObjectType.java
rank 4: PrototypeObjectType.java
rank 5: InstanceObjectType.java
```

Usage:

```text
duration_seconds: 21.779
prompt_tokens: 29650
completion_tokens: 2659
total_tokens: 32309
invalid_files: 0
fallback_added: 0
```

Merged Closure-20 output:

```text
selection: outputs/closure_typecycle_c4_selection.json
merged_predictions: outputs/closure_pilot_20_hybrid_focused_plus_deepseek_hard8_passchain_c13_typecycle_c4.jsonl
merged_eval: outputs/closure_pilot_20_hybrid_focused_plus_deepseek_hard8_passchain_c13_typecycle_c4_eval.json
```

Merged Closure-20 result:

```text
previous hard8 + pass-chain C13:
top_1_accuracy: 0.40
top_3_accuracy: 0.75
top_5_accuracy: 0.95
mrr: 0.5975

hard8 + pass-chain C13 + type-cycle C4:
top_1_accuracy: 0.40
top_3_accuracy: 0.80
top_5_accuracy: 1.00
mrr: 0.6225
```

Combined Closure targeted LLM usage:

```text
hard8 total_tokens: 262656
C13 total_tokens: 30637
C4 total_tokens: 32309
combined total_tokens: 325602
targeted calls: 10
avg tokens per call: 32560.2
combined duration_seconds: 193.505
avg duration per call: 19.351
```

Interpretation:

- The remaining Closure Top-5 miss is fixed.
- `Closure-4` shows that evidence quality mattered more than candidate recall: the true file was in the candidate pool but hidden behind a useless snippet and an overlong repeated stack trace.
- The snippet scoring change is likely reusable beyond Closure, but it should be validated on Math/Chart/Time before treating it as the default for all future reported numbers.
- Closure now has full Top-5 coverage after 10 targeted DeepSeek calls, not a full 20-bug DeepSeek run.

Recommended next step:

1. Re-run a small regression check on `Math-12`, `Math-14`, `Closure-4`, and `Closure-13` dry prompts to ensure snippet scoring does not remove useful evidence.
2. Add an automatic selector for type-cycle and pass-chain cases.
3. Expand to `Mockito-20` only after the selector is defined.

## 2026-05-26 18:05 CEST - Snippet regression dry-run after Closure fixes

Goal:

- Check that the new snippet scoring and compact-stack prompt changes do not remove key evidence from previously solved hard cases.
- Focus on no-cost dry-run prompts before spending more DeepSeek calls.

Regression targets:

```text
Math-12: state consistency / clone / reseed / sample
Math-14: matrix allocation through Weight
Closure-13: pass-chain candidate inclusion
Closure-4: type-cycle rerank evidence
```

Dry-run outputs:

```text
Math-12/Math-14 first regression:
outputs/math_pilot_20_rerank_evidence_dryrun_regression_m12_m14_s6_ctx4000_compactstack.jsonl

Closure-13 first regression:
outputs/closure_pilot_20_rerank_evidence_dryrun_regression_c13_s4_ctx3000_compactstack.jsonl

Math-12/Math-14 final regression:
outputs/math_pilot_20_rerank_evidence_dryrun_regression_m12_m14_s6_ctx4000_semanticfirst.jsonl

Math-12 clear-boost check:
outputs/math_pilot_20_rerank_evidence_dryrun_regression_m12_s6_ctx4000_stopwords.jsonl
```

Findings:

- `Math-14` remained stable. `Weight.java` still shows the constructor that creates a dense matrix:

```text
public Weight(double[] weight) {
    final int dim = weight.length;
    weightMatrix = MatrixUtils.createRealMatrix(dim, dim);
```

- `Closure-13` remained stable. `PeepholeOptimizationsPass.java` still has:

```text
pass_chain_hint:DefaultPassConfig->PeepholeOptimizationsPass
pass_chain_boost: 1380.0
```

- `Math-12` initially regressed at the snippet level. `BitsStreamGenerator.java` was still in the candidate pool, but the snippet selected generic exception/import lines instead of state-reset logic.

Fixes added:

```text
scripts/run_llm_rerank.py
  - Use triggering test source context as extra snippet query context.
  - Add semantic method terms for state-style failures: clear/reset/seed/random/next/sample/copy.
  - Add semantic method terms before the main query so they are not truncated by max_terms.

src/fl_localizer/snippets.py
  - Add clear/reset to HIGH_SIGNAL_TERMS.
  - Add abstract/int/double/float/long/boolean to STOP_TOKENS.
```

Final Math-12 snippet evidence:

```text
src/main/java/org/apache/commons/math3/random/BitsStreamGenerator.java

107:             random       = r * FastMath.cos(alpha);
108:             nextGaussian = r * FastMath.sin(alpha);
109:         } else {
...
165:      */
166:     public void clear() {
167:         nextGaussian = Double.NaN;
```

Interpretation:

- The Closure snippet fix is not obviously breaking the known Math hard cases.
- `Math-12` actually benefits from the follow-up semantic-method query because the prompt now exposes the cached Gaussian state and reset path.
- This is still dry-run validation only; no new Math DeepSeek call was made in this step.

Recommended next step:

1. Build an automatic rerank selector that detects pass-chain cases and type-cycle/state-reset cases.
2. Use that selector on `Mockito-20` rather than hand-picking cases.

## 2026-05-27

### AboutWork Company Dataset Baseline

Goal:

- Start the company-data experiment using real AboutWork git history.
- Convert `COMPANY_BUG_LOG.md` into the same JSONL shape used by the Defects4J pipeline.
- Run a first BM25 baseline without exposing fix commits, patch diffs, root causes, or ground-truth files to the query.

Implementation:

```text
scripts/build_aboutwork_dataset.py
src/fl_localizer/indexer.py
scripts/run_bm25.py
scripts/evaluate_predictions.py
```

Changes:

- Added an AboutWork log converter.
- The converter keeps only committed-history entries with concrete fix commits and ground-truth files.
- It creates detached git worktrees at each fixed commit's parent commit, so retrieval indexes the buggy version rather than the fixed version.
- Extended the source indexer from Java-only to Java/Python/TypeScript/TSX/JS/JSX.
- Added `--ks` to the evaluator so candidate recall can be measured with Top-50.

Generated dataset:

```text
data/aboutwork/aboutwork_committed_39.jsonl
```

Dataset summary:

```text
records: 39
backend records: 17
frontend records: 22
missing ground-truth files in buggy worktrees: 0
worktree root: /Users/jin/llm_location/project/workspaces/aboutwork
worktree disk usage: about 1.4G
```

Skipped entries:

```text
11 entries skipped because they were pending/local, template placeholders, or incomplete for committed-history evaluation.
```

Commands:

```bash
python3 -m py_compile scripts/build_aboutwork_dataset.py scripts/run_bm25.py scripts/evaluate_predictions.py src/fl_localizer/indexer.py

python3 scripts/build_aboutwork_dataset.py \
  --create-worktrees \
  --out data/aboutwork/aboutwork_committed_39.jsonl

python3 scripts/run_bm25.py \
  --bugs data/aboutwork/aboutwork_committed_39.jsonl \
  --out outputs/aboutwork_committed_39_bm25_top50.jsonl \
  --top-k 50

python3 scripts/evaluate_predictions.py \
  --bugs data/aboutwork/aboutwork_committed_39.jsonl \
  --pred outputs/aboutwork_committed_39_bm25_top50.jsonl \
  --per-bug \
  --ks 1,3,5,10,20,50 \
  > outputs/aboutwork_committed_39_bm25_top50_eval.json
```

BM25 result:

```text
bugs: 39
Top-1: 0.5897
Top-3: 0.8462
Top-5: 0.9487
Top-10: 0.9487
Top-20: 0.9744
Top-50: 1.0000
MRR: 0.7171
```

Hard cases:

```text
aboutwork-20260514-003 rank 41
ground truth: backend/assets/views.py
top-5: backend/analytics/tests.py, backend/outflow/views.py, backend/path/mixins.py, backend/workforce/permissions.py, backend/workforce/tests.py

aboutwork-20260312-001 rank 11
ground truth: src/components/cards/TodoCard.tsx
top-5: src/components/TopBar.tsx, src/components/PageHeader.tsx, src/components/GlobalSearch.tsx, src/components/Navbar.tsx, src/components/wrappers/UserWrapper.tsx
```

Interpretation:

- AboutWork committed-history data is usable as a company case-study benchmark.
- BM25 top-50 has full recall on this 39-bug set, so LLM rerank has a viable candidate pool.
- BM25 is already strong on Top-5, so the meaningful next experiment is targeted rerank on the two hard cases, plus possibly cases ranked 4-5 if optimizing Top-3.

Recommended next step:

1. Run DeepSeek rerank on `aboutwork-20260514-003` and `aboutwork-20260312-001`.
2. Optionally add selective rerank criteria for ranks greater than 5 or weak score gaps.
3. Compare AboutWork BM25 vs AboutWork targeted rerank in the final report.

### AboutWork Targeted DeepSeek Rerank

Goal:

- Rerank only the two AboutWork BM25 hard cases where the ground-truth file was outside Top-5.

Implementation update:

```text
scripts/run_llm_rerank.py
  - Switched source indexing from Java-only to generic source indexing, so AboutWork Python/TSX files can be used in prompts.
```

Dry-run prompt check:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/aboutwork/aboutwork_committed_39.jsonl \
  --bm25 outputs/aboutwork_committed_39_bm25_top50.jsonl \
  --out outputs/aboutwork_committed_39_rerank_dryrun_hard2.jsonl \
  --provider dry-run \
  --bug-ids aboutwork-20260514-003,aboutwork-20260312-001 \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 12 \
  --include-retrieval-evidence \
  --prompt-dir outputs/prompts_aboutwork_hard2_dryrun
```

DeepSeek command:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/aboutwork/aboutwork_committed_39.jsonl \
  --bm25 outputs/aboutwork_committed_39_bm25_top50.jsonl \
  --out outputs/aboutwork_committed_39_rerank_deepseek_hard2.jsonl \
  --provider deepseek \
  --bug-ids aboutwork-20260514-003,aboutwork-20260312-001 \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 12 \
  --include-retrieval-evidence \
  --prompt-dir outputs/prompts_aboutwork_hard2_deepseek
```

Hard-case rerank result:

```text
aboutwork-20260514-003: BM25 rank 41 -> DeepSeek rank 1
aboutwork-20260312-001: BM25 rank 11 -> DeepSeek rank 1
```

Usage:

```text
records: 2
total_duration_seconds: 65.602
avg_duration_seconds: 32.801
total_prompt_tokens: 51869
total_completion_tokens: 4869
total_tokens: 56738
avg_total_tokens: 28369
```

Merged output:

```text
outputs/aboutwork_committed_39_bm25_plus_deepseek_hard2.jsonl
outputs/aboutwork_committed_39_bm25_plus_deepseek_hard2_eval.json
```

Merged AboutWork result:

```text
Method: BM25 top-50 baseline
Top-1: 0.5897
Top-3: 0.8462
Top-5: 0.9487
Top-10: 0.9487
Top-20: 0.9744
Top-50: 1.0000
MRR: 0.7171

Method: BM25 + DeepSeek hard2
Top-1: 0.6410
Top-3: 0.8974
Top-5: 1.0000
Top-10: 1.0000
MRR: 0.7654
```

Interpretation:

- The AboutWork company benchmark now has a complete first pass: committed-history dataset, BM25 baseline, and targeted LLM rerank.
- Because BM25 Recall@50 is already 1.0, the next research question is not recall but selective rerank value versus token cost.
- The hard2 targeted rerank lifted both failures to rank 1 and made Top-5 reach 1.0 on the 39-bug committed subset.

### AboutWork Low-Ratio Selective Rerank

Goal:

- Test a non-oracle selective rerank rule on AboutWork BM25 output.
- Select bugs where BM25 top-1 and top-2 scores are close, using:

```text
top1_score / top2_score <= 1.02
```

Selection:

```text
outputs/aboutwork_lowratio_t102_selection.json
selected: 9 / 39
```

Selected bug ids:

```text
aboutwork-20260429-001
aboutwork-20260130-001
aboutwork-20260212-001
aboutwork-20260305-001
aboutwork-20260417-001
aboutwork-20260327-003
aboutwork-20260312-001
aboutwork-20260505-002
aboutwork-20260514-003
```

Notes:

- `aboutwork-20260312-001` and `aboutwork-20260514-003` were already run in the hard2 experiment.
- The remaining 7 were run as `outputs/aboutwork_committed_39_rerank_deepseek_lowratio_t102_add7.jsonl`.

Command for add7:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/aboutwork/aboutwork_committed_39.jsonl \
  --bm25 outputs/aboutwork_committed_39_bm25_top50.jsonl \
  --out outputs/aboutwork_committed_39_rerank_deepseek_lowratio_t102_add7.jsonl \
  --provider deepseek \
  --bug-ids aboutwork-20260429-001,aboutwork-20260130-001,aboutwork-20260212-001,aboutwork-20260305-001,aboutwork-20260417-001,aboutwork-20260327-003,aboutwork-20260505-002 \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 12 \
  --include-retrieval-evidence \
  --prompt-dir outputs/prompts_aboutwork_lowratio_t102_deepseek
```

Add7 rerank result:

```text
bugs: 7
Top-1: 1.0000
Top-3: 1.0000
Top-5: 1.0000
MRR: 1.0000
```

Low-ratio t102 merged result:

```text
outputs/aboutwork_committed_39_bm25_plus_deepseek_lowratio_t102.jsonl
outputs/aboutwork_committed_39_bm25_plus_deepseek_lowratio_t102_eval.json
```

```text
Method: BM25 + DeepSeek lowratio_t102
selected: 9 / 39
Top-1: 0.7436
Top-3: 0.9487
Top-5: 1.0000
Top-10: 1.0000
MRR: 0.8406
```

Usage:

```text
records: 9
total_duration_seconds: 222.551
avg_duration_seconds: 24.728
total_prompt_tokens: 233219
total_completion_tokens: 17116
total_tokens: 250335
avg_total_tokens: 27815
```

Interpretation:

- The low-ratio selector is useful on AboutWork: with 9/39 LLM calls, Top-1 increases from 0.5897 to 0.7436 and MRR from 0.7171 to 0.8406.
- No selected low-ratio case was harmed by rerank in this run.
- Two Top-3 misses remained after low-ratio rerank: `aboutwork-20260520-001` and `aboutwork-20251217-001`.

### AboutWork Remaining Top-3 Miss Upper Bound

Goal:

- Test whether the remaining Top-3 misses can be fixed by LLM rerank when selected.
- This is an oracle upper-bound experiment because selection used evaluation ranks.

Selection:

```text
outputs/aboutwork_remaining_top3_miss_selection.json
selected: 2 / 39
aboutwork-20260520-001
aboutwork-20251217-001
```

Command:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/aboutwork/aboutwork_committed_39.jsonl \
  --bm25 outputs/aboutwork_committed_39_bm25_top50.jsonl \
  --out outputs/aboutwork_committed_39_rerank_deepseek_remaining_top3_miss.jsonl \
  --provider deepseek \
  --bug-ids aboutwork-20260520-001,aboutwork-20251217-001 \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 12 \
  --include-retrieval-evidence \
  --prompt-dir outputs/prompts_aboutwork_remaining_top3_miss_deepseek
```

Result:

```text
aboutwork-20260520-001: BM25 rank 5 -> DeepSeek rank 2
aboutwork-20251217-001: BM25 rank 4 -> DeepSeek rank 1
```

Usage:

```text
records: 2
total_duration_seconds: 83.465
avg_duration_seconds: 41.733
total_prompt_tokens: 47106
total_completion_tokens: 6096
total_tokens: 53202
avg_total_tokens: 26601
```

Merged upper-bound result:

```text
outputs/aboutwork_committed_39_bm25_plus_deepseek_lowratio_t102_plus_remaining_top3.jsonl
outputs/aboutwork_committed_39_bm25_plus_deepseek_lowratio_t102_plus_remaining_top3_eval.json
```

```text
Method: BM25 + lowratio_t102 + oracle remaining Top-3 miss
selected: 11 / 39
Top-1: 0.7692
Top-3: 1.0000
Top-5: 1.0000
Top-10: 1.0000
MRR: 0.8675
total_tokens: 303537
```

Comparison:

```text
BM25:
Top-1 0.5897, Top-3 0.8462, Top-5 0.9487, MRR 0.7171

BM25 + hard2:
Top-1 0.6410, Top-3 0.8974, Top-5 1.0000, MRR 0.7654

BM25 + lowratio_t102:
Top-1 0.7436, Top-3 0.9487, Top-5 1.0000, MRR 0.8406

BM25 + lowratio_t102 + oracle remaining Top-3:
Top-1 0.7692, Top-3 1.0000, Top-5 1.0000, MRR 0.8675
```

Interpretation:

- For a deployable AboutWork selector, `lowratio_t102` is the cleaner result because it does not use ground truth.
- The oracle add-on shows remaining Top-3 misses are mostly rerankable if selected, but the selector still needs improvement to identify cases like `aboutwork-20260520-001` whose BM25 score ratio is not low.

### AboutWork Production-Only Index And Selector V3

Goal:

- Remove test-file noise from the AboutWork source index.
- Compare non-oracle selective rerank gates on the 39 committed AboutWork bug logs.
- Find a practical selector that does not rely on ground-truth rank.

Indexer change:

```text
src/fl_localizer/indexer.py
```

The generic source index now skips common test files in production app trees:

```text
tests.py
conftest.py
```

Production-only BM25 output:

```text
outputs/aboutwork_committed_39_bm25_prod_top50.jsonl
outputs/aboutwork_committed_39_bm25_prod_top50_eval.json
```

Result:

```text
bugs: 39
Top-1:  0.5897
Top-3:  0.8462
Top-5:  0.9487
Top-10: 0.9487
Top-20: 0.9744
Top-50: 1.0000
MRR:    0.7171
```

Observation:

- The metric is nearly unchanged versus the first AboutWork BM25 run.
- The top-10 candidate lists no longer include `backend/hr_chat/tests.py`, `backend/analytics/tests.py`, or `backend/workforce/tests.py`.
- This makes the candidate pool more realistic for production fault localization.

Production low-ratio variants:

```text
outputs/aboutwork_prod_lowratio_t102_selection.json
outputs/aboutwork_committed_39_bm25_prod_plus_deepseek_lowratio_t102_eval.json

outputs/aboutwork_prod_lowratio_t103_selection.json
outputs/aboutwork_committed_39_bm25_prod_plus_deepseek_lowratio_t103_eval.json
```

Results:

```text
BM25 + DeepSeek lowratio_t102
selected: 8 / 39
Top-1:  0.7179
Top-3:  0.9231
Top-5:  0.9744
Top-10: 0.9744
MRR:    0.8150

BM25 + DeepSeek lowratio_t103
selected: 11 / 39
Top-1:  0.7436
Top-3:  0.9231
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.8342
```

Interpretation:

- Raising the low-ratio threshold from `1.02` to `1.03` recovers `aboutwork-20260514-003`, but also selects weaker cases.
- One selected add-on, `aboutwork-20260226-001`, was harmed by rerank: BM25 rank 2 became DeepSeek rank 4.
- A pure score-ratio gate is useful but not enough for the remaining AboutWork hard cases.

Added selector script:

```text
scripts/select_aboutwork_rerank_candidates.py
```

Selector V2 rules:

```text
score_ratio <= 1.02
OR top1 path contains /management/commands/
OR domain mismatch:
  asset/assets text but top1 path is not assets
  employee context / employee_id / organization_id / uuid text but top1 path is not workforce
```

V2 selection:

```text
outputs/aboutwork_prod_selector_v2.json
selected: 12 / 39
```

V2 add-on run:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/aboutwork/aboutwork_committed_39.jsonl \
  --bm25 outputs/aboutwork_committed_39_bm25_prod_top50.jsonl \
  --out outputs/aboutwork_committed_39_rerank_deepseek_selector_v2_add1.jsonl \
  --provider deepseek \
  --top-candidates 50 \
  --top-output 10 \
  --include-retrieval-evidence \
  --bug-ids aboutwork-20260505-001
```

V2 result:

```text
outputs/aboutwork_committed_39_bm25_prod_plus_deepseek_selector_v2.jsonl
outputs/aboutwork_committed_39_bm25_prod_plus_deepseek_selector_v2_eval.json

selected: 12 / 39
Top-1:  0.7692
Top-3:  0.9744
Top-5:  0.9744
Top-10: 1.0000
MRR:    0.8632
```

V2 failure:

```text
aboutwork-20260505-001
ground truth: backend/chatbot_v2/action_drafts.py
BM25 production rank: 3
DeepSeek rank after V2 selection: 6
```

Interpretation:

- A broad `top1_management_command` rule is too aggressive.
- It correctly selects `aboutwork-20260520-001`, but also selects `aboutwork-20260505-001`, which was already Top-3 and was harmed by rerank.

Selector V3 rules:

```text
score_ratio <= 1.02
OR domain mismatch:
  asset/assets text but top1 path is not assets
  employee context / employee_id / organization_id / uuid text but top1 path is not workforce
OR top1 management command with attendance follow-up action-context text
```

V3 selection:

```text
outputs/aboutwork_prod_selector_v3.json
selected: 11 / 39
```

V3 merged result:

```text
outputs/aboutwork_committed_39_bm25_prod_plus_deepseek_selector_v3.jsonl
outputs/aboutwork_committed_39_bm25_prod_plus_deepseek_selector_v3_eval.json
```

Metrics:

```text
selected: 11 / 39
Top-1:  0.7692
Top-3:  1.0000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.8675
```

Token usage for the 11 selected rerank records:

```text
total_tokens: 303537
avg_total_tokens: 27594
```

Comparison:

```text
BM25 production:
Top-1 0.5897, Top-3 0.8462, Top-5 0.9487, Top-10 0.9487, MRR 0.7171

lowratio_t102:
Top-1 0.7179, Top-3 0.9231, Top-5 0.9744, Top-10 0.9744, MRR 0.8150

lowratio_t103:
Top-1 0.7436, Top-3 0.9231, Top-5 1.0000, Top-10 1.0000, MRR 0.8342

selector_v2:
Top-1 0.7692, Top-3 0.9744, Top-5 0.9744, Top-10 1.0000, MRR 0.8632

selector_v3:
Top-1 0.7692, Top-3 1.0000, Top-5 1.0000, Top-10 1.0000, MRR 0.8675
```

Conclusion:

- The best current AboutWork setting is production BM25 plus `selector_v3`.
- This is no longer an oracle selector: it uses score ambiguity, domain mismatch terms, and a narrow attendance follow-up management-command pattern.
- Because V3 was tuned after seeing the current 39 bug logs, it should be treated as a fitted case-study selector until validated on fresh AboutWork bug logs.

### Easy Finance Git-History Dataset Processing

Goal:

- Convert Easy Finance git-history bug-fix candidates into experiment-ready JSONL.
- Build at least 50 valid records from backend/frontend source commits.
- Create buggy-commit worktrees and run a BM25 baseline smoke experiment.

Candidate source:

```text
docs/easy_finance_candidate_bugfixes.md
```

Source repos:

```text
/Users/jin/capi_project/easy_finance/easy_finance_backend
/Users/jin/capi_project/easy_finance/easy_finance_frontend
```

Added builder:

```text
scripts/build_easy_finance_dataset.py
```

Builder behavior:

- Parses priority and expanded usable candidates from the markdown table.
- Resolves each fix commit and uses its first parent as the buggy commit.
- Filters ground-truth files to files that already exist in the buggy commit.
- Creates detached buggy-commit worktrees under:

```text
/Users/jin/llm_location/project/workspaces/easy_finance
```

- Writes JSONL compatible with `run_bm25.py`, `evaluate_predictions.py`, and `run_llm_rerank.py`.
- Records a build report with counts and skipped candidates.

Dry validation:

```text
data/easy_finance/easy_finance_committed_dry.jsonl
data/easy_finance/easy_finance_committed_dry.report.json
```

Result:

```text
records: 64
backend: 30
frontend: 34
priority: 18
expanded: 46
skipped: 0
```

First 50-record dataset:

```bash
python3 scripts/build_easy_finance_dataset.py \
  --out data/easy_finance/easy_finance_committed_50.jsonl \
  --report data/easy_finance/easy_finance_committed_50.report.json \
  --limit 50 \
  --create-worktrees
```

Validation:

```text
records: 50
backend: 30
frontend: 20
priority: 18
expanded: 32
source_missing: 0
ground_truth_missing: 0
skipped: 0
```

BM25 top-50 output:

```text
outputs/easy_finance_committed_50_bm25_top50.jsonl
outputs/easy_finance_committed_50_bm25_top50_eval.json
```

50-record BM25 result:

```text
bugs: 50
Top-1:  0.4400
Top-3:  0.6600
Top-5:  0.8200
Top-10: 0.9000
Top-20: 0.9600
Top-50: 1.0000
MRR:    0.5851
```

Complete 64-record dataset:

```bash
python3 scripts/build_easy_finance_dataset.py \
  --out data/easy_finance/easy_finance_committed_64.jsonl \
  --report data/easy_finance/easy_finance_committed_64.report.json \
  --create-worktrees
```

Validation:

```text
records: 64
backend: 30
frontend: 34
priority: 18
expanded: 46
source_missing: 0
ground_truth_missing: 0
skipped: 0
```

BM25 top-50 output:

```text
outputs/easy_finance_committed_64_bm25_top50.jsonl
outputs/easy_finance_committed_64_bm25_top50_eval.json
```

64-record BM25 result:

```text
bugs: 64
Top-1:  0.3906
Top-3:  0.6094
Top-5:  0.7969
Top-10: 0.8594
Top-20: 0.9531
Top-50: 1.0000
MRR:    0.5436
```

Top-10 misses in the 64-record BM25 run:

```text
easyfinance-backend-20251029-001 rank=45
easyfinance-frontend-20250520-001 rank=18
easyfinance-backend-20251106-001 rank=13
easyfinance-backend-20250501-001 rank=16
easyfinance-frontend-20260220-001 rank=40
easyfinance-frontend-20250930-001 rank=17
easyfinance-frontend-20250705-001 rank=33
easyfinance-frontend-20250627-002 rank=13
easyfinance-frontend-20250522-001 rank=12
```

Interpretation:

- Easy Finance now has enough processed data for a company-project experiment.
- The 64-record pool is preferable to the exact 50-record subset because it preserves frontend coverage.
- BM25 Top-50 recall is 1.0, so the current candidate pool is suitable for selective DeepSeek/Codex rerank experiments.
- Because bug reports are inferred from fix commit metadata rather than hand-written issue logs, this dataset has higher construct-validity risk than AboutWork and should be labeled as git-history-derived.

### Easy Finance DeepSeek Hard-Case Rerank

Goal:

- Start the Easy Finance rerank experiment.
- Test whether DeepSeek can recover BM25 hard cases when the correct file is already in the Top-50 candidate pool.

Initial oracle selection on 64 records:

```text
outputs/easy_finance_hard13_rank_gt5_selection.json
criterion: BM25 correct_rank > 5
selected: 13 / 64
```

During the first full hard13 run, a network/DNS failure interrupted the batch before final JSONL output was written. To avoid losing completed calls, the rerun used one output file per bug under:

```text
outputs/easy_finance_hard13_parts/
```

This run also reduced `max_snippet_lines` from 12 to 8 to control prompt size.

Merged hard13 rerank output:

```text
outputs/easy_finance_committed_64_rerank_deepseek_hard13_s8.jsonl
outputs/easy_finance_committed_64_rerank_deepseek_hard13_s8_eval.json
outputs/easy_finance_committed_64_bm25_plus_deepseek_hard13_s8.jsonl
outputs/easy_finance_committed_64_bm25_plus_deepseek_hard13_s8_eval.json
outputs/easy_finance_committed_64_rerank_deepseek_hard13_s8_usage.json
```

64-record BM25 vs hard13 result:

```text
BM25:
Top-1 0.3906, Top-3 0.6094, Top-5 0.7969, Top-10 0.8594, MRR 0.5436

BM25 + DeepSeek hard13:
Top-1 0.4688, Top-3 0.7344, Top-5 0.9531, Top-10 0.9844, MRR 0.6408
```

Hard13 usage:

```text
records: 13
total_duration_seconds: 314.411
total_tokens: 483097
avg_total_tokens: 37161
```

Important data-quality issue:

```text
easyfinance-backend-20251029-001
```

This bug fix adds `easy_finance_backend/manual_journal/signals.py`, which does not exist in the buggy commit. The dataset builder retained only the existing touched file `easy_finance_backend/manual_journal/apps.py` as ground truth. DeepSeek selected plausible manual journal/bookkeeping files but not `apps.py`, so this case remained outside Top-10. This is a construct-validity issue for file-level localization because new-file fixes cannot be localized to a pre-existing source file.

Clean dataset adjustment:

```text
data/easy_finance/easy_finance_committed_clean63.jsonl
```

The clean63 view excludes `easyfinance-backend-20251029-001`.

Clean63 old BM25 result:

```text
Top-1:  0.3968
Top-3:  0.6190
Top-5:  0.8095
Top-10: 0.8730
Top-20: 0.9683
Top-50: 1.0000
MRR:    0.5518
```

Clean63 hard12 rerank result:

```text
outputs/easy_finance_committed_clean63_rerank_deepseek_hard12_s8.jsonl
outputs/easy_finance_committed_clean63_bm25_plus_deepseek_hard12_s8.jsonl
outputs/easy_finance_committed_clean63_bm25_plus_deepseek_hard12_s8_eval.json
outputs/easy_finance_committed_clean63_rerank_deepseek_hard12_s8_usage.json

Top-1:  0.4762
Top-3:  0.7460
Top-5:  0.9683
Top-10: 1.0000
MRR:    0.6510
```

Clean63 hard12 usage:

```text
records: 12
total_duration_seconds: 285.517
total_tokens: 434820
avg_total_tokens: 36235
```

Production-source cleanup:

```text
src/fl_localizer/indexer.py
```

Added `format_files` to skipped directories after observing this generated bundle repeatedly polluting backend rankings:

```text
easy_finance_backend/format_files/lol.js
```

It appeared in clean63 BM25 Top-10 candidates 24 times before exclusion.

Clean63 production BM25:

```text
outputs/easy_finance_committed_clean63_bm25_prod_top50.jsonl
outputs/easy_finance_committed_clean63_bm25_prod_top50_eval.json

Top-1:  0.3968
Top-3:  0.6825
Top-5:  0.8571
Top-10: 0.8730
Top-20: 0.9683
Top-50: 1.0000
MRR:    0.5727
```

Production oracle hard cases:

```text
outputs/easy_finance_clean63_prod_hard9_rank_gt5_selection.json
selected: 9 / 63
```

DeepSeek production hard9 output:

```text
outputs/easy_finance_committed_clean63_rerank_deepseek_prod_hard9_s8.jsonl
outputs/easy_finance_committed_clean63_rerank_deepseek_prod_hard9_s8_eval.json
outputs/easy_finance_committed_clean63_bm25_prod_plus_deepseek_hard9_s8.jsonl
outputs/easy_finance_committed_clean63_bm25_prod_plus_deepseek_hard9_s8_eval.json
outputs/easy_finance_committed_clean63_rerank_deepseek_prod_hard9_s8_usage.json
```

Production BM25 + hard9 result:

```text
Top-1:  0.4444
Top-3:  0.7778
Top-5:  0.9524
Top-10: 1.0000
MRR:    0.6344
```

Production hard9 rank changes:

```text
easyfinance-frontend-20250520-001: 18 -> 10
easyfinance-backend-20260203-001: 7 -> 1
easyfinance-backend-20251106-001: 12 -> 2
easyfinance-backend-20250501-001: 11 -> 1
easyfinance-frontend-20260220-001: 40 -> 3
easyfinance-frontend-20250930-001: 17 -> 8
easyfinance-frontend-20250705-001: 33 -> 7
easyfinance-frontend-20250627-002: 13 -> 3
easyfinance-frontend-20250522-001: 12 -> 1
```

Production hard9 usage:

```text
records: 9
total_duration_seconds: 197.651
total_tokens: 203477
avg_total_tokens: 22609
```

Interpretation:

- Removing generated `format_files` improves BM25 Top-3/Top-5 and cuts DeepSeek prompt cost substantially for backend cases.
- On the clean production dataset, targeted DeepSeek recovers all hard cases into Top-10, but three remain outside Top-5.
- Current Easy Finance conclusion: BM25 production + targeted DeepSeek hard9 is effective for Top-10 localization, but we still need a non-oracle selector and perhaps better evidence snippets for Top-5.

## 2026-05-27 - Defects4J selector automation and Mockito-20 expansion

Goal:

- Continue from the `Closure-4` type-cycle fix.
- Replace hand-picked add-ons with an automatic selector for the known hard-case families:
  pass-chain, type-cycle, and state-reset.
- Expand the Defects4J benchmark to `Mockito-20`.

Implementation:

```text
scripts/select_rerank_candidates.py
scripts/build_defects4j_dataset.py
```

Selector changes:

```text
scripts/select_rerank_candidates.py
  - Added optional --bugs input so selector can inspect bug report, failing tests, and stack trace.
  - Added pattern:pass_chain from pass_chain_boost / pass_chain_hint retrieval evidence.
  - Added pattern:type_cycle from cycle / inheritance / implements / extends / subtype / StackOverflowError evidence.
  - Added pattern:state_reset from clone/copy/reset/state plus distribution/random/seed/sample context.
  - Added pass_chain_min_boost, default 1000, to avoid selecting every low-confidence Closure pass candidate.
```

Build script hardening:

```text
scripts/build_defects4j_dataset.py
  - Writes each successful bug record immediately instead of buffering all records until the end.
  - Added --skip-compile for metadata export from existing checkouts.
  - Added --skip-failures for long benchmark builds where one bug may fail.
```

Selector validation on existing Closure/Math data:

```bash
python3 scripts/select_rerank_candidates.py \
  --pred outputs/closure_pilot_20_hybrid_focused_direct_top50.jsonl \
  --bugs data/defects4j/closure_pilot_20.jsonl \
  --out outputs/closure_pilot_20_hybrid_focused_pattern_selector.json \
  --ids-only

python3 scripts/select_rerank_candidates.py \
  --pred outputs/closure_pilot_20_hybrid_focused_passchain_direct_top50.jsonl \
  --bugs data/defects4j/closure_pilot_20.jsonl \
  --out outputs/closure_pilot_20_hybrid_focused_passchain_pattern_selector.json \
  --ids-only

python3 scripts/select_rerank_candidates.py \
  --pred outputs/math_pilot_20_hybrid_focused_direct_top50.jsonl \
  --bugs data/defects4j/math_pilot_20.jsonl \
  --out outputs/math_pilot_20_hybrid_focused_pattern_selector.json \
  --ids-only
```

Validation result:

```text
Closure direct selector:
selected 9 / 20
Closure-4 selected by pattern:type_cycle

Closure pass-chain selector:
selected 12 / 20
pattern:pass_chain selected Closure-10, Closure-13, Closure-16, Closure-20
Closure-4 selected by pattern:type_cycle

Math selector:
selected 6 / 20
Math-12 selected by pattern:state_reset
```

Mockito dataset generation:

```bash
python3 scripts/build_defects4j_dataset.py \
  --project Mockito \
  --bugs 1-9 \
  --skip-compile \
  --skip-tests \
  --out data/defects4j/mockito_pilot_20.jsonl

python3 scripts/build_defects4j_dataset.py \
  --project Mockito \
  --bugs 10-20 \
  --append \
  --skip-failures \
  --out data/defects4j/mockito_pilot_20.jsonl
```

Environment note:

```text
Mockito uses Gradle 4.9 in these checkouts.
The sandbox blocked Gradle's local file-lock communicator with:
java.net.BindException: Operation not permitted (Bind failed)

The Mockito dataset build therefore had to run outside the sandbox.
One partial Mockito-10 checkout left a stale invalid workspace and was removed before rebuilding.
```

Mockito data audit:

```text
dataset: data/defects4j/mockito_pilot_20.jsonl
records: 20
bug ids: Mockito-1..Mockito-20
unique bug ids: 20
missing ground-truth files in buggy checkouts: 0
ground-truth file counts:
  1-file bugs: 16
  2-file bugs: 3
  5-file bugs: 1
```

Mockito hybrid baseline:

```bash
python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/mockito_pilot_20.jsonl \
  --out outputs/mockito_pilot_20_hybrid_focused_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints

python3 scripts/evaluate_predictions.py \
  --bugs data/defects4j/mockito_pilot_20.jsonl \
  --pred outputs/mockito_pilot_20_hybrid_focused_direct_top50.jsonl \
  --per-bug \
  --ks 1,3,5,10,20,50 \
  > outputs/mockito_pilot_20_hybrid_focused_direct_top50_eval.json
```

Mockito focused hybrid/direct result:

```text
bugs: 20
Top-1:  0.35
Top-3:  0.55
Top-5:  0.65
Top-10: 0.75
Top-20: 0.95
Top-50: 1.00
MRR:    0.4818
```

Mockito Top-5 failures:

```text
Mockito-1  rank 7   gt src/org/mockito/internal/invocation/InvocationMatcher.java
Mockito-7  rank 12  gt src/org/mockito/internal/util/reflection/GenericMetadataSupport.java
Mockito-9  rank 15  gt src/org/mockito/internal/stubbing/answers/CallsRealMethods.java
Mockito-12 rank 18  gt src/org/mockito/internal/util/reflection/GenericMaster.java
Mockito-15 rank 13  gt src/org/mockito/internal/configuration/injection/FinalMockCandidateFilter.java
Mockito-17 rank 10  gt src/org/mockito/internal/creation/MockSettingsImpl.java / MockUtil.java
Mockito-20 rank 23  gt src/org/mockito/internal/creation/bytebuddy/ByteBuddyMockMaker.java
```

Mockito selector:

```bash
python3 scripts/select_rerank_candidates.py \
  --pred outputs/mockito_pilot_20_hybrid_focused_direct_top50.jsonl \
  --bugs data/defects4j/mockito_pilot_20.jsonl \
  --out outputs/mockito_pilot_20_hybrid_focused_pattern_selector.json \
  --ids-only
```

Selector result:

```text
selected: 15 / 20
selected ids:
Mockito-1, Mockito-2, Mockito-3, Mockito-4, Mockito-5,
Mockito-7, Mockito-8, Mockito-9, Mockito-10, Mockito-12,
Mockito-13, Mockito-14, Mockito-17, Mockito-19, Mockito-20

reason counts:
top1_without_direct_hint: 8
many_direct_hints>=7: 8
low_score_ratio<=1.02: 2
pattern:type_cycle: 1

Top-5 failure coverage: 6 / 7
Top-3 failure coverage: 8 / 9
missed Top-5 failure: Mockito-15
```

Dry-run prompt check:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/mockito_pilot_20.jsonl \
  --bm25 outputs/mockito_pilot_20_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_pilot_20_rerank_dryrun_selector15_s8_ctx4000.jsonl \
  --provider dry-run \
  --bug-ids Mockito-1,Mockito-2,Mockito-3,Mockito-4,Mockito-5,Mockito-7,Mockito-8,Mockito-9,Mockito-10,Mockito-12,Mockito-13,Mockito-14,Mockito-17,Mockito-19,Mockito-20 \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 8 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 4000 \
  --prompt-dir outputs/prompts_mockito_selector15_s8_ctx4000
```

Dry-run size:

```text
records: 15
prompt_chars min: 69765
prompt_chars median: 83686
prompt_chars max: 143225
prompt_chars total: 1381208
largest prompts:
  Mockito-1 143225
  Mockito-3 120517
  Mockito-12 116628
  Mockito-20 110298
  Mockito-4 95618
```

Interpretation:

- The pattern selector now captures the exact hard-case families discovered in Closure and Math.
- `Mockito-20` has full Top-50 recall, so LLM rerank has a viable candidate pool.
- Mockito is harder than Math/Time under focused hybrid retrieval: Top-5 is only 0.65.
- The default selector is too broad on Mockito at 15/20 selected and still misses `Mockito-15`.
- `Mockito-15` is a different failure mode: test/runner classes dominate retrieval, while the true file is an injection filter. This suggests a separate Mockito/reflection-injection selector or improved noisy runner filtering, not another pass-chain/type-cycle/state-reset rule.
- Because selector15 dry-run prompts total about 1.38M characters, a DeepSeek run should wait until the Mockito gate is tightened or split into targeted hard-case diagnostics.

Recommended next step:

1. Add a Mockito-specific noisy runner filter or injection/reflection selector for `Mockito-15`.
2. Run a smaller DeepSeek batch on the covered Top-5 failures before spending on all 15 selector outputs.
3. Keep `Mockito-20` as the next benchmark row in the report.

## 2026-05-27 - Stage report draft

Goal:

- Shift from more benchmark spending to a phase-report deliverable.
- Consolidate the current Defects4J and AboutWork results into a readable stage report.
- Make the report usable for near-term discussion before running more DeepSeek calls.

Created report:

```text
docs/stage_report_2026-05-27.md
```

Report contents:

```text
1. Stage goal
2. Current system
3. Method progress
4. Defects4J results
5. Key findings
6. AboutWork case study
7. Current contributions
8. Limitations
9. Next plan
10. Stage conclusion
```

Key framing:

- The current result supports LLM rerank as a second-stage fault localization method.
- The main bottleneck has shifted from simply calling an LLM to candidate recall, evidence quality, selector quality, and token cost.
- Mockito-20 should not be reranked with the broad selector15 yet; the next useful work is a tighter noisy-runner / reflection-injection selector.

Status:

```text
stage report draft complete
```

## 2026-05-27 - Mockito selector expansion and hard7 DeepSeek diagnostic

Goal:

- Continue the benchmark path after the Closure-4 type-cycle fix.
- Add Mockito-specific selector signals before spending on a broad rerank batch.
- Run a small DeepSeek diagnostic batch on Mockito Top-5 failures and fold the result into the stage report.

Selector update:

```text
script: scripts/select_rerank_candidates.py
new pattern families:
  pattern:mockito_invocation_varargs
  pattern:mockito_generic
  pattern:mockito_injection
  pattern:mockito_constructor_real_method
  pattern:mockito_serialization
```

Pattern-only selector command:

```bash
python3 scripts/select_rerank_candidates.py \
  --pred outputs/mockito_pilot_20_hybrid_focused_direct_top50.jsonl \
  --bugs data/defects4j/mockito_pilot_20.jsonl \
  --score-ratio-threshold 0 \
  --no-top1-without-direct \
  --direct-hint-count-threshold 0 \
  --out outputs/mockito_pilot_20_hybrid_focused_pattern_only_selector.json \
  --ids-only
```

Pattern-only selector result:

```text
selected: 12 / 20
selected ids:
  Mockito-1, Mockito-3, Mockito-7, Mockito-8, Mockito-9, Mockito-10,
  Mockito-12, Mockito-14, Mockito-15, Mockito-17, Mockito-19, Mockito-20

Top-5 failure coverage: 7 / 7
extra selected: 5
  Mockito-3, Mockito-8, Mockito-10, Mockito-14, Mockito-19

reason counts:
  pattern:mockito_constructor_real_method: 5
  pattern:mockito_generic: 3
  pattern:mockito_injection: 2
  pattern:mockito_invocation_varargs: 3
  pattern:mockito_serialization: 2
  pattern:type_cycle: 1
```

Diagnostic DeepSeek batch:

```text
selection file:
  outputs/mockito_hard7_diagnostic_selection.json

note:
  This selection is diagnostic/oracle-based because it uses baseline Top-5 failures.
  It is not a deployment selector.
```

DeepSeek command:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/mockito_pilot_20.jsonl \
  --bm25 outputs/mockito_pilot_20_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_pilot_20_rerank_deepseek_hard7_s6_ctx3000_top30.jsonl \
  --provider deepseek \
  --bug-ids Mockito-1,Mockito-7,Mockito-9,Mockito-12,Mockito-15,Mockito-17,Mockito-20 \
  --top-candidates 30 \
  --top-output 10 \
  --max-snippet-lines 6 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 3000 \
  --prompt-dir outputs/prompts_mockito_hard7_s6_ctx3000_top30_deepseek
```

Hard7 rerank-only result:

```text
bugs: 7
Top-1: 0.5714
Top-3: 0.8571
Top-5: 0.8571
Top-10: 0.8571
MRR:   0.7143

rank changes:
  Mockito-1   7 -> 1
  Mockito-7  12 -> 1
  Mockito-9  15 -> 2
  Mockito-12 18 -> 1
  Mockito-15 13 -> 2
  Mockito-17 10 -> 1
  Mockito-20 23 -> miss
```

Usage:

```text
records: 7
total_tokens: 152020
avg_total_tokens: 21717.14
total_duration_seconds: 149.035
avg_duration_seconds: 21.291
```

Merged result:

```text
baseline:
  Top-1: 0.35
  Top-3: 0.55
  Top-5: 0.65
  Top-10: 0.75
  MRR:   0.4818

focused hybrid/direct + diagnostic DeepSeek hard7:
  Top-1: 0.55
  Top-3: 0.85
  Top-5: 0.95
  Top-10: 0.95
  MRR:   0.7033
```

Important caveat:

- The merged Top-50 number drops to 0.95 because the merged rerank output is truncated to top-10. It should not be compared against the baseline Top-50 recall.
- The Top-1/Top-3/Top-5/Top-10 metrics are comparable for this merged output.

Mockito-20 diagnosis:

- The true file `src/org/mockito/internal/creation/bytebuddy/ByteBuddyMockMaker.java` was in the top-30 candidate prompt.
- The snippet shown to the model was weak and generic, centered on copied mock settings rather than ByteBuddy mock creation/type mockability behavior.
- DeepSeek selected configuration/injection classes instead and did not return `ByteBuddyMockMaker.java` in the top-10.
- Next Mockito work should improve ByteBuddy/MockMaker evidence before spending more calls on `Mockito-20`.

Interpretation:

- Mockito is rerankable: 6 of 7 baseline Top-5 failures moved into Top-3.
- The pattern selector now covers all observed Mockito Top-5 failures, including the previously missed `Mockito-15`.
- The selector is still too broad at 12/20 for a final deployment policy.
- The current stage report can honestly claim a strong diagnostic gain on Mockito, while keeping selector generalization as the next risk.

## 2026-05-27 - Mockito-20 ByteBuddy evidence add-on

Goal:

- Diagnose the only remaining Mockito hard7 miss: `Mockito-20`.
- Test whether better constructor/spy evidence can make DeepSeek select `ByteBuddyMockMaker.java`.
- Keep the add-on to a single bug before changing report numbers.

Diagnosis:

```text
baseline rank: 23
true file:
  src/org/mockito/internal/creation/bytebuddy/ByteBuddyMockMaker.java

first hard7 DeepSeek result:
  miss

reason:
  The file was in the prompt, but the snippet showed only exception wrapping and
  class-instantiator initialization. It did not clearly expose the mock instance
  creation path for constructor/spy failures.
```

Code/prompt changes:

```text
src/fl_localizer/snippets.py
  add instantiate/instantiator/bytebuddy/useconstructor as high-signal snippet terms

scripts/run_llm_rerank.py
  add Mockito constructor/spy semantic snippet terms

src/fl_localizer/prompts.py
  add a general Mockito @Spy/useConstructor rule:
  inspect MockMaker or bytecode creation classes that decide how mock instances are instantiated
```

First M20 retry:

```text
output:
  outputs/mockito_pilot_20_rerank_deepseek_m20_bytebuddy_s10_ctx5000_top30.jsonl

result:
  miss

usage:
  total_tokens: 26057
  duration_seconds: 25.158
```

Second M20 retry with explicit Mockito constructor/spy prompt rule:

```text
output:
  outputs/mockito_pilot_20_rerank_deepseek_m20_bytebuddy_rule_s10_ctx5000_top30.jsonl

result:
  Mockito-20 rank 23 -> rank 3

usage:
  total_tokens: 25568
  duration_seconds: 18.694
```

DeepSeek ranked `ByteBuddyMockMaker.java` at rank 3 with this rationale:

```text
Creates mock instances and uses classInstantiator; if instantiation fails without
exception, could set null mock.
```

Merged final Mockito diagnostic result:

```text
baseline:
  Top-1:  0.35
  Top-3:  0.55
  Top-5:  0.65
  Top-10: 0.75
  MRR:    0.4818

hard7 + M20 ByteBuddy rule:
  Top-1:  0.55
  Top-3:  0.90
  Top-5:  1.00
  Top-10: 1.00
  MRR:    0.7200
```

Output files:

```text
outputs/mockito_m20_bytebuddy_rule_selection.json
outputs/mockito_pilot_20_hybrid_focused_plus_deepseek_hard7_plus_m20_bytebuddy_rule.jsonl
outputs/mockito_pilot_20_hybrid_focused_plus_deepseek_hard7_plus_m20_bytebuddy_rule_eval.json
outputs/mockito_hard7_plus_m20_bytebuddy_rule_usage_estimate.json
```

Interpretation:

- Mockito hard cases are strongly rerankable once prompt evidence points to the right framework layer.
- The final Mockito diagnostic result reaches Top-5 1.00 and Top-10 1.00.
- This is still not a clean deployment policy because the M20 add-on was triggered after inspecting the previous miss.
- The next research step is to turn the Mockito constructor/spy rule into a non-oracle selector rule and validate it on fresh Mockito or other mocking-framework bugs.

## 2026-05-27 - Results integration document

Goal:

- Consolidate the latest Defects4J, Mockito, cost, and AboutWork results into one report-ready document.
- Separate best current metrics from diagnostic/oracle caveats.

Created:

```text
docs/results_integration_2026-05-27.md
```

Integrated result:

```text
Best current Defects4J macro average:
  Top-1: 0.7583
  Top-3: 0.9333
  Top-5: 1.0000
  MRR:   0.8511
```

Included:

- Best current row for Lang, Math, Chart, Time, Closure, and Mockito.
- Mockito hard7 + M20 ByteBuddy add-on rank changes.
- Cost table for Math, Time, Closure, Mockito, and AboutWork.
- AboutWork selector_v3 case-study result.
- Clear caveat that Closure/Mockito add-ons are diagnostic and must become non-oracle selector rules before being claimed as deployment policy.

Linked from:

```text
docs/stage_report_2026-05-27.md
docs/current_results_report.md
```

## 2026-05-31 - Mockito tight non-oracle selector9

Goal:

- Return to the Defects4J benchmark experiments.
- Convert the previous Mockito diagnostic success into a narrower non-oracle selector.
- Reduce Mockito pattern selection from 12/20 to about 7-9/20 while preserving hard-case coverage.

Implementation:

```text
scripts/select_rerank_candidates.py
```

Added:

```text
--mockito-tight-patterns
```

The tight Mockito pattern rule keeps:

- Mockito pattern cases where top-1 lacks a direct hint.
- generic/deep-stub cases with many direct hints.
- constructor/spy cases with many direct hints and low top1/top2 score separation.
- injection cases.
- serialization cases where top-1 lacks a direct hint.
- type-cycle cases only when retrieval confidence is weak.

Selector command:

```bash
python3 scripts/select_rerank_candidates.py \
  --pred outputs/mockito_pilot_20_hybrid_focused_direct_top50.jsonl \
  --bugs data/defects4j/mockito_pilot_20.jsonl \
  --score-ratio-threshold 0 \
  --no-top1-without-direct \
  --direct-hint-count-threshold 0 \
  --mockito-tight-patterns \
  --out outputs/mockito_pilot_20_hybrid_focused_tight_pattern_selector.json \
  --ids-only
```

Selector result:

```text
selected: 9 / 20
selected ids:
  Mockito-1, Mockito-3, Mockito-7, Mockito-9, Mockito-12,
  Mockito-15, Mockito-17, Mockito-19, Mockito-20

baseline hard3 coverage: 9 / 9
baseline hard5 coverage: 7 / 7
extra selected beyond hard3: 0
```

This is not an oracle selector at runtime because it uses only bug text, stack/test context, retrieval scores, direct-hint signals, and pattern signals. It is still fitted on this Mockito-20 pilot and needs validation on fresh bugs.

Missing DeepSeek calls:

The prior hard7 + M20 runs already covered:

```text
Mockito-1, Mockito-7, Mockito-9, Mockito-12, Mockito-15, Mockito-17, Mockito-20
```

The tight selector additionally selected:

```text
Mockito-3, Mockito-19
```

Dry-run:

```text
outputs/mockito_pilot_20_rerank_dryrun_tight_selector_missing2_s6_ctx3000_top30.jsonl

prompt chars:
  Mockito-3:  90209
  Mockito-19: 47940
```

DeepSeek command:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/mockito_pilot_20.jsonl \
  --bm25 outputs/mockito_pilot_20_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_pilot_20_rerank_deepseek_tight_selector_missing2_s6_ctx3000_top30.jsonl \
  --provider deepseek \
  --bug-ids Mockito-3,Mockito-19 \
  --top-candidates 30 \
  --top-output 10 \
  --max-snippet-lines 6 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 3000 \
  --prompt-dir outputs/prompts_mockito_tight_selector_missing2_s6_ctx3000_top30_deepseek
```

Missing2 DeepSeek result:

```text
Mockito-3:  baseline rank 5 -> DeepSeek rank 1
Mockito-19: baseline rank 5 -> DeepSeek rank 1

selected-2 result:
  Top-1: 1.00
  Top-3: 1.00
  Top-5: 1.00
  MRR:   1.00
```

Usage for the two new calls:

```text
records: 2
total_tokens: 41968
avg_total_tokens: 20984.0
total_duration_seconds: 22.542
avg_duration_seconds: 11.271
```

Final merged output:

```text
outputs/mockito_pilot_20_hybrid_focused_plus_deepseek_tight_selector9.jsonl
outputs/mockito_pilot_20_hybrid_focused_plus_deepseek_tight_selector9_eval.json
outputs/mockito_tight_selector9_usage_estimate.json
```

Final Mockito-20 result:

```text
baseline focused hybrid/direct:
  Top-1:  0.35
  Top-3:  0.55
  Top-5:  0.65
  Top-10: 0.75
  MRR:    0.4818

focused hybrid/direct + tight selector9 DeepSeek:
  Top-1:  0.65
  Top-3:  1.00
  Top-5:  1.00
  Top-10: 1.00
  MRR:    0.8000
```

Deployment-equivalent usage estimate:

```text
records: 9
total_tokens: 195100
avg_total_tokens: 21677.778
total_duration_seconds: 164.742
avg_duration_seconds: 18.305
```

Interpretation:

- The tight selector improves over the previous diagnostic hard7 + M20 result:
  - Top-1: 0.55 -> 0.65
  - Top-3: 0.90 -> 1.00
  - MRR: 0.7200 -> 0.8000
- It reduces pattern-only selection from 12/20 to 9/20.
- It selects exactly the baseline Top-3 misses on this pilot, but this is still an in-sample result.
- Next step should validate the same selector on fresh Mockito bugs or another mocking-framework style project.

## 2026-05-27 - Easy Finance non-oracle selector_v1

Goal:

- Replace the Easy Finance oracle hard9 selection with a deployable selector that does not inspect ground-truth rank.
- Keep LLM calls selective on the clean production dataset.

Added selector:

```text
scripts/select_easy_finance_rerank_candidates.py
```

Selector input:

```text
data/easy_finance/easy_finance_committed_clean63.jsonl
outputs/easy_finance_committed_clean63_bm25_prod_top50.jsonl
```

Selector output:

```text
outputs/easy_finance_clean63_prod_selector_v1.json
```

Selector criteria:

- Backend `reports` / `bookkeeping` area mismatch when BM25 Top1 is outside the expected app path.
- Backend management-command noise when Top1 is under `/management/commands/` but the bug text is not a command bug.
- Backend admin invoice mismatch when the bug is admin-invoice specific but Top1 is non-admin invoice code.
- Frontend admin unreviewed-count, chat-history, admin-user-filtering, invoice-currency, expense-form, and confirm-loading domain/path mismatch patterns.
- Score ratio is implemented as an optional knob but disabled for `selector_v1`.

Selection:

```text
selected: 10 / 63
selected_fraction: 0.1587
```

The selector covers all 9 production BM25 Top-5 failures from the previous hard9 diagnostic and adds one non-hard case:

```text
easyfinance-backend-20251015-001
reason: backend_management_command_noise
BM25 rank: 3
DeepSeek rank: 1
```

Additional DeepSeek run for selector_v1:

```text
outputs/easy_finance_committed_clean63_rerank_deepseek_prod_selector_v1_add1_s8.jsonl
tokens: 21606
```

Merged selector_v1 outputs:

```text
outputs/easy_finance_committed_clean63_rerank_deepseek_prod_selector_v1_s8.jsonl
outputs/easy_finance_committed_clean63_rerank_deepseek_prod_selector_v1_s8_eval.json
outputs/easy_finance_committed_clean63_bm25_prod_plus_deepseek_selector_v1_s8.jsonl
outputs/easy_finance_committed_clean63_bm25_prod_plus_deepseek_selector_v1_s8_eval.json
outputs/easy_finance_committed_clean63_rerank_deepseek_prod_selector_v1_s8_usage.json
```

Clean63 production comparison:

```text
BM25 production:
Top-1 0.3968, Top-3 0.6825, Top-5 0.8571, Top-10 0.8730, MRR 0.5727

BM25 + DeepSeek hard9 oracle:
Top-1 0.4444, Top-3 0.7778, Top-5 0.9524, Top-10 1.0000, MRR 0.6344

BM25 + DeepSeek selector_v1:
Top-1 0.4603, Top-3 0.7778, Top-5 0.9524, Top-10 1.0000, MRR 0.6450
```

Selector_v1 rank changes:

```text
easyfinance-frontend-20250520-001: 18 -> 10
easyfinance-backend-20260203-001: 7 -> 1
easyfinance-backend-20251106-001: 12 -> 2
easyfinance-backend-20251015-001: 3 -> 1
easyfinance-backend-20250501-001: 11 -> 1
easyfinance-frontend-20260220-001: 40 -> 3
easyfinance-frontend-20250930-001: 17 -> 8
easyfinance-frontend-20250705-001: 33 -> 7
easyfinance-frontend-20250627-002: 13 -> 3
easyfinance-frontend-20250522-001: 12 -> 1
```

Selector_v1 usage:

```text
records: 10
total_duration_seconds: 222.123
total_tokens: 225083
avg_total_tokens: 22508
```

Interpretation:

- `selector_v1` is non-oracle at runtime: it only uses bug text, area metadata, BM25 Top1 path, optional score ratio metadata, and ranked file paths.
- On the current Easy Finance clean63 case study, it matches the hard9 Top-10 recovery and improves MRR by also reranking the management-command noise case.
- It is still fitted on the observed Easy Finance dataset, so the result should be reported as a company-project case-study selector and validated on fresh Easy Finance bug logs before making a broader generalization claim.

### Easy Finance UI evidence v2 diagnostic

Goal:

- Improve the three remaining selector_v1 Top-5 misses:
  `easyfinance-frontend-20250520-001`, `easyfinance-frontend-20250930-001`,
  and `easyfinance-frontend-20250705-001`.
- Diagnose whether the misses are caused by weak snippet evidence or by ambiguous git-derived bug reports.

Code changes:

```text
scripts/run_llm_rerank.py
src/fl_localizer/snippets.py
src/fl_localizer/prompts.py
```

Snippet/evidence changes:

- Added frontend semantic snippet terms for unreviewed counts, loading buttons, and currency display.
- Added wider context windows for high-signal UI/data terms.
- Added scoring boosts for `<Button>`, `isLoading` / `isPending` / `isSubmitting`, and `currency: USD/EUR` lines.
- Tightened the loading semantic trigger so the generic Easy Finance expected-behavior phrase `loading, or display behavior` does not pollute unrelated currency/display cases.
- Added evidence-mode prompt guidance to prefer page/container files that own API queries, mutations, state, routes, or display formatting over generic tables/modals/layouts when the snippet supports that ownership.

Dry-run prompts:

```text
outputs/prompts_easy_finance_prod_top5_miss_ui_guidance_s12_dryrun/
outputs/prompts_easy_finance_prod_top5_miss_ui_guidance_s18_widectx_dryrun/
outputs/prompts_easy_finance_prod_top5_miss_ui_guidance_s24_buttonctx_dryrun/
outputs/prompts_easy_finance_prod_currency_config_s32_dryrun/
```

Key evidence improvements:

```text
easyfinance-frontend-20250520-001
  ExpensesPage/InvoicePage snippets now expose useQuery returning mock count data.

easyfinance-frontend-20250705-001
  InvoiceSpecificPage snippet now exposes formatCurrency with currency: 'USD'.
```

Diagnostic DeepSeek runs:

```text
outputs/easy_finance_committed_clean63_rerank_deepseek_prod_top5_miss_ui_guidance_s32.jsonl
outputs/easy_finance_committed_clean63_rerank_deepseek_prod_top5_miss_ui_guidance_s32_usage.json

outputs/easy_finance_committed_clean63_rerank_deepseek_prod_currency_config_s32.jsonl
outputs/easy_finance_committed_clean63_rerank_deepseek_prod_currency_config_s32_usage.json
```

Focused rank changes:

```text
easyfinance-frontend-20250520-001: selector_v1 10 -> UI evidence 1
easyfinance-frontend-20250705-001: selector_v1 7 -> currency-config evidence 1
easyfinance-frontend-20250930-001: selector_v1 8 -> UI evidence 9
```

The `20250930` run got worse because the git-derived report says `Confirm expense/invoice buttons`, while the actual fix touches a `Continue` expense button, a `Create Invoice` button, and a `View PDF` button. The broader text makes unrelated confirm modals look plausible to the LLM.

Merged v2 output:

```text
outputs/easy_finance_committed_clean63_rerank_deepseek_prod_selector_v1_ui_evidence_v2.jsonl
outputs/easy_finance_committed_clean63_rerank_deepseek_prod_selector_v1_ui_evidence_v2_eval.json
outputs/easy_finance_committed_clean63_bm25_prod_plus_deepseek_selector_v1_ui_evidence_v2.jsonl
outputs/easy_finance_committed_clean63_bm25_prod_plus_deepseek_selector_v1_ui_evidence_v2_eval.json
outputs/easy_finance_committed_clean63_rerank_deepseek_prod_selector_v1_ui_evidence_v2_usage.json
```

Clean63 production comparison:

```text
BM25 production:
Top-1 0.3968, Top-3 0.6825, Top-5 0.8571, Top-10 0.8730, MRR 0.5727

BM25 + DeepSeek selector_v1:
Top-1 0.4603, Top-3 0.7778, Top-5 0.9524, Top-10 1.0000, MRR 0.6450

BM25 + DeepSeek selector_v1 UI evidence v2:
Top-1 0.4921, Top-3 0.8095, Top-5 0.9841, Top-10 1.0000, MRR 0.6729
```

Selector_v1 UI evidence v2 usage:

```text
records: 10
total_duration_seconds: 215.589
total_tokens: 250902
avg_total_tokens: 25090
```

Interpretation:

- The main remaining Easy Finance bottleneck is no longer Top-10 recovery; it is Top-5 precision on ambiguous frontend UI reports.
- Better snippet evidence directly fixed `admin unreviewed count` and `invoice currency` cases.
- `easyfinance-frontend-20250930-001` should be treated as a threat-to-validity example for git-history-derived reports: the commit message is too broad relative to the actual touched UI buttons.
- The v2 result is a fitted evidence diagnostic, not yet a final general selector policy.

### Easy Finance strict62 sensitivity analysis

Goal:

- Decide whether to keep optimizing the last clean63 Top-5 miss or treat it as a data-quality issue.
- Measure the result after excluding the one sample whose git-derived bug text does not match the touched files well.

Negative diagnostic:

```text
easyfinance-frontend-20250930-001
```

Commit message:

```text
EAS-121 added loading states to confirm expense and invoice buttons
```

Actual touched files/actions:

```text
easy_finance_frontend/src/pages/Expenses/UploadExpenseClientPage.tsx
  Continue button: added isProcessing/disabled behavior.

easy_finance_frontend/src/pages/Invoices/CreateNewInvoicePage.tsx
  Create Invoice button: added isLoading/disabled text behavior.

easy_finance_frontend/src/pages/Invoices/InvoiceSpecificPage.tsx
  View PDF button: added disabled behavior while PDF loads.
```

Why this is a data-quality issue:

- The bug text says `Confirm expense/invoice buttons`.
- The repository contains plausible confirm-modal candidates not touched by the fix:

```text
easy_finance_frontend/src/components/Admin/Invoices/InvoiceOverviewModal.tsx
easy_finance_frontend/src/pages/Invoices/UploadInvoiceOverview.tsx
```

- With stronger loading-action evidence, DeepSeek ranks those literal confirm-modal candidates above the ground truth. That is reasonable from the bug text, but wrong under fix-touched-file evaluation.

Negative diagnostic output:

```text
outputs/easy_finance_committed_clean63_rerank_deepseek_prod_loading_action_v3_s64_ctx8.jsonl
outputs/easy_finance_committed_clean63_rerank_deepseek_prod_loading_action_v3_s64_ctx8_usage.json
```

Usage for the negative diagnostic:

```text
records: 1
total_duration_seconds: 41.396
total_tokens: 57256
```

Created strict62 filtered view:

```text
data/easy_finance/easy_finance_committed_strict62.jsonl
outputs/easy_finance_committed_strict62_bm25_prod_top50.jsonl
outputs/easy_finance_committed_strict62_bm25_prod_top50_eval.json
outputs/easy_finance_strict62_prod_selector_v1.json
outputs/easy_finance_committed_strict62_rerank_deepseek_prod_selector_v1_ui_evidence_v2.jsonl
outputs/easy_finance_committed_strict62_rerank_deepseek_prod_selector_v1_ui_evidence_v2_eval.json
outputs/easy_finance_committed_strict62_rerank_deepseek_prod_selector_v1_ui_evidence_v2_usage.json
outputs/easy_finance_committed_strict62_bm25_prod_plus_deepseek_selector_v1_ui_evidence_v2.jsonl
outputs/easy_finance_committed_strict62_bm25_prod_plus_deepseek_selector_v1_ui_evidence_v2_eval.json
```

Strict62 comparison:

```text
BM25 production:
Top-1 0.4032, Top-3 0.6935, Top-5 0.8710, Top-10 0.8871, MRR 0.5810

BM25 + DeepSeek selector_v1 UI evidence v2:
Top-1 0.5000, Top-3 0.8226, Top-5 1.0000, Top-10 1.0000, MRR 0.6817
```

Strict62 selector usage:

```text
selected: 9 / 62
total_duration_seconds: 188.506
total_tokens: 226860
avg_total_tokens: 25207
```

Interpretation:

- The clean63 result remains the main Easy Finance result because it preserves the full filtered dataset.
- The strict62 result is a sensitivity analysis showing that the remaining Top-5 miss is driven by a questionable git-derived report, not by candidate recall.
- For reporting, use clean63 as primary and strict62 as a data-quality robustness check.

### Easy Finance strict62 controlled agentic inspection pilot

Goal:

- Try the optional RQ5 extension from the proposal: controlled agentic inspection before final file ranking.
- Keep the agent reproducible and comparable with the existing rerank pipeline.

Implementation added:

```text
src/fl_localizer/agent_tools.py
src/fl_localizer/agent_prompts.py
scripts/run_agentic_rerank.py
```

Agent constraints:

```text
candidate pool: strict62 BM25 production top-50
selected cases: selector_v1 9 / 62
max_steps: 2
tools: search_files, inspect_candidate, read_file_window
final output: same prediction JSONL schema as other rerank methods
forbidden context: fixed commit, patch, touched files, ground truth
```

Outputs:

```text
outputs/easy_finance_committed_strict62_agentic_deepseek_selector_v1_s2.jsonl
outputs/easy_finance_committed_strict62_agentic_deepseek_selector_v1_s2_trace.jsonl
outputs/easy_finance_committed_strict62_agentic_deepseek_selector_v1_s2_eval.json
outputs/easy_finance_committed_strict62_agentic_deepseek_selector_v1_s2_usage.json
outputs/easy_finance_committed_strict62_bm25_prod_plus_agentic_deepseek_selector_v1_s2.jsonl
outputs/easy_finance_committed_strict62_bm25_prod_plus_agentic_deepseek_selector_v1_s2_eval.json
```

Selected 9-case agent result:

```text
Top-1 0.6667, Top-3 0.8889, Top-5 1.0000, Top-10 1.0000, MRR 0.8056
```

Merged strict62 result:

```text
BM25 production + selector_v1 controlled agentic DeepSeek s2:
Top-1 0.5000, Top-3 0.8065, Top-5 1.0000, Top-10 1.0000, MRR 0.6831
```

Usage:

```text
records: 9
total_duration_seconds: 154.399
total_tokens: 250481
avg_total_tokens: 27831
```

Comparison against one-shot strict62 UI evidence v2:

```text
One-shot selective:
Top-1 0.5000, Top-3 0.8226, Top-5 1.0000, Top-10 1.0000, MRR 0.6817
tokens: 226860

Agentic selective s2:
Top-1 0.5000, Top-3 0.8065, Top-5 1.0000, Top-10 1.0000, MRR 0.6831
tokens: 250481
```

Interpretation:

- The controlled agent protocol works technically: tool traces are captured, JSON outputs are valid, and evaluator/merge scripts can consume the ranking.
- On this Easy Finance strict62 selector set, agentic inspection does not clearly outperform one-shot UI evidence reranking.
- The result is still useful for RQ5 as a pilot: it shows that limited tool use can match one-shot reranking but costs about 10.4% more tokens on this set.
- The next useful agent experiment should target cases where one-shot fails because the initial snippet is weak, or add a verifier pass instead of increasing agent steps blindly.

### Easy Finance strict62 agentic verifier pass

Goal:

- Test whether an independent verifier can improve the controlled agentic ranking without additional tool use.
- The verifier only sees the bug report, the agent top-10 ranking, fixed deterministic snippets for those top-10 files, and the prior agent observations.

Implementation added:

```text
src/fl_localizer/verifier_prompts.py
scripts/run_verifier_rerank.py
```

Outputs:

```text
outputs/easy_finance_committed_strict62_agentic_plus_verifier_deepseek_selector_v1_s2.jsonl
outputs/easy_finance_committed_strict62_agentic_plus_verifier_deepseek_selector_v1_s2_eval.json
outputs/easy_finance_committed_strict62_agentic_plus_verifier_deepseek_selector_v1_s2_usage.json
outputs/easy_finance_committed_strict62_bm25_prod_plus_agentic_verifier_deepseek_selector_v1_s2.jsonl
outputs/easy_finance_committed_strict62_bm25_prod_plus_agentic_verifier_deepseek_selector_v1_s2_eval.json
```

Selected 9-case verifier result:

```text
Top-1 0.6667, Top-3 0.8889, Top-5 1.0000, Top-10 1.0000, MRR 0.7870
```

Merged strict62 result:

```text
BM25 production + selector_v1 agentic s2 + verifier:
Top-1 0.5000, Top-3 0.8065, Top-5 1.0000, Top-10 1.0000, MRR 0.6804
```

Verifier-only usage:

```text
records: 9
total_duration_seconds: 121.980
total_tokens: 80569
avg_total_tokens: 8952
```

Comparison:

```text
Agentic s2 only:
Top-1 0.5000, Top-3 0.8065, Top-5 1.0000, Top-10 1.0000, MRR 0.6831
tokens: 250481

Agentic s2 + verifier:
Top-1 0.5000, Top-3 0.8065, Top-5 1.0000, Top-10 1.0000, MRR 0.6804
tokens: 331050 total agent + verifier
```

Interpretation:

- This verifier design does not improve the Easy Finance strict62 agentic result.
- It slightly lowers MRR because `easyfinance-frontend-20250520-001` moves from correct rank 2 to correct rank 4.
- The result is useful as a negative RQ5 finding: adding a verifier pass can increase cost without improving localization if the verifier receives noisy top-10 evidence.
- Do not use this verifier as the main method. Keep it as an ablation and prefer one-shot selective rerank or agentic-only for the current company-project results.

## 2026-05-31 Experiment design realignment with thesis proposal

Goal:

- Align the local experiment design with `ls/llm-assisted-fault-localization-proposal.md`.
- Reframe the project method around selective evidence-aware LLM fault localization rather than a simple backend comparison.
- Make the current Defects4J, AboutWork, and Easy Finance results fit the same RQ structure.

Updated file:

```text
docs/experiment_design.md
```

Main changes:

- Replaced the old RQ5 about DeepSeek API vs Codex backend with the proposal-aligned RQ5 about controlled agentic inspection and verifier reranking.
- Split the evaluation targets into three dataset groups: Defects4J benchmark, AboutWork bug logs, and Easy Finance git-history-derived cases.
- Promoted selective one-shot DeepSeek reranking as the current main method.
- Marked controlled agentic inspection as an RQ5 extension and verifier rerank as an ablation, not the main method.
- Added explicit no-leakage rules: ground truth, fixed commit diff, and post-fix code must not enter prompts, selectors, or agent tools.
- Integrated the current staged results:
  - Defects4J macro best: Top-1 0.7750, Top-3 0.9500, Top-5 1.0000, MRR 0.8644.
  - AboutWork selector_v3 + DeepSeek: 11/39 calls, Top-1 0.7692, Top-3/Top-5/Top-10 1.0000, MRR 0.8675.
  - Easy Finance one-shot UI evidence v2 remains the main company-repo result.
  - Easy Finance agentic/verifier runs are recorded as useful RQ5 evidence but not as improvements over one-shot reranking.

Interpretation:

- The current project should be presented as a retrieval + evidence construction + selective LLM rerank pipeline.
- Defects4J supports benchmark effectiveness, while AboutWork and Easy Finance support the real-repository transfer question.
- Agentic inspection is technically feasible but currently only conditionally useful; verifier is a negative ablation in its present design.

Next:

- Keep future result tables separated into main method, extension, and ablation groups.
- Before thesis writing, validate which Closure/Mockito targeted evidence rules are fully automatic and which are still diagnostic.

## 2026-05-31 Results report alignment after method update

Goal:

- Continue the proposal-alignment work by updating the current results documents.
- Make the reported results match the new RQ structure and method framing.
- Keep Easy Finance and RQ5 agentic/verifier results visible in the main integration report.

Updated files:

```text
docs/current_results_report.md
docs/results_integration_2026-05-27.md
```

Main changes:

- Added proposal-aligned interpretation to `current_results_report.md`.
- Updated stale Defects4J scope text from 5 projects / 100 bugs to 6 projects / 120 bugs.
- Demoted Codex backend from a core RQ to a future engineering comparison.
- Replaced the old next-step priority list with:
  - selector generalization validation,
  - converting diagnostic evidence into automatic non-oracle rules,
  - expanding benchmark/company validation,
  - redesigning RQ5 agentic experiments only for one-shot failure cases,
  - cost control,
  - thesis writing.
- Added Easy Finance clean63 / strict62 results to `results_integration_2026-05-27.md`.
- Added Easy Finance cost rows for one-shot, agentic, and verifier variants.
- Added the RQ5 interpretation: controlled agentic inspection is technically feasible but not clearly better than one-shot; verifier is a negative ablation in the current design.

Interpretation:

- The results documents now match the experimental design more closely.
- The current evidence supports the main pipeline: retrieval + evidence construction + selective one-shot DeepSeek rerank.
- The strongest next experimental risk is selector/evidence-rule overfitting, especially Mockito, AboutWork, and Easy Finance fitted selectors.

Next:

- Implement a small fresh-validation plan before adding more LLM-heavy runs.
- Prefer fresh samples or held-out case slices over further tuning on the same pilot cases.

## 2026-05-31 Fresh validation plan drafted

Goal:

- Turn the next experimental step into a concrete validation plan.
- Reduce the risk of overfitting to the same Defects4J, AboutWork, and Easy Finance pilot samples.
- Define when to run LLM calls and when to stop at retrieval/selector diagnostics.

New file:

```text
docs/fresh_validation_plan_2026-05-31.md
```

Main content:

- Mockito fresh validation plan using `Mockito-21..30`.
- Closure rule validation plan using `Closure-21..30`.
- AboutWork fresh log validation requirement: at least 10 new committed bug logs.
- Easy Finance fresh commit / held-out validation requirement.
- RQ5 agentic redesign rule: only run agentic on one-shot failures where evidence is missing but candidate recall is sufficient.

Recommended immediate next step:

```text
Mockito-21..30 non-LLM validation:
build dataset -> focused hybrid retrieval -> evaluate -> tight selector report
```

Interpretation:

- This plan makes the next benchmark step cheaper and more defensible.
- LLM calls should wait until selector behavior on fresh samples is visible.

## 2026-05-31 Mockito fresh validation 21..30 non-LLM run

Goal:

- Validate whether Mockito tight selector9 generalizes beyond the original `Mockito-1..20` pilot.
- Run only non-LLM steps first: dataset build, focused hybrid retrieval, evaluation, and selector report.

Commands:

```bash
python3 scripts/build_defects4j_dataset.py \
  --project Mockito \
  --bugs 21-30 \
  --out data/defects4j/mockito_fresh_21_30.jsonl \
  --skip-failures

python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/mockito_fresh_21_30.jsonl \
  --out outputs/mockito_fresh_21_30_hybrid_focused_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints

python3 scripts/evaluate_predictions.py \
  --bugs data/defects4j/mockito_fresh_21_30.jsonl \
  --pred outputs/mockito_fresh_21_30_hybrid_focused_direct_top50.jsonl \
  --per-bug \
  --out outputs/mockito_fresh_21_30_hybrid_focused_direct_top50_eval.json

python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/mockito_fresh_21_30.jsonl \
  --pred outputs/mockito_fresh_21_30_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_fresh_21_30_tight_selector.json \
  --mockito-tight-patterns
```

Outputs:

```text
data/defects4j/mockito_fresh_21_30.jsonl
outputs/mockito_fresh_21_30_hybrid_focused_direct_top50.jsonl
outputs/mockito_fresh_21_30_hybrid_focused_direct_top50_eval.json
outputs/mockito_fresh_21_30_tight_selector.json
docs/mockito_fresh_21_30_validation_report.md
```

Dataset result:

```text
requested: Mockito-21..30
built: 9 records
skipped: Mockito-21 compile failed
```

Focused hybrid/direct result:

```text
bugs: 9
Top-1: 0.4444
Top-3: 0.5556
Top-5: 0.5556
MRR:   0.5339
Recall@50: 9 / 9
```

Per-bug ranks:

```text
Mockito-22: rank 1
Mockito-23: rank 2
Mockito-24: rank 1
Mockito-25: rank 1
Mockito-26: rank 7
Mockito-27: rank 15
Mockito-28: rank 14
Mockito-29: rank 41
Mockito-30: rank 1
```

Selector result:

```text
selected: 4 / 9
selected ids: Mockito-23, Mockito-25, Mockito-27, Mockito-29
Top-1 miss coverage: 3 / 5
Top-3 miss coverage: 2 / 4
Top-5 miss coverage: 2 / 4
```

Interpretation:

- Candidate recall is good enough for reranking because all ground-truth files are in top50.
- The tight selector only partially generalizes on fresh Mockito bugs.
- It misses two hard fresh families:
  - `Mockito-26`: primitive default values, ground truth `Primitives.java`, rank 7.
  - `Mockito-28`: InjectMocks exact type / ancestor matching, ground truth `DefaultInjectionEngine.java`, rank 14.
- Do not spend DeepSeek calls on this selected set yet; the selector first needs diagnostic improvement or another validation slice.

Decision:

- Treat this as a useful negative/partial fresh-validation result.
- Do not tune production selector directly on this slice.
- Candidate future rules are `mockito_primitive_default_values` and `mockito_injection_exact_type_ancestor`, but they should be validated on a separate slice before promotion.

## 2026-05-31 Mockito diagnostic selector and fresh validation 31..38

Goal:

- Add diagnostic-only Mockito selector patterns for the two fresh hard-case families found in `Mockito-21..30`.
- Verify that these diagnostic patterns do not immediately over-select on a separate fresh slice.
- Keep the default production selector unchanged unless explicitly passed a diagnostic flag.

Code change:

```text
scripts/select_rerank_candidates.py
```

New explicit flag:

```text
--mockito-diagnostic-patterns
```

Diagnostic-only reasons:

```text
diagnostic:mockito_primitive_default_values
diagnostic:mockito_injection_exact_type_ancestor
```

Validation on `Mockito-21..30`:

```text
default tight selector:
  selected: 4 / 9
  selected ids: Mockito-23, Mockito-25, Mockito-27, Mockito-29
  Top-5 miss coverage: 2 / 4

with diagnostics:
  selected: 6 / 9
  selected ids: Mockito-23, Mockito-25, Mockito-26, Mockito-27, Mockito-28, Mockito-29
  Top-5 miss coverage: 4 / 4
```

Commands for second fresh slice:

```bash
python3 scripts/build_defects4j_dataset.py \
  --project Mockito \
  --bugs 31-38 \
  --out data/defects4j/mockito_fresh_31_38.jsonl \
  --skip-failures

python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/mockito_fresh_31_38.jsonl \
  --out outputs/mockito_fresh_31_38_hybrid_focused_direct_top50.jsonl \
  --top-k 50 \
  --force-direct-hints

python3 scripts/evaluate_predictions.py \
  --bugs data/defects4j/mockito_fresh_31_38.jsonl \
  --pred outputs/mockito_fresh_31_38_hybrid_focused_direct_top50.jsonl \
  --per-bug \
  --ks 1,3,5,10,20,50 \
  --out outputs/mockito_fresh_31_38_hybrid_focused_direct_top50_eval.json

python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/mockito_fresh_31_38.jsonl \
  --pred outputs/mockito_fresh_31_38_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_fresh_31_38_tight_selector.json \
  --mockito-tight-patterns

python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/mockito_fresh_31_38.jsonl \
  --pred outputs/mockito_fresh_31_38_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_fresh_31_38_tight_selector_with_diagnostics.json \
  --mockito-tight-patterns \
  --mockito-diagnostic-patterns
```

Outputs:

```text
data/defects4j/mockito_fresh_31_38.jsonl
outputs/mockito_fresh_31_38_hybrid_focused_direct_top50.jsonl
outputs/mockito_fresh_31_38_hybrid_focused_direct_top50_eval.json
outputs/mockito_fresh_31_38_tight_selector.json
outputs/mockito_fresh_31_38_tight_selector_with_diagnostics.json
docs/mockito_fresh_31_38_validation_report.md
```

`Mockito-31..38` retrieval result:

```text
bugs: 8
Top-1:  0.1250
Top-3:  0.5000
Top-5:  0.7500
Top-10: 0.8750
Top-20: 1.0000
Top-50: 1.0000
MRR:    0.3382
```

Default tight selector on `Mockito-31..38`:

```text
selected: 5 / 8
selected ids: Mockito-32, Mockito-33, Mockito-35, Mockito-36, Mockito-37
Top-3 miss coverage: 4 / 4
Top-5 miss coverage: 2 / 2
```

Diagnostic selector on `Mockito-31..38`:

```text
selected: same 5 / 8
```

Interpretation:

- The diagnostic switch fixed the two known misses on `Mockito-21..30`.
- On a separate slice, it did not add extra selections, so there is no immediate over-selection signal.
- It is still not enough evidence to promote the diagnostic patterns to default production behavior.
- Default tight selector generalizes better on `Mockito-31..38`, but selected ratio is high at 62.5%.

Verification:

```text
python3 -m py_compile scripts/select_rerank_candidates.py
```

Decision:

- Do not run DeepSeek yet unless the next objective is explicitly to evaluate selected `Mockito-31..38` cases.
- If running DeepSeek next, the defensible set is the default tight selector set:
  `Mockito-32,Mockito-33,Mockito-35,Mockito-36,Mockito-37`.
- Research next step is to reduce selected ratio while preserving Top-5 miss coverage.

## 2026-05-31 Mockito selector cost-control v2 analysis

Goal:

- Reduce selected LLM calls for Mockito fresh validation while preserving retrieval Top-5 failure coverage.
- Compare pattern-only tight selector, diagnostic selector, broader full selector, and a new experimental cost-control v2 selector.

Code change:

```text
scripts/select_rerank_candidates.py
```

New explicit flag:

```text
--mockito-cost-control-v2
```

Cost-control v2 behavior:

- Starts from pattern-only tight selector settings:
  `--score-ratio-threshold 0 --direct-hint-count-threshold 0 --no-top1-without-direct`.
- Requires explicit `--mockito-diagnostic-patterns` for diagnostic families.
- Keeps `pattern:mockito_invocation_varargs` when there are many direct hints.
- Adds `pattern:mockito_real_method_interface` for real-method-on-interface failures.
- Does not use broad `top1_without_direct_hint`.

Commands:

```bash
python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/mockito_pilot_20.jsonl \
  --pred outputs/mockito_pilot_20_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_pilot_20_tight_cost_control_v2_selector.json \
  --mockito-tight-patterns \
  --mockito-diagnostic-patterns \
  --mockito-cost-control-v2 \
  --score-ratio-threshold 0 \
  --direct-hint-count-threshold 0 \
  --no-top1-without-direct

python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/mockito_fresh_21_30.jsonl \
  --pred outputs/mockito_fresh_21_30_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_fresh_21_30_tight_cost_control_v2_selector.json \
  --mockito-tight-patterns \
  --mockito-diagnostic-patterns \
  --mockito-cost-control-v2 \
  --score-ratio-threshold 0 \
  --direct-hint-count-threshold 0 \
  --no-top1-without-direct

python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/mockito_fresh_31_38.jsonl \
  --pred outputs/mockito_fresh_31_38_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_fresh_31_38_tight_cost_control_v2_selector.json \
  --mockito-tight-patterns \
  --mockito-diagnostic-patterns \
  --mockito-cost-control-v2 \
  --score-ratio-threshold 0 \
  --direct-hint-count-threshold 0 \
  --no-top1-without-direct
```

Summary:

```text
Mockito-1..20:
  pattern-only tight: 9/20 selected, Top-5 miss coverage 7/7
  cost-control v2:   11/20 selected, Top-5 miss coverage 7/7

Mockito-21..30:
  pattern-only tight: 2/9 selected, Top-5 miss coverage 0/4
  diagnostic only:    4/9 selected, Top-5 miss coverage 2/4
  cost-control v2:    6/9 selected, Top-5 miss coverage 4/4

Mockito-31..38:
  pattern-only tight: 1/8 selected, Top-5 miss coverage 0/2
  full diagnostic:    5/8 selected, Top-5 miss coverage 2/2
  cost-control v2:    4/8 selected, Top-5 miss coverage 2/2
```

Aggregate:

```text
records: 37
retrieval Top-5 failures: 13

pattern-only tight:          selected 12/37, Top-5 miss coverage 7/13
pattern-only + diagnostics:  selected 15/37, Top-5 miss coverage 9/13
cost-control v2:             selected 21/37, Top-5 miss coverage 13/13
full no-top1 diagnostics:    selected 23/37, Top-5 miss coverage 13/13
```

New doc:

```text
docs/mockito_selector_cost_control_2026-05-31.md
```

Interpretation:

- Pattern-only tight selector was overfit to `Mockito-1..20` and fails fresh coverage.
- Cost-control v2 is currently the best tradeoff: it recovers all observed Top-5 failures while avoiding some broad selector cost.
- It is still experimental because it was developed after inspecting the fresh validation behavior.

Verification:

```text
python3 -m py_compile scripts/select_rerank_candidates.py
```

Decision:

- Do not make v2 the default selector.
- If the next step is to spend DeepSeek calls, use the `Mockito-31..38` v2 selected set:
  `Mockito-32,Mockito-33,Mockito-36,Mockito-37`.

## 2026-06-01 - Mockito fresh 31..38 cost-control v2 DeepSeek rerank

Goal:

- Run the experimental cost-control v2 selected set on `Mockito-31..38`.
- Check whether targeted DeepSeek rerank improves the fresh retrieval baseline without reranking all 8 bugs.

Selected set:

```text
Mockito-32, Mockito-33, Mockito-36, Mockito-37
```

Command:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/mockito_fresh_31_38.jsonl \
  --bm25 outputs/mockito_fresh_31_38_hybrid_focused_direct_top50.jsonl \
  --out outputs/mockito_fresh_31_38_rerank_deepseek_cost_control_v2_s6_ctx12000_top50.jsonl \
  --provider deepseek \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 6 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 12000 \
  --bug-ids Mockito-32,Mockito-33,Mockito-36,Mockito-37 \
  --prompt-dir outputs/prompts_mockito_fresh_31_38_cost_control_v2_s6_ctx12000_top50
```

Outputs:

```text
outputs/mockito_fresh_31_38_rerank_deepseek_cost_control_v2_s6_ctx12000_top50.jsonl
outputs/mockito_fresh_31_38_rerank_deepseek_cost_control_v2_s6_ctx12000_top50_eval.json
outputs/mockito_fresh_31_38_rerank_deepseek_cost_control_v2_s6_ctx12000_top50_usage.json
outputs/mockito_fresh_31_38_merged_deepseek_cost_control_v2_s6_ctx12000_top50.jsonl
outputs/mockito_fresh_31_38_merged_deepseek_cost_control_v2_s6_ctx12000_top50_eval.json
```

Selected-case rerank result:

```text
bugs: 4
Top-1: 1.0000
Top-3: 1.0000
Top-5: 1.0000
Top-10: 1.0000
MRR:   1.0000
```

Per selected bug:

```text
Mockito-32: rank 1
Mockito-33: rank 1
Mockito-36: rank 1
Mockito-37: rank 1
```

Merged result over all `Mockito-31..38` records:

```text
bugs: 8
Top-1:  0.6250
Top-3:  1.0000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.7500
```

Baseline comparison:

```text
focused hybrid/direct:
  Top-1:  0.1250
  Top-3:  0.5000
  Top-5:  0.7500
  Top-10: 0.8750
  MRR:    0.3382

cost-control v2 + DeepSeek selected rerank:
  Top-1:  0.6250
  Top-3:  1.0000
  Top-5:  1.0000
  Top-10: 1.0000
  MRR:    0.7500
```

Usage:

```text
records: 4
total tokens: 99326
avg tokens/call: 24831.5
total duration seconds: 70.298
avg duration seconds/call: 17.575
```

Interpretation:

- On this second fresh slice, cost-control v2 selected only 4/8 cases and DeepSeek moved all four selected cases to rank 1.
- The merged result improves Top-1 by 0.5000, Top-3 by 0.5000, Top-5 by 0.2500, and MRR by 0.4118 over focused hybrid/direct.
- This is a strong positive fresh-validation result for targeted rerank, but v2 remains experimental because its rules were developed after inspecting earlier fresh behavior.

## 2026-06-01 - Closure fresh validation 21..30

Goal:

- Validate Closure retrieval and selector behavior on a fresh slice.
- Check whether pass-chain hints generalize beyond the earlier targeted `Closure-13` case.
- Run selected DeepSeek rerank only after confirming candidate recall and selector coverage.

Dataset:

```text
requested: Closure-21..30
built: 10 records
skipped: none
```

Commands:

```bash
python3 scripts/build_defects4j_dataset.py \
  --project Closure \
  --bugs 21-30 \
  --out data/defects4j/closure_fresh_21_30.jsonl \
  --skip-failures

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

Retrieval result:

```text
focused direct and direct+pass-chain were identical on this slice:
Top-1:  0.4000
Top-3:  0.6000
Top-5:  0.7000
Top-10: 0.9000
Top-20: 0.9000
Top-50: 1.0000
MRR:    0.5553
```

Per-bug ranks:

```text
Closure-21: 6
Closure-22: 6
Closure-23: 1
Closure-24: 1
Closure-25: 1
Closure-26: 5
Closure-27: 1
Closure-28: 50
Closure-29: 2
Closure-30: 2
```

Selector:

```text
default selector selected 7 / 10:
Closure-21, Closure-22, Closure-23, Closure-26, Closure-28, Closure-29, Closure-30

Top-1 miss coverage: 6 / 6
Top-3 miss coverage: 4 / 4
Top-5 miss coverage: 3 / 3
```

Tighter selector without `top1_without_direct_hint`:

```text
selected 2 / 10:
Closure-23, Closure-28
```

Interpretation before LLM:

- Candidate recall@50 is strong enough for rerank.
- Pass-chain did not improve aggregate retrieval metrics on this fresh slice.
- The default selector covers all hard retrieval misses but is expensive at 70% selected.
- The tighter selector is too conservative because it misses `Closure-21` and `Closure-22`.

Selected DeepSeek rerank:

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

Selected-case result:

```text
bugs: 7
Top-1: 1.0000
Top-3: 1.0000
Top-5: 1.0000
Top-10: 1.0000
MRR:   1.0000
```

Merged result over all 10 records:

```text
Top-1:  1.0000
Top-3:  1.0000
Top-5:  1.0000
Top-10: 1.0000
MRR:    1.0000
```

Usage:

```text
LLM calls: 7
total tokens: 275689
avg tokens/call: 39384.1
total duration seconds: 114.110
avg duration seconds/call: 16.301
```

Outputs:

```text
docs/closure_fresh_21_30_validation_report.md
data/defects4j/closure_fresh_21_30.jsonl
outputs/closure_fresh_21_30_hybrid_focused_direct_top50.jsonl
outputs/closure_fresh_21_30_hybrid_focused_direct_passchain_top50.jsonl
outputs/closure_fresh_21_30_selector.json
outputs/closure_fresh_21_30_selector_no_top1_without_direct.json
outputs/closure_fresh_21_30_rerank_deepseek_default_selector_s6_ctx12000_top50.jsonl
outputs/closure_fresh_21_30_merged_deepseek_default_selector_s6_ctx12000_top50.jsonl
outputs/closure_fresh_21_30_merged_deepseek_default_selector_s6_ctx12000_top50_eval.json
outputs/closure_fresh_21_30_rerank_deepseek_default_selector_s6_ctx12000_top50_usage.json
```

Decision:

- Keep this as a positive fresh-validation result for evidence-aware rerank on Closure.
- Do not claim pass-chain generalized from this slice; it did not improve fresh retrieval metrics here.
- Next Closure work should reduce selector cost while preserving coverage of `Closure-21`, `Closure-22`, and `Closure-28`.

Closure selector cost-control follow-up:

- Added optional selector parameters:

```text
--top1-without-direct-min-direct-rank
--top1-without-direct-max-direct-rank
```

- Defaults preserve existing selector behavior.
- Regression command preserved default selected ids:

```text
Closure-21,Closure-22,Closure-23,Closure-26,Closure-28,Closure-29,Closure-30
```

Cost-control command:

```bash
python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/closure_fresh_21_30.jsonl \
  --pred outputs/closure_fresh_21_30_hybrid_focused_direct_passchain_top50.jsonl \
  --out outputs/closure_fresh_21_30_selector_direct_rank_3_6_no_patterns.json \
  --top1-without-direct-min-direct-rank 3 \
  --top1-without-direct-max-direct-rank 6 \
  --no-patterns
```

Cost-control selector result:

```text
selected: 4 / 10
selected ids: Closure-21, Closure-22, Closure-26, Closure-28
Top-3 miss coverage: 4 / 4
Top-5 miss coverage: 3 / 3
```

Merged result reusing existing DeepSeek calls for those 4 ids:

```text
Top-1:  0.8000
Top-3:  1.0000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.9000
```

Estimated 4-call usage:

```text
total tokens: 159898
avg tokens/call: 39974.5
total duration seconds: 65.553
avg duration seconds/call: 16.388
```

Interpretation:

- The 4-call selector is a better cost-control candidate than the 7-call default selector for this fresh slice.
- It preserves Top-3/Top-5 1.0000 while accepting that `Closure-29` and `Closure-30` stay rank 2.
- The direct-rank window rule was derived from this slice, so it needs another held-out Closure slice before becoming a stable rule.

## 2026-06-01 - Closure fresh validation 31..40

Goal:

- Validate whether the `Closure-21..30` direct-rank cost-control selector generalizes to a second fresh Closure slice.
- Stop before DeepSeek calls unless candidate recall and selector coverage are good enough.

Dataset:

```text
requested: Closure-31..40
built: 10 records
skipped: none
```

Retrieval:

```text
focused direct:
  Top-1:  0.2000
  Top-3:  0.3000
  Top-5:  0.4000
  Top-10: 0.7000
  Top-20: 0.8000
  Top-50: 0.8000
  MRR:    0.3185

focused direct + pass-chain:
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
Closure-31: 4
Closure-32: 1
Closure-33: top50 miss
Closure-34: 1
Closure-35: 18
Closure-36: 42
Closure-37: 7
Closure-38: 2
Closure-39: 9
Closure-40: 8
```

Default selector:

```text
selected: 6 / 10
selected ids: Closure-31, Closure-34, Closure-36, Closure-37, Closure-39, Closure-40
Top-1 miss coverage: 5 / 8
Top-3 miss coverage: 5 / 7
Top-5 miss coverage: 4 / 6
Top-10 miss coverage: 1 / 3
Top-50 miss coverage: 0 / 1
```

Direct-rank 3..6 no-pattern selector:

```text
selected: 2 / 10
selected ids: Closure-34, Closure-37
Top-5 miss coverage: 1 / 6
```

Decision:

- Do not run DeepSeek on this slice yet.
- The direct-rank cost-control rule from `Closure-21..30` does not generalize.
- The default selector is better but still misses important hard cases: `Closure-33` is absent from top50, and `Closure-35` is rank 18 but unselected.
- Next Closure work should target retrieval/selector diagnostics for JSType / `PrototypeObjectType` and `TypeInference` failures, possibly with top80/top100 candidate pools.

New doc:

```text
docs/closure_fresh_31_40_validation_report.md
```

Closure type-system retrieval follow-up:

- Added explicit retrieval flag:

```text
--force-type-system-hints
```

- This is disabled by default.
- It boosts Closure type-system candidates only for TypeCheck/type-mismatch evidence.

Type-system retrieval on `Closure-31..40`:

```text
Top-1:  0.2000
Top-3:  0.3000
Top-5:  0.5000
Top-10: 0.8000
Top-20: 0.9000
Top-50: 1.0000
MRR:    0.3486
```

Key changes:

```text
Closure-33 PrototypeObjectType.java: top50 miss -> rank 12
Closure-35 TypeInference.java:      rank 18 -> rank 4
Closure-36 InlineVariables.java:    rank 42, unchanged
```

Regression check on `Closure-21..30`:

```text
No aggregate metric change.
```

Selector follow-up:

- Added `pattern:type_system` when prediction output contains a high-confidence type-system hint.
- On `Closure-31..40`, type-system selector selected:

```text
Closure-31, Closure-33, Closure-34, Closure-35, Closure-36, Closure-37, Closure-39, Closure-40
```

Coverage:

```text
Top-3 miss coverage: 7 / 7
Top-5 miss coverage: 5 / 5
Top-10 miss coverage: 2 / 2
```

DeepSeek selected rerank:

```text
Initial selected-case result:
  Top-1:  0.2500
  Top-3:  0.3750
  Top-5:  0.7500
  Top-10: 0.8750
  MRR:    0.4208

Initial merged result:
  Top-1:  0.3000
  Top-3:  0.5000
  Top-5:  0.8000
  Top-10: 0.9000
  MRR:    0.4867
```

Hard2 wider-snippet diagnostic:

```text
Closure-33: rank 6 -> rank 5
Closure-36: top10 miss -> rank 8
```

Merged result with hard2 replacements:

```text
Top-1:  0.3000
Top-3:  0.5000
Top-5:  0.9000
Top-10: 1.0000
MRR:    0.5025
```

Deployment-equivalent usage:

```text
LLM calls: 8
total tokens: 286216
avg tokens/call: 35777.0
total duration seconds: 169.902
avg duration seconds/call: 21.238
```

Decision:

- Type-system retrieval is worth keeping as an explicit diagnostic/experimental Closure option.
- It fixes the candidate recall gap for `Closure-33` and improves `Closure-35`.
- At this point rerank still struggled with `Closure-36`, indicating an evidence-quality issue rather than a retrieval issue. This was superseded by the singleton/getter snippet fix below.
- This is not yet a cost-controlled production Closure selector because selected ratio is 8/10.

## 2026-06-01 - Closure 31..40 singleton getter snippet fix

Goal:

- Diagnose and fix the remaining `Closure-36` rerank/evidence miss from the type-system selector run.

Finding:

- `InlineVariables.java` was already in the Closure-36 candidate pool, but its prompt snippet did not include the strongest local evidence:

```text
// issue 668: Don't inline singleton getter methods
```

- The snippet extractor skipped all comment lines before scoring them, so high-signal comments could not be selected even when the test context contained `testSingletonGetter1`, `goog.addSingletonGetter`, and `getInstance`.

Code change:

```text
src/fl_localizer/snippets.py
```

- Added high-signal terms for `addsingletongetter`, `getter`, `getinstance`, and `singleton`.
- Changed snippet scoring to compute line terms before comment filtering.
- Kept comment lines only when they match high-signal terms.
- Widened context around singleton/getter evidence.

Dry-run prompt check:

```text
outputs/prompts_closure_fresh_31_40_typesystem_closure36_snippet_fix_s12/Closure-36_rerank_prompt.json
```

Confirmed that `InlineVariables.java` now exposes lines 569-574, including the issue-668 singleton getter comment.

DeepSeek single-case validation:

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
Closure-36 InlineVariables.java: rank 8 -> rank 1
tokens: 35706
duration seconds: 17.317
```

Final selected-case result after replacing `Closure-36` with the snippet-fix call and keeping the hard2 `Closure-33` call:

```text
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

Deployment-equivalent usage:

```text
LLM calls: 8
total tokens: 284148
avg tokens/call: 35518.5
total duration seconds: 163.655
avg duration seconds/call: 20.457
```

Outputs:

```text
outputs/closure_fresh_31_40_rerank_deepseek_typesystem_selector_plus_snippetfix_s12.jsonl
outputs/closure_fresh_31_40_rerank_deepseek_typesystem_selector_plus_snippetfix_s12_eval.json
outputs/closure_fresh_31_40_merged_deepseek_typesystem_selector_plus_snippetfix_s12.jsonl
outputs/closure_fresh_31_40_merged_deepseek_typesystem_selector_plus_snippetfix_s12_eval.json
```

Decision:

- `Closure-36` is fixed as an evidence-quality issue.
- The fresh `Closure-31..40` diagnostic now reaches Top-5/Top-10 1.0000, but still uses 8/10 selected calls and should not be treated as a final cost-controlled selector.

Regression check:

- No pytest/test package was present in `fl-localizer`, so this used dry-run prompt generation only.
- Generated prompts:

```text
outputs/prompts_snippetfix_regression_math12_m14
outputs/prompts_snippetfix_regression_closure_c4_c13
outputs/prompts_snippetfix_regression_mockito_m20
```

- `Math-12` still exposes `BitsStreamGenerator.java` with `nextGaussian` and `clear()`.
- `Closure-4` still exposes `PrototypeObjectType.java` and the cycle/subtype failure context.
- `Closure-13` still exposes `PeepholeOptimizationsPass.java` with `pass_chain_hint:DefaultPassConfig->PeepholeOptimizationsPass`.
- `Mockito-20` still exposes `ByteBuddyMockMaker.java` with mock instance instantiation evidence.

Cost-control diagnostic:

- Built an in-slice 5-call diagnostic selector with only:

```text
Closure-33, Closure-36, Closure-37, Closure-39, Closure-40
```

- This preserves the 8-call final merged metrics:

```text
Top-1:  0.4000
Top-3:  0.6000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.5900
```

- Usage drops from 8 calls / 284148 tokens to:

```text
LLM calls: 5
total tokens: 176983
avg tokens/call: 35396.6
total duration seconds: 111.245
avg duration seconds/call: 22.249
```

Output:

```text
outputs/closure_fresh_31_40_selector_typesystem_cost_gate_diagnostic5.json
outputs/closure_fresh_31_40_merged_deepseek_typesystem_cost_gate_diagnostic5_snippetfix_s12.jsonl
outputs/closure_fresh_31_40_merged_deepseek_typesystem_cost_gate_diagnostic5_snippetfix_s12_eval.json
```

Important caveat:

- At this point the 5-call gate was only a cost-control upper bound. The next section converts it into an explicit selector flag and checks it against `Closure-21..30`.

## 2026-06-01 - Closure cost-control v1 selector

Goal:

- Turn the `Closure-31..40` 5-call diagnostic gate into an explicit non-oracle selector option and check it against both Closure fresh slices.

Code change:

```text
scripts/select_rerank_candidates.py
```

- Added `--closure-cost-control-v1`.
- The rule filters Closure selector reasons using only retrieval/bug-text signals:
  - keep low score-ratio only when top-1 lacks a direct hint;
  - keep `top1_without_direct_hint` when the first direct hint is missing or rank >= 3;
  - keep high direct-hint-count records;
  - keep pass-chain records when top-1 lacks a direct hint, direct-hint count is high, or score ratio is at least 1.40;
  - keep type-system records when score ratio is at most 1.10 or top-1 lacks a direct hint;
  - keep type-cycle records when top-1 lacks a direct hint.

Selector outputs:

```text
outputs/closure_fresh_21_30_selector_closure_cost_control_v1.json
outputs/closure_fresh_31_40_selector_closure_cost_control_v1.json
```

Selected ids:

```text
Closure-21..30:
Closure-21, Closure-22, Closure-26, Closure-28

Closure-31..40:
Closure-33, Closure-36, Closure-37, Closure-39, Closure-40
```

Merged results:

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

Closure-21..40 combined, 9 / 20 calls:
Top-1:  0.6000
Top-3:  0.8000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.7450
tokens: 336881
seconds: 176.798
```

Outputs:

```text
outputs/closure_fresh_21_30_merged_deepseek_closure_cost_control_v1_s6_ctx12000_top50.jsonl
outputs/closure_fresh_21_30_merged_deepseek_closure_cost_control_v1_s6_ctx12000_top50_eval.json
outputs/closure_fresh_31_40_merged_deepseek_closure_cost_control_v1_snippetfix_s12.jsonl
outputs/closure_fresh_31_40_merged_deepseek_closure_cost_control_v1_snippetfix_s12_eval.json
outputs/closure_fresh_21_40_merged_deepseek_closure_cost_control_v1.jsonl
outputs/closure_fresh_21_40_merged_deepseek_closure_cost_control_v1_eval.json
```

Decision:

- This is now a reusable experimental Closure selector rather than a pure post-hoc gate.
- It preserves Top-3/Top-5/Top-10 on both fresh slices while cutting calls from 15/20 default/type-system selected cases to 9/20.
- It should still be reported as experimental because it has only been checked on `Closure-21..40`.

## 2026-06-01 - Closure fresh validation 41..50 and cost-control v2

Goal:

- Validate Closure cost-control on a third fresh slice and only expand the selector where the new slice exposes non-oracle coverage gaps.

Dataset:

```text
python3 scripts/build_defects4j_dataset.py --project Closure --bugs 41-50 --out data/defects4j/closure_fresh_41_50.jsonl --skip-failures
```

Records: 10.

Focused direct/pass-chain/type-system retrieval:

```text
Top-1:  0.2000
Top-3:  0.4000
Top-5:  0.5000
Top-10: 0.6000
Top-20: 0.8000
Top-50: 1.0000
MRR:    0.3154
```

Baseline ground-truth ranks:

```text
Closure-41 rank 40
Closure-42 rank 3
Closure-43 rank 5
Closure-44 rank 14
Closure-45 rank 10
Closure-46 rank 3
Closure-47 rank 1
Closure-48 rank 15
Closure-49 rank 42
Closure-50 rank 1
```

Selector update:

- `--closure-cost-control-v1` selected `Closure-41, Closure-42, Closure-48, Closure-49`, missing `Closure-44` and `Closure-45`.
- Added `--closure-cost-control-v2`.
- V2 keeps the v1 sets unchanged on `Closure-21..30` and `Closure-31..40`.
- V2 selected `Closure-41, Closure-42, Closure-44, Closure-45, Closure-48, Closure-49` on `Closure-41..50`.
- New v2 pattern reasons:
  - `pattern:closure_code_output`
  - `pattern:closure_deep_specific_direct_hint`

Code/evidence updates:

```text
scripts/select_rerank_candidates.py
src/fl_localizer/snippets.py
scripts/run_llm_rerank.py
```

- Added v2 selection logic.
- Added property/prototype declaration snippet terms.
- Added property-function semantic evidence injection for rerank prompts.

DeepSeek selected-case result:

```text
selected: 6 / 10
Top-1:  0.3333
Top-3:  0.6667
Top-5:  0.8333
Top-10: 1.0000
MRR:    0.5347
tokens: 242877
seconds: 135.602
```

Merged `Closure-41..50` result:

```text
Top-1:  0.4000
Top-3:  0.7000
Top-5:  0.9000
Top-10: 1.0000
MRR:    0.5742
```

Merged ranks:

```text
Closure-41 rank 4
Closure-42 rank 1
Closure-43 rank 5
Closure-44 rank 3
Closure-45 rank 1
Closure-46 rank 3
Closure-47 rank 1
Closure-48 rank 8
Closure-49 rank 2
Closure-50 rank 1
```

`Closure-48` diagnostic:

- The main v2 rerank moved `TypedScopeCreator.java` from baseline rank 15 to rank 8.
- A wider property/prototype diagnostic consumed 43436 extra tokens and moved it to rank 9, so it was not merged.
- The remaining miss is model attribution ambiguity: DeepSeek keeps ranking `TypeCheck.java` and `TypeInference.java` above `TypedScopeCreator.java`.

Combined `Closure-21..50`:

```text
baseline retrieval:
Top-1:  0.2667
Top-3:  0.4333
Top-5:  0.5667
Top-10: 0.7667
Top-20: 0.8667
Top-50: 1.0000
MRR:    0.4064

v2 merged, 15 / 30 calls:
Top-1:  0.5333
Top-3:  0.7667
Top-5:  0.9667
Top-10: 1.0000
Top-20: 1.0000
MRR:    0.6881
tokens: 579758
seconds: 312.400
```

Outputs:

```text
docs/closure_fresh_41_50_validation_report.md
docs/closure_cost_control_v2_report.md
outputs/closure_fresh_41_50_selector_closure_cost_control_v2.json
outputs/closure_fresh_41_50_rerank_deepseek_closure_cost_control_v2_s12_ctx12000_top50.jsonl
outputs/closure_fresh_41_50_merged_deepseek_closure_cost_control_v2_s12_ctx12000_top50.jsonl
outputs/closure_fresh_21_50_merged_deepseek_closure_cost_control_v2.jsonl
```

Decision:

- V2 is stronger than v1 on the new slice and does not increase earlier-slice calls.
- Across `Closure-21..50`, v2 reaches Top-5 0.9667 and Top-10 1.0000 with 15/30 calls.
- It remains an experimental Closure-only selector; `Closure-48` is the known unresolved Top-5 miss.

## 2026-06-01 - Closure fresh validation 51..60 and cost-control v3

Goal:

- Validate Closure cost-control on a fourth fresh slice and extend the selector only for new non-oracle miss patterns.

Dataset:

```text
python3 scripts/build_defects4j_dataset.py --project Closure --bugs 51-60 --out data/defects4j/closure_fresh_51_60.jsonl --skip-failures
```

Records: 10.

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

Baseline ground-truth ranks:

```text
Closure-51 rank 21
Closure-52 rank 12
Closure-53 rank 1
Closure-54 rank 5
Closure-55 rank 30
Closure-56 rank 27
Closure-57 rank 1
Closure-58 rank 1
Closure-59 rank 4
Closure-60 rank 1
```

Selector update:

- `--closure-cost-control-v2` selected `Closure-51, Closure-54, Closure-56`, missing `Closure-52` and `Closure-55`.
- Added `--closure-cost-control-v3`.
- V3 keeps the selected sets unchanged on `Closure-21..50`.
- V3 selected `Closure-51, Closure-52, Closure-54, Closure-55, Closure-56` on `Closure-51..60`.
- New v3 pattern reasons:
  - `pattern:closure_code_generator_output`
  - `pattern:closure_validator_transform_failure`

Code/evidence updates:

```text
scripts/select_rerank_candidates.py
src/fl_localizer/snippets.py
src/fl_localizer/prompts.py
```

- Added v3 selector logic.
- Added numeric output snippet terms so `CodeConsumer.addNumber` is exposed for negative-zero output failures.
- Added a code-printer numeric-output rerank rule.

DeepSeek result:

```text
selected: 5 / 10
Top-1:  0.8000
Top-3:  1.0000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.9000
tokens: 186961
seconds: 125.958
```

Merged `Closure-51..60` result:

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
Closure-51 rank 1
Closure-52 rank 1
Closure-53 rank 1
Closure-54 rank 2
Closure-55 rank 1
Closure-56 rank 1
Closure-57 rank 1
Closure-58 rank 1
Closure-59 rank 4
Closure-60 rank 1
```

`Closure-51` diagnostic:

- Initial v3 s12 rerank missed `CodeConsumer.java` because the snippet did not expose `addNumber(double x)`.
- Numeric-output snippet support plus a 20-line single-case rerun moved `CodeConsumer.java` to rank 1.
- Deployment-equivalent usage uses the successful `Closure-51` rerun and excludes the superseded first `Closure-51` call. Actual exploration spent 31956 extra tokens on that superseded call.

Combined `Closure-21..60`:

```text
baseline retrieval:
Top-1:  0.3000
Top-3:  0.4250
Top-5:  0.5750
Top-10: 0.7250
Top-20: 0.8250
Top-50: 1.0000
MRR:    0.4211

v3 merged, 20 / 40 calls:
Top-1:  0.6000
Top-3:  0.8000
Top-5:  0.9750
Top-10: 1.0000
Top-20: 1.0000
MRR:    0.7348
tokens: 766719
seconds: 438.358
```

Outputs:

```text
docs/closure_fresh_51_60_validation_report.md
docs/closure_cost_control_v3_report.md
outputs/closure_fresh_51_60_selector_closure_cost_control_v3.json
outputs/closure_fresh_51_60_rerank_deepseek_closure_cost_control_v3_plus_closure51_numeric_s20_ctx12000_top50.jsonl
outputs/closure_fresh_51_60_merged_deepseek_closure_cost_control_v3_plus_closure51_numeric_s20_ctx12000_top50.jsonl
outputs/closure_fresh_21_60_merged_deepseek_closure_cost_control_v3_plus_closure51_numeric.jsonl
```

Decision:

- V3 is stronger than v2 on the new slice and does not increase earlier-slice calls.
- Across `Closure-21..60`, v3 reaches Top-5 0.9750 and Top-10 1.0000 with 20/40 calls.
- It remains an experimental Closure-only selector; `Closure-48` is still the known unresolved Top-5 miss.

## 2026-06-01 - Frozen held-out Closure 61..80 validation

Goal:

- Freeze the next held-out protocol before looking at results.
- Validate the current Closure cost-control v3 pipeline on a new held-out slice.
- Do not tune selector, retrieval, prompt, or snippet rules based on this run.

Protocol:

```text
docs/frozen_protocol_2026-06-01.md
```

Dataset:

```text
requested: Closure-61..80
built: 19 records
skipped: Closure-63, not listed in active-bugs.csv
```

Data output:

```text
data/defects4j/closure_heldout_61_80.jsonl
```

Frozen retrieval:

```bash
python3 scripts/run_hybrid_retrieval.py \
  --bugs data/defects4j/closure_heldout_61_80.jsonl \
  --out outputs/closure_heldout_61_80_hybrid_focused_direct_passchain_typesystem_top50.jsonl \
  --top-k 50 \
  --force-direct-hints \
  --force-pass-chain-hints \
  --force-type-system-hints
```

Retrieval result:

```text
bugs:   19
Top-1:  0.4737
Top-3:  0.4737
Top-5:  0.5789
Top-10: 0.7368
Top-20: 0.8947
Top-50: 1.0000
MRR:    0.5344
```

Baseline ranks:

```text
Closure-61: 8
Closure-62: 1
Closure-64: 4
Closure-65: 8
Closure-66: 1
Closure-67: 48
Closure-68: 1
Closure-69: 1
Closure-70: 14
Closure-71: 1
Closure-72: 12
Closure-73: 4
Closure-74: 1
Closure-75: 21
Closure-76: 18
Closure-77: 8
Closure-78: 1
Closure-79: 1
Closure-80: 1
```

Frozen selector:

```bash
python3 scripts/select_rerank_candidates.py \
  --bugs data/defects4j/closure_heldout_61_80.jsonl \
  --pred outputs/closure_heldout_61_80_hybrid_focused_direct_passchain_typesystem_top50.jsonl \
  --out outputs/closure_heldout_61_80_selector_closure_cost_control_v3.json \
  --closure-cost-control-v3
```

Selected:

```text
selected: 6 / 19
selected ids: Closure-64, Closure-69, Closure-70, Closure-72, Closure-76, Closure-77

reason counts:
low_score_ratio<=1.02: 1
pattern:closure_code_output: 1
pattern:closure_deep_specific_direct_hint: 2
pattern:type_system: 2
```

Selector false negatives before LLM:

```text
Closure-61 baseline rank 8
Closure-65 baseline rank 8
Closure-67 baseline rank 48
Closure-75 baseline rank 21
```

These are recorded for error analysis only. They were not used to tune this held-out run.

DeepSeek selected-case rerank:

```bash
DEEPSEEK_TIMEOUT=600 python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/closure_heldout_61_80.jsonl \
  --bm25 outputs/closure_heldout_61_80_hybrid_focused_direct_passchain_typesystem_top50.jsonl \
  --out outputs/closure_heldout_61_80_rerank_deepseek_closure_cost_control_v3_s12_ctx12000_top50.jsonl \
  --provider deepseek \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 12 \
  --include-retrieval-evidence \
  --include-test-context \
  --max-test-context-chars 12000 \
  --bug-ids Closure-64,Closure-69,Closure-70,Closure-72,Closure-76,Closure-77 \
  --prompt-dir outputs/prompts_closure_heldout_61_80_cost_control_v3_s12_ctx12000_top50
```

Execution note:

- The first attempts hit DeepSeek read timeouts before writing output.
- Added `DEEPSEEK_TIMEOUT` support in `src/fl_localizer/llm_client.py`.
- Added incremental JSONL writing after each successful record in `scripts/run_llm_rerank.py`.
- These were execution robustness changes, not method changes.

Selected-case result:

```text
bugs:   6
Top-1:  0.6667
Top-3:  1.0000
Top-5:  1.0000
Top-10: 1.0000
MRR:    0.8056
```

Selected rank changes:

```text
Closure-64: 4  -> 2
Closure-69: 1  -> 1
Closure-70: 14 -> 3
Closure-72: 12 -> 1
Closure-76: 18 -> 1
Closure-77: 8  -> 1
```

Usage:

```text
records: 6
total_tokens: 225551
avg_total_tokens: 37591.83
total_duration_seconds: 106.985
avg_duration_seconds: 17.831
```

Merged result:

```text
Top-1:  0.6316
Top-3:  0.7368
Top-5:  0.7895
Top-10: 0.8947
MRR:    0.7018
```

Improvement over frozen retrieval:

```text
Top-1:  +0.1579
Top-3:  +0.2632
Top-5:  +0.2105
Top-10: +0.1579
MRR:    +0.1673
```

Important metric note:

- The merged main-method output is intentionally truncated to Top-10.
- Use retrieval output for Candidate Recall@20 and Recall@50.
- Do not interpret merged Top-20/Top-50 as candidate recall.

Outputs:

```text
docs/closure_heldout_61_80_validation_report.md
outputs/closure_heldout_61_80_hybrid_focused_direct_passchain_typesystem_top50.jsonl
outputs/closure_heldout_61_80_hybrid_focused_direct_passchain_typesystem_top50_eval.json
outputs/closure_heldout_61_80_selector_closure_cost_control_v3.json
outputs/closure_heldout_61_80_rerank_deepseek_closure_cost_control_v3_s12_ctx12000_top50.jsonl
outputs/closure_heldout_61_80_rerank_deepseek_closure_cost_control_v3_s12_ctx12000_top50_eval.json
outputs/closure_heldout_61_80_rerank_deepseek_closure_cost_control_v3_s12_ctx12000_top50_usage.json
outputs/closure_heldout_61_80_merged_deepseek_closure_cost_control_v3_s12_ctx12000_top50.jsonl
outputs/closure_heldout_61_80_merged_deepseek_closure_cost_control_v3_s12_ctx12000_top50_eval.json
```

Decision:

- This is a positive held-out validation for selected-case rerank behavior and overall Top-k improvement.
- The main limitation is selector recall. It missed four baseline Top-5 failures, especially `Closure-67` and `Closure-75`.
- Do not tune on this run. Use these failures to design a later frozen protocol.

## 2026-06-02 - Results Draft And Held-Out Error Analysis

Continued third-stage reporting work after integrating the held-out metrics into the current result and experiment design docs.

Added:

```text
docs/results_chapter_draft_2026-06-02.md
docs/closure_heldout_61_80_selector_error_analysis.md
```

Key points:

- Converted pilot, fresh, and frozen held-out results into a thesis-style results draft.
- Marked `Closure-61..80` as the first explicitly frozen held-out protocol.
- Separated reportable held-out metrics from post-hoc error analysis.
- Analyzed selector false negatives without changing retrieval, selector, prompt, or rerank rules.

Selector error-analysis summary:

```text
baseline Top-5 failures: 8
selected among those failures: 4
missed among those failures: Closure-61, Closure-65, Closure-67, Closure-75
most important misses: Closure-67 rank 48, Closure-75 rank 21
```

Interpretation:

- Selected-case rerank quality is strong: all selected held-out cases reached Top-3.
- The next improvement should be selector recall under a new frozen protocol, not tuning on `Closure-61..80`.
