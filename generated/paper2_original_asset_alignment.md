# Paper 2 Original Asset Alignment

This file maps the uploaded Paper 2 PDF tables and figures to the evidence currently available in this checkout.

Statuses:

- `exact_available`: the original RDI/static input artifact is present.
- `proxy_available`: current ScytaleDroid data can support a related, clearly caveated replacement.
- `manuscript_only`: the item is literature or diagram material, not a generated evidence artifact.
- `missing`: neither an exact source nor a safe proxy was found.

Status counts: `{"manuscript_only": 1, "proxy_available": 10}`

| Asset | Paper 2 label | Status | Current source | Caveat |
| --- | --- | --- | --- | --- |
| Table I | Comparison of dynamic and time-series analysis approaches | manuscript_only | Manuscript-maintained text/table | Not generated from ScytaleDroid evidence. |
| Figure 1 | Framework overview | proxy_available | fig1_study_pipeline.{png,pdf,svg} | It is not the exact original Paper 2 figure. |
| Table II | Per-app Runtime Deviation Index for idle and interactive execution | proxy_available | paper2_app_runtime_deviation_proxy.csv | Proxy rows are baseline-vs-interactive feature shifts, not exact RDI values. |
| Table III | Phase-level distribution and dispersion diagnostics from per-app mean RDI | proxy_available | paper2_baseline_interactive_metric_summary.csv | Do not report Paper 2 RDI mean, SD, CV, Shapiro, or variance-ratio values unless exact RDI rows are regenerated. |
| Table IV | Paired effect size for interaction-induced deviation shifts | proxy_available | paper2_baseline_interactive_metric_summary.csv | Cohen's dz requires exact paired per-app RDI deltas. |
| Table V | Descriptive statistics of per-app deviation shifts | proxy_available | paper2_baseline_interactive_metric_summary.csv | Do not copy the original n, mean, median, IQR, Wilcoxon, or n+/n- RDI values without the exact RDI table. |
| Table VI | Consistency between scripted and manual interaction modes | proxy_available | paper2_app_runtime_deviation_proxy.csv | The current proxy table does not reproduce Spearman rho, mean absolute delta, RMSE, or modality-specific RDI. |
| Table VII | Static exposure score components used for contextual reporting | proxy_available | table2_static_findings.csv | Current publication assets intentionally avoid a composite static score unless a reviewed formula is selected. |
| Figure 2 | Per-app deviation shifts | proxy_available | paper2_baseline_interactive_metric_summary.csv | Exact delta-D bar/point plot requires per-app RDI deltas. |
| Figure 3 | Static posture versus interactive RDI for social media apps | proxy_available | fig4_static_runtime_scatter.png | The current scatter is not static score versus interactive RDI. |
| Figure 4 | Static posture versus interactive RDI for messaging apps | proxy_available | fig4_static_runtime_scatter.png | The current scatter is not category-filtered static score versus interactive RDI. |

## Bottom Line

The current checkout can produce a Paper 2-style dynamic behavior bridge, but it should not claim exact reproduction of the original RDI tables unless the frozen Phase E RDI prevalence and static-deviation tables are restored or regenerated.
