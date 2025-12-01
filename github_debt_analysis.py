#!/usr/bin/env python3
"""
GitHub Technical Debt Analysis

Analyzes the relationship between repository popularity (stars) and 
technical debt indicators (issues) to examine whether debt existed
before AI coding tools became mainstream.

Thesis: Technical debt was overwhelming BEFORE AI, not caused by it.
"""

import requests
import os
import time
import json
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional
import statistics

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# GitHub API configuration
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # Optional but recommended for rate limits

@dataclass
class RepoMetrics:
    name: str
    full_name: str
    stars: int
    open_issues: int
    created_at: datetime
    language: Optional[str]
    forks: int
    # Extended metrics
    total_issues: int = 0
    closed_issues: int = 0
    contributors: int = 0
    commits: int = 0
    updated_at: Optional[datetime] = None
    
    @property
    def issues_per_1k_stars(self) -> float:
        """Issues per 1000 stars - normalized debt indicator"""
        if self.stars == 0:
            return 0
        return (self.open_issues / self.stars) * 1000
    
    @property
    def issue_close_rate(self) -> float:
        """Percentage of issues that have been closed (maintenance health)"""
        if self.total_issues == 0:
            return 0
        return (self.closed_issues / self.total_issues) * 100
    
    @property
    def age_days(self) -> int:
        """Repository age in days"""
        return (datetime.now(self.created_at.tzinfo) - self.created_at).days
    
    @property
    def issues_per_year(self) -> float:
        """Average open issues accumulated per year of existence"""
        years = max(self.age_days / 365, 0.1)
        return self.open_issues / years
    
    @property
    def era(self) -> str:
        """Categorize by AI era: pre-AI (before 2022) or post-AI (2022+)"""
        if self.created_at.year < 2022:
            return "pre-ai"
        return "post-ai"


def get_headers() -> dict:
    """Build request headers with optional auth"""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "TechDebtAnalyzer"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


def search_repos(query: str, sort: str = "stars", per_page: int = 100, page: int = 1) -> list[dict]:
    """Search GitHub repositories"""
    url = f"{GITHUB_API_BASE}/search/repositories"
    params = {
        "q": query,
        "sort": sort,
        "order": "desc",
        "per_page": per_page,
        "page": page
    }
    
    response = requests.get(url, headers=get_headers(), params=params)
    response.raise_for_status()
    
    # Respect rate limits
    remaining = int(response.headers.get("X-RateLimit-Remaining", 10))
    if remaining < 5:
        reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
        wait = max(reset_time - time.time(), 0) + 1
        print(f"Rate limit low ({remaining}), waiting {wait:.0f}s...")
        time.sleep(wait)
    
    return response.json().get("items", [])


def parse_repo(data: dict) -> RepoMetrics:
    """Parse GitHub API response into RepoMetrics"""
    updated = None
    if data.get("updated_at"):
        updated = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
    
    return RepoMetrics(
        name=data["name"],
        full_name=data["full_name"],
        stars=data["stargazers_count"],
        open_issues=data["open_issues_count"],
        created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
        language=data.get("language"),
        forks=data["forks_count"],
        updated_at=updated
    )


def fetch_repo_details(full_name: str) -> dict:
    """Fetch detailed repo info including issue counts"""
    url = f"{GITHUB_API_BASE}/repos/{full_name}"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()


def fetch_issue_counts(full_name: str) -> tuple[int, int]:
    """Fetch open and closed issue counts for a repo"""
    # Get open issues count
    open_url = f"{GITHUB_API_BASE}/search/issues?q=repo:{full_name}+type:issue+state:open&per_page=1"
    closed_url = f"{GITHUB_API_BASE}/search/issues?q=repo:{full_name}+type:issue+state:closed&per_page=1"
    
    try:
        open_resp = requests.get(open_url, headers=get_headers())
        open_count = open_resp.json().get("total_count", 0) if open_resp.ok else 0
        time.sleep(0.5)
        
        closed_resp = requests.get(closed_url, headers=get_headers())
        closed_count = closed_resp.json().get("total_count", 0) if closed_resp.ok else 0
        
        return open_count, closed_count
    except Exception:
        return 0, 0


def fetch_contributor_count(full_name: str) -> int:
    """Fetch contributor count for a repo"""
    url = f"{GITHUB_API_BASE}/repos/{full_name}/contributors?per_page=1&anon=true"
    try:
        response = requests.get(url, headers=get_headers())
        if response.ok:
            # GitHub returns total in Link header for pagination
            link = response.headers.get("Link", "")
            if 'rel="last"' in link:
                # Parse last page number from Link header
                import re
                match = re.search(r'page=(\d+)>; rel="last"', link)
                if match:
                    return int(match.group(1))
            return len(response.json())
    except Exception:
        pass
    return 0


def enrich_repo_metrics(repo: RepoMetrics, fetch_extended: bool = False) -> RepoMetrics:
    """Add extended metrics to a repo (uses extra API calls)"""
    if not fetch_extended:
        return repo
    
    try:
        print(f"  Enriching {repo.full_name}...")
        open_issues, closed_issues = fetch_issue_counts(repo.full_name)
        repo.total_issues = open_issues + closed_issues
        repo.closed_issues = closed_issues
        time.sleep(0.5)
        
        repo.contributors = fetch_contributor_count(repo.full_name)
        time.sleep(0.5)
    except Exception as e:
        print(f"  Error enriching {repo.full_name}: {e}")
    
    return repo


def fetch_popular_repos(min_stars: int = 1000, languages: list[str] = None, max_repos: int = 200) -> list[RepoMetrics]:
    """
    Fetch popular repositories across different eras.
    
    Args:
        min_stars: Minimum star count to consider
        languages: Filter by programming languages
        max_repos: Maximum repos to fetch
    """
    repos = []
    languages = languages or ["javascript", "python", "typescript", "java", "go", "rust"]
    
    for lang in languages:
        print(f"Fetching {lang} repos...")
        
        # Pre-AI era (before 2022)
        query_pre = f"language:{lang} stars:>{min_stars} created:<2022-01-01"
        try:
            items = search_repos(query_pre, per_page=30)
            repos.extend([parse_repo(item) for item in items])
            time.sleep(1)  # Be nice to the API
        except Exception as e:
            print(f"  Error fetching pre-AI {lang}: {e}")
        
        # Post-AI era (2022+)
        query_post = f"language:{lang} stars:>{min_stars} created:>=2022-01-01"
        try:
            items = search_repos(query_post, per_page=30)
            repos.extend([parse_repo(item) for item in items])
            time.sleep(1)
        except Exception as e:
            print(f"  Error fetching post-AI {lang}: {e}")
        
        if len(repos) >= max_repos:
            break
    
    return repos[:max_repos]


def analyze_by_era(repos: list[RepoMetrics]) -> dict:
    """Analyze metrics grouped by pre-AI vs post-AI era"""
    pre_ai = [r for r in repos if r.era == "pre-ai"]
    post_ai = [r for r in repos if r.era == "post-ai"]
    
    def calc_stats(repo_list: list[RepoMetrics]) -> dict:
        if not repo_list:
            return {"count": 0}
        
        ratios = [r.issues_per_1k_stars for r in repo_list]
        stars = [r.stars for r in repo_list]
        issues = [r.open_issues for r in repo_list]
        issues_per_year = [r.issues_per_year for r in repo_list]
        close_rates = [r.issue_close_rate for r in repo_list if r.total_issues > 0]
        contributors = [r.contributors for r in repo_list if r.contributors > 0]
        
        stats = {
            "count": len(repo_list),
            "avg_issues_per_1k_stars": round(statistics.mean(ratios), 2),
            "median_issues_per_1k_stars": round(statistics.median(ratios), 2),
            "std_dev_ratio": round(statistics.stdev(ratios), 2) if len(ratios) > 1 else 0,
            "total_stars": sum(stars),
            "total_open_issues": sum(issues),
            "avg_stars": round(statistics.mean(stars), 0),
            "avg_open_issues": round(statistics.mean(issues), 0),
            "avg_issues_per_year": round(statistics.mean(issues_per_year), 2),
            "median_issues_per_year": round(statistics.median(issues_per_year), 2),
        }
        
        # Extended metrics (if available)
        if close_rates:
            stats["avg_close_rate"] = round(statistics.mean(close_rates), 1)
            stats["median_close_rate"] = round(statistics.median(close_rates), 1)
        if contributors:
            stats["avg_contributors"] = round(statistics.mean(contributors), 0)
            stats["median_contributors"] = round(statistics.median(contributors), 0)
        
        return stats
    
    return {
        "pre_ai_era": calc_stats(pre_ai),
        "post_ai_era": calc_stats(post_ai)
    }


def analyze_by_language(repos: list[RepoMetrics]) -> dict:
    """Analyze metrics grouped by programming language"""
    by_lang = {}
    for repo in repos:
        lang = repo.language or "Unknown"
        if lang not in by_lang:
            by_lang[lang] = []
        by_lang[lang].append(repo)
    
    results = {}
    for lang, repo_list in by_lang.items():
        if len(repo_list) < 3:
            continue
        ratios = [r.issues_per_1k_stars for r in repo_list]
        results[lang] = {
            "count": len(repo_list),
            "avg_issues_per_1k_stars": round(statistics.mean(ratios), 2),
            "median_issues_per_1k_stars": round(statistics.median(ratios), 2),
        }
    
    return results


def find_extremes(repos: list[RepoMetrics], top_n: int = 10) -> dict:
    """Find repos with highest and lowest issue ratios"""
    sorted_by_ratio = sorted(repos, key=lambda r: r.issues_per_1k_stars, reverse=True)
    
    def repo_summary(r: RepoMetrics) -> dict:
        return {
            "name": r.full_name,
            "stars": r.stars,
            "open_issues": r.open_issues,
            "issues_per_1k_stars": round(r.issues_per_1k_stars, 2),
            "created": r.created_at.strftime("%Y-%m-%d"),
            "era": r.era
        }
    
    return {
        "highest_debt_ratio": [repo_summary(r) for r in sorted_by_ratio[:top_n]],
        "lowest_debt_ratio": [repo_summary(r) for r in sorted_by_ratio[-top_n:][::-1]]
    }


def generate_report(repos: list[RepoMetrics]) -> str:
    """Generate a markdown report of the analysis"""
    era_analysis = analyze_by_era(repos)
    lang_analysis = analyze_by_language(repos)
    extremes = find_extremes(repos)
    
    pre = era_analysis["pre_ai_era"]
    post = era_analysis["post_ai_era"]
    
    report = f"""# GitHub Technical Debt Analysis Report

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total Repositories Analyzed: {len(repos)}

## Executive Summary

This analysis examines the relationship between repository popularity (stars) and 
technical debt indicators (open issues) across different time periods.

**Key Finding:** {"Pre-AI era repos show HIGHER issue ratios, suggesting debt existed before AI." if pre.get("avg_issues_per_1k_stars", 0) > post.get("avg_issues_per_1k_stars", 0) else "Post-AI era shows higher ratios - but sample size and maturity matter."}

---

## Era Comparison

| Metric | Pre-AI Era (<2022) | Post-AI Era (≥2022) |
|--------|-------------------|---------------------|
| Repos Analyzed | {pre.get("count", 0)} | {post.get("count", 0)} |
| Avg Issues per 1K Stars | {pre.get("avg_issues_per_1k_stars", "N/A")} | {post.get("avg_issues_per_1k_stars", "N/A")} |
| Median Issues per 1K Stars | {pre.get("median_issues_per_1k_stars", "N/A")} | {post.get("median_issues_per_1k_stars", "N/A")} |
| Avg Issues per Year | {pre.get("avg_issues_per_year", "N/A")} | {post.get("avg_issues_per_year", "N/A")} |
| Median Issues per Year | {pre.get("median_issues_per_year", "N/A")} | {post.get("median_issues_per_year", "N/A")} |
| Avg Issue Close Rate % | {pre.get("avg_close_rate", "N/A")} | {post.get("avg_close_rate", "N/A")} |
| Avg Contributors | {pre.get("avg_contributors", "N/A")} | {post.get("avg_contributors", "N/A")} |
| Std Deviation | {pre.get("std_dev_ratio", "N/A")} | {post.get("std_dev_ratio", "N/A")} |
| Total Stars | {pre.get("total_stars", 0):,} | {post.get("total_stars", 0):,} |
| Total Open Issues | {pre.get("total_open_issues", 0):,} | {post.get("total_open_issues", 0):,} |

### Interpretation

- **Issues per 1K Stars** = normalized measure of "problems per unit of popularity"
- Higher values suggest more maintenance burden relative to community size
- Pre-AI era projects have had more time to accumulate issues, but also more time to close them

---

## Analysis by Language

| Language | Repos | Avg Issues/1K Stars | Median |
|----------|-------|---------------------|--------|
"""
    
    for lang, stats in sorted(lang_analysis.items(), key=lambda x: x[1]["avg_issues_per_1k_stars"], reverse=True):
        report += f"| {lang} | {stats['count']} | {stats['avg_issues_per_1k_stars']} | {stats['median_issues_per_1k_stars']} |\n"
    
    report += """
---

## Highest Debt Ratios (Most Issues per Star)

| Repository | Stars | Open Issues | Ratio | Created | Era |
|------------|-------|-------------|-------|---------|-----|
"""
    
    for r in extremes["highest_debt_ratio"]:
        report += f"| {r['name']} | {r['stars']:,} | {r['open_issues']:,} | {r['issues_per_1k_stars']} | {r['created']} | {r['era']} |\n"
    
    report += """
---

## Lowest Debt Ratios (Fewest Issues per Star)

| Repository | Stars | Open Issues | Ratio | Created | Era |
|------------|-------|-------------|-------|---------|-----|
"""
    
    for r in extremes["lowest_debt_ratio"]:
        report += f"| {r['name']} | {r['stars']:,} | {r['open_issues']:,} | {r['issues_per_1k_stars']} | {r['created']} | {r['era']} |\n"
    
    report += """
---

## Methodology Notes

1. **Data Source**: GitHub Search API
2. **Minimum Stars**: 1,000 (filters out abandoned/toy projects)
3. **Era Definition**: 
   - Pre-AI: Created before January 2022
   - Post-AI: Created January 2022 or later (ChatGPT/Copilot mainstream)
4. **Metric**: Open issues count (closed issues indicate healthy maintenance)
5. **Limitations**:
   - Issue count includes feature requests, not just bugs
   - Older repos have more time to accumulate community
   - Popular repos may attract more issue reports simply due to visibility

## Conclusion

Technical debt, as measured by issue accumulation, has been a persistent challenge 
in software development long before AI coding tools existed. While AI may introduce
new patterns of debt, the fundamental problem of maintenance burden is not new.
"""
    
    return report


def load_cache(cache_file: str = "repo_cache.json") -> list[RepoMetrics]:
    """Load cached repo data if available"""
    if not Path(cache_file).exists():
        return []
    
    try:
        with open(cache_file) as f:
            data = json.load(f)
        
        repos = []
        for item in data:
            repo = RepoMetrics(
                name=item["name"],
                full_name=item["full_name"],
                stars=item["stars"],
                open_issues=item["open_issues"],
                created_at=datetime.fromisoformat(item["created_at"]),
                language=item.get("language"),
                forks=item["forks"],
                total_issues=item.get("total_issues", 0),
                closed_issues=item.get("closed_issues", 0),
                contributors=item.get("contributors", 0),
            )
            repos.append(repo)
        return repos
    except Exception as e:
        print(f"Cache load failed: {e}")
        return []


def save_cache(repos: list[RepoMetrics], cache_file: str = "repo_cache.json"):
    """Save repo data to cache"""
    data = []
    for r in repos:
        data.append({
            "name": r.name,
            "full_name": r.full_name,
            "stars": r.stars,
            "open_issues": r.open_issues,
            "created_at": r.created_at.isoformat(),
            "language": r.language,
            "forks": r.forks,
            "total_issues": r.total_issues,
            "closed_issues": r.closed_issues,
            "contributors": r.contributors,
        })
    
    with open(cache_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"💾 Cache saved to: {cache_file}")


def main():
    parser = argparse.ArgumentParser(description="Analyze GitHub technical debt across eras")
    parser.add_argument("--extended", "-e", action="store_true", 
                        help="Fetch extended metrics (issue close rate, contributors) - uses more API calls")
    parser.add_argument("--max-repos", "-n", type=int, default=200,
                        help="Maximum repos to analyze (default: 200)")
    parser.add_argument("--min-stars", type=int, default=1000,
                        help="Minimum stars filter (default: 1000)")
    parser.add_argument("--use-cache", action="store_true",
                        help="Use cached data if available")
    parser.add_argument("--enrich-top", type=int, default=0,
                        help="Enrich only top N repos with extended metrics")
    args = parser.parse_args()
    
    print("=" * 60)
    print("GitHub Technical Debt Analysis")
    print("Thesis: Debt existed before AI - proving with data")
    print("=" * 60)
    print()
    
    if not GITHUB_TOKEN:
        print("⚠️  No GITHUB_TOKEN set. Rate limits will be strict (60 req/hour).")
        print("   Set GITHUB_TOKEN environment variable for 5000 req/hour.")
        print()
    
    # Try cache first
    repos = []
    if args.use_cache:
        repos = load_cache()
        if repos:
            print(f"📦 Loaded {len(repos)} repos from cache")
    
    if not repos:
        print("Fetching repository data...")
        repos = fetch_popular_repos(min_stars=args.min_stars, max_repos=args.max_repos)
        save_cache(repos)
    
    # Enrich with extended metrics if requested
    if args.extended:
        print("\nFetching extended metrics (this will take a while)...")
        for i, repo in enumerate(repos):
            enrich_repo_metrics(repo, fetch_extended=True)
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{len(repos)}")
        save_cache(repos)  # Update cache with enriched data
    elif args.enrich_top > 0:
        print(f"\nEnriching top {args.enrich_top} repos with extended metrics...")
        sorted_repos = sorted(repos, key=lambda r: r.stars, reverse=True)
        for repo in sorted_repos[:args.enrich_top]:
            enrich_repo_metrics(repo, fetch_extended=True)
        save_cache(repos)
    
    print(f"\nAnalyzed {len(repos)} repositories")
    print()
    
    # Generate and save report
    report = generate_report(repos)
    
    report_path = "debt_analysis_report.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"📊 Report saved to: {report_path}")
    
    # Also save raw data for further analysis
    raw_data = [
        {
            "name": r.full_name,
            "stars": r.stars,
            "open_issues": r.open_issues,
            "issues_per_1k_stars": round(r.issues_per_1k_stars, 2),
            "created_at": r.created_at.isoformat(),
            "era": r.era,
            "language": r.language
        }
        for r in repos
    ]
    
    with open("debt_analysis_data.json", "w") as f:
        json.dump(raw_data, f, indent=2)
    print("📁 Raw data saved to: debt_analysis_data.json")
    
    # Print quick summary
    era_analysis = analyze_by_era(repos)
    pre = era_analysis["pre_ai_era"]
    post = era_analysis["post_ai_era"]
    
    print("\n" + "=" * 60)
    print("QUICK SUMMARY")
    print("=" * 60)
    print(f"\nPre-AI Era (<2022):  {pre.get('count', 0)} repos, {pre.get('avg_issues_per_1k_stars', 'N/A')} avg issues/1K stars")
    print(f"Post-AI Era (≥2022): {post.get('count', 0)} repos, {post.get('avg_issues_per_1k_stars', 'N/A')} avg issues/1K stars")
    
    if pre.get("avg_issues_per_1k_stars", 0) > post.get("avg_issues_per_1k_stars", 0):
        print("\n✅ FINDING: Pre-AI era shows HIGHER debt ratios!")
        print("   This supports the thesis that technical debt was already a problem.")
    else:
        print("\n⚠️  FINDING: Post-AI shows higher ratios, but consider:")
        print("   - Newer repos have less time to close issues")
        print("   - Older repos have more mature maintenance practices")


if __name__ == "__main__":
    main()
