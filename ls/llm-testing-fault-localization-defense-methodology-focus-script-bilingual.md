# Methodology-Focused Defense Script / 强调方法部分的答辩讲稿

Deck: `llm-testing-fault-localization-defense-methodology-focus.pptx`

Use the English version for speaking. The Chinese version is for checking meaning.

---

## Slide 1. Title

**中文**

大家好，我是 Ziniu Jin。今天我介绍我的 literature study，主题是大语言模型在软件测试和故障定位中的应用。因为我的导师比较重视文献查找和筛选方法，所以我今天会特别强调：我是如何找文献、如何筛选文献、以及如何从文献中总结 research gaps 的。

**English**

Good morning / good afternoon. My name is Ziniu Jin. Today I will present my literature study on large language models for software testing and fault localization.

In this presentation, I will not only summarize the findings. I will also focus on the literature search and selection process: how I searched for papers, how I screened them, and how I used them to identify research gaps.

---

## Slide 2. Motivation

**中文**

这个主题比较分散。相关研究不只在 fault localization 里面，也出现在 flaky tests、UI test repair、vulnerability detection、CI/CD、IoT、microservices 和 testing agents 这些方向里。所以如果只用一个关键词，很容易漏掉重要文献。因此我需要一个 systematic search strategy，覆盖测试问题和 LLM 方法两个方面。

**English**

The motivation is that this research area is fragmented.

Relevant papers are not only in fault localization. They also appear in flaky tests, UI test repair, vulnerability detection, CI/CD testing, IoT platforms, microservices, and testing agents.

So if I only use one keyword or one research direction, I may miss important papers. This is why I designed the search to cover both testing problems and LLM-based solutions.

---

## Slide 3. Literature Search Protocol

**中文**

我的搜索策略包括三个部分。第一是数据库和搜索来源，包括 IEEE Xplore、ACM Digital Library，以及 Google Scholar 作为补充。第二是关键词族，比如 software testing、flaky test、fault localization、vulnerability detection、UI testing、large language model。第三是 Boolean combinations，例如 “fault localization AND LLM”，或者 “software testing OR test automation AND large language model”。这样做的目的是保证覆盖面，而不是只找和标题完全一样的论文。

**English**

My literature search protocol has three main parts.

First, I used academic sources such as IEEE Xplore and the ACM Digital Library, with Google Scholar as a supplement.

Second, I used several keyword families, including software testing, flaky test, fault localization, vulnerability detection, UI testing, and large language model.

Third, I combined these terms with Boolean search strings. For example, “fault localization AND LLM”, or “software testing OR test automation AND large language model”.

The reason is to improve coverage. I did not want to only find papers with exactly the same title as my topic.

---

## Slide 4. Screening Criteria

**中文**

找到候选文献后，我使用 inclusion 和 exclusion criteria 来筛选。纳入的论文需要是 peer-reviewed，并且和软件测试、缺陷分析、故障定位、漏洞检测、UI testing 或 automation 相关。如果是 LLM 论文，还需要说明模型是如何使用的，比如 fine-tuning、few-shot learning 或 prompting，并且要有实验评估。排除的包括非同行评审材料、只间接相关的论文、纯概念讨论、或者重复论文。

**English**

After collecting candidate papers, I used explicit inclusion and exclusion criteria.

A paper was included if it was peer-reviewed and related to software testing, defect analysis, fault localization, vulnerability detection, UI testing, or automation.

For LLM-based papers, I also required the paper to explain how the model was used, for example fine-tuning, few-shot learning, or prompt engineering, and to provide an evaluation.

I excluded non-peer-reviewed materials, papers only indirectly related to testing, purely conceptual papers without empirical validation, and duplicate studies.

This step is important because it makes the review more reproducible and defensible.

---

## Slide 5. Snowballing and Selection Results

**中文**

除了初始搜索，我还用了 snowballing。Backward snowballing 是检查 seed papers 的 reference list，看看它们引用了哪些重要论文。Forward snowballing 是在 Google Scholar 中找引用这些 seed papers 的后续研究。最后，初始搜索纳入 9 篇，backward snowballing 从 18 个候选中纳入 8 篇，forward snowballing 从 7 个候选中纳入 3 篇，extended venue search 纳入 5 篇，总共 25 篇。

**English**

In addition to the initial search, I used snowballing.

Backward snowballing means checking the reference lists of the seed papers. This helps identify earlier foundational work.

Forward snowballing means using Google Scholar to find newer papers that cite the seed papers. This helps identify more recent follow-up work.

In the final selection, the initial search contributed 9 studies. Backward snowballing identified 18 candidates and included 8. Forward snowballing identified 7 candidates and included 3. The extended venue search included 5 more studies.

In total, the final corpus contains 25 primary studies.

One improvement for the written version is that I should report the initial candidate count as well, to make the process even more reproducible.

---

## Slide 6. Data Extraction and Synthesis

**中文**

筛选结束后，我不是简单逐篇总结，而是用五个 research questions 来统一提取信息。RQ1 提取 testing challenges 和 root causes。RQ2 提取 detection、localization 和 repair approaches。RQ3 提取 LLM 的使用方式。RQ4 提取 datasets、metrics 和 baselines。RQ5 提取系统上下文和 practical implications。这样每篇论文都可以按同一套框架比较。

**English**

After selecting the papers, I did not only summarize them one by one.

I used five research questions as a data extraction framework.

RQ1 extracts testing challenges and root causes. RQ2 extracts detection, localization, and repair approaches. RQ3 extracts how LLMs are used. RQ4 extracts datasets, metrics, and baselines. RQ5 extracts system context and practical implications.

This means every paper is analyzed using the same structure. That is how I move from a list of papers to a synthesis.

---

## Slide 7. RQ1 Findings

**中文**

RQ1 的主要发现是，测试问题非常依赖具体生态。比如 JavaScript 的 flaky tests 可能和 shared mocking state 有关。UI test fragility 常常来自 DOM、locator 和 timing。IoT testing 会受到设备、firmware 和 low-power mode 的影响。微服务测试的问题既有 API 和 message format 这样的技术原因，也有 service ownership 这样的组织原因。

**English**

For RQ1, the main finding is that testing challenges are ecosystem-specific.

For example, flaky tests in JavaScript can be caused by shared mocking state. UI test fragility often comes from DOM changes, locators, or timing issues. IoT testing is affected by devices, firmware, and low-power modes.

For microservices, the causes are both technical and organizational, such as API mismatches, message format problems, and unclear service ownership.

The key point is that testing problems cannot be fully understood without context.

---

## Slide 8. RQ2 Findings

**中文**

RQ2 关注方法。传统的 spectrum-based fault localization，例如 Tarantula 和 Ochiai，依赖 test coverage 和 pass/fail results。这些方法可解释性强，但依赖可靠测试执行。后来的方法加入 compiler information 和 structural filtering。LLM-based fault localization 则尝试减少对测试执行的依赖，直接从代码或 bug report 中推断 fault location。

**English**

RQ2 focuses on methods.

Traditional spectrum-based fault localization methods, such as Tarantula and Ochiai, rely on test coverage and pass/fail results. They are interpretable, but they depend on reliable test execution.

Later methods add compiler information and structural filtering.

LLM-based fault localization tries to reduce this dependency by reasoning from source code, bug reports, or code representations.

The methodological takeaway is that when we use less execution evidence, context design becomes more important.

---

## Slide 9. RQ3 Findings

**中文**

RQ3 关注 LLM 如何被使用。Fine-tuning 通常需要更多数据，但在特定任务上可能表现更好。Few-shot learning 数据成本较低。Prompt engineering 最灵活，但对 prompt 和 context 很敏感。Testing agents 更接近真实 workflow，因为它们可以安装依赖、运行测试、观察错误并调整命令。对我的 thesis 来说，重点不只是模型本身，而是 context 和 validation。

**English**

RQ3 looks at how LLMs are used.

Fine-tuning usually needs more data, but can perform well on specific tasks. Few-shot learning has lower data cost. Prompt engineering is flexible, but sensitive to the prompt and context.

Testing agents are closer to real workflows, because they can install dependencies, run tests, observe errors, and revise commands.

For my thesis, this means the model itself is not the only important factor. Context and validation are also central.

---

## Slide 10. RQ4 Findings

**中文**

RQ4 的发现是，很多 evaluation 仍然集中在 benchmark 和 isolated tasks 上。Fault localization 常用 Defects4J、Siemens、Space。Flaky test 研究常用 IDoFT 和 FlakyCat。漏洞检测使用 OWASP、Juliet、CVEFixes 或 PrimeVul。这些 benchmark 很有用，但真实 repo 里还会有 bug reports、logs、dependencies、build failures 和 commit history。

**English**

RQ4 shows that many evaluations are still concentrated in benchmarks and isolated tasks.

Fault localization studies often use Defects4J, Siemens, or Space. Flaky test studies use IDoFT and FlakyCat. Vulnerability detection studies use OWASP, Juliet, CVEFixes, or PrimeVul.

These benchmarks are useful for comparison.

But real repositories also include bug reports, logs, dependencies, build failures, and commit history. This is the missing evidence layer.

---

## Slide 11. RQ5 Findings

**中文**

RQ5 说明，在真实项目中，方法不只是“预测哪个文件有 bug”。它还需要拿到正确 repo、正确 commit、安装依赖、运行测试、收集日志和选择上下文。ExecutionAgent 这类研究说明，甚至让测试跑起来本身就是一个问题。因此 fault localization 应该被看成 repository-level workflow。

**English**

RQ5 shows that practical deployment depends on repository workflow.

In a real project, the method does not only predict which file has a bug. It also needs the correct repository, the correct commit, dependencies, test commands, logs, and context selection.

Work such as ExecutionAgent shows that even running tests in arbitrary projects can be difficult.

So fault localization should be treated as a repository-level workflow, not only a code prediction task.

---

## Slide 12. Glasswing Reference

**中文**

我还讨论了 Glasswing 和 Mythos，但这里要说清楚：它们是 grey literature，不是 25 篇 peer-reviewed primary studies 的一部分。它们的价值在于展示了 agent-plus-verifier pattern。一个 agent 发现问题，另一个 agent 独立验证。这对我的 thesis 有启发，但我关注的是普通 application-level bugs，而不只是安全漏洞。

**English**

I also discuss Glasswing and Mythos, but I treat them carefully.

They are grey literature, not part of the 25 peer-reviewed primary studies.

Their value is that they show an agent-plus-verifier pattern. One agent discovers a possible issue, and another agent independently verifies it.

This is useful for thinking about my thesis, but my focus is ordinary application-level bugs, not only security vulnerabilities.

---

## Slide 13. Research Gaps

**中文**

基于这套文献搜索和综合，我总结出三个 gaps。第一，LLM-based fault localization 缺少 real repository-level validation。第二，agentic scaffolds 还没有充分应用到普通 application-level bugs。第三，不同 context level 和 independent verification 对定位效果的影响还没有系统评估。这些 gaps 是从多个 literature streams 综合出来的。

**English**

Based on the search and synthesis, I identify three research gaps.

First, LLM-based fault localization lacks real repository-level validation.

Second, agentic scaffolds have not been sufficiently applied to ordinary application-level bugs.

Third, the effects of context level and independent verification are still unclear.

These gaps come from synthesizing several literature streams, not from only one paper.

---

## Slide 14. Next Step

**中文**

下一步 thesis 可以设计一个实验，用真实 bug reports、buggy snapshots、fixing commits 和 repository context。然后比较不同 context conditions，比如只给 bug report，加入 logs，加入 code snippets，加入 history。最后用 Top-k、MRR、recall 等指标评估 LLM 是否能定位到正确文件或方法。这样可以回答：什么上下文最有用？独立验证是否有帮助？

**English**

The next step is to design a focused thesis experiment.

I can use real bug reports, buggy snapshots, fixing commits, and repository context.

Then I can compare different context conditions: bug report only, adding logs, adding code snippets, and adding history.

The model or agent will rank suspicious files or methods. I can evaluate the result with Top-k accuracy, MRR, or recall, using the verified fixing commit as ground truth.

This directly answers two questions: what context is useful, and whether independent verification helps.

Thank you. I am happy to take questions.

---

# Short Answer If Asked About Methodology / 如果导师追问方法

**English**

The main methodological idea is that I first used broad keyword families to avoid missing related subfields. Then I applied explicit inclusion and exclusion criteria to keep the corpus focused and peer-reviewed. Finally, I used backward and forward snowballing to improve coverage beyond the initial search. After selection, I coded every paper against the same five research questions, so the final gaps are based on synthesis rather than isolated paper summaries.

**中文**

我的方法核心是：先用比较宽的关键词族避免漏掉相关方向；然后用明确的 inclusion/exclusion criteria 保证 corpus 相关且 peer-reviewed；再用 backward 和 forward snowballing 扩展覆盖范围；最后用同样的五个 research questions 对每篇论文编码，所以 research gaps 是综合出来的，不是单篇论文总结。
