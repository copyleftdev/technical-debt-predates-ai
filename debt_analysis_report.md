# GitHub Technical Debt Analysis Report

Generated: 2025-11-30 16:53:22
Total Repositories Analyzed: 300

## Executive Summary

This analysis examines the relationship between repository popularity (stars) and 
technical debt indicators (open issues) across different time periods.

**Key Finding:** Pre-AI era repos show HIGHER issue ratios, suggesting debt existed before AI.

---

## Era Comparison

| Metric | Pre-AI Era (<2022) | Post-AI Era (≥2022) |
|--------|-------------------|---------------------|
| Repos Analyzed | 150 | 150 |
| Avg Issues per 1K Stars | 13.36 | 12.47 |
| Median Issues per 1K Stars | 4.37 | 6.75 |
| Avg Issues per Year | 111.47 | 232.87 |
| Median Issues per Year | 39.55 | 107.42 |
| Avg Issue Close Rate % | 90.3 | 70.0 |
| Avg Contributors | 865.0 | 207.0 |
| Std Deviation | 23.74 | 17.02 |
| Total Stars | 13,721,692 | 5,970,188 |
| Total Open Issues | 167,215 | 57,469 |

### Interpretation

- **Issues per 1K Stars** = normalized measure of "problems per unit of popularity"
- Higher values suggest more maintenance burden relative to community size
- Pre-AI era projects have had more time to accumulate issues, but also more time to close them

---

## Analysis by Language

| Language | Repos | Avg Issues/1K Stars | Median |
|----------|-------|---------------------|--------|
| Java | 60 | 17.05 | 5.89 |
| Python | 60 | 13.02 | 4.19 |
| TypeScript | 60 | 12.77 | 7.38 |
| Go | 60 | 11.89 | 7.64 |
| JavaScript | 60 | 9.86 | 4.92 |

---

## Highest Debt Ratios (Most Issues per Star)

| Repository | Stars | Open Issues | Ratio | Created | Era |
|------------|-------|-------------|-------|---------|-----|
| pytorch/pytorch | 95,493 | 17,801 | 186.41 | 2016-08-13 | pre-ai |
| spring-projects/spring-ai | 7,286 | 1,023 | 140.41 | 2023-06-27 | post-ai |
| python/cpython | 70,074 | 9,185 | 131.08 | 2017-02-10 | pre-ai |
| microsoft/vscode | 179,136 | 14,639 | 81.72 | 2015-09-03 | pre-ai |
| golang/go | 131,065 | 9,656 | 73.67 | 2014-08-19 | pre-ai |
| elastic/elasticsearch | 75,558 | 5,357 | 70.9 | 2010-02-08 | pre-ai |
| dbeaver/dbeaver | 47,465 | 3,209 | 67.61 | 2015-10-21 | pre-ai |
| ReVanced/revanced-patches | 4,968 | 335 | 67.43 | 2023-12-14 | post-ai |
| langchain4j/langchain4j | 9,789 | 636 | 64.97 | 2023-06-20 | post-ai |
| PhilJay/MPAndroidChart | 38,165 | 2,191 | 57.41 | 2014-04-25 | pre-ai |

---

## Lowest Debt Ratios (Fewest Issues per Star)

| Repository | Stars | Open Issues | Ratio | Created | Era |
|------------|-------|-------------|-------|---------|-----|
| loks666/get_jobs | 5,366 | 0 | 0.0 | 2024-03-07 | post-ai |
| FongMi/TV | 6,866 | 0 | 0.0 | 2022-06-22 | post-ai |
| shareAI-lab/analysis_claude_code | 11,455 | 0 | 0.0 | 2025-06-29 | post-ai |
| yonggekkk/Cloudflare-vless-trojan | 12,583 | 0 | 0.0 | 2023-07-22 | post-ai |
| Chalarangelo/30-seconds-of-code | 125,890 | 0 | 0.0 | 2017-11-29 | pre-ai |
| Shubhamsaboo/awesome-llm-apps | 81,056 | 2 | 0.02 | 2024-04-29 | post-ai |
| doocs/advanced-java | 78,562 | 2 | 0.03 | 2018-10-06 | pre-ai |
| gethomepage/homepage | 26,998 | 1 | 0.04 | 2022-08-24 | post-ai |
| YunaiV/ruoyi-vue-pro | 34,393 | 2 | 0.06 | 2021-01-24 | pre-ai |
| inkonchain/ink-kit | 36,805 | 3 | 0.08 | 2024-11-04 | post-ai |

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
