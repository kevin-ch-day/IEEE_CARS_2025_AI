# Camera-ready checkpoint (math + Disconnect + wording prune)

Generated from frozen alignment CSVs. Constructed scores remain internal-only. No `.tex` tracker numbers inserted.

Disconnect pin: `22c7d6166b6e30f7629ee1b49386855bb9b64a50`  
`services.json` SHA-256: `41b9a4949949fddd44a45c7e006264c30b44d6544dfb28dc313dd4673505005f`  
4468 unique normalized domains. CC BY-NC-SA 4.0.

Local compile: **`build/main.pdf` is 9 pages** (was 8). Prune before adding tracker prose.

---

## 1. Advanced-math claims: reproduced or corrected

| Prior narrative | Reproduced? | Correction |
|---|---|---|
| Spearman n=15 ρ≈0.01169 p≈0.967 | **Yes** ρ=0.0116908177 p=0.9670159355 | — |
| Spearman n=14 ρ≈0.04102 p≈0.889 | **Yes** ρ=0.0410208632 p=0.8892660404 | — |
| LOO most influential = BBC News | **Yes** Δρ=+0.187 | Snapchat rank 6, Δρ=+0.029 |
| Jackknife SE(ρ)≈4.5, CI outside [-1,1] | **Withdrawn** | Coding error in influence scaling. Correct jackknife SE=0.321, normal CI [-0.618, 0.641] (inside [-1,1] but still exploratory) |
| dCor hm vs hosts ≈0.31 p≈0.91 | **Yes** (10k perm, p=(c+1)/(B+1)) | — |
| dCor hosts vs log2 PPS ≈0.79 p≈0.002 | **Yes** 0.787 p=0.002; BH-q=0.006 among 6 pairs | Exploratory only |
| dCor dang vs log2 PPS ≈0.75 | **Yes** 0.752 p=0.0015; BH-q=0.006 | Category-confounded; not a paper claim |
| W1 idle→QFG ≈25 PPS | **Yes run-pooled 24.79** | App-balanced on app medians: **14.88** |
| W1 idle→int ≈95 PPS | **Yes run-pooled 95.20** | App-balanced: **84.34** |
| W1 QFG→int ≈70 PPS | **Yes run-pooled 70.40** | App-balanced: **69.46** |
| Hull (z hm, z hosts) area 6.95, Snapchat vertex | **Yes** 6.951; vertices Telegram, Snapchat, Facebook, BBC, Pinterest, Signal | z-score mean/sd ddof=1, frozen for LOO |
| Copula 0.20×4 | **Incomplete** | Fifth cell on-median-rank = 0.20; sum=1.00 |
| F(w) 32 crossings / 33 regions | **Yes on residual vs log2 PPS minmax** | StaticB vs RuntimeB (PPS+MB) is 19 / 20 — encoding-dependent |
| Median 3.39 = TikTok 8th of 15 | **Yes** z=3.385245 → 3.39; only TikTok has QFG baseline | Infinitesimal median derivative is piecewise; nondifferentiable at order crossings |

## 2. Copula-mass discrepancy

Rank copula with average ties and median-of-ranks threshold:

- UU=UL=LU=LL=0.20
- **on_median_rank=0.20**
- sum=1.00

The earlier 0.20×4 omitted points sitting on a median rank. Table IV is a **different** partition (raw ≥ median → higher group): HH=4, HL=4, LH=4, LL=3.

## 3. Spearman influence

Leave-one-out |Δρ| rank: BBC News, Facebook, Instagram, CNN, Guardian, … Snapchat is not top-3.

## 4. Bootstrap interval (app-level, 10 000, seed 20260709)

- Percentile 95%: **[-0.578, 0.584]**
- BCa 95%: **[-0.578, 0.584]**
- Exploratory at n=15. Does not support independence; supports “near-zero point estimate is not a Snapchat artifact.”

## 5. Wasserstein

Run-pooled weights apps with more captures. App-balanced uses one median per app per class, equal app weight.

Idle→interactive hostname W1 remains ~3 names (volume moves; names barely do). Per-app idle→int PPS W1: Instagram/WhatsApp/Facebook large; Snapchat modest; Guardian smallest. Tiny per-app n.

Byte-rate (bytes/s) used, not raw MB.

## 6. Convex hull

Primary scaler: full-cohort z-score (mean, sd ddof=1), **frozen** in LOO. Vertices are axis-dependent extremes, not “riskiest apps.” After residual/PPS axes, Snapchat leaves the hull.

## 7. Pareto (maximize both; not “riskiest”)

- max hm & hosts: Facebook, Snapchat
- max residual & log2 PPS: Facebook, WhatsApp
- max hm & tracker fraction (raw Disconnect tracking-oriented): Snapchat — **inflated by first-party Social listing**

## 8. Rank crossings

Verified **32 crossings / 33 orderings** for minmax(residual) vs minmax(log2 PPS). Do not quote 32/33 for other encodings.

## 9. Detector concentration

`ipc_components` dominates. Snapchat 290/325 high+med are the cohort-wide alias title. Residual ranking: Facebook 132, Instagram 104, Snapchat 35. Unique Android components are **not recoverable** from finding rows (component CSV is provider-scoped, n=171).

## 10. Disconnect pin

See header. Match: `host==d` or `host.endswith("."+d)`; no substring; no bare-TLD suffix.

## 11. Tracker results (56 interactive runs; 53 with retained names; 3 zero-retained = Telegram)

Tracking-oriented categories (Advertising, Analytics, Social, Fingerprinting*, Cryptomining, Email*, ConsentManagers).

**Raw Disconnect (includes first-party Social/Advertising listings such as `*.snapchat.com`):** Snapchat median proportion 0.77; Meta similarly high; BBC 0.51; Signal/WhatsApp/Telegram 0.

**After excluding the app’s own eTLD+1 properties (sensitivity, recommended for any manuscript sentence):**

| App | distinct retained | tracking-oriented | of which third-party |
|---|---|---|---|
| BBC News | 30 | 15 | **15** |
| The Guardian | 30 | 13 | **13** |
| CNN | 28 | 11 | **11** |
| Pinterest | 11 | 1 | 1 |
| TikTok | 20 | 4 | 1 |
| X | 17 | 9 | 1 |
| Snapchat, Facebook, Messenger, Instagram, LinkedIn, Reddit, Signal, Telegram, WhatsApp | — | — | **0** |

News apps carry the third-party tracker-associated hostname mass. Snapchat’s raw high fraction is almost entirely Disconnect listing `snapchat.com` as Advertising/Social.

**Association ≠ leakage.**

## 12–13. Posture matrix and confidence

`outputs/risk_posture_matrix.csv`, `outputs/evidence_confidence.csv`. Instagram/Reddit: `n_interactive=1` → low-confidence flag, not a score change. Telegram: zero retained names with traffic.

## 14. Claims to withdraw

1. Jackknife SE≈4.5 / CI outside [-1,1] (implementation error).
2. Copula 0.20×4 as a complete partition.
3. Any Final/Static/Runtime Risk Score as a cybersecurity measurement.
4. Raw Disconnect proportion as Snapchat “tracker load” without first-party exclusion.
5. “32 crossings” except on the residual vs log2 PPS minmax plane.

## 15. Eight-page recommendation

**A (preferred), after pruning back to 8 pages:** keep risk-posture definition, separate dimensions, Table IV, Snapchat-out Spearman in Table VI + one Results sentence, QFG, 3.39 formula, hosts/unguarded labels. **Do not add constructed scores.**

Tracker: **at most one sentence**, using **third-party** Disconnect matches, after page recovery. Do not add a table unless a page is freed.

Current local PDF: **9 pages**. Next edit pass should cut Methodology/Results, not add analysis.

## 16. Candidate risk language

See `reports/manuscript_risk_language.md`. A pruned form is already in the working `.tex`; do not add more prose until page count is 8.
