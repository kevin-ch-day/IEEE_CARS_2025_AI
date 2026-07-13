# Paper 2 Original Asset Alignment

This file maps the uploaded Paper 2 PDF tables and figures to the evidence currently available in this checkout.

Statuses:

- `original_available`: the original RDI/static input artifact is present.
- `current_data_bridge`: current ScytaleDroid data can support a related, clearly caveated method bridge.
- `manuscript_only`: the item is literature or diagram material, not a generated evidence artifact.
- `missing`: neither an original source nor a safe current-data bridge was found.

Status counts: `{"manuscript_only": 1, "current_data_bridge": 10}`

| Asset | Paper 2 label | Status | Current source | Caveat |
| --- | --- | --- | --- | --- |
| Table I | Comparison of dynamic and time-series analysis approaches | manuscript_only | Manuscript-maintained text/table | Not generated from ScytaleDroid evidence. |
| Figure 1 | Framework overview | current_data_bridge | fig1_study_pipeline.{png,pdf,svg} | It is a current-method figure, not the original Paper 2 figure. |
| Table II | Per-app Runtime Deviation Index for idle and interactive execution | current_data_bridge | baseline_relative_traffic_shape.csv | Bridge rows are baseline-vs-interactive feature shifts, not the original RDI values. |
| Table III | Phase-level distribution and dispersion diagnostics from per-app mean RDI | current_data_bridge | paper2_baseline_interactive_metric_summary.csv | Do not report Paper 2 RDI mean, SD, CV, Shapiro, or variance-ratio values unless original-compatible RDI rows are regenerated. |
| Table IV | Paired effect size for interaction-induced deviation shifts | current_data_bridge | paper2_baseline_interactive_metric_summary.csv | Cohen's dz requires paired per-app RDI deltas. |
| Table V | Descriptive statistics of per-app deviation shifts | current_data_bridge | paper2_baseline_interactive_metric_summary.csv | Do not copy the original n, mean, median, IQR, Wilcoxon, or n+/n- RDI values without the original-compatible RDI table. |
| Table VI | Consistency between scripted and manual interaction modes | current_data_bridge | baseline_relative_traffic_shape.csv | The current bridge table does not reproduce Spearman rho, mean absolute delta, RMSE, or modality-specific RDI. |
| Table VII | Static exposure score components used for contextual reporting | current_data_bridge | table2_static_findings.csv | Current publication assets intentionally avoid a composite static score unless a reviewed formula is selected. |
| Figure 2 | Per-app deviation shifts | current_data_bridge | paper2_baseline_interactive_metric_summary.csv | Delta-D bar/point plotting requires per-app RDI deltas. |
| Figure 3 | Static posture versus interactive RDI for social media apps | current_data_bridge | fig4_static_runtime_scatter.png | The current scatter is not static score versus interactive RDI. |
| Figure 4 | Static posture versus interactive RDI for messaging apps | current_data_bridge | fig4_static_runtime_scatter.png | The current scatter is not category-filtered static score versus interactive RDI. |

## Bottom Line

The current checkout can produce a Paper 2-style dynamic behavior bridge, but it should not claim regenerated original RDI tables unless the frozen Phase E RDI prevalence and static-deviation tables are restored or regenerated.
