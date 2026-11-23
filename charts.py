from collections import Counter
from datetime import datetime
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def create_category_chart(items, output_path):
    counts = Counter(x.get("category", "Other") for x in items)
    fig, ax = plt.subplots(figsize=(8, 3.8))
    if counts:
        labels, values = zip(*sorted(counts.items(), key=lambda x: x[1], reverse=True))
        ax.bar(labels, values)
        ax.set_ylabel("Number of headlines")
        ax.set_title("Headlines by category")
        ax.tick_params(axis="x", rotation=25)
        ax.grid(axis="y", alpha=.2)
    else:
        ax.text(.5, .5, "No headline data available", ha="center", va="center")
        ax.set_axis_off()
    fig.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)

def create_timeline_chart(items, output_path):
    counts = Counter()
    for item in items:
        value = item.get("published_at", "")
        try:
            day = datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
            counts[day] += 1
        except (ValueError, TypeError):
            continue
    fig, ax = plt.subplots(figsize=(8, 3.8))
    if counts:
        days = sorted(counts)
        ax.plot(days, [counts[d] for d in days], marker="o")
        ax.set_ylabel("Headlines")
        ax.set_title("Headlines by publication date")
        ax.tick_params(axis="x", rotation=30)
        ax.grid(alpha=.2)
    else:
        ax.text(.5, .5, "No date data available", ha="center", va="center")
        ax.set_axis_off()
    fig.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
