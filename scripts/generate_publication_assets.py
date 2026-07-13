#!/usr/bin/env python3
"""Generate publication tables and figures from ScytaleDroid report outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42})


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(
    "/home/secadmin/Laughlin/GitHub/ScytaleDroid/output/paper/"
    "android_empirical_alignment_final"
)
TABLE_DIR = ROOT / "tables"
FIGURE_DIR = ROOT / "figures"
SOURCE_DIR = ROOT / "generated" / "source_data"


APP_ORDER = [
    "BBC News",
    "CNN",
    "The Guardian",
    "Facebook",
    "Facebook Msg",
    "Instagram",
    "Pinterest",
    "Reddit",
    "TikTok",
    "X",
    "LinkedIn",
    "Signal",
    "Snapchat",
    "Telegram",
    "WhatsApp",
]


def latex_escape(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    protected: dict[str, str] = {}
    for idx, match in enumerate(re.findall(r"\\cite\{[^}]+\}", text)):
        token = f"@@CITE{idx}@@"
        protected[token] = match
        text = text.replace(match, token, 1)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    escaped = "".join(replacements.get(ch, ch) for ch in text)
    for token, cite in protected.items():
        escaped = escaped.replace(token, cite)
    return escaped


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_tex_table(
    path: Path,
    caption: str,
    label: str,
    columns: list[str],
    rows: list[dict[str, object]],
    align: str,
    size: str = r"\scriptsize",
    table_env: str = "table*",
) -> None:
    body = [
        rf"\begin{{{table_env}}}[t]",
        r"\centering",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        size,
        rf"\begin{{tabular}}{{{align}}}",
        r"\toprule",
        " & ".join(latex_escape(col) for col in columns) + r" \\",
        r"\midrule",
    ]
    for row in rows:
        body.append(" & ".join(latex_escape(row.get(col, "")) for col in columns) + r" \\")
    body.extend([r"\bottomrule", r"\end{tabular}", rf"\end{{{table_env}}}", ""])
    path.write_text("\n".join(body), encoding="utf-8")


def fnum(value: object, digits: int = 1) -> str:
    try:
        if value == "" or pd.isna(value):
            return ""
        return f"{float(value):.{digits}f}"
    except Exception:
        return ""


def count_ids(value: object) -> int:
    if pd.isna(value) or not str(value).strip():
        return 0
    return len([part for part in str(value).split(",") if part.strip()])


def category_sort(df: pd.DataFrame, column: str = "app_label") -> pd.DataFrame:
    order = {name: i for i, name in enumerate(APP_ORDER)}
    return df.assign(_order=df[column].map(order).fillna(999)).sort_values("_order").drop(columns=["_order"])


def read_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    manifest = pd.read_csv(SOURCE / "publication_cohort_manifest.csv")
    app = pd.read_csv(SOURCE / "data" / "publication_app_analysis_dataset.csv")
    static = pd.read_csv(SOURCE / "data" / "publication_static_app_metrics.csv")
    dynamic = pd.read_csv(SOURCE / "data" / "publication_dynamic_app_metrics.csv")
    runs = pd.read_csv(SOURCE / "data" / "publication_dynamic_run_metrics.csv")
    return manifest, app, static, dynamic, runs


def build_tables(manifest: pd.DataFrame, app: pd.DataFrame, static: pd.DataFrame, dynamic: pd.DataFrame, runs: pd.DataFrame) -> None:
    TABLE_DIR.mkdir(exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    lit_rows = [
        {
            "Study": r"ManiScope \cite{yang2022maniscope}",
            "Static": "Yes",
            "Runtime": "No",
            "Privacy": "Limited",
            "Provenance": "Manifest/package",
            "Scope": "Large app corpus",
            "Limit": "No runtime alignment",
        },
        {
            "Study": r"Runtime permissions \cite{wang2023runtimepermissions}",
            "Static": "Permissions",
            "Runtime": "Behavioral failures",
            "Privacy": "Indirect",
            "Provenance": "Version/context varies",
            "Scope": "Permission issues",
            "Limit": "Not network-focused",
        },
        {
            "Study": r"Dynamic SLR \cite{sutter2024dynamic}",
            "Static": "Surveyed",
            "Runtime": "Surveyed",
            "Privacy": "Varies",
            "Provenance": "Method-level",
            "Scope": "Literature",
            "Limit": "No empirical app bundle",
        },
        {
            "Study": r"Tracking study \cite{paci2023tracking}",
            "Static": "Some",
            "Runtime": "Yes",
            "Privacy": "Tracking",
            "Provenance": "Execution-based",
            "Scope": "Third-party tracking",
            "Limit": "Less build alignment",
        },
        {
            "Study": r"Data Safety longitudinal \cite{arkalakis2024datasafety}",
            "Static": "Ecosystem",
            "Runtime": "Dynamic",
            "Privacy": "Disclosure",
            "Provenance": "Longitudinal",
            "Scope": "Google Play labels",
            "Limit": "Disclosure-centered",
        },
        {
            "Study": r"Privacy labels \cite{khandelwal2024privacylabels}",
            "Static": "Measurement",
            "Runtime": "No",
            "Privacy": "Disclosure",
            "Provenance": "Developer/app",
            "Scope": "Data Safety",
            "Limit": "No runtime PCAP",
        },
        {
            "Study": r"Privacy SDKs \cite{zhang2024privacysdks}",
            "Static": "SDK config",
            "Runtime": "Limited",
            "Privacy": "SDK risk",
            "Provenance": "SDK/app",
            "Scope": "Mobile SDKs",
            "Limit": "SDK-specific",
        },
        {
            "Study": r"Android SAST \cite{zhu2024sastandroid}",
            "Static": "Yes",
            "Runtime": "No",
            "Privacy": "Security findings",
            "Provenance": "Tool/app",
            "Scope": "SAST tools",
            "Limit": "No runtime layer",
        },
        {
            "Study": "This study",
            "Static": "Yes",
            "Runtime": "Yes",
            "Privacy": "Transport/provenance",
            "Provenance": "Exact selected build",
            "Scope": "15 apps",
            "Limit": "Scenario-bounded",
        },
    ]
    lit_cols = ["Study", "Static", "Runtime", "Privacy", "Provenance", "Scope", "Limit"]
    write_csv(TABLE_DIR / "table1_literature_comparison.csv", lit_rows, lit_cols)
    write_tex_table(
        TABLE_DIR / "table1_literature_comparison.tex",
        "Comparison of related Android privacy and security studies.",
        "tab:literature-comparison",
        lit_cols,
        lit_rows,
        r"@{}p{0.18\textwidth}p{0.075\textwidth}p{0.075\textwidth}p{0.10\textwidth}p{0.125\textwidth}p{0.115\textwidth}p{0.15\textwidth}@{}",
        size=r"\tiny",
    )

    manifest = category_sort(manifest.rename(columns={"app_label": "App"}), column="App")
    table2 = []
    for _, row in manifest.iterrows():
        table2.append(
            {
                "App": row["App"],
                "Category": row["app_category"],
                "Version": row["selected_version_name"],
                "Static run": row["contributing_static_run_id"],
                "Runs": int(row["selected_run_count"]),
                "I/Q/Int": f"{count_ids(row['strict_idle_run_ids'])}/{count_ids(row['qfg_run_ids'])}/{count_ids(row['interactive_run_ids'])}",
                "Aligned": row["static_dynamic_same_build"],
            }
        )
    cols2 = ["App", "Category", "Version", "Static run", "Runs", "I/Q/Int", "Aligned"]
    write_csv(TABLE_DIR / "table2_cutoff_evidence_summary.csv", table2, cols2)
    write_tex_table(
        TABLE_DIR / "table2_cutoff_evidence_summary.tex",
        "Selected 14-day evidence bundles and provenance.",
        "tab:cutoff-evidence-summary",
        cols2,
        table2,
        r"lllrccc",
    )

    static = category_sort(static)
    table3 = []
    for _, row in static.iterrows():
        hm = int(row["severity_high_count"]) + int(row["severity_medium_count"])
        table3.append(
            {
                "App": row["app_label"],
                "Danger": int(row["dangerous_permissions"]),
                "High+Med": hm,
                "Unguarded": int(row["exported_components_without_permission_guard"]),
                "Privacy": int(row["privacy_findings"]),
                "Platform": int(row["platform_findings"]),
                "Network": int(row["network_security_findings"]),
                "Storage": int(row["storage_findings"]),
            }
        )
    cols3 = ["App", "Danger", "High+Med", "Unguarded", "Privacy", "Platform", "Network", "Storage"]
    write_csv(TABLE_DIR / "table3_static_exposure_summary.csv", table3, cols3)
    write_tex_table(
        TABLE_DIR / "table3_static_exposure_summary.tex",
        "Static exposure summary for selected app builds.",
        "tab:static-exposure-summary",
        cols3,
        table3,
        r"lrrrrrrr",
        size=r"\tiny",
    )

    dynamic = dynamic.rename(columns={"app": "app_label"})
    dynamic = category_sort(dynamic)
    table4 = []
    for _, row in dynamic.iterrows():
        table4.append(
            {
                "App": row["app_label"],
                "Runs": int(row["selected_run_count"]),
                "I/Q/Int": f"{int(row['strict_idle_run_count'])}/{int(row['qfg_run_count'])}/{int(row['interactive_run_count'])}",
                "Idle domains": fnum(row["strict_idle_median_domain_count"], 0),
                "Int domains": fnum(row["interactive_median_domain_count"], 0),
                "Idle pps": fnum(row["strict_idle_median_packets_per_second"], 1),
                "Int pps": fnum(row["interactive_median_packets_per_second"], 1),
                "Int MB": fnum(float(row["interactive_median_bytes"]) / 1_000_000 if not pd.isna(row["interactive_median_bytes"]) else np.nan, 1),
            }
        )
    cols4 = ["App", "Runs", "I/Q/Int", "Idle domains", "Int domains", "Idle pps", "Int pps", "Int MB"]
    write_csv(TABLE_DIR / "table4_runtime_behavior_summary.csv", table4, cols4)
    write_tex_table(
        TABLE_DIR / "table4_runtime_behavior_summary.tex",
        "Runtime coverage and median behavior indicators.",
        "tab:runtime-behavior-summary",
        cols4,
        table4,
        r"lrrcrrrr",
        size=r"\tiny",
    )

    merged = static.merge(dynamic, left_on="package_name", right_on="package", suffixes=("_s", "_d"))
    if "app_label_s" in merged.columns:
        merged["app_label"] = merged["app_label_s"]
    hm_vals = merged["severity_high_count"] + merged["severity_medium_count"]
    domain_vals = merged["interactive_median_domain_count"].fillna(0)
    merged["high_med"] = hm_vals
    merged["int_domains"] = domain_vals
    hm_med = float(hm_vals.median())
    dom_med = float(domain_vals.median())
    table5 = []
    for _, row in merged.pipe(category_sort).iterrows():
        s = "High static" if row["high_med"] >= hm_med else "Lower static"
        r = "high runtime" if row["int_domains"] >= dom_med else "lower runtime"
        table5.append(
            {
                "App": row["app_label"],
                "Group": f"{s}/{r}",
                "High+Med": int(row["high_med"]),
                "Int domains": fnum(row["int_domains"], 0),
                "Int runs": int(row["interactive_run_count"]),
                "Interpretation": "Review divergence" if (s.startswith("High") and r.startswith("lower")) or (s.startswith("Lower") and r.startswith("high")) else "Concordant",
            }
        )
    cols5 = ["App", "Group", "High+Med", "Int domains", "Int runs", "Interpretation"]
    write_csv(TABLE_DIR / "table5_integrated_static_runtime_profiles.csv", table5, cols5)
    write_tex_table(
        TABLE_DIR / "table5_integrated_static_runtime_profiles.tex",
        "Integrated static-runtime app profiles using median-split indicators.",
        "tab:integrated-static-runtime-profiles",
        cols5,
        table5,
        r"llrrrl",
        size=r"\tiny",
    )

    eligible = runs[runs["analytic_eligibility"].eq("eligible")].copy()
    base = eligible[eligible["evidence_class"].isin(["strict_idle", "qfg"])]
    inter = eligible[eligible["evidence_class"].eq("interactive")]
    compared = sorted(set(base["package"]) & set(inter["package"]))
    excluded = sorted(set(eligible["package"]) - set(compared))
    rho = merged[["high_med", "int_domains"]].corr(method="spearman").iloc[0, 1]
    shift = []
    for _, row in merged.iterrows():
        b = row["strict_idle_median_packets_per_second"]
        if pd.isna(b) or b == 0:
            b = row["qfg_median_packets_per_second"]
        i = row["interactive_median_packets_per_second"]
        if not pd.isna(b) and not pd.isna(i) and b > 0:
            shift.append(math.log2((i + 1) / (b + 1)))
    table6 = [
        {"Metric": "Apps with selected evidence", "Value": str(len(manifest)), "Note": "14-day window"},
        {"Metric": "Selected dynamic runs", "Value": str(int(dynamic["selected_run_count"].sum())), "Note": "PCAP-backed selected runs"},
        {"Metric": "Strict idle/QFG/interactive", "Value": f"{int(dynamic['strict_idle_run_count'].sum())}/{int(dynamic['qfg_run_count'].sum())}/{int(dynamic['interactive_run_count'].sum())}", "Note": "Classes reported separately"},
        {"Metric": "Baseline-relative eligible apps", "Value": str(len(compared)), "Note": f"Excluded: {len(excluded)} app(s)"},
        {"Metric": "Median log2 interactive/base pps shift", "Value": f"{np.median(shift):.2f}", "Note": "Strict idle else QFG baseline"},
        {"Metric": "Spearman high+med vs interactive domains", "Value": f"{rho:.2f}", "Note": "Descriptive app-level association"},
    ]
    cols6 = ["Metric", "Value", "Note"]
    write_csv(TABLE_DIR / "table6_statistical_summary.csv", table6, cols6)
    write_tex_table(
        TABLE_DIR / "table6_statistical_summary.tex",
        "Compact descriptive statistical summary.",
        "tab:statistical-summary",
        cols6,
        table6,
        r"@{}p{0.35\columnwidth}p{0.18\columnwidth}p{0.34\columnwidth}@{}",
        table_env="table",
        size=r"\scriptsize",
    )

    # A small eligibility CSV resolves the older 9-app/8-row discrepancy.
    eligibility = []
    for pkg, g in runs.groupby("package"):
        app_name = g["app"].iloc[0]
        base_count = int(g["evidence_class"].isin(["strict_idle", "qfg"]).sum())
        int_count = int(g["evidence_class"].eq("interactive").sum())
        eligibility.append(
            {
                "app": app_name,
                "package": pkg,
                "baseline_or_qfg_runs": base_count,
                "interactive_runs": int_count,
                "baseline_relative_eligible": "yes" if base_count and int_count else "no",
                "exclusion_reason": "" if base_count and int_count else "missing baseline/QFG or interactive evidence class",
            }
        )
    write_csv(
        SOURCE_DIR / "baseline_relative_eligibility.csv",
        sorted(eligibility, key=lambda r: APP_ORDER.index(r["app"]) if r["app"] in APP_ORDER else 999),
        ["app", "package", "baseline_or_qfg_runs", "interactive_runs", "baseline_relative_eligible", "exclusion_reason"],
    )

    for name, df in {
        "static_metrics_source.csv": static,
        "dynamic_metrics_source.csv": dynamic,
        "manifest_source.csv": manifest,
    }.items():
        df.to_csv(SOURCE_DIR / name, index=False)


def build_pipeline_figure() -> None:
    stages = [
        ("15-app\ndataset", 0.06, 0.72),
        ("APK harvest\n+ split identity", 0.22, 0.72),
        ("Static\nanalysis", 0.38, 0.82),
        ("Dynamic\nidle/QFG/int", 0.38, 0.60),
        ("Evidence\nQA gate", 0.55, 0.72),
        ("14-day build\nselection", 0.71, 0.72),
        ("Static-runtime\nalignment", 0.71, 0.48),
        ("Integrated\nmeasures", 0.86, 0.60),
        ("Tables, figures,\nchecksums", 0.86, 0.34),
    ]
    exclusions = "Exclude or defer:\nbuild mismatch\nmissing static/dynamic\ninvalid run"
    fig, ax = plt.subplots(figsize=(8.2, 3.1))
    ax.axis("off")
    for text, x, y in stages:
        ax.text(x, y, text, ha="center", va="center", fontsize=8.5,
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#eaf2f8", edgecolor="#2c5f8a", linewidth=1))
    arrows = [(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8)]
    for a, b in arrows:
        x1, y1 = stages[a][1], stages[a][2]
        x2, y2 = stages[b][1], stages[b][2]
        ax.annotate("", xy=(x2 - 0.06 if x2 > x1 else x2, y2), xytext=(x1 + 0.06 if x2 > x1 else x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#333333", lw=1))
    ax.text(0.55, 0.25, exclusions, ha="center", va="center", fontsize=8,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#fff1e6", edgecolor="#a85d15", linewidth=1))
    ax.annotate("", xy=(0.55, 0.34), xytext=(0.55, 0.62),
                arrowprops=dict(arrowstyle="->", color="#a85d15", lw=1, linestyle="--"))
    fig.tight_layout(pad=0.2)
    fig.savefig(FIGURE_DIR / "fig1_study_pipeline.pdf")
    fig.savefig(FIGURE_DIR / "fig1_study_pipeline.png", dpi=240)
    plt.close(fig)
    pipeline = {
        "nodes": [s[0].replace("\n", " ") for s in stages],
        "exclusion_branch": exclusions.replace("\n", "; "),
        "source": "scripts/generate_publication_assets.py",
    }
    (SOURCE_DIR / "fig1_study_pipeline.json").write_text(json.dumps(pipeline, indent=2), encoding="utf-8")


def build_figures(static: pd.DataFrame, dynamic: pd.DataFrame) -> None:
    FIGURE_DIR.mkdir(exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    build_pipeline_figure()

    static = category_sort(static)
    static["high_medium_findings"] = static["severity_high_count"] + static["severity_medium_count"]
    heat_cols = [
        ("dangerous_permissions", "Danger\\nperm."),
        ("high_medium_findings", "High/med\\nfindings"),
        ("exported_components_without_permission_guard", "Unguarded\\ncomponents"),
        ("privacy_findings", "Privacy"),
        ("platform_findings", "Platform"),
        ("network_security_findings", "Network"),
        ("storage_findings", "Storage"),
    ]
    heat = static[[c for c, _ in heat_cols]].astype(float)
    norm = (heat - heat.min()) / (heat.max() - heat.min()).replace(0, np.nan)
    norm = norm.fillna(0)
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    im = ax.imshow(norm.values, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(heat_cols)), [label for _, label in heat_cols], fontsize=8)
    ax.set_yticks(range(len(static)), static["app_label"], fontsize=8)
    for i in range(len(static)):
        for j, (col, _) in enumerate(heat_cols):
            ax.text(j, i, str(int(heat.iloc[i, j])), ha="center", va="center", fontsize=6.5,
                    color="white" if norm.iloc[i, j] > 0.55 else "black")
    ax.set_title("Static Exposure Indicators")
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02, label="min-max normalized")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "fig2_static_exposure_heatmap.pdf")
    fig.savefig(FIGURE_DIR / "fig2_static_exposure_heatmap.png", dpi=240)
    heat_out = static[["app_label"] + [c for c, _ in heat_cols]].copy()
    heat_out.to_csv(SOURCE_DIR / "fig2_static_exposure_heatmap_source.csv", index=False)
    plt.close(fig)

    dynamic = dynamic.rename(columns={"app": "app_label"})
    dynamic = category_sort(dynamic)
    dyn_counts = dynamic[["app_label", "strict_idle_run_count", "qfg_run_count", "interactive_run_count"]].copy()
    dyn_counts.to_csv(SOURCE_DIR / "fig3_runtime_coverage_source.csv", index=False)
    y = np.arange(len(dynamic))
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    left = np.zeros(len(dynamic))
    colors = ["#4c78a8", "#f58518", "#54a24b"]
    labels = ["Strict idle", "QFG", "Interactive"]
    cols = ["strict_idle_run_count", "qfg_run_count", "interactive_run_count"]
    for col, label, color in zip(cols, labels, colors):
        vals = dynamic[col].fillna(0).astype(int).values
        ax.barh(y, vals, left=left, label=label, color=color)
        for yi, val, li in zip(y, vals, left):
            if val >= 2:
                ax.text(li + val / 2, yi, str(val), ha="center", va="center", fontsize=7, color="white")
        left += vals
    ax.set_yticks(y, dynamic["app_label"], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("selected runs")
    ax.set_title("Runtime Evidence Coverage")
    ax.legend(loc="lower right", ncols=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "fig3_runtime_coverage_by_app.pdf")
    fig.savefig(FIGURE_DIR / "fig3_runtime_coverage_by_app.png", dpi=240)
    plt.close(fig)

    merged = static.merge(dynamic, left_on="package_name", right_on="package", suffixes=("_s", "_d"))
    if "app_label_s" in merged.columns:
        merged["app_label"] = merged["app_label_s"]
    merged["high_medium_findings"] = merged["severity_high_count"] + merged["severity_medium_count"]
    baseline = merged["strict_idle_median_packets_per_second"].where(
        merged["strict_idle_median_packets_per_second"].fillna(0) > 0,
        merged["qfg_median_packets_per_second"],
    )
    merged["runtime_shift_log2_pps"] = np.log2((merged["interactive_median_packets_per_second"].fillna(0) + 1) / (baseline.fillna(0) + 1))
    merged["x_log_high_med"] = np.log1p(merged["high_medium_findings"])
    merged[["app_label", "package_name", "high_medium_findings", "runtime_shift_log2_pps", "interactive_run_count", "app_category" if "app_category" in merged.columns else "package_name"]].to_csv(
        SOURCE_DIR / "fig4_static_runtime_scatter_source.csv", index=False
    )
    fig, ax = plt.subplots(figsize=(6.9, 4.2))
    cats = pd.read_csv(SOURCE / "publication_cohort_manifest.csv")[["app_label", "app_category"]]
    plot = merged.merge(cats, on="app_label", how="left")
    category_colors = {cat: c for cat, c in zip(sorted(plot["app_category"].dropna().unique()), plt.cm.Set2.colors)}
    for cat, group in plot.groupby("app_category"):
        ax.scatter(
            group["x_log_high_med"],
            group["runtime_shift_log2_pps"],
            s=35 + group["interactive_run_count"].fillna(0) * 14,
            label=cat,
            alpha=0.82,
            color=category_colors.get(cat),
            edgecolor="black",
            linewidth=0.4,
        )
    labels = {"Snapchat", "Facebook", "CNN", "Signal", "Telegram", "TikTok"}
    for _, row in plot.iterrows():
        if row["app_label"] in labels:
            ax.annotate(row["app_label"], (row["x_log_high_med"], row["runtime_shift_log2_pps"]),
                        xytext=(4, 4), textcoords="offset points", fontsize=7)
    ax.axhline(0, color="#777777", lw=0.8, linestyle="--")
    ax.set_xlabel("log(1 + high/medium static findings)")
    ax.set_ylabel("log2 interactive/base packet-rate shift")
    ax.set_title("Static Exposure and Runtime Shift")
    ax.legend(fontsize=6.5, loc="best")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "fig4_static_runtime_scatter.pdf")
    fig.savefig(FIGURE_DIR / "fig4_static_runtime_scatter.png", dpi=240)
    plt.close(fig)


def write_manifest() -> None:
    files = []
    checksum_path = SOURCE_DIR / "asset_checksums.json"
    for path in sorted(list(TABLE_DIR.glob("table*.*")) + list(FIGURE_DIR.glob("fig*.*")) + list(SOURCE_DIR.glob("*"))):
        if path.is_file():
            if path == checksum_path:
                continue
            files.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "bytes": path.stat().st_size,
                }
            )
    checksum_path.write_text(json.dumps({"source_root": str(SOURCE), "files": files}, indent=2), encoding="utf-8")


def main() -> None:
    manifest, app, static, dynamic, runs = read_inputs()
    build_tables(manifest, app, static, dynamic, runs)
    build_figures(static, dynamic)
    write_manifest()
    print(f"Wrote tables to {TABLE_DIR}")
    print(f"Wrote figures to {FIGURE_DIR}")
    print(f"Wrote source data to {SOURCE_DIR}")


if __name__ == "__main__":
    main()
