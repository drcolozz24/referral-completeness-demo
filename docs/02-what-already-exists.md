# What already exists: pre-send referral checking in Australia and elsewhere

*Ferney Bernal Buitrago · September 2026 · CC BY 4.0*

**Declaration.** Every statement below about a named organisation or product is taken from that organisation's own published material, a government page, or a named trade-press article, each linked beside the statement, as read on 24 September 2026. Nothing is included that I could not link to a page I opened. Where I express a view of my own it is marked *(mine)*. Nothing here is a comment on any organisation's people. If a statement is out of date or wrong, open an Issue with the source and it will be corrected and the correction recorded.

The demonstration in this repository shows a referral being checked against a published criteria list before it is sent. That idea is not new. Anyone thinking about it should know what is already in production, because the interesting questions start after that.

## Australia

**Queensland Health — GP Smart Referrals.** Launched from within Best Practice and MedicalDirector. Queensland Health's own user guide (July 2023) states that conditions returned in the search "are based on Clinical Prioritisation Criteria (CPC)", that the "CPC Clinical Urgency field will display information that advises the timeframe for a public appointment", and that "the submit button will remain disabled until all missing fields are complete". Source: [GP Smart Referrals User Guide, Queensland Health](https://www.health.qld.gov.au/__data/assets/pdf_file/0017/1201085/gp-smart-referrals-user-guide.pdf).

**Queensland Clinical Prioritisation Criteria.** "Over 419 conditions published across 27 specialties"; "almost 1,000 clinicians including General Practitioners (GPs), Specialists, Nurses and Allied Health staff have been involved in the development since the initiative commenced in 2014". Source: [Clinical Excellence Queensland](https://www.clinicalexcellence.qld.gov.au/improvement-exchange/clinical-prioritisation-criteria-cpc-making-triage-everyones-business) (page updated April 2025).

**Consultmed.** Digital referrals, clinical advice and guidance, virtual triage and consent management, integrated with Best Practice via Halo Connect ([Best Practice, 11 May 2026](https://bestpracticesoftware.com/blog/consultmed-smarter-digital-referrals-specialist-advice-and-guidance/): "over 1,000 connected Bp practices" within "a national network of more than 55,000 healthcare providers"); integrated with MedicalDirector Clinical ([MedicalDirector marketplace](https://www.medicaldirector.com/marketplace/consultmed)); integrated with MediRecords ([MediRecords, 25 May 2026](https://www.talkinghealthtech.com/news/medirecords-and-consultmed-integration-accelerates-digital-referrals-and-access-to-clinical-advice-guidance): "more than 60,000 healthcare professionals … including over 4,000 GP practices"). Founded by a paediatrician and launched into Sydney Children's Hospitals Network in March 2021 ([Startup Daily, 18 Jan 2022](https://www.startupdaily.net/topic/consultmed/)). Ongoing coverage: [Pulse+IT](https://www.pulseit.news/tag/consultmed/).

**HealthLink SmartForms — Western Australia pilot.** WA Primary Health Alliance reported on 15 June 2026 that four SmartForms with "embedded referral access criteria" had been developed for a three-month pilot from September 2026, "accessed via HealthLink from within the Best Practice, Medical Director, Genie and Communicare practice management software". Source: [WAPHA, 15 Jun 2026](https://news.wapha.org.au/wa-health-to-pilot-smartforms-for-public-outpatient-referrals/).

**Western Australia — Referral Access Criteria.** Since 2022, "the Central Referral Service will ensure that all mandatory information as outlined in the RAC has been provided before allocating the referral" ([WAPHA, 20 Sep 2022](https://news.wapha.org.au/specialist-referral-access-criteria-update/)). From 30 October 2026 the criteria "will no longer be mandated requirements through the Central Referral Service, but will continue as clinical guidance" ([WAPHA, 15 Jun 2026](https://news.wapha.org.au/wa-health-to-pilot-smartforms-for-public-outpatient-referrals/)). *(Mine: the one state that made criteria compulsory is walking that back — a data point on how enforceable sender-side rules turn out to be.)*

**Victoria and NSW.** Both publish Statewide Referral Criteria free ([Victoria](https://www.health.vic.gov.au/statewide-referral-criteria), updated 27 July 2026; [NSW](https://www.health.nsw.gov.au/outpatients/referrals/Pages/default.aspx)). The Victorian, Queensland and WA criteria are Crown copyright with all rights reserved; NSW's are Creative Commons Attribution, which is why this demonstration uses NSW's.

**Receiving-side systems.** Novari Health reported "a 40% reduction in referrals to gastroenterology and colorectal surgery specialty outpatient clinics" at Central Adelaide Local Health Network after its eRequest pathway went live. Source: [Novari Health press release, 6 Aug 2024](https://www.novarihealth.com/novari-healths-referral-and-wait-list-management-technology-successful-in-australia/) — the vendor's own figure.

## Elsewhere

**England — NEC Rego.** Described as producing referrals "fully validated against referral pathways", with prompting where, for example, a cancer history may indicate a different pathway; one customer reported rejected referrals falling "from 25 percent to two percent". Source: [HTN, 8 Aug 2024](https://htn.co.uk/2024/08/08/htn-now-nec-rego-on-simplifying-the-referral-process-to-support-the-right-care-first-time/) — trade press reporting the vendor.

**Corti.** On 3 February 2026 Corti announced an agent library including "pre-configured agents validated for immediate production use across medical coding, documentation, referral coordination, clinical education, and clinical guidelines". Source: [Corti newsroom](https://www.corti.ai/newsroom/corti-launches-agentic-infrastructure-to-scale-ai-deployment-in-healthcare).

**Heidi Health.** Announced "Heidi Evidence" on 21 September 2026. Source: [Heidi Health blog](https://www.heidihealth.com/en-au/blog/heidi-launches-evidence). I make no claim here about what it contains.

## Two observations *(mine)*

1. **The check is offered to the GP by the receiving side, or by the state.** Queensland's is government-run; WA's forms are being piloted by the health department; Consultmed and HealthLink are embedded in the practice software through arrangements with health services. On what I can see, the receiving service is the party that captures the value of a clean referral, and that is who pays for the check. I did not find a GP-side, GP-purchased pre-send checker in production. I tried to build one; see [03-what-i-got-wrong](03-what-i-got-wrong.md).
2. **The check is becoming a commodity; the measurement is not.** Comparing text against a criteria document is now offered as a configurable component by more than one vendor, and hand-encoded rule sets have to be maintained every time a state revises its criteria. What I could not find anywhere is the thing pointed the other way: a recurring measure of what referrals actually contained. See [01-the-question](01-the-question.md).

## What this means for the demonstration

The page in this repository is not a proposal to build another pre-send checker. It is a way to look at the idea, in the open, and argue about the questions above.
