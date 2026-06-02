# Thesis Experiment Plan: Benchmark Validation + Company Case Study

**Working title:** LLM-Based / Agentic Fault Localization in Benchmarks and Real-World Repository Settings  
**Author:** Ziniu Jin  
**Supervisor context:** This plan follows the agreed direction: first validate the approach on established benchmarks, then evaluate it on company/Capstone data as a real-world case study.  
**Date:** 2026-05-24

---

## 1. One-Page Summary

The thesis should be designed as a two-part evaluation:

1. **Benchmark validation**: run the proposed LLM-based fault localization approach on a standard benchmark, preferably **Defects4J**, to show that the approach works under controlled and comparable conditions.
2. **Company / Capstone case study**: apply the same approach to a real-world project where bug information comes from heterogeneous sources such as Jira, Bitbucket, website reports, logs, CI failures, source-code structure, and developer notes.

The key point is **not** to argue that benchmarks are useless. Benchmarks are necessary for comparability. The thesis argument should be:

> Benchmarks are necessary for controlled validation, but they are not sufficient to show how the approach behaves in real development environments. Therefore, this thesis combines benchmark-based validation with a real-world company case study.

The core experimental question is:

> Can an LLM-based, context-aware fault localization pipeline identify the correct faulty files or methods, and how do different context sources and an independent verification agent affect localization accuracy?

---

## 2. Research Problem

Existing LLM-based fault localization studies show promising results on academic benchmarks such as Defects4J. However, real-world software development is less structured than benchmark settings. In company or Capstone projects, bug-related information may be spread across different systems:

- Jira / issue tracker
- Bitbucket / Git repository
- Pull requests or fixing commits
- CI logs
- stack traces
- test failures
- website or user-facing bug reports
- project documentation
- frontend/backend/service architecture
- informal developer notes

Therefore, the thesis should study whether a context-aware LLM pipeline can use these heterogeneous information sources to improve fault localization.

---

## 3. Research Questions

### RQ1 — Benchmark Performance

**RQ1: How accurately can the proposed LLM-based fault localization approach identify faulty files or methods on established benchmarks?**

Purpose:

- Validate the approach under controlled conditions.
- Make the result comparable with prior fault localization research.
- Avoid relying only on a small company case study.

Primary dataset:

- Defects4J

Metrics:

- File-level Top-1 / Top-3 / Top-5 accuracy
- Method-level Top-1 / Top-3 / Top-5 accuracy, if feasible
- MRR
- Cost: tokens, number of LLM calls, runtime

---

### RQ2 — Context Effect

**RQ2: How does the amount and type of context affect LLM-based fault localization accuracy?**

Purpose:

- Test whether adding repository structure, retrieved code, logs, stack traces, or test failure information improves localization.
- This is one of the main thesis contributions.

Context variants:

| Variant | Bug report | Repo structure | Retrieved source code | Logs / stack trace / tests | Verifier |
|---|---:|---:|---:|---:|---:|
| V0 IR baseline | ✓ | index only | index only | optional | ✗ |
| V1 LLM-basic | ✓ | ✗ | ✗ | ✗ | ✗ |
| V2 LLM + structure | ✓ | ✓ | ✗ | ✗ | ✗ |
| V3 LLM + retrieved code | ✓ | ✓ | ✓ | ✗ | ✗ |
| V4 LLM + runtime evidence | ✓ | ✓ | ✓ | ✓ | ✗ |
| V5 Full agentic pipeline | ✓ | ✓ | ✓ | ✓ | ✓ |

---

### RQ3 — Verification Agent Effect

**RQ3: Does an independent verification agent improve the reliability of LLM-based fault localization?**

Purpose:

- Compare single-agent localization with localization + independent verification.
- Evaluate whether a second agent can re-rank or reject weak candidates.

Comparison:

| Setting | Description |
|---|---|
| Single-agent | One LLM ranks suspicious files/methods. |
| Agent + verifier | First LLM ranks candidates; second LLM checks evidence and re-ranks them. |

Metrics:

- Top-k improvement or degradation
- False-positive reduction
- Cost increase
- Failure cases where verifier removes or lowers the correct result

---

### RQ4 — Company / Capstone Applicability

**RQ4: How does the proposed approach perform in a real-world company or Capstone project where bug information comes from multiple sources?**

Purpose:

- Evaluate practical usefulness beyond benchmark conditions.
- Study what information sources are useful in real projects.
- Identify limitations caused by vague reports, noisy logs, large repositories, or incomplete ground truth.

Evaluation type:

- Small-scale case study
- Mixed quantitative and qualitative analysis

Expected size:

- Pilot: 3–5 real company/Capstone bugs
- Final thesis: 10–20 real company/Capstone bugs, if available

---

## 4. Data Sources

## 4.1 Primary Benchmark: Defects4J

**Recommended first benchmark:** Defects4J  
**Official link:** https://github.com/rjust/defects4j

Why Defects4J is the best first choice:

- It is widely used in fault localization, debugging, and automated program repair research.
- It contains reproducible Java bugs.
- Each bug has buggy and fixed versions.
- Bugs are fixed in a single commit.
- Bugs are fixed by modifying source code rather than only documentation, tests, or configuration.
- Triggering tests are available.
- Metadata can be obtained through the Defects4J CLI.

Recommended use in this thesis:

| Item | Plan |
|---|---|
| Role | Main benchmark validation |
| Language | Java |
| Initial pilot size | 20–30 bugs |
| Final size | 100–200 bugs if time allows |
| Ground truth | Source files/classes modified by the official fixing commit |
| Main metric | File-level Top-1 / Top-3 / Top-5 |
| Optional metric | Method-level Top-k |

Suggested first projects:

| Project ID | Project |
|---|---|
| Lang | Apache Commons Lang |
| Math | Apache Commons Math |
| Chart | JFreeChart |
| Time | Joda-Time |
| Mockito | Mockito |
| Closure | Google Closure Compiler |

Start with smaller and easier projects first, such as `Lang`, `Math`, `Time`, and `Chart`. Add `Closure` later because it is larger and may be harder for early pipeline debugging.

### Defects4J Setup Commands

```bash
git clone https://github.com/rjust/defects4j
cd defects4j
cpanm --installdeps .
./init.sh
export PATH=$PATH:$(pwd)/framework/bin
```

Check installation:

```bash
defects4j info -p Lang
```

Checkout one buggy version:

```bash
defects4j checkout -p Lang -v 1b -w /tmp/lang_1_buggy
cd /tmp/lang_1_buggy
defects4j compile
defects4j test
```

Useful metadata commands:

```bash
# Modified classes / source-level ground truth
defects4j export -p classes.modified

# Triggering tests
defects4j export -p tests.trigger

# Triggering tests with failure cause
defects4j export -p tests.trigger.cause

# Source directory
defects4j export -p dir.src.classes

# Test source directory
defects4j export -p dir.src.tests
```

Query metadata without checkout:

```bash
defects4j query -p Lang -q "bug.id,report.id,report.url,classes.modified,tests.trigger"
```

---

## 4.2 Optional Secondary Benchmark: Bench4BL

**Official link:** https://github.com/exatoa/Bench4BL

Bench4BL is useful if the thesis wants a dataset specifically designed for **bug report → source file localization**.

Why it is useful:

- It contains bug reports.
- Each bug report is mapped to corresponding source code files.
- It is closer to information-retrieval-based bug localization.

Recommended use:

| Item | Plan |
|---|---|
| Role | Optional secondary benchmark |
| Use case | Bug-report-based file localization |
| Strength | Good for comparing IR baseline vs LLM ranking |
| Weakness | More complex to set up and may contain old projects |

Recommendation:

- Do **not** start with Bench4BL.
- First make the pipeline work on Defects4J.
- Add Bench4BL only if there is enough time or if the supervisor asks for a more bug-report-centered benchmark.

---

## 4.3 Optional Recent Java Benchmark: GitBug-Java

**Official link:** https://github.com/gitbugactions/gitbug-java

GitBug-Java is useful because it contains more recent Java bugs and is designed with reproducibility in mind.

Recommended use:

| Item | Plan |
|---|---|
| Role | Optional robustness check |
| Strength | Recent Java bugs, closer to modern repositories |
| Weakness | Heavy setup; requires Docker/Poetry and large disk space |

Recommendation:

- Use only after Defects4J pilot succeeds.
- Mention it in the proposal as an optional extension, not as the first dataset.

---

## 4.4 Optional Python Benchmark: BugsInPy

**Official link:** https://github.com/soarsmu/BugsInPy

Use BugsInPy only if the company/Capstone project is mainly Python or if the thesis wants cross-language evaluation.

Recommendation:

- If the thesis remains Java-focused, skip BugsInPy.
- If the company project is Python, BugsInPy becomes a good benchmark alternative.

---

# 5. Company / Capstone Case Study Design

The company or Capstone case study is the practical evaluation part of the thesis.

The goal is not to replace benchmarks. The goal is to show how the same approach behaves when applied to a real project where information is distributed across multiple sources.

---

## 5.1 Role of the Company Case Study

| Aspect | Description |
|---|---|
| Purpose | Evaluate practical applicability in a real-world repository. |
| Data type | Real bugs from company/Capstone project. |
| Evaluation style | Case study with quantitative Top-k hit and qualitative analysis. |
| Thesis role | Separate chapter after benchmark experiment. |
| Main contribution | Shows how context sources affect localization in a realistic development setting. |

The case study should answer:

- Can the pipeline handle real bug reports?
- Which sources of information are useful?
- Does the pipeline still work when data is incomplete or noisy?
- What failure modes appear in real projects?
- How does the verifier behave in realistic settings?

---

## 5.2 Possible Company Data Sources

The company/Capstone dataset should collect bug information from the following sources where available:

| Source | Example | Use in pipeline |
|---|---|---|
| Jira / issue tracker | Bug title, description, comments, priority | Main bug report input |
| Bitbucket / Git | commits, branches, pull requests | Ground truth and repository history |
| Website / user report | User-facing description of failure | Extra symptom information |
| CI logs | failed build/test logs | Runtime evidence |
| Stack trace | exception class, file, line, method | Strong localization signal |
| Test failure | failing test name and assertion error | Runtime evidence |
| Repository structure | frontend/backend/service/module tree | Search space reduction |
| Documentation | API docs, architecture notes | Context enrichment |
| Developer notes | informal explanation from team | Case study explanation only, if allowed |

Important rule:

> The fixing commit, patch, or changed files must **not** be given to the localization agent. They are only used as ground truth for evaluation.

---

## 5.3 Privacy and Company Data Handling

Because company data may be sensitive, the thesis should include a clear data-handling protocol.

### Data that should be anonymized

- Company name, if required
- Customer names
- User emails
- internal URLs
- tokens, secrets, API keys
- private repository names
- production database names
- confidential business logic
- screenshots containing customer data

### Data that can usually be kept

- anonymized bug descriptions
- anonymized file paths, if allowed
- class/method names, if allowed
- stack trace structure, with sensitive values removed
- high-level architecture labels such as frontend, backend, API, database, service

### Suggested statement for thesis

> For the company case study, all bug reports, logs, and source-code references will be anonymized where necessary. Secrets, personal data, internal URLs, and customer-specific information will be removed. Fixing commits are used only to construct the evaluation ground truth and are not provided to the LLM during localization.

---

## 5.4 Company Bug Selection Criteria

Include bugs that satisfy most of the following:

| Inclusion criterion | Reason |
|---|---|
| Has a clear bug report or issue description | Needed as model input |
| Has a corresponding fixing commit or PR | Needed for ground truth |
| Fix modifies source code | Needed for fault localization |
| Bug is not only documentation/configuration | Keep the task source-code focused |
| Bug affects application behavior | Relevant to ordinary production bugs |
| Optional: has logs or stack trace | Useful for context ablation |
| Optional: has test failure | Useful for runtime evidence |

Exclude bugs with:

| Exclusion criterion | Reason |
|---|---|
| Huge refactoring commits | Fault location becomes ambiguous |
| Multiple unrelated bugs in one commit | Ground truth is not clean |
| Fix only changes docs/config/test snapshots | Not suitable for source-code localization |
| Missing repository version | Cannot reproduce or index correct source state |
| No usable bug description | No meaningful input |
| Sensitive data that cannot be anonymized | Cannot report safely |

Recommended dataset size:

| Stage | Number of bugs |
|---|---:|
| Pilot | 3–5 |
| Final case study | 10–20 |

---

# 6. Dataset Format

Use a unified JSONL format for both benchmark and company data.

Each line is one bug.

```json
{
  "bug_id": "CAPSTONE-001",
  "project": "company_project_anonymized",
  "bug_report": "User cannot submit an order when quantity is zero. The UI shows success, but the backend should reject it.",
  "stack_trace": "Optional stack trace after anonymization",
  "logs": "Optional CI or runtime logs after anonymization",
  "test_failure": "Optional failing test name and assertion error",
  "repo_path": "/path/to/buggy/repository/version",
  "buggy_commit": "abc123",
  "fix_commit": "def456",
  "ground_truth": {
    "files": [
      "src/main/java/com/example/order/OrderService.java"
    ],
    "methods": [
      "OrderService.validateOrder"
    ]
  },
  "extra_context": {
    "jira_id": "ANON-123",
    "source": "jira + bitbucket + logs",
    "available_artifacts": ["jira", "fix_commit", "logs"],
    "notes": "Fix commit used only for evaluation, not model input."
  }
}
```

For Defects4J, convert the metadata into the same schema:

```json
{
  "bug_id": "Lang-1",
  "project": "Lang",
  "bug_report": "Text from issue tracker if available, otherwise issue title/URL plus triggering test cause.",
  "stack_trace": "tests.trigger.cause output if available",
  "logs": "defects4j test output if collected",
  "test_failure": "triggering test names",
  "repo_path": "/tmp/defects4j/Lang_1b",
  "ground_truth": {
    "files": ["src/main/java/..."],
    "methods": []
  }
}
```

---

# 7. Proposed Method / Pipeline

The proposed method should be described as a context-aware, agentic fault localization pipeline.

## 7.1 Pipeline Overview

```text
Bug report / logs / tests / repository
            |
            v
[1] Bug Context Collector
            |
            v
[2] Repository Structure Analyzer + Code Retriever
            |
            v
[3] Localization Agent
            |
            v
[4] Verification Agent
            |
            v
Ranked suspicious files / methods
            |
            v
[5] Evaluator: Top-k, MRR, cost, qualitative analysis
```

---

## 7.2 Stage 1 — Bug Context Collector

Input:

- bug report
- issue title and description
- comments, if allowed
- logs
- stack trace
- failing test
- website/user report

Output:

```text
Structured bug context:
- symptom
- expected behavior
- actual behavior
- affected feature/module
- error messages
- mentioned classes/files/functions
- keywords for retrieval
- available runtime evidence
```

This stage can be rule-based at first. Later it can use an LLM to summarize the bug context.

---

## 7.3 Stage 2 — Repository Structure Analyzer + Code Retriever

Input:

- structured bug context
- repository source code

Tasks:

- scan source files
- extract file paths, class names, method names
- build lexical index
- optionally build embedding index
- retrieve top-k candidate files/methods/snippets

Retrieval signals:

| Signal | Example |
|---|---|
| keyword match | bug report mentions “quantity” and code contains `quantity` |
| file/class name match | report mentions `OrderService` |
| stack trace match | exception points to method name |
| module rule | frontend bug → search UI module first |
| test failure name | `testZeroQuantityOrderShouldFail` suggests order validation |
| dependency expansion | include imported/called files near top candidates |

Output:

```json
{
  "candidate_files": ["src/.../OrderService.java", "src/.../OrderController.java"],
  "candidate_methods": ["OrderService.validateOrder", "OrderController.submitOrder"],
  "snippets": ["..."]
}
```

---

## 7.4 Stage 3 — Localization Agent

Input:

- structured bug context
- repository structure summary
- retrieved candidate snippets

Output:

```json
[
  {
    "rank": 1,
    "file": "src/main/java/com/example/order/OrderService.java",
    "method": "OrderService.validateOrder",
    "confidence": 0.82,
    "reason": "The bug concerns invalid quantity acceptance. This method checks quantity before order submission."
  },
  {
    "rank": 2,
    "file": "src/main/java/com/example/order/OrderController.java",
    "method": "OrderController.submitOrder",
    "confidence": 0.61,
    "reason": "This method receives the request and calls the validation logic."
  }
]
```

Output must be strict JSON so that evaluation can be automated.

---

## 7.5 Stage 4 — Verification Agent

The verifier receives:

- bug context
- top candidate files/methods
- code snippets
- logs/stack traces/tests if available

The verifier does **not** receive:

- fix commit
- patch
- ground truth changed files

Verifier tasks:

- check if the candidate can explain the bug symptom
- check whether runtime evidence supports the candidate
- reject unrelated candidates
- re-rank the candidates
- produce a short evidence-based explanation

Output:

```json
{
  "verified_ranking": [
    {
      "rank": 1,
      "file": "src/main/java/com/example/order/OrderService.java",
      "method": "OrderService.validateOrder",
      "verdict": "likely",
      "evidence": "The stack trace and failing test both point to order validation."
    }
  ],
  "rejected_candidates": [
    {
      "file": "src/main/java/com/example/ui/OrderPage.java",
      "reason": "The UI page is related to submission but does not explain backend acceptance of invalid quantity."
    }
  ]
}
```

---

# 8. Experimental Design

## Experiment 0 — Pipeline Sanity Check

Purpose:

- Ensure the implementation works before running large experiments.

Dataset:

- 3–5 toy or company bugs
- 5–10 Defects4J bugs

Success criteria:

- repository indexing works
- retrieval returns candidates
- LLM/mock LLM returns parseable JSON
- predictions are saved
- Top-k metrics can be computed

---

## Experiment 1 — Defects4J Benchmark Validation

Purpose:

- Validate the approach on a standard benchmark.

Dataset:

- Start with 20–30 Defects4J bugs
- Expand to 100–200 if time allows

Recommended project order:

1. Lang
2. Math
3. Time
4. Chart
5. Mockito
6. Closure, optional later

Methods to compare:

| Method | Description |
|---|---|
| BM25 / keyword baseline | Rank files by textual similarity between bug report/runtime evidence and source code. |
| LLM-basic | LLM sees only bug report or triggering test cause. |
| LLM + structure | LLM also sees repository/module structure. |
| LLM + retrieved code | LLM sees retrieved source snippets. |
| Full pipeline | LLM + structure + retrieved code + runtime evidence + verifier. |

Main output table:

| Method | Top-1 | Top-3 | Top-5 | MRR | Avg tokens | Avg runtime |
|---|---:|---:|---:|---:|---:|---:|
| BM25 |  |  |  |  |  |  |
| LLM-basic |  |  |  |  |  |  |
| LLM + structure |  |  |  |  |  |  |
| LLM + retrieved code |  |  |  |  |  |  |
| Full pipeline |  |  |  |  |  |  |

---

## Experiment 2 — Context Ablation Study

Purpose:

- Identify which context sources improve or hurt localization.

Variants:

| Variant | Description | Expected insight |
|---|---|---|
| C0 | bug report / test failure only | Minimal LLM baseline |
| C1 | C0 + repository tree | Whether structure helps narrow search |
| C2 | C1 + retrieved code snippets | Whether source context improves ranking |
| C3 | C2 + stack trace/logs/tests | Whether runtime evidence helps |
| C4 | C3 + verifier | Whether independent checking helps |

Analysis:

- Compare Top-k changes between adjacent variants.
- Identify bugs where added context helps.
- Identify bugs where added context hurts due to noise.

Example result table:

| Variant | Top-1 | Top-3 | Top-5 | MRR | Notes |
|---|---:|---:|---:|---:|---|
| C0 |  |  |  |  | baseline |
| C1 |  |  |  |  | structure effect |
| C2 |  |  |  |  | code context effect |
| C3 |  |  |  |  | runtime evidence effect |
| C4 |  |  |  |  | verifier effect |

---

## Experiment 3 — Verification Agent Study

Purpose:

- Isolate the effect of the verification agent.

Comparison:

| Version | Description |
|---|---|
| Without verifier | localization agent output directly evaluated |
| With verifier | verifier re-ranks localization output |

Metrics:

- Top-1/3/5 before vs after verifier
- MRR before vs after verifier
- number of candidates rejected
- number of bugs where verifier improves rank
- number of bugs where verifier worsens rank
- additional token cost

Example table:

| Bug ID | Correct rank before | Correct rank after | Improved? | Verifier note |
|---|---:|---:|---|---|
| Lang-1 | 4 | 2 | yes | Stack trace supports candidate |
| Math-5 | 1 | 3 | no | Verifier over-weighted similar method |

---

## Experiment 4 — Company / Capstone Case Study

Purpose:

- Evaluate the approach on real project bugs.

Dataset:

- 10–20 company/Capstone bugs, if available

Evaluation:

| Metric / analysis | Description |
|---|---|
| File-level Top-k hit | Whether predicted files include changed files from fixing commit |
| Method-level Top-k hit | If changed methods can be identified |
| Qualitative usefulness | Whether prediction/explanation would help a developer |
| Context usefulness | Which information source helped most |
| Failure analysis | Why localization failed |
| Cost | LLM calls/tokens/runtime per bug |

Per-bug case template:

```markdown
## Case CAPSTONE-001

### Bug summary
- Symptom:
- Expected behavior:
- Actual behavior:
- Available artifacts:

### Ground truth
- Fix commit:
- Changed files:
- Changed methods:

### Agent result
| Rank | File | Method | Reason |
|---:|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |

### Evaluation
- Top-1 hit: yes/no
- Top-3 hit: yes/no
- Top-5 hit: yes/no

### Context analysis
- Helpful context:
- Noisy/misleading context:
- What the verifier changed:

### Failure analysis, if any
- Reason for failure:
- Possible improvement:
```

Cross-case result table:

| Bug ID | Available context | Top-1 | Top-3 | Top-5 | Most useful source | Failure mode |
|---|---|---:|---:|---:|---|---|
| CAP-001 | Jira + logs + fix commit | ✓ | ✓ | ✓ | stack trace | - |
| CAP-002 | website report + repo | ✗ | ✓ | ✓ | module structure | similar files |
| CAP-003 | vague issue only | ✗ | ✗ | ✗ | none | report too vague |

---

## Experiment 5 — Cost and Stability Analysis

Purpose:

- Understand practical feasibility.

Metrics:

| Metric | Description |
|---|---|
| LLM calls per bug | Number of model calls |
| Tokens per bug | Input + output tokens |
| Runtime per bug | Wall-clock time |
| JSON parse success | Percentage of outputs that are parseable |
| Repeated-run stability | Whether rankings change across repeated runs |

Suggested setup:

- Run each LLM-based variant with temperature 0 or very low temperature.
- For a small subset, repeat 3 times to check stability.
- Report average and standard deviation if possible.

---

# 9. Evaluation Metrics

## 9.1 File-Level Top-k Accuracy

A prediction is correct at file level if at least one ground-truth changed source file appears in the top-k predicted files.

Formula:

```text
Top-k accuracy = number of bugs where top-k contains a ground-truth file / total number of bugs
```

Use:

- Top-1
- Top-3
- Top-5

---

## 9.2 Method-Level Top-k Accuracy

A prediction is correct at method level if a ground-truth changed method appears in the top-k predicted methods.

This is harder than file-level evaluation.

Recommendation:

- File-level is mandatory.
- Method-level is optional but valuable if method extraction is reliable.

---

## 9.3 MRR

Mean Reciprocal Rank rewards methods that rank the correct location higher.

```text
MRR = average(1 / rank of first correct prediction)
```

Example:

| Correct rank | Reciprocal rank |
|---:|---:|
| 1 | 1.0 |
| 2 | 0.5 |
| 5 | 0.2 |
| not found | 0 |

---

## 9.4 Recall@k for Multi-File Fixes

If one bug has multiple ground-truth files, Recall@k measures how many are covered.

```text
Recall@k = number of ground-truth files found in top-k / total ground-truth files
```

Use this as optional analysis.

---

## 9.5 Qualitative Metrics for Company Case Study

Because real company bugs may not always have clean ground truth, add qualitative analysis.

| Qualitative aspect | Question |
|---|---|
| Usefulness | Would the result help a developer inspect the right area? |
| Explanation quality | Does the reason connect bug symptom to code behavior? |
| Context usefulness | Which information source helped most? |
| Failure mode | Why did the method fail? |
| Practical overhead | Was the pipeline too expensive or slow? |

---

# 10. Baselines

## 10.1 Required Baselines

| Baseline | Reason |
|---|---|
| BM25 / keyword retrieval | Simple IR baseline; easy to implement. |
| LLM-basic | Shows what happens if we only ask an LLM with minimal context. |
| LLM + retrieved code | Shows the effect of code context. |
| Full pipeline | Your proposed method. |

---

## 10.2 Optional Baselines

| Baseline | Use if |
|---|---|
| Embedding retrieval | You have time to add vector search. |
| Ochiai / Tarantula | You can run coverage on Defects4J reliably. |
| Existing LLM-FL paper results | Use only as literature comparison, not direct reproduction unless feasible. |

Traditional SBFL baselines such as Ochiai and Tarantula are useful, but they require coverage data and passing/failing tests. They are suitable for Defects4J, but not necessarily for company data.

---

# 11. Implementation Plan

You already have an MVP structure that can support this experiment.

Recommended modules:

```text
src/fl_localizer/
├── schema.py          # BugRecord, Candidate, Prediction schemas
├── io_utils.py        # read/write JSONL
├── indexer.py         # scan repository and build code index
├── chunker.py         # split code into classes/methods/snippets
├── bm25.py            # lexical retrieval baseline
├── prompts.py         # prompt templates
├── llm_client.py      # mock or real LLM client
├── pipeline.py        # end-to-end localization pipeline
├── evaluation.py      # Top-k, MRR, per-bug metrics
├── cli.py             # run localization
└── evaluate_cli.py    # run evaluation
```

---

## 11.1 Minimal Implementation Order

### Step 1 — Data loader

Implement:

- read benchmark/company bug JSONL
- validate required fields
- avoid giving ground truth to the agent

### Step 2 — Repository indexer

Implement:

- scan source files
- ignore generated files, build directories, dependencies
- collect path, class, method, code snippet

### Step 3 — Retrieval baseline

Implement:

- BM25 or simple TF-IDF
- rank candidate files/methods by similarity
- save top-k candidates

### Step 4 — LLM localization

Implement:

- prompt construction
- strict JSON output
- retry on invalid JSON
- temperature 0 for reproducibility

### Step 5 — Verifier

Implement:

- second prompt
- check top candidates
- re-rank
- save before/after rankings

### Step 6 — Evaluator

Implement:

- Top-1/3/5 file-level
- MRR
- per-bug result table
- CSV/JSON output

---

## 11.2 Run Commands for Your Pipeline

Run localization:

```bash
PYTHONPATH=src python -m fl_localizer.cli \
  --repo /path/to/repo \
  --bugs data/bugs.jsonl \
  --out outputs/predictions.jsonl \
  --top-retrieve 30 \
  --top-output 5 \
  --verifier
```

Evaluate:

```bash
PYTHONPATH=src python -m fl_localizer.evaluate_cli \
  --bugs data/bugs.jsonl \
  --pred outputs/predictions.jsonl \
  --per-bug
```

Run ablation:

```bash
python -m scripts.run_ablation \
  --repo /path/to/repo \
  --bugs data/bugs.jsonl \
  --out-dir outputs/ablation
```

---

# 12. Data Leakage Rules

This is critical.

The localization agent may use:

- bug report
- issue title/description/comments, if allowed
- stack trace
- logs
- failing test name/output
- repository structure
- source code from buggy version
- retrieved snippets from buggy version

The localization agent must **not** use:

- fixed version source code
- fixing commit diff
- patch
- list of changed files
- ground-truth method names obtained from the fix
- developer explanation written after the fix, unless clearly separated and used only in qualitative discussion

Recommended thesis statement:

> To avoid data leakage, all model inputs are constructed only from information available before or at the time the bug is reported. Fixing commits and modified files are used exclusively for evaluation.

---

# 13. Expected Results and Analysis

The thesis does not need to prove that the proposed method always wins. It needs to produce a careful analysis.

Possible outcomes:

| Outcome | Interpretation |
|---|---|
| Full pipeline improves Top-k | Context and verifier are useful. |
| Retrieved code improves over bug report only | Repository context matters. |
| Runtime evidence helps only when available | Stack traces/logs are high-value but sparse. |
| Verifier improves Top-3 but not Top-1 | Verifier helps remove weak candidates but may not always rank perfectly. |
| Company case study performs worse than benchmark | Real data is noisier; supports motivation. |
| Company case study performs similarly | Approach transfers well to realistic setting. |

Important:

- Do not overclaim.
- Discuss both successful and failed cases.
- Use failure analysis as a contribution.

---

# 14. Thesis Chapter Structure

## Chapter 1 — Introduction

- Motivation
- Problem statement
- Research questions
- Contributions

## Chapter 2 — Literature Study / Background

- Fault localization
- LLM-based software testing
- Agentic testing
- Benchmark limitations and real-world evaluation gap

## Chapter 3 — Methodology

- Problem definition
- Dataset construction
- Pipeline design
- Prompts
- Retrieval method
- Verification agent
- Metrics
- Data leakage prevention

## Chapter 4 — Benchmark Experiment

- Defects4J setup
- Bug selection
- Baselines
- Main results
- Context ablation
- Verifier analysis
- Cost/stability analysis

## Chapter 5 — Company / Capstone Case Study

- Company/project context, anonymized
- Bug selection
- Available information sources
- Per-bug analysis
- Cross-case findings
- Practical lessons

## Chapter 6 — Discussion

- Interpretation of results
- Benchmark vs real-world findings
- Limitations
- Threats to validity

## Chapter 7 — Conclusion

- Summary
- Answer research questions
- Future work

---

# 15. Threats to Validity

## Internal Validity

- The LLM may produce unstable output.
- Prompt design may influence results.
- Ground truth based on fixing commits may include files that were changed but not faulty.
- Retrieval quality may limit downstream localization.

Mitigation:

- use deterministic settings where possible
- save prompts and outputs
- use fixed seeds where applicable
- report parse failures and repeated-run stability

---

## Construct Validity

- Top-k accuracy may not fully measure developer usefulness.
- Method-level ground truth may be difficult to extract reliably.
- A fixing commit may contain cleanup changes in addition to actual bug fix.

Mitigation:

- report file-level and method-level separately
- include qualitative case analysis
- exclude large refactoring commits

---

## External Validity

- Defects4J is Java-focused.
- Company case study may only represent one project.
- Results may not generalize to all languages or organizations.

Mitigation:

- describe project context carefully
- do not overgeneralize
- optionally add Bench4BL or GitBug-Java if time allows

---

## Conclusion Validity

- Small sample size may limit statistical conclusions.
- LLM API/model updates may change results.
- Cost may vary over time.

Mitigation:

- use enough benchmark bugs for quantitative analysis
- record model version and date
- report confidence intervals if feasible

---

# 16. Timeline

| Week | Goal | Output |
|---:|---|---|
| 1 | Defects4J setup + 5 bug pilot | successful checkout, metadata extraction |
| 2 | Convert Defects4J bugs to JSONL | first benchmark dataset file |
| 3 | Run BM25 + LLM-basic | baseline results |
| 4 | Add retrieved code + repo structure variants | context ablation results |
| 5 | Add verifier agent | verifier comparison |
| 6 | Expand benchmark to 50–100 bugs | main benchmark table |
| 7 | Collect 3–5 company bugs | case study pilot |
| 8 | Expand to 10–20 company bugs | full case study data |
| 9 | Analyze failures and qualitative findings | case study chapter material |
| 10 | Write methodology and experiment chapters | draft chapters |

---

# 17. Immediate Next Steps

## Step 1 — Start Defects4J

```bash
git clone https://github.com/rjust/defects4j
cd defects4j
cpanm --installdeps .
./init.sh
export PATH=$PATH:$(pwd)/framework/bin
defects4j info -p Lang
```

## Step 2 — Try one bug

```bash
defects4j checkout -p Lang -v 1b -w /tmp/lang_1_buggy
cd /tmp/lang_1_buggy
defects4j compile
defects4j test
defects4j export -p classes.modified
defects4j export -p tests.trigger.cause
```

## Step 3 — Create first JSONL record

```json
{
  "bug_id": "Lang-1",
  "project": "Lang",
  "bug_report": "Use issue report text or triggering test cause.",
  "stack_trace": "Output from tests.trigger.cause or test log.",
  "logs": "Optional defects4j test output.",
  "test_failure": "Triggering test name.",
  "repo_path": "/tmp/lang_1_buggy",
  "ground_truth": {
    "files": ["PATH_FROM_CLASSES_MODIFIED"],
    "methods": []
  }
}
```

## Step 4 — Run MVP pipeline

```bash
PYTHONPATH=src python -m fl_localizer.cli \
  --repo /tmp/lang_1_buggy \
  --bugs data/defects4j/lang_1.jsonl \
  --out outputs/lang_1_predictions.jsonl \
  --top-retrieve 30 \
  --top-output 5 \
  --verifier
```

## Step 5 — Evaluate

```bash
PYTHONPATH=src python -m fl_localizer.evaluate_cli \
  --bugs data/defects4j/lang_1.jsonl \
  --pred outputs/lang_1_predictions.jsonl \
  --per-bug
```

---

# 18. Message You Can Send to Supervisor

```text
Dear Ana,

I have refined the experiment design based on our discussion. The thesis will use a two-part evaluation. First, I will validate the proposed LLM-based fault localization pipeline on a standard benchmark, starting with Defects4J. This provides controlled and comparable results using file-level Top-k accuracy and MRR. Second, I will apply the same pipeline to a company/Capstone case study, where bug information may come from Jira, Bitbucket, logs, website reports, repository structure, and fixing commits.

The proposed pipeline has four main stages: bug context collection, repository/code retrieval, LLM-based localization, and independent verification. I will compare several context settings: bug report only, bug report plus repository structure, bug report plus retrieved code, bug report plus runtime evidence, and the full pipeline with a verifier. The benchmark experiment will provide quantitative results, while the company case study will combine Top-k hit rate with qualitative analysis of which information sources are useful and why the approach succeeds or fails.

My next step is to run a small Defects4J pilot and prepare several anonymized company/Capstone bug records for the case study.

Best regards,
Ziniu
```

---

# 19. Links

## Recommended first benchmark

- Defects4J: https://github.com/rjust/defects4j

## Optional secondary benchmarks

- Bench4BL: https://github.com/exatoa/Bench4BL
- GitBug-Java: https://github.com/gitbugactions/gitbug-java
- BugsInPy: https://github.com/soarsmu/BugsInPy

## Suggested priority

1. **Defects4J** — start here.
2. **Company / Capstone case study** — build in parallel after the pipeline works.
3. **Bench4BL** — optional if more bug-report-based benchmark evidence is needed.
4. **GitBug-Java** — optional if a more recent Java benchmark is needed and setup time is available.
5. **BugsInPy** — only if the thesis needs Python evaluation.
