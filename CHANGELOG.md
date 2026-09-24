# Changelog

All notable changes to this repository. Dates are Australian Eastern time.

## [Unreleased] — first public release candidate

### 2026-09-24
- Rebuilt the demonstration from an earlier private proof of concept (March 2026). Removed all references to a former company, its provisional IP applications and website; removed a dashboard showing a practice name and invented performance figures; removed the fixed, scripted results.
- Replaced the invented rule list with the published NSW Health Statewide Referral Criteria for adult chest pain, reproduced verbatim with attribution (CC BY 4.0). An earlier draft cited a "NSW Cardiology CPC 2024" document that does not exist.
- The page now performs a real (small) check: the reader ticks items found in a fictional letter; the page counts them against the published list.
- Added an entry gate stating intended purpose and limitations before the page runs, including a liability statement that names negligence and an Australian Consumer Law statement.
- Added author line: personal work, no commercial interest, no affiliation.
- Added Agent 1 (`tests/test_demo.js`) and Agent 2 (`tests/check_criteria.py`, NSW consistency including triage wording).
- Added README, LICENSE, NOTICE, this changelog.
- Independent pre-release audit (25 findings) applied: NSW attribution made contiguous; triage category wording corrected to NSW's (Category 2 had omitted "in the absence of Emergency criteria"); the nine investigation items now shown as sub-items of "Patient health summary" as NSW publishes them, with the counting rule stated on screen; ticking rule stated ("only when everything it lists is mentioned"); repository address added to the ⓘ panel; accessibility fixes (dialog roles, initial focus, Escape to close, readable rather than disabled letter, icons hidden from screen readers); private files and a former name removed from the test script; factual corrections in docs (BJGP screening figures and issue date; prospective-evaluation wording; company details flagged for confirmation).
- docs/02 rewritten to contain only statements linked to a public source opened on 24 September 2026, with a declaration to that effect; unsourced statements removed rather than flagged.
