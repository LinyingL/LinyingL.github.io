"""
Sonntagsfrage: Links-/Rechtsblock und SPD-Anteil am Linksblock (2017–heute)
Datenquelle: dawum.de API (https://api.dawum.de/)  —  Lizenz: ODC-ODbL

Stil: FT/Reuters-restrained — die Grafik zeigt den Befund,
der Artikel liefert das Argument.
"""

import os
import urllib.request
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.transforms import blended_transform_factory
import numpy as np
from datetime import date, datetime

# ── FT-restrained Stil ────────────────────────────────────────────────────────
BG        = "#FBFAF7"
INK       = "#1F1F1F"
INK_LITE  = "#6B6B6B"
INK_FAINT = "#9A9A9A"
NAVY      = "#1F4E79"   # Linksblock
CORAL     = "#C05746"   # Rechtsblock / SPD-Akzent
SAGE      = "#6B8E5A"   # Grüne
GRID      = "#E8E5DD"
TINT_GRAY = "#E5E2DA"

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "axes.edgecolor": INK_LITE, "axes.labelcolor": INK, "axes.linewidth": 0.8,
    "xtick.color": INK_LITE, "ytick.color": INK_LITE,
    "xtick.labelsize": 9, "ytick.labelsize": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.spines.left": False, "axes.spines.bottom": True,
    "axes.grid": True, "axes.grid.axis": "y", "axes.axisbelow": True,
    "grid.color": GRID, "grid.linestyle": "-", "grid.linewidth": 0.6,
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "font.size": 10,
    "legend.frameon": False, "legend.fontsize": 9,
})

# ── Daten von API laden ───────────────────────────────────────────────────────
print("Lade Daten von dawum.de …")
with urllib.request.urlopen("https://api.dawum.de/", timeout=30) as resp:
    data = json.load(resp)

surveys = data["Surveys"]

# Party-IDs für Bundestagsumfragen (Parliament_ID = "0")
PARTY_IDS = {"spd": "2", "cducsu": "1", "gruene": "4",
             "fdp": "3", "afd": "7", "linke": "5", "bsw": "23"}

records = []
for s in surveys.values():
    if s.get("Parliament_ID") != "0":
        continue
    d = datetime.strptime(s["Date"], "%Y-%m-%d").date()
    r = s.get("Results", {})
    row = {"date": d}
    for name, pid in PARTY_IDS.items():
        row[name] = float(r[pid]) if pid in r else None
    if row["spd"] is not None:
        records.append(row)

records.sort(key=lambda x: x["date"])
print(f"  {len(records)} Bundestag-Umfragen geladen "
      f"({records[0]['date']} – {records[-1]['date']})")

# ── 14-Tage-Rollmittel ────────────────────────────────────────────────────────
WINDOW = 14
all_dates = [r["date"] for r in records]

def rolling_col(key):
    vals = [r[key] for r in records]
    out = []
    for i, d in enumerate(all_dates):
        cutoff = date.fromordinal(d.toordinal() - WINDOW)
        vs = [vals[j] for j in range(i + 1)
              if vals[j] is not None and all_dates[j] >= cutoff]
        out.append(sum(vs) / len(vs) if vs else np.nan)
    return np.array(out)

spd_a    = rolling_col("spd")
cducsu_a = rolling_col("cducsu")
gruene_a = rolling_col("gruene")
fdp_a    = rolling_col("fdp")
afd_a    = rolling_col("afd")
linke_a  = rolling_col("linke")
bsw_a    = np.nan_to_num(rolling_col("bsw"))   # BSW existiert erst ab 2023

links  = spd_a + gruene_a + linke_a + bsw_a
rechts = cducsu_a + fdp_a + afd_a

with np.errstate(divide="ignore", invalid="ignore"):
    spd_anteil    = np.where(links > 0, spd_a / links * 100, np.nan)
    gruene_anteil = np.where(links > 0, gruene_a / links * 100, np.nan)
    rest_anteil   = np.where(links > 0, (linke_a + bsw_a) / links * 100, np.nan)

x_start, x_end = date(2017, 1, 1), records[-1]["date"]

wahlen = [
    (date(2017, 9, 24), "BTW 2017"),
    (date(2021, 9, 26), "BTW 2021"),
    (date(2025, 2, 23), "BTW 2025"),
]

# ── Figure: zwei Panels ───────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(10, 8.2), sharex=True,
    gridspec_kw={"hspace": 0.32, "height_ratios": [1.15, 1.0]},
)
fig.subplots_adjust(left=0.07, right=0.93, top=0.86, bottom=0.09)

def event_lines(ax, with_labels):
    for xd, lbl in wahlen:
        ax.axvline(xd, color=INK_LITE, lw=0.7, ls=":", alpha=0.55, zorder=0)
        if with_labels:
            trans = blended_transform_factory(ax.transData, ax.transAxes)
            ax.text(xd, 0.97, lbl, transform=trans, fontsize=8.5,
                    color=INK_LITE, ha="center", va="top", style="italic")

def endpoint(ax, x, y, color, side="right"):
    sign, ha = (1, "left") if side == "right" else (-1, "right")
    ax.annotate(f"{y:.0f}", (x, y), xytext=(sign * 5, 0),
                textcoords="offset points", fontsize=9,
                color=color, weight="bold", ha=ha, va="center")

# ── Panel 1: Links- vs. Rechtsblock ──────────────────────────────────────────
ax1.plot(all_dates, links,  color=NAVY,  lw=2.2, label="Linksblock (SPD+Grüne+Linke+BSW)")
ax1.plot(all_dates, rechts, color=CORAL, lw=2.2, label="Rechtsblock (CDU/CSU+FDP+AfD)")
event_lines(ax1, with_labels=True)

endpoint(ax1, all_dates[-1], links[-1],  NAVY)
endpoint(ax1, all_dates[-1], rechts[-1], CORAL)

ax1.set_ylim(25, 70)
ax1.set_xlim(x_start, x_end)
ax1.set_yticks([30, 40, 50, 60])
ax1.set_yticklabels([f"{t}%" for t in [30, 40, 50, 60]])
ax1.legend(loc="lower left", ncol=1, handlelength=1.6)

# ── Panel 2: Anteile am Linksblock ───────────────────────────────────────────
ax2.stackplot(all_dates, spd_anteil, gruene_anteil, rest_anteil,
              labels=["SPD", "Grüne", "Linke + BSW"],
              colors=[CORAL, SAGE, TINT_GRAY], alpha=0.85, lw=0)
event_lines(ax2, with_labels=False)

# Endpunkt der SPD-Schicht (Anteil am Linksblock)
endpoint(ax2, all_dates[-1], spd_anteil[-1], "#8C3A2D")

# Die EINE Kernannotation der Grafik (≤ 12 Wörter)
ax2.text(date(2023, 6, 1), 84,
         f"SPD-Anteil am Linksblock fast halbiert: "
         f"{spd_anteil[0]:.0f}% → {spd_anteil[-1]:.0f}%",
         fontsize=10, color=INK, weight="bold", ha="center", va="center")

ax2.set_ylim(0, 100)
ax2.set_yticks([0, 25, 50, 75, 100])
ax2.set_yticklabels([f"{t}%" for t in [0, 25, 50, 75, 100]])
ax2.set_ylabel("Anteil am Linksblock", fontsize=9.5, color=INK_LITE)
ax2.legend(loc="lower left", ncol=3, handlelength=1.2, columnspacing=1.0)

ax2.xaxis.set_major_locator(mdates.YearLocator())
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

# ── Titelblock + Quelle ───────────────────────────────────────────────────────
fig.text(0.07, 0.955, "Sonntagsfrage: Linksblock, Rechtsblock, SPD-Anteil 2017–2026",
         fontsize=14, color=INK, weight="bold", ha="left")

last_update = data["Database"]["Last_Update"][:10]
fig.text(0.07, 0.02,
         f"Quelle: dawum.de (ODC-ODbL), 14-Tage-Rollmittel über alle Institute, ",
         fontsize=8, color=INK_LITE, style="italic", ha="left", va="bottom")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "sonntagsfrage_spd.png")
plt.savefig(out, dpi=160)
print(f"Gespeichert: {out}")
print(f"SPD-Anteil am Linksblock: {spd_anteil[0]:.0f}% (2017) → "
      f"{spd_anteil[-1]:.0f}% (heute)")