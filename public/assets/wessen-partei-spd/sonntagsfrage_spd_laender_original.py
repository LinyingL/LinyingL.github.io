"""
SPD in den Ländern: Landtagsumfragen vor der BTW 2025 vs. heute
Datenquelle: dawum.de API (https://api.dawum.de/)  —  Lizenz: ODC-ODbL

Dumbbell-Chart, FT-restrained. Befund: Seit der BTW 2025 verliert
vor allem die Bundespartei; die Landesverbände halten ihr Niveau.
"""

import os
import urllib.request
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, date, timedelta

# ── FT-restrained Stil ────────────────────────────────────────────────────────
BG, INK, INK_LITE, INK_FAINT = "#FBFAF7", "#1F1F1F", "#6B6B6B", "#9A9A9A"
NAVY, CORAL, GRID = "#1F4E79", "#C05746", "#E8E5DD"

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "axes.edgecolor": INK_LITE, "axes.labelcolor": INK, "axes.linewidth": 0.8,
    "xtick.color": INK_LITE, "ytick.color": INK,
    "xtick.labelsize": 9, "ytick.labelsize": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.spines.left": False, "axes.spines.bottom": True,
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "font.size": 10,
    "legend.frameon": False, "legend.fontsize": 9,
})

# ── Daten laden ───────────────────────────────────────────────────────────────
print("Lade Daten von dawum.de …")
with urllib.request.urlopen("https://api.dawum.de/", timeout=30) as resp:
    data = json.load(resp)

SPD_ID = "2"
LAND_NAMES = {                       # Parliament_ID -> Kurzname
    "1": "Baden-Württemberg", "2": "Bayern", "3": "Berlin",
    "4": "Brandenburg", "5": "Bremen", "6": "Hamburg", "7": "Hessen",
    "8": "Mecklenburg-Vorp.", "9": "Niedersachsen", "10": "NRW",
    "11": "Rheinland-Pfalz", "12": "Saarland", "13": "Sachsen",
    "14": "Sachsen-Anhalt", "15": "Schleswig-Holstein", "16": "Thüringen",
}

today = max(
    datetime.strptime(s["Date"], "%Y-%m-%d").date()
    for s in data["Surveys"].values()
)
BTW25 = date(2025, 2, 23)
# Ereignis-Stichtag: 1. Lesung des Rentenpakets im Bundestag (16.10.2025),
# Beginn des Rentenstreits, der die Koalition im Herbst 2025 lähmte
# (Verabschiedung erst 05.12.2025 gegen die Junge Gruppe der Union)
RENTENSTREIT = date(2025, 10, 16)
BASE_START, BASE_END = BTW25 + timedelta(days=1), RENTENSTREIT
CURR_START = RENTENSTREIT + timedelta(days=1)

SCOPES = dict(LAND_NAMES)
SCOPES["0"] = "Bund"                  # Bundestag als Vergleichszeile

base_vals = {pid: [] for pid in SCOPES}
curr_vals = {pid: [] for pid in SCOPES}

for s in data["Surveys"].values():
    pid = s.get("Parliament_ID")
    if pid not in SCOPES:
        continue
    r = s.get("Results", {})
    if SPD_ID not in r:
        continue
    d = datetime.strptime(s["Date"], "%Y-%m-%d").date()
    v = float(r[SPD_ID])
    if BASE_START <= d <= BASE_END:
        base_vals[pid].append(v)
    if d >= CURR_START:
        curr_vals[pid].append(v)

rows = []
for pid, name in SCOPES.items():
    if not base_vals[pid] or not curr_vals[pid]:
        print(f"  [übersprungen] {name}: keine ausreichenden Umfragen")
        continue
    rows.append((name,
                 float(np.mean(base_vals[pid])),
                 float(np.mean(curr_vals[pid])),
                 len(base_vals[pid]), len(curr_vals[pid])))

rows.sort(key=lambda x: x[2])        # aufsteigend -> höchster Wert oben
names = [r[0] for r in rows]
base  = np.array([r[1] for r in rows])
curr  = np.array([r[2] for r in rows])
y     = np.arange(len(rows))

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8.5, 7.0))
fig.subplots_adjust(left=0.21, right=0.95, top=0.86, bottom=0.09)

ax.set_axisbelow(True)
ax.xaxis.grid(True, color=GRID, linewidth=0.6)
ax.yaxis.grid(False)

# 5%-Hürde
ax.axvline(5, color=INK_LITE, lw=0.7, ls=":", alpha=0.55, zorder=1)
ax.text(5, len(rows) - 0.2, "5%-Hürde", fontsize=8.5, color=INK_LITE,
        ha="center", va="bottom", style="italic")

# Verbindungslinien + Punkte (Bund in Kontrastfarbe)
is_bund = np.array([n == "Bund" for n in names])
for yi, b, c, ib in zip(y, base, curr, is_bund):
    ax.plot([b, c], [yi, yi],
            color=CORAL if ib else INK_FAINT, lw=1.4 if ib else 1.2, zorder=2)
ax.scatter(base[~is_bund], y[~is_bund], s=42, color=BG, edgecolor=INK_FAINT,
           linewidth=1.4, zorder=3,
           label="BTW 2025 bis Rentenstreit (Okt 2025)")
ax.scatter(curr[~is_bund], y[~is_bund], s=46, color=NAVY, edgecolor=NAVY,
           zorder=4, label="seit dem Rentenstreit")
ax.scatter(base[is_bund], y[is_bund], s=42, color=BG, edgecolor=CORAL,
           linewidth=1.4, zorder=3)
ax.scatter(curr[is_bund], y[is_bund], s=46, color=CORAL, edgecolor=CORAL,
           zorder=4)

ax.set_yticks(y)
ax.set_yticklabels(names)
for tick, ib in zip(ax.get_yticklabels(), is_bund):
    if ib:
        tick.set_color(CORAL)
        tick.set_fontweight("bold")
ax.set_xlim(0, max(base.max(), curr.max()) * 1.12)
ax.set_xticks([0, 10, 20, 30, 40])
ax.set_xticklabels(["0%", "10%", "20%", "30%", "40%"])
ax.tick_params(axis="y", length=0)

# Die EINE Kernannotation (≤ 12 Wörter), dynamisch berechnet
n_stable = int(((curr - base) >= -1.0)[~is_bund].sum())
n_land   = int((~is_bund).sum())
ax.text(0.97, 0.06,
        f"{n_stable} von {n_land} Landesverbänden stabil oder im Plus",
        transform=ax.transAxes, fontsize=10, color=INK, weight="bold",
        ha="right", va="bottom")

ax.legend(loc="lower right", bbox_to_anchor=(0.97, 0.12), handletextpad=0.4)

# ── Titelblock + Quelle ───────────────────────────────────────────────────────
fig.text(0.06, 0.955,
         "SPD in den Ländern seit der Bundestagswahl 2025",
         fontsize=14, color=INK, weight="bold", ha="left")
fig.text(0.06, 0.92,
         "Seit der Wahl halten die meisten Landesverbände ihr Niveau.",
         fontsize=10, color=INK_LITE, ha="left")

fig.text(0.06, 0.02,
         f"Quelle: dawum.de (ODC-ODbL), Mittel aller Landtagsumfragen; "
         f"Stichtag: 1. Lesung Rentenpaket 16.10.2025",
         fontsize=8, color=INK_LITE, style="italic", ha="left", va="bottom")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "sonntagsfrage_spd_laender.png")
plt.savefig(out, dpi=160)
print(f"Gespeichert: {out}")
for n, b, c, nb, nc in sorted(rows, key=lambda r: r[2] - r[1]):
    flag = "  (!)" if min(nb, nc) < 3 else ""
    print(f"  {n:<20} {b:5.1f}% -> {c:5.1f}%  ({c-b:+.1f} Pp.)  "
          f"[n={nb}/{nc}]{flag}")
print("(!) = unter 3 Umfragen in einem Fenster — im Artikel als "
      "Datenlimitation ausweisen")