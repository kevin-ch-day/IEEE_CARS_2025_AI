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
    "Instagram",
    "Pinterest",
    "Reddit",
    "Snapchat",
    "TikTok",
    "X",
    "X (Twitter)",
    "Facebook Messenger",
    "Signal",
    "Telegram",
    "WhatsApp",
    "LinkedIn",
]

CATEGORY_POLICY_VERSION = "integrated-primary-function-v1"
CATEGORY_POLICY = {
    "bbc.mobile.news.ww": ("News", "News publication and consumption", "Primary purpose is news publication and consumption."),
    "com.cnn.mobile.android.phone": ("News", "News publication and consumption", "Primary purpose is news publication and consumption."),
    "com.guardian": ("News", "News publication and consumption", "Primary purpose is news publication and consumption."),
    "com.facebook.katana": ("Social Media", "Social feed and content interaction", "Supports social feeds, publishing, and broad social interaction."),
    "com.instagram.android": ("Social Media", "Social feed and content sharing", "Supports social feeds, creator content, and content sharing."),
    "com.pinterest": ("Social Media", "Content discovery and social recommendation", "Supports content discovery, recommendations, and social interaction."),
    "com.reddit.frontpage": ("Social Media", "Community content and discussion", "Supports public and semi-public community discussion and content feeds."),
    "com.snapchat.android": ("Social Media", "Social media and ephemeral content", "Classified by primary user-facing function rather than ownership; despite messaging features, it is treated as a social media/content app for this study."),
    "com.zhiliaoapp.musically": ("Social Media", "Short-form social video/content", "Supports creator content, social video, and feed-based interaction."),
    "com.twitter.android": ("Social Media", "Social feed and public interaction", "Supports social feeds, publishing, and public or semi-public interaction."),
    "com.facebook.orca": ("Messaging", "Direct and group private communication", "Primary purpose is direct or group private message exchange."),
    "org.thoughtcrime.securesms": ("Messaging", "Direct and group private communication", "Primary purpose is direct or group private message exchange and calls."),
    "org.telegram.messenger": ("Messaging", "Direct and group private communication", "Primary purpose is direct or group private message exchange and calls."),
    "com.whatsapp": ("Messaging", "Direct and group private communication", "Primary purpose is direct or group private message exchange and calls."),
    "com.linkedin.android": ("Professional Networking", "Professional identity and networking", "Primary purpose is professional identity, employment, and professional network formation."),
}

CATEGORY_ORDER = ["News", "Social Media", "Messaging", "Professional Networking"]
CATEGORY_STYLES = {
    "News": {"color": "#0072B2", "marker": "^"},
    "Social Media": {"color": "#D55E00", "marker": "o"},
    "Messaging": {"color": "#009E73", "marker": "s"},
    "Professional Networking": {"color": "#CC79A7", "marker": "D"},
}


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
    note: str = "",
) -> None:
    body = [
        rf"\begin{{{table_env}}}[!t]",
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
    body.extend([r"\bottomrule", r"\end{tabular}"])
    if note:
        body.extend([r"\vspace{1pt}", rf"\begin{{flushleft}}\scriptsize {note}\end{{flushleft}}"])
    body.extend([rf"\end{{{table_env}}}", ""])
    path.write_text("\n".join(body), encoding="utf-8")


def write_literature_table(path: Path, rows: list[dict[str, object]]) -> None:
    columns = ["Study", "Static", "Runtime", "Privacy", "Provenance", "Scope", "Limit"]
    body = [
        r"\begin{table*}[!t]",
        r"\centering",
        r"\caption{Comparison of related Android privacy and security studies.}",
        r"\label{tab:literature-comparison}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3.2pt}",
        r"\renewcommand{\arraystretch}{1.08}",
        r"\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}p{0.15\textwidth}cccc>{\raggedright\arraybackslash}p{0.13\textwidth}>{\raggedright\arraybackslash}X@{}}",
        r"\toprule",
        " & ".join(columns) + r" \\",
        r"\midrule",
    ]
    for row in rows:
        body.append(" & ".join(latex_escape(row.get(col, "")) for col in columns) + r" \\")
    body.extend([r"\bottomrule", r"\end{tabularx}", r"\end{table*}", ""])
    path.write_text("\n".join(body), encoding="utf-8")


def write_cutoff_evidence_table(path: Path, rows: list[dict[str, object]]) -> None:
    body = [
        r"\begin{table}[!t]",
        r"\centering",
        r"\caption{Selected 14-day evidence bundles.}",
        r"\label{tab:cutoff-evidence-summary}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{2.4pt}",
        r"\renewcommand{\arraystretch}{1.03}",
        r"\begin{tabularx}{\columnwidth}{@{}>{\raggedright\arraybackslash}p{0.23\columnwidth}>{\raggedright\arraybackslash}p{0.16\columnwidth}>{\raggedright\arraybackslash}X>{\centering\arraybackslash}p{0.13\columnwidth}@{}}",
        r"\toprule",
        r"App & Cat. & Sel. build & I/Q/Int \\",
        r"\midrule",
    ]
    for row in rows:
        body.append(
            " & ".join(
                [
                    latex_escape(row["App"]),
                    latex_escape(row["Category"]),
                    latex_breakable_version(row["Version"]),
                    latex_escape(row["I/Q/Int"]),
                ]
            )
            + r" \\"
        )
    body.extend(
        [
            r"\bottomrule",
            r"\end{tabularx}",
            r"\vspace{1pt}",
            r"\begin{flushleft}\tiny Sel. build is the evidence-window selected build/version, not necessarily the latest installed version; I/Q/Int reports strict-idle/QFG/interactive runs. Full versions, hashes, and run IDs are retained in source CSVs.\end{flushleft}",
            r"\end{table}",
            "",
        ]
    )
    path.write_text("\n".join(body), encoding="utf-8")


def latex_breakable_version(value: object) -> str:
    text = latex_escape(value)
    return text.replace(".", r".\allowbreak{}").replace("-", r"-\allowbreak{}")


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


def display_label(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    if text == "Facebook Messenger":
        return "Facebook Msg"
    if text == "X":
        return "X (Twitter)"
    return text


def publication_category(package: object) -> str:
    pkg = "" if pd.isna(package) else str(package)
    return CATEGORY_POLICY.get(pkg, ("Other", ""))[0]


def manuscript_category_label(category: object) -> str:
    text = "" if pd.isna(category) else str(category)
    if text == "Professional Networking":
        return "Prof. Net."
    if text == "Social Media":
        return "Social"
    return text


def write_category_policy() -> None:
    rows = []
    display_names = {
        "bbc.mobile.news.ww": "BBC News",
        "com.cnn.mobile.android.phone": "CNN",
        "com.guardian": "The Guardian",
        "com.facebook.katana": "Facebook",
        "com.instagram.android": "Instagram",
        "com.pinterest": "Pinterest",
        "com.reddit.frontpage": "Reddit",
        "com.snapchat.android": "Snapchat",
        "com.zhiliaoapp.musically": "TikTok",
        "com.twitter.android": "X (Twitter)",
        "com.facebook.orca": "Facebook Msg",
        "org.thoughtcrime.securesms": "Signal",
        "org.telegram.messenger": "Telegram",
        "com.whatsapp": "WhatsApp",
        "com.linkedin.android": "LinkedIn",
    }
    for package, (category, primary_function, rationale) in CATEGORY_POLICY.items():
        rows.append(
            {
                "app_display_name": display_names[package],
                "package_name": package,
                "category": category,
                "primary_function": primary_function,
                "assignment_rationale": rationale,
                "taxonomy_version": CATEGORY_POLICY_VERSION,
            }
        )
    write_csv(
        SOURCE_DIR / "app_category_policy.csv",
        sorted(rows, key=lambda r: APP_ORDER.index(r["app_display_name"]) if r["app_display_name"] in APP_ORDER else 999),
        ["app_display_name", "package_name", "category", "primary_function", "assignment_rationale", "taxonomy_version"],
    )


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
    write_category_policy()

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
            "Study": r"Karyotakis et al. \cite{karyotakis2026messaging}",
            "Static": "Yes",
            "Runtime": "Yes",
            "Privacy": "Security/privacy",
            "Provenance": "Scenario/build context",
            "Scope": "3 messaging apps",
            "Limit": "Messaging-only",
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
            "Scope": "15 heterogeneous apps",
            "Limit": "Single device; scenario-bounded",
        },
    ]
    lit_cols = ["Study", "Static", "Runtime", "Privacy", "Provenance", "Scope", "Limit"]
    write_csv(TABLE_DIR / "table1_literature_comparison.csv", lit_rows, lit_cols)
    write_literature_table(TABLE_DIR / "table1_literature_comparison.tex", lit_rows)

    manifest = manifest.copy()
    manifest["app_category"] = manifest["package_name"].map(publication_category)
    manifest = category_sort(manifest.rename(columns={"app_label": "App"}), column="App")
    table2_csv = []
    table2_tex = []
    for _, row in manifest.iterrows():
        common = {
            "App": display_label(row["App"]),
            "Version": row["selected_version_name"],
            "I/Q/Int": f"{count_ids(row['strict_idle_run_ids'])}/{count_ids(row['qfg_run_ids'])}/{count_ids(row['interactive_run_ids'])}",
        }
        table2_csv.append(
            {
                **common,
                "Category": row["app_category"],
            }
        )
        table2_tex.append(
            {
                **common,
                "Category": manuscript_category_label(row["app_category"]),
            }
        )
    cols2 = ["App", "Category", "Version", "I/Q/Int"]
    write_csv(TABLE_DIR / "table2_cutoff_evidence_summary.csv", table2_csv, cols2)
    write_cutoff_evidence_table(TABLE_DIR / "table2_cutoff_evidence_summary.tex", table2_tex)

    static = static.copy()
    static["app_category"] = static["package_name"].map(publication_category)
    static = category_sort(static)
    table3 = []
    for _, row in static.iterrows():
        hm = int(row["severity_high_count"]) + int(row["severity_medium_count"])
        table3.append(
            {
                "App": display_label(row["app_label"]),
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
        "Supplemental static exposure summary for selected app builds.",
        "tab:static-exposure-summary",
        cols3,
        table3,
        r"lrrrrrrr",
        size=r"\tiny",
        table_env="table",
    )

    dynamic = dynamic.rename(columns={"app": "app_label"})
    dynamic["app_category"] = dynamic["package"].map(publication_category)
    dynamic = category_sort(dynamic)
    table4 = []
    for _, row in dynamic.iterrows():
        baseline_is_qfg = pd.isna(row["strict_idle_median_packets_per_second"]) or float(row["strict_idle_run_count"]) == 0
        base_label = "Q" if baseline_is_qfg else "I"
        base_domains = row["qfg_median_domain_count"] if baseline_is_qfg else row["strict_idle_median_domain_count"]
        base_pps = row["qfg_median_packets_per_second"] if baseline_is_qfg else row["strict_idle_median_packets_per_second"]
        int_domains = row["interactive_median_domain_count"]
        int_pps = row["interactive_median_packets_per_second"]
        table4.append(
            {
                "App": display_label(row["app_label"]),
                "Base": base_label,
                "Domains B/I": f"{fnum(base_domains, 0) or '--'}/{fnum(int_domains, 0) or '--'}",
                "PPS B/I": f"{fnum(base_pps, 1) or '--'}/{fnum(int_pps, 1) or '--'}",
                "Int MB": fnum(float(row["interactive_median_bytes"]) / 1_000_000 if not pd.isna(row["interactive_median_bytes"]) else np.nan, 1),
            }
        )
    cols4 = ["App", "Base", "Domains B/I", "PPS B/I", "Int MB"]
    write_csv(TABLE_DIR / "table4_runtime_behavior_summary.csv", table4, cols4)
    write_tex_table(
        TABLE_DIR / "table4_runtime_behavior_summary.tex",
        "Runtime behavior indicators for selected app builds.",
        "tab:runtime-behavior-summary",
        cols4,
        table4,
        r"lcccc",
        size=r"\scriptsize",
        table_env="table",
        note="Base: I=strict-idle, Q=QFG. B/I reports baseline/interactive medians.",
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
    threshold_policy = {
        "policy_version": "median-split-v1",
        "static_indicator": "severity_high_count + severity_medium_count",
        "runtime_indicator": "interactive_median_domain_count",
        "static_threshold": hm_med,
        "runtime_threshold": dom_med,
        "comparison_operator": ">=",
        "tie_handling": "Values equal to the median are assigned to the higher group.",
        "taxonomy_version": CATEGORY_POLICY_VERSION,
    }
    (SOURCE_DIR / "integrated_profile_policy.json").write_text(json.dumps(threshold_policy, indent=2), encoding="utf-8")
    table5 = []
    for _, row in merged.pipe(category_sort).iterrows():
        s = "High static" if row["high_med"] >= hm_med else "Lower static"
        r = "high runtime" if row["int_domains"] >= dom_med else "lower runtime"
        if s.startswith("High") and r.startswith("high"):
            interp = "concordant higher"
        elif s.startswith("Lower") and r.startswith("lower"):
            interp = "concordant lower"
        elif s.startswith("High"):
            interp = "static-heavy"
        else:
            interp = "runtime-heavy"
        table5.append(
            {
                "App": display_label(row["app_label"]),
                "Group": f"{s}/{r}",
                "High+Med": int(row["high_med"]),
                "Int domains": fnum(row["int_domains"], 0),
                "Int runs": int(row["interactive_run_count"]),
                "Static threshold": f"{hm_med:.0f}",
                "Runtime threshold": f"{dom_med:.0f}",
                "Threshold policy": threshold_policy["comparison_operator"],
                "Policy version": threshold_policy["policy_version"],
                "Interpretation": interp,
            }
        )
    cols5 = [
        "App",
        "Group",
        "High+Med",
        "Int domains",
        "Int runs",
        "Static threshold",
        "Runtime threshold",
        "Threshold policy",
        "Policy version",
        "Interpretation",
    ]
    write_csv(TABLE_DIR / "table5_integrated_static_runtime_profiles.csv", table5, cols5)
    tex_cols5 = ["App", "Group", "High+Med", "Int domains", "Int runs", "Interpretation"]
    write_tex_table(
        TABLE_DIR / "table5_integrated_static_runtime_profiles.tex",
        "Supplemental integrated static-runtime app profiles using median-split indicators.",
        "tab:integrated-static-runtime-profiles",
        tex_cols5,
        table5,
        r"llrrrl",
        size=r"\tiny",
        table_env="table",
    )
    matrix_groups = {
        ("Lower static", "lower runtime"): [],
        ("Lower static", "high runtime"): [],
        ("High static", "lower runtime"): [],
        ("High static", "high runtime"): [],
    }
    for row in table5:
        group = str(row["Group"])
        s_group, r_group = group.split("/")
        matrix_groups[(s_group, r_group)].append(str(row["App"]))
    matrix_rows = [
        {
            "Static": "Lower static",
            "Lower runtime": f"{len(matrix_groups[('Lower static', 'lower runtime')])}: {', '.join(matrix_groups[('Lower static', 'lower runtime')])}",
            "Higher runtime": f"{len(matrix_groups[('Lower static', 'high runtime')])}: {', '.join(matrix_groups[('Lower static', 'high runtime')])}",
        },
        {
            "Static": "Higher static",
            "Lower runtime": f"{len(matrix_groups[('High static', 'lower runtime')])}: {', '.join(matrix_groups[('High static', 'lower runtime')])}",
            "Higher runtime": f"{len(matrix_groups[('High static', 'high runtime')])}: {', '.join(matrix_groups[('High static', 'high runtime')])}",
        },
    ]
    matrix_cols = ["Static", "Lower runtime", "Higher runtime"]
    write_csv(TABLE_DIR / "table5_integrated_profile_matrix.csv", matrix_rows, matrix_cols)
    note5 = (
        f"Higher static uses high/medium findings $\\geq {hm_med:.0f}$; "
        f"higher runtime uses interactive domains $\\geq {dom_med:.0f}$. "
        "Ties are assigned to the higher group."
    )
    write_tex_table(
        TABLE_DIR / "table5_integrated_profile_matrix.tex",
        "Integrated static-runtime profile matrix using median-split indicators.",
        "tab:integrated-profile-matrix",
        matrix_cols,
        matrix_rows,
        r"@{}>{\raggedright\arraybackslash}p{0.16\columnwidth}>{\raggedright\arraybackslash}p{0.34\columnwidth}>{\raggedright\arraybackslash}p{0.34\columnwidth}@{}",
        size=r"\scriptsize",
        table_env="table",
        note=note5,
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
        {"Measure": "Selected apps", "Basis": "Build-aligned set", "Value": str(len(manifest))},
        {"Measure": "Selected dynamic runs", "Basis": "QA-valid runs", "Value": str(int(dynamic["selected_run_count"].sum()))},
        {"Measure": "Strict idle/QFG/interactive", "Basis": "Evidence classes", "Value": f"{int(dynamic['strict_idle_run_count'].sum())}/{int(dynamic['qfg_run_count'].sum())}/{int(dynamic['interactive_run_count'].sum())}"},
        {"Measure": "Runtime-shift eligible apps", "Basis": "Baseline+interactive", "Value": str(len(compared))},
        {"Measure": "Median log2 PPS shift", "Basis": "App medians", "Value": f"{np.median(shift):.2f}"},
        {"Measure": "Spearman rho, findings vs. domains", "Basis": "Descriptive", "Value": f"{rho:.2f}"},
    ]
    cols6 = ["Measure", "Basis", "Value"]
    write_csv(TABLE_DIR / "table6_statistical_summary.csv", table6, cols6)
    write_tex_table(
        TABLE_DIR / "table6_statistical_summary.tex",
        "Compact descriptive statistical summary.",
        "tab:statistical-summary",
        cols6,
        table6,
        r"@{}p{0.42\columnwidth}p{0.34\columnwidth}r@{}",
        table_env="table",
        size=r"\scriptsize",
        note="Runtime shift uses strict-idle when available, otherwise QFG. Associations are descriptive.",
    )

    # Preserve the app-level basis for baseline-relative runtime comparisons.
    eligibility = []
    for pkg, g in runs.groupby("package"):
        app_name = g["app"].iloc[0]
        base_count = int(g["evidence_class"].isin(["strict_idle", "qfg"]).sum())
        int_count = int(g["evidence_class"].eq("interactive").sum())
        eligibility.append(
            {
                "app": display_label(app_name),
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
        out = df.copy()
        for display_col in ("app", "app_label", "App", "app_display_name"):
            if display_col in out.columns:
                out[display_col] = out[display_col].map(display_label)
        out.to_csv(SOURCE_DIR / name, index=False)


def build_pipeline_figure() -> None:
    stages = [
        ("15-app\ndataset", 0.50, 0.93),
        ("APK harvest\n+ split identity", 0.50, 0.82),
        ("Static\nanalysis", 0.32, 0.68),
        ("Dynamic\nI/QFG/Int", 0.68, 0.68),
        ("Evidence QA\n+ build gate", 0.50, 0.53),
        ("14-day build\nselection", 0.50, 0.39),
        ("Static-runtime\nalignment", 0.50, 0.27),
        ("Integrated\nanalysis", 0.50, 0.16),
        ("Tables, figures,\nchecksums", 0.50, 0.05),
    ]
    exclusions = "Exclude/defer:\nbuild mismatch\nmissing evidence\ninvalid run"
    fig, ax = plt.subplots(figsize=(3.35, 5.15))
    ax.axis("off")
    for text, x, y in stages:
        ax.text(x, y, text, ha="center", va="center", fontsize=8.2,
                bbox=dict(boxstyle="round,pad=0.22", facecolor="#eaf2f8", edgecolor="#2c5f8a", linewidth=0.9))
    arrows = [(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8)]
    for a, b in arrows:
        x1, y1 = stages[a][1], stages[a][2]
        x2, y2 = stages[b][1], stages[b][2]
        ax.annotate("", xy=(x2, y2 + 0.045 if y2 < y1 else y2), xytext=(x1, y1 - 0.045 if y2 < y1 else y1),
                    arrowprops=dict(arrowstyle="->", color="#333333", lw=0.9))
    ax.text(0.82, 0.50, exclusions, ha="center", va="center", fontsize=7.4,
            bbox=dict(boxstyle="round,pad=0.20", facecolor="#fff1e6", edgecolor="#a85d15", linewidth=0.9))
    ax.annotate("", xy=(0.70, 0.50), xytext=(0.56, 0.52),
                arrowprops=dict(arrowstyle="->", color="#a85d15", lw=0.9, linestyle="--"))
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
    plot_static = static.sort_values("high_medium_findings", ascending=True).copy()
    y = np.arange(len(plot_static))
    fig, ax = plt.subplots(figsize=(3.45, 4.6))
    series = [
        ("high_medium_findings", "High/medium findings", "#0072B2", "o", 0.22),
        ("exported_components_without_permission_guard", "Unguarded components", "#D55E00", "s", 0.0),
        ("dangerous_permissions", "Dangerous permissions", "#009E73", "^", -0.22),
    ]
    for col, label, color, marker, offset in series:
        vals = np.log10(1 + plot_static[col].astype(float).values)
        ax.scatter(vals, y + offset, label=label, color=color, marker=marker, s=22, edgecolor="black", linewidth=0.35)
    ax.set_yticks(y, [display_label(v) for v in plot_static["app_label"]], fontsize=8.0)
    ax.set_xlabel("log10(1 + count)", fontsize=8.6)
    ax.tick_params(axis="x", labelsize=8.0)
    ax.grid(axis="x", color="#dddddd", linewidth=0.5)
    ax.legend(loc="lower right", fontsize=7.2, frameon=True)
    fig.tight_layout(pad=0.2)
    fig.savefig(FIGURE_DIR / "fig2_static_exposure_dotplot.pdf")
    fig.savefig(FIGURE_DIR / "fig2_static_exposure_dotplot.png", dpi=240)
    heat_out = plot_static[["app_label", "high_medium_findings", "exported_components_without_permission_guard", "dangerous_permissions"]].copy()
    heat_out["app_label"] = heat_out["app_label"].map(display_label)
    heat_out.to_csv(SOURCE_DIR / "fig2_static_exposure_dotplot_source.csv", index=False)
    plt.close(fig)

    dynamic = dynamic.rename(columns={"app": "app_label"})
    dynamic["app_category"] = dynamic["package"].map(publication_category)
    dynamic = category_sort(dynamic)
    dyn_counts = dynamic[["app_label", "strict_idle_run_count", "qfg_run_count", "interactive_run_count"]].copy()
    dyn_counts["app_label"] = dyn_counts["app_label"].map(display_label)
    dyn_counts.to_csv(SOURCE_DIR / "fig3_runtime_coverage_source.csv", index=False)
    y = np.arange(len(dynamic))
    fig, ax = plt.subplots(figsize=(3.45, 4.75))
    left = np.zeros(len(dynamic))
    colors = ["#0072B2", "#E69F00", "#009E73"]
    hatches = ["", "///", "..."]
    labels = ["Strict-idle", "QFG", "Interactive"]
    cols = ["strict_idle_run_count", "qfg_run_count", "interactive_run_count"]
    for col, label, color, hatch in zip(cols, labels, colors, hatches):
        vals = dynamic[col].fillna(0).astype(int).values
        ax.barh(y, vals, left=left, label=label, color=color, hatch=hatch, edgecolor="black", linewidth=0.25)
        for yi, val, li in zip(y, vals, left):
            if val >= 2:
                ax.text(li + val / 2, yi, str(val), ha="center", va="center", fontsize=7.1, color="white")
        left += vals
    ax.set_yticks(y, [display_label(v) for v in dynamic["app_label"]], fontsize=7.8)
    ax.invert_yaxis()
    ax.set_xlabel("selected runs", fontsize=8.6)
    ax.tick_params(axis="x", labelsize=8.0)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.10), ncols=3, fontsize=7.0, frameon=False)
    fig.tight_layout(pad=0.2)
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
    merged["x_log_high_med"] = np.log10(1 + merged["high_medium_findings"])
    merged["app_category"] = merged["package_name"].map(publication_category)
    scatter_source = merged[
        [
            "app_label",
            "package_name",
            "app_category",
            "high_medium_findings",
            "runtime_shift_log2_pps",
            "interactive_run_count",
            "x_log_high_med",
        ]
    ].copy()
    scatter_source["app_label"] = scatter_source["app_label"].map(display_label)
    scatter_source.to_csv(SOURCE_DIR / "fig4_static_runtime_scatter_source.csv", index=False)
    fig, ax = plt.subplots(figsize=(7.2, 4.05))
    plot = merged.copy()
    for cat in CATEGORY_ORDER:
        group = plot[plot["app_category"].eq(cat)]
        if group.empty:
            continue
        style = CATEGORY_STYLES[cat]
        ax.scatter(
            group["x_log_high_med"],
            group["runtime_shift_log2_pps"],
            s=58,
            label=cat,
            alpha=0.82,
            color=style["color"],
            marker=style["marker"],
            edgecolor="black",
            linewidth=0.4,
        )
    offsets = {
        "BBC News": (-48, 7),
        "CNN": (6, 6),
        "The Guardian": (-76, -13),
        "Facebook": (8, 7),
        "Instagram": (-72, 9),
        "Pinterest": (-58, 9),
        "Reddit": (-52, -12),
        "TikTok": (8, -14),
        "X": (8, -15),
        "LinkedIn": (8, 7),
        "Signal": (7, 8),
        "Snapchat": (8, -10),
        "Telegram": (8, -12),
        "WhatsApp": (-68, 8),
        "Facebook Messenger": (8, 8),
    }
    for _, row in plot.iterrows():
        ax.annotate(
            display_label(row["app_label"]),
            (row["x_log_high_med"], row["runtime_shift_log2_pps"]),
            xytext=offsets.get(row["app_label"], (4, 4)),
            textcoords="offset points",
            fontsize=7.1,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.72),
            arrowprops=dict(arrowstyle="-", color="#8a8a8a", lw=0.35, shrinkA=0, shrinkB=4),
        )
    ax.axhline(0, color="#777777", lw=0.8, linestyle="--")
    ax.set_xlabel("log10(1 + high/medium findings)", fontsize=8.6)
    ax.set_ylabel("log2(interactive/base PPS)", fontsize=8.6)
    ax.tick_params(labelsize=8.0)
    ax.margins(x=0.18, y=0.14)
    ax.legend(fontsize=7.2, loc="upper center", bbox_to_anchor=(0.5, 1.17), ncols=4, frameon=False)
    fig.tight_layout(pad=0.2)
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
