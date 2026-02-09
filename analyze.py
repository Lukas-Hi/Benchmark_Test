#!/usr/bin/env python3
"""
Entscheider-Benchmark: Analyse & Visualisierung
HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46
© Gerald Pögl – Hunter-ID MemoryBlock BG FlexCo

Liest aggregated_stats.csv aus einem Run-Verzeichnis und erzeugt Charts.

Usage:
    python analyze.py results/run_20260207_144751
    python analyze.py results/run_20260207_144751 --open
"""

import csv
import sys
import argparse
import subprocess
from pathlib import Path
from collections import defaultdict
from statistics import mean, stdev

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


# ============================================
# Color scheme
# ============================================
MODEL_COLORS = {
    "Claude Opus 4.6": "#6B4C9A",
    "Claude Opus 4.5": "#9B72CF",
    "Claude Sonnet 4.5": "#C49CDE",
    "Claude Haiku 4.5": "#DFC5F0",
    "GPT-5.2": "#2D7D46",
    "GPT-5.2 Pro": "#3FA35A",
    "GPT-5.2 Chat": "#7BC88C",
    "GPT-5.2-Codex": "#A8DDB5",
    "o1": "#1A6B52",
    "Gemini 3 Pro": "#C75533",
    "Gemini 2.5 Pro": "#E07B5A",
    "Gemini 2.5 Flash": "#F0A888",
    "Grok 4.1": "#2B5EA7",
    "Mistral Large 3": "#D4A017",
    "DeepSeek V3.2": "#8B4513",
    "DeepSeek R1": "#A0522D",
    "Llama 3.3 70B": "#555555",
}
DEFAULT_COLOR = "#888888"

TASK_LABELS = {
    "A1_Entscheidungsvorlage": "A1 Entscheidung",
    "A2_Strategische_Zusammenfassung": "A2 Zusammenfassung",
    "A3_Kritisches_Hinterfragen": "A3 Krit. Hinterfragen",
    "A4_Szenario_Analyse": "A4 Szenario",
    "A5_Widerspruchserkennung": "A5 Widerspruch",
    "A6_Zahlenanalyse": "A6 Zahlen",
}


def get_color(model_name):
    return MODEL_COLORS.get(model_name, DEFAULT_COLOR)


def load_csv(run_dir: Path) -> list[dict]:
    """Load aggregated_stats.csv from run directory."""
    fp = run_dir / "aggregated_stats.csv"
    if not fp.exists():
        print(f"Fehler: {fp} nicht gefunden.")
        sys.exit(1)
    with open(fp, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        return list(reader)


def task_base(task_id: str) -> str:
    """Strip _N or _P suffix to get base task name."""
    if task_id.endswith("_N") or task_id.endswith("_P"):
        return task_id[:-2]
    return task_id


def task_variant(task_id: str) -> str:
    """Get N or P variant."""
    if task_id.endswith("_N"):
        return "N"
    if task_id.endswith("_P"):
        return "P"
    return "?"


def short_label(task_id: str) -> str:
    """Short display label for task."""
    base = task_base(task_id)
    return TASK_LABELS.get(base, base)


def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


# ============================================
# Chart 1: Latenz-Vergleich N vs P (gruppiert)
# ============================================
def chart_latency_np(rows, out_dir):
    """Grouped bar chart: Latency N vs P per model, per task."""
    models = sorted(set(r["model_name"] for r in rows))
    tasks_base = sorted(set(task_base(r["task_id"]) for r in rows))

    # Build lookup: (model, task_base, variant) -> latency_mean
    lookup = {}
    for r in rows:
        key = (r["model_name"], task_base(r["task_id"]), task_variant(r["task_id"]))
        lookup[key] = safe_float(r["latency_mean"])

    fig, axes = plt.subplots(1, len(tasks_base), figsize=(4 * len(tasks_base), 6),
                              sharey=True)
    if len(tasks_base) == 1:
        axes = [axes]

    for ax, tb in zip(axes, tasks_base):
        x = np.arange(len(models))
        width = 0.35
        n_vals = [lookup.get((m, tb, "N"), 0) for m in models]
        p_vals = [lookup.get((m, tb, "P"), 0) for m in models]

        bars_n = ax.bar(x - width/2, n_vals, width, label="Normal (N)",
                        color="#90CAF9", edgecolor="#1565C0", linewidth=0.5)
        bars_p = ax.bar(x + width/2, p_vals, width, label="Power (P)",
                        color="#1565C0", edgecolor="#0D47A1", linewidth=0.5)

        ax.set_title(short_label(tb + "_N"), fontsize=10, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels([m.replace("Claude ", "C.").replace("GPT-", "G")
                           for m in models], rotation=45, ha="right", fontsize=7)
        ax.grid(axis="y", alpha=0.3)

    axes[0].set_ylabel("Latenz (Sekunden)", fontsize=10)
    axes[0].legend(loc="upper left", fontsize=8)
    fig.suptitle("Latenz-Vergleich: Normal vs. Power-Prompt", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "chart_latency_np.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  chart_latency_np.png")


# ============================================
# Chart 2: Token-Output N vs P (Delta-Analyse)
# ============================================
def chart_tokens_np(rows, out_dir):
    """Grouped bar chart: Output tokens N vs P per model."""
    models = sorted(set(r["model_name"] for r in rows))
    tasks_base = sorted(set(task_base(r["task_id"]) for r in rows))

    lookup = {}
    for r in rows:
        key = (r["model_name"], task_base(r["task_id"]), task_variant(r["task_id"]))
        lookup[key] = safe_float(r["output_tokens_mean"])

    # Aggregate across all tasks
    model_n_avg = {}
    model_p_avg = {}
    for m in models:
        n_vals = [lookup.get((m, tb, "N"), 0) for tb in tasks_base if lookup.get((m, tb, "N"), 0) > 0]
        p_vals = [lookup.get((m, tb, "P"), 0) for tb in tasks_base if lookup.get((m, tb, "P"), 0) > 0]
        model_n_avg[m] = mean(n_vals) if n_vals else 0
        model_p_avg[m] = mean(p_vals) if p_vals else 0

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(models))
    width = 0.35

    bars_n = ax.bar(x - width/2, [model_n_avg[m] for m in models], width,
                    label="Normal (N)", color="#FFCC80", edgecolor="#E65100", linewidth=0.5)
    bars_p = ax.bar(x + width/2, [model_p_avg[m] for m in models], width,
                    label="Power (P)", color="#E65100", edgecolor="#BF360C", linewidth=0.5)

    # Add ratio labels
    for i, m in enumerate(models):
        n = model_n_avg[m]
        p = model_p_avg[m]
        if n > 0:
            ratio = p / n
            ax.text(i, max(n, p) + 100, f"{ratio:.1f}x",
                    ha="center", fontsize=8, fontweight="bold", color="#BF360C")

    ax.set_ylabel("Output-Tokens (Ø über alle Aufgaben)", fontsize=10)
    ax.set_title("Token-Output: Normal vs. Power-Prompt\n(Zahl = P/N Ratio)",
                 fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=30, ha="right", fontsize=9)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "chart_tokens_np.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  chart_tokens_np.png")


# ============================================
# Chart 3: N/P Delta Heatmap
# ============================================
def chart_np_delta_heatmap(rows, out_dir):
    """Heatmap showing P/N token ratio per model x task."""
    models = sorted(set(r["model_name"] for r in rows))
    tasks_base = sorted(set(task_base(r["task_id"]) for r in rows))

    lookup = {}
    for r in rows:
        key = (r["model_name"], task_base(r["task_id"]), task_variant(r["task_id"]))
        lookup[key] = safe_float(r["output_tokens_mean"])

    data = np.zeros((len(models), len(tasks_base)))
    for i, m in enumerate(models):
        for j, tb in enumerate(tasks_base):
            n = lookup.get((m, tb, "N"), 0)
            p = lookup.get((m, tb, "P"), 0)
            data[i, j] = p / n if n > 0 else 0

    fig, ax = plt.subplots(figsize=(max(8, len(tasks_base) * 1.5), max(4, len(models) * 0.6)))
    im = ax.imshow(data, cmap="YlOrRd", aspect="auto", vmin=0,
                   vmax=max(data.max(), 5))

    ax.set_xticks(np.arange(len(tasks_base)))
    ax.set_yticks(np.arange(len(models)))
    ax.set_xticklabels([short_label(tb + "_N") for tb in tasks_base],
                       rotation=30, ha="right", fontsize=9)
    ax.set_yticklabels(models, fontsize=9)

    # Annotate cells
    for i in range(len(models)):
        for j in range(len(tasks_base)):
            val = data[i, j]
            if val > 0:
                color = "white" if val > 3 else "black"
                ax.text(j, i, f"{val:.1f}x", ha="center", va="center",
                        fontsize=8, fontweight="bold", color=color)
            else:
                ax.text(j, i, "–", ha="center", va="center",
                        fontsize=8, color="#999999")

    ax.set_title("N/P Token-Delta: Wie viel holt der Power-Prompt heraus?\n"
                 "(Höher = größerer Effekt von Prompt-Kompetenz)",
                 fontsize=12, fontweight="bold")
    fig.colorbar(im, ax=ax, label="P/N Ratio", shrink=0.8)
    fig.tight_layout()
    fig.savefig(out_dir / "chart_np_delta_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  chart_np_delta_heatmap.png")


# ============================================
# Chart 4: Konsistenz (CV) pro Modell
# ============================================
def chart_consistency(rows, out_dir):
    """Bar chart: Response length CV per model (lower = more consistent)."""
    models = sorted(set(r["model_name"] for r in rows))

    # Average CV across all tasks per model
    model_cvs = {}
    for m in models:
        cvs = [safe_float(r["response_length_cv"])
               for r in rows if r["model_name"] == m and safe_float(r["response_length_cv"]) > 0]
        model_cvs[m] = mean(cvs) if cvs else 0

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = []
    for m in models:
        cv = model_cvs[m]
        if cv < 5:
            colors.append("#4CAF50")   # green
        elif cv < 15:
            colors.append("#FF9800")   # orange
        else:
            colors.append("#F44336")   # red

    x = np.arange(len(models))
    bars = ax.bar(x, [model_cvs[m] for m in models], color=colors, edgecolor="white", linewidth=0.5)

    # Reference lines
    ax.axhline(y=5, color="#4CAF50", linestyle="--", alpha=0.5, label="Gut (<5%)")
    ax.axhline(y=15, color="#F44336", linestyle="--", alpha=0.5, label="Problematisch (>15%)")

    ax.set_ylabel("Variationskoeffizient (CV %)", fontsize=10)
    ax.set_title("Antwort-Konsistenz (Ø CV über alle Aufgaben)\nNiedriger = konsistenter bei Temp 0",
                 fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=30, ha="right", fontsize=9)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    for bar, m in zip(bars, models):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{model_cvs[m]:.1f}%", ha="center", fontsize=8, fontweight="bold")

    fig.tight_layout()
    fig.savefig(out_dir / "chart_consistency.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  chart_consistency.png")


# ============================================
# Chart 5: Aufgaben-Radar (Tokens pro Task)
# ============================================
def chart_task_profile(rows, out_dir):
    """Stacked horizontal bar: Token output per task per model (P-variant only)."""
    models = sorted(set(r["model_name"] for r in rows))
    p_rows = [r for r in rows if r["task_id"].endswith("_P")]
    tasks_p = sorted(set(r["task_id"] for r in p_rows))

    if not tasks_p:
        return

    fig, ax = plt.subplots(figsize=(12, max(4, len(models) * 0.5)))
    y = np.arange(len(models))
    height = 0.7
    left = np.zeros(len(models))

    task_colors = plt.cm.Set2(np.linspace(0, 1, len(tasks_p)))

    for tid, color in zip(tasks_p, task_colors):
        vals = []
        for m in models:
            match = [r for r in p_rows if r["model_name"] == m and r["task_id"] == tid]
            vals.append(safe_float(match[0]["output_tokens_mean"]) if match else 0)
        ax.barh(y, vals, height, left=left, label=short_label(tid), color=color,
                edgecolor="white", linewidth=0.3)
        left += np.array(vals)

    ax.set_yticks(y)
    ax.set_yticklabels(models, fontsize=9)
    ax.set_xlabel("Output-Tokens (Power-Prompt)", fontsize=10)
    ax.set_title("Aufgabenprofil: Token-Verteilung pro Modell (nur P-Varianten)",
                 fontsize=12, fontweight="bold")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "chart_task_profile.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  chart_task_profile.png")


# ============================================
# Chart 6: Latenz vs. Qualität (Scatter)
# ============================================
def chart_latency_vs_tokens(rows, out_dir):
    """Scatter: Latency vs output tokens per model (P-variants, sized by task)."""
    p_rows = [r for r in rows if r["task_id"].endswith("_P") and safe_float(r["output_tokens_mean"]) > 0]
    if not p_rows:
        return

    fig, ax = plt.subplots(figsize=(10, 7))

    for r in p_rows:
        m = r["model_name"]
        lat = safe_float(r["latency_mean"])
        tok = safe_float(r["output_tokens_mean"])
        color = get_color(m)
        ax.scatter(lat, tok, s=80, color=color, alpha=0.7, edgecolors="white", linewidth=0.5)

    # Legend with model names
    handles = []
    seen = set()
    for r in p_rows:
        m = r["model_name"]
        if m not in seen:
            seen.add(m)
            handles.append(plt.Line2D([0], [0], marker="o", color="w",
                                       markerfacecolor=get_color(m), markersize=8, label=m))
    ax.legend(handles=handles, fontsize=8, loc="upper left")

    ax.set_xlabel("Latenz (Sekunden)", fontsize=10)
    ax.set_ylabel("Output-Tokens", fontsize=10)
    ax.set_title("Latenz vs. Ausführlichkeit (Power-Prompts)\nJeder Punkt = 1 Aufgabe",
                 fontsize=12, fontweight="bold")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "chart_latency_vs_tokens.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  chart_latency_vs_tokens.png")


# ============================================
# Summary statistics text file
# ============================================
def write_summary(rows, out_dir):
    """Write a human-readable summary of key findings."""
    models = sorted(set(r["model_name"] for r in rows))
    tasks_base = sorted(set(task_base(r["task_id"]) for r in rows))

    lookup = {}
    for r in rows:
        key = (r["model_name"], task_base(r["task_id"]), task_variant(r["task_id"]))
        lookup[key] = {
            "tokens": safe_float(r["output_tokens_mean"]),
            "latency": safe_float(r["latency_mean"]),
            "cv": safe_float(r["response_length_cv"]),
            "successful": int(safe_float(r["num_successful"])),
            "failed": int(safe_float(r["num_failed"])),
        }

    lines = [
        "=" * 70,
        "ENTSCHEIDER-BENCHMARK – ANALYSE-ZUSAMMENFASSUNG",
        "=" * 70,
        "",
    ]

    # Total stats
    total_ok = sum(int(safe_float(r["num_successful"])) for r in rows)
    total_fail = sum(int(safe_float(r["num_failed"])) for r in rows)
    lines.append(f"Modelle: {len(models)} | Aufgaben: {len(tasks_base)} (N+P) | "
                 f"Requests: {total_ok} OK / {total_fail} Fehler")
    lines.append("")

    # P/N ratios per model
    lines.append("N/P TOKEN-DELTA (Ø über alle Aufgaben):")
    lines.append("-" * 50)
    for m in models:
        n_vals = [lookup.get((m, tb, "N"), {}).get("tokens", 0)
                  for tb in tasks_base if lookup.get((m, tb, "N"), {}).get("tokens", 0) > 0]
        p_vals = [lookup.get((m, tb, "P"), {}).get("tokens", 0)
                  for tb in tasks_base if lookup.get((m, tb, "P"), {}).get("tokens", 0) > 0]
        n_avg = mean(n_vals) if n_vals else 0
        p_avg = mean(p_vals) if p_vals else 0
        ratio = p_avg / n_avg if n_avg > 0 else 0
        lines.append(f"  {m:<25s} N: {n_avg:>7.0f} tok | P: {p_avg:>7.0f} tok | "
                     f"Delta: {ratio:.1f}x")
    lines.append("")

    # Latency ranking
    lines.append("LATENZ-RANKING (Ø über Power-Aufgaben):")
    lines.append("-" * 50)
    lat_avg = {}
    for m in models:
        lats = [lookup.get((m, tb, "P"), {}).get("latency", 0)
                for tb in tasks_base if lookup.get((m, tb, "P"), {}).get("latency", 0) > 0]
        lat_avg[m] = mean(lats) if lats else 0
    for rank, (m, lat) in enumerate(sorted(lat_avg.items(), key=lambda x: x[1]), 1):
        lines.append(f"  {rank}. {m:<25s} {lat:.1f}s")
    lines.append("")

    # Consistency ranking
    lines.append("KONSISTENZ-RANKING (Ø CV, niedriger = besser):")
    lines.append("-" * 50)
    cv_avg = {}
    for m in models:
        cvs = [safe_float(r["response_length_cv"])
               for r in rows if r["model_name"] == m and safe_float(r["response_length_cv"]) > 0]
        cv_avg[m] = mean(cvs) if cvs else 0
    for rank, (m, cv) in enumerate(sorted(cv_avg.items(), key=lambda x: x[1]), 1):
        marker = "OK" if cv < 5 else ("WARNUNG" if cv < 15 else "PROBLEM")
        lines.append(f"  {rank}. {m:<25s} CV {cv:.1f}% [{marker}]")
    lines.append("")

    # Failures
    failures = [(r["model_name"], r["task_id"], int(safe_float(r["num_failed"])))
                for r in rows if safe_float(r["num_failed"]) > 0]
    if failures:
        lines.append("FEHLER:")
        lines.append("-" * 50)
        for m, t, n in sorted(failures):
            lines.append(f"  {m} × {t}: {n} Fehler")
    lines.append("")

    text = "\n".join(lines)
    (out_dir / "analysis_summary.txt").write_text(text, encoding="utf-8")
    print(f"  analysis_summary.txt")
    print()
    print(text)


# ============================================
# Main
# ============================================
def main():
    p = argparse.ArgumentParser(description="Entscheider-Benchmark Analyse & Visualisierung")
    p.add_argument("run_dir", type=str, help="Pfad zum Run-Verzeichnis")
    p.add_argument("--open", action="store_true", help="Charts nach Erstellung öffnen")
    args = p.parse_args()

    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(f"Fehler: {run_dir} existiert nicht.")
        sys.exit(1)

    charts_dir = run_dir / "charts"
    charts_dir.mkdir(exist_ok=True)

    print(f"\nAnalyse: {run_dir}")
    print(f"Charts -> {charts_dir}\n")

    rows = load_csv(run_dir)
    if not rows:
        print("Keine Daten in aggregated_stats.csv.")
        sys.exit(1)

    print("Generiere Charts:")
    chart_latency_np(rows, charts_dir)
    chart_tokens_np(rows, charts_dir)
    chart_np_delta_heatmap(rows, charts_dir)
    chart_consistency(rows, charts_dir)
    chart_task_profile(rows, charts_dir)
    chart_latency_vs_tokens(rows, charts_dir)
    write_summary(rows, charts_dir)

    if args.open:
        for png in sorted(charts_dir.glob("*.png")):
            subprocess.Popen(["start", "", str(png)], shell=True)


if __name__ == "__main__":
    main()
