# Referral Completeness Demonstration

**A small, open-source demonstration built to prompt discussion about one question: does a GP referral carry the information the receiving clinician says they need?**

Built by Dr Ferney Bernal Buitrago, general practitioner. Personal work. No commercial interest. Not affiliated with, or endorsed by, any practice, health service or employer. No software vendor has been involved.

- **Try it:** open `referral-completeness-demo.html` in any browser. It loads nothing from the internet and stores nothing.
- **Argue with it:** use the Discussions tab. Disagreement is the point.
- **Found a mistake:** open an Issue. Errors are expected and corrections are welcome — see *How mistakes are handled* below.

---

## Goals

1. **Make one thing visible.** Every Australian state publishes lists of what a specialist referral should contain. As far as I could find, no health system routinely measures whether referrals actually contain it. This page shows, for one fictional case, what such a check looks like — so that clinicians, patients and people who build health software can see it and argue about it.
2. **Invite disagreement from people who know.** GPs, specialists, triage nurses, practice managers, patients, and people who build the software GPs use. Is a check like this useful? Where would it sit? What does it get wrong? What would it miss?
3. **Put the question on the record.** The written material in `docs/` sets out what was searched, what was found, and the narrower question that survived an attempt to disprove it.

## Non-goals

- This is **not a product** and will not become one.
- It is **not a clinical tool** and is **not intended for use in the care of any person**.
- It is **not a medical device** and makes **no clinical recommendation**. It does not tell anyone what to order, diagnose or do.

## What it does

You are shown a fictional referral letter for adult chest pain. You tick which items from the published NSW Health referral criteria the letter contains. The page counts what is mentioned and what is not, and shows you the published list it compared against. That is all.

The rule list is visible on screen and in the source code, and is reproduced verbatim from the NSW Health page it links to, with the nine sub-items of "Patient health summary" counted individually (see *Sources and licences*).

## Limitations and caveats

Stated here and on the page itself, before it runs.

- **One condition, one jurisdiction, one fictional letter.** Adult chest pain, NSW public outpatient criteria. Other states' criteria are Crown copyright and are deliberately not reproduced.
- **The reader does the ticking.** The software does not read or interpret the letter. This is deliberate: it keeps the page honest about what it can do and keeps it clear of anything that could be mistaken for software analysing clinical information.
- **It counts mentions, not quality.** A ticked box means an item is mentioned, not that it is correct, complete or clinically appropriate.
- **Nothing has been validated.** It has not been tested against real referrals and has no evidence of benefit.
- **Published criteria change.** The page reproduces the NSW list as it stood on the date shown. The linked NSW page is authoritative. A monthly automated check compares the two (see below).
- **Most presentations have no published criteria at all.** A complaint that is not on a state's list cannot be checked against anything, because nothing agreed exists to check it against. That absence is part of what this demonstration is meant to make visible.

## How mistakes are handled

Mistakes are expected. The protection is not the absence of errors but making them easy to find, easy to report and quick to correct, in public.

1. **Provenance on every rule.** Each list carries its source link, the "current as at" date printed on the source page, and the licence — on screen and in the code. Anyone can check any item against the source in under a minute.
2. **Dated releases.** Every version is tagged; `CHANGELOG.md` records what changed and when.
3. **A visible path to report errors.** The Issues tab, and a line on the page itself.
4. **A correction rule.** A confirmed error is corrected in the next release and recorded in the changelog; if it was material, the page notes what changed.
5. **Two automated checks**, plus an independent audit of the release before first publication (findings recorded in `CHANGELOG.md`).
   - `tests/test_demo.js` — opens the page in a headless browser and runs 46 checks: no external resources, no storage, the entry warning present, attribution present, the count correct for the default, all-ticked and none-ticked states, every screen and button working, no script errors, no horizontal overflow at phone width on the letter screen. Run: `node tests/test_demo.js referral-completeness-demo.html`.
   - `tests/check_criteria.py` — compares the demo's rule data and triage wording, item by item, against a fetched copy of the NSW page, and reports any reworded, missing or extra item and any change of date. Run: `python3 tests/check_criteria.py referral-completeness-demo.html tests/fetched/<latest>.json`. The author runs this monthly against a fresh fetch of the live NSW page (automated outside this repository); the outcome is recorded in `CHANGELOG.md`.

## The question behind it

One finding survived an attempt to disprove it across the health systems of Australia, the UK and Ireland, continental Europe, North America, the Asia-Pacific and the Middle East, and the international indicator sets:

> No health system publishes a recurring, system-level measure of whether GP-to-specialist referrals contained the clinical information the receiving clinician needed, derived from the referrals themselves. Content standards exist in every developed system; none is paired with routine measurement of adherence.

Confidence: moderate-to-high, not certain. The nearest counter-examples — NHS England's single-item FIT-with-referral indicator, the unpublished e-Referral Service dashboard, Queensland's one-off returned-referral figure, New Zealand's district-level decline reasons — are set out in `docs/`, together with what was searched and what was not found. If you know of a counter-example, that is exactly the feedback wanted.

## Repository contents

```
referral-completeness-demo.html   the demonstration (single file, no dependencies)
README.md                          this file
LICENSE                            MIT for code, with an Australian Consumer Law statement
NOTICE                             third-party content and attributions
CHANGELOG.md                       dated record of changes
tests/test_demo.js                 Agent 1 — internal tests (Node + Playwright)
tests/check_criteria.py            Agent 2 — consistency with the NSW page (Python 3)
tests/fetched/                     dated copies of the NSW list used for comparison
docs/                              written material: the question, what was searched, what was found
```

## Sources and licences

- Referral criteria: NSW Health, *Chest pain, discomfort and/or tightness in adult patients*, Statewide Referral Criteria, current as at 10 September 2026 — https://www.health.nsw.gov.au/outpatients/referrals/Pages/chest-pain-tightness-adult.aspx. © State of New South Wales NSW Ministry of Health. For current information go to www.health.nsw.gov.au. Reproduced under Creative Commons Attribution 4.0.
- Code: MIT licence (see `LICENSE`).
- Written material in `docs/`: Creative Commons Attribution 4.0 International, © Ferney Bernal Buitrago.

## Authorship note

Much of the code was produced with the assistance of an AI model, under the author's direction: the author chose what the page should and should not do, selected and verified the rule content against the published source, reviewed and edited every output, and is responsible for the result. This is recorded because the copyright status of AI-assisted code in Australia is unsettled; the licence above is offered on whatever rights exist.

## Reporting a problem

Open an Issue, or use the Discussions tab. Please do not include any real patient information in anything you post.
