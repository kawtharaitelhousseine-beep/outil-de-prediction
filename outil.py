"""
=============================================================================
  OUTIL PAT — Système d'Aide à la Décision
  Base CFD : Warman 10/8 M | D2=549mm | H_BEP=37.27m | Q_BEP=905.7 m³/h
  PFE 2025-2026 | EMI | Weir Minerals North Africa
  streamlit run outil.py
  pip install streamlit numpy pandas matplotlib fpdf2
=============================================================================
"""
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle

st.set_page_config(
    page_title="Outil PAT — EMI × Weir Minerals",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'Exo 2',sans-serif;background:#ffffff;}
::-webkit-scrollbar{width:6px;}
::-webkit-scrollbar-track{background:#e2e8f0;}
::-webkit-scrollbar-thumb{background:#4a90d9;border-radius:3px;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#f0f4f8 0%,#e8eef5 100%) !important;border-right:1px solid rgba(46,117,182,0.20) !important;}
section[data-testid="stSidebar"] *{color:#1a2a3a !important;}
section[data-testid="stSidebar"] h2{color:#1565c0 !important;font-size:.85rem !important;letter-spacing:2px;text-transform:uppercase;}
section[data-testid="stSidebar"] label{color:#2c5282 !important;font-size:.8rem !important;}
section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"]{background:#2E75B6 !important;box-shadow:0 0 8px #2E75B6 !important;}
.main .block-container{background:#ffffff;background-image:radial-gradient(ellipse 80% 40% at 50% -10%,rgba(46,117,182,0.08) 0%,transparent 60%),repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(46,117,182,0.03) 40px),repeating-linear-gradient(90deg,transparent,transparent 39px,rgba(46,117,182,0.03) 40px);padding-top:1.5rem !important;}
.hero{position:relative;overflow:hidden;background:linear-gradient(135deg,#e8f0fe 0%,#dbeafe 45%,#bfdbfe 100%);border:1px solid rgba(37,99,235,0.25);border-radius:4px;padding:32px 44px;margin-bottom:24px;box-shadow:0 0 40px rgba(46,117,182,0.15),inset 0 1px 0 rgba(79,195,247,0.1);}
.hero::before{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background:repeating-linear-gradient(90deg,transparent 0px,transparent 48px,rgba(79,195,247,0.03) 48px,rgba(79,195,247,0.03) 49px);pointer-events:none;}
.hero-tag{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:.62rem;letter-spacing:3px;text-transform:uppercase;color:#1565c0;border:1px solid rgba(21,101,192,0.35);padding:3px 12px;border-radius:2px;margin-bottom:12px;background:rgba(21,101,192,0.07);}
.hero h1{font-size:2rem;font-weight:800;margin:0 0 8px 0;color:#1e3a5f;letter-spacing:-0.5px;line-height:1.1;}
.hero h1 span{background:linear-gradient(90deg,#4FC3F7,#2E75B6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero-line{width:48px;height:2px;background:linear-gradient(90deg,#4FC3F7,transparent);margin:10px 0;}
.hero-sub{font-size:.73rem;color:rgba(30,58,95,0.55);font-family:'JetBrains Mono',monospace;letter-spacing:.8px;}
.kpi{background:linear-gradient(145deg,#ffffff,#f0f6ff);border:1px solid rgba(46,117,182,0.25);border-radius:4px;padding:16px 14px;text-align:center;position:relative;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.4);}
.kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#2E75B6,transparent);}
.kpi-g::before{background:linear-gradient(90deg,transparent,#00c853,transparent);}
.kpi-r::before{background:linear-gradient(90deg,transparent,#ff1744,transparent);}
.kpi-o::before{background:linear-gradient(90deg,transparent,#ff6d00,transparent);}
.kpi-p::before{background:linear-gradient(90deg,transparent,#aa00ff,transparent);}
.kv{font-size:1.7rem;font-weight:800;color:#1a2a3a;font-family:'Exo 2',sans-serif;}
.kpi-g .kv{color:#00e676;}.kpi-r .kv{color:#ff5252;}.kpi-o .kv{color:#ff9100;}.kpi-p .kv{color:#e040fb;}
.ku{font-size:.68rem;color:rgba(50,90,140,0.65);margin-top:3px;font-family:'JetBrains Mono',monospace;}
.kl{font-size:.6rem;font-weight:600;color:rgba(21,101,192,0.75);text-transform:uppercase;letter-spacing:2px;margin-bottom:4px;font-family:'JetBrains Mono',monospace;}
.sh{color:#1565c0;font-size:.78rem;font-weight:700;border-bottom:1px solid rgba(21,101,192,0.2);padding-bottom:6px;margin:18px 0 12px 0;text-transform:uppercase;letter-spacing:2px;font-family:'JetBrains Mono',monospace;}
.ad{background:rgba(255,23,68,0.07);border-left:3px solid #ff1744;border-radius:2px;padding:12px 16px;margin:8px 0;color:#ffcdd2;}
.aw{background:rgba(255,160,0,0.07);border-left:3px solid #ffa000;border-radius:2px;padding:12px 16px;margin:8px 0;color:#ffe082;}
.aok{background:rgba(0,200,83,0.07);border-left:3px solid #00c853;border-radius:2px;padding:12px 16px;margin:8px 0;color:#b9f6ca;}
.loss-box{background:linear-gradient(135deg,#1a0608,#3d0d10);border-radius:4px;padding:18px 22px;text-align:center;color:white;margin:10px 0;border:1px solid rgba(255,23,68,0.2);}
.gain-box{background:linear-gradient(135deg,#061a0c,#0d3d18);border-radius:4px;padding:18px 22px;text-align:center;color:white;margin:10px 0;border:1px solid rgba(0,200,83,0.2);}
.stTabs [data-baseweb="tab-list"]{background:transparent;gap:4px;}
.stTabs [data-baseweb="tab"]{background:#e8eef5 !important;color:#2c5282 !important;border:1px solid rgba(46,117,182,0.25) !important;border-radius:3px !important;font-size:.78rem;letter-spacing:1px;font-family:'JetBrains Mono',monospace;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#1565c0,#1e88e5) !important;color:#ffffff !important;border-color:rgba(79,195,247,0.4) !important;}
hr{border-color:rgba(46,117,182,0.20) !important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="hero-tag">⚡ PFE 2025–2026 · EMI · Weir Minerals North Africa</div>
  <h1>Système d'Aide à la Décision <span>PAT</span></h1>
  <div class="hero-line"></div>
  <div class="hero-sub">CFD ANSYS CFX · SST k-ω · Warman 10/8 M · D₂=549mm · H_BEP=37.27m · Q_BEP=905.7 m³/h</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🏭 Réseau")
    Q_reseau  = st.number_input("Débit réseau Q (m³/h)",         value=864.9,  step=10.0,  min_value=50.0)
    dP_total  = st.number_input("ΔP total réseau (bar)",          value=45.0,   step=0.5,   min_value=1.0)
    dP_disque = st.number_input("ΔP disque de dissipation (bar)", value=10.0,   step=0.5,   min_value=0.0,
                                 help="Pression absorbée par l'orifice — le reste est utile pour les PATs")
    rho       = st.number_input("Densité pulpe ρ (kg/m³)",        value=1590.0, step=10.0)

    st.markdown("---")
    st.markdown("## 🔵 Base CFD — Warman 10/8 M")
    st.caption("Valeurs issues de la simulation ANSYS CFX")
    Q_bep   = st.number_input("Q_BEP CFD (m³/h)", value=905.7, step=10.0)
    H_bep   = st.number_input("H_BEP CFD (m)",    value=37.27, step=0.1)
    eta_h   = st.number_input("ηh CFD BEP (%)",   value=69.28, step=0.1) / 100
    E0      = 1.97e-8
    st.markdown(f"**Érosion P24 CFD :** `{E0:.2e}` kg/m²·s")
    st.caption("Valeur fixe — sera scalée avec S et K")
    D2_base = 549.0
    N_base  = 715.0

    st.markdown("---")
    st.markdown("## ⚙️ Rendements")
    eta_v    = st.slider("η volumétrique", 0.80, 1.00, 0.91, 0.01)
    eta_elec = st.slider("η électrique",   0.80, 1.00, 0.95, 0.01)

    st.markdown("---")
    st.markdown("## 🔧 Matériau & Érosion")
    MATS = {
        "Linatex® (Weir)":     {"rho_m": 960,  "f": 1.00, "c": "#2E75B6"},
        "Vulco® (Weir)":       {"rho_m": 1050, "f": 0.85, "c": "#2E7D32"},
        "Ultrachrome® (Weir)": {"rho_m": 7650, "f": 0.45, "c": "#E65100"},
        "Fonte au chrome":     {"rho_m": 7800, "f": 0.48, "c": "#6A0DAD"},
    }
    mat_sel  = st.selectbox("Matériau", list(MATS.keys()))
    ep_sac   = st.slider("Épaisseur sacrificielle (mm)", 5, 30, 20, 1)
    EP_MIN   = st.slider("Seuil sécurité minimum (mm)",  3, 15,  5, 1)
    K_local  = st.slider("Facteur sévérité K",           1, 50, 15, 1,
                          help="K=15 typique pulpe abrasive OCP")
    tarif    = st.number_input("Tarif élec. (MAD/kWh)", value=1.10, step=0.05)
    H_AN     = st.number_input("Heures fonct./an",      value=8000, step=100)

    
    st.markdown("---")
    st.markdown("## 🛒 TCO Matériaux")
    COUT_MAT = {
        "Linatex® (Weir)":     {"prix_set": 45_000,  "tps_pose_h": 8},
        "Vulco® (Weir)":       {"prix_set": 55_000,  "tps_pose_h": 8},
        "Ultrachrome® (Weir)": {"prix_set": 120_000, "tps_pose_h": 12},
        "Fonte au chrome":     {"prix_set": 35_000,  "tps_pose_h": 10},
    }
    tarif_downtime = st.number_input("Coût arrêt (MAD/h)", value=8_000, step=500)
    duree_tco      = st.slider("Horizon TCO (ans)", 3, 15, 5, 1)

    st.markdown("---")
    st.markdown("## 💰 Analyse Financière")
    C_invest   = st.number_input("Coût investissement (MAD)", value=2_500_000, step=100_000)
    taux_act   = st.slider("Taux d'actualisation (%)", 1, 20, 8, 1) / 100
    duree_proj = st.slider("Durée projet (ans)", 5, 30, 20, 1)
    C_OM_pct   = st.slider("Coût O&M annuel (% invest.)", 1, 10, 3, 1) / 100

# ══════════════════════════════════════════════════════════════════════════════
# CALCULS PRINCIPAUX
# ══════════════════════════════════════════════════════════════════════════════
g     = 9.81
eta_g = eta_h * eta_v * eta_elec

dP_utile  = max(dP_total - dP_disque, 0.1)
H_utile   = dP_utile * 1e5 / (rho * g)
H_total   = dP_total * 1e5 / (rho * g)

S         = (Q_reseau / Q_bep) ** (1/3)
H_unit    = H_bep * S**2

N_pat     = max(1, int(np.ceil(H_utile / H_unit)))
H_par_pat = H_utile / N_pat

S_real    = (H_par_pat / H_bep) ** 0.5
D2_real   = D2_base * S_real
N_real    = N_base  / S_real
Q_real    = Q_bep   * S_real**3

Ph_base   = rho * g * (Q_bep / 3600) * H_bep / 1000
Prec_base = Ph_base * eta_g
P_unit    = Prec_base * S_real**5
P_total   = P_unit * N_pat

E_an    = P_total * H_AN / 1000
gain    = E_an * 1000 * tarif
CO2     = E_an * 0.72

P_disque = rho * g * (Q_reseau / 3600) * H_total / 1000
E_perdue = P_disque * H_AN / 1000

# Fuite volumétrique
Q_fuite_max_m3h = Q_reseau * 0.05        # 5% du débit réseau réel
Q_fuite_reel    = Q_real * (1 - eta_v)
weir_eta_v_ok   = Q_fuite_reel <= Q_fuite_max_m3h

# Vitesse spécifique
Ns = N_real * (Q_real / 3600)**0.5 / (H_par_pat)**0.75 if H_par_pat > 0 else 0

# Érosion & durée de vie
mat      = MATS[mat_sel]
rho_poly = mat["rho_m"]
E_corr   = E0 * mat["f"] * K_local * (S_real**2.5)
Ev       = E_corr / rho_poly
ep_m     = ep_sac / 1000
duree_h  = (ep_m / Ev) / 3600 if Ev > 0 else 1e9
duree_an = duree_h / 24 / 365
usure_mm = Ev * H_AN * 3600 * 1000
ep_res   = max(ep_sac - usure_mm, 0)

WEIR_INSP_H = 1800
weir_ok = duree_h >= WEIR_INSP_H
alerte  = "DANGER" if ep_res <= EP_MIN else ("WARNING" if ep_res <= EP_MIN * 1.8 else "OK")


H_pat_slurry  = H_par_pat 
P_slurry      = rho * g * (Q_real / 3600) * H_pat_slurry * N_pat / 1000
P_elec_slurry = P_slurry * eta_g 

# ══════════════════════════════════════════════════
# NPSH — Thoma corrigé (σ depuis Ns)
# ══════════════════════════════════════════════════
H_atm       = 101325 / (rho * g)
Pv_Pa       = 3_170
sigma_thoma = max((Ns / 4500) ** (4/3), 0.02)
NPSH_r      = sigma_thoma * H_par_pat
NPSH_d      = H_atm - Pv_Pa / (rho * g) - 2.0
cavit_ok    = NPSH_d >= NPSH_r

# ── TCO ───────────────────────────────────────────────────────────────────────
tco_data = {}
for nm, p in MATS.items():
    Em_t    = E0 * p["f"] * K_local * (S_real**2.5)
    Evm_t   = Em_t / p["rho_m"]
    dv_h_t  = (ep_m / Evm_t) / 3600 if Evm_t > 0 else 1e6
    dv_an_t = dv_h_t / (24 * 365)
    n_remp  = max(int(np.ceil(duree_tco / dv_an_t)) - 1, 0)
    cout_c  = COUT_MAT[nm]
    cp_t    = n_remp * cout_c["prix_set"] * N_pat
    cpo_t   = n_remp * cout_c["tps_pose_h"] * tarif_downtime * N_pat
    tco_data[nm] = {
        "dv_an": dv_an_t, "n_remp": n_remp,
        "cout_pieces": cp_t, "cout_pose": cpo_t,
        "tco": cp_t + cpo_t,
    }

# ── Analyse Financière ────────────────────────────────────────────────────────
flux_an = gain - C_invest * C_OM_pct
payback = C_invest / flux_an if flux_an > 0 else 999
VAN     = -C_invest + sum(flux_an / (1 + taux_act)**t for t in range(1, duree_proj + 1))

def npv_r(r):
    return -C_invest + sum(flux_an / (1 + r)**t for t in range(1, duree_proj + 1))

lo, hi = 0.001, 5.0
for _ in range(80):
    mid = (lo + hi) / 2
    if npv_r(mid) > 0:
        lo = mid
    else:
        hi = mid
TRI = mid * 100

# ── PDF Report ────────────────────────────────────────────────────────────────
def generate_pdf_report():
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(6, 13, 24)
    pdf.rect(0, 0, 210, 297, 'F')

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(79, 195, 247)
    pdf.cell(0, 12, "RAPPORT PAT — EMI x Weir Minerals North Africa", ln=True, align='C')
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(200, 216, 240)
    pdf.cell(0, 7, f"Warman 10/8 M | D2={D2_real:.0f}mm | S={S_real:.3f} | "
                   f"N={N_real:.0f} tr/min | {N_pat} PAT(s)", ln=True, align='C')
    pdf.ln(4)

    def section(title):
        pdf.set_fill_color(13, 37, 80)
        pdf.set_text_color(79, 195, 247)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 8, f"  {title}", ln=True, fill=True)
        pdf.ln(2)

    def row(label, value, unit=""):
        pdf.set_text_color(180, 210, 240)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(90, 6, f"  {label}", ln=False)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 6, f"{value}  {unit}", ln=True)

    section("1. RÉSEAU & CONDITIONS")
    row("Débit réseau",   f"{Q_reseau:.1f}", "m³/h")
    row("ΔP total",       f"{dP_total:.1f}", "bar")
    row("ΔP disque",      f"{dP_disque:.1f}","bar")
    row("ΔP utile PATs",  f"{dP_utile:.1f}", "bar")
    row("Densité pulpe",  f"{rho:.0f}",      "kg/m³")
    pdf.ln(3)

    section("2. DIMENSIONNEMENT PAT (Similitude)")
    row("Nombre PATs série",     f"{N_pat}")
    row("Facteur S",              f"{S_real:.4f}")
    row("D₂ par PAT",             f"{D2_real:.0f}",     "mm")
    row("Vitesse N",              f"{N_real:.0f}",      "tr/min")
    row("Vitesse spécifique Ns",  f"{Ns:.1f}")
    row("Q par PAT",              f"{Q_real:.1f}",      "m³/h")
    row("H par PAT (eau)",        f"{H_par_pat:.2f}",   "m")
    row("H par PAT (pulpe)",      f"{H_pat_slurry:.2f}","m  [Sellgren]")
    row("P totale récupérée",     f"{P_total:.1f}",     "kW")
    pdf.ln(3)

    section("3. CORRECTION SELLGREN (Wilson & Sellgren, 2003)")
    row("NPSH disponible",   f"{NPSH_d:.2f}", "m")
    row("NPSH requis",       f"{NPSH_r:.2f}", "m")
    row("Cavitation",        "OK" if cavit_ok else "RISQUE")
    pdf.ln(3)

    section("4. USURE & MAINTENANCE")
    row("Matériau",             mat_sel.split('(')[0].strip())
    row("Épaisseur sacrif.",    f"{ep_sac}", "mm")
    row("Épaisseur résiduelle", f"{ep_res:.2f}", "mm")
    row("Durée de vie",         f"{duree_an:.1f}", "ans")
    row("Cycle Weir 1800h",     "RESPECTÉ" if weir_ok else "NON RESPECTÉ")
    row("Fuite volumétrique",   "OK" if weir_eta_v_ok else "EXCESSIVE")
    pdf.ln(3)

    section("5. BILAN ÉCONOMIQUE")
    row("Gain annuel",    f"{gain/1e6:.3f}", "M MAD/an")
    row("Énergie récup.", f"{E_an:.1f}",     "MWh/an")
    row("CO₂ évité",      f"{CO2:.1f}",      "t/an")
    row("VAN",            f"{VAN/1e6:.2f}",  "M MAD")
    row("TRI",            f"{TRI:.1f}",      "%")
    row("Payback",        f"{payback:.1f}",  "ans")
    pdf.ln(3)

    section(f"6. TCO MATÉRIAUX ({duree_tco} ans)")
    for nm, td in tco_data.items():
        row(nm.split('(')[0].strip(), f"{td['tco']:,.0f}", "MAD")

    pdf.set_y(-18)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(100, 140, 180)
    pdf.cell(0, 5,
             "PFE 2025-2026 · École Mohammadia d'Ingénieurs · Weir Minerals North Africa · ANSYS CFX SST k-ω",
             align='C')
    return bytes(pdf.output())

# ══════════════════════════════════════════════════════════════════════════════
# KPI HEADER
# ══════════════════════════════════════════════════════════════════════════════
kpis = [
    (f"{N_pat}",         "unités",   "PATs en série",  "kpi"),
    (f"{S_real:.3f}",    "—",        "Facteur S",      "kpi"),
    (f"{D2_real:.0f}",   "mm",       "D₂ par PAT",     "kpi"),
    (f"{P_total:.1f}",   "kW",       "P totale",       "kpi kpi-g"),
    (f"{CO2:.1f}",       "t CO₂/an", "CO₂ évité",      "kpi kpi-p"),
]
cols = st.columns(5)
for col, (v, u, l, c) in zip(cols, kpis):
    col.markdown(
        f'<div class="{c}"><div class="kl">{l}</div>'
        f'<div class="kv">{v}</div><div class="ku">{u}</div></div>',
        unsafe_allow_html=True
    )
st.markdown("<br>", unsafe_allow_html=True)

if H_unit > H_utile * 1.1:
    st.markdown(
        f'<div class="aw">⚠️ H unitaire ({H_unit:.1f}m) > H utile ({H_utile:.1f}m) — '
        f'Augmenter le nombre de PATs ou réduire S.</div>', unsafe_allow_html=True)
else:
    st.markdown(
        f'<div class="aok">✅ Architecture validée — {N_pat} PAT(s) × {H_par_pat:.1f}m = '
        f'{H_utile:.1f}m utile | ΔP disque = {dP_disque:.1f}bar</div>', unsafe_allow_html=True)

if not (10 <= Ns <= 70):
    st.markdown(
        f'<div class="aw">⚠️ Vitesse spécifique Ns={Ns:.1f} hors plage PAT recommandée [10–70] '
        f'— Vérifier le dimensionnement.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ONGLETS
# ══════════════════════════════════════════════════════════════════════════════
T1, T2, T3, T4, T5, T6, T7 = st.tabs([
    "📈 Performance & Scaling",
    "🔢 Système Multi-PAT",
    "🔧 Maintenance & Usure",
    "🌍 Bilan Éco & CO₂",
    "💰 Analyse Financière",
    "🌊  Cavitation",
    "🏷️ TCO Matériaux",
])


def style_ax(ax):
    ax.set_facecolor('white')
    ax.tick_params(colors='#334155', labelsize=9)
    ax.xaxis.label.set_color('#334155')
    ax.yaxis.label.set_color('#334155')
    ax.title.set_color('#1565c0')
    for spine in ax.spines.values():
        spine.set_edgecolor('#cbd5e1')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(alpha=.25, linestyle='--', color='#94a3b8')


# ─── TAB 1 ───────────────────────────────────────────────────────────────────
with T1:
    st.markdown('<div class="sh">Dimensionnement par Loi de Similitude</div>', unsafe_allow_html=True)
    st.markdown("---")
    cA, cB = st.columns([1, 1.8])
    with cA:
        ns_status = "✅ OK" if 10 <= Ns <= 70 else "⚠️ Hors plage"
        df_sim = pd.DataFrame({
            "Paramètre":   ["D₂ (mm)", "N (tr/min)", "Q/PAT (m³/h)", "H/PAT (m)",
                            "P/PAT (kW)", "P totale (kW)", "Ns"],
            "Base CFD":    [f"{D2_base:.0f}", f"{N_base:.0f}", f"{Q_bep:.1f}",
                            f"{H_bep:.2f}", f"{Prec_base:.2f}", "—", "—"],
            f"S={S_real:.3f}": [f"{D2_real:.0f}", f"{N_real:.1f}", f"{Q_real:.1f}",
                                f"{H_par_pat:.2f}", f"{P_unit:.1f}", f"{P_total:.1f}",
                                f"{Ns:.1f}  {ns_status}"],
        })
        st.dataframe(df_sim, use_container_width=True, hide_index=True)

    with cB:
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
        fig.patch.set_facecolor('#f8fafc')
        for ax in axes:
            style_ax(ax)
        S_r = np.linspace(0.5, 2.5, 200)

        axes[0].plot(S_r, Prec_base * S_r**5, '-', color='#00e676', lw=2.5, label='P par PAT')
        axes[0].plot(S_r, Prec_base * S_r**5 * np.ceil(H_utile / (H_bep * S_r**2)),
                     '--', color='#4FC3F7', lw=2, label='P totale (N×PAT)')
        axes[0].axvline(S_real, color='#ff5252', ls='--', lw=2, label=f'S={S_real:.3f}')
        axes[0].scatter([S_real], [P_unit], color='#ff5252', s=100, zorder=5, edgecolors='white', lw=1.5)
        axes[0].set_xlabel("Facteur S", fontsize=10, fontweight='bold')
        axes[0].set_ylabel("Puissance (kW)", fontsize=10, fontweight='bold')
        axes[0].set_title("Puissance vs S", fontsize=10, fontweight='bold')
        axes[0].legend(fontsize=8.5, facecolor='#f8fafc', edgecolor='#cbd5e1', labelcolor='#1a2a3a')

        axes[1].plot(S_r, H_bep * S_r**2, '-', color='#4FC3F7', lw=2.5, label='H/PAT requise')
        axes[1].axhline(H_utile, color='#ff9100', ls='--', lw=1.8, label=f'H utile={H_utile:.1f}m')
        axes[1].axhline(H_total, color='#ff5252', ls=':',  lw=1.5, label=f'H totale={H_total:.1f}m')
        axes[1].axvline(S_real,  color='#ff5252', ls='--', lw=2,   label=f'S={S_real:.3f}')
        S_incompat = S_r[H_bep * S_r**2 > H_utile]
        if len(S_incompat):
            axes[1].axvspan(S_incompat[0], S_r[-1], alpha=0.06, color='red')
        axes[1].set_xlabel("Facteur S", fontsize=10, fontweight='bold')
        axes[1].set_ylabel("H (m)", fontsize=10, fontweight='bold')
        axes[1].set_title("Hauteur vs S — Compatibilité", fontsize=10, fontweight='bold')
        axes[1].legend(fontsize=8, facecolor='#f8fafc', edgecolor='#cbd5e1', labelcolor='#1a2a3a')

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

# ─── TAB 2 ───────────────────────────────────────────────────────────────────
with T2:
    st.markdown('<div class="sh">Architecture Multi-PAT — Bilan de Pression</div>', unsafe_allow_html=True)
    c1p, c2p, c3p, c4p = st.columns(4)
    for col, (v, u, l, c) in zip([c1p, c2p, c3p, c4p], [
        (f"{dP_total:.1f}",  "bar",  "ΔP total réseau",   "kpi"),
        (f"{dP_disque:.1f}", "bar",  "ΔP disque orifice", "kpi kpi-r"),
        (f"{dP_utile:.1f}",  "bar",  "ΔP utile PATs",     "kpi kpi-g"),
        (f"{N_pat}",          "PATs", "Nombre en série",   "kpi kpi-o"),
    ]):
        col.markdown(
            f'<div class="{c}"><div class="kl">{l}</div>'
            f'<div class="kv">{v}</div><div class="ku">{u}</div></div>',
            unsafe_allow_html=True
        )
    st.markdown("<br>", unsafe_allow_html=True)

    fig_r, ax_r = plt.subplots(figsize=(13, 5.5))
    ax_r.set_xlim(0, 13)
    ax_r.set_ylim(0, 6)
    ax_r.axis('off')
    ax_r.set_facecolor('white')
    fig_r.patch.set_facecolor('#f8fafc')
    ax_r.text(6.5, 5.55, f'Architecture réseau — {N_pat} PAT(s) en série | Jorf Lasfar OCP',
              ha='center', fontsize=12, fontweight='bold', color='#4FC3F7')

    def rbox(x, y, w, h, fc, ec, lw=2.0):
        p = FancyBboxPatch((x - w/2, y - h/2), w, h,
                           boxstyle="round,pad=0.07", fc=fc, ec=ec, lw=lw, zorder=4)
        ax_r.add_patch(p)

    def arr(x1, y1, x2, y2, c='white', lw=2.2, label=''):
        ax_r.annotate('', xy=(x2, y2), xytext=(x1, y1),
                      arrowprops=dict(arrowstyle='->', color=c, lw=lw))
        if label:
            ax_r.text((x1+x2)/2, (y1+y2)/2 + 0.2, label,
                      ha='center', fontsize=8, color=c, fontweight='bold')

    arr(0.1, 3.0, 0.9, 3.0, '#2E75B6', 3, f'Q={Q_reseau:.0f}m³/h')
    rbox(0.65, 3.0, 0.85, 0.6, '#0d2550', '#2E75B6')
    ax_r.text(0.65, 3.0, 'PULPE\nHaute P.', ha='center', va='center',
              fontsize=7, fontweight='bold', color='#64B5F6', zorder=6)
    ax_r.text(0.65, 2.45, f'{dP_total:.0f}bar', ha='center', fontsize=7.5, color='#6ca8d4')
    arr(1.1, 3.0, 1.85, 3.0, '#ff5252', 2.5)
    rbox(2.1, 3.0, 0.55, 0.8, '#1a0608', '#ff5252', 2.5)
    ax_r.text(2.1, 3.05, '⊛', ha='center', va='center', fontsize=18, color='#ff5252', zorder=6)
    ax_r.text(2.1, 2.45, f'Disque\n-{dP_disque:.0f}bar',
              ha='center', fontsize=7.5, color='#ff5252', fontweight='bold')
    ax_r.text(2.1, 1.85, f'Dissipé:\n{dP_disque*1e5/(rho*g):.1f}m',
              ha='center', fontsize=7, color='#ff9999', style='italic')
    arr(2.4, 3.0, 2.9, 3.0, '#ff9100', 2, f'{dP_utile:.0f}bar')

    n_show  = min(N_pat, 5)
    spacing = min(1.2, 5.5 / max(n_show, 1))
    x_start = 3.1
    for ni in range(n_show):
        xp = x_start + ni * spacing
        yp = 3.0
        ax_r.add_patch(Circle((xp, yp), 0.32, fc='#dbeafe', ec='#1565c0', lw=2, zorder=5))
        for ang in range(0, 360, 72):
            th = np.radians(ang)
            ax_r.plot([xp + 0.14*np.cos(th), xp + 0.29*np.cos(th + np.radians(22))],
                      [yp + 0.14*np.sin(th), yp + 0.29*np.sin(th + np.radians(22))],
                      '-', color='#4FC3F7', lw=1.5, zorder=6)
        ax_r.text(xp, yp, '⚙', ha='center', va='center', fontsize=9, color='white', zorder=7)
        ax_r.text(xp, yp - 0.55, f'PAT {ni+1}', ha='center', fontsize=7, color='#4FC3F7', fontweight='bold')
        ax_r.text(xp, yp - 0.82, f'-{H_par_pat:.1f}m', ha='center', fontsize=6.5, color='#90CAF9')
        if ni < n_show - 1:
            arr(xp + 0.34, yp, xp + spacing - 0.34, yp, '#4FC3F7', 1.8)
    if N_pat > 5:
        ax_r.text(x_start + 5*spacing, 3.0, '...', ha='left', va='center',
                  fontsize=16, color='#4FC3F7', fontweight='bold')

    x_after = x_start + (n_show - 1)*spacing + 0.38
    arr(x_after, 3.0, x_after + 0.4, 3.0, '#4FC3F7', 2)
    xG = x_after + 0.7
    rbox(xG, 3.0, 0.7, 0.95, '#061a0c', '#00e676', 2)
    ax_r.text(xG, 3.0, 'G', ha='center', va='center',
              fontsize=14, fontweight='bold', color='white', zorder=6)
    ax_r.text(xG, 2.4, f'{P_total:.0f}kW', ha='center', fontsize=8, color='#00e676', fontweight='bold')
    arr(xG + 0.37, 3.0, xG + 0.65, 3.0, '#00e676', 2)
    xR = xG + 0.95
    rbox(xR, 3.0, 0.65, 0.9, '#061a0c', '#69F0AE', 2)
    ax_r.plot([xR, xR], [2.58, 3.48], '-', color='#69F0AE', lw=2.5, zorder=6)
    ax_r.plot([xR-.28, xR+.28], [3.25, 3.25], '-', color='#69F0AE', lw=2, zorder=6)
    ax_r.plot([xR-.2, xR+.2], [3.0, 3.0], '--', color='#69F0AE', lw=1.5, zorder=6)
    ax_r.text(xR, 2.32, 'Réseau', ha='center', fontsize=7.5, color='#69F0AE', fontweight='bold')
    ax_r.text(xR, 2.08, f'{E_an:.0f}MWh/an', ha='center', fontsize=7, color='#b9f6ca')

    bpdata = [(f'Disque ({dP_disque:.0f}bar)', dP_disque, '#ff5252'),
              (f'PATs {N_pat}× ({dP_utile:.0f}bar)', dP_utile, '#00e676')]
    ax_r.text(0.2, 1.55, 'Bilan ΔP :', fontsize=8.5, fontweight='bold', color='#4FC3F7')
    x0b = 0.2
    for lbl, val, c in bpdata:
        w = val / dP_total * 5.5
        ax_r.barh(1.12, w, left=x0b, height=0.32, color=c, alpha=.9)
        ax_r.text(x0b + w/2, 1.12, f'{val:.0f}bar',
                  ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        x0b += w

    ax_r.text(0.2, 0.72, 'Bilan P :', fontsize=8.5, fontweight='bold', color='#4FC3F7')
    x0p = 0.2
    for lbl, val, c in [('Pertes', P_disque - P_total, '#ff5252'), ('Récup.', P_total, '#00e676')]:
        w = max(val, 0) / P_disque * 5.5
        ax_r.barh(0.38, w, left=x0p, height=0.28, color=c, alpha=.88)
        ax_r.text(x0p + w/2, 0.38, f'{val:.0f}kW',
                  ha='center', va='center', fontsize=7.5, color='white', fontweight='bold')
        x0p += w

    plt.tight_layout()
    st.pyplot(fig_r)
    plt.close()

    st.markdown("---")
    st.markdown('<div class="sh">Comparaison des configurations</div>', unsafe_allow_html=True)
    configs = []
    for n in range(1, 7):
        He   = dP_utile * 1e5 / (rho * g) / n
        Sr   = (He / H_bep)**0.5 if He > 0 else 0
        D2n  = D2_base * Sr
        Nn   = N_base / Sr if Sr > 0 else 0
        Pn   = Prec_base * Sr**5 * n
        Ns_n = Nn * (Q_bep * Sr**3 / 3600)**0.5 / He**0.75 if He > 0 else 0
        Em   = E0 * mat["f"] * K_local * (Sr**2.5)
        Evm  = Em / mat["rho_m"]
        dvn  = (ep_m / Evm) / (3600*24*365) if Evm > 0 else 999
        ern  = max(ep_sac - Evm * H_AN * 3600 * 1000, 0)
        configs.append({
            "N PATs": n, "S par PAT": f"{Sr:.3f}",
            "D₂ (mm)": f"{D2n:.0f}", "N (tr/min)": f"{Nn:.0f}", "Ns": f"{Ns_n:.1f}",
            "H/PAT (m)": f"{He:.1f}", "P totale (kW)": f"{Pn:.1f}",
            "Durée vie (ans)": f"{dvn:.1f}", "Ép. résid.": f"{ern:.2f}mm",
            "Conseil": "✅ Optimal" if 0.7 < Sr < 1.6 else ("⚠️ Érosion" if Sr < 2.2 else "❌ Éviter"),
        })
    df_conf = pd.DataFrame(configs)

    def hi(row):
        return ['background-color:#dbeafe'] * len(row) if int(row["N PATs"]) == N_pat else [''] * len(row)

    st.dataframe(df_conf.style.apply(hi, axis=1), use_container_width=True, hide_index=True)

# ─── TAB 3 ───────────────────────────────────────────────────────────────────
with T3:
    st.markdown('<div class="sh">Maintenance & Durée de Vie — Validation Weir 1800h</div>',
                unsafe_allow_html=True)

    if not weir_ok:
        st.markdown(
            f'<div class="ad">🚨 <b>CYCLE WEIR NON RESPECTÉ</b> — '
            f'Durée vie <b>{duree_h:,.0f} h</b> &lt; seuil Weir <b>{WEIR_INSP_H} h</b></div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="aok">✅ <b>Cycle Weir respecté</b> — '
            f'Durée vie <b>{duree_h:,.0f} h</b> ≥ {WEIR_INSP_H} h</div>',
            unsafe_allow_html=True)

    if weir_eta_v_ok:
        st.markdown(
            f'<div class="aok">✅ Fuite volumétrique OK — '
            f'Q_fuite={Q_fuite_reel:.2f} m³/h ≤ seuil 5% réseau ({Q_fuite_max_m3h:.2f} m³/h)</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="ad">🚨 Fuite volumétrique excessive — '
            f'Q_fuite={Q_fuite_reel:.2f} m³/h &gt; seuil 5% réseau ({Q_fuite_max_m3h:.2f} m³/h) — '
            f'Vérifier garnitures mécaniques</div>',
            unsafe_allow_html=True)
    if alerte == "DANGER":
        st.markdown(
            f'<div class="ad">🚨 <b>USURE CRITIQUE — {mat_sel.split("(")[0]}</b> : '
            f'Ép. résiduelle <b>{ep_res:.2f} mm</b> ≤ seuil {EP_MIN} mm — '
            f'Remplacement avant <b>{duree_an:.2f} ans</b></div>', unsafe_allow_html=True)
    elif alerte == "WARNING":
        st.markdown(
            f'<div class="aw">⚠️ Ép. résiduelle <b>{ep_res:.2f} mm</b> — Inspection recommandée</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="aok">✅ Ép. résiduelle <b>{ep_res:.2f} mm</b> — '
            f'Durée vie : <b>{duree_an:.1f} ans</b></div>', unsafe_allow_html=True)

    cM1, cM2 = st.columns(2)
    with cM1:
        st.markdown("#### Multi-matériaux")
        rows = []
        for nm, p in MATS.items():
            Em  = E0 * p["f"] * K_local * (S_real**2.5)
            Evm = Em / p["rho_m"]
            dvn = (ep_m / Evm) / (3600*24*365) if Evm > 0 else 999
            dvh = (ep_m / Evm) / 3600 if Evm > 0 else 999
            ern = max(ep_sac - Evm * H_AN * 3600 * 1000, 0)
            rows.append({
                "Matériau":    nm.split('(')[0].strip(),
                "E (kg/m²s)":  f"{Em:.2e}",
                "Durée (ans)": f"{dvn:.1f}",
                "Durée (h)":   f"{dvh:,.0f}",
                "Ép. résid.":  f"{ern:.2f}mm",
                "Weir 1800h":  "✅" if dvh >= WEIR_INSP_H else "🚨",
                "État":        "🚨" if ern <= EP_MIN else ("⚠️" if ern <= EP_MIN*1.8 else "✅"),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with cM2:
        t_max = max(duree_an * 1.3, 3)
        t_r   = np.linspace(0, t_max, 400)

        fig_t, ax_t = plt.subplots(figsize=(6.5, 4))
        fig_t.patch.set_facecolor('#f8fafc')
        style_ax(ax_t)
        for nm, p in MATS.items():
            Em  = E0 * p["f"] * K_local * (S_real**2.5)
            Evm = Em / p["rho_m"]
            ep_t = np.maximum(ep_sac - Evm * t_r * 365 * 24 * 3600 * 1000, 0)
            ax_t.plot(t_r, ep_t, '-', color=p["c"], lw=2.2, label=nm.split('(')[0].strip()[:16])
        ax_t.axhline(EP_MIN, color='#ff5252', linestyle='--', lw=1.8, label=f'Seuil {EP_MIN}mm')
        ax_t.fill_between(t_r, 0, EP_MIN, color='red', alpha=.05)
        ax_t.axvline(WEIR_INSP_H / (365*24), color='#ff9100', linestyle=':', lw=1.8,
                     label=f'Weir {WEIR_INSP_H}h')
        ax_t.set_xlabel("Temps (années)", fontsize=10, fontweight='bold')
        ax_t.set_ylabel("Épaisseur résiduelle (mm)", fontsize=10, fontweight='bold')
        ax_t.set_title(f"Usure paroi — S={S_real:.3f} | K={K_local}", fontsize=10, fontweight='bold')
        ax_t.set_ylim(0, ep_sac * 1.12)
        ax_t.legend(fontsize=8.5, facecolor='#f8fafc', edgecolor='#cbd5e1', labelcolor='#1a2a3a')
        plt.tight_layout()
        st.pyplot(fig_t)
        plt.close()

        S_range = np.linspace(0.5, 2.0, 200)
        dv_S = []
        for sv in S_range:
            Em  = E0 * mat["f"] * K_local * (sv**2.5)
            Evm = Em / mat["rho_m"]
            dv_S.append((ep_m / Evm) / 3600 if Evm > 0 else 1e6)

        fig_s, ax_s = plt.subplots(figsize=(6.5, 3.8))
        fig_s.patch.set_facecolor('#f8fafc')
        style_ax(ax_s)
        ax_s.plot(S_range, np.array(dv_S) / 1000, '-', color=mat["c"], lw=2.5)
        ax_s.axvline(S_real, color='#ff5252', ls='--', lw=2, label=f'S={S_real:.3f}')
        ax_s.axhline(WEIR_INSP_H / 1000, color='#ff9100', ls=':', lw=2,
                     label=f'Seuil Weir {WEIR_INSP_H}h')
        ax_s.set_xlabel("Facteur S", fontsize=10, fontweight='bold')
        ax_s.set_ylabel("Durée de vie (×1000 h)", fontsize=10, fontweight='bold')
        ax_s.set_title(f"Durée vie vs S — {mat_sel.split('(')[0]}", fontsize=10, fontweight='bold')
        ax_s.legend(fontsize=9, facecolor='#f8fafc', edgecolor='#cbd5e1', labelcolor='#1a2a3a')
        plt.tight_layout()
        st.pyplot(fig_s)
        plt.close()

# ─── TAB 4 ───────────────────────────────────────────────────────────────────
with T4:
    st.markdown('<div class="sh">Bilan Économique & Impact Environnemental — Avant vs Après PAT</div>',
                unsafe_allow_html=True)
    c_av, c_mid, c_ap = st.columns(3)
    with c_av:
        st.markdown(f"""<div class="loss-box">
            <div style="font-size:1rem;font-weight:700;margin-bottom:8px;">🔴 AVANT — Vanne + Disque</div>
            <div style="font-size:1.9rem;font-weight:700;">{P_disque:.1f} kW</div>
            <div style="opacity:.7;font-size:.83rem;">Puissance totale dissipée</div>
            <hr style="border-color:rgba(255,255,255,.1);margin:8px 0;">
            <div style="font-size:1.1rem;font-weight:600;">{E_perdue:.1f} MWh/an perdus</div>
            <div style="font-size:1rem;color:#ff9999;margin-top:5px;">{E_perdue*1000*tarif/1e6:.3f} M MAD perdus/an</div>
            <div style="margin-top:5px;color:#ff9999;font-size:.88rem;">🌍 {E_perdue*0.72:.1f} t CO₂ non valorisées</div>
        </div>""", unsafe_allow_html=True)
    with c_mid:
        st.markdown(f"""<div style="background:linear-gradient(135deg,#dbeafe,#bfdbfe);border-radius:4px;padding:16px;text-align:center;color:#1e3a5f;margin:10px 0;border:1px solid rgba(37,99,235,0.3);">
            <div style="font-size:1.1rem;font-weight:700;margin-bottom:8px;color:#4FC3F7;">⚡ INSTALLATION PAT</div>
            <div style="font-size:1rem;margin:6px 0;">{N_pat} PAT(s) × D₂={D2_real:.0f}mm</div>
            <div style="font-size:.9rem;opacity:.7;">S = {S_real:.3f}</div>
            <div style="font-size:.9rem;opacity:.7;">N = {N_real:.0f} tr/min</div>
            <div style="font-size:.9rem;opacity:.7;">ΔP disque = {dP_disque:.0f}bar conservé</div>
            <div style="margin-top:8px;font-size:.95rem;color:#00e676;">η_global = {eta_g*100:.1f}%</div>
            <div style="font-size:.85rem;opacity:.6;margin-top:4px;">{mat_sel.split("(")[0].strip()}</div>
        </div>""", unsafe_allow_html=True)
    with c_ap:
        st.markdown(f"""<div class="gain-box">
            <div style="font-size:1rem;font-weight:700;margin-bottom:8px;">🟢 APRÈS — Récupération PAT</div>
            <div style="font-size:1.9rem;font-weight:700;">{P_total:.1f} kW</div>
            <div style="opacity:.7;font-size:.83rem;">Puissance récupérée ({N_pat} PATs)</div>
            <hr style="border-color:rgba(255,255,255,.1);margin:8px 0;">
            <div style="font-size:1.1rem;font-weight:600;">{E_an:.1f} MWh/an récupérés</div>
            <div style="font-size:1rem;color:#b3ffb3;margin-top:5px;">{gain/1e6:.3f} M MAD gagnés/an</div>
            <div style="margin-top:5px;color:#b3ffb3;font-size:.88rem;">🌍 {CO2:.1f} t CO₂ évitées/an</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    fig_eco, axes_eco = plt.subplots(1, 3, figsize=(13, 4.5))
    fig_eco.patch.set_facecolor('#f8fafc')
    for ax_e, vals, labels, title, colors in [
        (axes_eco[0],
         [P_disque, P_total, P_disque - P_total],
         ['Dissipée\n(avant)', 'Récupérée\n(PAT)', 'Pertes\nnettes'],
         'Puissance (kW)', ['#ff5252', '#00e676', '#555555']),
        (axes_eco[1],
         [E_perdue, E_an],
         ['Énergie perdue\n(avant)', 'Énergie récupérée\n(PAT)'],
         'Énergie (MWh/an)', ['#ff5252', '#00e676']),
        (axes_eco[2],
         [E_perdue * 0.72, CO2],
         ['CO₂ non\nvalorisé', 'CO₂\névité (PAT)'],
         'CO₂ (t/an)', ['#ff9100', '#00e676']),
    ]:
        style_ax(ax_e)
        ax_e.tick_params(axis='x', colors='#334155')
        bars = ax_e.bar(labels, vals, color=colors, width=0.5, edgecolor='#f8fafc', lw=1.5)
        for b, v in zip(bars, vals):
            ax_e.text(b.get_x() + b.get_width()/2, b.get_height() + max(vals)*0.02,
                      f'{v:.0f}', ha='center', fontsize=11, fontweight='bold', color='#1a2a3a')
        ax_e.set_title(title, fontsize=11, fontweight='bold')

    fig_eco.suptitle(
        f'Bilan Avant/Après PAT | Q={Q_reseau:.0f}m³/h | ΔP={dP_total:.0f}bar | '
        f'{N_pat}×PAT D₂={D2_real:.0f}mm',
        fontsize=11, fontweight='bold', color='#1565c0')
    plt.tight_layout()
    st.pyplot(fig_eco)
    plt.close()

    st.markdown("---")
    c1f, c2f, c3f, c4f, c5f = st.columns(5)
    arbres = int(CO2 * 1000 / 25)
    for col, (v, u, l, c) in zip([c1f, c2f, c3f, c4f, c5f], [
        (f"{gain/1e6:.3f}",            "M MAD/an", "Gain annuel",       "kpi kpi-g"),
        (f"{CO2:.1f}",                  "t CO₂/an", "CO₂ évité",         "kpi kpi-p"),
        (f"{E_an:.0f}",                 "MWh/an",   "Énergie récup.",    "kpi kpi-g"),
        (f"{P_total/P_disque*100:.0f}", "%",         "Taux récupération", "kpi kpi-o"),
        (f"≈{arbres:,}",               "arbres/an", "Équiv. arbres",     "kpi"),
    ]):
        col.markdown(
            f'<div class="{c}"><div class="kl">{l}</div>'
            f'<div class="kv">{v}</div><div class="ku">{u}</div></div>',
            unsafe_allow_html=True)

# ─── TAB 5 — Analyse Financière ──────────────────────────────────────────────
with T5:
    st.markdown('<div class="sh">Analyse Financière — VAN · TRI · Payback</div>',
                unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    for col, (v, u, l, c) in zip([k1, k2, k3, k4], [
        (f"{VAN/1e6:.2f}",    "M MAD",    "VAN",      "kpi kpi-g" if VAN > 0 else "kpi kpi-r"),
        (f"{TRI:.1f}",         "%",        "TRI",      "kpi kpi-g"),
        (f"{payback:.1f}",     "ans",      "Payback",  "kpi kpi-o"),
        (f"{flux_an/1e3:.1f}", "k MAD/an", "Flux net", "kpi"),
    ]):
        col.markdown(
            f'<div class="{c}"><div class="kl">{l}</div>'
            f'<div class="kv">{v}</div><div class="ku">{u}</div></div>',
            unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if VAN > 0:
        st.markdown(
            f'<div class="aok">✅ Projet rentable — VAN={VAN/1e6:.2f}M MAD | '
            f'TRI={TRI:.1f}% | Payback={payback:.1f}ans</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="ad">🚨 VAN négative ({VAN/1e6:.2f}M MAD) — '
            f'Revoir paramètres financiers</div>', unsafe_allow_html=True)

    annees = np.arange(0, duree_proj + 1)
    cum_cf = np.cumsum([-C_invest] + [flux_an] * duree_proj)

    fig_f, (ax_f, ax_s) = plt.subplots(1, 2, figsize=(13, 4.5))
    fig_f.patch.set_facecolor('#f8fafc')
    style_ax(ax_f)
    style_ax(ax_s)

    ax_f.fill_between(annees, cum_cf/1e6, 0, where=(cum_cf >= 0), color='#00e676', alpha=.15)
    ax_f.fill_between(annees, cum_cf/1e6, 0, where=(cum_cf < 0),  color='#ff5252', alpha=.15)
    ax_f.plot(annees, cum_cf/1e6, '-o', color='#4FC3F7', lw=2.5, ms=5, label='Cash-flow cumulé')
    ax_f.axhline(0, color='#94a3b8', lw=1, ls='--')
    if payback < duree_proj:
        ax_f.axvline(payback, color='#ff9100', ls='--', lw=2, label=f'Payback={payback:.1f}ans')
    ax_f.set_xlabel("Années", fontsize=10, fontweight='bold')
    ax_f.set_ylabel("Cash-flow cumulé (M MAD)", fontsize=10, fontweight='bold')
    ax_f.set_title(f"Cash-flow cumulé | VAN={VAN/1e6:.2f}M MAD", fontsize=10, fontweight='bold')
    ax_f.legend(fontsize=9, facecolor='#f8fafc', edgecolor='#cbd5e1', labelcolor='#1a2a3a')

    tarifs_r = np.linspace(0.5, 2.5, 100)
    vans_r = [
        -C_invest + sum(
            (E_an * 1000 * t - C_invest * C_OM_pct) / (1 + taux_act)**yr
            for yr in range(1, duree_proj + 1)
        )
        for t in tarifs_r
    ]
    ax_s.plot(tarifs_r, np.array(vans_r)/1e6, '-', color='#4FC3F7', lw=2.5)
    ax_s.axhline(0, color='#94a3b8', lw=1, ls='--')
    ax_s.axvline(tarif, color='#ff5252', lw=2, ls='--', label=f'Tarif actuel={tarif} MAD/kWh')
    ax_s.fill_between(tarifs_r, np.array(vans_r)/1e6, 0,
                      where=(np.array(vans_r) >= 0), color='#00e676', alpha=.1)
    ax_s.set_xlabel("Tarif électricité (MAD/kWh)", fontsize=10, fontweight='bold')
    ax_s.set_ylabel("VAN (M MAD)", fontsize=10, fontweight='bold')
    ax_s.set_title("Sensibilité VAN vs Tarif électricité", fontsize=10, fontweight='bold')
    ax_s.legend(fontsize=9, facecolor='#f8fafc', edgecolor='#cbd5e1', labelcolor='#1a2a3a')

    plt.tight_layout()
    st.pyplot(fig_f)
    plt.close()

    st.markdown("---")
    st.markdown('<div class="sh">Export Rapport PDF</div>', unsafe_allow_html=True)
    if st.button("📄 Générer et télécharger le rapport PDF", type="primary"):
        try:
            pdf_bytes = generate_pdf_report()
            st.download_button(
                label="⬇️ Télécharger rapport_PAT.pdf",
                data=pdf_bytes,
                file_name=f"rapport_PAT_D{D2_real:.0f}mm_{N_pat}PATs.pdf",
                mime="application/pdf",
            )
        except ImportError:
            st.error("📦 Installe fpdf2 : pip install fpdf2")

# ─── TAB 6 —  Cavitation ───────────────────────────────────────────
with T6:
    st.markdown(
        '<div class="sh">Correction Sellgren (Wilson & Sellgren, 2003) — '
        'Dératage Pulpe & Fenêtre Opératoire</div>',
        unsafe_allow_html=True)

    if not cavit_ok:
        st.markdown(
            f'<div class="ad">🚨 <b>RISQUE CAVITATION</b> — '
            f'NPSH_r={NPSH_r:.2f}m &gt; NPSH_d={NPSH_d:.2f}m</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="aok">✅ Cavitation OK — NPSH_d={NPSH_d:.2f}m ≥ NPSH_r={NPSH_r:.2f}m</div>',
            unsafe_allow_html=True)

   
    st.markdown('<div class="sh">Fenêtre Opératoire — Plage Admissible</div>', unsafe_allow_html=True)
    Q_range  = np.linspace(0.4 * Q_real, 1.5 * Q_real, 300)
    H_hq     = H_pat_slurry * (Q_range / Q_real)**2
    eta_hq   = eta_g * np.exp(-2.5 * ((Q_range - Q_real) / Q_real)**2)
    Q_min_op = 0.70 * Q_real
    Q_max_op = 1.20 * Q_real

    fig_op, ax_op = plt.subplots(figsize=(10, 5))
    fig_op.patch.set_facecolor('#f8fafc')
    style_ax(ax_op)

    mask = (Q_range >= Q_min_op) & (Q_range <= Q_max_op)
    ax_op.plot(Q_range, H_hq, '-', color='#4FC3F7', lw=2.5,
               label='Courbe H-Q PAT (pulpe corrigée Sellgren)')
    ax_op.fill_between(Q_range, H_hq, where=mask, color='#00e676', alpha=.2,
                       label='Zone admissible (70%–120% BEP)')
    ax_op.axvline(Q_real,   color='#ff5252', ls='--', lw=2,   label=f'Q_BEP={Q_real:.0f}m³/h')
    ax_op.axvline(Q_min_op, color='#ffa000', ls=':',  lw=1.8, label=f'Q_min={Q_min_op:.0f}m³/h')
    ax_op.axvline(Q_max_op, color='#ffa000', ls=':',  lw=1.8, label=f'Q_max={Q_max_op:.0f}m³/h')
    ax_op.axvline(Q_reseau, color='#334155', ls='-',  lw=2,   label=f'Q_réseau={Q_reseau:.0f}m³/h')
    ax_op.scatter([Q_real], [H_pat_slurry], color='#ff5252', s=120, zorder=6,
                  edgecolors='white', lw=1.5)

    ax2_op = ax_op.twinx()
    ax2_op.plot(Q_range, eta_hq * 100, '--', color='#ff9100', lw=1.8, alpha=0.7, label='η global (%)')
    ax2_op.set_ylabel("η global (%)", fontsize=10, fontweight='bold', color='#ff9100')
    ax2_op.tick_params(colors='#ff9100')
    ax2_op.spines['top'].set_visible(False)
    ax2_op.spines['right'].set_edgecolor('#cbd5e1')
    ax2_op.set_ylim(0, 100)

    lines1, labels1 = ax_op.get_legend_handles_labels()
    lines2, labels2 = ax2_op.get_legend_handles_labels()
    ax_op.legend(lines1 + lines2, labels1 + labels2,
                 fontsize=8.5, facecolor='#f8fafc', edgecolor='#cbd5e1', labelcolor='#1a2a3a')
    ax_op.set_xlabel("Débit Q (m³/h)", fontsize=10, fontweight='bold')
    ax_op.set_ylabel("Hauteur H (m)", fontsize=10, fontweight='bold')
    ax_op.set_title(
        
    plt.tight_layout()
    st.pyplot(fig_op)
    plt.close()

    if Q_min_op <= Q_reseau <= Q_max_op:
        st.markdown(
            f'<div class="aok">✅ Q réseau ({Q_reseau:.0f}m³/h) dans la fenêtre opératoire '
            f'[{Q_min_op:.0f} – {Q_max_op:.0f}] m³/h</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="ad">🚨 Q réseau ({Q_reseau:.0f}m³/h) HORS fenêtre opératoire '
            f'[{Q_min_op:.0f} – {Q_max_op:.0f}] m³/h — Risque vibrations / cavitation</div>',
            unsafe_allow_html=True)

# ─── TAB 7 — TCO Matériaux ───────────────────────────────────────────────────
with T7:
    st.markdown(
        f'<div class="sh">TCO — Coût Total de Possession sur {duree_tco} ans</div>',
        unsafe_allow_html=True)

    mat_opt = min(tco_data, key=lambda k: tco_data[k]['tco'])
    st.markdown(
        f'<div class="aok">🏆 Matériau optimal TCO sur {duree_tco}ans : '
        f'<b>{mat_opt.split("(")[0]}</b> — '
        f'{tco_data[mat_opt]["tco"]:,.0f} MAD</div>', unsafe_allow_html=True)

    tco_rows = []
    min_tco = min(v['tco'] for v in tco_data.values())
    for nm, td in tco_data.items():
        tco_rows.append({
            "Matériau":          nm.split('(')[0].strip(),
            "Durée vie (ans)":   f"{td['dv_an']:.1f}",
            "Remplacements":     td['n_remp'],
            "Coût pièces (MAD)": f"{td['cout_pieces']:,.0f}",
            "Coût arrêt (MAD)":  f"{td['cout_pose']:,.0f}",
            "TCO total (MAD)":   f"{td['tco']:,.0f}",
            "🏆": "⭐ Optimal" if td['tco'] == min_tco else "",
        })
    st.dataframe(pd.DataFrame(tco_rows), use_container_width=True, hide_index=True)
    st.markdown("---")

    nms   = [k.split('(')[0].strip()[:14] for k in tco_data]
    cp    = [tco_data[k]['cout_pieces'] / 1e3 for k in tco_data]
    cpose = [tco_data[k]['cout_pose']   / 1e3 for k in tco_data]

    fig_tco, ax_tco = plt.subplots(figsize=(10, 4.5))
    fig_tco.patch.set_facecolor('#f8fafc')
    style_ax(ax_tco)
    ax_tco.grid(axis='y', alpha=.30, linestyle='--', color='#94a3b8')
    ax_tco.tick_params(axis='x', colors='#334155')

    x  = np.arange(len(nms))
    b1 = ax_tco.bar(x, cp,    0.5, label='Coût pièces',      color='#2E75B6', edgecolor='#f8fafc')
    b2 = ax_tco.bar(x, cpose, 0.5, bottom=cp, label='Coût arrêt/pose', color='#ff9100', edgecolor='#f8fafc')

    for i, (bp, bps) in enumerate(zip(b1, b2)):
        total = bp.get_height() + bps.get_height()
        ax_tco.text(i, total + max(max(cp), 1) * 0.02, f'{total:.0f}k',
                    ha='center', fontsize=10, fontweight='bold', color='#1a2a3a')

    ax_tco.set_xticks(x)
    ax_tco.set_xticklabels(nms, fontsize=9, color='#334155')
    ax_tco.set_ylabel(f"TCO sur {duree_tco}ans (k MAD)", fontsize=10, fontweight='bold')
    ax_tco.set_title(
        f"Comparaison TCO — {duree_tco}ans | {N_pat}×PAT | Arrêt={tarif_downtime:,}MAD/h",
        fontsize=10, fontweight='bold')
    ax_tco.legend(fontsize=9, facecolor='#f8fafc', edgecolor='#cbd5e1', labelcolor='#1a2a3a')
    plt.tight_layout()
    st.pyplot(fig_tco)
    plt.close()

    st.markdown("---")
    st.markdown('<div class="sh">Sensibilité TCO vs Horizon</div>', unsafe_allow_html=True)
    horizons = np.arange(1, 16)
    fig_ts, ax_ts = plt.subplots(figsize=(10, 4))
    fig_ts.patch.set_facecolor('#f8fafc')
    style_ax(ax_ts)

    for nm, p in MATS.items():
        Em_t    = E0 * p["f"] * K_local * (S_real**2.5)
        Evm_t   = Em_t / p["rho_m"]
        dv_h_t  = (ep_m / Evm_t) / 3600 if Evm_t > 0 else 1e6
        dv_an_t = dv_h_t / (24 * 365)
        cout_c  = COUT_MAT[nm]
        tco_h = []
        for h in horizons:
            nr = max(int(np.ceil(h / dv_an_t)) - 1, 0)
            tco_h.append(
                (nr * (cout_c["prix_set"] + cout_c["tps_pose_h"] * tarif_downtime) * N_pat) / 1e3
            )
        ax_ts.plot(horizons, tco_h, '-o', color=p["c"], lw=2.2, ms=5,
                   label=nm.split('(')[0].strip()[:16])

    ax_ts.axvline(duree_tco, color='#334155', ls='--', lw=1.5, label=f'Horizon={duree_tco}ans')
    ax_ts.set_xlabel("Horizon (ans)", fontsize=10, fontweight='bold')
    ax_ts.set_ylabel("TCO (k MAD)", fontsize=10, fontweight='bold')
    ax_ts.set_title("Évolution TCO dans le temps — tous matériaux", fontsize=10, fontweight='bold')
    ax_ts.legend(fontsize=9, facecolor='#f8fafc', edgecolor='#cbd5e1', labelcolor='#1a2a3a')
    plt.tight_layout()
    st.pyplot(fig_ts)
    plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:rgba(50,90,140,0.45);font-size:.72rem;
            font-family:JetBrains Mono,monospace;'>
  PFE 2025–2026 · École Mohammadia d'Ingénieurs · Weir Minerals North Africa ·
  ANSYS CFX SST k-ω · Warman 10/8 M D₂=549mm
</div>
""", unsafe_allow_html=True)
