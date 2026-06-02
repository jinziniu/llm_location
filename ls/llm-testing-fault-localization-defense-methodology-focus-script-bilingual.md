# 15-Minute Defense Script

口语版 + 中文详细提示版

这版完全按 PPT 的 14 页结构来写，也对齐 literature study PDF 的核心结论：25 篇 primary studies、5 个 research questions、3 个 research gaps，最后引出 real-repository LLM-based fault localization。论文摘要和结论也明确指出，目前很多 LLM-based testing / fault localization 方法仍然停留在 academic benchmarks 或 isolated tasks，缺少真实开发环境验证。

---

## Slide 1. Title

### English - speak this

Good morning everyone. My name is Ziniu Jin, and today I’m going to present my literature study.

The topic is large language models for software testing and fault localization.

In this review, I’m mainly trying to answer two questions.

The first one is: what kinds of testing problems are discussed in recent software engineering research?

And the second one is: how are LLMs being used to help with these problems?

So I’m looking at tasks like detecting test problems, analyzing failures, localizing faults, repairing tests, and even using LLM agents for testing workflows.

Today, I will focus not only on the findings, but also on the methodology. So I will explain how I searched the literature, how I screened the papers, and how I synthesized the final results.

In total, I reviewed 25 primary studies, organized them with 5 research questions, and finally identified 3 main research gaps.

These gaps lead to my next thesis direction, which is LLM-based fault localization in real repository settings.

### 中文详细提示

这一页是开场，不要讲太快。你要让老师一开始就明白三件事：

第一，你的题目是 LLMs for software testing and fault localization。这里 software testing 是大范围，fault localization 是后面收束到 thesis 的方向。

第二，你不是简单讲“LLM 很厉害”，而是讲两个核心问题：

1. 现在 software testing 里到底有哪些问题？
2. LLM 现在被怎么用来解决或辅助这些问题？

第三，你今天的重点不只是 results，也包括 methodology。因为这是 literature study defense，老师很可能关心你怎么找文献、怎么筛选、怎么综合。所以开场就主动说：

not only what the papers say, but also how the literature was searched, screened, and synthesized.

这句话非常重要，和你的 PPT 第一页主旨一致。

这页最后要把三个数字讲清楚：

- 25 primary studies：说明 corpus 大小
- 5 research questions：说明分析框架
- 3 research gaps：说明最后贡献
- 最后落到 real repository settings：说明 thesis 方向

### 这一页中文理解

大家好，我是 Ziniu Jin。今天我讲我的 literature study，主题是大语言模型在软件测试和故障定位中的应用。

这篇综述想回答两个问题：第一，最近软件工程研究里讨论了哪些 testing problems；第二，LLM 被如何用于检测、分析、定位、修复这些问题，甚至用于 agentic testing workflow。

今天我不只是总结每篇 paper 的发现，也会重点解释我是怎么搜索文献、筛选文献、最后综合出 research gaps 的。

整篇综述包含 25 篇 primary studies，用 5 个 research questions 来组织，最后得到 3 个 research gaps。这些 gaps 引出了我后续 thesis 的方向：真实代码仓库环境下的 LLM-based fault localization。

### 过渡到下一页

Before explaining the search process, I first want to explain why this topic matters.

---

## Slide 2. Motivation

### English - speak this

The motivation for this study is that modern software testing is becoming more complex.

A testing failure is often not just a simple pass or fail signal.

In real projects, failures can depend on many things: the execution environment, shared state, system architecture, CI/CD pipelines, or the testing framework.

For example, flaky tests may fail because of asynchronous behavior, concurrency, or test order dependency.

UI tests may break because the DOM changes, a locator becomes invalid, or the page loads slightly differently.

And in microservice or IoT systems, the situation becomes even more complex, because testing may involve distributed services, devices, protocols, or even team coordination.

So the literature is quite fragmented. Some papers study flaky tests. Some study UI repair. Some study fault localization. Some study vulnerability detection. And some study testing agents.

That is why I wanted to bring these directions together.

The key idea is: if we want to use LLMs for software testing, we should not only ask whether the model understands code. We also need to ask whether it can work with real project context.

### 中文详细提示

这一页是 motivation。核心不是说“LLM 是热点”，而是说：testing 本身已经变复杂了，所以需要 systematic review 来整理。

你要强调：

现代 testing failure 不只是一个 test failed 这么简单。它背后可能有很多原因，比如：

- execution environment：运行环境不同，结果不同
- shared state：测试之间共享状态没有清理
- system architecture：系统架构复杂，比如 microservices
- CI/CD pipeline：在本地能跑，但 CI 上失败
- testing framework：比如 Jest、Selenium、Playwright、Cypress 各有自己的问题

举例时不用展开太多，每类讲一个就够：

Flaky tests：可能因为 async、concurrency、test order dependency。中文理解：代码没变，但测试一会儿 pass 一会儿 fail。

UI tests：可能因为 DOM 变了、locator 找不到、页面加载时间不同。中文理解：不是功能真的坏了，而是测试脚本跟不上 UI 变化。

Microservices / IoT：更复杂，因为涉及多个服务、设备、协议、硬件，甚至团队协作。中文理解：这种问题不是一行代码能解释的，必须看系统上下文。

这一页最后要引出你的核心观点：

LLM 不能只看 isolated code snippet。真实 testing 需要 real project context。

这为后面 real repository-level fault localization 铺路。

### 这一页中文理解

这篇综述的动机是：现代软件测试越来越复杂。测试失败不只是 pass/fail 信号，背后可能和运行环境、共享状态、系统架构、CI/CD、测试框架都有关系。

比如 flaky tests 可能是异步、并发、测试顺序导致；UI tests 可能是 DOM 或 locator 变化导致；microservices 和 IoT 还涉及分布式服务、真实设备、协议和团队协作。

所以相关文献很分散，有的研究 flaky tests，有的研究 UI repair，有的研究 fault localization，有的研究 vulnerability detection，有的研究 testing agents。我的 literature study 想把这些方向放到一个统一框架里看。

### 注意点

不要说：

LLM can solve these testing problems.

要说：

LLMs may help, but we need to understand whether they can work with real project context.

这样更稳。

### 过渡到下一页

Because the literature is fragmented, I needed a systematic search protocol.

---

## Slide 3. Literature Search Protocol

### English - speak this

To make the review more systematic, I started with a search protocol.

I used academic sources such as IEEE Xplore and ACM Digital Library, and I also used Google Scholar as a supplement.

The search terms covered two sides of the topic.

On one side, I used software testing terms, such as software testing, flaky test, fault localization, vulnerability detection, UI testing, and automation.

On the other side, I used LLM-related terms, such as large language model and LLM.

Then I combined these terms using Boolean search.

For example, I searched for combinations like “flaky test and LLM”, “fault localization and LLM”, and “security testing and LLM”.

The main point here is that the corpus was not chosen randomly.

I started broad, and then I refined the papers based on relevance, method detail, and evaluation evidence.

### 中文详细提示

这一页是 methodology 的第一部分。老师最关心的是：你的 25 篇 paper 是不是随便挑的？

所以你必须强调：

The corpus was not chosen randomly.

你的 search strategy 有三个层次：

第一，sources：

你用了 IEEE Xplore、ACM Digital Library，然后用 Google Scholar 作为补充。中文理解：主要用正式学术数据库，Google Scholar 用来补充查漏。

第二，keyword families：

关键词分成两组：

- testing side：software testing、flaky test、fault localization、vulnerability detection、UI testing
- LLM side：large language model、LLM

这样做的原因是：你的题目本来就是 testing problems + LLM solutions 的交叉。

第三，Boolean combinations：

比如：

- flaky test AND LLM
- fault localization AND LLM
- security testing AND LLM
- software testing OR test automation AND LLM

这说明你不是只搜一个词，而是通过组合覆盖不同方向。

### 这一页中文理解

为了让综述更系统，我先设计了 search protocol。我的文献来源包括 IEEE Xplore、ACM Digital Library，以及 Google Scholar 补充。

关键词分成两组：一组是 testing-related terms，比如 software testing、flaky test、fault localization、vulnerability detection、UI testing；另一组是 LLM-related terms，比如 large language model 和 LLM。

然后我用 Boolean search 把这些词组合起来，比如 “flaky test AND LLM”、“fault localization AND LLM”、“security testing AND LLM”。

这页最重要的是说明：我的 corpus 不是随便选出来的，而是从 broad search 开始，再根据 relevance、method detail 和 evaluation evidence 逐步 refined 出来的。

### 注意点

这里有一个潜在风险：你的 PDF methodology 里前面写了 database search，后面 snowballing 又写 initial search confined to ICST。这个如果老师问，你可以回答：

The initial seed set was mainly venue-focused, but the final corpus was expanded using backward snowballing, forward snowballing, and extended venue search. In the final written version, I should clarify this distinction more explicitly.

中文意思：初始 seed 主要来自 ICST，但最终 corpus 通过 snowballing 和 extended search 扩展了。最终版会把这个过程写得更清楚。

### 过渡到下一页

After retrieval, I needed clear screening criteria to decide which papers should be included.

---

## Slide 4. Screening Criteria

### English - speak this

After collecting candidate papers, I applied inclusion and exclusion criteria.

A paper was included if it was peer-reviewed, directly related to software testing or fault localization, and proposed a method for detection, analysis, localization, or repair.

For LLM-based papers, I also checked whether the paper clearly explained how the model was used, and how the method was evaluated.

I excluded papers if they were not peer-reviewed, only indirectly related, purely conceptual without empirical evaluation, or duplicated by a more complete version.

One important detail is about Glasswing and Mythos.

I discuss them later in the presentation, but they are not part of the 25 primary studies.

I treat them as grey literature, or industry reference, because they are useful for practical framing, but they are not peer-reviewed academic evidence.

### 中文详细提示

这一页是 methodology 的第二个重点：筛选标准。

老师可能会问：

Why did you include this paper and exclude that one?

这一页就是回答这个问题。

你纳入 paper 的标准大概有五点：

1. 必须 peer-reviewed。中文理解：正式期刊、会议、workshop paper。
2. 必须和 software testing / fault localization 直接相关。不是所有 LLM for code 的 paper 都算。
3. 必须提出 detection、analysis、localization 或 repair 方法。也就是说，它要和 testing-related problem 的处理有关。
4. 如果是 LLM-based paper，必须说明模型怎么用。比如 fine-tuning、few-shot、prompt engineering、agent workflow。
5. 必须有 evaluation。不能只是说一个想法，没有实验或方法细节。

排除的标准：

- non-peer-reviewed：比如 blog、white paper、technical report
- only indirectly related：只是泛泛讲 LLM 或 software engineering
- purely conceptual：没有 empirical evaluation
- duplicates：有更新/更完整版本时，只保留一个

### Glasswing 重点

这一页一定要说清楚 Glasswing。因为你后面会讲 Glasswing，但 Glasswing 不是 peer-reviewed primary study。

你的说法要非常稳：

Glasswing is discussed as grey literature, not counted as one of the 25 primary studies.

中文意思：

Glasswing 只是作为 industry reference / practical reference，用来启发 workflow pattern，不是 SLR corpus 里的 peer-reviewed evidence。

### 这一页中文理解

收集 candidate papers 之后，我用了明确的 inclusion 和 exclusion criteria。纳入的 paper 需要 peer-reviewed、和 testing 或 fault localization 直接相关，并且提出 detection、analysis、localization 或 repair 方法。如果是 LLM-based paper，还要清楚说明模型怎么用，以及怎么 evaluation。

排除的 paper 包括非 peer-reviewed、只间接相关、只有概念没有实验、或者和更完整研究重复的 paper。

Glasswing 和 Mythos 后面会讨论，但它们不是 25 篇 primary studies。它们属于 grey literature，只用于 practical framing。

### 过渡到下一页

After applying these criteria, I also used snowballing to expand the corpus.

---

## Slide 5. Snowballing and Selection Results

### English - speak this

The final corpus contains 25 primary studies.

The process started with 9 seed papers.

Then I used backward snowballing. This means I checked the references of the seed papers to find earlier relevant work.

From backward snowballing, I found 18 candidate studies, and 8 of them were included.

I also used forward snowballing. This means I looked for newer papers that cited the seed studies.

This step gave 7 candidate papers, and 3 were included.

Finally, I used an extended venue search, which added 5 more studies.

So in the end, the review is based on 25 studies.

One limitation I want to mention is that the current written version should report the initial candidate count more clearly.

The final corpus is clear, but for better reproducibility, the candidate count in the initial search should be clarified in the final version.

### 中文详细提示

这一页是 selection pipeline。你要讲得自然一点，不要像在念表格。

先说结果：

The final corpus contains 25 primary studies.

然后解释怎么来的。

Initial search：9 included

这是你的 seed papers，也就是最初的核心论文集合。

Backward snowballing：18 candidates, 8 included

Backward snowballing 是看 seed papers 的 reference list。中文理解：看看这些核心论文引用了哪些以前的研究，从里面继续找相关文献。

这个方法的作用是补基础文献，比如 Tarantula、Ochiai、flaky test foundational papers。

Forward snowballing：7 candidates, 3 included

Forward snowballing 是看哪些后来的论文引用了 seed papers。中文理解：看看这个方向后续发展出了哪些新研究。

这个方法的作用是补更近的研究，比如 LLM fault localization、testing agents、repair 等。

Extended venue search：5 included

这个是额外 venue search，补充一些和 benchmark quality、repository-level testing、industrial flaky tests 有关的研究。

### 主动承认 limitation

这里你 PPT 上已经写了：

candidate count missing in draft

你要主动说。不要等老师问。

推荐说法：

The final corpus is clear, but the initial candidate count should be reported more clearly in the final written version.

中文意思：

最终纳入 25 篇是清楚的，但最开始搜索到了多少 candidate，当前 draft 里写得不够完整。最终版我会补清楚，这样 reproducibility 更好。

这种说法很安全，因为你承认了一个小 limitation，但没有否定整个 methodology。

### 这一页中文理解

最终 corpus 是 25 篇 primary studies。流程从 9 篇 seed papers 开始，然后做 backward snowballing，从 seed papers 的 references 里找早期相关研究；这个步骤发现 18 篇 candidates，纳入 8 篇。接着做 forward snowballing，用 Google Scholar 找引用 seed papers 的后续研究；这个步骤发现 7 篇 candidates，纳入 3 篇。最后 extended venue search 增加 5 篇。

当前 draft 的一个 methodology limitation 是 initial candidate count 没有写得足够清楚。最终 corpus 没问题，但为了 reproducibility，最终 written version 应该补充这个数字。

### 过渡到下一页

After selecting the studies, I needed a consistent way to compare them. That is where the five research questions come in.

---

## Slide 6. Data Extraction and Synthesis

### English - speak this

After selecting the papers, I did not simply summarize them one by one.

Instead, I used the same five research questions to extract information from each paper.

RQ1 looks at the testing challenge, the root cause, and the system context.

RQ2 looks at the proposed approach, for example detection, localization, or repair.

RQ3 looks at how LLMs are used, such as fine-tuning, few-shot learning, prompting, or agents.

RQ4 looks at evaluation, including datasets, metrics, and baselines.

And RQ5 looks at practical context, such as CI/CD, IoT, microservices, and real repositories.

So the five research questions are not just labels. They are the structure I used to compare the papers.

This helped me move from a list of papers to a thematic synthesis.

### 中文详细提示

这一页非常重要，因为它解释你怎么从 25 篇 paper 得到 findings 和 gaps。

你要强调：

I did not summarize them one by one.

中文意思：我不是每篇论文讲两句，那样只是 annotated bibliography，不是 synthesis。

你的方法是：

每篇 paper 都用同样的 5 个 RQ 去提取信息。

RQ1：Challenge / root cause / system context

这篇 paper 研究的 testing problem 是什么？根本原因是什么？在哪种系统环境里？

RQ2：Approach

它提出了什么方法？是 detection、localization、repair、classification，还是 agent workflow？

RQ3：LLM use

如果用 LLM，它怎么用？fine-tuning、few-shot、prompt engineering、agent？

RQ4：Evaluation

它怎么评估？用什么 dataset？什么 metrics？有没有 baseline？

RQ5：Practice

它在哪种真实 context 下 relevant？CI/CD、IoT、microservices、open-source repo、industrial system？

### 这一页的核心作用

它把 paper list 变成 thematic synthesis。

中文理解：

我不是逐篇总结，而是把所有文献放进同一个分析框架里，这样可以比较它们研究了什么问题、用了什么方法、在哪里评估、有什么局限。

### 注意点

这页可以说得稍微慢一点，因为老师会关心你的 SLR 是否 structured。

### 过渡到下一页

Now I will go through the main findings, starting with RQ1.

---

## Slide 7. RQ1 Findings

### English - speak this

For RQ1, the main finding is that testing challenges are very context-specific.

The same term, like flaky test, can mean different things in different ecosystems.

For example, one JavaScript study found 55 order-dependent tests. And 42 of them were caused by shared mocking state.

This is interesting because this cause is very specific to the JavaScript and Jest ecosystem.

For UI testing, the main issues are DOM changes, locator failures, timing problems, and session-related problems.

For IoT platforms, the problems are different again. They involve device compatibility, firmware updates, physical devices, and low-power behavior.

For microservices, the causes are both technical and organizational. There can be API mismatches and message format problems, but also unclear service ownership or weak team coordination.

So the takeaway is that testing problems cannot be fully understood without context.

And this is important for my thesis, because it suggests that fault localization also needs repository context, not only isolated code snippets.

### 中文详细提示

这一页是 RQ1：testing challenges and root causes。

你要让老师记住一句话：

Testing challenges are ecosystem-specific rather than universal.

中文意思：

testing 问题不是所有系统都一样，它和语言、框架、架构、运行环境有关。

### 例子 1：Flaky tests

你可以讲 JavaScript/Jest 的例子。

55 个 order-dependent tests，其中 42 个由 shared mocking state 导致。

这说明什么？

在 Java/Python 研究里，可能没有这么突出地发现 shared mocking state；但在 JavaScript/Jest 里，它很重要。这就说明 root cause 是 ecosystem-specific 的。

中文解释：

同样叫 flaky test，但在不同技术生态中，它背后的原因可能完全不一样。

### 例子 2：UI fragility

UI tests 容易坏，主要因为：

- DOM changes
- locator failures
- timing issues
- session-related problems

中文理解：

UI test 不是因为功能一定坏了，而是 UI 页面结构变化、元素定位变化、加载时间变化，都会让测试脚本失败。

### 例子 3：IoT

IoT 的问题完全不同：

- device compatibility
- firmware updates
- physical devices
- low-power behavior

中文理解：

IoT 测试依赖真实设备、固件、低功耗模式、网络稳定性，所以普通软件测试工具未必适用。

### 例子 4：Microservices

Microservices 的问题有两类：

Technical causes：API mismatch、message format problems

Organizational causes：unclear service ownership、weak team coordination

中文理解：

微服务的 testing problem 不只是代码或接口问题，也可能是团队之间边界不清、服务 ownership 不明确导致的。

### 这一页最后一定要落到 thesis

你要说：

This suggests that fault localization also needs repository context, not only isolated code snippets.

中文意思：

如果 testing problem 本身依赖上下文，那么 fault localization 也不能只看一小段代码，而应该看 repository-level context。

### 过渡到下一页

After identifying the challenges, RQ2 looks at the methods proposed to detect or localize them.

---

## Slide 8. RQ2 Findings

### English - speak this

RQ2 looks at the approaches used to detect, analyze, or localize testing problems.

A traditional line of work is spectrum-based fault localization, or SBFL.

Methods like Tarantula and Ochiai use test coverage and pass/fail results to rank suspicious code locations.

The good thing is that these methods are quite interpretable. The suspiciousness score is connected to how the tests executed the code.

But the limitation is also clear. They need reliable test execution and useful coverage information.

Some later work improves SBFL by adding compiler information, type information, or structural filters.

More recent LLM-based approaches try to localize faults using source code, bug reports, or code representations.

This can reduce the dependency on test execution signals.

But there is a trade-off.

If we use less execution evidence, then the model depends more on the context we give it, and on how we validate its answer.

So my takeaway from RQ2 is: LLM-based fault localization is promising, but context design and validation become much more important.

### 中文详细提示

这一页是 RQ2：detection and analysis approaches。

你要讲一个方法演化：

从 traditional execution-based methods 到 LLM-based code/context reasoning。

### 传统方法：SBFL

SBFL = spectrum-based fault localization。

代表方法：

- Tarantula
- Ochiai

它们怎么做？

它们用 test coverage 和 pass/fail results 给代码位置打 suspiciousness score。

中文理解：

如果某一行代码经常被 failing tests 执行，但很少被 passing tests 执行，那它就更 suspicious。

### SBFL 的优点

优点是 interpretable。

中文理解：

它为什么认为某行代码可疑，是能解释的，因为这个分数来自测试覆盖和测试结果。

### SBFL 的缺点

缺点是依赖 reliable test execution 和 coverage。

中文理解：

如果测试本身 flaky，或者 coverage 不完整，或者项目根本跑不起来，那 SBFL 就很难用。

### 后续改进

一些研究加入 compiler information、type information、structural filters。

中文理解：

不是所有被覆盖到的代码都同样有用，所以可以用编译器信息和结构信息先过滤掉不太相关的 program elements。

### LLM-based fault localization

LLM 方法尝试用 source code、bug reports、code representations 来定位 fault。

中文理解：

它不一定完全依赖测试覆盖，而是通过代码语义、bug 描述、上下文来判断哪里可疑。

### 这一页最关键的 trade-off

你一定要讲清楚这句话：

Less execution evidence means stronger need for context design and validation.

中文意思：

LLM 方法减少了对 test execution 的依赖，但它不是没有代价。代价是它更依赖你给什么 context，以及怎么验证它的答案。

这句话非常适合答辩。

### 过渡到下一页

RQ3 then looks more specifically at how LLMs are used in these studies.

---

## Slide 9. RQ3 Findings

### English - speak this

RQ3 focuses on how LLMs are used in the reviewed papers.

I found four main strategies.

The first one is fine-tuning.

Fine-tuning can work well when there is enough task-specific data, but it is more expensive and usually needs labeled datasets.

The second one is few-shot learning.

This is useful when labeled data is limited, because the model can work with only a small number of examples.

The third one is prompt engineering.

This is flexible, because we do not need to train the model. But the result can change a lot depending on the prompt and the context.

The fourth one is testing agents.

Agents are closer to real development workflows, because they can do more than answer one question. They can install dependencies, run tests, observe errors, revise commands, and continue the process.

For my thesis, the important lesson is that model choice is not the only factor.

The context, the repository state, and the validation setup may be just as important.

### 中文详细提示

这一页是 RQ3：LLM 怎么被使用。

你要把 LLM usage 分成四类讲：

### 1. Fine-tuning

Fine-tuning 是在 task-specific data 上继续训练模型。

优点：

- 数据充足时效果可能很好
- 适合特定任务，比如 flaky test classification、fault localization

缺点：

- 需要 labelled data
- 成本高
- 很多 evidence 仍然来自 benchmark

中文理解：

Fine-tuning 就是让模型专门适应一个任务，但前提是你有足够训练数据。

### 2. Few-shot learning

Few-shot learning 是用少量 examples 引导模型。

优点：

- labeled data 少时有用
- 成本比 fine-tuning 低

中文理解：

当你没有很多标注数据时，few-shot learning 是一个更现实的选择。

### 3. Prompt engineering

Prompt engineering 不训练模型，只设计输入。

优点：

- 灵活
- 不需要训练数据
- 可以快速尝试不同 context

缺点：

- 对 prompt 很敏感
- 同一个模型换个 prompt，结果可能变化很大

中文理解：

prompt engineering 很方便，但也不稳定，因为模型表现很依赖你怎么问、给了什么上下文。

### 4. Testing agents

Testing agents 更接近真实开发 workflow。

它们不只是回答问题，还可以：

- install dependencies
- run tests
- observe errors
- revise commands
- continue the workflow

中文理解：

Agent 更像一个自动测试助手，可以和项目环境交互，而不是只给一个静态答案。

### 这一页最后的 thesis implication

你要强调：

Model choice is not the only factor.

中文意思：

不是只要换一个更强模型就够了。context、repository state、validation setup 可能同样重要。

这句话能很好地连接到你的 thesis 设计。

### 过渡到下一页

After looking at the methods, I also looked at how these methods are evaluated.

---

## Slide 10. RQ4 Findings

### English - speak this

RQ4 looks at evaluation and benchmarking.

A lot of studies use well-known benchmarks.

For fault localization, common datasets include Defects4J, Siemens, and the Space program.

For flaky tests, studies often use IDoFT and FlakyCat.

For vulnerability detection, datasets include OWASP, Juliet, CVEFixes, and PrimeVul.

And for UI test repair, some studies use broken Selenium statements.

These benchmarks are useful. They make controlled comparison possible.

But they also have a limitation.

They often evaluate one isolated task.

In real repositories, the workflow is more complicated. We may have bug reports, incomplete logs, dependency problems, build failures, changing code history, and CI/CD constraints.

So the evidence is quite strong for controlled benchmark tasks, but weaker for real repository-level fault localization.

This is one of the main reasons why my thesis direction focuses on real repositories.

### 中文详细提示

这一页是 RQ4：evaluation and benchmarking。

你要讲得平衡，不要说 benchmark 没用。正确态度是：

Benchmarks are useful, but not enough.

### Benchmark 的价值

Benchmark 的优点是 controlled comparison。

中文理解：

所有方法在同一个 dataset、同一套 metrics 上比较，这样结果更可比。

常见 benchmark：

Fault localization：Defects4J、Siemens、Space

Flaky tests：IDoFT、FlakyCat

Vulnerability detection：OWASP、Juliet、CVEFixes、PrimeVul

UI test repair：broken Selenium statements

### Benchmark 的限制

问题是很多 benchmark 只评估 isolated task。

中文理解：

它可能只问“模型能不能在给定数据集里找到 fault”，但真实项目中还会有很多额外问题。

真实 repository workflow 里可能有：

- bug reports
- incomplete logs
- dependency problems
- build failures
- changing code history
- CI/CD constraints

### 这一页核心结论

Evidence is strong for controlled benchmark tasks, but weaker for real repository-level fault localization.

中文意思：

现有研究在 benchmark 上有证据，但在真实仓库中的证据还不够。

这就是你 thesis 方向的直接来源之一。

### 过渡到下一页

RQ5 goes one step further and looks at what happens in practical system contexts.

---

## Slide 11. RQ5 Findings

### English - speak this

RQ5 looks at practical system context.

This is where the review becomes very relevant to my thesis.

In real projects, the hard part is not only asking the model: where is the bug?

Before we can even ask that question, we need the correct repository, the correct commit, the dependencies, the build command, the test command, and the relevant logs or error messages.

Some work, such as ExecutionAgent, shows that even running tests in arbitrary open-source projects can be difficult.

The agent may need to install dependencies, build the project, run tests, observe failures, and revise commands.

So this changes how I think about fault localization.

It should not be treated only as a code prediction task.

It should be treated as a repository-level workflow.

That means context collection and validation are part of the research problem.

### 中文详细提示

这一页是最接近你 thesis 的 findings。一定要讲慢一点。

核心转变是：

from code-only prediction to repository-level workflow.

中文意思：

fault localization 不应该只是“给模型一段代码，让它猜哪里错了”，而应该看成一个真实仓库中的 workflow。

### 真实项目里需要什么？

在问模型 bug 在哪里之前，首先要有：

- correct repository
- correct commit
- dependencies
- build command
- test command
- logs / error messages

中文理解：

真实项目不是一段干净的代码片段，而是一个有版本、有依赖、有构建过程、有测试环境的完整 repository。

### ExecutionAgent 的意义

ExecutionAgent 说明：即使只是让任意 open-source project 的 tests 跑起来，本身也很难。

它可能需要：

- install dependencies
- build project
- run tests
- observe failures
- revise commands

中文理解：

在真实环境里，困难不只是分析失败，而是项目能不能正确配置、构建和运行。

### 这一页怎么连接 thesis？

你可以强调：

This makes fault localization a repository-level workflow problem.

中文意思：

所以我的 thesis 不能只研究模型预测，还要研究 context collection 和 validation。

### 过渡到下一页

Besides academic studies, I also discuss one practical reference: Glasswing.

---

## Slide 12. Practical Reference - Glasswing

### English - speak this

The review also discusses Glasswing and Mythos.

Again, I want to be careful here.

They are not peer-reviewed primary studies. I treat them as grey literature, or industry reference.

So I do not use them as proof that LLMs can solve ordinary fault localization.

Instead, I use them to motivate a useful workflow pattern.

The pattern is agent plus verifier.

One agent reads the code, forms a hypothesis, runs experiments, and produces a report.

Then another agent independently checks whether the issue is reproducible and whether it has real impact.

Glasswing mainly focuses on security vulnerability discovery.

But this pattern is interesting for my thesis, because ordinary application bugs may also benefit from a similar process.

For example, the bug could be a business logic error, a state bug, API misuse, or a data processing failure.

So the question is not: does Glasswing directly solve my problem?

The question is: can this agent-plus-verifier pattern be adapted and evaluated for repository-level fault localization?

### 中文详细提示

这一页一定要谨慎，因为 Glasswing 不是 peer-reviewed academic paper。

你要先防守：

They are not peer-reviewed primary studies.

中文意思：

Glasswing 和 Mythos 不属于 25 篇 primary studies。它们是 grey literature / industry reference。

### 为什么还要讲 Glasswing？

因为它提供了一个 practical workflow pattern：

agent plus verifier

这比单纯 benchmark prediction 更接近真实环境。

### agent plus verifier 是什么？

第一步：Discovery agent

它读代码、提出假设、运行实验、生成报告。

第二步：Independent verifier

另一个 agent 独立检查问题是否真实、是否可复现、是否有实际影响。

中文理解：

一个 agent 负责发现问题，另一个 agent 负责验证问题。这可以减少 hallucination 或 false positive 的风险。

### Glasswing 的限制

Glasswing 主要关注 security vulnerability discovery，不是 ordinary application-level fault localization。

所以不能说：

Glasswing proves LLMs can localize bugs.

你应该说：

Glasswing motivates a workflow pattern.

中文意思：

它不是证明我的问题已经被解决，而是启发我考虑 agent + verifier 这种结构是否能迁移到普通 bug localization。

### 为什么和 thesis 有关？

普通 application-level bugs 可能包括：

- business logic errors
- state bugs
- API misuse
- data processing failures

这些和 security vulnerability 不一样，所以需要单独研究。

### 这一页核心句

The question is not whether Glasswing directly solves my problem. The question is whether this pattern can be adapted and evaluated.

中文意思：

重点不是 Glasswing 是否直接解决我的问题，而是它的模式能否被迁移并评估。

### 过渡到下一页

Based on all these findings, I summarize three research gaps.

---

## Slide 13. Discussion - Three Gaps

### English - speak this

Based on the review, I identify three main research gaps.

The first gap is that LLM-based fault localization still lacks validation in real repository environments.

Many existing studies are still evaluated on academic benchmarks, such as Defects4J-style settings.

The second gap is that agentic scaffolds have not been sufficiently applied to ordinary application-level bugs.

Most agentic examples focus on security vulnerabilities, but ordinary bugs can be different. They may involve business logic, state synchronization, API usage, or data processing.

The third gap is that we still do not clearly know the effect of context level and independent verification.

For example, how much context should we give to the model?

Should we give only the bug report?

Should we add logs, stack traces, code snippets, or repository history?

And does an independent verifier actually improve the result?

These gaps all point to the same central problem.

LLM-based fault localization needs to be evaluated in a more realistic, repository-grounded setting.

### 中文详细提示

这一页是整场答辩最重要的结论页。三个 gaps 一定要背熟。

### Gap A：缺少 real repository-level validation

英文：

LLM-based fault localization still lacks validation in real repository environments.

中文理解：

现有 LLM fault localization 研究很多还是在 Defects4J 这类 benchmark 上做，真实仓库环境下的系统验证还不够。

为什么重要？

因为真实 repository 有：

- noisy bug reports
- incomplete logs
- multiple files
- dependencies
- build issues
- evolving code history

这些 benchmark 不一定覆盖。

### Gap B：agentic scaffold 还没充分用于普通 bugs

英文：

Agentic scaffolds have not been sufficiently applied to ordinary application-level bugs.

中文理解：

agent workflow 现在更多在 security vulnerability discovery 里展示，但普通 application bugs 还没被充分研究。

普通 bug 可能是：

- business logic error
- state synchronization bug
- API misuse
- data processing bug

这些和 security vulnerability 不同，不能直接假设 Glasswing-style workflow 一定有效。

### Gap C：context level 和 independent verification 的影响不清楚

英文：

The effect of context level and independent verification is still unclear.

中文理解：

我们还不知道应该给模型多少上下文，也不知道 verifier 是否真的有帮助。

可以问：

- 只给 bug report 够不够？
- 加 logs 会不会更好？
- 加 stack traces 有没有帮助？
- 加 related code snippets 会不会提升 Top-k？
- repository history 是否有用？
- independent verifier 能不能减少 false positives？

### 三个 gap 怎么合在一起？

这三个 gap 都指向同一个 central problem：

LLM-based fault localization needs repository-grounded evaluation.

中文意思：

LLM fault localization 需要在更真实的 repository setting 里评估，而不是只在 benchmark 或 isolated tasks 里评估。

### 过渡到下一页

These gaps lead directly to my next thesis step.

---

## Slide 14. Next Step

### English - speak this

Based on this literature study, my next step is to design a more focused thesis experiment.

The idea is to use real bug reports, buggy repository snapshots, source-code context, repository history, and verified bug-fixing commits.

Then I can compare different context settings.

For example, one setting may use only the bug report.

Another setting may add logs or stack traces.

Another one may add related code snippets.

And another one may include repository history or previous fixing commits.

The model or agent can then be asked to rank suspicious files or methods.

I can evaluate the result using metrics such as Top-k accuracy, MRR, and recall, with the verified fixing commit as ground truth.

This experiment would help answer two practical questions.

First, which repository-level context actually helps LLM-based fault localization?

Second, does independent verification improve localization accuracy or reduce false positives?

So to conclude, this literature study shows that LLMs have strong potential in software testing.

But much of the current evidence is still based on benchmarks and isolated tasks.

My thesis will try to move this direction toward real repository-level fault localization, with controlled context and validation.

Thank you. I’m happy to take questions.

### 中文详细提示

这一页是结尾，也是 thesis direction。

你要说：literature study 不是停在总结文献，而是引出一个可以做的 thesis experiment。

### Dataset

你后续 thesis 可以用：

- real bug reports
- buggy repository snapshots
- source-code context
- repository history
- verified bug-fixing commits

中文理解：

数据不是人工 benchmark 里的孤立样本，而是真实 bug report、真实出错版本、真实修复 commit。

### Context conditions

你可以比较不同上下文设置：

Setting 1：bug report only

只给模型 bug report。

Setting 2：bug report + logs / stack traces

加入错误日志或 stack trace。

Setting 3：bug report + related code snippets

加入相关代码片段。

Setting 4：bug report + code + history

加入 repository history 或 previous fixing commits。

中文理解：

这样可以做 ablation study，比较到底哪种 context 最有用。

### Task

让 LLM 或 agent 做什么？

rank suspicious files or methods

中文理解：

让模型给出最可疑的文件或方法排名，而不是直接生成 patch。

这样评估更清楚，也更适合 fault localization。

### Evaluation

用什么 metrics？

- Top-k accuracy
- MRR
- recall

ground truth 是 verified fixing commit。

中文理解：

如果 fixing commit 修改了某些文件或方法，那么这些位置可以作为正确答案，用来判断模型有没有定位对。

### Thesis questions

你的 thesis 可以回答两个实际问题：

第一：

Which repository-level context actually helps?

中文：哪种上下文最有帮助？

第二：

Does independent verification improve accuracy or reduce false positives?

中文：独立验证是否真的能提高定位准确率，或者减少错误判断？

### 最后总结

结尾不要过度 claim。你要说：

LLMs have potential, but current evidence is still benchmark-based.

中文意思：

LLM 有潜力，但现有证据还主要停留在 benchmark 和 isolated tasks。

最后落到：

My thesis moves toward real repository-level evaluation.

中文意思：

我的 thesis 会把这个问题推进到更真实的 repository-level fault localization。

---

## 超时备用结尾

如果讲到最后时间不够，Slide 14 可以直接用这个短版：

### English

To summarize, this literature study shows that LLMs have strong potential in software testing, but much of the current evidence is still based on benchmarks and isolated tasks.

The central gap is real repository-level validation.

So my thesis will focus on LLM-based fault localization using real bug reports, source-code context, repository history, and verified bug-fixing commits.

Thank you. I’m happy to take questions.

### 中文理解

总结一下，这篇 literature study 说明 LLM 在 software testing 中有潜力，但目前很多证据仍然停留在 benchmark 和 isolated tasks。

核心 gap 是缺少 real repository-level validation。

所以我的 thesis 会关注真实 bug reports、source-code context、repository history 和 verified bug-fixing commits 下的 LLM-based fault localization。

---

## 最该背熟的中文逻辑链

你答辩时只要记住这条中文逻辑，就不容易乱：

第一步：为什么做这个 literature study？

因为现代 software testing 问题很复杂，而且文献分散在 flaky tests、UI repair、fault localization、vulnerability detection、testing agents 等不同方向。

第二步：我怎么做？

我用了 search protocol、inclusion/exclusion criteria、backward and forward snowballing，最后选出 25 篇 primary studies。

第三步：我怎么分析？

我不是逐篇总结，而是用 5 个 RQ 对每篇 paper 编码：challenge、approach、LLM use、evaluation、practical context。

第四步：我发现了什么？

testing challenges 很依赖上下文；传统方法依赖 test execution；LLM 方法有潜力，但更依赖 context design 和 validation；很多 evaluation 仍然停留在 benchmark 或 isolated task。

第五步：gap 是什么？

LLM-based fault localization 缺少真实 repository-level validation；agentic scaffold 还没有充分用于普通 application-level bugs；context level 和 independent verification 的影响还不清楚。

第六步：thesis 做什么？

用真实 bug reports、buggy snapshots、source-code context、repo history、verified fixing commits 来评估 LLM-based fault localization，并比较不同 context 和 verification strategy。

---

## 最适合答辩时临场救场的 10 句英文

1. The corpus was not chosen randomly.
2. I used search criteria, screening criteria, and snowballing to build the final corpus.
3. The five research questions were used as the extraction framework.
4. Modern testing failures are not just pass or fail signals.
5. Testing problems are highly context-dependent.
6. Traditional SBFL methods are interpretable, but they depend on reliable test execution.
7. LLM-based methods reduce some dependency on test execution, but they need stronger context and validation.
8. Benchmarks are useful, but they do not fully capture real repository workflows.
9. Glasswing is grey literature, not one of my primary studies.
10. The central gap is real repository-level validation for LLM-based fault localization.
