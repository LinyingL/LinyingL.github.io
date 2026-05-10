"""
Rebuild the three publish-ready figures to match the visual style of
LinyingL.github.io (see the Arbeit post). Key style traits:

  - Cream background (#FAF8F3)
  - Color palette: navy, coral, mustard, sage, with light tint regions
  - Inline labels (no detached legend boxes where avoidable)
  - Highlighted period bands with semi-transparent fills
  - Numeric callouts at endpoints
  - Top/right spines removed; light dotted horizontal grid
  - "© Linying Li" watermark bottom-right
  - Bold title, italic source line at bottom-left

Outputs (overwrite the previous _en versions):
  ../figures/two_layer_paradox_blog.png
  ../figures/transfer_structure_blog.png
  ../figures/revised_evidence_blog.png
"""

from pathlib import Path
HERE = Path(__file__).resolve().parent
FIG_DIR = HERE.parent / 'figures'
FIG_DIR.mkdir(exist_ok=True, parents=True)

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np


# ============================================================
# Visual style — modeled on LinyingL.github.io
# ============================================================
BG       = '#FAF8F3'   # cream
INK      = '#2A2A2A'   # near-black for body text
INK_LITE = '#666666'   # subtitle / caption color
NAVY     = '#1F4E79'   # primary data series (self-sufficiency, discretionary share)
CORAL    = '#B7472A'   # contrast/alternative series
MUSTARD  = '#B8860B'   # reference lines, annotations
SAGE     = '#7BA05B'   # accent / positive endpoint
PURPLE   = '#5D4E73'   # auxiliary
BROWN    = '#8B6F47'   # auxiliary
GRID     = '#D5D0C5'   # subtle grid

TINT_BLUE   = '#D6E2EE'   # light navy fill
TINT_CORAL  = '#F3D9CC'   # light coral fill
TINT_MUSTARD= '#F0E5C8'   # light mustard fill
TINT_GRAY   = '#E5E2DA'   # neutral

plt.rcParams.update({
    'figure.facecolor': BG,
    'axes.facecolor': BG,
    'savefig.facecolor': BG,
    'axes.edgecolor': INK_LITE,
    'axes.labelcolor': INK,
    'xtick.color': INK_LITE,
    'ytick.color': INK_LITE,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'axes.axisbelow': True,
    'grid.color': GRID,
    'grid.linestyle': ':',
    'grid.linewidth': 0.7,
    'grid.alpha': 0.8,
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Helvetica', 'Arial'],
    'font.size': 10,
    'axes.titlesize': 14,
    'axes.labelsize': 10,
    'legend.frameon': False,
    'legend.fontsize': 9,
})


def add_watermark(fig, ax=None, source=''):
    """Add bottom-right author watermark and bottom-left italic source line."""
    if source:
        fig.text(0.06, 0.025, source, fontsize=8, color=INK_LITE,
                 style='italic', ha='left', va='bottom')
    fig.text(0.97, 0.025, '© Linying Li', fontsize=8, color=INK_LITE,
             ha='right', va='bottom', alpha=0.7)


def add_title(fig, title, subtitle=None, y_title=0.96, y_sub=0.925):
    fig.text(0.06, y_title, title, fontsize=15, color=INK, weight='bold', ha='left')
    if subtitle:
        fig.text(0.06, y_sub, subtitle, fontsize=10, color=INK_LITE, style='italic', ha='left')


# ============================================================
# Embedded data (same as 04_make_english_charts.py)
# ============================================================
YEARS = list(range(2013, 2027))

SHARE_FREE = {2019:31.8,2020:31.2,2021:35.3,2022:33.6,2023:35.9,2024:37.4,
              2025:41.5,2026:41.7}
SELF_SUFF  = {2013:57.0,2014:57.7,2015:55.2,2016:54.4,2017:52.8,2018:52.0,
              2019:49.6,2020:47.6,2021:52.7,2022:48.3,2023:49.6,2024:48.9,
              2025:50.0,2026:49.2}
DEPEND     = {2013:39.6,2014:39.2,2015:36.6,2016:37.0,2017:37.6,2018:37.0,
              2019:36.5,2020:39.5,2021:39.0,2022:43.1,2023:43.5,2024:41.1,
              2025:41.7,2026:41.0}

SHARE_TAX     = {2013:10.5,2014:9.8,2015:9.1,2016:11.5,2017:12.3,2018:11.5,
                 2019:15.1,2020:13.5,2021:14.1,2022:12.2,2023:11.0,2024:12.1,
                 2025:12.2,2026:11.8}
SHARE_SHARED  = {2019:42.9,2020:38.7,2021:41.7,2022:37.5,2023:35.8,2024:37.4,
                 2025:37.3,2026:37.4}
SHARE_SPECIAL = {2013:38.8,2014:36.7,2015:39.2,2016:34.9,2017:33.6,2018:32.9,
                 2019:10.2,2020:16.5,2021: 9.0,2022:16.6,2023:17.3,2024:13.1,
                 2025: 9.0,2026: 9.0}
GENERAL_PRE19 = {2013:50.7,2014:53.5,2015:51.7,2016:53.6,2017:54.1,2018:55.6}

PROPERTY_PCT = {2013:15.13,2014:15.50,2015:14.37,2016:14.89,2017:16.17,
                2018:17.00,2019:17.67,2020:18.40,2021:17.76,2022:16.51,
                2023:14.85,2024:14.39}
LAND_SALES   = {2018:6.29,2019:7.06,2020:8.21,2021:8.49,2022:6.53,2023:5.66,2024:4.77}
CENTRAL_PT   = {2013:79.8,2014:80.0,2015:79.6,2016:82.1,2017:80.2,2018:81.5,
                2019:83.2,2020:100.5,2021:89.8,2022:102.2,2023:103.3,2024:99.9}


# ============================================================
# Figure 1: Two-layer paradox (the centerpiece)
# ============================================================
def fig_two_layer():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 9.5), sharex=True,
                                    gridspec_kw={'height_ratios': [1, 1.3], 'hspace': 0.30})

    # --- Top panel: discretionary share (only 2019+) ---
    xs_top = sorted(SHARE_FREE.keys())
    ys_top = [SHARE_FREE[y] for y in xs_top]

    # Budget-vs-actual zone shading
    ax1.axvspan(2024.5, 2026.5, color=TINT_MUSTARD, alpha=0.35, zorder=0)

    ax1.plot(xs_top, ys_top, color=NAVY, linewidth=2.6, marker='o',
             markersize=7, markerfacecolor=BG, markeredgecolor=NAVY, markeredgewidth=1.8)

    # Inline endpoint annotations
    ax1.annotate(f'{ys_top[0]:.1f}%', xy=(xs_top[0], ys_top[0]),
                 xytext=(xs_top[0] - 0.4, ys_top[0] + 1.6),
                 color=NAVY, fontsize=10, weight='bold', ha='left')
    ax1.annotate(f'{ys_top[-1]:.1f}%', xy=(xs_top[-1], ys_top[-1]),
                 xytext=(xs_top[-1] + 0.15, ys_top[-1] - 0.5),
                 color=NAVY, fontsize=10, weight='bold', ha='left')

    # Inline series label (right of last point)
    ax1.text(xs_top[-1] + 0.4, ys_top[-1] + 1, "discretionary share\nof central transfers",
             color=NAVY, fontsize=9, ha='left', va='top')

    # Inflection / reform marker
    ax1.axvline(2019, color=INK_LITE, linewidth=0.8, linestyle='--', alpha=0.6)
    ax1.text(2019.15, 31, ' 2019: shared fiscal\n responsibility separated',
             fontsize=8.5, color=INK_LITE, va='bottom', style='italic')
    ax1.text(2025.5, 31, 'budget', fontsize=9, color=MUSTARD,
             style='italic', ha='center', va='bottom')

    ax1.set_xlim(2012.5, 2027)
    ax1.set_ylim(28, 48)
    ax1.set_ylabel('% of central transfers', fontsize=9.5)
    ax1.set_title("Layer 1 — On paper: provinces are getting more discretion",
                  loc='left', fontsize=11.5, color=NAVY, weight='bold', pad=8)
    ax1.set_yticks([30, 35, 40, 45])
    ax1.set_yticklabels(['30%', '35%', '40%', '45%'])

    # --- Bottom panel: self-sufficiency + dependency ---
    xs = YEARS
    ss = [SELF_SUFF[y] for y in xs]
    dp = [DEPEND[y] for y in xs]

    # Budget-zone shading
    ax2.axvspan(2024.5, 2026.5, color=TINT_MUSTARD, alpha=0.35, zorder=0)

    # Self-sufficiency line (navy, primary)
    ax2.plot(xs, ss, color=NAVY, linewidth=2.8, marker='o',
             markersize=6.5, markerfacecolor=BG, markeredgecolor=NAVY, markeredgewidth=1.6)
    ax2.text(xs[0] - 0.4, ss[0] + 1.5, f'{ss[0]:.1f}%', color=NAVY,
             fontsize=10.5, weight='bold', ha='left')
    ax2.text(xs[-1] + 0.15, ss[-1] - 0.4, f'{ss[-1]:.1f}%', color=NAVY,
             fontsize=10.5, weight='bold', ha='left')
    ax2.text(xs[-1] + 0.4, ss[-1] + 1.5, "self-sufficiency", color=NAVY,
             fontsize=9.5, ha='left')

    # Dependency line (coral, secondary)
    ax2.plot(xs, dp, color=CORAL, linewidth=2.4, marker='s',
             markersize=5.5, markerfacecolor=BG, markeredgecolor=CORAL, markeredgewidth=1.4,
             linestyle='-')
    ax2.text(xs[0] - 0.4, dp[0] - 2, f'{dp[0]:.1f}%', color=CORAL,
             fontsize=10, weight='bold', ha='left')
    ax2.text(xs[-1] + 0.15, dp[-1] - 0.4, f'{dp[-1]:.1f}%', color=CORAL,
             fontsize=10, weight='bold', ha='left')
    ax2.text(xs[-1] + 0.4, dp[-1] - 2.2, "dependency on\ncentral transfers",
             color=CORAL, fontsize=9.5, ha='left', va='top')

    # Big takeaway annotation — the 8-point loss
    ax2.annotate('', xy=(2024, 49.5), xytext=(2015, 56),
                 arrowprops=dict(arrowstyle='->', color=NAVY, lw=1.6, alpha=0.55))
    ax2.text(2019, 53.5, '8 pp lost in 11 years', fontsize=11.5, color=NAVY,
             weight='bold', ha='center',
             bbox=dict(facecolor=TINT_BLUE, edgecolor='none', boxstyle='round,pad=0.45', alpha=0.9))

    # Inflection markers — positioned in upper portion (clear of data)
    for x, label in [(2016, '2016 VAT-for-business-tax'),
                      (2020, '2020 COVID'),
                      (2022, '2022 VAT refunds')]:
        ax2.axvline(x, color=INK_LITE, linewidth=0.7, linestyle=':', alpha=0.5)
        ax2.text(x, 60.5, label, fontsize=8.5, color=INK_LITE,
                 ha='center', va='bottom', style='italic')
    ax2.text(2025.5, 60.5, 'budget', fontsize=9, color=MUSTARD,
             style='italic', ha='center', va='bottom')

    ax2.set_xlim(2012.5, 2027)
    ax2.set_ylim(35, 62)
    ax2.set_ylabel('% of local general public expenditure', fontsize=9.5)
    ax2.set_xticks(xs)
    ax2.set_xticklabels([str(y) for y in xs])
    ax2.set_title("Layer 2 — In practice: provinces are losing fiscal self-sufficiency",
                  loc='left', fontsize=11.5, color=CORAL, weight='bold', pad=8)
    ax2.set_yticks([40, 45, 50, 55, 60])
    ax2.set_yticklabels(['40%', '45%', '50%', '55%', '60%'])

    # Title + source + watermark
    add_title(fig,
              "How Beijing centralized by letting go",
              subtitle="Two sides of the same operation: discretion up, autonomy down. Both come from the same Ministry of Finance ledgers.")
    add_watermark(fig,
                  source='Source: Ministry of Finance Budget Department, 2013–2024 final accounts; Treasury Department, January 2026 release for 2025; 2026 central budget tables.')

    plt.subplots_adjust(left=0.06, right=0.93, top=0.88, bottom=0.10)
    out = FIG_DIR / 'two_layer_paradox_blog.png'
    plt.savefig(str(out), dpi=180, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f'Wrote {out.name}')


# ============================================================
# Figure 2: Stacked composition (the four-band area chart)
# ============================================================
def fig_composition():
    fig, ax = plt.subplots(figsize=(13, 7.2))
    xs = YEARS

    tax_pct, shared_pct, free_pct, special_pct = [], [], [], []
    for y in xs:
        tax_pct.append(SHARE_TAX[y])
        if y < 2019:
            shared_pct.append(0)
            free_pct.append(GENERAL_PRE19[y])
        else:
            shared_pct.append(SHARE_SHARED[y])
            free_pct.append(SHARE_FREE[y])
        special_pct.append(SHARE_SPECIAL[y])

    colors = [TINT_BLUE, TINT_MUSTARD, NAVY, CORAL]
    labels = ['Tax rebates', 'Shared fiscal responsibility',
              'Discretionary general transfers', 'Special + Category-3']
    arrays = [np.array(tax_pct), np.array(shared_pct), np.array(free_pct), np.array(special_pct)]

    bot = np.zeros(len(xs))
    band_centers = []   # (center_x, center_y, label, text_color)
    for arr, c, lab in zip(arrays, colors, labels):
        ax.fill_between(xs, bot, bot + arr, color=c, alpha=0.88,
                        linewidth=0.4, edgecolor=BG)
        # Compute label position for inside-band annotation
        # Place at year 2022 (a stable middle point where all bands are wide-ish)
        anchor_year = 2022
        i = xs.index(anchor_year)
        if arr[i] > 4:   # only label bands wider than 4 pp at the anchor
            mid_y = bot[i] + arr[i] / 2
            text_color = ('white' if c in (NAVY, CORAL)
                          else (MUSTARD if c == TINT_MUSTARD else NAVY))
            band_centers.append((anchor_year, mid_y, lab, text_color))
        bot = bot + arr

    # Inside-band labels
    for x, y, lab, color in band_centers:
        ax.text(x, y, lab, color=color, fontsize=10, weight='bold',
                ha='center', va='center')

    # Pre-2019 shared band is zero — call out the reclassification with arrow
    ax.annotate('"Shared fiscal responsibility"\nbecomes a separately\nreported line in 2019',
                xy=(2019.2, 26), xytext=(2015.5, 18),
                fontsize=9, color=INK, ha='left', va='center',
                arrowprops=dict(arrowstyle='->', color=INK_LITE, lw=0.8, alpha=0.6),
                bbox=dict(facecolor=BG, edgecolor=INK_LITE, boxstyle='round,pad=0.35',
                          linewidth=0.5, alpha=0.95))

    # Reform marker lines
    ax.axvline(2014, color=INK_LITE, linewidth=0.8, linestyle='--', alpha=0.5)
    ax.text(2014, 102, '2014  special-purpose consolidation',
            fontsize=8.5, color=INK_LITE, va='bottom', style='italic', ha='center')
    ax.axvline(2019, color=INK_LITE, linewidth=0.8, linestyle='--', alpha=0.5)
    ax.axvspan(2024.5, 2026.5, color=TINT_MUSTARD, alpha=0.25, zorder=0)
    ax.text(2025.5, 102, 'budget', fontsize=9, color=MUSTARD,
            style='italic', ha='center', va='bottom')

    ax.set_xlim(2013, 2026)
    ax.set_ylim(0, 100)
    ax.set_xticks(xs)
    ax.set_xticklabels([str(y) for y in xs])
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_yticklabels(['0%', '20%', '40%', '60%', '80%', '100%'])
    ax.set_ylabel('Share of central-to-local fiscal flows')

    add_title(fig,
              "What's inside central-to-local transfers, 2013–2026",
              subtitle="The red band — project-locked spending — shrank after 2014. The blue band — discretionary general transfers — grew. Both shifts happened inside an envelope drawn in Beijing.",
              y_title=0.95, y_sub=0.91)
    add_watermark(fig,
                  source='Source: Ministry of Finance Budget Department, annual final-account tables (2013–2024) and 2025/2026 budget tables. Pre-2019, "shared fiscal responsibility" was not separately listed and is collapsed into "discretionary general transfers" here.')

    plt.subplots_adjust(left=0.06, right=0.97, top=0.85, bottom=0.13)
    out = FIG_DIR / 'transfer_structure_blog.png'
    plt.savefig(str(out), dpi=180, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f'Wrote {out.name}')


# ============================================================
# Figure 3: Revised evidence — property channel + pass-through
# ============================================================
def fig_revised_evidence():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 11),
                                    gridspec_kw={'height_ratios': [1, 1], 'hspace': 0.40})

    # --- Top panel: property tax % (left axis) + land sales trillion (right axis) ---
    pt_years = sorted(PROPERTY_PCT.keys())
    pt_vals  = [PROPERTY_PCT[y] for y in pt_years]
    ls_years = sorted(LAND_SALES.keys())
    ls_vals  = [LAND_SALES[y] for y in ls_years]

    # Tint band for post-2021 collapse
    ax1.axvspan(2021, 2024, color=TINT_CORAL, alpha=0.30, zorder=0)
    ax1.text(2022.5, 19.4, 'property collapse', fontsize=9, color=CORAL,
             ha='center', va='top', style='italic',
             bbox=dict(facecolor=BG, edgecolor='none', boxstyle='round,pad=0.25', alpha=0.85))

    # Property-tax line (navy, primary)
    ax1.plot(pt_years, pt_vals, color=NAVY, linewidth=2.6, marker='o',
             markersize=6.5, markerfacecolor=BG, markeredgecolor=NAVY, markeredgewidth=1.5)
    # 2021 annotation — matching the article's "peaked in 2021 at 1.97 trillion, 17.8 percent"
    pt_2021 = PROPERTY_PCT[2021]
    ax1.annotate(f'{pt_2021:.1f}%',
                 xy=(2021, pt_2021),
                 xytext=(2021 - 0.6, pt_2021 + 0.55),
                 color=NAVY, fontsize=10, weight='bold', ha='right')
    ax1.text(pt_years[-1] + 0.15, pt_vals[-1] - 0.3, f'{pt_vals[-1]:.1f}%',
             color=NAVY, fontsize=10, weight='bold', ha='left')
    ax1.text(pt_years[-1] + 0.4, pt_vals[-1] - 1.2,
             "property taxes\n(% of local revenue)",
             color=NAVY, fontsize=9, ha='left', va='top')

    ax1.set_ylim(13, 20)
    ax1.set_ylabel('% of provincial own-source revenue', color=NAVY, fontsize=9.5)
    ax1.tick_params(axis='y', labelcolor=NAVY)
    ax1.set_yticks([14, 16, 18, 20])
    ax1.set_yticklabels(['14%', '16%', '18%', '20%'])

    # Land sales on right axis
    ax1b = ax1.twinx()
    ax1b.spines['top'].set_visible(False)
    ax1b.plot(ls_years, ls_vals, color=CORAL, linewidth=2.4, marker='s',
              markersize=5.5, markerfacecolor=BG, markeredgecolor=CORAL,
              markeredgewidth=1.4, linestyle='--')
    ls_peak = max(ls_vals)
    ax1b.annotate(f'{ls_peak:.1f}T',
                  xy=(2021, ls_peak), xytext=(2020.6, ls_peak + 0.35),
                  color=CORAL, fontsize=10, weight='bold', ha='right')
    ax1b.text(ls_years[-1] + 0.15, ls_vals[-1] + 0.1, f'{ls_vals[-1]:.1f}T',
              color=CORAL, fontsize=10, weight='bold', ha='left')
    ax1b.text(ls_years[-1] + 0.4, ls_vals[-1] - 0.6,
              "land sale revenue\n(trillion yuan)",
              color=CORAL, fontsize=9, ha='left', va='top')

    ax1b.set_ylim(3, 10)
    ax1b.set_ylabel('Trillion yuan (current prices)', color=CORAL, fontsize=9.5)
    ax1b.tick_params(axis='y', labelcolor=CORAL)
    ax1b.set_yticks([4, 6, 8, 10])
    ax1b.set_yticklabels(['¥4T', '¥6T', '¥8T', '¥10T'])
    ax1b.grid(False)

    ax1.set_title("The property channel: how the housing slowdown reached the general budget",
                  loc='left', fontsize=11.5, color=INK, weight='bold', pad=14)
    ax1.set_xticks(pt_years)
    ax1.set_xticklabels([str(y) for y in pt_years])

    # --- Bottom panel: central pass-through ratio ---
    cp_years = sorted(CENTRAL_PT.keys())
    cp_vals  = [CENTRAL_PT[y] for y in cp_years]

    # Fill above 100% (debt-financed years)
    ax2.axhspan(100, 110, color=TINT_CORAL, alpha=0.30, zorder=0)
    ax2.axhline(100, color=CORAL, linewidth=1.0, linestyle=':', alpha=0.7)
    ax2.text(2013.2, 100.7, "100% line — transfers exceed central revenue (debt-financed)",
             fontsize=8.5, color=CORAL, va='bottom', style='italic')

    ax2.plot(cp_years, cp_vals, color=NAVY, linewidth=2.6, marker='D',
             markersize=6, markerfacecolor=BG, markeredgecolor=NAVY, markeredgewidth=1.5)

    # Endpoint callouts
    ax2.text(cp_years[0] - 0.4, cp_vals[0] - 2.5, f'{cp_vals[0]:.0f}%',
             color=NAVY, fontsize=11, weight='bold', ha='left')
    ax2.text(cp_years[-1] + 0.15, cp_vals[-1] - 0.5, f'{cp_vals[-1]:.0f}%',
             color=NAVY, fontsize=11, weight='bold', ha='left')

    # Highlight peak (2023) and other above-100 years
    for y, v in zip(cp_years, cp_vals):
        if v > 100:
            ax2.text(y, v + 1.5, f'{v:.0f}%', ha='center', fontsize=8.5,
                     color=CORAL, weight='bold')

    # Trajectory annotation in lower-left clear area
    ax2.text(2014.5, 83, "Beijing becomes a near pass-through",
             fontsize=10.5, color=NAVY, weight='bold', ha='left', va='center',
             bbox=dict(facecolor=TINT_BLUE, edgecolor='none', boxstyle='round,pad=0.4', alpha=0.85))
    ax2.annotate('', xy=(2022.5, 99), xytext=(2017.5, 84.5),
                 arrowprops=dict(arrowstyle='->', color=NAVY, lw=1.5, alpha=0.55))

    ax2.set_ylim(75, 110)
    ax2.set_xlim(cp_years[0] - 0.6, cp_years[-1] + 1.8)
    ax2.set_ylabel('Central transfers ÷ central revenue', fontsize=9.5)
    ax2.set_xticks(cp_years)
    ax2.set_xticklabels([str(y) for y in cp_years])
    ax2.set_yticks([80, 90, 100, 110])
    ax2.set_yticklabels(['80%', '90%', '100%', '110%'])
    ax2.set_title("Beijing's evolving role: from redistributor to debt-financed pass-through",
                  loc='left', fontsize=11.5, color=INK, weight='bold', pad=14)

    add_title(fig,
              "Two pieces of evidence that complicate any simple causal account",
              subtitle="The property channel explains the post-2021 acceleration but not the long arc. Meanwhile, the center itself has become a pass-through, increasingly funded by its own debt.",
              y_title=0.965, y_sub=0.943)
    add_watermark(fig,
                  source='Sources: MoF Budget Department, Local General Public Budget Revenue tables (top, property taxes) and Local Government-managed Funds Revenue tables (top, land sales); Central General Public Budget Revenue tables (bottom).')

    plt.subplots_adjust(left=0.07, right=0.85, top=0.90, bottom=0.08)
    out = FIG_DIR / 'revised_evidence_blog.png'
    plt.savefig(str(out), dpi=180, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f'Wrote {out.name}')


# ============================================================
# Figure 4 (NEW): What changed is not the split. It is the size of what is being split.
# ============================================================
def fig_split_vs_pie():
    """Two side-by-side panels for the article's central reversal finding:
       (left) central-local share of general revenue, 2013 vs 2024 — basically unchanged
       (right) general revenue as % of GDP, 2013 vs 2024 — fell 5.7 pp, split almost evenly"""
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13, 6.5),
                                    gridspec_kw={'width_ratios': [1, 1], 'wspace': 0.30})

    # ----- LEFT: stacked bar showing central-local share, 2013 vs 2024 -----
    years_x = ['2013', '2024']
    central_share = [46.6, 46.2]
    local_share   = [53.4, 53.8]

    bar_w = 0.55
    xs_bar = np.arange(2)

    # Central on bottom, local on top
    b1 = axL.bar(xs_bar, central_share, bar_w, color=CORAL, alpha=0.85, edgecolor=BG, linewidth=2)
    b2 = axL.bar(xs_bar, local_share, bar_w, bottom=central_share, color=NAVY,
                 alpha=0.85, edgecolor=BG, linewidth=2)

    # In-bar labels
    for i, (cs, ls) in enumerate(zip(central_share, local_share)):
        axL.text(i, cs / 2, f'Central\n{cs:.1f}%', ha='center', va='center',
                 color='white', fontsize=10, weight='bold')
        axL.text(i, cs + ls / 2, f'Local\n{ls:.1f}%', ha='center', va='center',
                 color='white', fontsize=10, weight='bold')

    # Connecting annotation showing "unchanged"
    axL.annotate('', xy=(1.32, 53.8), xytext=(0.32, 53.4),
                 arrowprops=dict(arrowstyle='<->', color=INK_LITE, lw=1.0, alpha=0.5))
    axL.text(0.5, 58, '+0.4 pp · essentially unchanged',
             ha='center', fontsize=10.5, color=INK, weight='bold', style='italic',
             bbox=dict(facecolor=TINT_BLUE, edgecolor='none', boxstyle='round,pad=0.4', alpha=0.85))

    axL.set_xticks(xs_bar)
    axL.set_xticklabels(years_x, fontsize=11)
    axL.set_ylim(0, 105)
    axL.set_yticks([0, 25, 50, 75, 100])
    axL.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
    axL.set_ylabel('Share of national general public budget revenue', fontsize=9.5)
    axL.set_title("The central-local split barely moved",
                  loc='left', fontsize=11.5, color=INK, weight='bold', pad=10)

    # ----- RIGHT: revenue / GDP, 2013 vs 2024 -----
    cat_labels = ['Central\nrevenue', 'Local\nrevenue']
    rev_2013   = [10.1, 11.7]
    rev_2024   = [7.6,  8.8]

    xs_g = np.arange(2)
    bar_w = 0.32

    bars_2013 = axR.bar(xs_g - bar_w/2 - 0.02, rev_2013, bar_w, color=NAVY, alpha=0.85,
                        edgecolor=BG, linewidth=1.5, label='2013')
    bars_2024 = axR.bar(xs_g + bar_w/2 + 0.02, rev_2024, bar_w, color=CORAL, alpha=0.85,
                        edgecolor=BG, linewidth=1.5, label='2024')

    # Value labels above bars
    for i, v in enumerate(rev_2013):
        axR.text(i - bar_w/2 - 0.02, v + 0.25, f'{v:.1f}%', ha='center',
                 fontsize=10, color=NAVY, weight='bold')
    for i, v in enumerate(rev_2024):
        axR.text(i + bar_w/2 + 0.02, v + 0.25, f'{v:.1f}%', ha='center',
                 fontsize=10, color=CORAL, weight='bold')

    # Delta arrows + labels
    for i, (a, b) in enumerate(zip(rev_2013, rev_2024)):
        delta = b - a
        axR.annotate('', xy=(i + bar_w/2 + 0.02, b + 1.0),
                     xytext=(i - bar_w/2 - 0.02, a + 1.0),
                     arrowprops=dict(arrowstyle='->', color=INK_LITE, lw=1.0, alpha=0.6))
        axR.text(i, max(a, b) + 1.9, f'{delta:+.1f} pp',
                 ha='center', fontsize=10, color=INK, weight='bold')

    axR.set_xticks(xs_g)
    axR.set_xticklabels(cat_labels, fontsize=11)
    axR.set_ylim(0, 14)
    axR.set_yticks([0, 4, 8, 12])
    axR.set_yticklabels(['0%', '4%', '8%', '12%'])
    axR.set_ylabel('% of nominal GDP', fontsize=9.5)
    axR.set_title("Both halves shrank against GDP",
                  loc='left', fontsize=11.5, color=INK, weight='bold', pad=10)
    axR.legend(loc='upper right', frameon=False, fontsize=10)

    # Big takeaway between panels
    fig.text(0.5, 0.46,
             '"What changed is not the split. It is the size of what is being split."',
             ha='center', va='center', fontsize=11.5, color=INK, style='italic',
             bbox=dict(facecolor=TINT_MUSTARD, edgecolor='none',
                       boxstyle='round,pad=0.5', alpha=0.6))

    # Title + source
    add_title(fig,
              "Why this isn't simply about Beijing taking provincial revenue",
              subtitle="Beijing didn't take a bigger slice of the pie. The pie itself shrank — and the central and provincial halves shrank in roughly equal proportion.",
              y_title=0.955, y_sub=0.92)
    add_watermark(fig,
                  source='Source: Ministry of Finance Budget Department, National + Central + Local General Public Budget Revenue final-account tables, 2013 and 2024; nominal GDP from National Bureau of Statistics.')

    plt.subplots_adjust(left=0.07, right=0.96, top=0.86, bottom=0.13)
    out = FIG_DIR / 'split_vs_pie_blog.png'
    plt.savefig(str(out), dpi=180, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f'Wrote {out.name}')


if __name__ == '__main__':
    fig_two_layer()
    fig_composition()
    fig_revised_evidence()
    fig_split_vs_pie()
    print(f'\nBlog-styled figures written to {FIG_DIR}')
