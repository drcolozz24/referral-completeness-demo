# Changelog

All notable changes to this repository. Dates are Australian Eastern time.

## [Unreleased] — first public release candidate

### 2026-09-24
- Rebuilt the demonstration from an earlier private proof of concept (March 2026). Removed all references to a former company, its patent applications and website; removed a dashboard showing a practice name and invented performance figures; removed the fixed, scripted results.
- Replaced the invented rule list with the published NSW Health Statewide Referral Criteria for adult chest pain, reproduced verbatim with attribution (CC BY 4.0). An earlier draft cited a "NSW Cardiology CPC 2024" document that does not exist.
- The page now performs a real (small) check: the reader ticks items found in a fictional letter; the page counts them against the published list.
- Added an entry gate stating intended purpose and limitations before the page runs, including a liability statement that names negligence and an Australian Consumer Law statement.
- Added author line: personal work, no commercial interest, no affiliation.
- Added Agent 1 (`tests/test_demo.js`, 47 checks) and Agent 2 (`tests/check_criteria.py`, NSW consistency). Agent 2's first run found two items paraphrased rather than quoted; both corrected to NSW's wording.
- Added README, LICENSE, NOTICE, this changelog.
