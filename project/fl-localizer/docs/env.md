# Environment Setup

This project uses two separate environments:

1. Defects4J environment for benchmark checkout, compile, test, and metadata export.
2. LLM provider environment for reranking candidates with DeepSeek API or Codex backend.

## Defects4J

Load the prepared Defects4J environment before running benchmark scripts:

```bash
source /Users/jin/llm_location/project/defects4j-env.sh
```

This sets:

```bash
DEFECTS4J_HOME=/Users/jin/llm_location/project/defects4j
PATH=$DEFECTS4J_HOME/framework/bin:/opt/homebrew/opt/openjdk@11/bin:/opt/homebrew/bin:$PATH
PERL5LIB=$DEFECTS4J_HOME/local/perl5/lib/perl5:$PERL5LIB
TZ=America/Los_Angeles
```

Smoke test:

```bash
defects4j info -p Lang -b 1
```

## DeepSeek API

DeepSeek is the planned provider for batch reranking experiments because it is API-based and easier to record/reproduce.

Set the key in your shell:

```bash
export DEEPSEEK_API_KEY="your_deepseek_key"
```

Recommended default model:

```bash
export DEEPSEEK_MODEL="deepseek-v4-flash"
```

Run a small smoke test first:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/lang_pilot_20.jsonl \
  --bm25 outputs/lang_pilot_20_bm25_top50.jsonl \
  --out outputs/lang_pilot_20_rerank_deepseek_smoke.jsonl \
  --provider deepseek \
  --model deepseek-v4-flash \
  --top-candidates 20 \
  --top-output 10 \
  --max-snippet-lines 12 \
  --limit 3
```

Then evaluate:

```bash
python3 scripts/evaluate_predictions.py \
  --bugs data/defects4j/lang_pilot_20.jsonl \
  --pred outputs/lang_pilot_20_rerank_deepseek_smoke.jsonl \
  --per-bug
```

Full Lang-20 run:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/lang_pilot_20.jsonl \
  --bm25 outputs/lang_pilot_20_bm25_top50.jsonl \
  --out outputs/lang_pilot_20_rerank_deepseek.jsonl \
  --provider deepseek \
  --model deepseek-v4-flash \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 12
```

## Codex Backend

Codex backend is useful for small sanity checks and qualitative comparison. It is not the primary batch provider.

The current sandbox may block Codex backend initialization. If that happens, run the same command with elevated execution approval.

Smoke test:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/lang_pilot_20.jsonl \
  --bm25 outputs/lang_pilot_20_bm25_top50.jsonl \
  --out outputs/lang_pilot_20_rerank_codex_smoke.jsonl \
  --provider codex \
  --top-candidates 10 \
  --top-output 5 \
  --max-snippet-lines 8 \
  --limit 1
```

## Dry Run

Use dry-run to generate prompts without calling any model:

```bash
python3 scripts/run_llm_rerank.py \
  --bugs data/defects4j/lang_pilot_20.jsonl \
  --bm25 outputs/lang_pilot_20_bm25_top50.jsonl \
  --out outputs/lang_pilot_20_rerank_dryrun_top50.jsonl \
  --provider dry-run \
  --top-candidates 50 \
  --top-output 10 \
  --max-snippet-lines 12
```

Generated prompts are written to:

```text
outputs/prompts/
```

## Data Leakage Rule

Model prompts may include:

- bug report id/text
- triggering test
- stack trace
- candidate source file summaries/snippets from the buggy version
- BM25 rank and score

Model prompts must not include:

- `ground_truth`
- fixed source code
- fixing commit diff
- changed files/classes from the fixing commit
- `classes.modified` as model input

