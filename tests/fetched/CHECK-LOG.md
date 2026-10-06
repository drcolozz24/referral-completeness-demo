# Record of checks against the live NSW Health page

One line per check, including checks that could not run. Lines are added by the monthly
GitHub Actions job (`.github/workflows/monthly-nsw-check.yml`) or by hand when a check is run
another way. A month with no line means no check was recorded for that month.

"Consistent" means the Required list, the If-available list, the three triage categories and
the "current as at" date in the demonstration matched the NSW page as fetched that day. How the
page was obtained is stated, because it limits what a match means: text from an AI fetch tool
is the text as that tool returned it, not verified against the raw HTML.

| Date | Run by | Outcome | Detail |
|---|---|---|---|
| 2026-09-24 | By hand, AI fetch tool | CONSISTENT | Demo aligned with the page that day; snapshot nsw-chest-pain-adult-2026-09-24.json |
| 2026-10-01 | Scheduled AI task, unattended | COULD NOT RUN | The fetch needed an approval nobody was present to give; two attempts; nothing compared |
| 2026-10-06 | By hand, AI fetch tool | CONSISTENT | 13 required, 5 if-available, 3 triage categories and the date (10 September 2026) identical; Emergency section and headings recorded for the first time as a baseline; snapshot nsw-chest-pain-adult-2026-10-06.json |
| 2026-10-07 | GitHub Actions (started by hand) | COULD NOT RUN | the page was fetched but not every section could be read — Emergency section not found; expected 3 triage categories in a table, found 2. NSW may have restructured the page; a person should look. — [run](https://github.com/drcolozz24/referral-completeness-demo/actions/runs/37547901323) |
| 2026-10-07 | By hand, raw HTML saved from Chrome | CONSISTENT | First character-for-character check against the page's own HTML: 13 required, 5 if-available, 3 triage categories and the date identical. Found that NSW attaches a note to "Cardiovascular disease risk assessment" which the demo does not show; the demo now says so. The failed run above was the parser, not NSW: it has been corrected against this page. Snapshot nsw-chest-pain-adult-2026-10-07-saved-page.json |
