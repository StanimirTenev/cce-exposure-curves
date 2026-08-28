# Ten questions to ask before you fix a migration order

A short companion to the migration guidance you are already required to follow. It does not
replace it. NIST SP 1800-38, the NCSC roadmap, ETSI TR 103 619, Singapore's Quantum-Safe
Handbook and the FS-ISAC roadmap all tell you to inventory, prioritise, then migrate. This
covers the prioritise step, which is where those documents say the least and where the
consequences of getting it wrong are largest.

**Each question wants a number or a name. None of them is a yes/no.** A checklist answered
"yes, we have that" is a checklist that has told you nothing.

---

## Before you order anything

**1. For what share of the systems your scan found do you have a stated confidentiality
lifetime?**

Not "do we have a data classification policy" — what fraction of the estate that policy actually
reaches. The answer is a percentage.

*A good answer:* "412 of 690 locations, 60%." *A bad answer:* "we classify our data."

**2. Which systems have no entry? Name them.**

This is the denominator. An ordering computed over the classified part is not an ordering over
the estate, and the difference is invisible unless someone writes it down.

## On the order itself

**3. Is your order derived from something measured, or from a criticality register?**

Most published guidance says to start with the most critical systems, and criticality registers
are usually inherited from an older risk process. Ask what measurement, if any, sits underneath.

**4. Does your order change if the capability arrives in 2035 rather than 2045?**

If the answer is no, the order is not conditioned on anything about the threat. It is a ranking
of your present opinion of your own systems, which is a different object.

**5. For each of your top ten: what is the confidentiality lifetime, and what is the emission
rate?**

The second one is usually missing. A system that emits a small volume of long-lived data can
matter more than a system that holds a large volume of short-lived data, and criticality does
not see the difference.

## The part migration does not fix

**6. Which systems have a required confidentiality lifetime longer than any assumption you
would defend in front of an auditor?**

Thirty-year retention protected by an assumption most people would defend for ten is not a
migration problem. Migrating it changes which conjecture you are relying on, not how long you
need the answer to hold.

**7. For those, what is the plan other than migration?**

There are three, and none of them is a new algorithm: retain the data for less time, split the
secret so that no single location holds it, or do not collect it. All three are unfashionable
and all three are cheaper than the alternative.

**8. Have you estimated what has already left?**

Migration protects future emission. It does nothing for data already captured. If harvest-now-
decrypt-later is in your threat model — Singapore's handbook names long-lived records as the
primary target — then the volume already gone is part of the answer, and it does not shrink.

## The evidence underneath

**9. Can you show the date and scope of the inventory the plan rests on?**

Scope means what was looked at and what was not: source, CI, infrastructure-as-code, runtime,
hardware, third parties. A plan built on an inventory of unstated scope inherits that silence.

**10. Does your scanner report what it could not read?**

Ask for the number of targets it attempted and failed to open — permission errors, binaries with
no symbols, containers it could not enter, repositories it lacked a token for. If the tool cannot
answer, "no findings" and "nothing vulnerable" are the same sentence in your report, and they are
not the same fact.

---

## Why the order matters more than it looks

The guidance converges on ordering by criticality: NIST triages critical business processes
first, the NCSC roadmap's 2031 milestone is the "most critical assets", PMMP groups by risk and
process. Singapore's handbook is the most careful of them — it names IT systems with long-lived
data as primary harvest-now-decrypt-later targets and asks for impact mapped against likelihood.
Even there, long-lived data is a category to include among the crown jewels rather than a
quantity to order by.

There is a result about this. No ordering built only on a system's present criticality can
minimise capability-conditioned exposure for all capability distributions, shelf lives, emission
rates, durations and objective weights. It is not that criticality-first is a poor heuristic; it
is that no static ranking of present properties can be optimal across the instances an
organisation might actually be in, because the optimal order depends on those quantities
jointly.

Proposition 3, in *From Q-Day to Exposure Curves*: https://doi.org/10.5281/zenodo.22126410

That is the whole argument for asking questions 3, 4 and 5 rather than accepting an inherited
register.

## What this checklist is not

It does not tell you what your order should be, and it produces no score, rating or risk level.
It is a set of questions whose answers you should have before you defend an order to anyone.
If several of them cannot be answered today, that is the finding, and it is a more useful one
than a number would have been.

---

*CC BY 4.0. Part of [cce-exposure-curves](https://github.com/StanimirTenev/cce-exposure-curves).
Corrections welcome as issues.*
