# Actually, We've Always Been Terrible at This

**A data-driven look at "The Vibe Tax" — and why technical debt might not be AI's fault.**

---

There's a popular narrative going around about the "Vibe Tax" — the idea that AI-generated code is flooding the market with unvalidated garbage and driving up technical debt. It's a compelling argument. Easy to nod along to.

But I started wondering: is this actually new? Or have we always been drowning in technical debt, long before ChatGPT was a twinkle in anyone's eye?

So I did what any reasonable person would do. I wrote a Python script, hit the GitHub API, and pulled data on 300 popular repositories. Because nothing settles an argument like a Saturday afternoon of data analysis.

## The Numbers Don't Lie (But They Do Hurt)

Here's what I found when I compared repos created **before** January 2022 (pre-AI coding tools) versus **after**:

| What I Measured | Pre-AI Era | Post-AI Era |
|-----------------|------------|-------------|
| Repos Analyzed | 150 | 150 |
| Issues per 1,000 Stars | **13.36** | 12.47 |
| Issue Close Rate | 90.3% | 70.0% |
| Avg Contributors | 865 | 207 |

Read that first data row again. **Pre-AI repositories have a higher issue-to-star ratio than post-AI ones.**

The repos built by experienced engineers before AI tools went mainstream actually have *more* technical debt per unit of popularity than newer ones.

## But Wait, There's More: NLP Analysis

I wasn't satisfied with just counting issues. I wanted to look inside the commits themselves. So I pulled 18,000+ commit messages from 40 repositories and ran NLP analysis looking for signals of debt, frustration, and code quality.

| What Developers Write | Pre-AI Era | Post-AI Era |
|-----------------------|------------|-------------|
| Commits Analyzed | 9,555 | 9,026 |
| **Debt signals** (TODO, HACK, FIXME) per 100 | **2.51** | 1.20 |
| **Frustration signals** (wtf, stupid, ugh) per 100 | **0.29** | 0.04 |
| **Positive signals** (refactor, improve, clean) per 100 | 7.94 | **18.03** |
| Avg commit message length | 166 chars | **285 chars** |

Pre-AI developers left **twice as many** TODO/HACK/FIXME markers in their commits. They expressed frustration **seven times more often**. And post-AI commits contain **twice as many** positive signals like "refactor" and "improve."

The cherry on top? Post-AI commit messages are nearly twice as long on average. More context. More explanation. Better documentation.

If AI were teaching developers bad habits, we'd see the opposite pattern.

## The Hall of Shame

Let's look at which repositories have the most issues relative to their popularity:

1. **pytorch/pytorch** — 186 issues per 1K stars (created 2016)
2. **python/cpython** — 131 issues per 1K stars (created 2017)  
3. **microsoft/vscode** — 82 issues per 1K stars (created 2015)
4. **golang/go** — 74 issues per 1K stars (created 2014)
5. **elastic/elasticsearch** — 71 issues per 1K stars (created 2010)

These aren't vibe-coded MVPs built by founders who asked ChatGPT to center a div. These are foundational projects. The Python interpreter. The Go compiler. VS Code — the editor you're probably reading this in.

They were all built by humans. Expert humans. And they're drowning in issues.

## "But Wait," You Say

I can already hear the objections:

**"Older repos have more time to accumulate issues!"**

Sure. They've also had more time to *close* them. Pre-AI repos have a 90% close rate versus 70% for newer ones. These are mature projects with dedicated maintainers who've been fighting the debt dragon for years. They're still losing.

**"Big projects attract more issues!"**

That's... literally my point. Technical debt scales with complexity, not with whether a human or AI wrote the code. The issue isn't *who* writes the code. It's that software is fundamentally a liability that requires ongoing maintenance.

**"These are apples and oranges!"**

The search criteria were identical. Same minimum star count. Same languages. Same API. The only difference is the creation date. If anything, post-AI repos are at a disadvantage because they're younger and haven't had time to close issues yet. And they're *still* showing lower debt ratios.

## The Real Problem

The "Vibe Tax" article describes real symptoms. I've seen the Frankenstein codebases. I've audited the 50MB todo apps. I've watched juniors install a library to check if a number is odd.

But here's the thing: I saw all of that *before* AI coding tools existed.

The junior who installs `is-odd` from npm isn't doing it because ChatGPT told them to. They're doing it because they don't know better yet. That's what being a junior means. The solution isn't to ban AI — it's the same solution it's always been: code review, mentorship, and time.

The "Frankenstein codebase" with three different date formatting approaches? I've seen those in codebases that predate GitHub. That's not a vibe tax. That's what happens when multiple developers touch the same project over time without strong conventions. It's called "working in software."

## The Uncomfortable Truth

Technical debt isn't a new phenomenon caused by AI. It's an inherent property of software development. Every line of code you write is a liability. Every dependency you add is a risk. Every feature you ship is a maintenance burden.

PyTorch has 865 contributors on average. These are smart people. PhD-level smart. They still have 17,800 open issues. Not because they're lazy or careless, but because building complex software generates issues faster than any team can close them.

If the Python interpreter itself — written by some of the best programmers on the planet over decades — can't escape technical debt, maybe the problem isn't that some founder used Cursor to build their MVP.

## What This Actually Means

I agree that we need more senior engineers to supervise AI-generated code. But not because AI is uniquely dangerous.

We've always needed senior engineers to supervise code. We've always had juniors making questionable architectural decisions. We've always had tech debt piling up faster than we can pay it down.

AI didn't create this problem. It just made it more visible. And honestly? Making problems visible is usually the first step to solving them.

## The Bottom Line

We've always needed to address technical debt. We've always needed to mentor juniors. We've always needed to review code. AI didn't create this problem, but it can help us solve it.

---

## Try It Yourself

All the code and data for this analysis is in this repo:

```bash
# Clone and setup
git clone https://github.com/copyleftdev/technical-debt-predates-ai.git
cd technical-debt-predates-ai
python -m venv venv
source venv/bin/activate
pip install requests python-dotenv

# Optional: add your GitHub token for higher rate limits
echo "export GITHUB_TOKEN=your_token_here" > .env

# Run the analysis
python github_debt_analysis.py --use-cache

# Or fetch fresh data with extended metrics
python github_debt_analysis.py --extended --max-repos 300
```

The methodology is transparent. The data is reproducible. If I'm wrong, prove it with better data.

That's how this is supposed to work.

---

*If you enjoyed this post, consider not installing `is-odd` the next time you need to check if a number is odd. Your future self will thank you.*
