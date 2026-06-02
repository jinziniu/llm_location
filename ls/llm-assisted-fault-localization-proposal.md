# LLM-Assisted Fault Localization in Benchmark and Real-World Repository Settings

Author: Ziniu Jin

VU supervisor: Ana Oprescu

Daily supervisor: Supervisor Name

Second reader: Second Reader Name

Date: May 2026

## Abstract

Modern software systems are increasingly difficult to test and debug because failures often depend on framework behavior, runtime context, configuration, and interactions across multiple files. Recent research shows that large language models (LLMs) can support software testing tasks such as fault localization, vulnerability detection, flaky test classification, and UI test repair. However, many LLM-based approaches are still evaluated mainly on academic benchmarks or isolated tasks, and there is limited evidence about how well they work in real repository settings with incomplete bug reports, noisy logs, large codebases, and changing project histories.

This project investigates an LLM-assisted file-level fault localization approach. The proposed system first retrieves suspicious source files using BM25 and hybrid retrieval, then uses an LLM to rerank selected candidate files based on bug reports, failing tests, stack traces, source-code snippets, and retrieval evidence. To control cost, the project studies selective reranking, where LLM calls are applied only to uncertain or domain-mismatched cases. As an extension, the project will evaluate a controlled agentic inspection and verification loop, where an LLM can use limited search and file-reading tools before producing a final ranking.

The evaluation will combine benchmark validation on Defects4J with real-world case studies from AboutWork and Easy Finance. The main expected contribution is empirical evidence on when LLM-assisted fault localization helps, where it fails, and how retrieval quality, context selection, and selective LLM usage affect practical usefulness.

## 1. Introduction

Software testing is essential for maintaining reliability, but modern software systems make debugging and fault localization increasingly difficult. Bugs may be caused by business logic errors, unstable tests, API mismatches, state synchronization problems, UI changes, framework behavior, or incomplete integration between components. In continuous integration and real development environments, developers often need to inspect bug reports, failing tests, stack traces, logs, and source-code context before they can identify the likely faulty files.

Fault localization studies how to rank program locations by their likelihood of containing a defect. Traditional techniques such as spectrum-based fault localization use test coverage and pass/fail information to compute suspiciousness scores. These methods are interpretable and useful when reliable tests and coverage data are available, but they are less suitable when tests are incomplete, flaky, difficult to execute, or unavailable.

Recent large language models have introduced new possibilities for software engineering tasks. Prior work has applied LLMs to fault localization, vulnerability detection, UI test repair, flaky test classification, and test execution. My literature study found a common research gap: many LLM-based methods are evaluated on academic benchmarks or single-task datasets, while their behavior in real repository settings is less understood. In practice, fault localization requires reasoning over noisy and heterogeneous information, including issue descriptions, stack traces, project structure, candidate source files, and bug-fixing commits used only for evaluation.

This project addresses that gap by designing and evaluating an LLM-assisted fault localization pipeline. The project focuses on file-level localization as a practical first step: given a bug report and repository context, the system ranks source files that are most likely to contain the bug. The work combines controlled benchmark experiments with real-world company case studies, making it possible to compare benchmark performance with practical repository-level behavior.

The personal value of this project is to develop stronger research and engineering ability in empirical software engineering, LLM-based tooling, experiment design, and reproducible evaluation. It also connects directly to practical debugging problems that appear in real software development.

## 2. Background

Fault localization is the task of identifying likely faulty locations in a program. In this project, the main granularity is the source file. A prediction is considered successful if at least one file changed by the verified bug-fixing commit appears within the top-k ranked files.

BM25 is an information retrieval method that ranks documents according to term relevance. In this project, each source file is indexed as a document using its path, package, class names, method names, and source text. A bug query is constructed from the bug report, failing test, triggering tests, and stack trace.

Hybrid retrieval extends BM25 by adding repository-specific signals. These include stack-trace class hints, triggering-test hints, identifier overlap, and focused filtering of relevant failure sections. This step is important because LLM reranking cannot recover the correct file if it is absent from the candidate pool.

LLM reranking is a second-stage method. Instead of asking the model to search the whole repository, the system provides a limited list of candidate files with source-code snippets and retrieval evidence. The model then returns a structured JSON ranking. The output is validated, deduplicated, and completed with BM25 fallback if necessary.

Selective reranking is used to control cost. Rather than sending every bug to the LLM, a selector chooses cases where the initial retrieval appears uncertain or semantically mismatched with the bug report. This makes the method more realistic for practical use because LLM calls have token, time, and cost constraints.

Finally, an agentic inspection loop extends one-shot reranking. In this controlled version, the LLM can use a small set of tools, such as searching files and reading selected source snippets, for a fixed number of steps. A verifier can then independently check the top candidates before the final ranking is produced.

## 3. Problem

The main problem is that current LLM-based fault localization research does not yet provide enough evidence for practical repository-level use. Existing methods show promising results on benchmarks such as Defects4J, but real projects differ from benchmarks in several ways.

First, real bug reports are often incomplete or ambiguous. They may describe user-visible symptoms rather than exact failing tests. Second, repositories contain noise such as generated files, framework code, scripts, generic UI components, and historical artifacts. Third, the relevant evidence may be distributed across multiple files and may not appear in the highest-ranked BM25 result. Fourth, LLM-based methods can be expensive if applied to every bug with large prompts. Finally, one-shot LLM predictions may produce plausible but weakly supported rankings unless the model is given useful source-code evidence.

The scope of this project is therefore not full automatic repair. Instead, the project studies a narrower and measurable question: can a retrieval-and-reranking system, optionally extended with controlled agentic inspection and verification, improve file-level fault localization across benchmarks and real repositories?

## 4. Related Work

Traditional fault localization includes techniques such as Tarantula and Ochiai, which use coverage and pass/fail test results to rank suspicious program elements. These methods are useful baselines but depend on executable tests and coverage data.

Recent work has applied code language models to fault localization. For example, LLM-based approaches on Defects4J show that pretrained or fine-tuned code models can improve Top-k localization accuracy. Other work explores test-free fault localization, where models predict suspicious code without relying on test execution. These studies motivate the use of LLMs, but they are still mainly benchmark-centered.

LLMs have also been used in adjacent testing tasks, including vulnerability detection, flaky test classification, UI test repair, and agent-based test execution. These studies show that prompt design, context quality, and benchmark quality strongly affect performance. Agentic testing systems further suggest that LLMs can interact with repositories and tools, but their use has mainly been explored for test execution or security vulnerability discovery rather than ordinary application-level fault localization.

My literature study consolidates these findings into three gaps. First, LLM-based fault localization lacks validation in real repository settings. Second, agentic scaffolds have not been sufficiently evaluated for ordinary business and application-level bugs. Third, the effects of context level and independent verification on localization accuracy remain unclear. This project is designed around these gaps.

## 5. Research Questions

RQ1: Compared with BM25 and hybrid retrieval baselines, does LLM reranking improve file-level fault localization accuracy on Defects4J?

This question evaluates the benchmark effectiveness of LLM reranking under controlled conditions.

RQ2: How do candidate retrieval quality and source-code evidence quality affect LLM reranking performance?

This question studies whether failures are caused by missing candidates, noisy candidates, weak snippets, or incorrect LLM reasoning.

RQ3: Can selective reranking reduce LLM calls while preserving Top-k accuracy and MRR?

This question evaluates whether a non-oracle selector can control token cost and runtime without losing most of the accuracy benefit.

RQ4: How well does the approach transfer from academic benchmarks to real-world company repositories?

This question compares Defects4J results with AboutWork bug logs and Easy Finance git-history-derived bug records.

RQ5: Does a controlled agentic inspection and verification loop improve localization compared with one-shot LLM reranking?

This question evaluates whether limited tool use and independent verification can improve the quality of final rankings.

## 6. Approach

The project will use a reproducible pipeline with three levels of evaluation.

First, benchmark validation will be performed on Defects4J. For each bug, the system checks out the buggy version, extracts triggering tests and failure information, indexes source files, runs retrieval, and evaluates predictions against modified files from the official fixing commit. The current pilot already covers Lang, Math, Chart, Time, Closure, and Mockito.

Second, real-world case studies will be performed using AboutWork and Easy Finance. AboutWork provides manually recorded company bug logs. Easy Finance provides git-history-derived bug records built from fixing commits. These two datasets allow the project to study realistic bug descriptions, frontend/backend codebases, business-domain mismatch, and data quality issues that do not appear in clean benchmarks.

Third, the system will compare four method variants:

1. BM25 baseline.
2. Focused hybrid retrieval.
3. One-shot LLM reranking on retrieved candidates.
4. Controlled agentic inspection and optional verifier reranking.

The controlled agent will not have access to ground truth, fixing commits, or post-fix code. It will receive an initial candidate list and a fixed tool set: search files, read file snippets, inspect candidate metadata, and produce a final JSON ranking. The number of tool-use steps will be limited to keep the experiment reproducible.

The evaluation metrics are Top-1, Top-3, Top-5, Top-10, MRR, candidate recall, total tokens, average tokens per bug, runtime, and output validity. Error analysis will classify failures into candidate-missing failures, evidence-quality failures, ambiguous-report failures, selector failures, and LLM reasoning failures.

## 7. Plan

Week 1: Finalize proposal and research questions. Clean up the current experimental documentation and define the final scope of benchmark and company datasets.

Week 2: Consolidate the Defects4J benchmark pipeline. Recheck dataset construction, BM25 outputs, hybrid retrieval outputs, and evaluation scripts.

Week 3: Consolidate AboutWork and Easy Finance case-study datasets. Document data sources, ground-truth construction, filtering decisions, and data-quality caveats.

Week 4: Run and verify final BM25 and hybrid retrieval baselines. Produce consistent tables for Top-k accuracy, MRR, and candidate recall.

Week 5: Run or finalize one-shot LLM reranking experiments. Summarize token usage, runtime, output validity, and per-project improvements.

Week 6: Implement the controlled agentic inspection variant. Add fixed search and read tools, logging of tool traces, and maximum-step limits.

Week 7: Evaluate the agentic variant on selected hard cases from Defects4J and company datasets. Compare it against one-shot reranking.

Week 8: Perform error analysis. Identify whether failures are caused by retrieval recall, weak evidence snippets, ambiguous bug reports, or LLM reasoning.

Week 9: Write the methodology and experimental design sections of the thesis.

Week 10: Write results, discussion, and threats to validity. Prepare tables and figures.

Week 11: Revise the thesis based on supervisor feedback. Prepare the final presentation.

Week 12: Final polishing, submission, and defense preparation.

Key deliverables are the final thesis report, reproducible experiment scripts, result tables, worklog documentation, and a final presentation.

## 8. Conclusion

This project investigates whether LLM-assisted fault localization can move beyond isolated benchmark tasks toward practical repository-level debugging support. The proposed work starts from a controlled retrieval-and-reranking pipeline, evaluates it on Defects4J, and then studies its behavior on real company project data. The project also explores a controlled agentic extension with limited tool use and verification. The expected outcome is not a fully automatic repair agent, but an empirically grounded understanding of how retrieval, context, LLM reasoning, selective invocation, and verification affect file-level fault localization.

## References

[1] B. Kitchenham and S. Charters. Guidelines for performing systematic literature reviews in software engineering. EBSE Technical Report, 2007.

[2] J. A. Jones, M. J. Harrold, and J. Stasko. Visualization of test information to assist fault localization. ICSE, 2002.

[3] R. Abreu, P. Zoeteweij, and A. J. C. van Gemund. On the accuracy of spectrum-based fault localization. TAICPART-MUTATION, 2007.

[4] S. Ji et al. Impact of large language models of code on fault localization. ICST, 2025.

[5] A. Khare et al. Understanding the effectiveness of large language models in detecting security vulnerabilities. ICST, 2025.

[6] Z. Xu, Q. Li, and S. H. Tan. Understanding and enhancing attribute prioritization in fixing web UI tests with LLMs. ICST, 2025.

[7] R. Feldt et al. Towards autonomous testing agents with large language models. 2024.

[8] I. Bouzenia and M. Pradel. Repository-level test execution with LLM agents. 2024.
