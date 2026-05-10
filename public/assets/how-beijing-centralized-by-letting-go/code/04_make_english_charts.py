"""
Generate English-labeled versions of the four published charts using values
embedded from the year-by-year decision tables. Run this for English-language
publication. Reads no external xlsx — figures regenerate from the data
dictionaries below, which match the values in data/2 and data/3.

Outputs:
  ../figures/1_transfer_structure_2013_2026_en.png  (stacked area)
  ../figures/2_fiscal_autonomy_trend_2013_2026_en.png (three-line trend)
  ../figures/3_two_layer_paradox_2013_2026_en.png   (two-panel paradox)
  ../figures/4_revised_evidence_2013_2024_en.png    (NEW: property + central-local)
"""

from pathlib import Path
HERE = Path(__file__).resolve().parent
FIG_DIR = HERE.parent / 'figures'
FIG_DIR.mkdir(exist_ok=True, parents=True)

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False


# ============================================================
# Embedded data (matches data/2 + data/3 + data/4)
# ============================================================
YEARS = list(range(2013, 2027))
KIND  = {y: ('final account' if y <= 2024 else 'budget') for y in YEARS}

# Decomposition shares (% of total transfer payment), pre-2019 has no
# shared/free split, so we mark with None
SHARE_TAX     = {2013:10.5,2014:9.8,2015:9.1,2016:11.5,2017:12.3,2018:11.5,
                 2019:15.1,2020:13.5,2021:14.1,2022:12.2,2023:11.0,2024:12.1,
                 2025:12.2,2026:11.8}
SHARE_SHARED  = {2013:None,2014:None,2015:None,2016:None,2017:None,2018:None,
                 2019:42.9,2020:38.7,2021:41.7,2022:37.5,2023:35.8,2024:37.4,
                 2025:37.3,2026:37.4}
SHARE_FREE    = {2013:None,2014:None,2015:None,2016:None,2017:None,2018:None,
                 2019:31.8,2020:31.2,2021:35.3,2022:33.6,2023:35.9,2024:37.4,
                 2025:41.5,2026:41.7}
SHARE_SPECIAL = {2013:38.8,2014:36.7,2015:39.2,2016:34.9,2017:33.6,2018:32.9,
                 2019:10.2,2020:16.5,2021: 9.0,2022:16.6,2023:17.3,2024:13.1,
                 2025: 9.0,2026: 9.0}
# Pre-2019 collapse free + shared into single "general" bar so stack still adds
GENERAL_SHARE_PRE19 = {2013:50.7,2014:53.5,2015:51.7,2016:53.6,2017:54.1,2018:55.6}

# Self-sufficiency, dependency for the bottom panel (% of local total expenditure)
SELF_SUFF = {2013:57.0,2014:57.7,2015:55.2,2016:54.4,2017:52.8,2018:52.0,
             2019:49.6,2020:47.6,2021:52.7,2022:48.3,2023:49.6,2024:48.9,
             2025:50.0,2026:49.2}
DEPEND    = {2013:39.6,2014:39.2,2015:36.6,2016:37.0,2017:37.6,2018:37.0,
             2019:36.5,2020:39.5,2021:39.0,2022:43.1,2023:43.5,2024:41.1,
             2025:41.7,2026:41.0}

# Property-tax channel (Sheet A of file 4)
PROPERTY_PCT_OF_LOCAL = {2013:15.13,2014:15.50,2015:14.37,2016:14.89,2017:16.17,
                         2018:17.00,2019:17.67,2020:18.40,2021:17.76,2022:16.51,
                         2023:14.85,2024:14.39}

# Land sale revenue (Sheet B of file 4) — trillion yuan
LAND_SALES = {2018:6.29,2019:7.06,2020:8.21,2021:8.49,2022:6.53,2023:5.66,2024:4.77}

# Central pass-through ratio (Sheet D of file 4)
CENTRAL_PT = {2013:0.798,2014:0.800,2015:0.796,2016:0.821,2017:0.802,2018:0.815,
              2019:0.832,2020:1.005,2021:0.898,2022:1.022,2023:1.033,2024:0.999}


# ============================================================
# Chart 1: stacked composition over time
# ============================================================
def chart_composition():
    fig, ax = plt.subplots(figsize=(12, 6.5))
    xs = YEARS

    tax_pct, shared_pct, free_pct, special_pct = [], [], [], []
    for y in xs:
        tax_pct.append(SHARE_TAX[y])
        if y < 2019:
            shared_pct.append(0)
            free_pct.append(GENERAL_SHARE_PRE19[y])
        else:
            shared_pct.append(SHARE_SHARED[y])
            free_pct.append(SHARE_FREE[y])
        special_pct.append(SHARE_SPECIAL[y])

    colors = {'tax': '#A9C5E8', 'shared': '#F4B183', 'free': '#5B9BD5', 'special': '#C00000'}

    bot = np.zeros(len(xs))
    ax.fill_between(xs, bot, bot + np.array(tax_pct), color=colors['tax'],
                    label='Tax rebates (rule-based; not discretionary)')
    bot += np.array(tax_pct)
    ax.fill_between(xs, bot, bot + np.array(shared_pct), color=colors['shared'],
                    label='Shared fiscal responsibility (central-mandated; 2019+ separated)')
    bot += np.array(shared_pct)
    ax.fill_between(xs, bot, bot + np.array(free_pct), color=colors['free'],
                    label="Other general transfers (province's true discretionary share)")
    bot += np.array(free_pct)
    ax.fill_between(xs, bot, bot + np.array(special_pct), color=colors['special'],
                    label='Special purpose + Category-3 (project-locked)')

    ax.axvline(2014, color='#888', linestyle='--', linewidth=1, alpha=0.6)
    ax.axvline(2019, color='#888', linestyle='--', linewidth=1, alpha=0.6)
    ax.axvline(2024.5, color='#444', linestyle=':', linewidth=1.2)
    ax.text(2014, 102, '2014\nspecial-purpose grant\nconsolidation', ha='center', va='bottom',
            fontsize=8.5, color='#444')
    ax.text(2019, 102, '2019\nshared fiscal responsibility\nseparated out', ha='center', va='bottom',
            fontsize=8.5, color='#444')
    ax.text(2025.5, 102, 'budget figures', ha='center', va='bottom', fontsize=8.5,
            color='#444', style='italic')

    ax.set_xlim(2013, 2026)
    ax.set_ylim(0, 100)
    ax.set_xticks(xs)
    ax.set_xticklabels([str(y) for y in xs])
    ax.set_ylabel("Share of central-to-local fiscal flows (%)")
    ax.set_title("Composition of China's central-to-local transfer payments, 2013–2026",
                 fontsize=13, pad=22, weight='bold')
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.22), ncol=2, frameon=False, fontsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.text(0.06, 0.02,
             'Source: Ministry of Finance Budget Department, annual final-account tables (2013–2024) and 2025 / 2026 budget tables.\n'
             'Notes: Pre-2019 the "shared fiscal responsibility" category was not separately listed and is collapsed into "Other general transfers." '
             '"Category-3" captures the temporary supplementary line used in 2020 (COVID), 2022 (VAT credit refunds), 2023 and 2024 (disaster recovery).',
             fontsize=8, color='#555', ha='left', va='bottom')

    plt.subplots_adjust(left=0.07, right=0.96, top=0.88, bottom=0.22)
    out = FIG_DIR / '1_transfer_structure_2013_2026_en.png'
    plt.savefig(str(out), dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Wrote {out.name}')


# ============================================================
# Chart 2: three-line trend (special / shared / free shares)
# ============================================================
def chart_three_lines():
    fig, ax = plt.subplots(figsize=(12, 6))
    xs = YEARS

    sp = [SHARE_SPECIAL[y] for y in xs]
    sh_xs = [y for y in xs if SHARE_SHARED[y] is not None]
    sh = [SHARE_SHARED[y] for y in sh_xs]
    fr_xs = [y for y in xs if SHARE_FREE[y] is not None]
    fr = [SHARE_FREE[y] for y in fr_xs]

    ax.plot(xs, sp, marker='o', color='#C00000', linewidth=2.2, markersize=6,
            label='Special + Category-3 / total transfers (project-locked)')
    ax.plot(sh_xs, sh, marker='s', color='#F4B183', linewidth=2.2, markersize=6,
            label='Shared fiscal responsibility / total transfers (central-mandated)')
    ax.plot(fr_xs, fr, marker='^', color='#2E75B6', linewidth=2.5, markersize=7,
            label="Other general transfers / total (province's true discretionary share)")

    ax.annotate(f'2019: {fr[0]:.1f}%',
                xy=(2019, fr[0]), xytext=(2014.5, 22),
                fontsize=10, color='#2E75B6',
                arrowprops=dict(arrowstyle='-', color='#2E75B6', lw=0.8))
    ax.annotate(f'2026 budget: {fr[-1]:.1f}%',
                xy=(2026, fr[-1]), xytext=(2023.3, 50),
                fontsize=10, color='#2E75B6', weight='bold',
                arrowprops=dict(arrowstyle='-', color='#2E75B6', lw=0.8))

    ax.axvline(2014, color='#888', linestyle='--', linewidth=1, alpha=0.5)
    ax.axvline(2019, color='#888', linestyle='--', linewidth=1, alpha=0.5)
    ax.axvline(2024.5, color='#444', linestyle=':', linewidth=1.0, alpha=0.7)
    ymax = max(sp + sh + fr) + 5
    ax.text(2014, ymax * 0.95, '2014 reform', fontsize=9, color='#666', ha='left', va='top')
    ax.text(2019, ymax * 0.95, '2019 reclassification', fontsize=9, color='#666', ha='left', va='top')

    ax.set_xlim(2012.7, 2026.3)
    ax.set_xticks(xs)
    ax.set_xticklabels([str(y) for y in xs])
    ax.set_ylabel('Share of central-to-local fiscal flows (%)')
    ax.set_title('Three ratios that frame the "decentralization" debate, 2013–2026',
                 fontsize=13, pad=18, weight='bold')
    ax.legend(loc='upper right', frameon=False, fontsize=9.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.25)

    fig.text(0.06, 0.02,
             'Source: Ministry of Finance Budget Department, 2013–2024 final accounts and 2025/2026 budgets. '
             'Lines for shared fiscal responsibility and discretionary share are reportable only from 2019, '
             'when the former category was first separated from general transfers.',
             fontsize=8, color='#555', ha='left', va='bottom')

    plt.subplots_adjust(left=0.07, right=0.96, top=0.90, bottom=0.13)
    out = FIG_DIR / '2_fiscal_autonomy_trend_2013_2026_en.png'
    plt.savefig(str(out), dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Wrote {out.name}')


# ============================================================
# Chart 3: two-panel paradox (centerpiece)
# ============================================================
def chart_two_layer():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 9), sharex=True,
                                    gridspec_kw={'height_ratios': [1, 1.3], 'hspace': 0.16})
    xs = YEARS

    fr_xs = [y for y in xs if SHARE_FREE[y] is not None]
    fr = [SHARE_FREE[y] for y in fr_xs]

    ax1.plot(fr_xs, fr, marker='^', color='#2E75B6', linewidth=2.5, markersize=8)
    ax1.fill_between(fr_xs, 0, fr, color='#2E75B6', alpha=0.10)
    for x, y in zip(fr_xs, fr):
        ax1.text(x, y + 1.3, f'{y:.1f}%', ha='center', fontsize=9, color='#2E75B6')
    ax1.set_ylim(25, 50)
    ax1.set_ylabel('% of central transfer payments', fontsize=10)
    ax1.set_title("Layer 1 — On paper: provinces' discretionary share of central transfers is rising",
                  fontsize=12, color='#2E75B6', loc='left', weight='bold')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.axvline(2019, color='#888', linestyle='--', linewidth=1, alpha=0.5)
    ax1.text(2019, 47, ' 2019: shared fiscal responsibility separated', fontsize=9, color='#666', va='top')
    ax1.axvspan(2024.5, 2026.5, color='#FFF2CC', alpha=0.5, zorder=0)
    ax1.text(2025.5, 47, 'budget', fontsize=9, color='#888', ha='center', style='italic', va='top')

    ss = [SELF_SUFF[y] for y in xs]
    dp = [DEPEND[y] for y in xs]

    ax2.plot(xs, ss, marker='o', color='#C00000', linewidth=2.8, markersize=8,
             label='Self-sufficiency (own-source revenue / total expenditure)')
    ax2.plot(xs, dp, marker='s', color='#7F7F7F', linewidth=2.0, markersize=6,
             label='Dependency on central transfers (transfers / total expenditure)')

    ax2.annotate(f'{ss[0]:.1f}%', xy=(xs[0], ss[0]), xytext=(xs[0], ss[0] + 1.5),
                 fontsize=10, color='#C00000', weight='bold', ha='center')
    ax2.annotate(f'{ss[-1]:.1f}%', xy=(xs[-1], ss[-1]), xytext=(xs[-1], ss[-1] + 1.5),
                 fontsize=10, color='#C00000', weight='bold', ha='center')
    ax2.annotate('', xy=(2024.5, 50), xytext=(2014.5, 56),
                 arrowprops=dict(arrowstyle='->', color='#C00000', lw=2, alpha=0.6))
    ax2.text(2019, 51.5, '8 percentage points lost in 11 years', fontsize=11,
             color='#C00000', ha='center', weight='bold')

    ax2.axvline(2016, color='#888', linestyle=':', linewidth=1, alpha=0.6)
    ax2.text(2016, 60, ' 2016 VAT-for-business-tax full rollout', fontsize=9, color='#666', va='top')
    ax2.axvline(2020, color='#888', linestyle=':', linewidth=1, alpha=0.6)
    ax2.text(2020, 60, ' 2020 COVID', fontsize=9, color='#666', va='top')
    ax2.axvline(2022, color='#888', linestyle=':', linewidth=1, alpha=0.6)
    ax2.text(2022, 60, ' 2022 VAT credit refunds', fontsize=9, color='#666', va='top')
    ax2.axvspan(2024.5, 2026.5, color='#FFF2CC', alpha=0.5, zorder=0)

    ax2.set_ylim(35, 62)
    ax2.set_ylabel('% of local general public expenditure', fontsize=10)
    ax2.set_xticks(xs)
    ax2.set_xticklabels([str(y) for y in xs])
    ax2.set_title('Layer 2 — In practice: provincial self-sufficiency keeps falling; dependency on the center keeps rising',
                  fontsize=12, color='#C00000', loc='left', weight='bold')
    ax2.legend(loc='upper right', frameon=False, fontsize=10)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.grid(axis='y', alpha=0.25)

    fig.suptitle('How Beijing centralized by letting go: two layers of the same redesign',
                 fontsize=15, weight='bold', y=0.97)
    fig.text(0.06, 0.02,
             'Source: Ministry of Finance Budget Department, 2013–2024 final accounts; Treasury Department, January 2026 fiscal status release for 2025; '
             '2026 central budget tables.\n'
             'Definitions: Self-sufficiency = local own-source revenue ÷ local general public budget expenditure. '
             'Dependency = central transfer payments (incl. tax rebates) ÷ local general public budget expenditure.\n'
             'The discretionary-share line at top is reportable from 2019 onward, when the shared fiscal responsibility category was first separated from general transfers.',
             fontsize=8, color='#555', ha='left', va='bottom')

    plt.subplots_adjust(left=0.07, right=0.96, top=0.91, bottom=0.16)
    out = FIG_DIR / '3_two_layer_paradox_2013_2026_en.png'
    plt.savefig(str(out), dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Wrote {out.name}')


# ============================================================
# Chart 4 (NEW): Revised-evidence panel
#   Top   — Property-tax share + land sale revenue (the property channel)
#   Bottom — Central pass-through ratio (transfers / central revenue)
# ============================================================
def chart_revised_evidence():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 9),
                                    gridspec_kw={'height_ratios': [1, 1], 'hspace': 0.32})

    # ---- Top panel: property-tax share + land sale revenue ----
    pt_years = sorted(PROPERTY_PCT_OF_LOCAL.keys())
    pt_vals = [PROPERTY_PCT_OF_LOCAL[y] for y in pt_years]
    ax1.plot(pt_years, pt_vals, marker='o', color='#7030A0', linewidth=2.5, markersize=7,
             label='Four property/land taxes (% of provincial own-source revenue, left axis)')
    ax1.set_ylim(12, 20)
    ax1.set_ylabel('Property-tax share of local revenue (%)', fontsize=10, color='#7030A0')
    ax1.tick_params(axis='y', labelcolor='#7030A0')

    ax1b = ax1.twinx()
    ls_years = sorted(LAND_SALES.keys())
    ls_vals = [LAND_SALES[y] for y in ls_years]
    ax1b.plot(ls_years, ls_vals, marker='s', color='#C00000', linewidth=2.5, markersize=7,
              linestyle='--',
              label='Land sale revenue (trillion yuan, right axis)')
    ax1b.set_ylim(3, 9)
    ax1b.set_ylabel('Land sale revenue (trillion yuan)', fontsize=10, color='#C00000')
    ax1b.tick_params(axis='y', labelcolor='#C00000')

    # Annotate peaks
    peak_pt_year = max(pt_years, key=lambda y: PROPERTY_PCT_OF_LOCAL[y])
    ax1.annotate(f'peak {PROPERTY_PCT_OF_LOCAL[peak_pt_year]:.1f}%',
                 xy=(peak_pt_year, PROPERTY_PCT_OF_LOCAL[peak_pt_year]),
                 xytext=(peak_pt_year - 1.5, 19),
                 fontsize=9, color='#7030A0',
                 arrowprops=dict(arrowstyle='-', color='#7030A0', lw=0.8))
    ax1b.annotate(f'peak {max(ls_vals):.1f} trillion',
                  xy=(2021, max(ls_vals)), xytext=(2018.5, 8.5),
                  fontsize=9, color='#C00000',
                  arrowprops=dict(arrowstyle='-', color='#C00000', lw=0.8))
    ax1b.annotate(f'2024: {ls_vals[-1]:.1f} trillion (-44%)',
                  xy=(2024, ls_vals[-1]), xytext=(2022.3, 3.8),
                  fontsize=9, color='#C00000', weight='bold',
                  arrowprops=dict(arrowstyle='-', color='#C00000', lw=0.8))

    ax1.set_title('The property channel: how the housing slowdown hits provincial general budget revenue',
                  fontsize=12, weight='bold', loc='left')
    ax1.set_xticks(pt_years)
    ax1.set_xticklabels([str(y) for y in pt_years])
    ax1.spines['top'].set_visible(False)
    ax1b.spines['top'].set_visible(False)
    ax1.grid(axis='y', alpha=0.25)
    # Combined legend
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax1b.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='lower left', frameon=False, fontsize=9)

    # ---- Bottom panel: central pass-through ratio ----
    cp_years = sorted(CENTRAL_PT.keys())
    cp_vals = [CENTRAL_PT[y] * 100 for y in cp_years]
    ax2.plot(cp_years, cp_vals, marker='D', color='#2E75B6', linewidth=2.5, markersize=7,
             label='Central transfers ÷ central general public budget revenue')
    ax2.fill_between(cp_years, 80, cp_vals,
                     where=[v > 80 for v in cp_vals], color='#2E75B6', alpha=0.10)
    ax2.axhline(100, color='#666', linestyle=':', linewidth=1)
    ax2.text(2013.2, 100.5, '100% line: transfers exceed central revenue (debt-financed)',
             fontsize=9, color='#666', va='bottom')

    for y, v in zip(cp_years, cp_vals):
        ax2.text(y, v + 1.5, f'{v:.0f}%', ha='center', fontsize=8.5, color='#2E75B6')

    ax2.annotate(f'2013: {cp_vals[0]:.0f}%', xy=(2013, cp_vals[0]),
                 xytext=(2013, cp_vals[0] - 5), fontsize=10, color='#2E75B6', weight='bold',
                 ha='left')
    ax2.annotate(f'2024: {cp_vals[-1]:.0f}%', xy=(2024, cp_vals[-1]),
                 xytext=(2024, cp_vals[-1] - 5), fontsize=10, color='#2E75B6', weight='bold',
                 ha='right')

    ax2.set_ylim(75, 110)
    ax2.set_ylabel('Central transfers as % of central revenue', fontsize=10)
    ax2.set_xticks(cp_years)
    ax2.set_xticklabels([str(y) for y in cp_years])
    ax2.set_title('Beijing as pass-through: nearly all of central revenue (and then some) now flows out as transfers',
                  fontsize=12, weight='bold', loc='left')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.grid(axis='y', alpha=0.25)

    fig.suptitle('Revised evidence: the property channel and the pass-through center, 2013–2024',
                 fontsize=14, weight='bold', y=0.98)
    fig.text(0.06, 0.02,
             'Sources (top): Local General Public Budget Revenue Final Account Tables for the four 100%-local property taxes (deed, land VAT, property, urban land use). '
             'Local Government-managed Funds Revenue Final Account Tables for land sale revenue.\n'
             'Source (bottom): Central General Public Budget Revenue Final Account Tables, 2013–2024. '
             'Transfer total = general transfer + special transfer (+ Category-3 in 2020/2022/2023/2024).',
             fontsize=8, color='#555', ha='left', va='bottom')

    plt.subplots_adjust(left=0.07, right=0.94, top=0.92, bottom=0.16)
    out = FIG_DIR / '4_revised_evidence_2013_2024_en.png'
    plt.savefig(str(out), dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Wrote {out.name}')


if __name__ == '__main__':
    chart_composition()
    chart_three_lines()
    chart_two_layer()
    chart_revised_evidence()
    print(f'\nAll English-labeled charts written to {FIG_DIR}')
