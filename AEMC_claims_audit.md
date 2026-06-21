# AEMC Claims Audit — Full Report
**Grattan Institute: AEMC Electricity Pricing Review submission**
**Prepared after end-to-end reading of the AEMC Final Report (184pp, 18 June 2026)**

---

## What this is

This document audits every major claim and argument in our interactive visualization against what the AEMC final report actually says. It is organised as:

1. **Claims we get right** — accurately represent the report
2. **Claims that need nuance** — true but incomplete or framed too sharply
3. **Claims the report doesn't actually make** — things we may be arguing against that aren't there
4. **Things the AEMC says that we should probably acknowledge**
5. **Recommended changes to the visualization**

---

## 1. Claims we get right

### ✅ The cross-subsidy problem is real and the AEMC acknowledges it

The report consistently states that under the current volumetric tariff framework, consumers with solar/batteries can reduce their network cost contributions while still relying on the shared grid. This is unambiguously asserted throughout Appendices C and D.

> *"Consumers with access to CER can reduce the amount they contribute to network costs through volumetric charges, even though they continue to rely on shared infrastructure. Consumers without access to CER – including renters, apartment residents and lower-income households – may be left carrying a larger share of those costs."* — Appendix C, p.71

Our visualization frames this correctly. The AEMC does see a cross-subsidy problem — we're not misrepresenting that.

### ✅ Revenue neutrality — the reform is about who pays, not how much

The report is clear that total network revenue is unchanged. The reform shifts cost recovery from volumetric (per-kWh) charges toward a shared network access charge. Our visualization correctly states this.

### ✅ The $2–6 billion savings figure is accurate

The correct figure is **$6 billion in cumulative savings over 15 years (present value)**. The report cites this in multiple places (p.38, Appendix D.2, Appendix H.1.1). The range "$2–$6 billion" appears in some earlier AEMC publications; the final report settles on "$6 billion." Our bill impact section should make clear this is 15-year cumulative PV, not annual.

**Recommended fix:** If our visualization says "$2–6bn," change to "$6bn cumulative over 15 years (present value)" to match the final report's precise claim. The average annual bill reduction is ~$40–$80 per customer by 2040.

### ✅ Solar payback periods affected only marginally

The report models a 10-year transition to 80% network access charges and finds payback periods for solar/battery investments are "marginally increased." The summary notes this excludes potential gains from dynamic pricing rewards. Our "~3 months longer" figure is consistent with this.

### ✅ The three groups who can't access CER

The AEMC consistently identifies three distinct groups: **renters, apartment dwellers, and lower-income households.** Our visualization correctly reflects all three. This is the AEMC's own framing, not something we've invented.

### ✅ Consumer protections are not yet designed

The report is explicit: consumer protections are a "critical design feature" and "necessary precursor" to reform, but the specific mechanism is not yet determined. HoustonKemp was commissioned to identify *options*, not specify final protections. We correctly note protections are undesigned.

---

## 2. Claims that need nuance

### ⚠️ We may be over-simplifying "fixed charge"

**What we say:** The reform increases fixed charges, which hurts low-consumption households (renters, pensioners).

**What the AEMC actually says:** The AEMC has explicitly **rebranded away from "fixed charge"** to **"shared network access charge"** (Appendix C, Box 16, p.72). Their stated reason: the word "fixed" implies (a) uniform for all customers, and (b) the same as a retailer's standing charge. Their final recommendation explicitly allows the shared network access charge to **vary by connection type and historical consumption**, so low-use households could pay less than high-use ones.

> *"The level of the 'shared network access' charge may need to vary depending on the methodology deployed to design the underlying network tariff. For example, the charge could vary according to aspects of a customer's historical consumption or a customer's characteristics. As such, this charge may not be uniform across all customers."* — Appendix C, Box 16, p.72

**Recommended fix:** Our visualization's bill impact section should note that the AEMC does not propose a uniform fixed charge for all customers — it proposes that networks have flexibility to tier or vary the charge. Our modelling (which applies a flat per-household increase) represents one scenario, not the AEMC's mandated design. We should frame it as "under a scenario where shared costs are spread equally across connections" and acknowledge the AEMC's preferred approach includes differentiation.

### ⚠️ The "solar = wealthy" premise — what the AEMC actually claims

**What we argue:** The AEMC's distributional premise — that solar owners are wealthy — is not supported by postcode-level data.

**What the AEMC actually argues:** The AEMC does NOT directly claim "solar owners are wealthy." Their equity argument is more precisely:

> "All connected consumers continue to rely on shared network infrastructure and should contribute to the costs of maintaining access to it. Where CER owners can avoid these costs, they are increasingly recovered from consumers who cannot afford or do not own CER, including **renters and low-income households**." — Appendix D.3.2, p.109

The AEMC's argument is about who is *excluded* from solar (renters, apartment-dwellers, lower-income), not about the income profile of solar *owners*. The claim is that the non-solar group skews toward disadvantaged consumers. They are NOT claiming the solar group is uniformly wealthy.

**Why this matters:** Our data shows solar penetration is high across all income deciles among houses, including middle-to-lower income postcodes. This DOES challenge the AEMC's implicit premise (because it shows that even if the solar group includes some disadvantaged households, the policy doesn't protect the non-solar poor — it just hurts them differently). But we should frame this more carefully:

- **Our stronger argument:** "The AEMC implicitly assumes that shifting costs away from solar households toward non-solar households is equitable. But our data shows ~40%+ of lower-income homeowner households already have solar, meaning the 'non-solar household' category is not a reliable proxy for disadvantage."
- **Not our argument:** "Solar owners aren't wealthy" (some are, some aren't — this is complicated by the confounders we identified: dwelling type, tenure).

**Recommended fix:** The "cross-subsidy" section should explicitly engage with the AEMC's actual mechanism (who can't access solar, not who has it) and show that the fixed charge solution doesn't distinguish between non-solar poor (whom the AEMC wants to protect) and non-solar renters or apartment dwellers (who face the same charge increase but can't respond by getting solar either). The AEMC's solution creates a category ("non-solar consumer pays fixed charge") that does not track the problem it's solving.

### ⚠️ The cross-subsidy direction in our cameo model

Our AEMC cameo section says something like "Karen's solar panels let her reduce her grid bill while Tom pays more." This is accurate as a description of the mechanics. But we should be careful not to imply the AEMC's only claim is that solar owners are rich and non-solar owners are poor. The AEMC also notes:

> "This is particularly important because shared network investment is driven by the need to meet peak demand, and both CER and non-CER customers use the network during peak periods." — D.3.2

In other words, there's also an efficiency argument (solar households use the grid at peak times but don't pay for it via volumetric charges). Our cameo should acknowledge both the equity AND efficiency arguments the AEMC makes.

### ⚠️ "The reform hurts renters" — check direction

This is accurate but slightly complex. The AEMC says renters CURRENTLY pay too much under the status quo (because they can't reduce volumetric consumption via solar). Under the reform:

- A uniform fixed charge would also hurt renters (they can't reduce the fixed charge by getting solar)
- BUT: the AEMC claims dynamic pricing could eventually let renters benefit through flexible demand products

So renters are caught in a bind either way — the AEMC is not claiming the reform fixes the renter problem, just that it fixes the growing imbalance at a system level. Our argument that "renters lose under both regimes" is actually CONSISTENT with the AEMC's own analysis; we should use this more explicitly.

### ⚠️ The $6bn savings — who benefits?

Our visualization should note that the $6bn is aggregate system savings flowing to all consumers over 15 years (through lower network augmentation costs etc.), not a direct transfer to non-solar households. The distribution of these benefits is not modelled in the report. We should not imply non-solar consumers get the savings directly.

---

## 3. Claims the report does NOT make (things we might be arguing against that aren't there)

### ❌ The AEMC does not claim solar owners are predominantly wealthy

Nowhere in the 184-page report does the AEMC say "solar adopters have high incomes" or "solar penetration is concentrated in wealthy postcodes." Their equity argument is about the people excluded from solar, not about the income level of solar owners. We should not argue against a claim the report doesn't make.

### ❌ The AEMC does not propose a uniform flat charge for all customers

The final report explicitly moves away from this. It proposes a principles-based framework allowing charges to vary by consumption history, connection characteristics etc. If we're modelling equal per-household fixed charge increases, we need to be clear this is one scenario, not the AEMC's actual proposal.

### ❌ The AEMC does not claim higher fixed charges will make solar adoption fall sharply

The distributional analysis models only a "marginal" increase in payback periods. We should not overstate the solar investment impact.

### ❌ The AEMC has not finalised consumer protections — but it says they're mandatory

We sometimes imply "the AEMC hasn't designed any consumer protections." More accurately: the AEMC says protections are a mandatory design element of any reform, it just hasn't specified what they look like yet. The distinction matters — we should say "without adequate protections that don't yet exist" not "the AEMC ignores consumer protections."

---

## 4. Things the AEMC says that we should probably acknowledge

### 🔶 The status quo also hurts the same people

The AEMC makes a strong point that even without reform, low-income and renter households face worsening outcomes as CER uptake grows and network costs are recovered from a shrinking volumetric base:

> "It is these consumers, namely, those who are socially disadvantaged and least engaged with the energy market who are also likely to incur adverse bill impacts under the **current** network pricing framework and who will bear an increasing share of the costs of shared electricity network through volumetric charges, particularly as CER take up increases." — D.3.2

Our visualization is somewhat silent on this. We should acknowledge: inaction also has distributional costs. The question is whether the reform solution is better or worse than the status quo trajectory — and for whom.

### 🔶 The AER's suggestion on minimum charge floors

The AER itself (in submissions to the AEMC) suggested: *"the charge for the minimum level of capacity required to stay connected to the network may need to be very low or zero"* with differentiated tiers above that floor. This is a more consumer-protective design than a flat fixed charge. Our visualization doesn't reference this potential design option.

### 🔶 QLD/SA jurisdictional specifics

For QLD, the Uniform Tariff Policy means regional and SEQ customers pay the same — which affects how the reform plays out in Queensland specifically. Worth noting given QLD has the most politically sensitive seats in our electoral chart.

### 🔶 The AEMC frames the reform as eventually reducing CER export limits

A key benefit the report emphasises: under dynamic pricing, solar owners would get better export rewards when the grid needs their power, replacing the current blunt export limits and curtailment. This is a genuine benefit to current solar owners that our visualization doesn't acknowledge at all.

---

## 5. Recommended changes to the visualization

### Priority 1 — Terminology fix
Replace "fixed charge" with "shared network access charge" or "network access charge" throughout, noting in a tooltip/footnote that the AEMC's preferred design would allow this to vary by connection type.

### Priority 2 — Nuance the "solar = wealthy" section
The cross-subsidy section should frame our data finding more precisely: "The reform assumes that 'solar households' and 'advantaged households' sufficiently overlap to make the cross-subsidy problem worth fixing with a broad charge shift. Our postcode data suggests this overlap is weaker than assumed — particularly because income is a poor predictor of solar adoption among homeowners."

### Priority 3 — Add "status quo also has costs" acknowledgement
A brief line in the policy conclusion acknowledging that volumetric charges also shift costs onto low-income non-CER households as solar uptake grows. Frame our argument as: "the reform addresses a real problem through an instrument that fails to distinguish the groups it's meant to protect."

### Priority 4 — Savings figure precision
Change any reference to "$2–6bn" to "$6bn cumulative over 15 years (present value)" and add that average annual per-customer savings by 2040 are $40–$80.

### Priority 5 — Renter framing
Strengthen the renter section to use the AEMC's own logic: renters are already losing under the status quo AND would continue to lose under the reform. This is the AEMC's own implicit concession, buried in D.3.2.

### Priority 6 — Consumer protections framing
Change "no consumer protections designed" to "consumer protections identified as mandatory but not yet specified — the AEMC commissioned HoustonKemp to identify options, not finalise a design."

---

## Summary table

| Claim in our viz | Accuracy | Notes |
|---|---|---|
| Cross-subsidy problem is real | ✅ Accurate | AEMC confirms throughout |
| Solar owners can reduce network charges | ✅ Accurate | Core AEMC mechanism |
| Renters/apt-dwellers/low-income are disadvantaged | ✅ Accurate | AEMC's exact three groups |
| Revenue neutrality | ✅ Accurate | Confirmed p.36 |
| $2–6bn savings | ⚠️ Slightly off | Final report says $6bn cumulative 15yr PV |
| Solar payback ~3 months longer | ✅ Accurate | "Marginal" increase per D.3.4 |
| Protections not designed | ⚠️ Needs nuance | AEMC says they're mandatory but unspecified |
| "Fixed charge increase" | ⚠️ Imprecise | AEMC now calls it "shared network access charge" and allows variation |
| AEMC claims solar = wealthy | ❌ Not their claim | AEMC's claim is about who's excluded from solar |
| Uniform flat charge for all | ❌ Not their proposal | AEMC explicitly rejects uniform charges |
| Renters hurt by reform | ✅ Accurate | But AEMC also says status quo hurts renters |
| Status quo is fine | ⚠️ We imply this? | We should acknowledge status quo also worsens |
| One Nation electorates have high solar | ✅ Accurate data | r=0.37, top QLD/NSW electorates >50% solar |
| Electoral exposure to reform | ✅ Accurate framing | Marginal seats have above-average solar |

---

*Report compiled: June 2026*
*Based on full reading of AEMC Electricity Pricing Review: Final Report, 18 June 2026, 184 pages*
