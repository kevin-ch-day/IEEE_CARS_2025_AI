#!/usr/bin/env python3
"""Reproducible risk-posture, mathematical, and Disconnect tracker audit.

Internal diagnostic only. Constructed scalar scores are written under
internal_scores/ and must not enter the camera-ready manuscript.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.integrate import trapezoid
from scipy.spatial import ConvexHull, QhullError

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "inputs"
OUT = ROOT / "outputs"
FIG = ROOT / "figures"
TRACKER = ROOT / "tracker"
SCORES = ROOT / "internal_scores"
REPORTS = ROOT / "reports"
VALIDATION = ROOT / "validation"

SEED = 20260709
N_BOOT = 10_000
N_PERM = 10_000
SNAP = "com.snapchat.android"
ALIAS_TITLE = "Exported activity alias without permission"
UNGUARD_PHRASES = ("without permission", "weak guard")
TRACKING_CATS = {
    "Advertising",
    "Analytics",
    "Social",
    "FingerprintingInvasive",
    "FingerprintingGeneral",
    "Cryptomining",
    "Email",
    "EmailAggressive",
    "ConsentManagers",
}

CAT = {
    "bbc.mobile.news.ww": "News",
    "com.cnn.mobile.android.phone": "News",
    "com.guardian": "News",
    "com.facebook.katana": "Social",
    "com.instagram.android": "Social",
    "com.pinterest": "Social",
    "com.reddit.frontpage": "Social",
    "com.snapchat.android": "Social",
    "com.zhiliaoapp.musically": "Social",
    "com.twitter.android": "Social",
    "com.facebook.orca": "Messaging",
    "org.thoughtcrime.securesms": "Messaging",
    "org.telegram.messenger": "Messaging",
    "com.whatsapp": "Messaging",
    "com.linkedin.android": "Professional",
}

DISCONNECT_COMMIT = "22c7d6166b6e30f7629ee1b49386855bb9b64a50"
DISCONNECT_REPO = "https://github.com/disconnectme/disconnect-tracking-protection"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fnum(x) -> float:
    try:
        if x in ("", None):
            return float("nan")
        return float(x)
    except Exception:
        return float("nan")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows and fieldnames is None:
        path.write_text("", encoding="utf-8")
        return
    names = fieldnames or list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=names, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in names})


def dump_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n", encoding="utf-8")


def minmax(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, float)
    lo, hi = np.nanmin(a), np.nanmax(a)
    if not np.isfinite(lo) or hi == lo:
        return np.zeros_like(a)
    return (a - lo) / (hi - lo)


def percentile_rank(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, float)
    return (stats.rankdata(a, method="average") - 1) / (len(a) - 1)


def robust_mad_scale(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, float)
    med = np.median(a)
    mad = np.median(np.abs(a - med))
    z = 0.6745 * (a - med) / mad if mad else np.zeros_like(a)
    return 1.0 / (1.0 + np.exp(-z))


def w1_quantile(a, b, grid: int = 1001) -> float:
    a = np.sort(np.asarray(a, float))
    b = np.sort(np.asarray(b, float))
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if a.size == 0 or b.size == 0:
        return float("nan")
    t = np.linspace(0.0, 1.0, grid)

    def q(s, t):
        if s.size == 1:
            return np.full_like(t, s[0])
        u = (np.arange(1, s.size + 1) - 0.5) / s.size
        return np.interp(t, u, s, left=s[0], right=s[-1])

    return float(trapezoid(np.abs(q(a, t) - q(b, t)), t))


def biased_dcor(x, y) -> float:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    a = np.abs(x[:, None] - x[None, :])
    b = np.abs(y[:, None] - y[None, :])
    A = a - a.mean(0) - a.mean(1)[:, None] + a.mean()
    B = b - b.mean(0) - b.mean(1)[:, None] + b.mean()
    dcov2 = float((A * B).mean())
    dvarx = float((A * A).mean())
    dvary = float((B * B).mean())
    if dvarx <= 0 or dvary <= 0:
        return 0.0
    return float(np.sqrt(max(dcov2, 0.0) / math.sqrt(dvarx * dvary)))


def dcor_perm_p(x, y, rng: np.random.Generator, B: int) -> tuple[float, float, int]:
    obs = biased_dcor(x, y)
    y = np.asarray(y, float)
    cnt = 0
    for _ in range(B):
        if biased_dcor(x, rng.permutation(y)) >= obs - 1e-15:
            cnt += 1
    p = (cnt + 1) / (B + 1)
    return obs, p, cnt


def bh_fdr(pvals: list[float]) -> list[float]:
    m = len(pvals)
    order = np.argsort(pvals)
    q = np.empty(m)
    prev = 1.0
    for rank, idx in enumerate(order[::-1], start=0):
        i = order[m - 1 - rank]
        adj = pvals[i] * m / (m - rank)
        prev = min(prev, adj)
        q[i] = min(prev, 1.0)
    return q.tolist()


def load_apps() -> tuple[list[dict], dict]:
    static = {r["package_name"]: r for r in read_csv(INPUTS / "publication_static_app_metrics.csv")}
    dyn = {r["package"]: r for r in read_csv(INPUTS / "publication_dynamic_app_metrics.csv")}
    findings = read_csv(INPUTS / "publication_static_finding_rows.csv")
    run_pkg = {s["contributing_static_run_id"]: pkg for pkg, s in static.items()}
    alias = Counter()
    high_n = Counter()
    hm_n = Counter()
    for f in findings:
        pkg = run_pkg.get(f["run_id"])
        if not pkg:
            continue
        if f["severity"] in ("High", "Medium"):
            hm_n[pkg] += 1
            if f["title"] == ALIAS_TITLE:
                alias[pkg] += 1
        if f["severity"] == "High":
            high_n[pkg] += 1
    apps = []
    for pkg, s in static.items():
        d = dyn[pkg]
        idle_n = int(float(d["strict_idle_run_count"] or 0))
        pref = "strict_idle" if idle_n > 0 else "qfg"
        bp = fnum(d[f"{pref}_median_packets_per_second"])
        ip = fnum(d["interactive_median_packets_per_second"])
        ibps = fnum(d["interactive_median_bytes_per_second"])
        bbps = fnum(d[f"{pref}_median_bytes_per_second"])
        apps.append(
            {
                "app": s["app_label"],
                "pkg": pkg,
                "cat": CAT[pkg],
                "hm": int(s["severity_high_count"]) + int(s["severity_medium_count"]),
                "ung": int(s["exported_components_without_permission_guard"]),
                "dang": int(s["dangerous_permissions"]),
                "high": high_n[pkg],
                "alias": alias[pkg],
                "residual": hm_n[pkg] - alias[pkg],
                "idom": fnum(d["interactive_median_domain_count"]),
                "imb": fnum(d["interactive_median_bytes"]) / 1e6,
                "ibps": ibps,
                "bbps": bbps,
                "ipps": ip,
                "bpps": bp,
                "baseline_class": pref,
                "log_s": float(np.log2((ip + 1) / (bp + 1))),
                "nidle": idle_n,
                "nqfg": int(float(d["qfg_run_count"] or 0)),
                "nint": int(float(d["interactive_run_count"] or 0)),
            }
        )
    apps.sort(key=lambda a: a["app"])
    meta = {
        "static_csv": str(INPUTS / "publication_static_app_metrics.csv"),
        "dynamic_csv": str(INPUTS / "publication_dynamic_app_metrics.csv"),
        "findings_csv": str(INPUTS / "publication_static_finding_rows.csv"),
        "residual_rule": f"cohort-wide drop of High/Medium rows titled '{ALIAS_TITLE}'",
        "pps_shift": "log2((interactive_median_pps+1)/(baseline_median_pps+1)); baseline=strict_idle if count>0 else qfg",
        "hostname_metric": "interactive_median_domain_count = median per-run union of retained top_dns/top_sni",
    }
    return apps, meta


def spearman_audit(apps: list[dict], rng: np.random.Generator) -> dict:
    names = [a["app"] for a in apps]
    x = np.array([a["hm"] for a in apps], float)
    y = np.array([a["idom"] for a in apps], float)
    n = len(x)
    sp = stats.spearmanr(x, y)
    mask = np.array([a["pkg"] != SNAP for a in apps])
    sp14 = stats.spearmanr(x[mask], y[mask])
    loo = []
    for i, name in enumerate(names):
        m = np.ones(n, bool)
        m[i] = False
        spi = stats.spearmanr(x[m], y[m])
        loo.append(
            {
                "app": name,
                "full_rho": sp.statistic,
                "loo_rho": spi.statistic,
                "delta": spi.statistic - sp.statistic,
                "abs_delta": abs(spi.statistic - sp.statistic),
                "loo_p": spi.pvalue,
            }
        )
    loo.sort(key=lambda r: -r["abs_delta"])
    for rank, r in enumerate(loo, 1):
        r["influence_rank"] = rank
    write_csv(OUT / "spearman_leave_one_out.csv", loo)

    loo_rho = np.array([next(r["loo_rho"] for r in loo if r["app"] == name) for name in names])
    loo_mean = float(loo_rho.mean())
    jack_var = ((n - 1) / n) * float(np.sum((loo_rho - loo_mean) ** 2))
    jack_se = math.sqrt(jack_var) if jack_var > 0 else 0.0
    jack_ci = [sp.statistic - 1.96 * jack_se, sp.statistic + 1.96 * jack_se]
    jack_usable = jack_ci[0] >= -1.0 and jack_ci[1] <= 1.0
    pseudo = n * sp.statistic - (n - 1) * loo_rho
    # equivalent pseudo-value variance: var_p / (n(n-1)) wait: SE^2 = 1/(n(n-1)) sum (pseudo-mean_p)^2
    # which equals jack_var above.

    boots = np.empty(N_BOOT)
    for b in range(N_BOOT):
        idx = rng.integers(0, n, n)
        boots[b] = stats.spearmanr(x[idx], y[idx]).statistic
    perc = np.quantile(boots, [0.025, 0.5, 0.975])

    def stat(d1, d2):
        return stats.spearmanr(d1, d2).statistic

    bca = stats.bootstrap(
        (x, y),
        stat,
        n_resamples=N_BOOT,
        paired=True,
        method="BCa",
        random_state=np.random.default_rng(SEED),
        vectorized=False,
    )
    boot = {
        "unit": "app-level pairs (n=15), with-replacement",
        "n_resamples": N_BOOT,
        "seed": SEED,
        "point_rho": float(sp.statistic),
        "percentile_ci_95": [float(perc[0]), float(perc[2])],
        "percentile_median": float(perc[1]),
        "bca_ci_95": [float(bca.confidence_interval.low), float(bca.confidence_interval.high)],
        "exploratory_note": "n=15; interval is exploratory, not a confirmatory CI",
        "jackknife": {
            "formula": "V=((n-1)/n)*sum((theta_(-i)-mean_loo)^2); SE=sqrt(V); pseudo=n*theta-(n-1)*theta_(-i)",
            "se": jack_se,
            "mean_loo": loo_mean,
            "ci_normal_approx": jack_ci,
            "usable": jack_usable,
            "reason_if_unusable": None
            if jack_usable
            else "linearized interval leaves [-1,1]; first-order jackknife SE is not a valid Spearman CI at n=15 near independence",
        },
    }
    dump_json(OUT / "spearman_bootstrap.json", boot)
    return {
        "n15": {"rho": float(sp.statistic), "p": float(sp.pvalue), "n": 15},
        "n14_no_snapchat": {"rho": float(sp14.statistic), "p": float(sp14.pvalue), "n": 14},
        "most_influential_loo": loo[0]["app"],
        "jackknife_usable": jack_usable,
        "bootstrap": boot,
        "columns": {
            "x": "severity_high_count+severity_medium_count",
            "y": "interactive_median_domain_count",
        },
    }


def dcor_audit(apps: list[dict], rng: np.random.Generator) -> list[dict]:
    x_hm = np.array([a["hm"] for a in apps], float)
    x_res = np.array([a["residual"] for a in apps], float)
    y_h = np.array([a["idom"] for a in apps], float)
    z = np.array([a["log_s"] for a in apps], float)
    dang = np.array([a["dang"] for a in apps], float)
    pairs = [
        ("hm vs hosts (paper)", x_hm, y_h),
        ("residual vs hosts", x_res, y_h),
        ("hm vs log2 PPS", x_hm, z),
        ("hosts vs log2 PPS", y_h, z),
        ("dang vs log2 PPS", dang, z),
        ("dang vs hosts", dang, y_h),
    ]
    rows = []
    pvals = []
    for name, xa, ya in pairs:
        ties_x = len(xa) != len(set(xa.tolist()))
        ties_y = len(ya) != len(set(ya.tolist()))
        dc, p, cnt = dcor_perm_p(xa, ya, rng, N_PERM)
        sp = stats.spearmanr(xa, ya)
        rows.append(
            {
                "pair": name,
                "estimator": "Székely–Rizzo biased distance correlation (double-centering, n^{-2})",
                "n": 15,
                "dcor": dc,
                "perm_B": N_PERM,
                "perm_seed_stream": SEED,
                "perm_count_ge_obs": cnt,
                "p_plus_one": p,
                "ties_x": ties_x,
                "ties_y": ties_y,
                "spearman_rho": float(sp.statistic),
                "spearman_p": float(sp.pvalue),
            }
        )
        pvals.append(p)
    q = bh_fdr(pvals)
    for r, qi in zip(rows, q):
        r["bh_q_among_6_pairs"] = qi
        r["n_hypotheses"] = 6
    write_csv(OUT / "distance_correlation.csv", rows)
    return rows


def wasserstein_audit(apps: list[dict], rng: np.random.Generator) -> dict:
    runs = read_csv(INPUTS / "publication_dynamic_run_metrics.csv")
    by_cls = defaultdict(list)
    by_app_cls = defaultdict(lambda: defaultdict(list))
    for r in runs:
        pps = fnum(r["packets_per_second"])
        bps = fnum(r["bytes_per_second"])
        hosts = fnum(r["domain_count"])
        rec = {"pps": pps, "bps": bps, "hosts": hosts, "pkg": r["package"]}
        by_cls[r["evidence_class"]].append(rec)
        by_app_cls[r["package"]][r["evidence_class"]].append(rec)

    def pooled(cls, field):
        return np.array([x[field] for x in by_cls[cls] if np.isfinite(x[field])], float)

    def app_medians(cls, field):
        vals = []
        for a in apps:
            xs = [x[field] for x in by_app_cls[a["pkg"]].get(cls, []) if np.isfinite(x[field])]
            if xs:
                vals.append(float(np.median(xs)))
        return np.array(vals, float)

    cohort_rows = []
    for field, unit in [("pps", "packets/s"), ("bps", "bytes/s"), ("hosts", "retained names")]:
        for a, b in [("strict_idle", "qfg"), ("strict_idle", "interactive"), ("qfg", "interactive")]:
            cohort_rows.append(
                {
                    "field": field,
                    "unit": unit,
                    "from": a,
                    "to": b,
                    "run_pooled_W1": w1_quantile(pooled(a, field), pooled(b, field)),
                    "n_from_runs": int(pooled(a, field).size),
                    "n_to_runs": int(pooled(b, field).size),
                    "app_balanced_W1_on_app_medians": w1_quantile(app_medians(a, field), app_medians(b, field)),
                    "n_from_apps": int(app_medians(a, field).size),
                    "n_to_apps": int(app_medians(b, field).size),
                    "warning_pooled": "run-pooled weights apps with more selected captures more heavily",
                    "app_balanced_construction": "one median per app per class, then W1 between those empirical measures (equal app weight)",
                }
            )
    write_csv(OUT / "wasserstein_cohort.csv", cohort_rows)

    per_app = []
    for a in apps:
        idle = [x["pps"] for x in by_app_cls[a["pkg"]].get("strict_idle", [])]
        qfg = [x["pps"] for x in by_app_cls[a["pkg"]].get("qfg", [])]
        inter = [x["pps"] for x in by_app_cls[a["pkg"]].get("interactive", [])]
        idle_h = [x["hosts"] for x in by_app_cls[a["pkg"]].get("strict_idle", [])]
        inter_h = [x["hosts"] for x in by_app_cls[a["pkg"]].get("interactive", [])]
        idle_b = [x["bps"] for x in by_app_cls[a["pkg"]].get("strict_idle", [])]
        inter_b = [x["bps"] for x in by_app_cls[a["pkg"]].get("interactive", [])]
        per_app.append(
            {
                "app": a["app"],
                "pkg": a["pkg"],
                "n_idle": len(idle),
                "n_qfg": len(qfg),
                "n_int": len(inter),
                "W1_idle_int_pps": w1_quantile(idle, inter) if idle and inter else "",
                "W1_qfg_int_pps": w1_quantile(qfg, inter) if qfg and inter else "",
                "W1_idle_int_bps": w1_quantile(idle_b, inter_b) if idle_b and inter_b else "",
                "W1_idle_int_hosts": w1_quantile(idle_h, inter_h) if idle_h and inter_h else "",
                "note": "tiny per-app n; W1 is a transport cost, not a risk score",
            }
        )
    write_csv(OUT / "wasserstein_per_app.csv", per_app)

    # app-level bootstrap of app-balanced W1 for idle vs interactive PPS
    pkgs_both = [a["pkg"] for a in apps if by_app_cls[a["pkg"]].get("strict_idle") and by_app_cls[a["pkg"]].get("interactive")]
    boots = []
    for _ in range(N_BOOT):
        sample = [pkgs_both[i] for i in rng.integers(0, len(pkgs_both), len(pkgs_both))]
        idle_m, int_m = [], []
        for pkg in sample:
            idle_m.append(float(np.median([x["pps"] for x in by_app_cls[pkg]["strict_idle"]])))
            int_m.append(float(np.median([x["pps"] for x in by_app_cls[pkg]["interactive"]])))
        boots.append(w1_quantile(idle_m, int_m))
    boots = np.array(boots)
    boot = {
        "target": "app-balanced W1 of app-median PPS, idle vs interactive",
        "n_apps_with_both": len(pkgs_both),
        "n_resamples": N_BOOT,
        "seed": SEED,
        "point": w1_quantile(app_medians("strict_idle", "pps"), app_medians("interactive", "pps")),
        "percentile_ci_95": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))],
        "unit": "packets/s",
    }
    dump_json(OUT / "wasserstein_bootstrap.json", boot)
    return {"cohort": cohort_rows, "bootstrap": boot}


def hull_audit(apps: list[dict], tracker_frac: dict[str, float] | None) -> dict:
    names = [a["app"] for a in apps]
    planes = {
        "hm_vs_hosts": (
            np.array([a["hm"] for a in apps], float),
            np.array([a["idom"] for a in apps], float),
            "high+medium findings",
            "interactive retained-host median",
        ),
        "residual_vs_logpps": (
            np.array([a["residual"] for a in apps], float),
            np.array([a["log_s"] for a in apps], float),
            "residual high+medium (alias title dropped cohort-wide)",
            "smoothed log2 PPS shift",
        ),
    }
    if tracker_frac is not None:
        planes["hm_vs_tracker_frac"] = (
            np.array([a["hm"] for a in apps], float),
            np.array([tracker_frac.get(a["pkg"], float("nan")) for a in apps], float),
            "high+medium findings",
            "interactive tracker-associated hostname fraction",
        )

    results = {}
    loo_rows = []
    for key, (x, y, xlab, ylab) in planes.items():
        mx, sx = float(np.mean(x)), float(np.std(x, ddof=1))
        my, sy = float(np.mean(y)), float(np.std(y, ddof=1))
        Xz = (x - mx) / sx
        Yz = (y - my) / sy
        P = np.c_[Xz, Yz]
        try:
            H = ConvexHull(P)
            area = float(H.volume)  # 2D area
            peri = float(H.area)
            verts = [names[i] for i in H.vertices]
        except QhullError as e:
            area, peri, verts = float("nan"), float("nan"), [f"QhullError:{e}"]
        results[key] = {
            "x": xlab,
            "y": ylab,
            "normalization": "z-score mean/sd, ddof=1, fitted once on full n=15",
            "robust_alternative_not_used": "median/MAD not used for primary hull",
            "area": area,
            "perimeter": peri,
            "vertices": verts,
            "note": "vertices are axis-dependent extremes, not highest-risk apps",
            "tolerance": "Qhull default",
        }
        n = len(apps)
        for i, name in enumerate(names):
            m = np.ones(n, bool)
            m[i] = False
            P2 = np.c_[Xz[m], Yz[m]]  # same full-cohort scaler
            try:
                a2 = float(ConvexHull(P2).volume)
            except QhullError:
                a2 = float("nan")
            loo_rows.append(
                {
                    "plane": key,
                    "left_out": name,
                    "full_area": area,
                    "loo_area": a2,
                    "delta_area": area - a2 if np.isfinite(a2) else "",
                    "rel_change": (area - a2) / area if np.isfinite(a2) and area else "",
                    "scaler": "frozen full-cohort mean/sd",
                }
            )
    write_csv(OUT / "convex_hull_leave_one_out.csv", loo_rows)
    dump_json(OUT / "convex_hulls.json", results)

    if plt is not None:
        fig, axes = plt.subplots(1, min(2, len(planes)), figsize=(9.2, 4.0))
        if not hasattr(axes, "__len__"):
            axes = [axes]
        for ax, key in zip(axes, list(planes)[:2]):
            x, y, xlab, ylab = planes[key]
            mx, sx = np.mean(x), np.std(x, ddof=1)
            my, sy = np.mean(y), np.std(y, ddof=1)
            Xz, Yz = (x - mx) / sx, (y - my) / sy
            H = ConvexHull(np.c_[Xz, Yz])
            ax.scatter(Xz, Yz, c="#444", s=28)
            for i, nm in enumerate(names):
                ax.annotate(nm, (Xz[i], Yz[i]), fontsize=6, xytext=(3, 3), textcoords="offset points")
            hull_pts = np.c_[Xz, Yz][H.vertices]
            hull_pts = np.vstack([hull_pts, hull_pts[0]])
            ax.plot(hull_pts[:, 0], hull_pts[:, 1], color="#0072B2", lw=1.0)
            ax.set_xlabel("z " + xlab, fontsize=7)
            ax.set_ylabel("z " + ylab, fontsize=7)
            ax.set_title(key.replace("_", " "), fontsize=8)
        fig.tight_layout()
        FIG.mkdir(parents=True, exist_ok=True)
        fig.savefig(FIG / "posture_hulls.pdf")
        fig.savefig(FIG / "posture_hulls.png", dpi=160)
        plt.close(fig)
    return results


def copula_audit(apps: list[dict]) -> dict:
    x = np.array([a["hm"] for a in apps], float)
    y = np.array([a["idom"] for a in apps], float)
    rx = stats.rankdata(x, method="average")
    ry = stats.rankdata(y, method="average")
    mx, my = float(np.median(rx)), float(np.median(ry))
    n = len(apps)
    uu = ul = lu = ll = on = 0
    detail = []
    for a, rxi, ryi in zip(apps, rx, ry):
        if rxi == mx or ryi == my:
            cat = "on_median_rank"
            on += 1
        elif rxi > mx and ryi > my:
            cat = "UU"
            uu += 1
        elif rxi > mx and ryi < my:
            cat = "UL"
            ul += 1
        elif rxi < mx and ryi > my:
            cat = "LU"
            lu += 1
        else:
            cat = "LL"
            ll += 1
        detail.append({"app": a["app"], "rank_x": float(rxi), "rank_y": float(ryi), "copula_cell": cat})
    masses = {
        "rank_method": "scipy.stats.rankdata average ties",
        "threshold": "median of ranks",
        "UU": uu / n,
        "UL": ul / n,
        "LU": lu / n,
        "LL": ll / n,
        "on_median_rank": on / n,
        "sum": (uu + ul + lu + ll + on) / n,
        "prior_0.20x4_explanation": "earlier 0.20*4=0.80 omitted the on-median-rank mass; it was not a copula of independent uniforms with a missing 0.20 from error in arithmetic of independent cells alone",
        "table_iv_rule": "higher group if value >= cohort median (raw metric, not rank copula)",
        "detail": detail,
    }
    # Table IV
    hm_med = float(np.median(x))
    host_med = float(np.median(y))
    tv: dict[str, list[str]] = {}
    for a in apps:
        hs = "H" if a["hm"] >= hm_med else "L"
        hr = "H" if a["idom"] >= host_med else "L"
        tv.setdefault(hs + hr, []).append(a["app"])
    masses["table_iv"] = {
        "static_threshold": hm_med,
        "runtime_threshold": host_med,
        "tie_rule": ">= median assigned to higher group",
        "cells": {k: v for k, v in tv.items()},
        "counts": {k: len(v) for k, v in tv.items()},
    }
    dump_json(OUT / "copula_quadrant_masses.json", masses)
    return masses


def pareto_front(apps: list[dict], tracker_frac: dict[str, float] | None) -> list[dict]:
    planes = [
        ("max hm & max hosts", "hm", "idom", True, True),
        ("max residual & max log_s", "residual", "log_s", True, True),
    ]
    rows = []
    if tracker_frac is not None:
        for a in apps:
            a["tfrac"] = tracker_frac.get(a["pkg"], float("nan"))
        planes.append(("max hm & max tracker_frac", "hm", "tfrac", True, True))
    for name, kx, ky, maxx, maxy in planes:
        xs = np.array([a[kx] for a in apps], float)
        ys = np.array([a[ky] for a in apps], float)
        if not maxx:
            xs = -xs
        if not maxy:
            ys = -ys
        nd = []
        for i, a in enumerate(apps):
            dominated = False
            for j in range(len(apps)):
                if i == j:
                    continue
                if xs[j] >= xs[i] and ys[j] >= ys[i] and (xs[j] > xs[i] or ys[j] > ys[i]):
                    dominated = True
                    break
            nd.append(not dominated)
            rows.append(
                {
                    "plane": name,
                    "app": a["app"],
                    "x_var": kx,
                    "y_var": ky,
                    "x": a[kx],
                    "y": a[ky],
                    "maximize": "both",
                    "nondominated": (not dominated),
                    "label": "nondominated under the selected evidence dimensions"
                    if not dominated
                    else "dominated",
                }
            )
    write_csv(OUT / "pareto_fronts.csv", rows)
    return rows


def score_stress(apps: list[dict]) -> dict:
    hm = np.array([a["hm"] for a in apps], float)
    ung = np.array([a["ung"] for a in apps], float)
    dang = np.array([a["dang"] for a in apps], float)
    res = np.array([a["residual"] for a in apps], float)
    high = np.array([a["high"] for a in apps], float)
    logs = np.array([a["log_s"] for a in apps], float)
    hosts = np.array([a["idom"] for a in apps], float)
    mb = np.array([a["imb"] for a in apps], float)

    variants = {
        "StaticA_minmax": (minmax(hm) + minmax(ung) + minmax(dang)) / 3,
        "StaticB_minmax": (minmax(res) + minmax(high) + minmax(dang)) / 3,
        "RuntimeA_minmax": (minmax(logs) + minmax(hosts) + minmax(mb)) / 3,
        "RuntimeB_minmax": (minmax(logs) + minmax(mb)) / 2,
        "StaticB_pct": (percentile_rank(res) + percentile_rank(high) + percentile_rank(dang)) / 3,
        "RuntimeB_pct": (percentile_rank(logs) + percentile_rank(mb)) / 2,
        "StaticB_madlog": (robust_mad_scale(res) + robust_mad_scale(high) + robust_mad_scale(dang)) / 3,
        "RuntimeB_madlog": (robust_mad_scale(logs) + robust_mad_scale(mb)) / 2,
    }
    variants["FinalAA"] = 0.5 * variants["StaticA_minmax"] + 0.5 * variants["RuntimeA_minmax"]
    variants["FinalBB"] = 0.5 * variants["StaticB_minmax"] + 0.5 * variants["RuntimeB_minmax"]

    rows = []
    for i, a in enumerate(apps):
        rec = {"app": a["app"], "pkg": a["pkg"]}
        for k, v in variants.items():
            rec[k] = float(v[i])
        rows.append(rec)
    write_csv(SCORES / "score_variants.csv", rows)

    S = variants["StaticB_minmax"]
    R = variants["RuntimeB_minmax"]
    names = [a["app"] for a in apps]
    n = len(apps)
    crosses = []
    for i in range(n):
        for j in range(i + 1, n):
            den = (S[i] - S[j]) - (R[i] - R[j])
            if abs(den) < 1e-12:
                continue
            w = (R[j] - R[i]) / den
            if 0.0 < w < 1.0:
                crosses.append(
                    {
                        "w": float(w),
                        "app_i": names[i],
                        "app_j": names[j],
                        "S_i": float(S[i]),
                        "R_i": float(R[i]),
                        "S_j": float(S[j]),
                        "R_j": float(R[j]),
                        "formula": "w=(Rj-Ri)/((Si-Sj)-(Ri-Rj))",
                        "tolerance": 1e-12,
                    }
                )
    crosses.sort(key=lambda r: r["w"])
    write_csv(SCORES / "weight_crossings.csv", crosses)

    ws = np.linspace(0, 1, 2001)
    perms = []
    seen = set()
    region_rows = []
    last = None
    for w in ws:
        sc = w * S + (1 - w) * R
        order = tuple(np.argsort(-sc))
        if order not in seen:
            seen.add(order)
            top3 = [names[k] for k in order[:3]]
            region_rows.append({"w_left": float(w), "top3": ", ".join(top3), "perm": ",".join(str(k) for k in order)})
            if last is not None:
                region_rows[-2]["w_right"] = float(w)
            last = order
            perms.append(order)
    if region_rows:
        region_rows[-1]["w_right"] = 1.0
    write_csv(SCORES / "rank_regions.csv", region_rows)

    rank_range = []
    grid = np.linspace(0, 1, 11)
    for i, name in enumerate(names):
        ranks = []
        for w in grid:
            sc = w * S + (1 - w) * R
            ranks.append(int(np.argsort(np.argsort(-sc))[i]) + 1)
        rank_range.append({"app": name, "min_rank": min(ranks), "max_rank": max(ranks), "span": max(ranks) - min(ranks)})

    md = SCORES / "constructed_score_stress_test.md"
    md.write_text(
        "\n".join(
            [
                "# Internal constructed-score stress test",
                "",
                "These indices are **not** manuscript results, probabilities of harm, or validated risk scores.",
                "",
                "## Formulas (primary min-max variants)",
                "- Static A = mean(minmax(hm, ung, dang)) — alias-inflated.",
                "- Static B = mean(minmax(residual, high, dang)) — cohort-wide alias-title drop.",
                "- Runtime A = mean(minmax(log2 PPS, hosts, MB)) — mixes opposite geometries.",
                "- Runtime B = mean(minmax(log2 PPS, MB)) — intensity only.",
                "- Final AA = 0.5 StaticA + 0.5 RuntimeA; Final BB = 0.5 StaticB + 0.5 RuntimeB.",
                "",
                f"## Rank crossings of F(w)=w StaticB + (1-w) RuntimeB (minmax)",
                f"- crossings in (0,1): **{len(crosses)}**",
                f"- unique ranking regions on 2001-point grid: **{len(region_rows)}**",
                f"- earlier narrative claimed 32 crossings / 33 orderings on residual-static vs log2PPS-only; this file uses StaticB vs RuntimeB (PPS+MB).",
                "",
                "Also stored: percentile-rank and MAD-logistic variants in score_variants.csv.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (SCORES / "score_stability_report.md").write_text(
        "# Score stability\n\n"
        + "\n".join(f"- {r['app']}: ranks {r['min_rank']}–{r['max_rank']} (span {r['span']})" for r in rank_range)
        + "\n\nEncoding dependence is the intended diagnostic: top-3 membership changes with w.\n",
        encoding="utf-8",
    )
    return {"n_crossings_01": len(crosses), "n_regions": len(region_rows), "rank_range": rank_range}


def median_audit(apps: list[dict]) -> dict:
    rows = []
    for a in apps:
        rows.append(
            {
                "app": a["app"],
                "baseline_class": a["baseline_class"],
                "baseline_pps": a["bpps"],
                "interactive_pps": a["ipps"],
                "z_i": a["log_s"],
            }
        )
    rows.sort(key=lambda r: r["z_i"])
    zs = np.array([r["z_i"] for r in rows])
    med = float(np.median(zs))
    write_csv(OUT / "pps_shift_values.csv", rows)
    order = [r["app"] for r in rows]
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "median_functional_audit.md").write_text(
        "\n".join(
            [
                "# Median functional audit (smoothed PPS shift)",
                "",
                f"z_i = log2((I+1)/(B+1)); B = strict-idle median if that class exists, else QFG.",
                f"Sorted apps: {', '.join(order)}",
                f"8th of 15 (median app): **{order[7]}** z={rows[7]['z_i']:.6f} → formatted **{med:.2f}** (paper 3.39).",
                f"7th={order[6]} {rows[6]['z_i']:.6f}; 9th={order[8]} {rows[8]['z_i']:.6f}.",
                "",
                "Local derivative of the sample median is piecewise: while the order is fixed and n is odd,",
                "d median / d z_i = 1 for the current median observation and 0 otherwise.",
                "It is nondifferentiable at order crossings. Finite perturbations confirm this only inside",
                "a neighborhood that does not reorder the 8th order statistic.",
                "TikTok is the only QFG baseline fallback.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {"median": med, "median_app": order[7], "sorted": order}


def static_detector_audit(apps: list[dict]) -> None:
    static = {r["package_name"]: r for r in read_csv(INPUTS / "publication_static_app_metrics.csv")}
    findings = read_csv(INPUTS / "publication_static_finding_rows.csv")
    run_pkg = {s["contributing_static_run_id"]: pkg for pkg, s in static.items()}
    by_pkg = defaultdict(list)
    for f in findings:
        pkg = run_pkg.get(f["run_id"])
        if pkg:
            by_pkg[pkg].append(f)
    conc = []
    variants = []
    for a in apps:
        fs = by_pkg[a["pkg"]]
        hm = [f for f in fs if f["severity"] in ("High", "Medium")]
        fam = Counter(f["detector"] for f in hm)
        titles = Counter(f["title"] for f in hm)
        shares = np.array(list(fam.values()), float)
        shares = shares / shares.sum() if shares.size else shares
        H = float(-(shares * np.log(shares)).sum()) if shares.size else 0.0
        hhi = float((shares**2).sum()) if shares.size else 0.0
        top_fam, top_n = fam.most_common(1)[0] if fam else ("", 0)
        top_t, top_tn = titles.most_common(1)[0] if titles else ("", 0)
        conc.append(
            {
                "app": a["app"],
                "n_hm": len(hm),
                "n_findings": len(fs),
                "n_detectors": len(fam),
                "n_unique_titles": len(titles),
                "top_detector": top_fam,
                "top_detector_n": top_n,
                "top_detector_share": top_n / len(hm) if hm else 0,
                "top_title": top_t,
                "top_title_n": top_tn,
                "shannon_entropy_nats": H,
                "hhi": hhi,
                "unique_components_recoverable": "UNKNOWN: finding rows are not unique component IDs; component CSV is provider-scoped (n=171 cohort-wide)",
            }
        )
        no_alias = [f for f in hm if f["title"] != ALIAS_TITLE]
        no_ipc = [f for f in hm if f["detector"] != "ipc_components"]
        variants.append(
            {
                "app": a["app"],
                "published_hm_rows": len(hm),
                "dedup_unique_titles": len(titles),
                "alias_dropped_cohort_rule": len(no_alias),
                "leave_ipc_family_out": len(no_ipc),
            }
        )
    write_csv(OUT / "static_detector_concentration.csv", conc)
    write_csv(OUT / "static_metric_variants.csv", variants)
    (REPORTS / "static_measurement_audit.md").write_text(
        "# Static measurement audit\n\n"
        f"Cohort-wide alias title dropped: `{ALIAS_TITLE}`.\n"
        "955 unguarded-export findings = High/Medium rows whose title contains "
        "'without permission' or 'weak guard'. These are finding rows, not unique components.\n",
        encoding="utf-8",
    )


def load_disconnect() -> tuple[dict[str, set[str]], dict]:
    path = TRACKER / "disconnect_services.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    domain_cats: dict[str, set[str]] = defaultdict(set)
    for cat, entities in raw["categories"].items():
        for ent in entities:
            for _name, hosts_by_url in ent.items():
                for _url, hosts in hosts_by_url.items():
                    for h in hosts:
                        domain_cats[h.lower().rstrip(".")].add(cat)
    man = {
        "repository": DISCONNECT_REPO,
        "commit": DISCONNECT_COMMIT,
        "source_file": "services.json",
        "source_path": str(path),
        "source_sha256": sha256_file(path),
        "retrieval_timestamp_utc": "2026-08-14T16:20:22Z",
        "license": "CC BY-NC-SA 4.0 (Disconnect, Inc.)",
        "list_format": "JSON categories -> entities -> homepage -> hostname list",
        "categories": sorted(raw["categories"].keys()),
        "unique_normalized_domains": len(domain_cats),
        "match_rule": "host==d or host.endswith('.'+d); no substring match",
        "primary_tracking_categories": sorted(TRACKING_CATS),
        "content_category_note": "Disconnect Content often includes CDNs; reported separately from tracking-oriented categories",
    }
    dump_json(TRACKER / "disconnect_manifest.json", man)
    return domain_cats, man


def match_host(host: str, domain_cats: dict[str, set[str]]) -> set[str]:
    """host==d or host.endswith('.'+d). Do not match a bare TLD suffix."""
    host = host.lower().rstrip(".")
    cats: set[str] = set()
    parts = host.split(".")
    for i in range(len(parts)):
        cand = ".".join(parts[i:])
        if "." not in cand and cand != host:
            continue
        if cand in domain_cats:
            cats |= domain_cats[cand]
    return cats


def tracker_audit(apps: list[dict], domain_cats: dict[str, set[str]]) -> dict[str, float]:
    runs = read_csv(INPUTS / "publication_dynamic_run_metrics.csv")
    dom = read_csv(INPUTS / "publication_dynamic_domain_rows.csv")
    int_runs = [r for r in runs if r["evidence_class"] == "interactive"]
    hosts_by_run: dict[str, set[str]] = defaultdict(set)
    for row in dom:
        hosts_by_run[row["dynamic_run_id"]].add(row["domain"].lower().rstrip("."))
    per_host = []
    seen_hosts = set()
    for r in int_runs:
        for h in hosts_by_run.get(r["dynamic_run_id"], set()):
            if (r["package"], h) in seen_hosts:
                continue
            seen_hosts.add((r["package"], h))
            cats = match_host(h, domain_cats)
            track = sorted(c for c in cats if c in TRACKING_CATS)
            per_host.append(
                {
                    "package": r["package"],
                    "hostname": h,
                    "matched_any": bool(cats),
                    "matched_tracking_oriented": bool(track),
                    "categories": "|".join(sorted(cats)),
                    "tracking_oriented_categories": "|".join(track),
                }
            )
    write_csv(OUT / "tracker_matches_per_hostname.csv", per_host)

    per_run = []
    for r in int_runs:
        hs = hosts_by_run.get(r["dynamic_run_id"], set())
        m_any = {h for h in hs if match_host(h, domain_cats)}
        m_tr = {h for h in hs if any(c in TRACKING_CATS for c in match_host(h, domain_cats))}
        per_run.append(
            {
                "dynamic_run_id": r["dynamic_run_id"],
                "package": r["package"],
                "app": r["app"],
                "n_retained": len(hs),
                "n_match_any": len(m_any),
                "n_match_tracking_oriented": len(m_tr),
                "prop_tracking_oriented": (len(m_tr) / len(hs)) if hs else "",
                "zero_retained_status": "zero_retained_names" if not hs else "has_retained_names",
            }
        )
    write_csv(OUT / "tracker_matches_per_run.csv", per_run)

    frac = {}
    per_app = []
    for a in apps:
        rs = [x for x in per_run if x["package"] == a["pkg"]]
        union = set()
        t_union = set()
        for x in rs:
            rid = x["dynamic_run_id"]
            hs = hosts_by_run.get(rid, set())
            union |= hs
            t_union |= {h for h in hs if any(c in TRACKING_CATS for c in match_host(h, domain_cats))}
        props = [x["prop_tracking_oriented"] for x in rs if x["prop_tracking_oriented"] != ""]
        counts = [x["n_match_tracking_oriented"] for x in rs]
        n_with = sum(1 for x in rs if x["n_retained"] > 0)
        med_prop = float(np.median(props)) if props else float("nan")
        frac[a["pkg"]] = med_prop if props else float("nan")
        cats = Counter()
        for h in t_union:
            for c in match_host(h, domain_cats):
                if c in TRACKING_CATS:
                    cats[c] += 1
        per_app.append(
            {
                "app": a["app"],
                "package": a["pkg"],
                "interactive_run_count": len(rs),
                "runs_with_retained_hostnames": n_with,
                "runs_with_zero_retained": len(rs) - n_with,
                "median_retained_hostname_count": a["idom"],
                "distinct_retained_interactive_hostnames": len(union),
                "distinct_tracker_associated_hostnames": len(t_union),
                "median_per_run_tracker_count": float(np.median(counts)) if counts else "",
                "median_per_run_tracker_proportion": med_prop if props else "",
                "tracker_categories": "|".join(f"{k}:{v}" for k, v in cats.most_common()),
                "unmatched_retained": "|".join(sorted(union - t_union)),
            }
        )
    write_csv(OUT / "tracker_matches_per_app.csv", per_app)

    n_int = len(int_runs)
    n_with_rows = sum(1 for r in int_runs if hosts_by_run.get(r["dynamic_run_id"]))
    summary = {
        "interactive_runs_total": n_int,
        "interactive_runs_with_retained_hostname_rows": n_with_rows,
        "interactive_runs_zero_retained": n_int - n_with_rows,
        "zero_retained_interpretation": "domain_count=0 and no top_dns/top_sni rows: zero retained names, not missing extraction",
        "cohort_distinct_interactive_hostnames": len({h["hostname"] for h in per_host}),
        "cohort_distinct_tracking_oriented_matches": len(
            {h["hostname"] for h in per_host if h["matched_tracking_oriented"]}
        ),
        "interpretation": "tracker-associated infrastructure; not confirmed tracking, leakage, exfiltration, or malice",
    }
    dump_json(OUT / "tracker_cohort_summary.json", summary)
    (REPORTS / "tracker_analysis.md").write_text(
        "# Disconnect tracker association (interactive retained DNS/SNI)\n\n"
        f"Pinned `{DISCONNECT_COMMIT}`.\n\n"
        f"Interactive runs: {n_int}; with retained hostname rows: {n_with_rows}; "
        f"zero retained names: {n_int - n_with_rows}.\n\n"
        "Match rule: `host==d` or `host.endswith('.'+d)`.\n\n"
        "Primary reported matches use tracking-oriented Disconnect categories "
        "(Advertising, Analytics, Social, Fingerprinting*, Cryptomining, Email*, ConsentManagers). "
        "Content/Anti-fraud are recorded in per-hostname categories but not counted in the primary fraction.\n\n"
        "**Tracker association ≠ leakage.**\n",
        encoding="utf-8",
    )
    return frac


def posture_and_confidence(apps: list[dict], tfrac: dict[str, float]) -> None:
    runs = read_csv(INPUTS / "publication_dynamic_run_metrics.csv")
    by = defaultdict(lambda: defaultdict(list))
    for r in runs:
        by[r["package"]][r["evidence_class"]].append(r)
    hm_med = float(np.median([a["hm"] for a in apps]))
    host_med = float(np.median([a["idom"] for a in apps]))
    matrix = []
    conf = []
    for a in apps:
        ints = by[a["pkg"]].get("interactive", [])
        pps = np.array([fnum(r["packets_per_second"]) for r in ints], float)
        dur = np.array([fnum(r["duration"]) for r in ints], float)
        cv_pps = float(pps.std(ddof=1) / pps.mean()) if pps.size > 1 and pps.mean() else float("nan")
        cv_dur = float(dur.std(ddof=1) / dur.mean()) if dur.size > 1 and dur.mean() else float("nan")
        hs = "static-heavy" if a["hm"] >= hm_med and a["idom"] < host_med else ""
        rt = "runtime-intense" if a["log_s"] >= float(np.median([x["log_s"] for x in apps])) else ""
        tf = tfrac.get(a["pkg"], float("nan"))
        tr = "tracker-associated" if np.isfinite(tf) and tf >= 0.25 else ""
        elev = "cross-layer elevated" if a["hm"] >= hm_med and a["idom"] >= host_med else ""
        div = "cross-layer divergent" if (a["hm"] >= hm_med) != (a["idom"] >= host_med) else ""
        depth = "limited runtime depth" if a["nint"] <= 1 else ""
        warnings = []
        if a["nint"] <= 1:
            warnings.append("n_interactive=1")
        if a["idom"] == 0:
            warnings.append("zero_retained_hosts_with_possible_traffic")
        if np.isfinite(cv_pps) and cv_pps > 1:
            warnings.append("high_interactive_pps_cv")
        labels = [x for x in (hs, rt, tr, elev, div, depth) if x]
        matrix.append(
            {
                "app": a["app"],
                "static_hm": a["hm"],
                "static_residual": a["residual"],
                "static_hhi_placeholder": "",
                "dangerous_permissions": a["dang"],
                "unguarded_export_findings": a["ung"],
                "smoothed_log2_pps": a["log_s"],
                "interactive_pps": a["ipps"],
                "interactive_bytes_per_second": a["ibps"],
                "retained_hosts": a["idom"],
                "tracker_associated_hostname_fraction": tf if np.isfinite(tf) else "",
                "n_idle": a["nidle"],
                "n_qfg": a["nqfg"],
                "n_int": a["nint"],
                "relative_descriptors": "|".join(labels),
                "measurement_warnings": "|".join(warnings),
            }
        )
        conf.append(
            {
                "app": a["app"],
                "n_strict_idle": a["nidle"],
                "n_qfg": a["nqfg"],
                "n_interactive": a["nint"],
                "interactive_pps_cv": cv_pps if np.isfinite(cv_pps) else "",
                "interactive_duration_cv": cv_dur if np.isfinite(cv_dur) else "",
                "hostname_availability": "present" if a["nint"] and a["idom"] == a["idom"] else "unknown",
                "low_confidence_flag": a["nint"] <= 1 or a["nidle"] == 0,
                "note": "confidence qualifies interpretation; it is not a risk score",
            }
        )
    # fill HHI from detector file if present
    conc_path = OUT / "static_detector_concentration.csv"
    if conc_path.exists():
        hhi = {r["app"]: r["hhi"] for r in read_csv(conc_path)}
        for row in matrix:
            row["static_hhi_placeholder"] = hhi.get(row["app"], "")
            row["static_concentration_hhi"] = row.pop("static_hhi_placeholder")
    write_csv(OUT / "risk_posture_matrix.csv", matrix)
    write_csv(OUT / "evidence_confidence.csv", conf)
    (REPORTS / "risk_posture_interpretation.md").write_text(
        "# Risk-posture matrix (internal interpretation)\n\n"
        "Relative descriptors only: static-heavy, runtime-intense, tracker-associated, "
        "cross-layer elevated, cross-layer divergent, limited runtime depth.\n\n"
        "Do not read as safe/critical/exploitable/highest true risk.\n",
        encoding="utf-8",
    )


def manuscript_language() -> None:
    (REPORTS / "manuscript_risk_language.md").write_text(
        """# Candidate manuscript language (not inserted)

## Abstract
One use of **privacy and security risk posture**.

## Introduction
Risk denotes evidence-supported exposure to conditions that may enable privacy or security harm, rather than a calibrated probability of exploitation or realized harm.

## Methodology
Static indicators characterize potential exposure. Runtime indicators characterize behavior observed during controlled execution. Tracker association, when reported, identifies communication with infrastructure independently classified as tracking-related. The layers are not collapsed into a composite risk score.

## Discussion
Disagreement between static exposure and observed runtime behavior is itself risk-relevant: low observed activity does not negate a broad packaged surface, and high runtime activity does not by itself establish exploitation.

## Limitations
Tracker-associated hostnames identify infrastructure context only; they do not reveal encrypted payload contents or demonstrate private-data leakage.

## Conclusion
Together, the evidence layers provide an auditable characterization of app-level privacy and security risk posture while preserving the distinction between potential exposure and observed runtime behavior.
""",
        encoding="utf-8",
    )


def main() -> None:
    for d in (OUT, FIG, SCORES, REPORTS, VALIDATION, TRACKER):
        d.mkdir(parents=True, exist_ok=True)
    versions = {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "matplotlib": getattr(__import__("matplotlib"), "__version__", None),
        "seed": SEED,
        "n_boot": N_BOOT,
        "n_perm": N_PERM,
        "generated_utc": utc_now(),
    }
    rng_sp = np.random.default_rng(SEED)
    rng_dc = np.random.default_rng(SEED + 1)
    rng_w = np.random.default_rng(SEED + 2)

    apps, meta = load_apps()
    sp = spearman_audit(apps, rng_sp)
    dc = dcor_audit(apps, rng_dc)
    wass = wasserstein_audit(apps, rng_w)
    domain_cats, dman = load_disconnect()
    tfrac = tracker_audit(apps, domain_cats)
    hull = hull_audit(apps, tfrac)
    cop = copula_audit(apps)
    par = pareto_front(apps, tfrac)
    scores = score_stress(apps)
    med = median_audit(apps)
    static_detector_audit(apps)
    posture_and_confidence(apps, tfrac)
    manuscript_language()

    summary = {
        "versions": versions,
        "inputs": json.loads((INPUTS / "INPUT_SHA256.json").read_text()),
        "metric_definitions": meta,
        "spearman": sp,
        "distance_correlation_pairs": [{k: r[k] for k in ("pair", "dcor", "p_plus_one", "bh_q_among_6_pairs")} for r in dc],
        "wasserstein_idle_int_pps_run_pooled": next(
            r for r in wass["cohort"] if r["field"] == "pps" and r["from"] == "strict_idle" and r["to"] == "interactive"
        ),
        "convex_hull_vertices_hm_hosts": hull["hm_vs_hosts"]["vertices"],
        "copula_masses": {k: cop[k] for k in ("UU", "UL", "LU", "LL", "on_median_rank", "sum")},
        "score_crossings": scores["n_crossings_01"],
        "score_regions": scores["n_regions"],
        "median_pps_shift": med,
        "disconnect": {k: dman[k] for k in ("commit", "source_sha256", "unique_normalized_domains", "license")},
        "tracker_summary_path": str(OUT / "tracker_cohort_summary.json"),
        "withdraw": [
            "jackknife normal CI for Spearman (unusable; leaves [-1,1])",
            "copula 0.20/0.20/0.20/0.20 as a complete partition (omitted on-median mass)",
            "constructed Final Risk Score as a cybersecurity measurement",
        ],
    }
    dump_json(OUT / "advanced_math_results.json", summary)

    (REPORTS / "advanced_math_reconciliation.md").write_text(
        "# Advanced-math reconciliation\n\n"
        f"Generated {versions['generated_utc']} with numpy {versions['numpy']}, scipy {versions['scipy']}.\n\n"
        f"## Spearman (paper pairing)\n"
        f"- n=15 rho={sp['n15']['rho']:.10f} p={sp['n15']['p']:.10f}\n"
        f"- n=14 no Snapchat rho={sp['n14_no_snapchat']['rho']:.10f} p={sp['n14_no_snapchat']['p']:.10f}\n"
        f"- most influential LOO: {sp['most_influential_loo']}\n"
        f"- jackknife usable: {sp['jackknife_usable']}\n"
        f"- bootstrap percentile 95% CI: {sp['bootstrap']['percentile_ci_95']}\n"
        f"- BCa 95% CI: {sp['bootstrap']['bca_ci_95']}\n",
        encoding="utf-8",
    )
    print("Wrote", ROOT)
    print("Spearman n15", sp["n15"])
    print("Spearman n14", sp["n14_no_snapchat"])
    print("Disconnect domains", dman["unique_normalized_domains"])
    print("Score crossings", scores["n_crossings_01"], "regions", scores["n_regions"])
    print("Median z", med)


if __name__ == "__main__":
    main()
