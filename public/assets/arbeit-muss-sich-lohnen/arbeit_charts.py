"""
Arbeit muss sich lohnen - Abbildungen 1-4 (Status quo 2025, ohne UBI)
=====================================================================
Erzeugt die vier getrennten Grafiken des Artikels:
  figur_1_einkommen()          Abb. 1  Verfuegbares Einkommen
  figur_2_lohnverbleibsquote() Abb. 2  Lohnverbleibsquote
  figur_3_wasserfall()         Abb. 3  Was von 600 EUR Tariferhoehung bleibt
  figur_4_oecd()               Abb. 4 Marginale Lohnsteuer OECD-Vergleich

Jede Abbildung wird als PNG (DPI dpi) und als Vektor-PDF gespeichert.
"""

DPI = 500   

"""
Deutschland Steuerparadoxie 2025 (numerische Ableitung)
2-Panel: Verfügbares Einkommen · ROI (Arbeit vs. Kapital)
Szenario A: Alleinstehend (kinderlos)
Szenario B: Alleinerziehend + 1 Kind (8 J.)

HINWEIS: §6a BKGG ist analytisch nicht exakt reproduzierbar (Erwerbs-
  tätigenfreibeträge, Wohnbedarfsanteile). kiz_B() ist daher eine auf reale
  Stützpunkte kalibrierte Reduktionsform. KIZ_BEMESS ist der zentrale
  Kalibrierungsparameter; bei geänderter KdU-Annahme nachjustieren.
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# ═══════════ PALETTE═══════════
BG_COL="#ffffff"; PANEL="#ffffff"; PANEL2="#f5f5f5"
GRAY="#d5d5d5"; LGRAY="#aaaaaa"
# Hauptdatenfarben: gedämpftes Blau ↔ Ziegelrot (Brookings / ifo / SVR)
C_NETTO="#1a5276"      # Dunkelblau – Single
C_FAM="#c0392b"        # Ziegelrot – Familie
C_FAM2="#922b21"       # Tieferes Rot
C_BASE="#2980b9"       # Mittleres Blau – BG-Grundniveau Single
C_OHNE_TR="#95a5a6"    # Mittelgrau – Netto (nur ESt+SV)
# Akzentfarben
C_KAP="#b7950b"        # Dunkelgold – ROI Kapital
C_YELLOW="#7d6608"     # Dunkles Amber – Mindestlohn
C_ORANGE="#d35400"     # Orange (Reserve)
C_ROI="#2471a3"        # Blau (Legacy)
# Warnung / Sonderzonen (gedämpft für weißen Hintergrund)
C_BG_ZONE="#d4e6f1"    # Helles Blau – BG-Zone
C_NL_ZONE="#d4a574"    # Helles Karamell – Transferentzugszone
C_DEAD="#c0392b"       # Ziegelrot – Tote Zone
# Text
WHITE="#1a1a1a"; DIMW="#555555"

plt.rcParams.update({"font.family":"serif",
    "font.serif":["Georgia","Palatino","Times New Roman","DejaVu Serif"],
    "mathtext.fontset":"dejavuserif",
    "figure.facecolor":BG_COL,
    "axes.facecolor":PANEL,"text.color":WHITE,"axes.labelcolor":DIMW,
    "xtick.color":DIMW,"ytick.color":DIMW,
    "axes.linewidth":0.6})

# ═══════════ KONSTANTEN 2025 ═══════════
AVG_WAGE=50_257
GFB=12_096; ZONE2_GRENZE=17_443; ZONE3_GRENZE=68_480
REICH_GRENZE=277_826; SOLI_FREIGRENZE=19_950
BBG_KV=66_150; BBG_RV=96_600

# ── Sozialversicherung ──
KV_S=0.171        # 14,6% allg. + 2,5% Zusatzbeitrag (Durchschnitt 2025)
PV_S=0.036        # Pflegeversicherung Basissatz 3,6%
PV_KL_ZU=0.006    # Kinderlosenzuschlag (100% AN), nur Szenario A
RV_S=0.186; AV_S=0.026
MINIJOB=556*12; MIDIJOB=2_000*12

# ── Bürgergeld (BG) ──
BG_RS=563*12                  # Regelbedarf Stufe 1
BG_RS_K=390*12                # Regelbedarf Stufe 5 (Kind 6-13 J.)
BG_KDU_S=450*12               # KdU Single (Durchschnitt)
BG_KDU_F=550*12               # KdU Familie
MB_AE=round(0.12*563,2)*12    # Mehrbedarf AE, 1 Kind 8 J. (12% × 563€)
BG_BED_S=BG_RS+BG_KDU_S       # Single-Bedarf
BG_BED_F=BG_RS+BG_RS_K+BG_KDU_F+MB_AE  # Familien-Bedarf (inkl. Mehrbedarf)

BG_FG=100*12; BG_G1=520*12; BG_G2=1_000*12
BG_G3S=1_200*12; BG_G3F=1_500*12

# NK-Pauschale (Heizung/Warmwasser/sonstiges, BG-Bezug)
BG_NB_S=(18.36+10+29)*12                       # ≈688€ Single
BG_NB_F=BG_NB_S+(12+8)*12                      # ≈928€ Familie (zusätzl. NK)

# ── Familienleistungen ──
KINDERGELD=255*12              # 255€/Mo. ab 01.2025
FAM_ENTL=4_260                 # Entlastungsbetrag Alleinerziehende
KIZ_HOECHST=297*12             # KiZ-Höchstbetrag 2025 (297€/Mo., OHNE Sofortzuschlag)
KIZ_SOFORT=25*12               # Kindersofortzuschlag (separat, on top)
KIZ_MEG=600*12                 # Mindesteinkommensgrenze AE (brutto)
KIZ_KIND_ANR=0.45              # Anrechnung Kindereinkommen/UVG: 45% (Starke-Familien-Gesetz 2019/20)
KIZ_ELT_ANR=0.45               # Anrechnung elterl. Einkommen über Bemessungsgrenze: 45%
# Bemessungsgrenze EMPIRISCH KALIBRIERT (§6a BKGG analytisch nicht exakt
# reproduzierbar). Stützpunkt: Nettolohn 1.730€/Mo -> ~50€/Mo KiZ.
# Liegt höher als die nominale Formel RB+MB+KdU-Anteil (~1.054€/Mo), weil die
# reale KiZ-Prüfung Erwerbstätigenfreibeträge abzieht (hier nicht separat
# modelliert); KIZ_BEMESS absorbiert diesen Effekt.
KIZ_BEMESS=1_425*12            # kalibrierte Bemessungsgrenze (≈17.100€/J.)
UVG=299*12                     # Unterhaltsvorschuss 6-11 J. (2025)
BUT_MATERIAL=130+65               # Schulbedarf 195€/J.
BUT_TEILHABE=15*12                # Teilhabe 180€/J.
BUT_ESSEN=700                     # Mittagsverpflegung ≈700€/J. (3.70€ × 190 Schultage)
BUT=BUT_MATERIAL+BUT_TEILHABE+BUT_ESSEN  # ≈1.075€/J.

# ── Kinderfreibetrag (Günstigerprüfung §31 EStG) ──
KFB_KIND=6_612                    # Kinderfreibetrag 2025 (voll, §32 Abs.6 S.6 bei UVG)
KFB_BEA=2_928                     # BEA-Freibetrag 2025 (voll bei AE)
KFB=KFB_KIND+KFB_BEA              # 9.540€ gesamt

# ── Wohngeld ──
# Szenario A (Single): weiterhin vereinfachte lineare Rampe
WG_MAX1=250*12; WG_UG1=15_500; WG_OG1=22_500
# Szenario B (Alleinerziehend + 1 Kind): echte §19-WoGG-Formel
#   Wohngeld/Monat = 1,15 * (M - (a + b*M + c*Y) * Y)
#   a,b,c: Anlage 2 WoGG, Stand 1.1.2025 (BGBl. 2024 I Nr. 314), 2 Haushaltsmitglieder
WG_A2=0.03; WG_B2=3.571e-4; WG_C2=3.040e-5     # a, b, c (2 Haushaltsmitglieder)
WG_FAKTOR=1.15
# §12 WoGG Höchstbetrag Miete, 2 Personen, 2025, nach Mietenstufe I..VII:
WG_HOECHST_2P={1:437,2:493,3:551,4:619,5:680,6:745,7:820}
WG_MIETENSTUFE=3               # Annahme: mittelgroße ostdeutsche Stadt -> Mietenstufe III
WG_KLIMA_2P=24.80              # §12 Abs.7 Klimakomponente, 2 Personen
WG_HEIZ_2P=142.60              # §12 Abs.6 Heizkostenentlastung (Gesamtbetrag), 2 Personen
WG_AE_FREIBETRAG=1_320         # §17 WoGG Freibetrag Alleinerziehende (1 Kind <18)
WG_MIETE_B=BG_KDU_F            # zu berücksichtigende Bruttokaltmiete/Jahr (= KdU-Annahme)

# ── Sonstiges ──
ML_H=12.82; ML_VZ=ML_H*2_080
KEST=0.25; SOLI_K=0.055; TAX_KAP=KEST*(1+SOLI_K); ROI_KAP=(1-TAX_KAP)*100

# ── Reform-Szenario: UBI + ML 15€/h ──
UBI=1_200*12                      # 14.400€/J. bedingungslos, steuerfrei
ML15_H=15.00; ML15_VZ=ML15_H*2_080  # 31.200€/J.
MINIJOB_UBI=650*12                 # Minijob-Grenze bei 15€ ML (15 * 130 / 3 = 650)
MIDIJOB_UBI=2_340*12               # Midijob-Grenze geschätzt (2000 * 15 / 12.82 ≈ 2340)

# ═══════════ KERN-FUNKTIONEN ═══════════
def est(z):
    z=max(0.,z)
    if z<=GFB: return 0.
    if z<=ZONE2_GRENZE: y=(z-GFB)/1e4; return (932.30*y+1400)*y
    if z<=ZONE3_GRENZE: w=(z-ZONE2_GRENZE)/1e4; return (176.64*w+2397)*w+1015.13
    if z<=REICH_GRENZE: return .42*z-10911.83
    return .45*z-19246.61

def est_m(z):
    z=max(0.,z)
    if z<=GFB: return 0.
    if z<=ZONE2_GRENZE: y=(z-GFB)/1e4; return (2*932.30*y+1400)/1e4
    if z<=ZONE3_GRENZE: w=(z-ZONE2_GRENZE)/1e4; return (2*176.64*w+2397)/1e4
    if z<=REICH_GRENZE: return .42
    return .45

def soli(z):
    e=est(z)
    if e<=SOLI_FREIGRENZE: return 0.
    return min(.119*(e-SOLI_FREIGRENZE),.055*e)

def soli_m(z,em):
    e=est(z)
    if e<=SOLI_FREIGRENZE: return 0.
    if .119*(e-SOLI_FREIGRENZE)<.055*e: return .119*em
    return .055*em

# ── SV mit Midijob (PV-Differenzierung) ──
def mj_f(b, minijob=MINIJOB, midijob=MIDIJOB):
    if b<=minijob: return 0.
    if b<=midijob: return (b-minijob)/(midijob-minijob)
    return 1.

def sv_an(b, kinderlos=True, minijob=MINIJOB, midijob=MIDIJOB):
    """AN-Sozialversicherungsbeitrag, mit PV-Kinderlosenzuschlag."""
    pv_zu=PV_KL_ZU if kinderlos else 0.
    return (min(b,BBG_KV)*((KV_S+PV_S)/2+pv_zu)
           +min(b,BBG_RV)*(RV_S+AV_S)/2)*mj_f(b, minijob, midijob)

def sv_an_mg(b, kinderlos=True, minijob=MINIJOB, midijob=MIDIJOB):
    """Marginaler AN-SV-Satz."""
    pv_zu=PV_KL_ZU if kinderlos else 0.
    r=0.
    if b<=BBG_KV: r+=(KV_S+PV_S)/2+pv_zu
    if b<=BBG_RV: r+=(RV_S+AV_S)/2
    if b<=minijob: return 0.
    if b<=midijob:
        f=mj_f(b, minijob, midijob); span=midijob-minijob
        raw=r*f+r*b/span
        return min(raw, r*2)
    return r

def sv_ag_mg(b):
    """AG-SV: kein Kinderlosenzuschlag (wird nur von AN getragen)."""
    r=0.
    if b<=BBG_KV: r+=(KV_S+PV_S)/2
    if b<=BBG_RV: r+=(RV_S+AV_S)/2
    return r

def netto_fn(b, entl=0, kinderlos=True, minijob=MINIJOB, midijob=MIDIJOB):
    sv=sv_an(b, kinderlos, minijob, midijob); zvE=max(0.,b-sv-1230-entl)
    return b-sv-est(zvE)-soli(zvE)

# ── BG Freibetrag ──
def bg_fb(b,g3):
    fb=min(b,BG_FG)
    if b>BG_FG: fb+=.20*min(b-BG_FG,BG_G1-BG_FG)
    if b>BG_G1: fb+=.30*min(b-BG_G1,BG_G2-BG_G1)
    if b>BG_G2: fb+=.10*min(b-BG_G2,g3-BG_G2)
    return fb

# ── Szenario A: Single (kinderlos) ──
def bg_A(b):
    n=netto_fn(b, kinderlos=True)
    return max(0.,BG_BED_S-max(0.,n-bg_fb(b,BG_G3S)))
def nb_A(b): return BG_NB_S if bg_A(b)>0 else 0.
def wg_A(b):
    if bg_A(b)>0: return 0.
    n=netto_fn(b, kinderlos=True)
    if n>=WG_OG1: return 0.
    return WG_MAX1*max(0.,min(1.,(WG_OG1-n)/(WG_OG1-WG_UG1)))

# ── Szenario B: Alleinerziehend+Kind (8 J.) ──
def bg_B(b):
    n=netto_fn(b, FAM_ENTL, kinderlos=False); fb=bg_fb(b,BG_G3F)
    # UVG und Kindergeld sind Einkommen, das BG mindert
    return max(0.,BG_BED_F-max(0.,n-fb)-KINDERGELD-UVG)

def kiz_B(b):
    """Kinderzuschlag §6a BKGG - empirisch kalibrierte Reduktionsform.

    KiZ = (Hoechstbetrag + Sofortzuschlag)
          - 45% Kindereinkommen (UVG)
          - 45% Nettolohn ueber der kalibrierten Bemessungsgrenze KIZ_BEMESS.
    Kalibriert auf: Nettolohn 1.730 EUR/Mo -> ~50 EUR/Mo KiZ;
    Auslauf bei ~2.500 EUR/Mo brutto (Alleinerziehend + 1 Kind).
    """
    if bg_B(b)>0: return 0.        # in BG-Bezug -> kein KiZ
    if b<KIZ_MEG: return 0.        # unter Mindesteinkommensgrenze 600 EUR/Mo. brutto
    n=netto_fn(b, FAM_ENTL, kinderlos=False)
    bemess=KIZ_BEMESS                                  # kalibrierte Bemessungsgrenze
    abzug_eltern=KIZ_ELT_ANR*max(0.,n-bemess)          # 45% elterl. Einkommen ueber Grenze
    abzug_kind=KIZ_KIND_ANR*UVG                        # 45% Kindereinkommen (UVG)
    kiz=max(0.,KIZ_HOECHST+KIZ_SOFORT-abzug_kind-abzug_eltern)
    return kiz

def nb_B(b): return BG_NB_F if bg_B(b)>0 else 0.

def but_B(b):
    """BuT: verfügbar bei BG-, KiZ- oder WG-Bezug."""
    if bg_B(b)>0 or kiz_B(b)>0 or wg_B(b)>0:
        return BUT
    return 0.

def wg_B(b):
    """Wohngeld nach §19 WoGG (echte Formel, Anlage 2 Stand 2025).
    Wohngeld/Monat = 1,15 * (M - (a + b*M + c*Y) * Y)
    Formel + M gegen den amtlichen Thüringer Wohngeldrechner geeicht
    (Rechtsstand Jan. 2025, Wohnort Erfurt): ohne UVG ergibt der Rechner
    26.700->292, 33.900->111 EUR/Mo. §14 WoGG rechnet UVG aber voll als
    Haushaltseinkommen an -> hier korrekt MIT UVG (Rechnerläufe ließen
    es weg) -> 26.700->~164, 33.900->0 EUR/Mo.
    """
    if bg_B(b)>0: return 0.            # §20 WoGG: kein Wohngeld neben Bürgergeld
    # Y = wohngeldrechtliches Monatseinkommen: Erwerbseinkommen abzgl.
    #   Werbungskosten, -30% pauschal (§16: Steuer/RV/KV je 10%),
    #   + UVG (§14: voll als Einkommen angerechnet),
    #   - Freibetrag Alleinerziehende (§17).
    erwerb=max(0., b-1230)
    Y=max(0., 0.70*erwerb + UVG - WG_AE_FREIBETRAG)/12.
    # M = zu berücksichtigende Miete: Bruttokaltmiete gedeckelt auf
    #   §12-Abs.1-Höchstbetrag + Klimakomponente, dann + Heizkostenkomponente.
    cap=WG_HOECHST_2P[WG_MIETENSTUFE]+WG_KLIMA_2P
    M=min(WG_MIETE_B/12., cap)+WG_HEIZ_2P
    wg=WG_FAKTOR*(M-(WG_A2+WG_B2*M+WG_C2*Y)*Y)
    return max(0., min(M, wg))*12.     # Jahresbetrag

def gsp_B(b, minijob=MINIJOB, midijob=MIDIJOB):
    """Günstigerprüfung §31 EStG: Mehrvorteil KFB vs. Kindergeld.
    Bei AE + UVG (andere Elternteil leistet keinen Unterhalt)
    → voller KFB gem. §32 Abs.6 Satz 6 EStG.
    Rückgabe: max(0, Steuerersparnis_KFB − Kindergeld)."""
    sv=sv_an(b, kinderlos=False, minijob=minijob, midijob=midijob)
    zvE=max(0., b-sv-1230-FAM_ENTL)
    zvE_kfb=max(0., zvE-KFB)
    ersparnis=(est(zvE)+soli(zvE))-(est(zvE_kfb)+soli(zvE_kfb))
    return max(0., ersparnis-KINDERGELD)

# ── Arbeitgeberkosten ──
def ag_kosten(b, minijob=MINIJOB):
    """Gesamtkosten Arbeitgeber (Brutto + AG-SV)."""
    if b<=minijob:
        return b*1.31        # Minijob: Pauschal-AG ≈31%
    ag=min(b,BBG_KV)*(KV_S+PV_S)/2+min(b,BBG_RV)*(RV_S+AV_S)/2
    return b+ag

# ── Gesamtverfügbares Einkommen (alle Transfers) ──
def verfuegbar_A(b):
    """Single: Netto + BG + Nebenkosten + Wohngeld."""
    n=netto_fn(b, kinderlos=True)
    return n+bg_A(b)+nb_A(b)+wg_A(b)

def verfuegbar_B(b):
    """Alleinerziehend+Kind: Netto + BG + NB + WG + KG + KiZ + UVG + BuT + GSP."""
    n=netto_fn(b, FAM_ENTL, kinderlos=False)
    return n+bg_B(b)+nb_B(b)+wg_B(b)+KINDERGELD+kiz_B(b)+UVG+but_B(b)+gsp_B(b)

# ── Reform: UBI (ersetzt alle bedarfsgeprüften Transfers) ──
def verfuegbar_UBI_A(b):
    """UBI-Single: Netto + UBI (kein BG, WG, NB)."""
    return netto_fn(b, kinderlos=True, minijob=MINIJOB_UBI, midijob=MIDIJOB_UBI)+UBI

def verfuegbar_UBI_B(b):
    """UBI-Familie: Netto + UBI + KG + UVG + GSP (kein BG, KiZ, WG, NB, BuT)."""
    return netto_fn(b, FAM_ENTL, kinderlos=False, minijob=MINIJOB_UBI, midijob=MIDIJOB_UBI)+UBI+KINDERGELD+UVG+gsp_B(b, minijob=MINIJOB_UBI, midijob=MIDIJOB_UBI)

# ═══════════ BERECHNUNG (numerische Ableitung) ═══════════
N=8000; brutto=np.linspace(0,130_000,N); xf=brutto/AVG_WAGE
nvA=np.zeros(N); ntA=np.zeros(N); roiA=np.zeros(N)
nvB=np.zeros(N); ntB=np.zeros(N); roiB=np.zeros(N)
# UBI-Reform
nvUA=np.zeros(N); nvUB=np.zeros(N); roiUA=np.zeros(N); roiUB=np.zeros(N)
EPS=1.0   # 1€ Schrittweite für numerische Ableitung

for i,b in enumerate(brutto):
    # ── Verfügbares Einkommen ──
    nvA[i]=verfuegbar_A(b)
    nvB[i]=verfuegbar_B(b)
    ntA[i]=netto_fn(b, kinderlos=True)
    ntB[i]=netto_fn(b, FAM_ENTL, kinderlos=False)
    # UBI-Reform
    nvUA[i]=verfuegbar_UBI_A(b)
    nvUB[i]=verfuegbar_UBI_B(b)
    # ── Marginale Arbeitsrendite (numerisch) ──
    #    ROI = ΔVerfügbar / ΔArbeitgeberkosten × 100
    #    Erfasst automatisch alle Cliff-Effekte:
    #    BG-Entzug, WG-Auslauf, KiZ-Entzug, BuT-Verlust, NB-Verlust
    dag=(ag_kosten(b+EPS)-ag_kosten(b))/EPS
    dag_UBI=(ag_kosten(b+EPS, minijob=MINIJOB_UBI)-ag_kosten(b, minijob=MINIJOB_UBI))/EPS
    dA=(verfuegbar_A(b+EPS)-nvA[i])/EPS
    dB=(verfuegbar_B(b+EPS)-nvB[i])/EPS
    dUA=(verfuegbar_UBI_A(b+EPS)-nvUA[i])/EPS
    dUB=(verfuegbar_UBI_B(b+EPS)-nvUB[i])/EPS
    roiA[i]=np.clip(dA/dag*100,-20,100)
    roiB[i]=np.clip(dB/dag*100,-20,100)
    roiUA[i]=np.clip(dUA/dag_UBI*100,-20,100)
    roiUB[i]=np.clip(dUB/dag_UBI*100,-20,100)

# Baselines = Einkommen bei 0€ Arbeit
BASE_A=nvA[0]; BASE_B=nvB[0]

# Zonen
bga_arr=np.array([bg_A(b) for b in brutto])
wga_arr=np.array([wg_A(b) for b in brutto])
bg_end=int(np.where(bga_arr>0)[0][-1]) if (bga_arr>0).any() else N//4
wg_end=int(np.where(wga_arr>0)[0][-1]) if (wga_arr>0).any() else bg_end+100
dead=np.where((roiA<=1.)&(bga_arr>0)&(brutto>BG_G3S))[0]
ds=dead[0] if len(dead)>0 else None; de=dead[-1] if len(dead)>0 else None



def figur_1_einkommen():

    # ═══════════ ABBILDUNG 1 – Verfügbares Einkommen (Status quo) ═══════════
    fig,ax1=plt.subplots(figsize=(18,10),facecolor=BG_COL)
    ax1.set_facecolor(PANEL); ax1.spines[["top","right"]].set_visible(False)
    ax1.spines[["left","bottom"]].set_color(LGRAY)

    xlim=(0.,2.5); m=(xf>=xlim[0])&(xf<=xlim[1])
    xm=xf[m]; nva=nvA[m]; nta=ntA[m]; nvb=nvB[m]
    nmax=max(nva.max(),nvb.max())
    bx=xf[bg_end]; wx=xf[wg_end]; mlx=ML_VZ/AVG_WAGE

    at=ax1.twiny()
    at.set_xlim(xlim[0]*AVG_WAGE/1e3,xlim[1]*AVG_WAGE/1e3)
    at.set_xlabel("Brutto-Jahreseinkommen [k€]",color=DIMW,fontsize=10,labelpad=8)
    at.tick_params(colors=DIMW,labelsize=8.5)
    at.spines[["top","right","left","bottom"]].set_color(LGRAY)
    at.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}k"))

    pol=[(GFB/AVG_WAGE,f"GFB\n{GFB//1000}k€",DIMW),
         (ZONE3_GRENZE/AVG_WAGE,f"Spitzen-\nsteuer\n{ZONE3_GRENZE//1000}k€",C_YELLOW),
         (BBG_KV/AVG_WAGE,f"BBG KV\n{BBG_KV//1000}k€","#2e86ab"),
         (BBG_RV/AVG_WAGE,f"BBG RV\n{BBG_RV//1000}k€",C_NETTO)]
    def dpol(ax,lbl=True):
        yfs=[.05,.72,.46,.05]
        for (xt,l,c),yf in zip(pol,yfs):
            if xlim[0]<xt<=xlim[1]:
                ax.axvline(xt,color=c,lw=.8,ls=":",alpha=.55,zorder=1)
                if lbl:
                    yl=ax.get_ylim()
                    ax.text(xt+.015,yl[0]+(yl[1]-yl[0])*yf,l,color=c,fontsize=7,alpha=.9,
                            va="bottom",ha="left",zorder=12,
                            bbox=dict(boxstyle="round,pad=0.15",fc=BG_COL,alpha=.88,ec="none"))

    ax1.axvspan(0,bx,color=C_BG_ZONE,alpha=.30,zorder=0)
    ax1.axvspan(bx,wx,color=C_NL_ZONE,alpha=.18,zorder=0)
    if ds is not None:
        ax1.axvspan(xf[ds],xf[de],color=C_DEAD,alpha=.10,zorder=1)

    for base,col,lbl,yoff in [(BASE_A,C_BASE,f"Single: {BASE_A/12:.0f}€/Mo.",-nmax*.035),
                               (BASE_B,C_FAM,f"Familie: {BASE_B/12:.0f}€/Mo.",+nmax*.018)]:
        ax1.axhline(base,color=col,lw=1.2,ls="--",alpha=.60,zorder=4)
        ax1.text(xlim[1]-.02,base+yoff,
                 f"BG-Grundniveau {lbl}",color=col,ha="right",fontsize=7.5,zorder=12,
                 bbox=dict(boxstyle="round,pad=0.15",fc=BG_COL,ec=col,lw=.6,alpha=.92))

    ax1.axvline(mlx,color=C_YELLOW,lw=1.4,ls="-.",alpha=.55,zorder=2)
    ax1.plot(xm,nta,color=C_OHNE_TR,lw=1.2,ls="--",alpha=.55,zorder=3)
    ax1.plot(xm,nva,color=C_NETTO,lw=2.4,zorder=5)
    ax1.plot(xm,nvb,color=C_FAM,lw=2.4,zorder=5)

    if ds is not None:
        ax1.text((xf[ds]+xf[de])/2,nmax*.50,'Tote Zone\n0% Wachstum',
                 color=C_DEAD,ha="center",fontsize=9,fontweight="bold",alpha=.90,zorder=12,
                 bbox=dict(boxstyle="round,pad=0.3",fc=BG_COL,ec=C_DEAD,lw=.6,alpha=.95))

    mli=np.argmin(np.abs(brutto-ML_VZ))
    eA=max(0,(nvA[mli]-BASE_A)/2080); eB=max(0,(nvB[mli]-BASE_B)/2080)
    ax1.annotate(
        f"Mindestlohn Vollzeit ({ML_VZ/1e3:.0f}k€):\n"
        f"  Single: eff. {eA:.1f}€/h  ({eA/ML_H*100:.0f}% d. ML)\n"
        f"  Familie: eff. {eB:.1f}€/h  ({eB/ML_H*100:.0f}% d. ML)",
        xy=(mlx,nvA[mli]),xytext=(mlx+.25,nmax*.33),fontsize=8.5,color=C_YELLOW,zorder=12,
        arrowprops=dict(arrowstyle="->",color=C_YELLOW,lw=1.2,connectionstyle="arc3,rad=-.15"),
        bbox=dict(boxstyle="round,pad=0.35",fc=BG_COL,ec=C_YELLOW,lw=.6,alpha=.95))

    ax1.text(.02,nmax*.82,"Aufstiegsfalle\n80–100 %\ndes Lohnzuwachses\nverdunsten",
        fontsize=8.5,color="#8b5e3c",zorder=12,
        bbox=dict(boxstyle="round,pad=0.25",fc=BG_COL,ec="#8b5e3c",lw=.6,alpha=.95))

    dpol(ax1)
    ax1.set_xlim(*xlim); ax1.set_ylim(0,nmax*1.18)
    ax1.set_ylabel("Verfügbares Einkommen [€/Jahr]",color=DIMW,fontsize=11,labelpad=12)
    ax1.tick_params(axis="y",colors=DIMW,labelsize=9)
    ax1.tick_params(axis="x",colors=DIMW,labelsize=9)
    ax1.set_xlabel(f"Einkommen (Vielfaches Durchschnittslohn · 1,0x = {AVG_WAGE/1e3:.1f}k€)",
                   color=DIMW,fontsize=10.5,labelpad=10)
    ax1.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.1fx'))
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v/1e3:.0f}k€"))
    ax1.grid(False)

    leg1=[Line2D([0],[0],color=C_NETTO,lw=2.4,label="Single"),
          Line2D([0],[0],color=C_FAM,lw=2.4,label="Alleinerziehend +1 Kind"),
          Line2D([0],[0],color=C_OHNE_TR,lw=1.2,ls="--",alpha=.6,label="Netto (nur ESt+SV, ohne Transfers)"),
          Line2D([0],[0],color=C_BASE,lw=1.2,ls="--",alpha=.6,label="BG-Grundniveau (0€ Arbeit)"),
          Patch(facecolor=C_DEAD,alpha=.12,label="Tote Zone (0 % Ertrag)")]
    ax1.legend(handles=leg1,loc="upper left",facecolor=PANEL2,edgecolor=LGRAY,
               fontsize=8.5,framealpha=.95)
    ax1.set_title("Verfügbares Einkommen — Aufstiegsfalle im unteren Lohnbereich (Status quo 2025)",
        fontsize=15,fontweight="bold",pad=30,color=WHITE)
    ax1.annotate("© Linying Li", xy=(1.0,-0.085), xycoords='axes fraction',
                 ha='right', va='top', fontsize=12, color=DIMW, alpha=0.65,
                 fontstyle='italic', annotation_clip=False)

    out1="/Users/lilinying/Downloads/abb1_verfuegbares_einkommen.png"
    plt.savefig(out1,dpi=DPI,facecolor=BG_COL,bbox_inches='tight')
    plt.savefig(out1.replace('.png','.pdf'),facecolor=BG_COL,bbox_inches='tight')
    print(f"Gespeichert: {out1}")



def figur_2_lohnverbleibsquote():

    # ═══════════ ABBILDUNG 2 – Lohnverbleibsquote (ohne UBI) ═══════════
    fig,ax=plt.subplots(figsize=(18,9),facecolor=BG_COL)
    ax.set_facecolor(PANEL); ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color(LGRAY)
    xlim=(0.,2.5); m=(xf>=xlim[0])&(xf<=xlim[1])
    xm=xf[m]; ra=roiA[m]; rb=roiB[m].copy()
    
    # Spitze (BuT-Klippe) entfernen und durch Marker ersetzen
    spike_mask = rb < -15
    idx_cliff = np.where(spike_mask)[0]
    if len(idx_cliff) > 0:
        x_cliff = xm[idx_cliff[0]]
        rb[spike_mask] = np.nan
    else:
        x_cliff = None
        
    bx=xf[bg_end]; mlx=ML_VZ/AVG_WAGE

    at=ax.twiny()
    at.set_xlim(xlim[0]*AVG_WAGE/1e3,xlim[1]*AVG_WAGE/1e3)
    at.set_xlabel("Brutto-Jahreseinkommen [k€]",color=DIMW,fontsize=10,labelpad=8)
    at.tick_params(colors=DIMW,labelsize=8.5)
    at.spines[["top","right","left","bottom"]].set_color(LGRAY)
    at.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}k"))

    for xt,c in [(GFB/AVG_WAGE,DIMW),(ZONE3_GRENZE/AVG_WAGE,C_YELLOW),
                 (BBG_KV/AVG_WAGE,"#2e86ab"),(BBG_RV/AVG_WAGE,C_NETTO)]:
        if xlim[0]<xt<=xlim[1]:
            ax.axvline(xt,color=c,lw=.8,ls=":",alpha=.55,zorder=1)

    ax.axvspan(0,bx,color=C_BG_ZONE,alpha=.30,zorder=0)
    if ds is not None:
        ax.axvspan(xf[ds],xf[de],color=C_DEAD,alpha=.10,zorder=1)

    ax.plot(xm,ra,color=C_NETTO,lw=2.4,zorder=5)
    ax.plot(xm,rb,color=C_FAM,lw=2.0,zorder=5)
    ax.axhline(ROI_KAP,color=C_KAP,lw=1.6,ls="--",alpha=.85,zorder=4)
    ax.text(xlim[1]-.03,ROI_KAP+2.5,f"Kapitalrendite ({ROI_KAP:.1f} %) — KESt+Soli, keine SV",
            color=C_KAP,ha="right",fontsize=9,fontweight="bold",zorder=12,
            bbox=dict(boxstyle="round,pad=0.15",fc=BG_COL,alpha=.92,ec="none"))
    ax.axvline(mlx,color=C_YELLOW,lw=1.4,ls="-.",alpha=.45,zorder=2)

    if ds is not None:
        ax.text((xf[ds]+xf[de])/2,-15,'0 % Wachstum\nTote Zone',color=C_DEAD,
                ha="center",fontsize=8.5,fontweight="bold",alpha=.90,zorder=12,
                bbox=dict(boxstyle="round,pad=0.25",fc=BG_COL,ec=C_DEAD,lw=.6,alpha=.95))

    if x_cliff is not None:
        ax.plot(x_cliff, 0, marker="v", color=C_DEAD, markersize=8, zorder=13)
        ax.annotate("BuT-Klippe: −1.075€/Jahr", xy=(x_cliff, -2), xytext=(x_cliff + 0.05, -12),
                    color=C_DEAD, fontsize=8.5, fontweight="bold", alpha=0.90, zorder=12,
                    arrowprops=dict(arrowstyle="->", color=C_DEAD, lw=1.2),
                    bbox=dict(boxstyle="round,pad=0.25", fc=BG_COL, ec=C_DEAD, lw=0.6, alpha=0.95),
                    va="center", ha="left")

    ax.axhline(0,color=LGRAY,lw=.8,alpha=.5)
    ax.set_xlim(*xlim); ax.set_ylim(-25,100)
    ax.set_xlabel(f"Einkommen (Vielfaches Durchschnittslohn · 1,0x = {AVG_WAGE/1e3:.1f}k€)",
                  color=DIMW,fontsize=10.5,labelpad=10)
    ax.set_ylabel("Lohnverbleibsquote [%]",color=DIMW,fontsize=11,labelpad=12)
    ax.tick_params(axis="y",colors=DIMW,labelsize=9)
    ax.tick_params(axis="x",colors=DIMW,labelsize=9)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.1fx'))
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.grid(False)

    leg=[Line2D([0],[0],color=C_NETTO,lw=2.4,label="Single"),
         Line2D([0],[0],color=C_FAM,lw=2.0,label="Alleinerziehend +1 Kind"),
         Line2D([0],[0],color=C_KAP,lw=1.6,ls="--",label=f"Kapitalrendite ({ROI_KAP:.1f} %)")]
    ax.legend(handles=leg,loc="lower right",facecolor=PANEL2,edgecolor=LGRAY,
              fontsize=8.5,framealpha=.95)
    ax.set_title("Lohnverbleibsquote — was vom nächsten Euro Bruttolohn übrig bleibt",
                 fontsize=15,fontweight="bold",pad=30,color=WHITE)
    ax.annotate("© Linying Li",xy=(1.0,-0.10),xycoords='axes fraction',ha='right',va='top',
                fontsize=12,color=DIMW,alpha=0.65,fontstyle='italic',annotation_clip=False)

    out2="/Users/lilinying/Downloads/abb2_lohnverbleibsquote.png"
    plt.savefig(out2,dpi=DPI,facecolor=BG_COL,bbox_inches='tight')
    plt.savefig(out2.replace('.png','.pdf'),facecolor=BG_COL,bbox_inches='tight')
    print(f"Gespeichert: {out2}")



def figur_3_wasserfall():

    # ═══════════ ABBILDUNG 4 – Wasserfall: Was von 600 € übrig bleibt ═══════════
    # Werte = finalisierte Modellrechnung (deutschland_steuer_v8, 26.700 -> 33.900 EUR/J),
    # identisch zum korrigierten Artikeltext.
    W_BRUTTO=600; W_WG=-165; W_KIZ=-60; W_BUT=-90; W_SV=-125; W_LST=-115
    W_NETTO=W_BRUTTO+W_WG+W_KIZ+W_BUT+W_SV+W_LST   # = 45

    fig,ax=plt.subplots(figsize=(18,9.5),facecolor=BG_COL)
    ax.set_facecolor(PANEL); ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color(LGRAY)

    labels=["Brutto-\nErhöhung","Wohngeld\n(Anrechnung)","Kinderzuschlag\n(Wegfall)",
            "BuT\n(Wegfall)","Sozial-\nabgaben","Lohn-\nsteuer","Netto-\nPlus"]
    steps=[W_BRUTTO,W_WG,W_KIZ,W_BUT,W_SV,W_LST,None]
    barcol=[C_NETTO,C_KAP,C_KAP,C_KAP,C_ORANGE,C_FAM2,"#1e7e44"]
    GREEN="#1e7e44"

    cum=0; bottoms=[]; heights=[]
    for i,v in enumerate(steps):
        if i==0:
            bottoms.append(0); heights.append(W_BRUTTO); cum=W_BRUTTO
        elif v is None:
            bottoms.append(0); heights.append(cum)            # Netto-Plus
        else:
            bottoms.append(cum+v); heights.append(-v); cum=cum+v
    tops=[W_BRUTTO]
    c=W_BRUTTO
    for v in steps[1:-1]:
        c+=v; tops.append(c)

    for i in range(7):
        ax.bar(i,heights[i],bottom=bottoms[i],width=0.62,color=barcol[i],zorder=3)
    # Verbindungslinien
    for i in range(6):
        ax.plot([i+0.31,i+1-0.31],[tops[i],tops[i]],ls=(0,(4,3)),color=LGRAY,lw=1.0,zorder=2)

    disp=["600 €","−165 €","−60 €","−90 €","−125 €","−115 €","45 €"]
    for i in range(7):
        if i in (0,6):
            ax.text(i,heights[i]+22,disp[i],ha="center",va="bottom",fontsize=21,
                    fontweight="bold",color=(C_NETTO if i==0 else GREEN),zorder=6)
        else:
            ax.text(i,bottoms[i]+heights[i]/2,disp[i],ha="center",va="center",fontsize=14,
                    fontweight="bold",color="white",zorder=6)

    ax.axhline(W_BRUTTO,color=C_NETTO,lw=1.0,ls=":",alpha=.6,zorder=1)
    ax.text(6.45,W_BRUTTO+8,"Brutto-Niveau (600 €)",ha="right",va="bottom",fontsize=9,
            color=C_NETTO,fontstyle="italic")

    pct=["100 % nominale Erhöhung","−28 %","−10 %","−15 %","−21 %","−19 %","8 % als Netto-Plus"]
    for i in range(7):
        ax.text(i,-52,pct[i],ha="center",va="top",fontsize=9.5,
                color=(C_NETTO if i==0 else (GREEN if i==6 else DIMW)),
                fontweight=("bold" if i in (0,6) else "normal"))
    ax.text(2,-92,"Transferentzug",ha="center",fontsize=10.5,color=C_KAP,
            fontstyle="italic",fontweight="bold")
    ax.text(4,-92,"Sozialversicherung",ha="center",fontsize=10.5,color=C_ORANGE,
            fontstyle="italic",fontweight="bold")
    ax.text(5,-92,"Einkommensteuer",ha="center",fontsize=10.5,color=C_FAM2,
            fontstyle="italic",fontweight="bold")

    ax.set_xticks(range(7)); ax.set_xticklabels(labels,fontsize=10,color=WHITE)
    ax.set_xlim(-0.7,6.7); ax.set_ylim(-120,720)
    ax.set_ylabel("Euro pro Monat (Modellrechnung)",color=DIMW,fontsize=11,labelpad=10)
    ax.tick_params(axis="y",colors=DIMW,labelsize=9)
    ax.tick_params(axis="x",length=0)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f} €"))
    ax.grid(axis="y",color=GRAY,alpha=.45,lw=.6); ax.set_axisbelow(True)

    fig.text(0.075,0.965,"Modellrechnung: Alleinerziehende Vollzeitbeschäftigte "
             "(Mindestlohn 12,82 €/h) mit einem Kind, mittelgroße ostdeutsche Stadt",
             fontsize=10.5,color=DIMW,fontstyle="italic")
    ax.set_title("Was von 600 € Brutto-Tariferhöhung übrig bleibt",
                 fontsize=17,fontweight="bold",pad=26,color=WHITE,loc="left")
    ax.text(0.5,-0.205,"8 % der nominalen Lohnerhöhung verbleiben als realer Nettogewinn "
            "— drei Subsysteme greifen gleichzeitig zu",
            transform=ax.transAxes,ha="center",va="top",fontsize=11.5,color=GREEN,
            fontweight="bold",bbox=dict(boxstyle="round,pad=0.5",fc=BG_COL,ec=GREEN,lw=1.0))
    ax.annotate("© Linying Li",xy=(1.0,-0.30),xycoords='axes fraction',ha='right',va='top',
                fontsize=11,color=DIMW,alpha=0.65,fontstyle='italic',annotation_clip=False)

    out4="/Users/lilinying/Downloads/abb3_wasserfall_600euro.png"
    plt.savefig(out4,dpi=DPI,facecolor=BG_COL,bbox_inches='tight')
    plt.savefig(out4.replace('.png','.pdf'),facecolor=BG_COL,bbox_inches='tight')
    print(f"Gespeichert: {out4}")



def figur_4_oecd():
    """
    Lohnsteuer-Grenzsteuersatz im OECD-Vergleich (2025) - 
    + Kapitalertrags- und Immobilienbesteuerung Deutschland

    Quellen:
      OECD Taxing Wages 2025 | §32a EStG 2025 (Steueränderungsgesetz 2024)
      SV-Beitragssätze 2025: KV 14,6 % + Ø-Zusatzbeitrag 2,5 % = 17,1 %,
                             RV 18,6 %, AV 2,6 %; PV 3,6 % paritätisch,
                             kinderlos + 0,6 % Zuschlag (AN allein)
      APW Deutschland 2025 ≈ 50.257 € p.a. (OECD-Schätzung)
      BBG KV/PV 2025: 66.150 € | BBG RV/AV 2025: 96.600 € (bundeseinheitlich)
      Soli-Freigrenze 2025: 19.950 € (Alleinstehende)
      Werbungskostenpauschale: 1.230 €
    """

    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker

    # ══════════════════════════════════════════════════════════════════════════════
    # STIL  — Think-Tank / Wirtschaftsjournal (hell, serif)
    # ══════════════════════════════════════════════════════════════════════════════
    BG       = "#ffffff"   # reines Weiß (Druckqualität)
    PANEL    = "#f8f8f6"   # sehr helles Warm-Grau für Plot-Fläche
    GRIDC    = "#d0d0cc"   # helles Grau für Gitternetz
    SPINE    = "#444444"   # dunkles Grau für Achsenränder
    TEXTC    = "#1a1a1a"   # fast Schwarz für Hauptbeschriftungen
    SUBTEXT  = "#555555"   # mittleres Grau für Achsentitel, Ticks

    plt.rcParams.update({
        "font.family":       ["Palatino Linotype", "Palatino", "Georgia",
                              "Times New Roman", "DejaVu Serif"],
        "font.size":         10,
        "figure.facecolor":  BG,
        "axes.facecolor":    PANEL,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.spines.left":  True,
        "axes.spines.bottom":True,
        "axes.edgecolor":    SPINE,
        "axes.grid":         False,
        "grid.linestyle":    "-",
        "grid.alpha":        0.50,
        "grid.color":        GRIDC,
        "text.color":        TEXTC,
        "axes.labelcolor":   SUBTEXT,
        "xtick.color":       SUBTEXT,
        "ytick.color":       SUBTEXT,
        "xtick.labelsize":   9,
        "ytick.labelsize":   9,
    })

    # ══════════════════════════════════════════════════════════════════════════════
    # STEUERFUNKTIONEN DEUTSCHLAND (§32a EStG 2025)
    # ══════════════════════════════════════════════════════════════════════════════
    APW      = 50_257    # OECD-Durchschnittslohn DE 2025 (Schätzung)
    GFB      = 12_096    # Grundfreibetrag 2025
    Z2       = 17_443    # Ende Zone 2 (1. Progressionszone)
    Z3       = 68_480    # Ende Zone 3 (2. Progressionszone)
    REICH    = 277_826   # Reichensteuer-Grenze (unverändert)
    SF       = 19_950    # Soli-Freigrenze 2025 (Alleinstehende)
    BBG_KV   = 66_150    # KV/PV-BBG 2025
    BBG_RV   = 96_600    # RV/AV-BBG 2025 (bundeseinheitlich)
    KV_AN    = 0.171 / 2 # KV 14,6 % + Ø-Zusatzbeitrag 2,5 % = 17,1 %
    PV_AN    = 0.036 / 2 + 0.006 # PV kinderlos: 1,8 % + 0,6 % Kinderlosenzuschlag = 2,4 % (AN)
    RV_AN    = 0.186 / 2 # RV 18,6 %
    AV_AN    = 0.026 / 2 # AV 2,6 %
    WERBUNG  = 1_230     # Arbeitnehmer-Pauschbetrag 2025

    def sv_an_betrag(b):
        return min(b, BBG_KV) * (KV_AN + PV_AN) + min(b, BBG_RV) * (RV_AN + AV_AN)

    def sv_an_grenz(b):
        r = 0.0
        if b <= BBG_KV: r += KV_AN + PV_AN
        if b <= BBG_RV: r += RV_AN + AV_AN
        return r

    def est_grenz(zve):
        zve = max(0, zve)
        if zve <= GFB:  return 0.0
        elif zve <= Z2:
            y = (zve - GFB) / 10_000
            return (2 * 932.30 * y + 1_400) / 10_000
        elif zve <= Z3:
            z = (zve - Z2) / 10_000
            return (2 * 176.64 * z + 2_397) / 10_000
        elif zve <= REICH: return 0.42
        else:              return 0.45

    def est_betrag(zve):
        zve = max(0, zve)
        if zve <= GFB:  return 0.0
        elif zve <= Z2:
            y = (zve - GFB) / 10_000; return (932.30 * y + 1_400) * y
        elif zve <= Z3:
            z = (zve - Z2) / 10_000; return (176.64 * z + 2_397) * z + 1_015.13
        elif zve <= REICH: return 0.42 * zve - 10_911.83
        else:              return 0.45 * zve - 19_246.61

    def soli_grenz(zve, em):
        est = est_betrag(zve)
        if est <= SF: return 0.0
        if 0.119 * (est - SF) < 0.055 * est: return 0.119 * em
        return 0.055 * em

    def de_marginal_an(mult):
        """Grenzbelastung AN-Sicht (ESt+Soli+AN-SV) inkl. Vorsorgeaufwendungen-Deckelung"""
        b    = max(mult * APW, 1.0)
        kv_pv_g = (KV_AN + PV_AN) if b <= BBG_KV else 0.0
        rv_av_g = (RV_AN + AV_AN) if b <= BBG_RV else 0.0
        sv_g = kv_pv_g + rv_av_g
    
        # Tatsächlicher ZvE-Abzug: Basis-KV (96%) und PV unbeschränkt. 
        # Der Rest (AV, 4% KV) ist im 1.900€ Deckel verpufft, da Basis-KV diesen sofort sprengt.
        rv_betrag = min(b, BBG_RV) * RV_AN
        kv_basis_betrag = min(b, BBG_KV) * (KV_AN * 0.96 + PV_AN)
    
        zve = max(0, b - (rv_betrag + kv_basis_betrag) - WERBUNG)
    
        em   = est_grenz(zve)
        sm   = soli_grenz(zve, em)
    
        # Marginal-Derivat: Nur RV + Basis-KV sind an der Grenze abzugsfähig
        sv_g_deductible = 0.0
        if b <= BBG_RV: sv_g_deductible += RV_AN
        if b <= BBG_KV: sv_g_deductible += (KV_AN * 0.96 + PV_AN)
        
        return (sv_g + (em + sm) * (1.0 - sv_g_deductible)) * 100.0

    def de_average_an(mult):
        """Durchschnittsbelastung AN-Sicht (ESt+Soli+AN-SV) / Brutto"""
        b = max(mult * APW, 1.0)
    
        # Tatsächliche SV-Beiträge
        sv_betrag = min(b, BBG_KV) * (KV_AN + PV_AN) + min(b, BBG_RV) * (RV_AN + AV_AN)
    
        # Abzugsaufwendungen für ZvE
        rv_deductible = min(b, BBG_RV) * RV_AN
        kv_basis_deductible = min(b, BBG_KV) * (KV_AN * 0.96 + PV_AN)
        zve = max(0, b - (rv_deductible + kv_basis_deductible) - WERBUNG)
    
        em_betrag = est_betrag(zve)
    
        # Soli
        soli = 0.0
        if em_betrag > SF:
            soli = min(0.119 * (em_betrag - SF), 0.055 * em_betrag)
        
        return (sv_betrag + em_betrag + soli) / b * 100.0


    # ══════════════════════════════════════════════════════════════════════════════
    # OECD-LÄNDER: Formelbasierte Grenzbelastung (ESt + AN-SV, 2025)
    # Jedes Land: eigener AW, eigene Steuerformel, eigene SV-Grenzen
    # ══════════════════════════════════════════════════════════════════════════════

    # ── USA 2025 ──────────────────────────────────────────────────────────────────
    # Federal brackets (single, 2025): 10/12/22/24/32/35/37 %
    # FICA: SS 6.2% (BBG $176,100) + Medicare 1.45% + add. Medicare 0.9% (>$200k)
    # Standard deduction $15,700; AW ≈ $82,933
    _US_AW = 82_933
    _US_SD = 15_700
    _US_BRACKETS = [(11_925, 0.10), (48_475, 0.12), (103_350, 0.22),
                    (201_775, 0.24), (256_225, 0.32), (640_600, 0.35),
                    (float('inf'), 0.37)]
    _US_SS_BBG = 176_100
    def marginal_us(mult):
        b = max(mult * _US_AW, 1.0)
    
        def calc_us_net_tax(inc):
            # 1. FICA (Social Security + Medicare)
            ss = min(inc, _US_SS_BBG) * 0.062
            mc = inc * 0.0145
            if inc > 200_000:
                mc += (inc - 200_000) * 0.009  # Additional Medicare 0.9%
        
            # 2. Federal Income Tax (progressive brackets)
            ti = max(0, inc - _US_SD)
            tax_fed = 0.0
            prev_top = 0.0
            for top, rate in _US_BRACKETS:
                if ti > prev_top:
                    tax_fed += (min(ti, top) - prev_top) * rate
                prev_top = top
            
            # 3. State Income Tax: Michigan 4.25% flat (OECD reference city Detroit)
            # Consistent with other countries including sub-central taxes
            tax_state = max(0.0, inc - 5_400) * 0.0425  # MI personal exemption ~$5,400
        
            return ss + mc + tax_fed + tax_state
    
        return (calc_us_net_tax(b + 1.0) - calc_us_net_tax(b)) * 100.0

    # ── Frankreich 2025 ───────────────────────────────────────────────────────────
    # Barème IR 2025: 0/11/30/41/45 %
    # AN-SV: CSG 9.2%×98.25% + CRDS 0.5%×98.25% + Vieillesse déplafonnée 0.40%
    #         + Vieillesse plafonnée 6.90% (≤1 PSS=47,100€) + Autonomie 0.30%
    # AW ≈ €43,356
    _FR_AW = 43_356
    _FR_PSS = 47_100
    _FR_BRACKETS = [(11_600, 0.00), (29_579, 0.11), (84_577, 0.30),
                    (181_917, 0.41), (float('inf'), 0.45)]
    def marginal_fr(mult):
        b = max(mult * _FR_AW, 1.0)
    
        def calc_fr_net_tax(inc):
            # 1. AN social contributions (Amounts)
            csg_crds_base = inc * 0.9825 # Simplified: applies up to 4 PSS, assume full for simplicity
            csg_ded = csg_crds_base * 0.068
            csg_nded = csg_crds_base * (0.024 + 0.005)
        
            vieil_depl = inc * (0.004 + 0.003)
            vieil_plaf = min(inc, _FR_PSS) * 0.069
        
            # AGIRC-ARRCO (Complémentaire retraite)
            # Tranche 1: <= 1 PSS (~4.01% AN)
            # Tranche 2: 1 PSS - 8 PSS (~9.86% AN)
            t1 = min(inc, _FR_PSS)
            t2 = max(0, min(inc, 8 * _FR_PSS) - _FR_PSS)
            agirc_arrco = t1 * 0.0401 + t2 * 0.0986
        
            # Prévoyance & Mutuelle (approx 0.78%)
            prevoyance = inc * 0.0078
        
            # Sums
            sv_total = csg_ded + csg_nded + vieil_depl + vieil_plaf + agirc_arrco + prevoyance
            # French payslip law: ALL mandatory employee contributions are deducted
            # from gross to get net imposable, EXCEPT CSG non-déductible and CRDS.
            # vieil_plaf, AGIRC-ARRCO, prévoyance ARE all deductible.
            sv_deductible = csg_ded + vieil_depl + vieil_plaf + agirc_arrco + prevoyance
        
            # 2. Income Tax Base
            net_imp = inc - sv_deductible
            abattement = min(max(net_imp * 0.10, 471), 14_171) # 10% allowance has min and max
            rni = max(0.0, net_imp - abattement)
        
            # 3. Barème IR (Income Tax)
            tax = 0.0
            prev_top = 0.0
            for top, rate in _FR_BRACKETS:
                if rni > prev_top:
                    tax += (min(rni, top) - prev_top) * rate
                prev_top = top
            
            # 4. CEHR (Surtax on high incomes)
            cehr = 0.0
            if rni > 500_000:
                cehr = (500_000 - 250_000) * 0.03 + (rni - 500_000) * 0.04
            elif rni > 250_000:
                cehr = (rni - 250_000) * 0.03
            
            return sv_total + tax + cehr
        
        return (calc_fr_net_tax(b + 1.0) - calc_fr_net_tax(b)) * 100.0

    # ── Dänemark 2025 ─────────────────────────────────────────────────────────────
    # AM-bidrag 8% (auf Brutto, VOR Einkommensteuer)
    # Bundskat 12.01% + Kommunalskat ~25.1% + ggf. Topskat 15%
    # Personfradrag 51,600 DKK; Topskat ab 611,800 DKK (nach AM)
    # Skatteloft 52.07% (ohne AM) → max. Grenz-ESt 52.07%
    # AW ≈ DKK 490,000 (OECD Schätzung 2024)
    _DK_AW = 490_000
    _DK_FRADRAG = 51_600
    _DK_TOPSKAT_GRENZE = 611_800  # nach AM-bidrag
    _DK_BUND = 0.1201
    _DK_KOMM = 0.251
    _DK_TOP  = 0.15
    _DK_LOFT = 0.5207  # Skatteloft (ohne AM)
    def marginal_dk(mult):
        b = max(mult * _DK_AW, 1.0)
    
        def calc_dk_net_tax(inc):
            # 1. AM-bidrag (Labour market contribution, purely on gross!)
            am_tax = inc * 0.08
            after_am = inc - am_tax
        
            # 2. Beschäftigungsabzug (Beskæftigelsesfradrag) ~ 10.65%, max ca. 45.100 DKK
            # Only reduces the basis for Kommune tax.
            besk = min(after_am * 0.1065, 45_100)
        
            # 3. Taxable Bases
            # Crucial Modification: Personfradrag is a direct baseline deduction!
            base_bund = max(0.0, after_am - _DK_FRADRAG)
            base_komm = max(0.0, after_am - besk - _DK_FRADRAG)
        
            # 4. Compute Sub-Taxes
            tax_bund = base_bund * _DK_BUND
            tax_komm = base_komm * _DK_KOMM
        
            # 5. Topskat
            tax_top = max(0.0, after_am - _DK_TOPSKAT_GRENZE) * _DK_TOP
        
            # 6. Skatteloft Check
            # The marginal rate on "after_am" is capped at 52.07%. 
            # For our net total simulation, we cap the sum of Bund+Komm+Top rates explicitly.
            # But modeling it in absolute numbers:
            total_income_tax = tax_bund + tax_komm + tax_top
        
            # Simulate ceiling constraint roughly 
            theoretical_ceiling_tax = max(0.0, after_am - _DK_FRADRAG) * _DK_LOFT
            if total_income_tax > theoretical_ceiling_tax:
                tax_top -= (total_income_tax - theoretical_ceiling_tax) # Topskat is reduced if ceiling hit
                total_income_tax = theoretical_ceiling_tax
            
            return am_tax + total_income_tax

        return (calc_dk_net_tax(b + 1.0) - calc_dk_net_tax(b)) * 100.0

    # ── Schweiz 2025 (Kanton Zürich, Stadt Zürich als Referenz) ───────────────────
    # Bundessteuer max. eff. 11.5%, Kanton+Gemeinde Zürich ~24-28% progressiv
    # AHV/IV/EO AN: 5.30%, ALV AN: 1.10% (bis CHF 148,200)
    # AW ≈ CHF 96,846
    _CH_AW = 96_846
    _CH_AHV_AN = 0.053
    _CH_ALV_AN = 0.011
    _CH_ALV_BBG = 148_200
    # Vereinfachte progressive Bundessteuer + Zürich Kantonal/Gemeinde
    # (Näherung anhand effektiver Grenzsteuersätze Zürich Stadt)
    _CH_BRACKETS = [(18_500, 0.0), (33_200, 0.02), (45_000, 0.06),
                    (60_000, 0.10), (80_000, 0.16), (110_000, 0.22),
                    (150_000, 0.28), (200_000, 0.32), (300_000, 0.35),
                    (float('inf'), 0.36)]
    def marginal_ch(mult):
        b = max(mult * _CH_AW, 1.0)
    
        def calc_ch_net_tax(inc):
            # 1. Social Insurance
            ahv = inc * _CH_AHV_AN
            alv = min(inc, _CH_ALV_BBG) * _CH_ALV_AN
            sv_total = ahv + alv
        
            # 2. Tax Base Deductions (Zürich)
            # Berufsauslagen (Professional expenses): 3% of income, min 2,000, max 4,000
            berufs = min(max(inc * 0.03, 2_000), 4_000)
            # Versicherungsabzug (Insurance deduction): ~2,600 CHF
            versicherung = 2_600
            # Social insurance is fully deductible
            taxable = max(0.0, inc - berufs - versicherung - sv_total)
        
            # 3. Combined progressive tax (Federal + Kanton Zürich + Gemeinde)
            tax = 0.0
            prev_top = 0.0
            for top, rate in _CH_BRACKETS:
                if taxable > prev_top:
                    tax += (min(taxable, top) - prev_top) * rate
                prev_top = top
        
            return sv_total + tax
    
        return (calc_ch_net_tax(b + 1.0) - calc_ch_net_tax(b)) * 100.0

    # ── Schweden 2025 ─────────────────────────────────────────────────────────────
    # Kommunalskatt ~32.41%, statlig inkomstskatt 20% ab SEK 625,800
    # AN-Pensionsavgift 7% (BBG SEK 604,500)
    # AW ≈ SEK 529,659
    _SE_AW = 529_659
    _SE_KOMM = 0.3241
    _SE_STAT = 0.20
    _SE_STAT_GRENZE = 625_800
    _SE_PENSION_AN = 0.07
    _SE_PENSION_BBG = 604_500
    def marginal_se(mult):
        b = max(mult * _SE_AW, 1.0)
    
        def calc_se_net_tax(inc):
            pension_fee = min(inc, _SE_PENSION_BBG) * 0.07
        
            # 1. Grundavdrag (GA) - Basic Deduction
            pbb = 57_300 # Exact Prisbasbelopp (PBB) for 2024/2025 actual parameter tracking
            if inc <= 0.99 * pbb:
                ga = 0.423 * pbb
            elif inc <= 2.72 * pbb:
                ga = 0.423 * pbb + 0.20 * (inc - 0.99 * pbb)
            elif inc <= 3.11 * pbb:
                ga = 0.77 * pbb
            elif inc <= 7.88 * pbb:
                ga = 0.77 * pbb - 0.10 * (inc - 3.11 * pbb)
            else:
                ga = 0.293 * pbb
            ga = min(ga, inc)
        
            # 2. Tax Base
            # Crucial Correction: Pension fee is given as a skattereduktion (tax credit),
            # so it MUST NOT be actively deducted from the tax base here! (No double counting)
            tax_base = max(0.0, inc - ga)
        
            # 3. Gross Taxes
            tax_komm = tax_base * _SE_KOMM
            tax_stat = max(0.0, tax_base - _SE_STAT_GRENZE) * _SE_STAT
            tax_total = tax_komm + tax_stat
        
            # 4. Jobbskatteavdrag (JSA) - Skatteverket official formula (IL 67 kap)
            # JSA approximates the kommunalskatt that would be paid on earned income,
            # effectively making low-to-middle earners pay near-zero kommunalskatt.
            # The formula uses "beskattningsbar förvärvsinkomst" (taxable earned income)
            s = _SE_KOMM  # kommunalskattesats
            bfi = tax_base  # beskattningsbar förvärvsinkomst = inc - ga
        
            # IL 67 kap: statutory coefficients 0.332/0.111 are FRACTIONS of kommunalskattesats
            # i.e., actual rate = coefficient × s, not the raw coefficient
            c2 = 0.332 * s  # Phase 2 effective rate ~10.8%
            c3 = 0.111 * s  # Phase 3 effective rate ~3.6%
            if inc <= 0.91 * pbb:
                jsa_calc = max(0.0, bfi) * s
            elif inc <= 3.24 * pbb:
                jsa_calc = min(0.91 * pbb, bfi) * s + max(0.0, bfi - 0.91 * pbb) * c2
            elif inc <= 8.08 * pbb:
                jsa_p2 = min(0.91 * pbb, bfi) * s + max(0.0, min(bfi, 3.24 * pbb) - 0.91 * pbb) * c2
                jsa_calc = jsa_p2 + max(0.0, bfi - 3.24 * pbb) * c3
            elif inc <= 13.54 * pbb:
                jsa_p2 = min(0.91 * pbb, bfi) * s + max(0.0, min(bfi, 3.24 * pbb) - 0.91 * pbb) * c2
                jsa_calc = jsa_p2 + max(0.0, min(bfi, 8.08 * pbb) - 3.24 * pbb) * c3
            else:
                jsa_p2 = min(0.91 * pbb, bfi) * s + max(0.0, min(bfi, 3.24 * pbb) - 0.91 * pbb) * c2
                jsa_plateau = jsa_p2 + max(0.0, min(bfi, 8.08 * pbb) - 3.24 * pbb) * c3
                jsa_calc = jsa_plateau - 0.03 * (inc - 13.54 * pbb)
        
            # JSA cannot exceed the total kommunalskatt on earned income
            jsa = max(0.0, min(jsa_calc, tax_komm))
        
            # 5. Skattereduktion för allmän pensionsavgift 
            pension_credit = pension_fee 
        
            # Net tax calculation (Credits cannot reduce tax below 0)
            net_inc_tax = max(0.0, tax_total - jsa - pension_credit)
        
            return pension_fee + net_inc_tax
        
        return (calc_se_net_tax(b + 1.0) - calc_se_net_tax(b)) * 100.0

    # ── Polen 2025 ────────────────────────────────────────────────────────────────
    # PIT: 12% (≤PLN 120,000) / 32% (darüber), Freibetrag PLN 30,000
    # AN-ZUS: Emerytura 9.76% + Renta 1.5% + Chorobowe 2.45% = 13.71%
    # ZUS-BBG (Emerytura+Renta): ~PLN 260,190 (30× Durchschnittslohn)
    # Zdrowotna (Gesundheit): 9% ohne Obergrenze, nicht absetzbar
    # AW ≈ PLN 91,625
    _PL_AW = 91_625
    _PL_ZUS_RATE = 0.0976 + 0.015 + 0.0245   # 13.71%
    _PL_ZUS_BBG = 260_190
    _PL_ZDROW = 0.09    # Gesundheitsversicherung, ohne Obergrenze
    _PL_FREI = 30_000
    _PL_GRENZE_32 = 120_000
    def marginal_pl(mult):
        b = max(mult * _PL_AW, 1.0)
    
        def calc_pl_net_tax(inc):
            # 1. ZUS Contributions (Deductible from tax base)
            zus_betrag = min(inc, _PL_ZUS_BBG) * _PL_ZUS_RATE
        
            # 2. Zdrowotna (Health Insurance, 9%) on income AFTER ZUS deduction, NON-deductible
            # Polski Ład 2022: base = gross - ZUS contributions
            zdrow = max(0.0, inc - zus_betrag) * _PL_ZDROW
        
            # 3. PIT Base
            pit_basis = max(0.0, inc - zus_betrag)
        
            # 4. PIT Calculation
            if pit_basis <= _PL_FREI:
                tax = 0.0
            elif pit_basis <= _PL_GRENZE_32:
                tax = max(0.0, pit_basis - _PL_FREI) * 0.12 # 30,000 allowance is tax free
            else:
                tax = max(0.0, _PL_GRENZE_32 - _PL_FREI) * 0.12 + (pit_basis - _PL_GRENZE_32) * 0.32
            
            return zus_betrag + zdrow + tax

        return (calc_pl_net_tax(b + 1.0) - calc_pl_net_tax(b)) * 100.0

    # ── Niederlande 2025 ──────────────────────────────────────────────────────────
    # Box 1: Schijf 1 35.82% (≤€38,441), Schijf 2 37.48% (≤€76,817), Schijf 3 49.50%
    # Die 35.82% enthalten bereits Volksverzekeringen (AOW 17.90%+ANW 0.10%+WLZ 9.65%)
    # Keine separate AN-SV neben den integrierten Prämien
    # AN-Beitrag ZVW (Zorgverzekering): 5.26% (bereits in Box 1 Tarif integriert)
    # AW ≈ €58,248
    _NL_AW = 58_248
    def marginal_nl(mult):
        b = max(mult * _NL_AW, 1.0)
    
        def calc_nl_net_tax(inc):
            # 1. Box 1 Stat Tax
            if inc <= 38_441:
                tax = inc * 0.3582
            elif inc <= 76_817:
                tax = 38_441 * 0.3582 + (inc - 38_441) * 0.3748
            else:
                tax = 38_441 * 0.3582 + (76_817 - 38_441) * 0.3748 + (inc - 76_817) * 0.4950
            
            # 2. Algemene Heffingskorting (AHK)
            ahk = 3_068.0 - max(0.0, (inc - 24_814) * 0.0663)
            ahk = max(0.0, ahk)
        
            # 3. Arbeidskorting (AK) - utilizing the precise ~43.7% Opbouw logic 
            ak = 0.0
            if inc <= 11_490:
                ak = inc * 0.0842
            elif inc <= 24_814:
                ak = 11_490 * 0.0842 + (inc - 11_490) * 0.30
            elif inc <= 39_957:
                ak = 11_490 * 0.0842 + (24_814 - 11_490) * 0.30 + (inc - 24_814) * 0.0247
            elif inc <= 43_071:
                ak = 11_490 * 0.0842 + (24_814 - 11_490) * 0.30 + (39_957 - 24_814) * 0.0247
            else:
                max_ak = 11_490 * 0.0842 + (24_814 - 11_490) * 0.30 + (39_957 - 24_814) * 0.0247
                ak = max_ak - max(0.0, (inc - 43_071) * 0.0651)
            ak = max(0.0, ak)
        
            # Tax credits are NON-refundable
            # reduce the income tax to 0.
            return max(0.0, tax - ahk - ak)
        
        # Numeric derivative: The flawless reflection of true marginal burden
        return (calc_nl_net_tax(b + 1.0) - calc_nl_net_tax(b)) * 100.0

    # ── Japan 2025 ────────────────────────────────────────────────────────────────
    # Nationale ESt: 5/10/20/23/33/40/45% + 2.1% Surtax
    # Wohnsteuer (Jūminzei): ~10% flat
    # AN-SV: Kosei Nenkin 9.15% (BBG ~JPY 650,000/Monat = JPY 7,800,000/Jahr)
    #         Kenko Hoken ~5.0% + Kaigo ~0.91% (40+) + Koyo 0.6%
    # AW ≈ JPY 5,003,351
    _JP_AW = 5_003_351
    _JP_NENKIN_RATE = 0.0915
    _JP_NENKIN_BBG = 7_800_000   # Kosei Nenkin BBG
    _JP_KENKO_RATE = 0.05 + 0.0091 # Health + Kaigo
    _JP_KENKO_BBG = 16_680_000   # Kenko Hoken BBG (approx 1.39M * 12)
    _JP_KOYO_RATE = 0.006        # Employment insurance (no ceiling)
    _JP_BRACKETS = [(1_950_000, 0.05), (3_300_000, 0.10), (6_950_000, 0.20),
                    (9_000_000, 0.23), (18_000_000, 0.33), (40_000_000, 0.40),
                    (float('inf'), 0.45)]
    _JP_SURTAX = 0.021  # Wiederaufbausteuer
    _JP_JUMIN = 0.10    # Wohnsteuer
    # Einkommensabzug (kyuyo shotoku kojo) vereinfacht
    def _jp_employment_deduction(b):
        if b <= 1_625_000: return 650_000
        elif b <= 1_800_000: return b * 0.4 - 100_000
        elif b <= 3_600_000: return b * 0.3 + 80_000
        elif b <= 6_600_000: return b * 0.2 + 440_000
        elif b <= 8_500_000: return b * 0.1 + 1_100_000
        else: return 1_950_000

    def _jp_employment_deduction_deriv(b):
        if b <= 1_625_000: return 0.0
        elif b <= 1_800_000: return 0.4
        elif b <= 3_600_000: return 0.3
        elif b <= 6_600_000: return 0.2
        elif b <= 8_500_000: return 0.1
        else: return 0.0

    def marginal_jp(mult):
        b = max(mult * _JP_AW, 1.0)
    
        def calc_jp_net_tax(inc):
            # 1. Social Insurance (separate ceilings per branch)
            nenkin = min(inc, _JP_NENKIN_BBG) * _JP_NENKIN_RATE
            kenko = min(inc, _JP_KENKO_BBG) * _JP_KENKO_RATE
            koyo = inc * _JP_KOYO_RATE
            sv_total = nenkin + kenko + koyo
        
            # 2. Employment Income Deduction (給与所得控除)
            ded = _jp_employment_deduction(inc)
        
            # 3. National Tax (所得税)
            # Deductions: Employment deduction + Social insurance (全額控除) + Basic deduction (基礎控除 480,000)
            ti_nat = max(0, inc - ded - sv_total - 480_000)
            tax_nat = 0.0
            prev_top = 0.0
            for top, rate in _JP_BRACKETS:
                if ti_nat > prev_top:
                    tax_nat += (min(ti_nat, top) - prev_top) * rate
                prev_top = top
            tax_nat *= (1 + _JP_SURTAX)  # 復興特別所得税 2.1%
        
            # 4. Residential Tax (住民税) — separate basic deduction of 430,000
            ti_res = max(0, inc - ded - sv_total - 430_000)
            tax_res = ti_res * 0.10  # 市町村民税 6% + 都道府県民税 4%
            # 均等割 (~5,000 JPY per capita levy) omitted for marginal analysis
        
            return sv_total + tax_nat + tax_res
    
        return (calc_jp_net_tax(b + 1.0) - calc_jp_net_tax(b)) * 100.0

    # ══════════════════════════════════════════════════════════════════════════════
    # X-ACHSE & KURVENBERECHNUNG
    # ══════════════════════════════════════════════════════════════════════════════
    x_fine  = np.linspace(0.001, 5.0, 2000)
    de_fine = np.array([de_marginal_an(v) for v in x_fine])
    de_avg_fine = np.array([de_average_an(v) for v in x_fine])

    # Alle OECD-Länder jetzt ebenfalls formelbasiert auf feinem Raster
    us_fine = np.array([marginal_us(v) for v in x_fine])
    fr_fine = np.array([marginal_fr(v) for v in x_fine])
    dk_fine = np.array([marginal_dk(v) for v in x_fine])
    ch_fine = np.array([marginal_ch(v) for v in x_fine])
    se_fine = np.array([marginal_se(v) for v in x_fine])
    pl_fine = np.array([marginal_pl(v) for v in x_fine])
    nl_fine = np.array([marginal_nl(v) for v in x_fine])
    jp_fine = np.array([marginal_jp(v) for v in x_fine])

    # Kapital & Immobilien DE
    KAP_SATZ  = 26.375   # 25 % + 5,5 % Soli
    IMMO_SATZ =  0.0     # >10 Jahre Haltedauer § 23 EStG

    # ══════════════════════════════════════════════════════════════════════════════
    # FIGURE
    # ══════════════════════════════════════════════════════════════════════════════
    fig, ax = plt.subplots(figsize=(16, 9), facecolor=BG)
    ax.set_facecolor(PANEL)
    ax.spines[["left","bottom"]].set_color(SPINE)
    ax.spines[["top","right"]].set_visible(False)

    xlim = (-0.05, 5.55)
    ylim = (-4, 73)

    # ── OECD-Hintergrundkurven (jetzt formelbasiert) ──────────────────────────────
    # Klassische Zeitschriften-Palette: gedeckte, gut unterscheidbare Farben
    OECD_LINES = [
        ("USA",          us_fine, "#2166ac", 1.4, (4, 3)),    # Königsblau
        ("Frankreich",   fr_fine, "#d6604d", 1.4, (6, 2)),    # gedämpftes Rot
        ("Dänemark",     dk_fine, "#1a9850", 1.4, (3, 4)),    # Waldgrün
        ("Schweiz",      ch_fine, "#b35806", 1.4, (5, 2, 1, 2)), # Dunkelorange
        ("Schweden",     se_fine, "#762a83", 1.4, (4, 4)),    # Pflaume
        ("Polen",        pl_fine, "#4393c3", 1.4, (2, 5)),    # Stahlblau
        ("Niederlande",  nl_fine, "#e08214", 1.4, (6, 3)),    # Bernstein
        ("Japan",        jp_fine, "#7b3294", 1.4, (4, 2, 1, 2)), # Indigo
    ]

    # Labelpositionen (x, y-offset) für Zeilenende — dynamisch aus Endwert
    OECD_LABEL_Y = {
        "USA":         (5.0, us_fine[-1]  + 0.3),
        "Frankreich":  (5.0, fr_fine[-1]  + 0.3),
        "Dänemark":    (5.0, dk_fine[-1]  - 2.0),
        "Schweiz":     (5.0, ch_fine[-1]  + 0.3),
        "Schweden":    (5.0, se_fine[-1]  + 0.3),
        "Polen":       (5.0, pl_fine[-1]  + 0.3),
        "Niederlande": (5.0, nl_fine[-1]  - 2.5),
        "Japan":       (5.0, jp_fine[-1]  + 0.3),
    }

    for name, ydata, color, lw, dash in OECD_LINES:
        ax.plot(x_fine, ydata, color=color, lw=lw, linestyle=(0, dash),
                alpha=0.55, zorder=2)
        lx, ly = OECD_LABEL_Y[name]
        ax.text(lx + 0.05, ly, name, color=color,
                fontsize=7.8, va="center", alpha=0.78, clip_on=True)

    # ── Deutschland AN-Kurve (Formel) ─────────────────────────────────────────────
    # Deutschland-Hauptkurve: kräftiges Dunkelrot
    ax.plot(x_fine, de_fine, color="#b2182b", lw=3.0, zorder=8,
            label="Deutschland — Grenzbelastung (Lohn)")
    ax.plot(x_fine, de_avg_fine, color="#b2182b", lw=3.0, linestyle="--", zorder=8,
            label="Deutschland — Durchschnittsbelastung (Lohn)")

    # ── BBG-Sprünge in DE annotieren ──────────────────────────────────────────────
    BBG_KV_x = BBG_KV / APW   # 1.370x
    BBG_RV_x = BBG_RV / APW   # 2.000x

    # KV/PV-Sprung: Rate fällt um ~6,2 PP
    y_before_kv = de_marginal_an(BBG_KV_x - 0.002)
    y_after_kv  = de_marginal_an(BBG_KV_x + 0.002)
    ax.axvline(BBG_KV_x, color="#555555", lw=0.9, ls=":", alpha=0.60, zorder=3)
    ax.annotate(
        f"BBG KV/PV\n({BBG_KV/1000:.0f}k€)\n↓{y_before_kv-y_after_kv:.1f} PP",
        xy=(BBG_KV_x, (y_before_kv + y_after_kv) / 2),
        xytext=(BBG_KV_x - 0.48, 56),
        fontsize=7.8, color="#333333", alpha=0.90,
        arrowprops=dict(arrowstyle="->", color="#555555", lw=0.9,
                        connectionstyle="arc3,rad=0.2"),
        bbox=dict(boxstyle="round,pad=0.25", fc=BG, ec="#888888", alpha=0.85)
    )

    # RV/AV-Sprung: Rate fällt um ~5,6 PP
    y_before_rv = de_marginal_an(BBG_RV_x - 0.002)
    y_after_rv  = de_marginal_an(BBG_RV_x + 0.002)
    ax.axvline(BBG_RV_x, color="#555555", lw=0.9, ls=":", alpha=0.60, zorder=3)
    ax.annotate(
        f"BBG RV/AV\n({BBG_RV/1000:.0f}k€)\n↓{y_before_rv-y_after_rv:.1f} PP",
        xy=(BBG_RV_x, (y_before_rv + y_after_rv) / 2),
        xytext=(BBG_RV_x + 0.12, 57),
        fontsize=7.8, color="#333333", alpha=0.90,
        arrowprops=dict(arrowstyle="->", color="#555555", lw=0.9,
                        connectionstyle="arc3,rad=-0.2"),
        bbox=dict(boxstyle="round,pad=0.25", fc=BG, ec="#888888", alpha=0.85)
    )

    # ── Kapitalertrag-Linie ───────────────────────────────────────────────────────
    ax.axhline(KAP_SATZ, color="#2166ac", lw=1.8, linestyle=(0, (5, 3)), zorder=6,
               label=f"Deutschland — Kapitalertrag (Abgeltungsteuer {KAP_SATZ:.2f}%)")
    ax.text(0.04, KAP_SATZ + 1.2,
            f"Kapitalertrag: {KAP_SATZ:.1f}% flat  (25% KESt + 5,5% Soli)",
            color="#2166ac", fontsize=8.5, va="bottom",
            bbox=dict(boxstyle="round,pad=0.3", fc=BG, ec="#2166ac", alpha=0.80))

    # ── Immobilien-Linie ──────────────────────────────────────────────────────────
    ax.axhline(IMMO_SATZ + 0.4, color="#1a9850", lw=1.4,
               linestyle=(0, (3, 5)), zorder=6,
               label="Deutschland — Immobilien >10 J. (§23 EStG): 0%")
    ax.text(0.04, IMMO_SATZ + 1.8,
            "Immobilien >10 J. (§23 EStG): 0 %  — vollständig steuerfrei",
            color="#1a9850", fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.3", fc=BG, ec="#1a9850", alpha=0.80))

    # ── Scherenpfeil: DE-Lohn vs. Kapital bei 2,5x ────────────────────────────────
    ref_x   = 2.5
    ref_de  = de_marginal_an(ref_x)
    gap     = ref_de - KAP_SATZ
    y_mid   = (ref_de + KAP_SATZ) / 2
    ax.annotate("", xy=(ref_x, KAP_SATZ + 0.5), xytext=(ref_x, ref_de - 0.5),
                arrowprops=dict(arrowstyle="<->", color="#444444", lw=1.0))
    ax.text(ref_x + 0.08, y_mid,
            f"~{gap:.0f} PP\nSchere\nLohn / Kapital",
            color="#333333", fontsize=8, va="center", alpha=0.90,
            bbox=dict(boxstyle="round,pad=0.25", fc=BG, alpha=0.75, ec="#aaaaaa"))

    # ── Referenzlinien APW und BBG ────────────────────────────────────────────────
    ax.axvline(1.0, color="#666666", lw=0.7, ls=":", alpha=0.45, zorder=1)
    ax.text(1.02, ylim[0] + 1.5, f"⌀-Lohn\n({APW/1000:.0f}k€)",
            color="#555555", fontsize=7.5, alpha=0.80, va="bottom")

    # Niedriglohn-Zone schattieren
    ax.axvspan(0, 0.67, color="#aaaaaa", alpha=0.08, zorder=0)
    ax.text(0.02, ylim[1] - 16, "Niedriglohnzone\n(<2/3 Durchschnitt)",
            color="#666666", fontsize=7, alpha=0.65)

    # ── Achsenformatierung ────────────────────────────────────────────────────────
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xlabel("Vielfaches des nationalen Durchschnittslohns (APW-Multiple)  "
                  f"— DE: 1,0x = {APW:,} € p.a. (Quelle: OECD 2024)",
                  fontsize=10, labelpad=10, color=SUBTEXT)
    ax.set_ylabel("Marginale Grenzbelastung [%]\n(Einkommensteuer + AN-Sozialabgaben)",
                  fontsize=10, labelpad=10, color=SUBTEXT)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}x"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(10))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(5))
    ax.tick_params(which="minor", length=3)

    # ── DE-Label am Linienende ────────────────────────────────────────────────────
    de_end = de_marginal_an(5.0)
    ax.text(5.07, de_end,
            "DE Grenz.",
            color="#b2182b", fontsize=9, fontweight="bold", va="center",
            bbox=dict(boxstyle="round,pad=0.3", fc=BG, ec="#b2182b", alpha=0.85))

    de_avg_end = de_average_an(5.0)
    ax.text(5.07, de_avg_end,
            "DE Durchschn.",
            color="#b2182b", fontsize=9, fontweight="bold", va="center",
            bbox=dict(boxstyle="round,pad=0.3", fc=BG, ec="#b2182b", alpha=0.85, linestyle="--"))

    # ── Legende ───────────────────────────────────────────────────────────────────
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    leg_handles = [
        Line2D([0],[0], color="#b2182b", lw=2.8,
               label="Deutschland — Grenzbelastung (Marginal: ESt + AN-SV)"),
        Line2D([0],[0], color="#b2182b", lw=2.8, linestyle="--",
               label="Deutschland — Durchschnittsbelastung (Effektiv: ESt + AN-SV)"),
        Line2D([0],[0], color="#2166ac", lw=1.8, linestyle=(0,(5,3)),
               label=f"Deutschland — Kapitalertrag ({KAP_SATZ:.2f}% flat)"),
        Line2D([0],[0], color="#1a9850", lw=1.4, linestyle=(0,(3,5)),
               label="Deutschland — Immobilien >10 J. (0%)"),
        Line2D([0],[0], color="#888888", lw=1.2, linestyle="--", alpha=0.7,
               label="OECD-Länder (gestrichelt)"),
    ]
    legend = ax.legend(
        handles=leg_handles,
        loc="upper left",
        framealpha=0.80,
        edgecolor="#cccccc",
        facecolor=BG,
        fontsize=9,
        handlelength=2.8,
        labelspacing=0.6,
    )
    for text in legend.get_texts():
        text.set_color(TEXTC)

    # ── Titel & Quellenzeile ──────────────────────────────────────────────────────
    fig.suptitle(
        "Marginale Lohnsteuerbelastung im OECD-Vergleich (2025)",
        fontsize=14, fontweight="bold", color="#1a1a1a", y=0.995, 
    )

    # ── Autor ─────────────────────────────────────────────────────────────────────
    fig.text(0.99, 0.01, "© Linying Li", ha="right", va="bottom",
             fontsize=10, color="#555555", alpha=0.80, style="italic")

    plt.tight_layout(rect=[0, 0, 1, 0.975])

    outpath = "/Users/lilinying/Downloads/abb4_oecd_vergleich.png"
    plt.savefig(outpath, dpi=DPI, bbox_inches="tight", facecolor=BG, edgecolor="none")
    plt.savefig(outpath.replace(".png",".pdf"), bbox_inches="tight", facecolor=BG, edgecolor="none")
    print(f"Gespeichert: {outpath}")

    # ── Abschlusskontrolle ────────────────────────────────────────────────────────
    print("\n── Kontrollwerte DE (korrigiert) ──")
    for m in [0.25, 0.50, 1.00, BBG_KV/APW, BBG_RV/APW, 2.50, 5.00]:
        print(f"  {m:.3f}x ({m*APW:>7,.0f}€): {de_marginal_an(m):.1f}%")

    print("\n── Kontrollwerte OECD-Länder bei 1.0x AW ──")
    for name, fn in [("USA", marginal_us), ("Frankreich", marginal_fr),
                     ("Dänemark", marginal_dk), ("Schweiz", marginal_ch),
                     ("Schweden", marginal_se), ("Polen", marginal_pl),
                     ("Niederlande", marginal_nl), ("Japan", marginal_jp)]:
        vals = [fn(m) for m in [0.5, 1.0, 2.0, 5.0]]
        print(f"  {name:12s}: 0.5x={vals[0]:5.1f}%  1.0x={vals[1]:5.1f}%  2.0x={vals[2]:5.1f}%  5.0x={vals[3]:5.1f}%")



if __name__ == "__main__":
    figur_1_einkommen()
    figur_2_lohnverbleibsquote()
    figur_3_wasserfall()
    figur_4_oecd()
    print("Fertig(%d dpi)" % DPI)
