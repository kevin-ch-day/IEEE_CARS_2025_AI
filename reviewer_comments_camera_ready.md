# IEEE CARS 2026 camera-ready revision control

Internal checklist for the author and professor. This is **not** a conference rebuttal letter.

- Paper: *An Empirical Study of Privacy and Security Risk in Android Apps Using Static and Runtime Evidence*
- Paper ID: `1571323717`
- Primary dataset (historical, submitted): **15 apps / 123 runs** (44 strict-idle, 23 QFG, 56 interactive)
- Starting source: GitHub `kevin-ch-day/IEEE_CARS_2025_AI` commit `49c08c4`
- Working branch: `camera-ready-2026` (local; do not push until approved)
- Untouched baseline branch: `submission-baseline` (= `49c08c4`)
- Professor-ready target: Thursday night, 20 August 2026
- Internal submission target: 28 August 2026

---

## Reviewer 1 — Weak Accept

### Strengths

- well written;
- useful Android evaluation application;
- multiple app types.

### Issues

- undefined qualification policy `P` in Algorithm 1;
- one temporal collection window (longitudinal repeatability, not “one run per app”).

### Manuscript work

- `P` definition (historical technical validity, not later `paper_eligible`);
- temporal-repeatability wording in limitations / abstract / conclusion.

---

## Reviewer 2 — Accept

### Strengths

- exact build/hash preservation via the recent-evidence cutoff;
- QFG distinction (do not merge into strict idle).

### Issues

- limited generalization (15 apps; one Motorola Moto G 5G; one environment/network);
- metadata cannot prove leakage/exploitation; static findings are exposure counts.

### Requested analyses

- Snapchat sensitivity (Spearman with and without Snapchat);
- tracker blocklist match on existing interactive destinations.

### Manuscript work

- no-Snapchat Spearman on the submitted 15-app / 123-run cohort;
- tracker-associated hostname analysis (Disconnect, pinned);
- concise limitation reinforcement;
- keep QFG and build/hash control.

---

## Status checklist

- [x] P verified against historical code (`843e485`)
- [x] Unguarded metric verified as High/Medium finding-row count (955), not unique components
- [x] Operationalize **risk posture** (Abstract once; Intro one sentence; Methodology one paragraph; RQ3/Table IV; Conclusion)
- [x] P added to Methodology (historical thresholds; not `paper_eligible`)
- [x] Build-ranking wording fixed (`ordered` rather than `canonical deterministic`); ranking kept **separate from P**
- [x] 14-day wording corrected (operational provenance window; not preregistered; not longitudinal proof)
- [x] Repeatability limitation added (within-window vs independent periods)
- [x] QFG preserved
- [x] no-Snapchat Spearman added
- [ ] Disconnect list pinned
- [ ] tracker analysis reproduced (show table to author before `.tex`)
- [ ] tracker interpretation boundary added (association ≠ leakage)
- [x] 3.39 formula label corrected (`log2((pps_int+1)/(pps_base+1))`; baseline = strict-idle else QFG)
- [x] Hostname metric terminology: retained DNS/SNI hostname breadth (`Hosts B/I`)
- [x] Unguarded-export **findings** label in Results
- [x] Two limitation sentences strengthened (one-device/network; no payload/leak proof)
- [x] Existing Discussion compressed to pay for additions (no new subsection)
- [ ] Final PDF <= 8 pages
- [ ] Professor review copy generated

---

## Decisions already taken

1. Primary manuscript dataset remains **123 runs**. The 120-run `paper_eligible=true` cohort is internal-only unless the authors later change this.
2. Keep Table V value **3.39**; correct the formula description, do not replace with 3.90. Baseline is strict-idle if present, else QFG (TikTok only).
3. Keep Table III integer host medians and SI `MB = 10^6 bytes`.
4. Do not regenerate frozen July evidence.
5. Do not push to `main` or overwrite Overleaf until the author approves the diff.
6. **Keep the accepted title.** Define *risk* operationally as **risk posture**, not P(attack)×impact, exploitability, or realized harm.
7. **No composite risk score.** Static = potential exposure indicators; runtime = observed behavioral indicators; Disconnect match = privacy-relevant infrastructure context. Jointly: risk-relevant evidence.
8. Table IV median-split cells are **cohort-relative**, not absolute risk tiers. Divergence is risk-relevant; it is not a failed correlation and not a ranking of true harm.
9. Do not add Snapchat alias-decomposition or the dangerous-permission vs PPS-shift association as results. Those inform interpretation discipline only (finding volume ≠ severity-weighted realized risk; category confounding).
10. Qualification **(P)** is run-level technical validity. Build grouping, ordered ranking, and static/dynamic same-build alignment are a **separate** selection policy.
11. Tracker matching uses existing retained interactive DNS/SNI hostnames only. Show numbers to the author before they enter the manuscript.

---

## Locked operational definition (use this wording, then stop)

**Risk (this study):** evidence-supported conditions that may enlarge the opportunity for privacy or security harm. Not a calibrated probability of exploitation, not confirmed harm, not a composite score.

**Static layer:** potential exposure (permissions, unguarded-export findings, packaged configuration).

**Runtime layer:** observed behavior under controlled execution (intensity, retained hostname breadth, interaction-induced shift).

**Tracker layer (after Disconnect run):** communication with infrastructure independently classified as tracking-related. Association only.

Do not rename every occurrence of “risk.” Use **risk posture** once in the Abstract, define it in Introduction + Methodology, then prefer *exposure*, *behavior*, and *tracker-associated hostnames* in Results.
