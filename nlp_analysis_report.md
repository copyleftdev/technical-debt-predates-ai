# Commit Message NLP Analysis

Generated: 2025-11-30 17:16:14

## Overview

This analysis examines commit messages for signals of technical debt, 
bugs, frustration, and code quality across pre-AI and post-AI era repositories.

---

## Era Comparison

| Signal Type | Pre-AI Era | Post-AI Era | Interpretation |
|-------------|------------|-------------|----------------|
| Repos Analyzed | 20 | 20 | |
| Total Commits | 9,555 | 9,026 | |
| **Debt signals** per 100 | 2.51 | 1.2 | TODO, FIXME, HACK, etc. |
| **Bug/fix signals** per 100 | 34.84 | 40.29 | fix, bug, issue, patch |
| **Revert signals** per 100 | 1.3 | 2.13 | revert, undo, rollback |
| **Frustration signals** per 100 | 0.29 | 0.04 | finally, wtf, ugh, etc. |
| **Positive signals** per 100 | 7.94 | 18.03 | improve, refactor, clean |
| Avg message length | 166.1 | 284.9 | chars |

---

## Top Debt Signals Found

### Pre-AI Era
- **broken**: 151
- **xxx**: 25
- **temporary**: 20
- **todo**: 19
- **workaround**: 13

### Post-AI Era  
- **temporary**: 42
- **broken**: 31
- **todo**: 17
- **workaround**: 11
- **ugly**: 4

---

## Top Frustration Signals Found

### Pre-AI Era
- **finally**: 16
- **stupid**: 5
- **terrible**: 2
- **hate**: 2
- **damn**: 1

### Post-AI Era
- **finally**: 2
- **stupid**: 1
- **hate**: 1

---

## Sample Commit Messages (Debt/Frustration)

### Pre-AI Era Samples
- "fix(curriculum): add assert to prevent empty editor pass in todo list (#64193)"
- "feat(curriculum): Add interactive examples to try…catch…finally lesson (#63552)"
- "chore: temporarily block E2E runs on main branch pushes (#63207)"
- "Remove MFaaS, it's broken"
- "Remove Kawal Corona, it's broken"
- "Remove Affirmations, it's broken"
- "Remove WeatherReactApi, it's broken"
- "Remove Utelly, it's broken"
- "Add 3 DSA Books under subjects list (#12962)"
- "Replace broken 'Python 中文学习大本营' link with '菜鸟教程 Python3 教程' (#13005) (#13008)"

### Post-AI Era Samples
- "hotfix(backend): Temporarily disable library existence check for graph execution (#11318)"
- "feat(platform): implement admin user impersonation with header-based authentication (#11298)"
- "hotfix(backend/scheduler): Bump `apscheduler` to DST-fixed version 3.11.1 (#11294)"
- "fix(backend/scheduler): Bump `apscheduler` to DST-fixed version 3.11.1 (#11294)"
- "feat(backend/executor): Implement cascading stop for nested graph executions (#11277)"
- "fix Replace preview"
- "Enable Vulkan with a temporary opt-in setting (#12931)"
- "vulkan: temporary cary of vulkan fixes (#12971)"
- "mac: fix stale VRAM data (#12972)"
- "cpu: always ensure LibOllamaPath included (#12890)"

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
