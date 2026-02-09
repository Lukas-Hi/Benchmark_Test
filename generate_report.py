#!/usr/bin/env python3
"""
Entscheider-Benchmark – HTML Report Generator
Copyright (c) 2026 Gerald T. Pögl – Hunter-ID MemoryBlock BG FlexCo
HID: HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46

Generates a self-contained HTML report from benchmark results.
Usage: python generate_report.py results/run_YYYYMMDD_HHMMSS
"""

import csv
import sys
import base64
import io
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


# ============================================================
# Data Loading
# ============================================================

def load_data(run_dir: Path) -> list[dict]:
    """Load aggregated_stats.csv, parse numeric fields."""
    csv_path = run_dir / "aggregated_stats.csv"
    if not csv_path.exists():
        print(f"Fehler: {csv_path} nicht gefunden.")
        sys.exit(1)

    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for r in reader:
            for key in r:
                if key not in ("model_name", "model_id", "provider", "task_id", "task_title"):
                    try:
                        r[key] = float(r[key])
                    except (ValueError, TypeError):
                        r[key] = 0.0
            rows.append(r)
    return rows


def filter_successful(rows: list[dict]) -> list[dict]:
    """Filter out rows with 0 successful runs (A5_N/A6_N failures)."""
    return [r for r in rows if r["num_successful"] > 0]


def get_models(rows: list[dict]) -> list[str]:
    """Get unique model names in order of appearance."""
    seen = []
    for r in rows:
        if r["model_name"] not in seen:
            seen.append(r["model_name"])
    return seen


def get_tasks(rows: list[dict]) -> list[str]:
    """Get unique task IDs."""
    seen = []
    for r in rows:
        if r["task_id"] not in seen:
            seen.append(r["task_id"])
    return seen


# ============================================================
# Chart Helpers
# ============================================================

MODEL_COLORS = {
    "Claude Haiku 4.5": "#6bb7c7",
    "Claude Sonnet 4.5": "#e8915a",
    "Claude Opus 4.5": "#7b68ae",
    "Claude Opus 4.6": "#c0392b",
}

def get_color(model: str) -> str:
    return MODEL_COLORS.get(model, "#888888")


def fig_to_base64(fig) -> str:
    """Convert matplotlib figure to base64-encoded SVG."""
    buf = io.BytesIO()
    fig.savefig(buf, format="svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def setup_chart_style():
    """Set consistent chart styling."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linestyle": "--",
    })


# ============================================================
# Chart Functions
# ============================================================

def chart_np_delta(rows: list[dict], models: list[str]) -> str:
    """N/P Token-Delta: grouped bar chart."""
    setup_chart_style()
    fig, ax = plt.subplots(figsize=(10, 5))

    # Compute average tokens for N and P per model
    n_tokens = {}
    p_tokens = {}
    for model in models:
        n_vals = [r["output_tokens_mean"] for r in rows
                  if r["model_name"] == model and "_N" in r["task_id"]
                  and r["num_successful"] > 0]
        p_vals = [r["output_tokens_mean"] for r in rows
                  if r["model_name"] == model and "_P" in r["task_id"]
                  and r["num_successful"] > 0]
        n_tokens[model] = sum(n_vals) / len(n_vals) if n_vals else 0
        p_tokens[model] = sum(p_vals) / len(p_vals) if p_vals else 0

    x = np.arange(len(models))
    width = 0.35

    bars_n = ax.bar(x - width/2, [n_tokens[m] for m in models], width,
                    label="Normal (N)", color="#b0b0b0", edgecolor="white")
    bars_p = ax.bar(x + width/2, [p_tokens[m] for m in models], width,
                    label="Power (P)", color=[get_color(m) for m in models],
                    edgecolor="white")

    # Add delta labels
    for i, m in enumerate(models):
        if n_tokens[m] > 0:
            delta = p_tokens[m] / n_tokens[m]
            ax.annotate(f"{delta:.1f}x",
                        xy=(x[i] + width/2, p_tokens[m]),
                        xytext=(0, 8), textcoords="offset points",
                        ha="center", fontweight="bold", fontsize=12,
                        color=get_color(m))

    ax.set_ylabel("Output-Tokens (Durchschnitt)")
    ax.set_title("N/P Token-Delta: Wie viel holt Prompt-Kompetenz heraus?",
                 fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace("Claude ", "") for m in models])
    ax.legend(loc="upper left")
    ax.set_ylim(0, max(p_tokens.values()) * 1.25)

    return fig_to_base64(fig)


def chart_latency(rows: list[dict], models: list[str]) -> str:
    """Latency comparison: N vs P grouped bars per task."""
    setup_chart_style()

    tasks_n = sorted(set(r["task_id"] for r in rows
                         if "_N" in r["task_id"] and r["num_successful"] > 0))
    tasks_p = sorted(set(r["task_id"] for r in rows
                         if "_P" in r["task_id"] and r["num_successful"] > 0))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    # N tasks
    x = np.arange(len(tasks_n))
    width = 0.8 / len(models)
    for i, model in enumerate(models):
        vals = []
        for t in tasks_n:
            match = [r for r in rows if r["model_name"] == model and r["task_id"] == t]
            vals.append(match[0]["latency_mean"] if match and match[0]["num_successful"] > 0 else 0)
        ax1.bar(x + i * width, vals, width, label=model.replace("Claude ", ""),
                color=get_color(model), edgecolor="white")

    ax1.set_title("Latenz – Normal (N)", fontweight="bold")
    ax1.set_ylabel("Sekunden")
    ax1.set_xticks(x + width * (len(models) - 1) / 2)
    ax1.set_xticklabels([t.split("_")[0] for t in tasks_n], rotation=45, ha="right")
    ax1.legend(fontsize=8)

    # P tasks
    x = np.arange(len(tasks_p))
    for i, model in enumerate(models):
        vals = []
        for t in tasks_p:
            match = [r for r in rows if r["model_name"] == model and r["task_id"] == t]
            vals.append(match[0]["latency_mean"] if match and match[0]["num_successful"] > 0 else 0)
        ax2.bar(x + i * width, vals, width, label=model.replace("Claude ", ""),
                color=get_color(model), edgecolor="white")

    ax2.set_title("Latenz – Power (P)", fontweight="bold")
    ax2.set_xticks(x + width * (len(models) - 1) / 2)
    ax2.set_xticklabels([t.split("_")[0] for t in tasks_p], rotation=45, ha="right")

    fig.suptitle("Latenz-Vergleich nach Aufgabe und Variante",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    return fig_to_base64(fig)


def chart_tokens(rows: list[dict], models: list[str]) -> str:
    """Token output comparison: N vs P per model (stacked by task)."""
    setup_chart_style()
    fig, ax = plt.subplots(figsize=(10, 5))

    # Average over all P-tasks per model
    data = {}
    for model in models:
        n_avg = np.mean([r["output_tokens_mean"] for r in rows
                         if r["model_name"] == model and "_N" in r["task_id"]
                         and r["num_successful"] > 0]) if any(
            r["model_name"] == model and "_N" in r["task_id"]
            and r["num_successful"] > 0 for r in rows) else 0
        p_avg = np.mean([r["output_tokens_mean"] for r in rows
                         if r["model_name"] == model and "_P" in r["task_id"]
                         and r["num_successful"] > 0]) if any(
            r["model_name"] == model and "_P" in r["task_id"]
            and r["num_successful"] > 0 for r in rows) else 0
        data[model] = (n_avg, p_avg)

    x = np.arange(len(models))
    width = 0.35

    ax.bar(x - width/2, [data[m][0] for m in models], width,
           label="Normal (N)", color="#b0b0b0", edgecolor="white")
    ax.bar(x + width/2, [data[m][1] for m in models], width,
           label="Power (P)", color=[get_color(m) for m in models], edgecolor="white")

    ax.set_ylabel("Output-Tokens (Durchschnitt)")
    ax.set_title("Token-Output: Normal vs. Power",
                 fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace("Claude ", "") for m in models])
    ax.legend()

    return fig_to_base64(fig)


def chart_consistency_heatmap(rows: list[dict], models: list[str]) -> str:
    """Consistency heatmap: CV% per model x task."""
    setup_chart_style()

    successful = [r for r in rows if r["num_successful"] > 0]
    tasks = []
    for r in successful:
        if r["task_id"] not in tasks:
            tasks.append(r["task_id"])

    matrix = np.full((len(models), len(tasks)), np.nan)
    for i, model in enumerate(models):
        for j, task in enumerate(tasks):
            match = [r for r in successful
                     if r["model_name"] == model and r["task_id"] == task]
            if match:
                matrix[i, j] = match[0]["response_length_cv"]

    fig, ax = plt.subplots(figsize=(12, 4))

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "cv", ["#27ae60", "#f1c40f", "#e74c3c"], N=256)
    im = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=0, vmax=20)

    ax.set_xticks(range(len(tasks)))
    ax.set_xticklabels([t.replace("_", "\n") for t in tasks],
                       fontsize=8, rotation=45, ha="right")
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels([m.replace("Claude ", "") for m in models])

    # Annotate cells
    for i in range(len(models)):
        for j in range(len(tasks)):
            val = matrix[i, j]
            if not np.isnan(val):
                color = "white" if val > 12 else "black"
                ax.text(j, i, f"{val:.1f}%", ha="center", va="center",
                        fontsize=9, color=color, fontweight="bold")

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("CV (%)")
    ax.set_title("Konsistenz-Heatmap (CV% – niedriger = besser)",
                 fontsize=13, fontweight="bold", pad=15)
    fig.tight_layout()
    return fig_to_base64(fig)


def chart_task_profile(rows: list[dict], models: list[str]) -> str:
    """Task profile: horizontal bars showing tokens per P-task per model."""
    setup_chart_style()

    p_tasks = sorted(set(r["task_id"] for r in rows
                         if "_P" in r["task_id"] and r["num_successful"] > 0))
    task_labels = [t.replace("_P", "").replace("_", " ").replace("A", "A", 1)
                   for t in p_tasks]

    fig, ax = plt.subplots(figsize=(10, 6))
    y = np.arange(len(p_tasks))
    height = 0.8 / len(models)

    for i, model in enumerate(models):
        vals = []
        for t in p_tasks:
            match = [r for r in rows if r["model_name"] == model and r["task_id"] == t]
            vals.append(match[0]["output_tokens_mean"] if match and match[0]["num_successful"] > 0 else 0)
        ax.barh(y + i * height, vals, height,
                label=model.replace("Claude ", ""),
                color=get_color(model), edgecolor="white")

    ax.set_yticks(y + height * (len(models) - 1) / 2)
    ax.set_yticklabels(task_labels)
    ax.set_xlabel("Output-Tokens")
    ax.set_title("Task-Profil: Output-Tokens pro Aufgabe (Power-Variante)",
                 fontsize=13, fontweight="bold", pad=15)
    ax.legend(loc="lower right", fontsize=9)
    ax.invert_yaxis()
    fig.tight_layout()
    return fig_to_base64(fig)


def chart_scatter(rows: list[dict], models: list[str]) -> str:
    """Latency vs Tokens scatter plot."""
    setup_chart_style()
    fig, ax = plt.subplots(figsize=(10, 6))

    for model in models:
        model_rows = [r for r in rows
                      if r["model_name"] == model and r["num_successful"] > 0]
        latencies = [r["latency_mean"] for r in model_rows]
        tokens = [r["output_tokens_mean"] for r in model_rows]
        labels = [r["task_id"] for r in model_rows]

        ax.scatter(latencies, tokens, label=model.replace("Claude ", ""),
                   color=get_color(model), s=80, alpha=0.8, edgecolors="white")

        for lat, tok, lbl in zip(latencies, tokens, labels):
            short = lbl.split("_")[0] + ("N" if "_N" in lbl else "P")
            ax.annotate(short, (lat, tok), fontsize=7, alpha=0.6,
                        xytext=(4, 4), textcoords="offset points")

    ax.set_xlabel("Latenz (Sekunden)")
    ax.set_ylabel("Output-Tokens")
    ax.set_title("Effizienz: Latenz vs. Token-Output",
                 fontsize=13, fontweight="bold", pad=15)
    ax.legend()
    fig.tight_layout()
    return fig_to_base64(fig)


# ============================================================
# Data Analysis Helpers
# ============================================================

def compute_np_deltas(rows: list[dict], models: list[str]) -> dict:
    """Compute N/P token delta per model."""
    deltas = {}
    for model in models:
        n_vals = [r["output_tokens_mean"] for r in rows
                  if r["model_name"] == model and "_N" in r["task_id"]
                  and r["num_successful"] > 0]
        p_vals = [r["output_tokens_mean"] for r in rows
                  if r["model_name"] == model and "_P" in r["task_id"]
                  and r["num_successful"] > 0]
        n_avg = sum(n_vals) / len(n_vals) if n_vals else 0
        p_avg = sum(p_vals) / len(p_vals) if p_vals else 0
        deltas[model] = {
            "n_avg": round(n_avg),
            "p_avg": round(p_avg),
            "delta": round(p_avg / n_avg, 1) if n_avg > 0 else 0,
        }
    return deltas


def compute_latency_ranking(rows: list[dict], models: list[str]) -> list[tuple]:
    """Rank models by average P-task latency."""
    ranking = []
    for model in models:
        p_lats = [r["latency_mean"] for r in rows
                  if r["model_name"] == model and "_P" in r["task_id"]
                  and r["num_successful"] > 0]
        avg = sum(p_lats) / len(p_lats) if p_lats else 999
        ranking.append((model, round(avg, 1)))
    return sorted(ranking, key=lambda x: x[1])


def compute_consistency_ranking(rows: list[dict], models: list[str]) -> list[tuple]:
    """Rank models by average CV%."""
    ranking = []
    for model in models:
        cvs = [r["response_length_cv"] for r in rows
               if r["model_name"] == model and r["num_successful"] > 0
               and r["response_length_cv"] > 0]
        avg = sum(cvs) / len(cvs) if cvs else 999
        ranking.append((model, round(avg, 1)))
    return sorted(ranking, key=lambda x: x[1])


def compute_total_stats(rows: list[dict]) -> dict:
    """Compute total benchmark statistics."""
    total_ok = sum(r["num_successful"] for r in rows)
    total_fail = sum(r["num_failed"] for r in rows)
    total_tokens = sum(r["output_tokens_mean"] * r["num_successful"]
                       for r in rows if r["num_successful"] > 0)
    models = get_models(rows)
    tasks = get_tasks(rows)
    return {
        "models": len(models),
        "tasks": len(set(t.rsplit("_", 1)[0] for t in tasks)),
        "variants": len(tasks),
        "runs": 10,
        "total_ok": int(total_ok),
        "total_fail": int(total_fail),
        "total_tokens": int(total_tokens),
    }


# ============================================================
# HTML Template
# ============================================================

def build_html(run_dir: Path, rows: list[dict]) -> str:
    """Build complete HTML report."""
    models = get_models(rows)
    stats = compute_total_stats(rows)
    deltas = compute_np_deltas(rows, models)
    lat_rank = compute_latency_ranking(rows, models)
    con_rank = compute_consistency_ranking(rows, models)

    # Generate all charts
    svg_np_delta = chart_np_delta(rows, models)
    svg_latency = chart_latency(rows, models)
    svg_tokens = chart_tokens(rows, models)
    svg_heatmap = chart_consistency_heatmap(rows, models)
    svg_task_profile = chart_task_profile(rows, models)
    svg_scatter = chart_scatter(rows, models)

    run_name = run_dir.name
    run_date = datetime.now().strftime("%d.%m.%Y")

    # Build delta table rows
    delta_rows_html = ""
    for m in models:
        d = deltas[m]
        delta_class = "delta-high" if d["delta"] >= 2.0 else "delta-low"
        delta_rows_html += f"""
        <tr>
            <td><span class="model-dot" style="background:{get_color(m)}"></span>{m}</td>
            <td class="num">{d['n_avg']:,}</td>
            <td class="num">{d['p_avg']:,}</td>
            <td class="num {delta_class}"><strong>{d['delta']}x</strong></td>
        </tr>"""

    # Build latency ranking rows
    lat_rows_html = ""
    for i, (m, lat) in enumerate(lat_rank):
        lat_rows_html += f"""
        <tr>
            <td>{i+1}.</td>
            <td><span class="model-dot" style="background:{get_color(m)}"></span>{m}</td>
            <td class="num">{lat}s</td>
        </tr>"""

    # Build consistency ranking rows
    con_rows_html = ""
    for i, (m, cv) in enumerate(con_rank):
        badge = "cv-green" if cv < 5 else ("cv-yellow" if cv < 15 else "cv-red")
        con_rows_html += f"""
        <tr>
            <td>{i+1}.</td>
            <td><span class="model-dot" style="background:{get_color(m)}"></span>{m}</td>
            <td class="num"><span class="{badge}">{cv}%</span></td>
        </tr>"""

    # Build full data table
    full_table_html = ""
    for r in rows:
        if r["num_successful"] > 0:
            cv_class = "cv-green" if r["response_length_cv"] < 5 else (
                "cv-yellow" if r["response_length_cv"] < 15 else "cv-red")
            full_table_html += f"""
            <tr>
                <td>{r['model_name']}</td>
                <td>{r['task_id']}</td>
                <td class="num">{int(r['num_successful'])}/{int(r['num_runs'])}</td>
                <td class="num">{r['latency_mean']:.1f}s</td>
                <td class="num">{int(r['output_tokens_mean']):,}</td>
                <td class="num"><span class="{cv_class}">{r['response_length_cv']:.1f}%</span></td>
            </tr>"""

    # Determine key findings for executive summary
    lowest_delta_model = min(deltas, key=lambda m: deltas[m]["delta"])
    highest_delta_model = max(deltas, key=lambda m: deltas[m]["delta"])
    fastest_model = lat_rank[0][0]
    most_consistent = con_rank[0][0]

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Entscheider-Benchmark Report – Anthropic-Familie</title>
<style>
:root {{
    --primary: #1a1a2e;
    --accent: #e8915a;
    --accent2: #7b68ae;
    --text: #2c3e50;
    --text-light: #7f8c8d;
    --bg: #f8f9fa;
    --card: #ffffff;
    --border: #e9ecef;
    --green: #27ae60;
    --yellow: #f39c12;
    --red: #e74c3c;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    font-family: -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: var(--text);
    background: var(--bg);
    line-height: 1.6;
}}

.header {{
    background: linear-gradient(135deg, var(--primary) 0%, #16213e 100%);
    color: white;
    padding: 3rem 2rem;
    text-align: center;
}}

.header h1 {{
    font-size: 2.2rem;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}}

.header .subtitle {{
    font-size: 1.1rem;
    opacity: 0.85;
    margin-bottom: 1.5rem;
}}

.header .meta {{
    display: flex;
    justify-content: center;
    gap: 2rem;
    flex-wrap: wrap;
    font-size: 0.85rem;
    opacity: 0.7;
}}

.header .meta span {{
    background: rgba(255,255,255,0.1);
    padding: 0.3rem 0.8rem;
    border-radius: 4px;
}}

.container {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 1.5rem;
}}

.section {{
    background: var(--card);
    border-radius: 12px;
    padding: 2rem;
    margin: 1.5rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border: 1px solid var(--border);
}}

.section h2 {{
    font-size: 1.5rem;
    color: var(--primary);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--accent);
    display: inline-block;
}}

.section h3 {{
    font-size: 1.15rem;
    color: var(--primary);
    margin: 1.5rem 0 0.5rem;
}}

.chart-container {{
    text-align: center;
    margin: 1.5rem 0;
    overflow-x: auto;
}}

.chart-container img {{
    max-width: 100%;
    height: auto;
}}

.interpretation {{
    background: #f0f4f8;
    border-left: 4px solid var(--accent);
    padding: 1.2rem 1.5rem;
    margin: 1.5rem 0;
    border-radius: 0 8px 8px 0;
}}

.interpretation h4 {{
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--accent);
    margin-bottom: 0.3rem;
}}

.interpretation p {{
    margin-bottom: 0.8rem;
    font-size: 0.95rem;
}}

.interpretation p:last-child {{
    margin-bottom: 0;
}}

.summary-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}}

.summary-card {{
    background: linear-gradient(135deg, var(--primary) 0%, #16213e 100%);
    color: white;
    padding: 1.2rem;
    border-radius: 10px;
    text-align: center;
}}

.summary-card .number {{
    font-size: 2rem;
    font-weight: 700;
    margin: 0.3rem 0;
}}

.summary-card .label {{
    font-size: 0.8rem;
    opacity: 0.8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
    font-size: 0.9rem;
}}

th {{
    background: var(--primary);
    color: white;
    padding: 0.7rem 1rem;
    text-align: left;
    font-weight: 600;
}}

td {{
    padding: 0.6rem 1rem;
    border-bottom: 1px solid var(--border);
}}

tr:hover {{
    background: #f8f9fa;
}}

.num {{
    text-align: right;
    font-variant-numeric: tabular-nums;
}}

.model-dot {{
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
}}

.delta-high {{
    color: var(--green);
}}

.delta-low {{
    color: var(--red);
}}

.cv-green {{
    background: #d4efdf;
    color: #1e8449;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
}}

.cv-yellow {{
    background: #fdebd0;
    color: #b7950b;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
}}

.cv-red {{
    background: #fadbd8;
    color: #922b21;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
}}

.warning-box {{
    background: #fef9e7;
    border: 1px solid #f9e79f;
    border-left: 4px solid var(--yellow);
    padding: 1rem 1.2rem;
    border-radius: 0 8px 8px 0;
    margin: 0.8rem 0;
}}

.warning-box strong {{
    color: #b7950b;
}}

.exec-summary {{
    background: linear-gradient(135deg, #f8f9fa 0%, #e8f4fd 100%);
    border: 1px solid #bee5eb;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin: 1.5rem 0;
}}

.exec-summary ul {{
    list-style: none;
    padding: 0;
}}

.exec-summary li {{
    padding: 0.5rem 0;
    padding-left: 1.5rem;
    position: relative;
    font-size: 1.05rem;
}}

.exec-summary li::before {{
    content: "\\2192";
    position: absolute;
    left: 0;
    color: var(--accent);
    font-weight: bold;
}}

.method-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 0.8rem;
    margin: 1rem 0;
}}

.method-item {{
    background: var(--bg);
    padding: 0.8rem 1rem;
    border-radius: 8px;
    border: 1px solid var(--border);
    text-align: center;
}}

.method-item .val {{
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--primary);
}}

.method-item .desc {{
    font-size: 0.8rem;
    color: var(--text-light);
}}

.fazit-box {{
    background: linear-gradient(135deg, var(--primary) 0%, #16213e 100%);
    color: white;
    padding: 2rem;
    border-radius: 12px;
    margin: 1.5rem 0;
}}

.fazit-box h3 {{
    color: var(--accent);
    margin-bottom: 0.5rem;
}}

.fazit-box p {{
    opacity: 0.9;
    margin-bottom: 0.8rem;
}}

.footer {{
    text-align: center;
    padding: 2rem;
    color: var(--text-light);
    font-size: 0.8rem;
    border-top: 1px solid var(--border);
    margin-top: 2rem;
}}

.chart-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}}

@media (max-width: 768px) {{
    .header h1 {{ font-size: 1.5rem; }}
    .chart-grid {{ grid-template-columns: 1fr; }}
    .container {{ padding: 0 0.8rem; }}
    .section {{ padding: 1.2rem; }}
}}
</style>
</head>
<body>

<!-- ===== HEADER ===== -->
<div class="header">
    <h1>Entscheider-Benchmark v3.0</h1>
    <p class="subtitle">Wie gut performen KI-Modelle bei strategischen Fuehrungsaufgaben?</p>
    <div class="meta">
        <span>Anthropic-Familie (4 Modelle)</span>
        <span>{stats['total_ok']} API-Calls</span>
        <span>10 Runs | Temp 0</span>
        <span>Run: {run_name}</span>
    </div>
</div>

<div class="container">

<!-- ===== EXECUTIVE SUMMARY ===== -->
<div class="section">
    <h2>Executive Summary</h2>
    <div class="exec-summary">
        <ul>
            <li><strong>Prompt-Kompetenz-Effekt variiert dramatisch:</strong>
                {highest_delta_model} zeigt {deltas[highest_delta_model]['delta']}x mehr Output mit Power-Prompts,
                waehrend {lowest_delta_model} nur {deltas[lowest_delta_model]['delta']}x erreicht &ndash;
                das Modell schreibt bereits ohne Anleitung ausfuehrlich.</li>
            <li><strong>Schnellstes Modell:</strong> {fastest_model} mit {lat_rank[0][1]}s Durchschnittslatenz
                &ndash; ueber {round(lat_rank[-1][1] / lat_rank[0][1], 1)}x schneller als {lat_rank[-1][0]} ({lat_rank[-1][1]}s).</li>
            <li><strong>Hoechste Konsistenz:</strong> {most_consistent} mit CV {con_rank[0][1]}%.
                Alle Modelle im gelben Bereich (5&ndash;15%) &ndash; keines erreicht den gruenen Bereich (&lt;5%) im Schnitt.</li>
            <li><strong>Anomalie:</strong> Claude Opus 4.6 zeigt bei Szenario-Analyse (A4_N) einen
                Variationskoeffizienten von 26% (rot) &ndash; ungewoehnlich hohe Schwankungen ohne strukturierten Prompt.</li>
        </ul>
    </div>
</div>

<!-- ===== METHODIK ===== -->
<div class="section">
    <h2>Methodik</h2>
    <p>Der Entscheider-Benchmark misst, wie gut LLMs bei realen Fuehrungsaufgaben performen. Jede Aufgabe
       wird in zwei Varianten getestet: <strong>Normal (N)</strong> &ndash; ein Prompt wie ihn ein Geschaeftsfuehrer
       tippen wuerde &ndash; und <strong>Power (P)</strong> &ndash; ein optimierter Prompt mit System-Prompt,
       Guardrails und expliziten Anforderungen. Das Delta zwischen N und P ist die eigentliche Messgrösse.</p>
    <div class="method-grid">
        <div class="method-item"><div class="val">{stats['tasks']}</div><div class="desc">Aufgaben</div></div>
        <div class="method-item"><div class="val">N + P</div><div class="desc">Varianten</div></div>
        <div class="method-item"><div class="val">{stats['runs']}</div><div class="desc">Wiederholungen</div></div>
        <div class="method-item"><div class="val">Temp 0</div><div class="desc">Reproduzierbarkeit</div></div>
        <div class="method-item"><div class="val">{stats['models']}</div><div class="desc">Modelle</div></div>
        <div class="method-item"><div class="val">{stats['total_ok']}</div><div class="desc">Erfolgreiche Calls</div></div>
    </div>
    <p style="font-size:0.85rem;color:var(--text-light);margin-top:1rem;">
        <strong>Aufgaben:</strong> A1 Entscheidungsvorlage | A2 Strategische Zusammenfassung |
        A3 Kritisches Hinterfragen | A4 Szenario-Analyse | A5 Widerspruchserkennung | A6 Zahlenanalyse<br>
        <strong>Audit-Trail:</strong> Exakter Prompt, Raw-API-Response und SHA-256-Checksummen werden pro Request archiviert.
    </p>
</div>

<!-- ===== N/P-DELTA (KERNMETRIK) ===== -->
<div class="section">
    <h2>Kernmetrik: N/P Token-Delta</h2>
    <p>Die zentrale Frage: <strong>Wie viel holt professionelles Prompt-Engineering aus einem Modell heraus?</strong></p>

    <div class="chart-container">
        <img src="data:image/svg+xml;base64,{svg_np_delta}" alt="N/P Delta Chart">
    </div>

    <table>
        <thead>
            <tr><th>Modell</th><th class="num">Normal (N)</th><th class="num">Power (P)</th><th class="num">Delta</th></tr>
        </thead>
        <tbody>{delta_rows_html}</tbody>
    </table>

    <div class="interpretation">
        <h4>Befund</h4>
        <p>Drei von vier Modellen (Haiku, Sonnet, Opus 4.5) zeigen einen klaren Prompt-Kompetenz-Effekt:
           Power-Prompts generieren 2,2&ndash;2,5x mehr Output-Tokens. Opus 4.6 ist der Ausreisser mit nur 1,1x.</p>
        <h4>Erklaerung</h4>
        <p>Claude Opus 4.6 hat einen deutlich ausfuehrlicheren Default-Stil: Bereits ohne System-Prompt und
           Strukturvorgaben produziert es durchschnittlich 1.714 Tokens &ndash; doppelt so viel wie Opus 4.5 (833 tok).
           Der Power-Prompt bringt bei Opus 4.6 kaum zusaetzlichen Output, weil das Modell bereits &bdquo;von sich aus&ldquo;
           umfassend antwortet.</p>
        <h4>Relevanz fuer Entscheider</h4>
        <p>Fuer Organisationen ohne Prompt-Engineering-Expertise ist Opus 4.6 attraktiv: Es liefert auch bei
           einfachen Prompts hochwertige, ausfuehrliche Antworten. Fuer Organisationen mit Prompt-Kompetenz
           bieten Opus 4.5 und Sonnet 4.5 das bessere Preis-Leistungs-Verhaeltnis, da sie im Normal-Modus
           sparsam sind und erst mit optimierten Prompts ihr volles Potenzial entfalten.</p>
    </div>
</div>

<!-- ===== LATENZ ===== -->
<div class="section">
    <h2>Latenz-Vergleich</h2>

    <div class="chart-container">
        <img src="data:image/svg+xml;base64,{svg_latency}" alt="Latency Chart">
    </div>

    <table>
        <thead><tr><th>Rang</th><th>Modell</th><th class="num">Ø Latenz (Power)</th></tr></thead>
        <tbody>{lat_rows_html}</tbody>
    </table>

    <div class="interpretation">
        <h4>Befund</h4>
        <p>Haiku 4.5 ist mit 19,3s im Schnitt klar das schnellste Modell &ndash; ueber 2x schneller als die
           Opus-Varianten (~40s). Ueberraschend: Sonnet 4.5 (Mid-Tier) ist mit 54,8s das langsamste Modell.</p>
        <h4>Erklaerung</h4>
        <p>Sonnets hohe Latenz entsteht primaer durch die Aufgaben A5 und A6: Bei A5 (Widerspruchserkennung)
           laeuft Sonnet konsistent in das max_tokens-Limit (4.096 Tokens) und benoetigt ~82s pro Request.
           Bei A6 (Zahlenanalyse) sind es ~81s. Diese beiden Aufgaben treiben den Schnitt nach oben.</p>
        <h4>Relevanz fuer Entscheider</h4>
        <p>Fuer zeitkritische Anwendungen (Chat-Interfaces, Echtzeit-Entscheidungen) ist Haiku klar die
           beste Wahl. Fuer Batch-Verarbeitung und Reports ist die Latenz weniger relevant &ndash; hier
           zaehlt die Qualitaet der Antworten.</p>
    </div>
</div>

<!-- ===== TOKEN-OUTPUT ===== -->
<div class="section">
    <h2>Token-Output im Vergleich</h2>

    <div class="chart-container">
        <img src="data:image/svg+xml;base64,{svg_tokens}" alt="Token Output Chart">
    </div>

    <div class="interpretation">
        <h4>Befund</h4>
        <p>Im Power-Modus produziert Sonnet 4.5 die meisten Tokens (Ø 2.636), gefolgt von Opus 4.5 (2.069),
           Haiku (1.926) und Opus 4.6 (1.875). Im Normal-Modus dominiert Opus 4.6 (1.714) deutlich.</p>
        <h4>Erklaerung</h4>
        <p>Mehr Tokens bedeuten nicht automatisch bessere Qualitaet. Sonnets hoher Token-Output bei A5 und A6
           ist teilweise ein Artefakt des max_tokens-Limits: Das Modell wuerde laenger schreiben, wird aber
           bei 4.096 Tokens abgeschnitten. Opus 4.6 erreicht vergleichbare inhaltliche Tiefe mit weniger
           Tokens im Power-Modus, weil es bereits im Normal-Modus ausfuehrlich strukturiert.</p>
        <h4>Relevanz fuer Entscheider</h4>
        <p>Token-Verbrauch korreliert direkt mit API-Kosten. Opus 4.6 ist im Power-Modus am effizientesten
           (wenigste Tokens), bietet aber gleichzeitig im Normal-Modus die ausfuehrlichsten Antworten.</p>
    </div>
</div>

<!-- ===== KONSISTENZ ===== -->
<div class="section">
    <h2>Konsistenz-Analyse</h2>
    <p>Der Variationskoeffizient (CV) misst, wie stark die Antwortlaenge zwischen 10 identischen Runs schwankt.
       Niedrigere Werte bedeuten hoehere Reproduzierbarkeit.</p>

    <div class="chart-container">
        <img src="data:image/svg+xml;base64,{svg_heatmap}" alt="Consistency Heatmap">
    </div>

    <table>
        <thead><tr><th>Rang</th><th>Modell</th><th class="num">Ø CV</th></tr></thead>
        <tbody>{con_rows_html}</tbody>
    </table>

    <div class="interpretation">
        <h4>Befund</h4>
        <p>Opus 4.5 und Sonnet 4.5 sind praktisch gleich konsistent (CV 6,8% vs. 6,9%). Opus 4.6 folgt
           mit 7,6%, Haiku bildet das Schlusslicht (9,4%). Kein Modell erreicht im Schnitt den gruenen
           Bereich (&lt;5%), obwohl Temperature 0 verwendet wird.</p>
        <h4>Erklaerung</h4>
        <p>Selbst bei Temperature 0 erzeugen LLMs keine identischen Outputs &ndash; GPU-Parallelisierung,
           Sampling-Rundungsfehler und Batch-Effekte fuehren zu natuerlicher Varianz. Die Power-Varianten
           zeigen generell niedrigere CVs als Normal-Varianten, weil strukturierte Prompts den Output-Raum
           einschraenken.</p>
        <h4>Relevanz fuer Entscheider</h4>
        <p>Fuer regulierte Branchen (Finance, Healthcare) ist Konsistenz entscheidend: Gleiche Eingabe sollte
           aehnliche Ausgabe produzieren. Die Power-Variante ist hier immer vorzuziehen, weil sie die Varianz
           systematisch reduziert.</p>
    </div>
</div>

<!-- ===== TASK-PROFIL ===== -->
<div class="section">
    <h2>Task-Profil</h2>
    <p>Wie verteilt sich der Output ueber die sechs Aufgabentypen?</p>

    <div class="chart-container">
        <img src="data:image/svg+xml;base64,{svg_task_profile}" alt="Task Profile Chart">
    </div>

    <div class="interpretation">
        <h4>Befund</h4>
        <p>A5 (Widerspruchserkennung) und A6 (Zahlenanalyse) generieren mit Abstand die meisten Tokens,
           weil sie Dokumentenanalyse erfordern. A1 (Entscheidungsvorlage) und A3 (Kritisches Hinterfragen)
           sind die kompaktesten Aufgaben.</p>
        <h4>Erklaerung</h4>
        <p>Aufgaben mit eingebetteten Dokumenten (A5, A6) erfordern systematische Analyse und produzieren
           entsprechend laengere Antworten. Freie Aufgaben (A1, A3) ohne Dokumentenkontext fuehren zu
           kuerzeren, fokussierteren Antworten.</p>
        <h4>Relevanz fuer Entscheider</h4>
        <p>Bei dokumentenintensiven Aufgaben (Vertragsanalyse, Due Diligence) sollte das Token-Limit
           grosszuegig bemessen werden. Bei kurzen Entscheidungsfragen genuegen kleinere Limits.</p>
    </div>
</div>

<!-- ===== SCATTER ===== -->
<div class="section">
    <h2>Effizienz: Latenz vs. Token-Output</h2>

    <div class="chart-container">
        <img src="data:image/svg+xml;base64,{svg_scatter}" alt="Scatter Chart">
    </div>

    <div class="interpretation">
        <h4>Befund</h4>
        <p>Haiku-Cluster (unten links): Schnell und kompakt. Sonnet-Ausreisser (oben rechts): A5_P und A6_P
           mit hoher Latenz und hohem Token-Output. Opus-Modelle bilden die Mitte.</p>
        <h4>Erklaerung</h4>
        <p>Die Effizienz-Grenze verlaeuft diagonal: Mehr Tokens kosten proportional mehr Zeit. Haiku ist
           die effizienteste Kombination (niedrigste Latenz pro Token), Sonnet die am wenigsten effiziente
           bei dokumentenintensiven Aufgaben.</p>
    </div>
</div>

<!-- ===== AUFFAELLIGKEITEN ===== -->
<div class="section">
    <h2>Auffaelligkeiten &amp; Limitationen</h2>

    <div class="warning-box">
        <strong>Opus 4.6 &ndash; A4_N Varianz (CV 26%)</strong><br>
        Die Szenario-Analyse ohne strukturierten Prompt erzeugt bei Opus 4.6 stark schwankende
        Antwortlaengen (2.290 &plusmn; 591 Tokens). Dies ist der einzige rote Wert im gesamten Benchmark.
        Moegliche Ursache: Opus 4.6 interpretiert die offene Aufgabenstellung unterschiedlich &ndash;
        mal als Kurzanalyse, mal als ausfuehrliches Szenario-Paper.
    </div>

    <div class="warning-box">
        <strong>Sonnet 4.5 &ndash; max_tokens bei A5_P (CV 0,6%)</strong><br>
        Sonnet produziert bei A5 (Widerspruchserkennung) exakt 4.096 Output-Tokens in allen 10 Runs.
        Der extrem niedrige CV (0,6%) signalisiert nicht Konsistenz, sondern ein Limit-Problem:
        Die Antworten werden abgeschnitten. Fuer A5 und A6 sollte max_tokens auf 8.192+ erhoht werden.
    </div>

    <div class="warning-box">
        <strong>A5_N / A6_N &ndash; 80 erwartete Fehler</strong><br>
        Die Normal-Varianten von A5 und A6 senden volle PDF-Dokumente (&gt;200k Tokens) als Kontext.
        Dies uebersteigt das Eingabe-Limit und fuehrt zu 100% Fehlern. Dies ist by design: Es demonstriert,
        dass Power-Prompts mit kuratierten Auszuegen notwendig sind.
    </div>

    <div class="warning-box">
        <strong>Temperature 0 ist nicht deterministisch</strong><br>
        Trotz Temperature 0 zeigen alle Modelle CV-Werte von 3&ndash;14%. Absolute Reproduzierbarkeit
        ist mit aktuellen LLM-APIs nicht erreichbar. Die 10 Runs quantifizieren diese natuerliche Varianz.
    </div>
</div>

<!-- ===== FAZIT ===== -->
<div class="section">
    <h2>Fazit &amp; Empfehlung</h2>

    <div class="fazit-box">
        <h3>Fuer Entscheider ohne Prompt-Expertise</h3>
        <p><strong>Claude Opus 4.6</strong> &ndash; Liefert auch mit einfachen Prompts ausfuehrliche,
           strukturierte Antworten (Delta nur 1,1x). Geringster Prompt-Engineering-Aufwand fuer gute Ergebnisse.</p>
    </div>

    <div class="fazit-box">
        <h3>Fuer Organisationen mit Prompt-Kompetenz</h3>
        <p><strong>Claude Opus 4.5</strong> &ndash; Beste Konsistenz (CV 6,8%), vernuenftiger Latenz (39,9s)
           und hoechster Delta-Effekt (2,5x). Belohnt professionelle Prompts am staerksten.</p>
    </div>

    <div class="fazit-box">
        <h3>Fuer zeitkritische Anwendungen</h3>
        <p><strong>Claude Haiku 4.5</strong> &ndash; 2x schneller als alles andere (19,3s).
           Ideal fuer Chat-Interfaces und Echtzeit-Entscheidungen, wenn Tiefenanalyse nicht noetig ist.</p>
    </div>

    <div class="fazit-box">
        <h3>Sonnet 4.5 &ndash; Einschraenkung</h3>
        <p>Trotz Mid-Tier-Positionierung das langsamste Modell (54,8s) mit max_tokens-Problemen bei
           komplexen Aufgaben. Fuer Entscheider-Aufgaben derzeit nicht die optimale Wahl.</p>
    </div>
</div>

<!-- ===== DETAIL-TABELLE ===== -->
<div class="section">
    <h2>Vollstaendige Datentabelle</h2>
    <div style="overflow-x:auto;">
    <table>
        <thead>
            <tr>
                <th>Modell</th>
                <th>Aufgabe</th>
                <th class="num">Runs</th>
                <th class="num">Latenz Ø</th>
                <th class="num">Tokens Ø</th>
                <th class="num">CV</th>
            </tr>
        </thead>
        <tbody>{full_table_html}</tbody>
    </table>
    </div>
</div>

</div>

<!-- ===== FOOTER ===== -->
<div class="footer">
    <p><strong>Entscheider-Benchmark v3.0</strong> | Gerald T. Poegl &ndash; Hunter-ID MemoryBlock BG FlexCo</p>
    <p>HID: HID-LINKEDIN-BENCHMARK-2026-02-06-ACTIVE-C4E8A1-CLO46</p>
    <p>Daten: {run_name} | Generiert: {datetime.now().strftime("%d.%m.%Y %H:%M")} UTC |
       Vollstaendiger Audit-Trail im Run-Verzeichnis verfuegbar</p>
</div>

</body>
</html>"""

    return html


# ============================================================
# Main
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_report.py <run_directory>")
        print("Beispiel: python generate_report.py results/run_20260207_144751")
        sys.exit(1)

    run_dir = Path(sys.argv[1])
    if not run_dir.exists():
        print(f"Fehler: {run_dir} existiert nicht.")
        sys.exit(1)

    print(f"Lade Daten aus: {run_dir}")
    rows = load_data(run_dir)
    if not rows:
        print("Keine Daten gefunden.")
        sys.exit(1)

    print(f"  {len(rows)} Datensaetze geladen")
    print(f"  Modelle: {', '.join(get_models(rows))}")

    print("Generiere Charts...")
    html = build_html(run_dir, rows)

    output_path = run_dir / "report.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"\nReport geschrieben: {output_path}")
    print(f"  Groesse: {output_path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
