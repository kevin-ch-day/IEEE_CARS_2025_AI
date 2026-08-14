# Internal constructed-score stress test

These indices are **not** manuscript results, probabilities of harm, or validated risk scores.

## Formulas (primary min-max variants)
- Static A = mean(minmax(hm, ung, dang)) — alias-inflated.
- Static B = mean(minmax(residual, high, dang)) — cohort-wide alias-title drop.
- Runtime A = mean(minmax(log2 PPS, hosts, MB)) — mixes opposite geometries.
- Runtime B = mean(minmax(log2 PPS, MB)) — intensity only.
- Final AA = 0.5 StaticA + 0.5 RuntimeA; Final BB = 0.5 StaticB + 0.5 RuntimeB.

## Rank crossings of F(w)=w StaticB + (1-w) RuntimeB (minmax)
- crossings in (0,1): **19**
- unique ranking regions on 2001-point grid: **20**
- earlier narrative claimed 32 crossings / 33 orderings on residual-static vs log2PPS-only; this file uses StaticB vs RuntimeB (PPS+MB).

Also stored: percentile-rank and MAD-logistic variants in score_variants.csv.
