# Actually, We've Always Been Terrible at This

**A data-driven response to "The Vibe Tax" — or, why blaming AI for technical debt is like blaming GPS for traffic.**

---

I recently read Ali Karbasi's article about the "Vibe Tax" — the idea that AI-generated code is flooding the market with unvalidated garbage and driving up technical debt. It's a well-written piece. It's got that righteous energy. It makes you want to nod along and mutter "kids these days" into your artisanal coffee.

There's just one problem: the premise is wrong.

Not wrong like "you made a typo" wrong. Wrong like "we've been drowning in technical debt since before ChatGPT was a twinkle in Sam Altman's eye" wrong.

So I did what any reasonable person would do. I wrote a Python script, hit the GitHub API, and pulled data on 300 popular repositories. Because nothing says "I disagree with your blog post" like spending a Saturday afternoon writing code to prove it.

## The Numbers Don't Lie (But They Do Hurt)

Here's what I found when I compared repos created **before** January 2022 (pre-AI coding tools) versus **after**:

| What I Measured | Pre-AI Era | Post-AI Era |
|-----------------|------------|-------------|
| Repos Analyzed | 150 | 150 |
| Issues per 1,000 Stars | **13.36** | 12.47 |
| Issue Close Rate | 90.3% | 70.0% |
| Avg Contributors | 865 | 207 |

Read that first data row again. **Pre-AI repositories have a higher issue-to-star ratio than post-AI ones.**

The repos built by Serious Engineers™ before the AI apocalypse have *more* technical debt per unit of popularity than the supposed "vibe coded" garbage.

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

Ali's article describes real symptoms. I've seen the Frankenstein codebases. I've audited the 50MB todo apps. I've watched juniors install a library to check if a number is odd.

But here's the thing: I saw all of that *before* AI coding tools existed.

The junior who installs `is-odd` from npm isn't doing it because ChatGPT told them to. They're doing it because they don't know better yet. That's what being a junior means. The solution isn't to ban AI — it's the same solution it's always been: code review, mentorship, and time.

The "Frankenstein codebase" with three different date formatting approaches? I've seen those in codebases that predate GitHub. That's not a vibe tax. That's what happens when multiple developers touch the same project over time without strong conventions. It's called "working in software."

## The Uncomfortable Truth

Technical debt isn't a new phenomenon caused by AI. It's an inherent property of software development. Every line of code you write is a liability. Every dependency you add is a risk. Every feature you ship is a maintenance burden.

PyTorch has 865 contributors on average. These are smart people. PhD-level smart. They still have 17,800 open issues. Not because they're lazy or careless, but because building complex software generates issues faster than any team can close them.

If the Python interpreter itself — written by some of the best programmers on the planet over decades — can't escape technical debt, maybe the problem isn't that some founder used Cursor to build their MVP.

## What This Actually Means

I'm not saying AI-generated code is perfect. It's not. It makes mistakes. It lacks context. It needs supervision.

But you know what else makes mistakes, lacks context, and needs supervision? 

Every developer I've ever worked with, including me.

The difference is that AI makes mistakes *faster*. Which, depending on how you look at it, either means we're generating debt at unprecedented rates, or we're iterating at unprecedented rates. The data suggests it might actually be the latter.

## The Bottom Line

Ali argues that we need more senior engineers to supervise AI-generated code. I agree! But not because AI is uniquely dangerous.

We've always needed senior engineers to supervise code. We've always had juniors making questionable architectural decisions. We've always had tech debt piling up faster than we can pay it down.

AI didn't create this problem. It just made it more visible. And honestly? Making problems visible is usually the first step to solving them.

---

## Try It Yourself

All the code and data for this analysis is in this repo:

```bash
# Clone and setup
git clone <this-repo>
cd ali_chin_check
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
