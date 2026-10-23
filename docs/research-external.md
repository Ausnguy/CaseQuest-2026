# External Evidence Pack

**Researched:** 2026-10-23, by a research agent that downloaded and read each primary document. Page and section references come from the documents themselves, not from search snippets.

**Scope:** context and safety guidance only. **The case's costs and effect sizes come from the Solutions sheet, never from these sources.**

> **Like I'm 5:** The spreadsheet is our rule book for the game. These sources are what real grown-up experts (OSHA, NASA, the Department of Energy) say about fixing machines safely. We use them to show the judges that our idea makes sense in the real world. We don't use them to change the game's numbers.

## Headline cautions (read before citing anything)

1. **The famous DOE predictive-maintenance percentages are uncited inside the DOE guide itself.** These are the "8–12% cheaper than preventive", "35–45% less downtime" and "10x ROI" figures (S1 §5.3–5.4). The guide is also written for federal buildings, not oilfield pumps. If used, say: *"DOE-published, planning-grade ranges, originally uncited"*.
2. **No authoritative source quantifies how much a critical-spares program cuts repair time for onshore oil and gas.** The best government evidence is a Navy analogy (S16).
3. **OSHA's oil and gas pages focus on drilling and well servicing.** Production maintenance relies on general-industry rules: LOTO, confined space, and PSM where it applies.

## 1. Reactive vs preventive vs predictive maintenance

| Fact (source) | Use for us |
|---|---|
| DOE defines reactive ("run it till it breaks"), preventive, predictive and RCM. Top facilities run less than 10% reactive, 25–35% preventive and 45–55% predictive (S1 §5.2, §5.5). | A **criticality-based mix (hybrid)** is the textbook position. |
| Condition-based work shouldn't replace all interval work (S2 §2.2, p. 2-3). Scheduled overhauls can *raise* failure rates through infant mortality (S2 §4.1, p. 4-7). | Caution against blanket refurbishment (O5). |
| New predictive and RCM programs typically **increase** cost for about 2–3 years before net savings (S2 §3.5.3, p. 3-8). | Supports a staged rollout and honest first-year expectations. |
| Start with a small, visible project on troubled equipment, and keep before-and-after records (S1 §3.6). | A pilot-first roadmap. |

## 2. Critical spares

| Fact (source) | Use for us |
|---|---|
| Navy ships filled only 54% of part requests from onboard stock (goal 65%), and high-priority parts took 18.1 days versus a 5.6-day goal. 58% of work orders couldn't be completed because parts weren't onboard. Root cause: bad equipment records and bad demand data (S16, GAO-03-887, 2003). | The only quantified government example of what missing parts do. **It's an analogy:** naval, about 2000. The root cause links spare parts (O4) to good asset and work-order data. |
| DOE review criteria: critical spares stock levels should be based on usage, lead time, cost and shelf life, and adjusted with maintenance feedback (S18, criterion MT.3). DOE's Inspector General found untracked spares put critical parts at risk (S17). | How to *run* O4 responsibly. |
| Predictive monitoring gives lead time to order parts ahead of need (S1 §5.4). Time-to-repair should include parts delivery (S2 §14.3). | O1 and O4 reinforce each other. |

## 3. What condition monitoring can and can't do

| Fact (source) | Use for us |
|---|---|
| Vibration monitoring detects wear, imbalance, misalignment and **bearing damage** on rotating equipment, including pumps and compressors (S2 §6.3.1.1, p. 6-3). Electrical conditions are assigned to *other* tools such as motor-current analysis and insulation testing (S1 Table 6.1.1; S2 Table 6-1). | Matches our data: vibration signals appear before bearing and seal failures and not before electrical trips or process upsets. |
| Navy studies: probability of detection 0.76–0.92, false-alarm rate 0.08 (S2 §6.3.1.3). The underlying studies aren't cited. | Real-world monitoring is good, not perfect. Our backtest looks cleaner because the data is synthetic, so say so. |
| You need at least 3 data points to confirm a trend. After an alert, shorten the sampling interval (S2 §5.2.2.2, §4.1). The most common practice is biweekly or monthly (S2 p. 5-7). | Daily snapshots are *more* frequent than typical practice, but a 2-day warning means about 2–3 points. |
| In the cited studies, 77–92% of failures were random rather than age-related (S2 §4.1; aircraft and Navy data). | Monitoring can't catch everything, which is an argument for a hybrid. |
| Predictive equipment needs a serious commitment to training (S1 §6.1). | The O6 training prerequisite is real. |

## 4. Safety: controls a faster-maintenance initiative must never bypass

| Control | Source |
|---|---|
| Lockout/tagout: shut down, isolate, lock, relieve stored energy, **verify isolation** before work. Tags are never bypassed. | 29 CFR 1910.147 §(c)(7), (d)(1)–(6) (S4) |
| Controlled restart: inspect the area, confirm people are clear, notify | 1910.147 §(e) (S4) |
| Calibrated gas and oxygen monitors, and **no lone work near tanks**. Nine tank-gauging deaths in 2010–2014, all with the worker alone or unobserved; H2S was ruled out in every one. | NIOSH/OSHA 2016-108, pp. 1, 4, 6 (S3) |
| H2S limits: OSHA ceiling 20 ppm (peak 50); NIOSH IDLH 100 ppm. Workers lose the sense of smell around 100–150 ppm. | OSHA H2S page (S5); 29 CFR 1910.1000 Table Z-2 (S7) |
| Confined-space permits, atmospheric testing (oxygen, then flammables, then toxics) and an attendant. Hot-work permits. | 29 CFR 1910.146 (S9); 1910.119(k) (S8) |
| Rated lifting capacity, and daily sling inspection | 29 CFR 1910.184, 1910.180 (S10) |
| Secondary containment, sealed dike drains and overfill alarms at tank batteries | 40 CFR 112.9 (S11) |
| Don't bypass safety devices while troubleshooting. Incidents cluster at startups, so use stop-work authority. | CSB Safety Digest (S14) |

Three of five on-site oil and gas extraction fatalities are struck-by, caught-in or caught-between, including from high-pressure lines (S6).

**For us:** the "restart" and "dispatch" stages must **not** be squeezed in ways that skip verification or send a lone worker. This is why the Solutions sheet has zero restart reduction for every option, and why `protected_repair_hours` exist.

## 5. Human oversight of alerts

| Fact (source) | Use for us |
|---|---|
| NIST AI RMF: define human-AI roles (GOVERN 3.2), document oversight (MAP 3.5), allow override and deactivation (MANAGE 2.4), measure false positives and negatives, and track how often humans overrule the system (Appendix C) (S12) | The prototype's **employee review** step |
| CISA/NSA AI-in-OT (Dec 2025): humans remain responsible for functional safety. Route passive recommendations through change management. Know false-alarm rates against the base rate. Keep a manual fallback. Use push-based, buffered data for OT (S13, pp. 16–20) | Alerts *advise* a qualified planner and never authorize work. Supports edge buffering. |

## 6. KPIs with external definitions

| KPI | Definition and benchmark | Source |
|---|---|---|
| Equipment availability | hours available at capacity ÷ total hours; > 95% | S1 Table 3.1.1 |
| Schedule compliance | scheduled hours worked ÷ hours scheduled; > 90% | S1 Table 3.1.1; S2 §12.10 |
| Emergency maintenance share | emergency hours ÷ total hours; < 10% | S1; S2 Table 12-1 |
| Time to repair / mean down time | Includes diagnosis, **parts delivery**, repair and return to service. This maps to our five downtime stages. | S2 §14.3 |
| Alert precision and override rate | False and true positives against the base rate; human overrides | S12, S13 |

## Source register

- **S1** PNNL for DOE FEMP. *O&M Best Practices Guide, Release 3.0* (PNNL-19634), Aug 2010. https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-19634.pdf
- **S2** NASA. *RCM Guide for Facilities and Collateral Equipment*, Sep 2008. https://www.nasa.gov/wp-content/uploads/2023/06/nasa-rcmguide.pdf
- **S3** NIOSH/OSHA. *Hazard Alert: Manual Tank Gauging and Sampling* (2016-108), Feb 2016. https://www.cdc.gov/niosh/docs/2016-108/
- **S4** 29 CFR 1910.147 (LOTO). https://www.ecfr.gov/current/title-29/section-1910.147
- **S5** OSHA. *Hydrogen Sulfide – Hazards*. https://www.osha.gov/hydrogen-sulfide/hazards
- **S6** OSHA. *Oil and Gas Extraction – Hazards*. https://www.osha.gov/oil-and-gas-extraction/hazards
- **S7** 29 CFR 1910.1000 Table Z-2. https://www.ecfr.gov/current/title-29/section-1910.1000
- **S8** 29 CFR 1910.119 (PSM). https://www.ecfr.gov/current/title-29/section-1910.119
- **S9** 29 CFR 1910.146 (confined spaces). https://www.ecfr.gov/current/title-29/section-1910.146
- **S10** 29 CFR 1910.180 / 1910.184 (cranes and slings). https://www.ecfr.gov/current/title-29/section-1910.184
- **S11** 40 CFR 112.9 (SPCC, onshore production). https://www.ecfr.gov/current/title-40/section-112.9
- **S12** NIST. *AI Risk Management Framework 1.0* (AI 100-1), Jan 2023. https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf
- **S13** CISA/NSA et al. *Principles for the Secure Integration of AI in OT*, Dec 2025. https://www.cisa.gov/sites/default/files/2025-12/joint-guidance-principles-for-the-secure-integration-of-artificial-intelligence-in-operational-technology-508c.pdf
- **S14** US CSB. *Safety Digest: Incidents during Startups and Shutdowns*. https://www.csb.gov/assets/1/6/csb_digest_-_startup_shutdown.pdf
- **S15** US CSB. *Drivers of Critical Chemical Safety Change: Preventive Maintenance*, Apr 2018. https://www.csb.gov/assets/1/6/csb_cdl_fact_sheet_-_preventive_maintenance.pdf
- **S16** GAO. *Defense Inventory: Spare Parts Support Aboard Deployed Navy Ships* (GAO-03-887), Aug 2003. https://www.gao.gov/assets/gao-03-887.pdf
- **S17** DOE OIG. *Management of Spare Parts at Selected Sites* (DOE/IG-0936), May 2015. https://www.energy.gov/sites/default/files/2015/05/f22/DOE-IG-0936.pdf
- **S18** DOE EA. *CRAD 30-06, Conduct of Maintenance*, Apr 2019. https://www.energy.gov/sites/default/files/2019/04/f61/EA%20CRAD%2030-06%20Rev%200%20-%20Conduct%20of%20Maintenance.pdf

**Could not access (paywalled or blocked):** API RP 54/55/74, ISO 13373/17359/55000, ISA-18.2, SMRP metrics, DoDI 4151.22, and the NIOSH Pocket Guide (OSHA's page was used for the same values). No numbers from these are cited.
