# What I got wrong: the record of a closed project

*Ferney Bernal Buitrago · September 2026 · CC BY 4.0*

*Status: a first-person account of a project I ran from March to August 2026 and closed. Included because the errors are more useful than the product was. Names of other people and organisations I dealt with privately are omitted.*

## What I set out to do

In March 2026 I formed a small company to build a tool that would check a GP's referral against the relevant specialist criteria before it was sent — flag what was missing, estimate the chance of rejection, and let the GP fix it. I filed provisional patents, wrote a grant application, built three browser prototypes and a Python one, drafted surveys, and approached practice-software vendors and health-service executives. Active work ran from early March to mid-April. I then took a clinical post in another state, and the project went quiet without anyone — including me — recording that it had.

In August 2026 I commissioned three pieces of work on my own files: an independent audit of the folder, an adversarial review instructed to find the competitor and the prior art, and an attempt to falsify the project's central research claim. On the strength of them I closed the project the same day. Total spend, about $2,600.

## The errors, in order of cost

**1. I claimed to be first, and I wasn't — by about seven years.** The stated differentiator was "the first Australian platform to perform multi-source clinical validation of referrals". Queensland Health has shipped exactly that, free, statewide, inside the software GPs already use, since about 2019 (see [02-what-already-exists](02-what-already-exists.md)). Two private vendors ship criteria-embedded forms across several states, also free. The competitor was findable in twelve minutes by someone told to look for it. Nobody was ever told to look.

**2. I counted four state criteria sets. There are at least five.** I omitted Western Australia, the state with the most mechanically enforced return process in the country.

**3. I filed patents on things that were already published.** Three self-filed provisionals, none reviewed by an attorney. Three independent prior-art searches, run without knowledge of each other, concluded each was anticipated — by standards and earlier patents dating from 2003 to 2026 — and that each would independently fail Australia's manner-of-manufacture test, because the specifications described functions without describing any mechanism. A fourth provisional was filed whose receipt I did not retrieve for five months. They will lapse.

**4. I built on a market with no price.** Every serious player gives the check to the GP free, because the receiving service benefits and the GP does not. The apparently empty space — a GP-purchased pre-send checker — is empty for a reason.

**5. I circulated numbers that were wrong by orders of magnitude.** "Only 2 papers in PubMed address referral quality frameworks"; "only 6 apply NLP to referral letters". Both were artefacts of narrow searches. The real literature runs to thousands of records and includes validated scoring instruments from three countries.

**6. I had already reached the right conclusion, and didn't act on it.** On 14 April I wrote in my own log: *"So it is not novelty. It's consolidating existing process / tools to be more integrative and efficient."* The grant application, the patents and a draft journal outline all continued to rest on the novelty claim I had just retracted.

**7. The governance layer stopped and nothing noticed.** I had built an unusually careful evidence process — a source-traced facts register with confidence grades, a section for disconfirming evidence, bias scans. It caught four fabricated or misattributed citations before they reached anyone. Then it fell silent on 15 April, and for four months the product direction was abandoned, a grant decision went unanswered and a regulator's letter went unread, with no log entry. A process that cannot detect its own silence is not a safety net.

**8. An error I identified propagated anyway.** A false statement about a meeting outcome was flagged as false in April, logged, never corrected, and by May had been re-asserted in the master tracker as fact. Logging an error is not fixing it.

## What survived

Two things.

The narrower research question in [01-the-question](01-the-question.md): content standards exist everywhere; routine measurement of adherence exists nowhere. The engine I designed as a product has no commercial future; pointed backwards at referrals already sent, it is a measurement instrument for a variable nobody has measured at scale. Instruments do not need customers.

And this record. The failure is a better story than the company was a business.

## Why publish it

Because the people best placed to tell me what else I have wrong are the ones who work on the other side of the referral — triage nurses, outpatient clinicians, practice managers, the people who build the software — and they cannot do that if the record stays in a drawer.
