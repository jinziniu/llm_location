# 15-Minute Defense Script / 15分钟答辩讲稿

File: `llm-testing-fault-localization-defense.pptx`

Tip: English is the version to speak. Chinese is for checking meaning.

---

## Slide 1. Title

**中文**

大家好，我是 Ziniu Jin。今天我介绍我的文献综述，题目是“大语言模型在软件测试和故障定位中的应用”。这篇综述主要关注两个问题：第一，现代软件测试中有哪些常见挑战；第二，大语言模型是否已经能有效帮助测试和故障定位。最后，我会说明这篇综述如何引出我后续 thesis 的研究方向。

**English**

Good morning / good afternoon. My name is Ziniu Jin. Today I will present my literature study on large language models for software testing and fault localization.

The goal of this review is to understand two things. First, what kinds of testing problems are discussed in recent software engineering research. Second, how large language models are being used to detect, analyze, localize, or repair these problems.

At the end, I will explain how this review leads to my thesis direction: LLM-based fault localization in real repository settings.

---

## Slide 2. Motivation

**中文**

软件测试现在不只是看一个测试通过还是失败。很多失败和运行环境、共享状态、系统架构、CI/CD 工具链有关。例如 flaky tests 可能和异步、并发、测试顺序有关；UI tests 可能因为 DOM 改动或 timing 问题失败；微服务和 IoT 系统还会受到分布式环境、设备和团队协作的影响。因此，如果我们想用 LLM 来帮助测试，就不能只看代码本身，还需要考虑真实上下文。

**English**

The motivation is that modern testing failures are not only simple pass or fail signals.

Many testing problems depend on the execution environment, shared state, system architecture, and toolchains. For example, flaky tests can be caused by asynchronous behavior, concurrency, or test order dependency. UI tests can break because the DOM changes, locators become invalid, or timing changes. In microservice and IoT systems, testing also depends on distributed execution, devices, and sometimes team coordination.

So if we want to use LLMs for testing, we should not only ask whether the model understands code. We also need to ask whether it can work with real project context.

---

## Slide 3. Methodology

**中文**

这篇文献综述一共纳入了 25 篇主要研究。文献来源包括初始搜索、backward snowballing、forward snowballing，以及额外的 venue search。Backward snowballing 是从已有论文的参考文献里继续找相关论文；forward snowballing 是找引用这些论文的新研究。这个流程帮助我从比较分散的研究中整理出一个更系统的 corpus。

**English**

For the methodology, I selected 25 primary studies.

The selection process included an initial search, backward snowballing, forward snowballing, and an extended venue search. Backward snowballing means checking the references of selected papers. Forward snowballing means finding newer papers that cite the selected papers.

This process helped me build a broader corpus, because the topic is quite fragmented. Some papers focus on flaky tests, some on UI test repair, some on fault localization, and others on vulnerability detection or testing agents.

One important note is that the methodology section should still be made fully consistent in the final written version, especially about the exact source of the initial search.

---

## Slide 4. Corpus Map

**中文**

我用五个 research questions 来组织这 25 篇论文。RQ1 关注测试挑战和根本原因。RQ2 关注检测、分析和定位方法。RQ3 关注 LLM 的使用方式，例如 fine-tuning、few-shot learning、prompt engineering 和 agents。RQ4 关注 evaluation 和 benchmark。RQ5 关注这些问题出现在哪些真实系统环境中，例如 CI/CD、IoT、微服务和开源项目。

**English**

I organized the review around five research questions.

RQ1 asks what testing challenges are reported, and what root causes are identified.

RQ2 asks what approaches are proposed to detect, analyze, or localize these problems.

RQ3 focuses on how LLMs are used, for example through fine-tuning, few-shot learning, prompt engineering, or agentic workflows.

RQ4 looks at evaluation, including datasets, benchmarks, and metrics.

RQ5 focuses on practical system contexts, such as CI/CD pipelines, IoT platforms, microservices, and open-source repositories.

This structure allows me to compare not only different methods, but also their evidence and limitations.

---

## Slide 5. RQ1 Findings

**中文**

RQ1 的主要发现是：测试挑战非常依赖具体生态和上下文。比如 JavaScript 中的 order-dependent flaky tests 很多和 shared mocking state 有关。UI test fragility 主要和 DOM、locator、timing 有关。IoT 平台的问题则和真实设备、firmware、低功耗模式有关。微服务测试的问题既有技术原因，比如 API 或 message format 不匹配，也有组织原因，比如服务 ownership 不清楚。

**English**

For RQ1, the main finding is that testing challenges are ecosystem-specific.

For flaky tests, one JavaScript study found 55 order-dependent tests, and many of them were caused by shared mocking state. This is a very framework-specific cause.

For UI tests, the main problems are DOM changes, locator failures, timing issues, and session-related problems.

For IoT platforms, the challenges are different again. They include device compatibility, firmware updates, and low-power behavior.

For microservices, the causes are both technical and organizational. There can be API mismatches or message format problems, but also unclear service ownership or weak team coordination.

So the key point is that testing problems cannot be fully understood without context.

---

## Slide 6. RQ2 Findings

**中文**

RQ2 关注解决方法。传统方法中，spectrum-based fault localization，比如 Tarantula 和 Ochiai，依赖测试覆盖率和 pass/fail 结果来给代码位置打 suspiciousness score。这些方法可解释性比较好，但依赖可靠的测试执行。后来的研究开始加入 compiler information 和 structural filtering。再往后，LLM-based fault localization 尝试直接从代码或 bug report 中预测 fault location，减少对测试执行的依赖。

**English**

RQ2 focuses on detection and analysis approaches.

Traditional spectrum-based fault localization methods, such as Tarantula and Ochiai, use test coverage and pass/fail results to rank suspicious code locations. These methods are interpretable, but they depend on reliable test execution.

Later work improves this direction by adding compiler information, type information, and structural filters.

More recent LLM-based approaches try to localize faults using source code, bug reports, or code representations. This reduces the dependency on test execution.

However, this also creates a new challenge. If a method uses less test evidence, then it needs stronger context design and stronger validation.

---

## Slide 7. RQ3 Findings

**中文**

RQ3 关注 LLM 的使用方式。Fine-tuning 通常在有足够 task-specific data 时效果更好，但成本更高。Few-shot learning 对数据要求较低，适合 labeled data 不多的情况。Prompt engineering 最灵活，不需要训练模型，但效果对 prompt 和 context 非常敏感。Agentic testing 则更接近真实开发流程，因为 agent 可以尝试安装依赖、运行测试、观察错误并修改命令。

**English**

RQ3 looks at how LLMs are used.

There are four main strategies in the reviewed papers.

First, fine-tuning. This can give strong results when enough task-specific data is available, but it is more expensive.

Second, few-shot learning. This is useful when labeled data is limited.

Third, prompt engineering. This is flexible and does not require training, but the result is very sensitive to the prompt and the context given to the model.

Fourth, testing agents. These are closer to real development workflows, because an agent can install dependencies, run tests, observe failures, and revise commands.

For my thesis, this suggests that model choice is not the only important factor. Context and validation are also central.

---

## Slide 8. RQ4 Findings

**中文**

RQ4 的主要发现是：很多 evaluation 仍然集中在 benchmark 或单一任务上。Fault localization 常用 Defects4J、Siemens、Space 等数据集。Flaky test 研究常用 IDoFT 和 FlakyCat。漏洞检测使用 OWASP、Juliet、CVEFixes 或 PrimeVul。UI test repair 使用 broken Selenium statements。这些 benchmark 很有价值，但它们通常不能完全代表真实 repo 中复杂的开发环境。

**English**

RQ4 focuses on evaluation and benchmarking.

Many studies use well-known benchmarks. Fault localization studies often use Defects4J, Siemens, or the Space program. Flaky test studies use datasets such as IDoFT and FlakyCat. Vulnerability detection studies use OWASP, Juliet, CVEFixes, or PrimeVul. UI test repair studies use broken Selenium statements.

These benchmarks are useful because they make comparison possible.

But they also have a limitation. They often evaluate one isolated task, while real repository workflows include bug reports, incomplete logs, dependency problems, build issues, and changing code history.

So the evidence is strong for some controlled tasks, but weaker for real-world repository-level fault localization.

---

## Slide 9. RQ5 Findings

**中文**

RQ5 关注真实系统上下文。这里一个重要发现是：在真实项目中，困难不只是“让模型判断哪里有 bug”。在这之前，系统需要拿到正确的 repo、正确的 commit、安装依赖、运行测试、收集日志和上下文。ExecutionAgent 这类研究说明，即使只是让不同项目的测试跑起来，本身也是一个复杂问题。所以 fault localization 应该被看作一个 repo-level workflow，而不是 code-only prediction。

**English**

RQ5 looks at practical system context.

A key finding is that in real projects, the hard part is not only asking the model where the bug is.

Before that, we need the correct repository, the correct commit, the dependencies, the build command, the test command, and the relevant logs or error messages.

Work such as ExecutionAgent shows that even running tests in arbitrary projects can be difficult.

This changes how I think about fault localization. It should not be treated only as a code prediction task. It should be treated as a repository-level workflow, where context collection and validation are part of the problem.

---

## Slide 10. Glasswing Reference

**中文**

文献综述中还讨论了 Glasswing 和 Mythos。这里要注意，它们不是 peer-reviewed primary studies，而是 industry reference 或 grey literature。它们的价值在于展示了一个 agent-plus-verifier 模式：一个 agent 先阅读代码、提出漏洞假设、运行验证并生成报告；另一个 agent 再独立验证结果。虽然它主要关注安全漏洞，但这个模式对普通 bug 的 fault localization 也有启发。

**English**

The review also discusses Glasswing and Mythos as a practical reference.

It is important to say that these are not peer-reviewed primary studies. They should be treated as industry reference or grey literature.

Still, they are useful because they show an agent-plus-verifier pattern. One agent reads the code, forms a hypothesis, runs experiments, and produces a report. Then another agent independently verifies the result.

This is mainly used for security vulnerability discovery. But the pattern is interesting for my thesis, because a similar idea may be useful for ordinary application-level bugs, such as business logic errors, state bugs, API misuse, or data processing bugs.

---

## Slide 11. Research Gaps

**中文**

最后，我总结出三个 research gaps。Gap A 是 LLM-based fault localization 缺少真实 repo-level validation。Gap B 是 agentic scaffolds 还没有充分应用到普通 application-level bugs。Gap C 是不同 context level 和 independent verification 对 fault localization 的影响还没有被系统比较。这三个 gap 指向同一个问题：LLM 方法需要在更真实的 repository setting 中被评估。

**English**

Based on the review, I identify three main research gaps.

Gap A is that LLM-based fault localization still lacks validation in real repository environments. Many results are still based on academic benchmarks.

Gap B is that agentic scaffolds have not been sufficiently applied to ordinary application-level bugs. Most agentic examples focus on security vulnerabilities.

Gap C is that the effect of context level and independent verification is still unclear. We do not yet know how much context is useful, or when an independent verifier improves the result.

Together, these gaps point to one central problem: LLM-based fault localization needs more repository-grounded evaluation.

---

## Slide 12. Next Step

**中文**

基于这篇文献综述，我后续 thesis 可以设计一个更聚焦的实验：使用真实 bug reports、buggy snapshots、source code context、repository history 和 verified fixing commits。然后比较不同 context conditions，例如只有 bug report，加入 logs，加入相关代码片段，或者加入 history。最后用 Top-k、MRR、recall 等指标评估 LLM 是否能定位到正确文件或方法。这样可以回答：什么上下文最有用？independent verification 是否真的有帮助？

**English**

Based on this literature study, my next step is to design a focused thesis experiment.

The idea is to use real bug reports, buggy repository snapshots, source-code context, repository history, and verified bug-fixing commits.

Then I can compare different context conditions. For example, one setting may only use the bug report. Another may add logs or stack traces. Another may add related code snippets or history.

The model or agent will rank suspicious files or methods. The result can be evaluated with metrics such as Top-k accuracy, MRR, or recall, using the verified fixing commit as ground truth.

This would help answer two practical questions: what context is most useful, and whether independent verification improves fault localization.

Thank you. I am happy to take questions.

---

# Short Backup Ending / 简短备用结尾

**中文**

总结一下，这篇文献综述说明，LLM 在软件测试中已经有很多潜力，但目前证据仍然偏 benchmark 和 isolated tasks。我的 thesis 将尝试把这个问题推进到更真实的 repository-level fault localization。

**English**

To summarize, this literature study shows that LLMs have strong potential in software testing, but much of the current evidence is still based on benchmarks and isolated tasks.

My thesis will try to move this direction toward real repository-level fault localization, with controlled context and validation.

Thank you.
