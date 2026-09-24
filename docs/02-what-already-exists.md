# What already exists: pre-send referral checking in Australia and elsewhere

*Ferney Bernal Buitrago · September 2026 · CC BY 4.0*

*Status: a landscape as at August 2026, compiled from the organisations' own public materials. Facts are attributed; opinion is marked as mine. Nothing here is a comment on any organisation's people. Corrections welcome — open an Issue with the source.*

The demonstration in this repository shows a referral being checked against a published criteria list before it is sent. That idea is not new. Anyone thinking about it should know what is already in production, because the interesting questions start after that.

## Australia

**Queensland Health — GP Smart Referrals.** Integrated into Best Practice and MedicalDirector, deployed across every Hospital and Health Service plus Mater Public, free to GPs, roughly two million referrals a year. Queensland Health's own user documentation describes, before the GP presses send: condition search driven by the Clinical Prioritisation Criteria; the condition's minimum referral criteria rendered into the form; a predicted triage outcome ("meets the criteria for a public appointment within 30 / 90 / 365 calendar days"); a submit button that stays disabled until required fields are complete; and an override that requires a written clinical reason and carries the warning that it "opens the referral to possible non-acceptance from Queensland Health". Behind it sits a corpus of 419 condition-specific criteria across 27 specialties, built by nearly a thousand clinicians between 2015 and 2020. In production since about 2019. *[Source: Queensland Health and Gold Coast Health user documentation; links to be confirmed before publication.]*

**Consultmed.** Sydney-based, founded 2019. Digital referrals, clinical advice and guidance, virtual triage, consent management and AI digitisation of paper referrals, embedded in Best Practice (via Halo Connect), MedicalDirector, Gentu and Shexie; live in public hospitals in several states; by mid-2026 described by partners as reaching more than 4,000 GP practices and 55–60,000 providers. Free to referrers. Sources: [Best Practice, May 2026](https://bestpracticesoftware.com/blog/consultmed-smarter-digital-referrals-specialist-advice-and-guidance/); [MediRecords, May 2026](https://www.talkinghealthtech.com/news/medirecords-and-consultmed-integration-accelerates-digital-referrals-and-access-to-clinical-advice-guidance); [MedicalDirector marketplace](https://www.medicaldirector.com/marketplace/consultmed); [Pulse+IT coverage](https://www.pulseit.news/tag/consultmed/).

**HealthLink SmartForms.** Condition-specific electronic referral forms with jurisdiction-specific criteria embedded, across nine practice-software platforms and a large majority of NSW general practices; NSW building forms aligned to the Statewide Referral Criteria; a WA pilot with embedded Referral Access Criteria scheduled for late 2026. Funded by the receiving service; free to GPs. *[Links to be confirmed.]*

**The states themselves.** NSW, Victoria, Queensland, South Australia and Western Australia all publish referral criteria free. They author the criteria, commission the forms and run the receiving triage. WA's criteria were mandatory in eight specialties and enforced by a Central Referral Service that returns non-conforming referrals; WA has announced the criteria move from mandatory to advisory on 30 October 2026 — worth noting as a data point on how enforceable sender-side rules turn out to be. *[Source: WA Health; to be confirmed.]*

**Receiving-side systems.** Novari / VitalHub's eRequest at Central Adelaide reported large reductions in referrals to some clinics after triage-side screening. *[Source to be confirmed.]*

## Elsewhere

**England — NEC Rego.** Validates referrals against local guidelines before sending, with red-flag prompting; deployed across several integrated care boards; one customer reported rejections falling from about 25% to about 2%. *[Vendor material; to be confirmed.]*

**AI scribes and clinical-agent vendors.** Heidi Health licensed HealthPathways — the localised Australian referral-criteria layer — as a content partner in February 2026, and its templates accept free-text instructions, so a clinician can build a criteria check inside a scribe template. Corti announced in February 2026 composable agents for guideline compliance, note completeness and referral generation. Ambience and Abridge shipped in-encounter documentation-gap detection in 2025–26. *[Vendor announcements; to be confirmed.]* The US prior-authorisation industry has run automated clinical-criteria adjudication at scale for years.

## Two observations (mine)

1. **Everyone gives the check away to the GP.** Queensland's is government-funded; Consultmed is free to referrers; SmartForms are paid for by the receiving service; scribe vendors offer free tiers. The receiving service captures the value of a clean referral and the GP does not. A GP-side, GP-purchased checker is an empty space because it is a pricing graveyard, not because nobody thought of it. I found this out by trying.
2. **The check is a commodity; the measurement is not.** "Compare text against a criteria document" is now an off-the-shelf capability, and hand-encoded rule sets break every time a state revises its criteria — Victoria revised in February, April and July 2026. What nobody has built is the thing pointed the other way: a recurring measure of what referrals actually contained. See [01-the-question](01-the-question.md).

## What this means for the demonstration

The page in this repository is not a proposal to build another pre-send checker. It is a way to look at the idea, in the open, and argue about the questions above.
