"""
=============================================================================
  OUTIL PAT — Système d'Aide à la Décision  v2.0
  Base CFD : Warman 10/8 M | D2=549mm | H_BEP=37.27m | Q_BEP=905.7 m³/h
  PFE 2025-2026 | EMI | Weir Minerals North Africa
  streamlit run outil_v2.py

  NOUVEAUTÉS v2.0 :
    ✅ TCO Material Selector          — Coût total de possession par matériau
    ✅ Fenêtre de Fonctionnement       — Plage opératoire sûre par matériau
    ✅ Correction Cave/Sellgren        — Correction physique HR/ER (pas IA)
    ✅ Modèle Analytique d'Usure       — Truscott (1972), remplace toute approche ML
    ✅ Rapport PDF                     — Export professionnel téléchargeable
=============================================================================
"""
import io
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
from datetime import datetime

st.set_page_config(page_title="Outil PAT — EMI × Weir Minerals", page_icon="⚡",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'Exo 2',sans-serif;background:#060d18;}
::-webkit-scrollbar{width:6px;}
::-webkit-scrollbar-track{background:#0a1628;}
::-webkit-scrollbar-thumb{background:#1e4d8c;border-radius:3px;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#060d18 0%,#0a1628 100%) !important;border-right:1px solid rgba(46,117,182,0.25) !important;}
section[data-testid="stSidebar"] *{color:#c8d8f0 !important;}
section[data-testid="stSidebar"] h2{color:#4FC3F7 !important;font-size:.85rem !important;letter-spacing:2px;text-transform:uppercase;}
section[data-testid="stSidebar"] label{color:#7aa8d4 !important;font-size:.8rem !important;}
section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"]{background:#2E75B6 !important;box-shadow:0 0 8px #2E75B6 !important;}
.main .block-container{background:#060d18;background-image:radial-gradient(ellipse 80% 40% at 50% -10%,rgba(46,117,182,0.15) 0%,transparent 60%),repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(46,117,182,0.04) 40px),repeating-linear-gradient(90deg,transparent,transparent 39px,rgba(46,117,182,0.04) 40px);padding-top:1.5rem !important;}
.hero{position:relative;overflow:hidden;background:linear-gradient(135deg,#040c1a 0%,#0a1e3d 45%,#0d2545 100%);border:1px solid rgba(79,195,247,0.2);border-radius:4px;padding:32px 44px;margin-bottom:24px;box-shadow:0 0 40px rgba(46,117,182,0.15),inset 0 1px 0 rgba(79,195,247,0.1);}
.hero::before{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background:repeating-linear-gradient(90deg,transparent 0px,transparent 48px,rgba(79,195,247,0.03) 48px,rgba(79,195,247,0.03) 49px);pointer-events:none;}
.hero-tag{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:.62rem;letter-spacing:3px;text-transform:uppercase;color:#4FC3F7;border:1px solid rgba(79,195,247,0.35);padding:3px 12px;border-radius:2px;margin-bottom:12px;background:rgba(79,195,247,0.05);}
.hero h1{font-size:2rem;font-weight:800;margin:0 0 8px 0;color:#ffffff;letter-spacing:-0.5px;line-height:1.1;}
.hero h1 span{background:linear-gradient(90deg,#4FC3F7,#2E75B6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero-line{width:48px;height:2px;background:linear-gradient(90deg,#4FC3F7,transparent);margin:10px 0;}
.hero-sub{font-size:.73rem;color:rgba(200,216,240,0.5);font-family:'JetBrains Mono',monospace;letter-spacing:.8px;}
.kpi{background:linear-gradient(145deg,#0c1e36,#0a1628);border:1px solid rgba(46,117,182,0.2);border-radius:4px;padding:16px 14px;text-align:center;position:relative;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.4);}
.kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#2E75B6,transparent);}
.kpi-g::before{background:linear-gradient(90deg,transparent,#00c853,transparent);}
.kpi-r::before{background:linear-gradient(90deg,transparent,#ff1744,transparent);}
.kpi-o::before{background:linear-gradient(90deg,transparent,#ff6d00,transparent);}
.kpi-p::before{background:linear-gradient(90deg,transparent,#aa00ff,transparent);}
.kv{font-size:1.7rem;font-weight:800;color:#e8f4ff;font-family:'Exo 2',sans-serif;}
.kpi-g .kv{color:#00e676;}.kpi-r .kv{color:#ff5252;}.kpi-o .kv{color:#ff9100;}.kpi-p .kv{color:#e040fb;}
.ku{font-size:.68rem;color:rgba(120,160,200,0.65);margin-top:3px;font-family:'JetBrains Mono',monospace;}
.kl{font-size:.6rem;font-weight:600;color:rgba(79,195,247,0.6);text-transform:uppercase;letter-spacing:2px;margin-bottom:4px;font-family:'JetBrains Mono',monospace;}
.sh{color:#4FC3F7;font-size:.78rem;font-weight:700;border-bottom:1px solid rgba(79,195,247,0.2);padding-bottom:6px;margin:18px 0 12px 0;text-transform:uppercase;letter-spacing:2px;font-family:'JetBrains Mono',monospace;}
.ad{background:rgba(255,23,68,0.07);border-left:3px solid #ff1744;border-radius:2px;padding:12px 16px;margin:8px 0;color:#ffcdd2;}
.aw{background:rgba(255,160,0,0.07);border-left:3px solid #ffa000;border-radius:2px;padding:12px 16px;margin:8px 0;color:#ffe082;}
.aok{background:rgba(0,200,83,0.07);border-left:3px solid #00c853;border-radius:2px;padding:12px 16px;margin:8px 0;color:#b9f6ca;}
.info-box{background:rgba(79,195,247,0.06);border-left:3px solid #4FC3F7;border-radius:2px;padding:12px 16px;margin:8px 0;color:#b3d9f5;font-size:.82rem;}
.weir-box{background:linear-gradient(135deg,#0a1628,#0d2040);border-radius:4px;padding:14px 18px;color:#c8d8f0;margin:8px 0;border-left:3px solid #4FC3F7;}
.loss-box{background:linear-gradient(135deg,#1a0608,#3d0d10);border-radius:4px;padding:18px 22px;text-align:center;color:white;margin:10px 0;border:1px solid rgba(255,23,68,0.2);}
.gain-box{background:linear-gradient(135deg,#061a0c,#0d3d18);border-radius:4px;padding:18px 22px;text-align:center;color:white;margin:10px 0;border:1px solid rgba(0,200,83,0.2);}
div[data-testid="metric-container"]{background:#0c1e36;border:1px solid rgba(46,117,182,0.2);border-radius:4px;padding:8px;}
.stTabs [data-baseweb="tab-list"]{background:transparent;gap:4px;}
.stTabs [data-baseweb="tab"]{background:#0c1e36 !important;color:#7aa8d4 !important;border:1px solid rgba(46,117,182,0.2) !important;border-radius:3px !important;font-size:.78rem;letter-spacing:1px;font-family:'JetBrains Mono',monospace;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#0d2545,#1a3a6e) !important;color:#4FC3F7 !important;border-color:rgba(79,195,247,0.4) !important;}
.stDataFrame{background:#0a1628 !important;}
hr{border-color:rgba(46,117,182,0.15) !important;}
.formula-box{background:#0a1628;border:1px solid rgba(79,195,247,0.2);border-radius:4px;padding:14px 18px;margin:10px 0;font-family:'JetBrains Mono',monospace;font-size:.78rem;color:#90CAF9;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="hero-tag">⚡ PFE 2025–2026 · EMI · Weir Minerals North Africa · v2.0</div>
  <h1>Système d'Aide à la Décision <span>PAT</span></h1>
  <div class="hero-line"></div>
  <div class="hero-sub">CFD ANSYS CFX · SST k-ω · Warman 10/8 M · D₂=549mm · H_BEP=37.27m · Q_BEP=905.7 m³/h</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🏭 Réseau ")
    Q_reseau   = st.number_input("Débit réseau Q (m³/h)",         value=864.9, step=10.0, min_value=50.0)
    dP_total   = st.number_input("ΔP total réseau (bar)",          value=45.0,  step=0.5,  min_value=1.0)
    dP_disque  = st.number_input("ΔP disque de dissipation (bar)", value=10.0,  step=0.5,  min_value=0.0)
    rho        = st.number_input("Densité pulpe ρ (kg/m³)",        value=1590.0, step=10.0)

    st.markdown("---")
    st.markdown("## 🔵 Base CFD — Warman 10/8 M")
    st.caption("Valeurs issues de la simulation ANSYS CFX")
    Q_bep  = st.number_input("Q_BEP CFD (m³/h)", value=905.7,  step=10.0)
    H_bep  = st.number_input("H_BEP CFD (m)",    value=37.27,  step=0.1)
    eta_h  = st.number_input("ηh CFD BEP (%)",   value=69.28,  step=0.1) / 100
    E0     = 1.97e-8
    st.markdown(f"**Érosion P24 CFD :** `{E0:.2e}` kg/m²·s")
    D2_base = 549.0; N_base = 715.0

    st.markdown("---")
    st.markdown("## ⚙️ Rendements")
    eta_v    = st.slider("η volumétrique", 0.80, 1.00, 0.91, 0.01)
    eta_elec = st.slider("η électrique",   0.80, 1.00, 0.95, 0.01)

    st.markdown("---")
    st.markdown("## 🔧 Matériau & Érosion")
    MATS = {
        "Linatex® (Weir)":     {"rho_m":960,  "f":1.00, "c":"#2E75B6", "HV":45,  "prix_usd_kg":12.0, "ep_ref":25},
        "Vulco® (Weir)":       {"rho_m":1050, "f":0.85, "c":"#2E7D32", "HV":60,  "prix_usd_kg":18.0, "ep_ref":25},
        "Ultrachrome® (Weir)": {"rho_m":7650, "f":0.45, "c":"#E65100", "HV":650, "prix_usd_kg":9.0,  "ep_ref":12},
        "Fonte au chrome":     {"rho_m":7800, "f":0.48, "c":"#6A0DAD", "HV":700, "prix_usd_kg":7.5,  "ep_ref":12},
    }
    mat_sel   = st.selectbox("Matériau", list(MATS.keys()))
    ep_sac    = st.slider("Épaisseur sacrificielle (mm)", 5, 30, 20, 1)
    EP_MIN    = st.slider("Seuil sécurité minimum (mm)",  3, 15,  5, 1)
    K_local   = st.slider("Facteur sévérité K",           1, 50, 15, 1)
    tarif     = st.number_input("Tarif élec. (MAD/kWh)", value=1.10, step=0.05)
    H_AN      = st.number_input("Heures fonct./an",      value=8000, step=100)

    st.markdown("---")
    st.markdown("## 🔬 Slurry — Correction Physique")
    st.caption("Cave (1976) + Sellgren (1982) — modèle physique analytique")
    d50_mm  = st.number_input("d₅₀ — taille médiane particules (mm)", value=0.10, step=0.01, min_value=0.01, max_value=20.0)
    Cv_pct  = st.slider("Cv — concentration volumique (%)", 1, 55, 30, 1)
    SG_s    = st.number_input("Densité relative solides SG_s", value=3.0, step=0.1, min_value=1.5, max_value=6.0)

    st.markdown("---")
    st.markdown("## 💰 TCO — Paramètres Financiers")
    A_liner_m2  = st.number_input("Superficie garniture (m²)",   value=0.85, step=0.05)
    taux_change = st.number_input("Taux de change MAD/USD",       value=10.0, step=0.5)
    C_main_op   = st.number_input("Main d'œuvre / remplacement (MAD)", value=5000.0, step=500.0)

    st.markdown("---")
    st.markdown("## 💰 Analyse Financière")
    C_invest   = st.number_input("Coût investissement (MAD)", value=2_500_000, step=100000)
    taux_act   = st.slider("Taux d'actualisation (%)", 1, 20, 8, 1) / 100
    duree_proj = st.slider("Durée projet (ans)", 5, 30, 20, 1)
    C_OM_pct   = st.slider("Coût O&M annuel (% invest.)", 1, 10, 3, 1) / 100

# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS PHYSIQUES — PAS DE ML / PAS DE DONNÉES SYNTHÉTIQUES
# ══════════════════════════════════════════════════════════════════════════════

def cave_sellgren_correction(d50_mm, Cv, SG_s, D2_mm, N_rpm, eta_bep):
    """
    Correction Cave/Sellgren — modèle analytique physique.
    Calcule les facteurs de déclassement HR et ER pour une pompe en slurry.

    Références :
      • Cave I.L. (1976) — Performance of centrifugal pumps in slurries
      • Sellgren A. (1982) — Performance of a centrifugal pump when pumping ores and industrial minerals
      • Wilson K.C., Addie G.R., Sellgren A. (2006) — Slurry Transport Using Centrifugal Pumps, 3ᵉ éd.

    NB : Ce modèle est basé sur des corrélations empiriques physiques,
         calibrées sur des données expérimentales de pompes centrifuges en slurry.
         Il n'utilise aucun algorithme d'apprentissage automatique.
    """
    # Vitesse périphérique de la roue [m/s]
    U_tip = np.pi * (D2_mm / 1000) * N_rpm / 60

    # Paramètre de sévérité dimensionnel (Cave 1976, adapté)
    # Φ intègre : taille particules, concentration, densité relative, vitesse
    Phi = (SG_s - 1)**0.4 * Cv**0.45 * d50_mm**0.15 * (U_tip / 15)**0.25

    # Réduction relative (Sellgren 1982, corrélation empirique)
    delta = min(0.0094 * Phi**1.2, 0.30)  # plafonné à 30% pour éviter extrapolation

    # Head Ratio : HR = H_slurry / H_eau
    HR = max(1.0 - delta, 0.70)

    # Efficiency Ratio : ER = η_slurry / η_eau
    # ER < HR car les pertes hydrauliques s'ajoutent aux pertes par friction solide
    extra_loss = delta * (1.0 - eta_bep) / eta_bep
    ER = max(1.0 - delta - extra_loss * 0.5, 0.60)

    return HR, ER, Phi, U_tip, delta


def wear_analytique(E0, mat_f, K_sev, S_factor, d50_mm, Cv, SG_s, D2_mm, N_rpm):
    """
    Modèle analytique d'usure par érosion — Truscott (1972), adapté aux données CFD Warman.

    Ce modèle est une loi de puissance physique basée sur :
      • Finnie I. (1960)     — modèle d'érosion par impact angulaire
      • Truscott G.F. (1972) — wear of centrifugal pump impellers
      • Roco M.C. (1990)     — solid-liquid flow model
      • Calibration sur simulation CFD ANSYS CFX de la Warman 10/8 M (ce PFE)

    LABEL HONNÊTE : C'est un modèle analytique paramétrique, pas un réseau de neurones,
    pas de forêt aléatoire, pas de données synthétiques.
    Les incertitudes sont ±25% (typique pour modèles d'usure empiriques).

    Paramètres :
      E0      — taux d'érosion de référence CFD au BEP [kg/m²·s]
      mat_f   — facteur matériau (relatif à référence)
      K_sev   — facteur de sévérité opératoire (granulométrie, impuretés)
      S_factor — facteur de similitude S (lois d'affinité)
      d50_mm  — taille médiane particules [mm]
      Cv      — fraction volumique solides [-]
      SG_s    — densité relative solides [-]
      D2_mm   — diamètre roue [mm]
      N_rpm   — vitesse rotation [tr/min]
    """
    U_tip = np.pi * (D2_mm / 1000) * N_rpm / 60  # [m/s]

    # Composante cinétique — loi de puissance Truscott (1972) : E ∝ V^2.5
    f_vitesse = S_factor ** 2.5

    # Composante sévérité slurry : E ∝ Cv^0.8 × d50^0.5 × (SG_s-1)^0.6
    Cv_ref = 0.30; d50_ref = 0.10; SG_ref = 3.0
    f_slurry = (Cv / Cv_ref)**0.8 * (d50_mm / d50_ref)**0.5 * ((SG_s - 1) / (SG_ref - 1))**0.6

    E_corr = E0 * mat_f * K_sev * f_vitesse * f_slurry

    return E_corr, U_tip, f_vitesse, f_slurry


def tco_calcul(mat_name, mat_props, duree_h, H_AN, ep_sac_mm, A_m2,
               taux_change, C_main_op_mad, tarif_elec, P_total_kW, taux_act, duree_proj):
    """
    Calcul TCO — Coût Total de Possession sur durée_proj années.
    Inclut : coût garnitures + main d'œuvre + arrêts + énergie récupérée manquée.
    """
    # Masse garniture [kg]
    rho_m   = mat_props["rho_m"]
    masse_kg = A_m2 * (ep_sac_mm / 1000) * rho_m

    # Coût un remplacement [MAD]
    prix_usd_kg = mat_props["prix_usd_kg"]
    cout_mat_mad = masse_kg * prix_usd_kg * taux_change
    cout_remp    = cout_mat_mad + C_main_op_mad  # matériau + main d'oeuvre

    # Fréquence de remplacement par an
    if duree_h < 1:
        duree_h = 1
    remp_par_an = H_AN / duree_h  # peut être < 1 (ex: 0.5 = tous les 2 ans)

    # Coût annuel garnitures
    cout_annuel_garn = remp_par_an * cout_remp

    # Coût arrêt non planifié — pénalité si durée_h < seuil Weir (1800h)
    SEUIL_WEIR = 1800
    penalite_arret = 0
    if duree_h < SEUIL_WEIR:
        # Surcoût d'un arrêt non prévu (estimation 2× main d'œuvre)
        penalite_arret = remp_par_an * C_main_op_mad * 2.0

    # Coût annuel total (garnitures + main d'œuvre + pénalités)
    cout_annuel = cout_annuel_garn + penalite_arret

    # Valeur actualisée sur durée_proj années
    vpn_couts = sum(cout_annuel / (1 + taux_act)**t for t in range(1, duree_proj + 1))

    return {
        "masse_kg":         masse_kg,
        "cout_mat_mad":     cout_mat_mad,
        "cout_remp":        cout_remp,
        "remp_par_an":      remp_par_an,
        "cout_annuel":      cout_annuel,
        "cout_annuel_garn": cout_annuel_garn,
        "penalite_arret":   penalite_arret,
        "vpn_couts":        vpn_couts,
    }


# ══════════════════════════════════════════════════════════════════════════════
# CALCULS PRINCIPAUX
# ══════════════════════════════════════════════════════════════════════════════
g       = 9.81
eta_g   = eta_h * eta_v * eta_elec
Cv      = Cv_pct / 100.0

dP_utile = max(dP_total - dP_disque, 0.1)
H_utile  = dP_utile * 1e5 / (rho * g)
H_total  = dP_total * 1e5 / (rho * g)

S       = (Q_reseau / Q_bep) ** (1/3)
H_unit  = H_bep * S**2
D2_dim  = D2_base * S
N_dim   = N_base / S

N_pat   = max(1, int(np.ceil(H_utile / H_unit)))
H_par_pat = H_utile / N_pat

S_real  = (H_par_pat / H_bep) ** 0.5
D2_real = D2_base * S_real
N_real  = N_base / S_real
Q_real  = Q_bep * S_real**3

Ph_base  = rho * g * (Q_bep/3600) * H_bep / 1000
Prec_base= Ph_base * eta_g
P_unit   = Prec_base * S_real**5
P_total  = P_unit * N_pat

E_an    = P_total * H_AN / 1000
gain    = E_an * 1000 * tarif
CO2     = E_an * 0.72

P_disque  = rho * g * (Q_reseau/3600) * H_total / 1000
E_perdue  = P_disque * H_AN / 1000

Q_fuite_max_Ls = 0.70
Q_fuite_max_m3h= Q_fuite_max_Ls * 3.6
Q_fuite_reel   = Q_real * (1 - eta_v)
weir_eta_v_ok  = Q_fuite_reel <= Q_fuite_max_m3h

mat      = MATS[mat_sel]
rho_poly = mat["rho_m"]

# Érosion avec modèle analytique Truscott (1972)
E_corr, U_tip_calc, f_v, f_sl = wear_analytique(
    E0, mat["f"], K_local, S_real,
    d50_mm, Cv, SG_s, D2_real, N_real
)

Ev       = E_corr / rho_poly
ep_m     = ep_sac / 1000
duree_h  = (ep_m / Ev) / 3600 if Ev > 0 else 1e9
duree_an = duree_h / 24 / 365
usure_mm = Ev * H_AN * 3600 * 1000
ep_res   = max(ep_sac - usure_mm, 0)

WEIR_INSP_H = 1800
weir_ok  = duree_h >= WEIR_INSP_H
alerte   = "DANGER" if ep_res<=EP_MIN else ("WARNING" if ep_res<=EP_MIN*1.8 else "OK")

# Correction Cave/Sellgren au point de fonctionnement réel
HR, ER, Phi_cs, U_tip_cs, delta_cs = cave_sellgren_correction(
    d50_mm, Cv, SG_s, D2_real, N_real, eta_h
)
H_slurry   = H_bep * S_real**2 * HR
eta_slurry = eta_h * ER
P_slurry   = rho * g * (Q_real/3600) * H_slurry / (eta_slurry * eta_v * eta_elec) / 1000 if eta_slurry > 0 else 0

# ══════════════════════════════════════════════════════════════════════════════
# KPI HEADER
# ══════════════════════════════════════════════════════════════════════════════
kpis = [
    (f"{N_pat}",                "unités",    "PATs en série",   "kpi"),
    (f"{S_real:.3f}",           "—",         "Facteur S",       "kpi"),
    (f"{D2_real:.0f}",          "mm",        "D₂ par PAT",      "kpi"),
    (f"{P_total:.1f}",          "kW",        "P totale",        "kpi kpi-g"),
    (f"{HR*100:.1f}% / {ER*100:.1f}%", "HR / ER", "Cave/Sellgren", "kpi kpi-o"),
]
cols=st.columns(5)
for col,(v,u,l,c) in zip(cols,kpis):
    col.markdown(f'<div class="{c}"><div class="kl">{l}</div>'
                 f'<div class="kv">{v}</div><div class="ku">{u}</div></div>',
                 unsafe_allow_html=True)
st.markdown("<br>",unsafe_allow_html=True)

if H_unit > H_utile*1.1:
    st.markdown(f'<div class="aw">⚠️ H unitaire ({H_unit:.1f}m) > H utile ({H_utile:.1f}m) — '
                f'Augmenter le nombre de PATs ou réduire S.</div>',unsafe_allow_html=True)
else:
    st.markdown(f'<div class="aok">✅ Architecture validée — {N_pat} PAT(s) × {H_par_pat:.1f}m = '
                f'{H_utile:.1f}m utile | HR={HR:.3f} | ER={ER:.3f}</div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ONGLETS
# ══════════════════════════════════════════════════════════════════════════════
T1, T2, T3, T4, T5, T6 = st.tabs([
    "📈 Performance & Scaling",
    "🔢 Système Multi-PAT",
    "🔧 Maintenance & Usure",
    "🌍 Bilan Éco & CO₂",
    "💰 TCO Matériaux",
    "🔬 Cave/Sellgren + Fenêtre",
])

C1="#4FC3F7"; C2="#ff5252"; C3="#00e676"; C4="#ff9100"

def style_ax(ax):
    ax.set_facecolor('#060d18')
    ax.tick_params(colors='#7aa8d4', labelsize=9)
    ax.xaxis.label.set_color('#7aa8d4')
    ax.yaxis.label.set_color('#7aa8d4')
    ax.title.set_color('#4FC3F7')
    for spine in ax.spines.values():
        spine.set_edgecolor('#1e4d8c')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(alpha=.15, linestyle='--', color='#1e4d8c')

# ─── TAB 1 ───────────────────────────────────────────────────────────────────
with T1:
    st.markdown('<div class="sh">Dimensionnement par Loi de Similitude</div>',unsafe_allow_html=True)
    st.markdown("---")
    cA,cB = st.columns([1,1.8])
    with cA:
        df_sim = pd.DataFrame({
            "Paramètre":   ["D₂ (mm)","N (tr/min)","Q/PAT (m³/h)","H/PAT (m)","P/PAT (kW)","P totale (kW)"],
            "Base CFD":    [f"{D2_base:.0f}",f"{N_base:.0f}",f"{Q_bep:.1f}",f"{H_bep:.2f}",f"{Prec_base:.2f}","—"],
            f"S={S_real:.3f}": [f"{D2_real:.0f}",f"{N_real:.1f}",f"{Q_real:.1f}",f"{H_par_pat:.2f}",f"{P_unit:.1f}",f"{P_total:.1f}"]
        })
        st.dataframe(df_sim, use_container_width=True, hide_index=True)
    with cB:
        fig,axes=plt.subplots(1,2,figsize=(10,4.5))
        fig.patch.set_facecolor('#0a1628')
        S_r=np.linspace(0.5,2.5,200)
        for ax in axes:
            style_ax(ax)
        ax=axes[0]
        ax.plot(S_r, Prec_base*(S_r**5), '-', color='#00e676', lw=2.5, label='P par PAT')
        ax.plot(S_r, Prec_base*(S_r**5)*np.ceil(H_utile/(H_bep*S_r**2)),'--', color='#4FC3F7', lw=2, label='P totale (N×PAT)')
        ax.axvline(S_real, color='#ff5252', ls='--', lw=2, label=f'S={S_real:.3f}')
        ax.scatter([S_real],[P_unit],color='#ff5252',s=100,zorder=5,edgecolors='white',lw=1.5)
        ax.set_xlabel("Facteur S",fontsize=10,fontweight='bold')
        ax.set_ylabel("Puissance (kW)",fontsize=10,fontweight='bold')
        ax.set_title("Puissance vs S",fontsize=10,fontweight='bold')
        ax.legend(fontsize=8.5,facecolor='#0a1628',edgecolor='#1e4d8c',labelcolor='#c8d8f0')
        ax2=axes[1]
        ax2.plot(S_r, H_bep*S_r**2, '-', color='#4FC3F7', lw=2.5, label='H/PAT requise')
        ax2.axhline(H_utile, color='#ff9100', ls='--', lw=1.8, label=f'H utile={H_utile:.1f}m')
        ax2.axhline(H_total, color='#ff5252', ls=':', lw=1.5, label=f'H totale={H_total:.1f}m')
        ax2.axvline(S_real, color='#ff5252', ls='--', lw=2, label=f'S={S_real:.3f}')
        ax2.set_xlabel("Facteur S",fontsize=10,fontweight='bold')
        ax2.set_ylabel("H (m)",fontsize=10,fontweight='bold')
        ax2.set_title("Hauteur vs S — Compatibilité",fontsize=10,fontweight='bold')
        ax2.legend(fontsize=8,facecolor='#0a1628',edgecolor='#1e4d8c',labelcolor='#c8d8f0')
        plt.tight_layout(); st.pyplot(fig); plt.close()

# ─── TAB 2 ───────────────────────────────────────────────────────────────────
with T2:
    st.markdown('<div class="sh">Architecture Multi-PAT — Bilan de Pression</div>',unsafe_allow_html=True)
    c1p,c2p,c3p,c4p = st.columns(4)
    for col,(v,u,l,c) in zip([c1p,c2p,c3p,c4p],[
        (f"{dP_total:.1f}",  "bar","ΔP total réseau","kpi"),
        (f"{dP_disque:.1f}", "bar","ΔP disque orifice","kpi kpi-r"),
        (f"{dP_utile:.1f}",  "bar","ΔP utile PATs","kpi kpi-g"),
        (f"{N_pat}",          "PATs","Nombre en série","kpi kpi-o"),
    ]):
        col.markdown(f'<div class="{c}"><div class="kl">{l}</div>'
                     f'<div class="kv">{v}</div><div class="ku">{u}</div></div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)

    fig_r,ax_r=plt.subplots(figsize=(13,5.5))
    ax_r.set_xlim(0,13); ax_r.set_ylim(0,6); ax_r.axis('off')
    ax_r.set_facecolor('#060d18'); fig_r.patch.set_facecolor('#060d18')
    ax_r.text(6.5,5.55,f'Architecture réseau — {N_pat} PAT(s) en série | Jorf Lasfar OCP',
              ha='center',fontsize=12,fontweight='bold',color='#4FC3F7')

    def rbox(x,y,w,h,fc,ec,lw=2.0):
        p=FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle="round,pad=0.07",fc=fc,ec=ec,lw=lw,zorder=4)
        ax_r.add_patch(p)
    def arr(x1,y1,x2,y2,c='white',lw=2.2,label=''):
        ax_r.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='->',color=c,lw=lw))
        if label:
            ax_r.text((x1+x2)/2,(y1+y2)/2+0.2,label,ha='center',fontsize=8,color=c,fontweight='bold')

    arr(0.1,3.0,0.9,3.0,'#2E75B6',3,f'Q={Q_reseau:.0f}m³/h')
    rbox(0.65,3.0,0.85,0.6,'#0d2550','#2E75B6')
    ax_r.text(0.65,3.0,'PULPE\nHaute P.',ha='center',va='center',fontsize=7,fontweight='bold',color='#64B5F6',zorder=6)
    arr(1.1,3.0,1.85,3.0,'#ff5252',2.5)
    rbox(2.1,3.0,0.55,0.8,'#1a0608','#ff5252',2.5)
    ax_r.text(2.1,3.05,'⊛',ha='center',va='center',fontsize=18,color='#ff5252',zorder=6)
    ax_r.text(2.1,2.45,f'Disque\n-{dP_disque:.0f}bar',ha='center',fontsize=7.5,color='#ff5252',fontweight='bold')
    arr(2.4,3.0,2.9,3.0,'#ff9100',2,f'{dP_utile:.0f}bar')

    n_show = min(N_pat, 5)
    spacing = min(1.2, 5.5/max(n_show,1))
    x_start = 3.1
    for ni in range(n_show):
        xp = x_start + ni*spacing; yp = 3.0
        c_p=Circle((xp,yp),0.32,fc='#0d2545',ec='#4FC3F7',lw=2,zorder=5)
        ax_r.add_patch(c_p)
        for ang in range(0,360,72):
            th=np.radians(ang)
            ax_r.plot([xp+0.14*np.cos(th),xp+0.29*np.cos(th+np.radians(22))],
                      [yp+0.14*np.sin(th),yp+0.29*np.sin(th+np.radians(22))],'-',color='#4FC3F7',lw=1.5,zorder=6)
        ax_r.text(xp,yp,'⚙',ha='center',va='center',fontsize=9,color='white',zorder=7)
        ax_r.text(xp,yp-0.55,f'PAT {ni+1}',ha='center',fontsize=7,color='#4FC3F7',fontweight='bold')
        ax_r.text(xp,yp-0.82,f'-{H_par_pat:.1f}m',ha='center',fontsize=6.5,color='#90CAF9')
        if ni<n_show-1:
            arr(xp+0.34,yp,xp+spacing-0.34,yp,'#4FC3F7',1.8)
    if N_pat > 5:
        ax_r.text(x_start+5*spacing,3.0,'...',ha='left',va='center',fontsize=16,color='#4FC3F7',fontweight='bold')

    x_after = x_start+(n_show-1)*spacing+0.38
    arr(x_after,3.0,x_after+0.4,3.0,'#4FC3F7',2)
    xG=x_after+0.7
    rbox(xG,3.0,0.7,0.95,'#061a0c','#00e676',2)
    ax_r.text(xG,3.0,'G',ha='center',va='center',fontsize=14,fontweight='bold',color='white',zorder=6)
    ax_r.text(xG,2.4,f'{P_total:.0f}kW',ha='center',fontsize=8,color='#00e676',fontweight='bold')

    plt.tight_layout(); st.pyplot(fig_r); plt.close()

    st.markdown("---")
    st.markdown('<div class="sh">Comparaison des configurations</div>',unsafe_allow_html=True)
    configs=[]
    for n in range(1,7):
        He=dP_utile*1e5/(rho*g)/n
        Sr=(He/H_bep)**0.5 if He>0 else 0
        D2n=D2_base*Sr; Nn=N_base/Sr if Sr>0 else 0
        Pn=Prec_base*Sr**5*n
        E_c, _, _, _ = wear_analytique(E0, mat["f"], K_local, Sr, d50_mm, Cv, SG_s, D2n, Nn)
        Evm=E_c/mat["rho_m"]
        dvn=(ep_m/Evm)/(3600*24*365) if Evm>0 else 999
        ern=max(ep_sac-Evm*H_AN*3600*1000,0)
        configs.append({"N PATs":n,"S par PAT":f"{Sr:.3f}","D₂ (mm)":f"{D2n:.0f}","N (tr/min)":f"{Nn:.0f}",
            "H/PAT (m)":f"{He:.1f}","P totale (kW)":f"{Pn:.1f}","Durée vie (ans)":f"{dvn:.1f}",
            "Ép. résid.":f"{ern:.2f}mm",
            "Conseil":"✅ Optimal" if 0.7<Sr<1.6 else("⚠️ Érosion" if Sr<2.2 else"❌ Éviter")})
    df_conf=pd.DataFrame(configs)
    def hi(row):
        return ['background-color:#0d2545']*len(row) if int(row["N PATs"])==N_pat else ['']*len(row)
    st.dataframe(df_conf.style.apply(hi,axis=1),use_container_width=True,hide_index=True)

# ─── TAB 3 ───────────────────────────────────────────────────────────────────
with T3:
    st.markdown('<div class="sh">Maintenance & Durée de Vie — Validation Weir 1800h</div>',unsafe_allow_html=True)
    st.markdown("""<div class="info-box">⚙️ <b>Modèle utilisé :</b> Truscott (1972) adapté — loi analytique de puissance.
    E ∝ S<sup>2.5</sup> × Cv<sup>0.8</sup> × d50<sup>0.5</sup> × (SG_s−1)<sup>0.6</sup> × f_mat × K.
    Incertitude estimée : ±25%. Pas de ML, pas de données synthétiques.</div>""", unsafe_allow_html=True)

    if not weir_ok:
        st.markdown(f'<div class="ad">🚨 <b>CYCLE WEIR NON RESPECTÉ</b> — Durée vie <b>{duree_h:,.0f} h</b> &lt; seuil Weir <b>{WEIR_INSP_H} h</b></div>',unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="aok">✅ <b>Cycle Weir respecté</b> — Durée vie <b>{duree_h:,.0f} h</b> ≥ {WEIR_INSP_H} h</div>',unsafe_allow_html=True)
    if alerte=="DANGER":
        st.markdown(f'<div class="ad">🚨 <b>USURE CRITIQUE</b> : Ép. résiduelle <b>{ep_res:.2f} mm</b> ≤ seuil {EP_MIN} mm</div>',unsafe_allow_html=True)
    elif alerte=="WARNING":
        st.markdown(f'<div class="aw">⚠️ Ép. résiduelle <b>{ep_res:.2f} mm</b> — Inspection recommandée</div>',unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="aok">✅ Ép. résiduelle <b>{ep_res:.2f} mm</b> — Durée vie : <b>{duree_an:.1f} ans</b></div>',unsafe_allow_html=True)

    cM1,cM2 = st.columns(2)
    with cM1:
        st.markdown("#### Multi-matériaux")
        rows=[]
        for nm,p in MATS.items():
            E_c, _, _, _ = wear_analytique(E0, p["f"], K_local, S_real, d50_mm, Cv, SG_s, D2_real, N_real)
            Evm=E_c/p["rho_m"]
            dvn=(ep_m/Evm)/(3600*24*365) if Evm>0 else 999
            dvh=(ep_m/Evm)/3600 if Evm>0 else 999
            ern=max(ep_sac-Evm*H_AN*3600*1000,0)
            rows.append({"Matériau":nm.split('(')[0].strip(),"E (kg/m²s)":f"{E_c:.2e}","Durée (ans)":f"{dvn:.1f}",
                         "Durée (h)":f"{dvh:,.0f}","Ép. résid.":f"{ern:.2f}mm",
                         "Weir 1800h":"✅" if dvh>=WEIR_INSP_H else "🚨",
                         "État":"🚨" if ern<=EP_MIN else("⚠️" if ern<=EP_MIN*1.8 else"✅")})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    with cM2:
        t_max=max(duree_an*1.3,3); t_r=np.linspace(0,t_max,400)
        fig_t,ax_t=plt.subplots(figsize=(6.5,4))
        fig_t.patch.set_facecolor('#0a1628'); style_ax(ax_t)
        for nm,p in MATS.items():
            E_c, _, _, _ = wear_analytique(E0, p["f"], K_local, S_real, d50_mm, Cv, SG_s, D2_real, N_real)
            Evm=E_c/p["rho_m"]
            ep_t=np.maximum(ep_sac-Evm*t_r*365*24*3600*1000,0)
            ax_t.plot(t_r,ep_t,'-',color=p["c"],lw=2.2,label=nm.split('(')[0].strip()[:16])
        ax_t.axhline(EP_MIN,color='#ff5252',linestyle='--',lw=1.8,label=f'Seuil {EP_MIN}mm')
        ax_t.fill_between(t_r,0,EP_MIN,color='red',alpha=.05)
        ax_t.axvline(WEIR_INSP_H/(365*24),color='#ff9100',linestyle=':',lw=1.8,label=f'Weir {WEIR_INSP_H}h')
        ax_t.set_xlabel("Temps (années)",fontsize=10,fontweight='bold')
        ax_t.set_ylabel("Épaisseur résiduelle (mm)",fontsize=10,fontweight='bold')
        ax_t.set_title(f"Usure paroi — S={S_real:.3f} | K={K_local} | Truscott (1972)",fontsize=9,fontweight='bold')
        ax_t.set_ylim(0,ep_sac*1.12)
        ax_t.legend(fontsize=8.5,facecolor='#0a1628',edgecolor='#1e4d8c',labelcolor='#c8d8f0')
        plt.tight_layout(); st.pyplot(fig_t); plt.close()

# ─── TAB 4 ───────────────────────────────────────────────────────────────────
with T4:
    st.markdown('<div class="sh">Bilan Économique & Impact Environnemental</div>',unsafe_allow_html=True)
    c_av,c_mid,c_ap = st.columns(3)
    with c_av:
        st.markdown(f"""<div class="loss-box">
            <div style="font-size:1rem;font-weight:700;margin-bottom:8px;">🔴 AVANT — Vanne + Disque</div>
            <div style="font-size:1.9rem;font-weight:700;">{P_disque:.1f} kW</div>
            <div style="opacity:.7;font-size:.83rem;">Puissance dissipée</div>
            <hr style="border-color:rgba(255,255,255,.1);margin:8px 0;">
            <div>{E_perdue:.1f} MWh/an perdus</div>
            <div style="color:#ff9999;">{E_perdue*1000*tarif/1e6:.3f} M MAD perdus/an</div>
        </div>""",unsafe_allow_html=True)
    with c_mid:
        st.markdown(f"""<div style="background:linear-gradient(135deg,#0a1628,#0d2545);border-radius:4px;padding:16px;text-align:center;color:white;margin:10px 0;border:1px solid rgba(79,195,247,0.3);">
            <div style="font-size:1rem;font-weight:700;color:#4FC3F7;">⚡ INSTALLATION PAT</div>
            <div>{N_pat} PAT(s) × D₂={D2_real:.0f}mm</div>
            <div style="color:#00e676;">η_global = {eta_g*100:.1f}%</div>
            <div style="opacity:.6;">HR={HR:.3f} | ER={ER:.3f}</div>
        </div>""",unsafe_allow_html=True)
    with c_ap:
        st.markdown(f"""<div class="gain-box">
            <div style="font-size:1rem;font-weight:700;margin-bottom:8px;">🟢 APRÈS — Récupération PAT</div>
            <div style="font-size:1.9rem;font-weight:700;">{P_total:.1f} kW</div>
            <div style="opacity:.7;font-size:.83rem;">Puissance récupérée</div>
            <hr style="border-color:rgba(255,255,255,.1);margin:8px 0;">
            <div>{E_an:.1f} MWh/an récupérés</div>
            <div style="color:#b3ffb3;">{gain/1e6:.3f} M MAD gagnés/an</div>
            <div style="color:#b3ffb3;">🌍 {CO2:.1f} t CO₂ évitées/an</div>
        </div>""",unsafe_allow_html=True)

    st.markdown("---")
    c1f,c2f,c3f,c4f,c5f = st.columns(5)
    arbres = int(CO2*1000/25)
    for col,(v,u,l,c) in zip([c1f,c2f,c3f,c4f,c5f],[
        (f"{gain/1e6:.3f}","M MAD/an","Gain annuel","kpi kpi-g"),
        (f"{CO2:.1f}","t CO₂/an","CO₂ évité","kpi kpi-p"),
        (f"{E_an:.0f}","MWh/an","Énergie récup.","kpi kpi-g"),
        (f"{P_total/P_disque*100:.0f}","%","Taux récup.","kpi kpi-o"),
        (f"≈{arbres:,}","arbres/an","Équiv. arbres","kpi"),
    ]):
        col.markdown(f'<div class="{c}"><div class="kl">{l}</div>'
                     f'<div class="kv">{v}</div><div class="ku">{u}</div></div>',unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — TCO MATERIAL SELECTOR
# ═══════════════════════════════════════════════════════════════════════════════
with T5:
    st.markdown('<div class="sh">TCO — Coût Total de Possession sur Durée de Projet</div>',
                unsafe_allow_html=True)
    st.markdown(f"""<div class="info-box">
    💡 Le TCO intègre : coût matériau + main d'œuvre + pénalités arrêts non planifiés.
    Basé sur le modèle analytique Truscott (1972) pour les durées de vie.
    Durée projet = <b>{duree_proj} ans</b> | Taux actualisation = <b>{taux_act*100:.0f}%</b>
    | Superficie garniture = <b>{A_liner_m2} m²</b>
    </div>""", unsafe_allow_html=True)

    tco_rows = []
    tco_data = {}
    for nm, p in MATS.items():
        E_c, _, _, _ = wear_analytique(E0, p["f"], K_local, S_real, d50_mm, Cv, SG_s, D2_real, N_real)
        Evm = E_c / p["rho_m"]
        dv_h = (ep_m / Evm) / 3600 if Evm > 0 else 999_999
        dv_an = dv_h / 24 / 365

        tco = tco_calcul(nm, p, dv_h, H_AN, ep_sac, A_liner_m2,
                         taux_change, C_main_op, tarif, P_total, taux_act, duree_proj)
        tco_data[nm] = tco

        tco_rows.append({
            "Matériau":           nm.split('(')[0].strip(),
            "Prix (USD/kg)":      f"{p['prix_usd_kg']:.1f}",
            "Masse garniture(kg)":f"{tco['masse_kg']:.1f}",
            "Coût / remp. (MAD)": f"{tco['cout_remp']:,.0f}",
            "Remp./an":           f"{tco['remp_par_an']:.2f}",
            "Coût annuel (MAD)":  f"{tco['cout_annuel']:,.0f}",
            "Pénalité arrêt/an":  f"{tco['penalite_arret']:,.0f}",
            f"VAN {duree_proj}ans (MAD)": f"{tco['vpn_couts']:,.0f}",
            "Durée vie (h)":      f"{dv_h:,.0f}",
            "Durée vie (ans)":    f"{dv_an:.1f}",
            "Weir 1800h":         "✅" if dv_h >= 1800 else "🚨",
        })

    df_tco = pd.DataFrame(tco_rows)

    # Trouver le meilleur matériau (VAN minimale)
    vpn_vals = [tco_data[nm]["vpn_couts"] for nm in MATS]
    best_idx = np.argmin(vpn_vals)
    best_mat = list(MATS.keys())[best_idx]

    def highlight_best(row):
        if row["Matériau"] == best_mat.split('(')[0].strip():
            return ['background-color:#0d3d18; color:#00e676']*len(row)
        return ['']*len(row)

    st.dataframe(df_tco.style.apply(highlight_best, axis=1),
                 use_container_width=True, hide_index=True)
    st.markdown(f'<div class="aok">🏆 <b>Meilleur TCO :</b> {best_mat} '
                f'— VAN = <b>{tco_data[best_mat]["vpn_couts"]:,.0f} MAD</b> '
                f'sur {duree_proj} ans</div>', unsafe_allow_html=True)

    st.markdown("---")
    cT1, cT2 = st.columns(2)

    # Graphique 1 — VAN comparée
    with cT1:
        fig_tco, ax_tco = plt.subplots(figsize=(6.5, 4.5))
        fig_tco.patch.set_facecolor('#0a1628'); style_ax(ax_tco)
        noms_court = [nm.split('(')[0].strip()[:14] for nm in MATS]
        vpn_arr    = [tco_data[nm]["vpn_couts"] / 1e6 for nm in MATS]
        colors_mat = [p["c"] for p in MATS.values()]
        bars = ax_tco.bar(noms_court, vpn_arr, color=colors_mat, edgecolor='#060d18', lw=1.5, width=0.55)
        for b, v in zip(bars, vpn_arr):
            ax_tco.text(b.get_x()+b.get_width()/2, b.get_height()+max(vpn_arr)*0.02,
                        f'{v:.2f}M', ha='center', fontsize=10, fontweight='bold', color='white')
        ax_tco.set_ylabel(f"VAN Coûts sur {duree_proj} ans (M MAD)", fontsize=10, fontweight='bold')
        ax_tco.set_title("Comparaison TCO — VAN des coûts garnitures", fontsize=10, fontweight='bold')
        ax_tco.tick_params(axis='x', colors='#c8d8f0', labelsize=9)
        plt.tight_layout(); st.pyplot(fig_tco); plt.close()

    # Graphique 2 — Coût annuel décomposé
    with cT2:
        fig_stack, ax_stack = plt.subplots(figsize=(6.5, 4.5))
        fig_stack.patch.set_facecolor('#0a1628'); style_ax(ax_stack)
        noms_c = [nm.split('(')[0].strip()[:14] for nm in MATS]
        c_garn  = [tco_data[nm]["cout_annuel_garn"] / 1e3 for nm in MATS]
        c_pen   = [tco_data[nm]["penalite_arret"] / 1e3 for nm in MATS]
        x = np.arange(len(noms_c))
        b1 = ax_stack.bar(x, c_garn, label='Garnitures (MAD)', color=[p["c"] for p in MATS.values()],
                          edgecolor='#060d18', width=0.5)
        b2 = ax_stack.bar(x, c_pen, bottom=c_garn, label='Pénalités arrêt (MAD)',
                          color='#ff5252', alpha=0.7, edgecolor='#060d18', width=0.5)
        ax_stack.set_xticks(x); ax_stack.set_xticklabels(noms_c, fontsize=9)
        ax_stack.tick_params(axis='x', colors='#c8d8f0')
        ax_stack.set_ylabel("Coût annuel (k MAD/an)", fontsize=10, fontweight='bold')
        ax_stack.set_title("Décomposition coût annuel par matériau", fontsize=10, fontweight='bold')
        ax_stack.legend(fontsize=9, facecolor='#0a1628', edgecolor='#1e4d8c', labelcolor='#c8d8f0')
        plt.tight_layout(); st.pyplot(fig_stack); plt.close()

    # Graphique 3 — Évolution cumulative TCO dans le temps
    st.markdown("---")
    st.markdown('<div class="sh">Évolution Cumulative du TCO dans le Temps</div>', unsafe_allow_html=True)
    fig_cum, ax_cum = plt.subplots(figsize=(12, 4.5))
    fig_cum.patch.set_facecolor('#0a1628'); style_ax(ax_cum)
    t_range = np.arange(1, duree_proj + 1)
    for nm, p in MATS.items():
        tco_m = tco_data[nm]
        vpn_cumul = np.array([
            sum(tco_m["cout_annuel"] / (1 + taux_act)**t for t in range(1, yr+1))
            for yr in t_range
        ]) / 1e6
        lbl = nm.split('(')[0].strip()
        style = '-' if nm == best_mat else '--'
        ax_cum.plot(t_range, vpn_cumul, style, color=p["c"], lw=2.5, label=lbl)

    ax_cum.set_xlabel("Années", fontsize=11, fontweight='bold')
    ax_cum.set_ylabel("VAN cumulative coûts (M MAD)", fontsize=11, fontweight='bold')
    ax_cum.set_title(f"TCO cumulatif — {duree_proj} ans | Taux act. {taux_act*100:.0f}%", fontsize=11, fontweight='bold')
    ax_cum.legend(fontsize=9, facecolor='#0a1628', edgecolor='#1e4d8c', labelcolor='#c8d8f0')
    plt.tight_layout(); st.pyplot(fig_cum); plt.close()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — CAVE/SELLGREN + FENÊTRE DE FONCTIONNEMENT
# ═══════════════════════════════════════════════════════════════════════════════
with T6:
    col_cs1, col_cs2 = st.columns([1, 1])

    with col_cs1:
        st.markdown('<div class="sh">Correction Cave/Sellgren — Résultats au Point de Fonctionnement</div>',
                    unsafe_allow_html=True)
        st.markdown("""<div class="formula-box">
Modèle physique analytique — Cave (1976) + Sellgren (1982)<br>
Φ = (SG_s − 1)^0.4 × Cv^0.45 × d50^0.15 × (U_tip/15)^0.25<br>
δ = 0.0094 × Φ^1.2  [réduction relative]<br>
HR = 1 − δ           [Head Ratio : H_slurry / H_eau]<br>
ER = f(HR, η_bep)    [Efficiency Ratio : η_slurry / η_eau]<br>
<br>
Ce modèle est un modèle physique calibré sur données expérimentales.<br>
Il ne contient aucun algorithme de Machine Learning.
        </div>""", unsafe_allow_html=True)

        kpis_cs = [
            (f"{Phi_cs:.4f}",       "—",     "Paramètre Φ",     "kpi"),
            (f"{delta_cs*100:.2f}", "%",     "Réduction δ",     "kpi kpi-o"),
            (f"{HR:.4f}",           "—",     "HR (Head Ratio)", "kpi kpi-g" if HR>0.90 else "kpi kpi-o"),
            (f"{ER:.4f}",           "—",     "ER (Eff. Ratio)", "kpi kpi-g" if ER>0.85 else "kpi kpi-o"),
        ]
        k1,k2,k3,k4 = st.columns(4)
        for col,(v,u,l,c) in zip([k1,k2,k3,k4],kpis_cs):
            col.markdown(f'<div class="{c}"><div class="kl">{l}</div>'
                         f'<div class="kv">{v}</div><div class="ku">{u}</div></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)

        df_perf = pd.DataFrame({
            "Paramètre":    ["H/PAT (m)", "η hydraulique (%)", "P récupérée (kW)", "U_tip (m/s)"],
            "Eau pure":     [f"{H_bep*S_real**2:.2f}", f"{eta_h*100:.2f}", f"{P_total:.1f}", f"{U_tip_cs:.2f}"],
            f"Slurry (Cv={Cv_pct}%)": [
                f"{H_slurry:.2f}",
                f"{eta_slurry*100:.2f}",
                f"{rho*g*(Q_real/3600)*H_slurry/(eta_slurry*eta_v*eta_elec)/1000 if eta_slurry>0 else 0:.1f}",
                f"{U_tip_cs:.2f}"
            ],
            "Déclassement": [
                f"−{(1-HR)*100:.1f}%",
                f"−{(1-ER)*100:.1f}%",
                f"−{(1-ER)*100:.1f}%",
                "—"
            ]
        })
        st.dataframe(df_perf, use_container_width=True, hide_index=True)

        # Sensibilité Cv
        st.markdown("#### Sensibilité à la Concentration Volumique Cv")
        Cv_range = np.linspace(0.05, 0.55, 100)
        HR_Cv, ER_Cv = [], []
        for cv_i in Cv_range:
            hr_i, er_i, _, _, _ = cave_sellgren_correction(d50_mm, cv_i, SG_s, D2_real, N_real, eta_h)
            HR_Cv.append(hr_i); ER_Cv.append(er_i)

        fig_cv, ax_cv = plt.subplots(figsize=(6, 3.5))
        fig_cv.patch.set_facecolor('#0a1628'); style_ax(ax_cv)
        ax_cv.plot(Cv_range*100, HR_Cv, '-', color='#4FC3F7', lw=2.5, label='HR (Head Ratio)')
        ax_cv.plot(Cv_range*100, ER_Cv, '-', color='#00e676', lw=2.5, label='ER (Efficiency Ratio)')
        ax_cv.axvline(Cv_pct, color='#ff5252', ls='--', lw=2, label=f'Cv actuel = {Cv_pct}%')
        ax_cv.axhline(HR, color='#4FC3F7', ls=':', lw=1.5, alpha=0.5)
        ax_cv.axhline(ER, color='#00e676', ls=':', lw=1.5, alpha=0.5)
        ax_cv.set_xlabel("Cv (%)", fontsize=10, fontweight='bold')
        ax_cv.set_ylabel("Ratio [−]", fontsize=10, fontweight='bold')
        ax_cv.set_title(f"Cave/Sellgren — Sensibilité à Cv | d50={d50_mm}mm | SG_s={SG_s}", fontsize=9)
        ax_cv.set_ylim(0.5, 1.02)
        ax_cv.legend(fontsize=9, facecolor='#0a1628', edgecolor='#1e4d8c', labelcolor='#c8d8f0')
        plt.tight_layout(); st.pyplot(fig_cv); plt.close()

    with col_cs2:
        st.markdown('<div class="sh">Fenêtre de Fonctionnement — Plage Opératoire par Matériau</div>',
                    unsafe_allow_html=True)
        st.markdown("""<div class="info-box">
        La fenêtre de fonctionnement définit la plage d₅₀–Cv dans laquelle chaque matériau
        peut opérer avec une durée de vie ≥ seuil Weir (1800h).
        Le point rouge = conditions actuelles (sidebar).
        </div>""", unsafe_allow_html=True)

        # Grille d50 vs Cv
        d50_g = np.linspace(0.02, 5.0, 120)
        Cv_g  = np.linspace(0.02, 0.55, 100)
        D50, CV = np.meshgrid(d50_g, Cv_g)

        fig_win, axes_win = plt.subplots(2, 2, figsize=(11, 8.5))
        fig_win.patch.set_facecolor('#0a1628')
        fig_win.suptitle(f"Fenêtre de Fonctionnement par Matériau | S={S_real:.3f} | K={K_local} | EP={ep_sac}mm",
                         fontsize=11, fontweight='bold', color='#4FC3F7')

        mat_list = list(MATS.items())
        for idx, (nm, p) in enumerate(mat_list):
            ax = axes_win[idx//2][idx%2]
            style_ax(ax)

            # Calcul de la durée de vie sur la grille
            E_grid, _, _, _ = wear_analytique(E0, p["f"], K_local, S_real,
                                               D50, CV, SG_s, D2_real, N_real)
            Ev_grid = E_grid / p["rho_m"]
            dv_grid = np.where(Ev_grid > 0,
                               (ep_m / Ev_grid) / 3600,
                               999_999)

            # Zones : rouge < 1800h, orange 1800-5000h, vert > 5000h
            Z = np.zeros_like(dv_grid)
            Z[dv_grid >= 5000]  = 3
            Z[(dv_grid >= 1800) & (dv_grid < 5000)] = 2
            Z[(dv_grid >= 500)  & (dv_grid < 1800)] = 1

            from matplotlib.colors import ListedColormap, BoundaryNorm
            cmap_z = ListedColormap(['#3d0d10', '#3d2800', '#0d3d18', '#0a2d14'])
            norm_z = BoundaryNorm([0, 1, 2, 3, 4], cmap_z.N)
            pcm = ax.pcolormesh(d50_g, Cv_g*100, Z, cmap=cmap_z, norm=norm_z, shading='auto', alpha=0.85)

            # Contours durée de vie
            CS = ax.contour(d50_g, Cv_g*100, dv_grid/1000,
                            levels=[1.8, 5.0, 10.0, 20.0],
                            colors=['#ff9100', '#4FC3F7', '#00e676', '#00e676'],
                            linewidths=[1.5, 1.5, 1.5, 1.5], linestyles=['--', '-', '-', '-'])
            ax.clabel(CS, inline=True, fontsize=8, fmt='%.0f k·h',
                      colors=['#ff9100', '#4FC3F7', '#00e676', '#00e676'])

            # Point de fonctionnement actuel
            ax.scatter([d50_mm], [Cv_pct], color='#ff5252', s=120,
                       zorder=10, marker='*', edgecolors='white', lw=1, label='Point actuel')
            ax.set_xscale('log')
            ax.set_xlabel("d₅₀ (mm)", fontsize=9, fontweight='bold')
            ax.set_ylabel("Cv (%)", fontsize=9, fontweight='bold')
            ax.set_title(nm.split('(')[0].strip(), fontsize=10, fontweight='bold', color=p["c"])

            # Légende zones
            patches = [
                mpatches.Patch(color='#0a2d14', label='> 5000h ✅'),
                mpatches.Patch(color='#0d3d18', label='1800–5000h ⚠️'),
                mpatches.Patch(color='#3d2800', label='500–1800h 🚨'),
                mpatches.Patch(color='#3d0d10', label='< 500h ❌'),
            ]
            ax.legend(handles=patches, fontsize=7.5, facecolor='#0a1628',
                      edgecolor='#1e4d8c', labelcolor='#c8d8f0', loc='upper right')

        plt.tight_layout(); st.pyplot(fig_win); plt.close()


# ═══════════════════════════════════════════════════════════════════════════════
# RAPPORT PDF — GÉNÉRATION ET TÉLÉCHARGEMENT
# ═══════════════════════════════════════════════════════════════════════════════
def generate_pdf_report():
    """
    Génère un rapport PDF professionnel multi-pages.
    Contenu : Synthèse · Dimensionnement · Cave/Sellgren · TCO · Fenêtre de Fonctionnement
    """
    buf = io.BytesIO()
    BG   = '#060d18'
    BG2  = '#0a1628'
    BLUE = '#4FC3F7'
    GRN  = '#00e676'
    RED  = '#ff5252'
    ORG  = '#ff9100'
    TXT  = '#c8d8f0'
    STXT = '#7aa8d4'

    with PdfPages(buf) as pdf:

        # ─── PAGE 1 : Synthèse exécutive ─────────────────────────────────
        fig = plt.figure(figsize=(11.69, 8.27))  # A4 paysage
        fig.patch.set_facecolor(BG)

        ax_title = fig.add_axes([0, 0.82, 1, 0.18])
        ax_title.set_facecolor('#0a1e3d')
        ax_title.axis('off')
        ax_title.text(0.04, 0.65, "RAPPORT PAT — Système d'Aide à la Décision",
                      fontsize=18, fontweight='bold', color='white', transform=ax_title.transAxes)
        ax_title.text(0.04, 0.25,
                      f"Warman 10/8 M | D₂=549mm | Jorf Lasfar OCP | {datetime.now().strftime('%d/%m/%Y')}",
                      fontsize=10, color=BLUE, transform=ax_title.transAxes, style='italic')
        ax_title.text(0.04, 0.05,
                      "PFE 2025–2026 · École Mohammadia d'Ingénieurs · Weir Minerals North Africa · ANSYS CFX SST k-ω",
                      fontsize=8, color=STXT, transform=ax_title.transAxes)

        kpi_data = [
            ("N° PATs",          f"{N_pat}",          "unités en série"),
            ("Facteur S",        f"{S_real:.3f}",      "—"),
            ("D₂ par PAT",       f"{D2_real:.0f} mm",  "—"),
            ("P récupérée",      f"{P_total:.1f} kW",  f"{E_an:.0f} MWh/an"),
            ("Gain financier",   f"{gain/1e6:.3f}",    "M MAD/an"),
            ("CO₂ évité",        f"{CO2:.1f}",         "t/an"),
            ("HR Cave/Sellgren", f"{HR:.3f}",           f"ER={ER:.3f}"),
            ("Durée vie mat.",   f"{duree_an:.1f} ans", f"{duree_h:,.0f} h"),
        ]
        cols_pdf = 4
        for i, (lbl, val, sub) in enumerate(kpi_data):
            x0 = 0.03 + (i % cols_pdf) * 0.245
            y0 = 0.42 + (1 - i // cols_pdf) * 0.20
            ax_k = fig.add_axes([x0, y0, 0.215, 0.165])
            ax_k.set_facecolor(BG2)
            for spine in ax_k.spines.values():
                spine.set_edgecolor(BLUE); spine.set_linewidth(0.8)
            ax_k.axis('off')
            ax_k.text(0.5, 0.82, lbl, ha='center', fontsize=8, color=STXT,
                      transform=ax_k.transAxes, fontweight='bold')
            ax_k.text(0.5, 0.40, val, ha='center', fontsize=14, fontweight='bold',
                      color=GRN, transform=ax_k.transAxes)
            ax_k.text(0.5, 0.10, sub, ha='center', fontsize=7.5, color=STXT,
                      transform=ax_k.transAxes)

        # Table conditions de fonctionnement
        ax_cond = fig.add_axes([0.03, 0.02, 0.45, 0.38])
        ax_cond.set_facecolor(BG2)
        for spine in ax_cond.spines.values():
            spine.set_edgecolor(BLUE); spine.set_linewidth(0.8)
        ax_cond.axis('off')
        ax_cond.text(0.02, 0.95, "PARAMÈTRES OPÉRATOIRES", fontsize=9,
                     fontweight='bold', color=BLUE, transform=ax_cond.transAxes)
        cond_lines = [
            f"Q réseau        : {Q_reseau:.1f} m³/h",
            f"ΔP total        : {dP_total:.1f} bar",
            f"ΔP utile PATs   : {dP_utile:.1f} bar",
            f"ρ pulpe         : {rho:.0f} kg/m³",
            f"d₅₀ particules  : {d50_mm:.3f} mm",
            f"Cv volumique    : {Cv_pct} %",
            f"SG solides      : {SG_s:.1f}",
            f"Matériau        : {mat_sel.split('(')[0].strip()}",
            f"K sévérité      : {K_local}",
            f"η_global        : {eta_g*100:.1f} %",
        ]
        for j, line in enumerate(cond_lines):
            ax_cond.text(0.04, 0.83 - j*0.085, line, fontsize=8.5,
                         color=TXT, transform=ax_cond.transAxes, fontfamily='monospace')

        # Résultats Cave/Sellgren
        ax_cs = fig.add_axes([0.52, 0.02, 0.45, 0.38])
        ax_cs.set_facecolor(BG2)
        for spine in ax_cs.spines.values():
            spine.set_edgecolor(BLUE); spine.set_linewidth(0.8)
        ax_cs.axis('off')
        ax_cs.text(0.02, 0.95, "CAVE/SELLGREN — CORRECTION PHYSIQUE", fontsize=9,
                   fontweight='bold', color=BLUE, transform=ax_cs.transAxes)
        cs_lines = [
            f"Φ (sévérité)    : {Phi_cs:.4f}",
            f"δ (réduction)   : {delta_cs*100:.2f} %",
            f"HR (Head Ratio) : {HR:.4f}",
            f"ER (Eff. Ratio) : {ER:.4f}",
            f"H slurry/PAT    : {H_slurry:.2f} m",
            f"η slurry        : {eta_slurry*100:.2f} %",
            f"U_tip roue      : {U_tip_cs:.2f} m/s",
            "Modèle : Cave(1976)+Sellgren(1982)",
            "≠ ML — loi physique analytique",
        ]
        for j, line in enumerate(cs_lines):
            color = ORG if j >= 7 else TXT
            ax_cs.text(0.04, 0.83 - j*0.085, line, fontsize=8.5,
                       color=color, transform=ax_cs.transAxes, fontfamily='monospace')

        fig.text(0.5, 0.005, f"Page 1/3 — Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} — PFE EMI × Weir Minerals",
                 ha='center', fontsize=8, color=STXT)
        pdf.savefig(fig, facecolor=BG, dpi=150); plt.close()

        # ─── PAGE 2 : TCO ────────────────────────────────────────────────
        fig2, axes2 = plt.subplots(1, 2, figsize=(11.69, 8.27))
        fig2.patch.set_facecolor(BG)
        fig2.suptitle(f"Analyse TCO — Coût Total de Possession sur {duree_proj} ans | Taux d'act. {taux_act*100:.0f}%",
                      fontsize=13, fontweight='bold', color=BLUE, y=0.97)

        for ax_t in axes2: style_ax(ax_t)

        noms_c = [nm.split('(')[0].strip() for nm in MATS]
        vpn_arr = [tco_data[nm]["vpn_couts"] / 1e6 for nm in MATS]
        clrs    = [p["c"] for p in MATS.values()]

        bars = axes2[0].bar(noms_c, vpn_arr, color=clrs, edgecolor='#060d18', lw=1.5, width=0.55)
        for b, v in zip(bars, vpn_arr):
            axes2[0].text(b.get_x()+b.get_width()/2, b.get_height()+max(vpn_arr)*0.02,
                          f'{v:.2f}M', ha='center', fontsize=10, fontweight='bold', color='white')
        axes2[0].set_ylabel(f"VAN Coûts (M MAD)", fontsize=10, fontweight='bold')
        axes2[0].set_title("VAN des Coûts Totaux", fontsize=11, fontweight='bold')

        t_r2 = np.arange(1, duree_proj + 1)
        for nm, p in MATS.items():
            tco_m = tco_data[nm]
            vpn_c = np.array([
                sum(tco_m["cout_annuel"] / (1 + taux_act)**t for t in range(1, yr+1))
                for yr in t_r2
            ]) / 1e6
            style = '-' if nm == best_mat else '--'
            axes2[1].plot(t_r2, vpn_c, style, color=p["c"], lw=2.5, label=nm.split('(')[0].strip())

        axes2[1].set_xlabel("Années", fontsize=10, fontweight='bold')
        axes2[1].set_ylabel("VAN cumulative (M MAD)", fontsize=10, fontweight='bold')
        axes2[1].set_title(f"TCO Cumulatif — {duree_proj} ans", fontsize=11, fontweight='bold')
        axes2[1].legend(fontsize=9, facecolor=BG2, edgecolor='#1e4d8c', labelcolor='#c8d8f0')

        fig2.text(0.5, 0.005, f"Page 2/3 — Meilleur TCO : {best_mat.split('(')[0].strip()} | PFE EMI × Weir Minerals",
                  ha='center', fontsize=8, color=STXT)
        pdf.savefig(fig2, facecolor=BG, dpi=150); plt.close()

        # ─── PAGE 3 : Fenêtre de Fonctionnement ──────────────────────────
        fig3, axes3 = plt.subplots(2, 2, figsize=(11.69, 8.27))
        fig3.patch.set_facecolor(BG)
        fig3.suptitle(f"Fenêtre de Fonctionnement — Zones de Sécurité par Matériau | S={S_real:.3f} | K={K_local}",
                      fontsize=12, fontweight='bold', color=BLUE, y=0.98)

        d50_p = np.linspace(0.02, 5.0, 100)
        Cv_p  = np.linspace(0.02, 0.55, 80)
        D50p, CVp = np.meshgrid(d50_p, Cv_p)

        from matplotlib.colors import ListedColormap, BoundaryNorm
        cmap_z = ListedColormap(['#3d0d10', '#3d2800', '#0d3d18', '#0a2d14'])
        norm_z = BoundaryNorm([0, 1, 2, 3, 4], cmap_z.N)

        for idx, (nm, p) in enumerate(list(MATS.items())):
            ax_w = axes3[idx//2][idx%2]
            style_ax(ax_w)
            E_g, _, _, _ = wear_analytique(E0, p["f"], K_local, S_real, D50p, CVp, SG_s, D2_real, N_real)
            dv_g = np.where(E_g > 0, (ep_m / (E_g / p["rho_m"])) / 3600, 999_999)
            Z2 = np.zeros_like(dv_g)
            Z2[dv_g >= 5000] = 3
            Z2[(dv_g >= 1800) & (dv_g < 5000)] = 2
            Z2[(dv_g >= 500)  & (dv_g < 1800)] = 1
            ax_w.pcolormesh(d50_p, Cv_p*100, Z2, cmap=cmap_z, norm=norm_z, shading='auto', alpha=0.85)
            CS3 = ax_w.contour(d50_p, Cv_p*100, dv_g/1000,
                               levels=[1.8, 5.0, 10.0],
                               colors=['#ff9100', '#4FC3F7', '#00e676'],
                               linewidths=[1.5, 1.5, 1.5])
            ax_w.clabel(CS3, inline=True, fontsize=7.5, fmt='%.0f k·h',
                        colors=['#ff9100', '#4FC3F7', '#00e676'])
            ax_w.scatter([d50_mm], [Cv_pct], color=RED, s=80, zorder=10,
                         marker='*', edgecolors='white', lw=0.8, label='Point actuel')
            ax_w.set_xscale('log')
            ax_w.set_xlabel("d₅₀ (mm)", fontsize=8, fontweight='bold')
            ax_w.set_ylabel("Cv (%)", fontsize=8, fontweight='bold')
            ax_w.set_title(nm.split('(')[0].strip(), fontsize=9.5, fontweight='bold', color=p["c"])
            patches = [
                mpatches.Patch(color='#0a2d14', label='>5000h ✅'),
                mpatches.Patch(color='#0d3d18', label='1800–5000h'),
                mpatches.Patch(color='#3d2800', label='<1800h 🚨'),
            ]
            ax_w.legend(handles=patches, fontsize=7, facecolor=BG2,
                        edgecolor='#1e4d8c', labelcolor='#c8d8f0', loc='upper right')

        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        fig3.text(0.5, 0.005, f"Page 3/3 — ★ = point actuel (d50={d50_mm}mm, Cv={Cv_pct}%) | PFE EMI × Weir Minerals",
                  ha='center', fontsize=8, color=STXT)
        pdf.savefig(fig3, facecolor=BG, dpi=150); plt.close()

    buf.seek(0)
    return buf.read()


# ─── BOUTON TÉLÉCHARGEMENT PDF ────────────────────────────────────────────────
st.markdown("---")
col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
with col_pdf2:
    st.markdown('<div class="sh" style="text-align:center;">📄 Export Rapport PDF Professionnel</div>',
                unsafe_allow_html=True)
    if st.button("🖨️ Générer & Télécharger le Rapport PDF", use_container_width=True):
        with st.spinner("Génération du rapport PDF en cours..."):
            try:
                pdf_bytes = generate_pdf_report()
                filename = f"Rapport_PAT_Warman_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                st.download_button(
                    label="📥 Télécharger le PDF",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                st.markdown('<div class="aok">✅ Rapport généré avec succès — 3 pages (Synthèse · TCO · Fenêtre)</div>',
                            unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erreur génération PDF : {e}")

st.markdown("""<div style='text-align:center;color:rgba(120,160,200,0.4);font-size:.72rem;font-family:JetBrains Mono,monospace;margin-top:8px;'>
PFE 2025–2026 · École Mohammadia d'Ingénieurs · Weir Minerals North Africa · ANSYS CFX SST k-ω · Warman 10/8 M D₂=549mm · v2.0
</div>""", unsafe_allow_html=True)low_html=True)
