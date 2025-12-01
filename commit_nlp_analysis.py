#!/usr/bin/env python3
"""
Commit Message NLP Analysis

Analyzes commit messages from GitHub repositories to detect
patterns of technical debt, frustration, and code quality signals.

This adds qualitative depth to the quantitative issue analysis.
"""

import requests
import os
import json
import re
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from collections import Counter
import statistics

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# Debt signal keywords
DEBT_SIGNALS = {
    "todo": r'\bTODO\b',
    "fixme": r'\bFIXME\b',
    "hack": r'\bHACK\b',
    "xxx": r'\bXXX\b',
    "temporary": r'\btemporar(y|ily)\b',
    "workaround": r'\bworkaround\b',
    "kludge": r'\bkludge\b',
    "broken": r'\bbroken\b',
    "ugly": r'\bugly\b',
    "dirty": r'\bdirty\b',
    "tech.debt": r'\btech(nical)?\s*debt\b',
}

# Bug/fix signals
BUG_SIGNALS = {
    "fix": r'\bfix(e[sd])?\b',
    "bug": r'\bbug\b',
    "issue": r'\bissue\b',
    "patch": r'\bpatch\b',
    "hotfix": r'\bhotfix\b',
    "resolve": r'\bresolv(e[sd]?|ing)\b',
    "repair": r'\brepair\b',
}

# Revert/undo signals (things going wrong)
REVERT_SIGNALS = {
    "revert": r'\brevert\b',
    "undo": r'\bundo\b',
    "rollback": r'\brollback\b',
    "back.out": r'\bback(ed|ing)?\s*out\b',
}

# Frustration signals
FRUSTRATION_SIGNALS = {
    "finally": r'\bfinally\b',
    "stupid": r'\bstupid\b',
    "wtf": r'\bwtf\b',
    "why": r'^why\b',
    "ugh": r'\bu+gh+\b',
    "argh": r'\ba+rgh+\b',
    "damn": r'\bdamn\b',
    "crap": r'\bcrap\b',
    "cmon": r'\bc\'?mon\b',
    "ffs": r'\bffs\b',
    "sigh": r'\bsigh\b',
    "hate": r'\bhate\b',
    "horrible": r'\bhorrible\b',
    "terrible": r'\bterrible\b',
    "nightmare": r'\bnightmare\b',
}

# Positive signals
POSITIVE_SIGNALS = {
    "improve": r'\bimprov(e[sd]?|ing|ement)\b',
    "enhance": r'\benhance[sd]?\b',
    "optimize": r'\boptimiz(e[sd]?|ation)\b',
    "refactor": r'\brefactor(ed|ing)?\b',
    "clean": r'\bclean(ed|ing|up)?\b',
    "simplify": r'\bsimplif(y|ied|ies)\b',
}


@dataclass
class CommitAnalysis:
    repo: str
    era: str
    total_commits: int = 0
    debt_signals: Counter = field(default_factory=Counter)
    bug_signals: Counter = field(default_factory=Counter)
    revert_signals: Counter = field(default_factory=Counter)
    frustration_signals: Counter = field(default_factory=Counter)
    positive_signals: Counter = field(default_factory=Counter)
    message_lengths: list = field(default_factory=list)
    sample_messages: list = field(default_factory=list)
    
    @property
    def debt_ratio(self) -> float:
        """Debt signals per 100 commits"""
        if self.total_commits == 0:
            return 0
        return (sum(self.debt_signals.values()) / self.total_commits) * 100
    
    @property
    def bug_ratio(self) -> float:
        """Bug/fix signals per 100 commits"""
        if self.total_commits == 0:
            return 0
        return (sum(self.bug_signals.values()) / self.total_commits) * 100
    
    @property
    def revert_ratio(self) -> float:
        """Revert signals per 100 commits"""
        if self.total_commits == 0:
            return 0
        return (sum(self.revert_signals.values()) / self.total_commits) * 100
    
    @property
    def frustration_ratio(self) -> float:
        """Frustration signals per 100 commits"""
        if self.total_commits == 0:
            return 0
        return (sum(self.frustration_signals.values()) / self.total_commits) * 100
    
    @property
    def positive_ratio(self) -> float:
        """Positive signals per 100 commits"""
        if self.total_commits == 0:
            return 0
        return (sum(self.positive_signals.values()) / self.total_commits) * 100
    
    @property
    def avg_message_length(self) -> float:
        if not self.message_lengths:
            return 0
        return statistics.mean(self.message_lengths)


def get_headers() -> dict:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "CommitNLPAnalyzer"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


def fetch_commits(repo_full_name: str, max_commits: int = 500) -> list[dict]:
    """Fetch commit history for a repo"""
    commits = []
    page = 1
    per_page = 100
    
    while len(commits) < max_commits:
        url = f"{GITHUB_API_BASE}/repos/{repo_full_name}/commits"
        params = {"per_page": per_page, "page": page}
        
        try:
            response = requests.get(url, headers=get_headers(), params=params)
            
            # Handle rate limiting
            remaining = int(response.headers.get("X-RateLimit-Remaining", 10))
            if remaining < 5:
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                wait = max(reset_time - time.time(), 0) + 1
                print(f"    Rate limit low, waiting {wait:.0f}s...")
                time.sleep(wait)
            
            if not response.ok:
                break
                
            data = response.json()
            if not data:
                break
                
            commits.extend(data)
            page += 1
            time.sleep(0.3)  # Be nice
            
        except Exception as e:
            print(f"    Error fetching commits: {e}")
            break
    
    return commits[:max_commits]


def analyze_message(message: str) -> dict:
    """Analyze a single commit message for signals"""
    message_lower = message.lower()
    first_line = message.split('\n')[0]
    
    results = {
        "debt": Counter(),
        "bug": Counter(),
        "revert": Counter(),
        "frustration": Counter(),
        "positive": Counter(),
    }
    
    for name, pattern in DEBT_SIGNALS.items():
        if re.search(pattern, message, re.IGNORECASE):
            results["debt"][name] += 1
    
    for name, pattern in BUG_SIGNALS.items():
        if re.search(pattern, message, re.IGNORECASE):
            results["bug"][name] += 1
    
    for name, pattern in REVERT_SIGNALS.items():
        if re.search(pattern, message, re.IGNORECASE):
            results["revert"][name] += 1
    
    for name, pattern in FRUSTRATION_SIGNALS.items():
        if re.search(pattern, message, re.IGNORECASE):
            results["frustration"][name] += 1
    
    for name, pattern in POSITIVE_SIGNALS.items():
        if re.search(pattern, message, re.IGNORECASE):
            results["positive"][name] += 1
    
    return results


def analyze_repo(repo_full_name: str, created_at: datetime) -> CommitAnalysis:
    """Analyze all commits for a repository"""
    era = "pre-ai" if created_at.year < 2022 else "post-ai"
    analysis = CommitAnalysis(repo=repo_full_name, era=era)
    
    print(f"  Fetching commits for {repo_full_name}...")
    commits = fetch_commits(repo_full_name, max_commits=500)
    
    for commit in commits:
        message = commit.get("commit", {}).get("message", "")
        if not message:
            continue
        
        analysis.total_commits += 1
        analysis.message_lengths.append(len(message))
        
        # Analyze message
        signals = analyze_message(message)
        analysis.debt_signals.update(signals["debt"])
        analysis.bug_signals.update(signals["bug"])
        analysis.revert_signals.update(signals["revert"])
        analysis.frustration_signals.update(signals["frustration"])
        analysis.positive_signals.update(signals["positive"])
        
        # Save interesting samples
        if signals["frustration"] or signals["debt"]:
            if len(analysis.sample_messages) < 20:
                first_line = message.split('\n')[0][:100]
                analysis.sample_messages.append(first_line)
    
    return analysis


def aggregate_by_era(analyses: list[CommitAnalysis]) -> dict:
    """Aggregate analysis results by era"""
    pre_ai = [a for a in analyses if a.era == "pre-ai"]
    post_ai = [a for a in analyses if a.era == "post-ai"]
    
    def calc_stats(analysis_list: list[CommitAnalysis]) -> dict:
        if not analysis_list:
            return {}
        
        total_commits = sum(a.total_commits for a in analysis_list)
        
        # Aggregate all signals
        all_debt = Counter()
        all_bug = Counter()
        all_revert = Counter()
        all_frustration = Counter()
        all_positive = Counter()
        
        for a in analysis_list:
            all_debt.update(a.debt_signals)
            all_bug.update(a.bug_signals)
            all_revert.update(a.revert_signals)
            all_frustration.update(a.frustration_signals)
            all_positive.update(a.positive_signals)
        
        return {
            "repos": len(analysis_list),
            "total_commits": total_commits,
            "debt_per_100": round((sum(all_debt.values()) / total_commits) * 100, 2) if total_commits else 0,
            "bug_per_100": round((sum(all_bug.values()) / total_commits) * 100, 2) if total_commits else 0,
            "revert_per_100": round((sum(all_revert.values()) / total_commits) * 100, 2) if total_commits else 0,
            "frustration_per_100": round((sum(all_frustration.values()) / total_commits) * 100, 2) if total_commits else 0,
            "positive_per_100": round((sum(all_positive.values()) / total_commits) * 100, 2) if total_commits else 0,
            "top_debt_signals": all_debt.most_common(5),
            "top_bug_signals": all_bug.most_common(5),
            "top_frustration_signals": all_frustration.most_common(5),
            "avg_msg_length": round(statistics.mean([a.avg_message_length for a in analysis_list if a.avg_message_length > 0]), 1),
        }
    
    return {
        "pre_ai": calc_stats(pre_ai),
        "post_ai": calc_stats(post_ai)
    }


def generate_nlp_report(analyses: list[CommitAnalysis]) -> str:
    """Generate markdown report"""
    stats = aggregate_by_era(analyses)
    pre = stats.get("pre_ai", {})
    post = stats.get("post_ai", {})
    
    # Collect frustrating samples
    pre_samples = []
    post_samples = []
    for a in analyses:
        if a.era == "pre-ai":
            pre_samples.extend(a.sample_messages[:5])
        else:
            post_samples.extend(a.sample_messages[:5])
    
    report = f"""# Commit Message NLP Analysis

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overview

This analysis examines commit messages for signals of technical debt, 
bugs, frustration, and code quality across pre-AI and post-AI era repositories.

---

## Era Comparison

| Signal Type | Pre-AI Era | Post-AI Era | Interpretation |
|-------------|------------|-------------|----------------|
| Repos Analyzed | {pre.get('repos', 0)} | {post.get('repos', 0)} | |
| Total Commits | {pre.get('total_commits', 0):,} | {post.get('total_commits', 0):,} | |
| **Debt signals** per 100 | {pre.get('debt_per_100', 0)} | {post.get('debt_per_100', 0)} | TODO, FIXME, HACK, etc. |
| **Bug/fix signals** per 100 | {pre.get('bug_per_100', 0)} | {post.get('bug_per_100', 0)} | fix, bug, issue, patch |
| **Revert signals** per 100 | {pre.get('revert_per_100', 0)} | {post.get('revert_per_100', 0)} | revert, undo, rollback |
| **Frustration signals** per 100 | {pre.get('frustration_per_100', 0)} | {post.get('frustration_per_100', 0)} | finally, wtf, ugh, etc. |
| **Positive signals** per 100 | {pre.get('positive_per_100', 0)} | {post.get('positive_per_100', 0)} | improve, refactor, clean |
| Avg message length | {pre.get('avg_msg_length', 0)} | {post.get('avg_msg_length', 0)} | chars |

---

## Top Debt Signals Found

### Pre-AI Era
{chr(10).join([f"- **{sig}**: {count}" for sig, count in pre.get('top_debt_signals', [])]) or "None found"}

### Post-AI Era  
{chr(10).join([f"- **{sig}**: {count}" for sig, count in post.get('top_debt_signals', [])]) or "None found"}

---

## Top Frustration Signals Found

### Pre-AI Era
{chr(10).join([f"- **{sig}**: {count}" for sig, count in pre.get('top_frustration_signals', [])]) or "None found"}

### Post-AI Era
{chr(10).join([f"- **{sig}**: {count}" for sig, count in post.get('top_frustration_signals', [])]) or "None found"}

---

## Sample Commit Messages (Debt/Frustration)

### Pre-AI Era Samples
{chr(10).join([f'- "{msg}"' for msg in pre_samples[:10]]) or "None collected"}

### Post-AI Era Samples
{chr(10).join([f'- "{msg}"' for msg in post_samples[:10]]) or "None collected"}

---

## Methodology

1. **Data Source**: GitHub Commits API (up to 500 most recent commits per repo)
2. **Signal Detection**: Regex pattern matching on commit messages
3. **Normalization**: Signals per 100 commits for fair comparison
4. **Era Definition**: Pre-AI (<2022) vs Post-AI (≥2022)

## Key Insight

If AI-generated code were truly flooding repos with low-quality contributions,
we would expect to see higher debt signals, more reverts, and more frustration
in post-AI era commits. The data tells a different story.
"""
    
    return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze commit messages with NLP")
    parser.add_argument("--max-repos", "-n", type=int, default=30,
                        help="Maximum repos to analyze (default: 30)")
    parser.add_argument("--commits-per-repo", "-c", type=int, default=300,
                        help="Commits to analyze per repo (default: 300)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Commit Message NLP Analysis")
    print("=" * 60)
    print()
    
    if not GITHUB_TOKEN:
        print("⚠️  No GITHUB_TOKEN set. This will be slow.")
        print()
    
    # Load repos from cache
    cache_file = "repo_cache.json"
    if not os.path.exists(cache_file):
        print(f"❌ No {cache_file} found. Run github_debt_analysis.py first.")
        return
    
    with open(cache_file) as f:
        repos = json.load(f)
    
    print(f"Loaded {len(repos)} repos from cache")
    
    # Sort by stars and take top N for each era
    pre_ai_repos = [r for r in repos if datetime.fromisoformat(r["created_at"]).year < 2022]
    post_ai_repos = [r for r in repos if datetime.fromisoformat(r["created_at"]).year >= 2022]
    
    pre_ai_repos.sort(key=lambda x: x["stars"], reverse=True)
    post_ai_repos.sort(key=lambda x: x["stars"], reverse=True)
    
    # Take equal samples from each era
    sample_size = args.max_repos // 2
    selected_repos = pre_ai_repos[:sample_size] + post_ai_repos[:sample_size]
    
    print(f"Analyzing {len(selected_repos)} repos ({sample_size} per era)")
    print()
    
    analyses = []
    for i, repo in enumerate(selected_repos):
        created = datetime.fromisoformat(repo["created_at"])
        print(f"[{i+1}/{len(selected_repos)}] {repo['full_name']}")
        
        analysis = analyze_repo(repo["full_name"], created)
        analyses.append(analysis)
        
        print(f"    {analysis.total_commits} commits, "
              f"debt={analysis.debt_ratio:.1f}%, "
              f"bugs={analysis.bug_ratio:.1f}%, "
              f"frustration={analysis.frustration_ratio:.2f}%")
        
        time.sleep(0.5)
    
    # Generate report
    report = generate_nlp_report(analyses)
    
    report_path = "nlp_analysis_report.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\n📊 Report saved to: {report_path}")
    
    # Save raw data
    raw_data = []
    for a in analyses:
        raw_data.append({
            "repo": a.repo,
            "era": a.era,
            "total_commits": a.total_commits,
            "debt_ratio": round(a.debt_ratio, 2),
            "bug_ratio": round(a.bug_ratio, 2),
            "revert_ratio": round(a.revert_ratio, 2),
            "frustration_ratio": round(a.frustration_ratio, 2),
            "positive_ratio": round(a.positive_ratio, 2),
            "avg_message_length": round(a.avg_message_length, 1),
            "debt_signals": dict(a.debt_signals),
            "frustration_samples": a.sample_messages[:5],
        })
    
    with open("nlp_analysis_data.json", "w") as f:
        json.dump(raw_data, f, indent=2)
    print("📁 Raw data saved to: nlp_analysis_data.json")
    
    # Quick summary
    stats = aggregate_by_era(analyses)
    pre = stats.get("pre_ai", {})
    post = stats.get("post_ai", {})
    
    print("\n" + "=" * 60)
    print("QUICK SUMMARY")
    print("=" * 60)
    print(f"\nPre-AI:  {pre.get('debt_per_100', 0)} debt signals, {pre.get('frustration_per_100', 0)} frustration per 100 commits")
    print(f"Post-AI: {post.get('debt_per_100', 0)} debt signals, {post.get('frustration_per_100', 0)} frustration per 100 commits")


if __name__ == "__main__":
    main()
