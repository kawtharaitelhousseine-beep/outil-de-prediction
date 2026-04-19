"""
=============================================================================
  OUTIL PAT — Système d'Aide à la Décision 
  Base CFD : Warman 10/8 M | D2=549mm | H_BEP=37.27m | Q_BEP=905.7 m³/h
  PFE 2025-2026 | EMI | Weir Minerals North Africa
  streamlit run outil.py
=============================================================================
"""
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle

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
.weir-box{background:linear-gradient(135deg,#0a1628,#0d2040);border-radius:4px;padding:14px 18px;color:#c8d8f0;margin:8px 0;border-left:3px solid #4FC3F7;}
.loss-box{background:linear-gradient(135deg,#1a0608,#3d0d10);border-radius:4px;padding:18px 22px;text-align:center;color:white;margin:10px 0;border:1px solid rgba(255,23,68,0.2);}
.gain-box{background:linear-gradient(135deg,#061a0c,#0d3d18);border-radius:4px;padding:18px 22px;text-align:center;color:white;margin:10px 0;border:1px solid rgba(0,200,83,0.2);}
div[data-testid="metric-container"]{background:#0c1e36;border:1px solid rgba(46,117,182,0.2);border-radius:4px;padding:8px;}
.stTabs [data-baseweb="tab-list"]{background:transparent;gap:4px;}
.stTabs [data-baseweb="tab"]{background:#0c1e36 !important;color:#7aa8d4 !important;border:1px solid rgba(46,117,182,0.2) !important;border-radius:3px !important;font-size:.78rem;letter-spacing:1px;font-family:'JetBrains Mono',monospace;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#0d2545,#1a3a6e) !important;color:#4FC3F7 !important;border-color:rgba(79,195,247,0.4) !important;}
.stDataFrame{background:#0a1628 !important;}
hr{border-color:rgba(46,117,182,0.15) !important;}
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
    st.markdown("## 🏭 Réseau ")
    Q_reseau   = st.number_input("Débit réseau Q (m³/h)",         value=864.9, step=10.0, min_value=50.0)
    dP_total   = st.number_input("ΔP total réseau (bar)",          value=45.0,  step=0.5,  min_value=1.0)
    dP_disque  = st.number_input("ΔP disque de dissipation (bar)", value=10.0,  step=0.5,  min_value=0.0,
                                  help="Pression absorbée par l'orifice — le reste est utile pour les PATs")
    rho        = st.number_input("Densité pulpe ρ (kg/m³)",        value=1590.0, step=10.0)

    st.markdown("---")
    st.markdown("## 🔵 Base CFD — Warman 10/8 M")
    st.caption("Valeurs issues de la simulation ANSYS CFX")
    Q_bep  = st.number_input("Q_BEP CFD (m³/h)", value=905.7,  step=10.0)
    H_bep  = st.number_input("H_BEP CFD (m)",    value=37.27,  step=0.1)
    eta_h  = st.number_input("ηh CFD BEP (%)",   value=69.28,  step=0.1) / 100
    E0     = 1.97e-8
    st.markdown(f"**Érosion P24 CFD :** `{E0:.2e}` kg/m²·s")
    st.caption("Valeur fixe — sera scalée avec S et K")
    D2_base = 549.0; N_base = 715.0

    st.markdown("---")
    st.markdown("## ⚙️ Rendements")
    eta_v    = st.slider("η volumétrique", 0.80, 1.00, 0.91, 0.01)
    eta_elec = st.slider("η électrique",   0.80, 1.00, 0.95, 0.01)

    st.markdown("---")
    st.markdown("## 🔧 Matériau & Érosion")
    MATS = {
        "Linatex® (Weir)":     {"rho_m":960,  "f":1.00, "c":"#2E75B6"},
        "Vulco® (Weir)":       {"rho_m":1050, "f":0.85, "c":"#2E7D32"},
        "Ultrachrome® (Weir)": {"rho_m":7650, "f":0.45, "c":"#E65100"},
        "Fonte au chrome":     {"rho_m":7800, "f":0.48, "c":"#6A0DAD"},
    }
    mat_sel   = st.selectbox("Matériau", list(MATS.keys()))
    ep_sac    = st.slider("Épaisseur sacrificielle (mm)", 5, 30, 20, 1)
    EP_MIN    = st.slider("Seuil sécurité minimum (mm)",  3, 15,  5, 1)
    K_local   = st.slider("Facteur sévérité K",           1, 50, 15, 1,
                           help="K=15 typique pulpe abrasive OCP")
    tarif     = st.number_input("Tarif élec. (MAD/kWh)", value=1.10, step=0.05)
    H_AN      = st.number_input("Heures fonct./an",      value=8000, step=100)

# ══════════════════════════════════════════════════════════════════════════════
# CALCULS PRINCIPAUX
# ══════════════════════════════════════════════════════════════════════════════
g       = 9.81
eta_g   = eta_h * eta_v * eta_m * eta_elec

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
E_corr   = E0 * mat["f"] * K_local * (S_real ** 2.5)
Ev       = E_corr / rho_poly
ep_m     = ep_sac / 1000
duree_h  = (ep_m / Ev) / 3600 if Ev > 0 else 1e9
duree_an = duree_h / 24 / 365
usure_mm = Ev * H_AN * 3600 * 1000
ep_res   = max(ep_sac - usure_mm, 0)

WEIR_INSP_H = 1800
weir_ok  = duree_h >= WEIR_INSP_H
alerte   = "DANGER" if ep_res<=EP_MIN else ("WARNING" if ep_res<=EP_MIN*1.8 else "OK")

# ══════════════════════════════════════════════════════════════════════════════
# KPI HEADER
# ══════════════════════════════════════════════════════════════════════════════
kpis = [
    (f"{N_pat}",          "unités",    "PATs en série",   "kpi"),
    (f"{S_real:.3f}",     "—",         "Facteur S",       "kpi"),
    (f"{D2_real:.0f}",    "mm",        "D₂ par PAT",      "kpi"),
    (f"{P_total:.1f}",    "kW",        "P totale",        "kpi kpi-g"),
    (f"{CO2:.1f}",        "t CO₂/an",  "CO₂ évité",       "kpi kpi-p"),
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
                f'{H_utile:.1f}m utile | ΔP disque = {dP_disque:.1f}bar</div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ONGLETS
# ══════════════════════════════════════════════════════════════════════════════
T1,T2,T3,T4 = st.tabs([
    "📈 Performance & Scaling",
    "🔢 Système Multi-PAT",
    "🔧 Maintenance & Usure",
    "🌍 Bilan Éco & CO₂"
])

C1="#4FC3F7"; C2="#ff5252"; C3="#00e676"; C4="#ff9100"

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
            ax.set_facecolor('#060d18')
            ax.tick_params(colors='#7aa8d4',labelsize=9)
            ax.xaxis.label.set_color('#7aa8d4'); ax.yaxis.label.set_color('#7aa8d4')
            ax.title.set_color('#4FC3F7')
            for spine in ax.spines.values(): spine.set_edgecolor('#1e4d8c')
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            ax.grid(alpha=.15,linestyle='--',color='#1e4d8c')

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
        S_incompat = S_r[H_bep*S_r**2 > H_utile]
        if len(S_incompat):
            ax2.axvspan(S_incompat[0],S_r[-1],alpha=0.06,color='red')
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
    ax_r.text(0.65,2.45,f'{dP_total:.0f}bar',ha='center',fontsize=7.5,color='#6ca8d4')
    arr(1.1,3.0,1.85,3.0,'#ff5252',2.5)
    rbox(2.1,3.0,0.55,0.8,'#1a0608','#ff5252',2.5)
    ax_r.text(2.1,3.05,'⊛',ha='center',va='center',fontsize=18,color='#ff5252',zorder=6)
    ax_r.text(2.1,2.45,f'Disque\n-{dP_disque:.0f}bar',ha='center',fontsize=7.5,color='#ff5252',fontweight='bold')
    ax_r.text(2.1,1.85,f'Dissipé:\n{dP_disque*1e5/(rho*g):.1f}m',ha='center',fontsize=7,color='#ff9999',style='italic')
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
    arr(xG+0.37,3.0,xG+0.65,3.0,'#00e676',2)
    xR=xG+0.95
    rbox(xR,3.0,0.65,0.9,'#061a0c','#69F0AE',2)
    ax_r.plot([xR,xR],[2.58,3.48],'-',color='#69F0AE',lw=2.5,zorder=6)
    ax_r.plot([xR-.28,xR+.28],[3.25,3.25],'-',color='#69F0AE',lw=2,zorder=6)
    ax_r.plot([xR-.2,xR+.2],[3.0,3.0],'--',color='#69F0AE',lw=1.5,zorder=6)
    ax_r.text(xR,2.32,'Réseau',ha='center',fontsize=7.5,color='#69F0AE',fontweight='bold')
    ax_r.text(xR,2.08,f'{E_an:.0f}MWh/an',ha='center',fontsize=7,color='#b9f6ca')

    bpdata=[(f'Disque ({dP_disque:.0f}bar)',dP_disque,'#ff5252'),(f'PATs {N_pat}× ({dP_utile:.0f}bar)',dP_utile,'#00e676')]
    ax_r.text(0.2,1.55,'Bilan ΔP :',fontsize=8.5,fontweight='bold',color='#4FC3F7')
    x0b=0.2
    for lbl,val,c in bpdata:
        w=val/dP_total*5.5
        ax_r.barh(1.12,w,left=x0b,height=0.32,color=c,alpha=.9)
        ax_r.text(x0b+w/2,1.12,f'{val:.0f}bar',ha='center',va='center',fontsize=8,color='white',fontweight='bold')
        x0b+=w
    ax_r.text(0.2,0.72,'Bilan P :',fontsize=8.5,fontweight='bold',color='#4FC3F7')
    p_items=[('P_disque',P_disque-P_total,'#ff5252'),('P_récup',P_total,'#00e676')]
    x0p=0.2
    for lbl,val,c in p_items:
        w=max(val,0)/P_disque*5.5
        ax_r.barh(0.38,w,left=x0p,height=0.28,color=c,alpha=.88)
        ax_r.text(x0p+w/2,0.38,f'{val:.0f}kW',ha='center',va='center',fontsize=7.5,color='white',fontweight='bold')
        x0p+=w

    plt.tight_layout(); st.pyplot(fig_r); plt.close()

    st.markdown("---")
    st.markdown('<div class="sh">Comparaison des configurations</div>',unsafe_allow_html=True)
    configs=[]
    for n in range(1,7):
        He=dP_utile*1e5/(rho*g)/n
        Sr=(He/H_bep)**0.5 if He>0 else 0
        D2n=D2_base*Sr; Nn=N_base/Sr if Sr>0 else 0
        Pn=Prec_base*Sr**5*n
        Em=E0*mat["f"]*K_local*(Sr**2.5); Evm=Em/mat["rho_m"]
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
    if not weir_ok:
        st.markdown(f'<div class="ad">🚨 <b>CYCLE WEIR NON RESPECTÉ</b> — Durée vie <b>{duree_h:,.0f} h</b> &lt; seuil Weir <b>{WEIR_INSP_H} h</b></div>',unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="aok">✅ <b>Cycle Weir respecté</b> — Durée vie <b>{duree_h:,.0f} h</b> ≥ {WEIR_INSP_H} h</div>',unsafe_allow_html=True)
    if alerte=="DANGER":
        st.markdown(f'<div class="ad">🚨 <b>USURE CRITIQUE — {mat_sel.split("(")[0]}</b> : Ép. résiduelle <b>{ep_res:.2f} mm</b> ≤ seuil {EP_MIN} mm — Remplacement avant <b>{duree_an:.2f} ans</b></div>',unsafe_allow_html=True)
    elif alerte=="WARNING":
        st.markdown(f'<div class="aw">⚠️ Ép. résiduelle <b>{ep_res:.2f} mm</b> — Inspection recommandée</div>',unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="aok">✅ Ép. résiduelle <b>{ep_res:.2f} mm</b> — Durée vie : <b>{duree_an:.1f} ans</b></div>',unsafe_allow_html=True)

    cM1,cM2 = st.columns(2)
    with cM1:
        st.markdown("#### Multi-matériaux")
        rows=[]
        for nm,p in MATS.items():
            Em=E0*p["f"]*K_local*(S_real**2.5); Evm=Em/p["rho_m"]
            dvn=(ep_m/Evm)/(3600*24*365) if Evm>0 else 999
            dvh=(ep_m/Evm)/3600 if Evm>0 else 999
            ern=max(ep_sac-Evm*H_AN*3600*1000,0)
            rows.append({"Matériau":nm.split('(')[0].strip(),"E (kg/m²s)":f"{Em:.2e}","Durée (ans)":f"{dvn:.1f}",
                         "Durée (h)":f"{dvh:,.0f}","Ép. résid.":f"{ern:.2f}mm",
                         "Weir 1800h":"✅" if dvh>=WEIR_INSP_H else "🚨",
                         "État":"🚨" if ern<=EP_MIN else("⚠️" if ern<=EP_MIN*1.8 else"✅")})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

    with cM2:
        t_max=max(duree_an*1.3,3); t_r=np.linspace(0,t_max,400)
        fig_t,ax_t=plt.subplots(figsize=(6.5,4))
        fig_t.patch.set_facecolor('#0a1628'); ax_t.set_facecolor('#060d18')
        ax_t.tick_params(colors='#7aa8d4',labelsize=9)
        ax_t.xaxis.label.set_color('#7aa8d4'); ax_t.yaxis.label.set_color('#7aa8d4')
        ax_t.title.set_color('#4FC3F7')
        for spine in ax_t.spines.values(): spine.set_edgecolor('#1e4d8c')
        ax_t.spines['top'].set_visible(False); ax_t.spines['right'].set_visible(False)
        ax_t.grid(alpha=.15,linestyle='--',color='#1e4d8c')
        for nm,p in MATS.items():
            Em=E0*p["f"]*K_local*(S_real**2.5); Evm=Em/p["rho_m"]
            ep_t=np.maximum(ep_sac-Evm*t_r*365*24*3600*1000,0)
            ax_t.plot(t_r,ep_t,'-',color=p["c"],lw=2.2,label=nm.split('(')[0].strip()[:16])
        ax_t.axhline(EP_MIN,color='#ff5252',linestyle='--',lw=1.8,label=f'Seuil {EP_MIN}mm')
        ax_t.fill_between(t_r,0,EP_MIN,color='red',alpha=.05)
        t_weir_an=WEIR_INSP_H/(365*24)
        ax_t.axvline(t_weir_an,color='#ff9100',linestyle=':',lw=1.8,label=f'Weir {WEIR_INSP_H}h')
        ax_t.set_xlabel("Temps (années)",fontsize=10,fontweight='bold')
        ax_t.set_ylabel("Épaisseur résiduelle (mm)",fontsize=10,fontweight='bold')
        ax_t.set_title(f"Usure paroi — S={S_real:.3f} | K={K_local}",fontsize=10,fontweight='bold')
        ax_t.set_ylim(0,ep_sac*1.12)
        ax_t.legend(fontsize=8.5,facecolor='#0a1628',edgecolor='#1e4d8c',labelcolor='#c8d8f0')
        plt.tight_layout(); st.pyplot(fig_t); plt.close()

        S_range=np.linspace(0.5,2.0,200); dv_S=[]
        for sv in S_range:
            Em=E0*mat["f"]*K_local*(sv**2.5); Evm=Em/mat["rho_m"]
            dv_S.append((ep_m/Evm)/3600 if Evm>0 else 1e6)
        fig_s,ax_s=plt.subplots(figsize=(6.5,3.8))
        fig_s.patch.set_facecolor('#0a1628'); ax_s.set_facecolor('#060d18')
        ax_s.tick_params(colors='#7aa8d4',labelsize=9)
        ax_s.xaxis.label.set_color('#7aa8d4'); ax_s.yaxis.label.set_color('#7aa8d4')
        ax_s.title.set_color('#4FC3F7')
        for spine in ax_s.spines.values(): spine.set_edgecolor('#1e4d8c')
        ax_s.spines['top'].set_visible(False); ax_s.spines['right'].set_visible(False)
        ax_s.grid(alpha=.15,linestyle='--',color='#1e4d8c')
        ax_s.plot(S_range,np.array(dv_S)/1000,'-',color=mat["c"],lw=2.5)
        ax_s.axvline(S_real,color='#ff5252',ls='--',lw=2,label=f'S={S_real:.3f}')
        ax_s.axhline(WEIR_INSP_H/1000,color='#ff9100',ls=':',lw=2,label=f'Seuil Weir {WEIR_INSP_H}h')
        ax_s.set_xlabel("Facteur S",fontsize=10,fontweight='bold')
        ax_s.set_ylabel("Durée de vie (×1000 h)",fontsize=10,fontweight='bold')
        ax_s.set_title(f"Durée vie vs S — {mat_sel.split('(')[0]}",fontsize=10,fontweight='bold')
        ax_s.legend(fontsize=9,facecolor='#0a1628',edgecolor='#1e4d8c',labelcolor='#c8d8f0')
        plt.tight_layout(); st.pyplot(fig_s); plt.close()

# ─── TAB 4 ───────────────────────────────────────────────────────────────────
with T4:
    st.markdown('<div class="sh">Bilan Économique & Impact Environnemental — Avant vs Après PAT</div>',unsafe_allow_html=True)
    c_av,c_mid,c_ap = st.columns(3)
    with c_av:
        st.markdown(f"""<div class="loss-box">
            <div style="font-size:1rem;font-weight:700;margin-bottom:8px;">🔴 AVANT — Vanne + Disque</div>
            <div style="font-size:1.9rem;font-weight:700;">{P_disque:.1f} kW</div>
            <div style="opacity:.7;font-size:.83rem;">Puissance totale dissipée</div>
            <hr style="border-color:rgba(255,255,255,.1);margin:8px 0;">
            <div style="font-size:1.1rem;font-weight:600;">{E_perdue:.1f} MWh/an perdus</div>
            <div style="font-size:1rem;color:#ff9999;margin-top:5px;">{E_perdue*1000*tarif/1e6:.3f} M MAD perdus/an</div>
            <div style="margin-top:5px;color:#ff9999;font-size:.88rem;">🌍 {E_perdue*0.72:.1f} t CO₂ non valorisées</div>
        </div>""",unsafe_allow_html=True)
    with c_mid:
        st.markdown(f"""<div style="background:linear-gradient(135deg,#0a1628,#0d2545);border-radius:4px;padding:16px;text-align:center;color:white;margin:10px 0;border:1px solid rgba(79,195,247,0.3);">
            <div style="font-size:1.1rem;font-weight:700;margin-bottom:8px;color:#4FC3F7;">⚡ INSTALLATION PAT</div>
            <div style="font-size:1rem;margin:6px 0;">{N_pat} PAT(s) × D₂={D2_real:.0f}mm</div>
            <div style="font-size:.9rem;opacity:.7;">S = {S_real:.3f}</div>
            <div style="font-size:.9rem;opacity:.7;">N = {N_real:.0f} tr/min</div>
            <div style="font-size:.9rem;opacity:.7;">ΔP disque = {dP_disque:.0f}bar conservé</div>
            <div style="margin-top:8px;font-size:.95rem;color:#00e676;">η_global = {eta_g*100:.1f}%</div>
            <div style="font-size:.85rem;opacity:.6;margin-top:4px;">{mat_sel.split("(")[0].strip()}</div>
        </div>""",unsafe_allow_html=True)
    with c_ap:
        st.markdown(f"""<div class="gain-box">
            <div style="font-size:1rem;font-weight:700;margin-bottom:8px;">🟢 APRÈS — Récupération PAT</div>
            <div style="font-size:1.9rem;font-weight:700;">{P_total:.1f} kW</div>
            <div style="opacity:.7;font-size:.83rem;">Puissance récupérée ({N_pat} PATs)</div>
            <hr style="border-color:rgba(255,255,255,.1);margin:8px 0;">
            <div style="font-size:1.1rem;font-weight:600;">{E_an:.1f} MWh/an récupérés</div>
            <div style="font-size:1rem;color:#b3ffb3;margin-top:5px;">{gain/1e6:.3f} M MAD gagnés/an</div>
            <div style="margin-top:5px;color:#b3ffb3;font-size:.88rem;">🌍 {CO2:.1f} t CO₂ évitées/an</div>
        </div>""",unsafe_allow_html=True)

    st.markdown("---")
    fig_eco,axes_eco=plt.subplots(1,3,figsize=(13,4.5))
    fig_eco.patch.set_facecolor('#0a1628')
    for ax_e,vals,labels,title,colors in [
        (axes_eco[0],[P_disque,P_total,P_disque-P_total],['Dissipée\n(avant)','Récupérée\n(PAT)','Pertes\nnettes'],'Puissance (kW)',['#ff5252','#00e676','#555555']),
        (axes_eco[1],[E_perdue,E_an],['Énergie perdue\n(avant)','Énergie récupérée\n(PAT)'],'Énergie (MWh/an)',['#ff5252','#00e676']),
        (axes_eco[2],[E_perdue*0.72,CO2],['CO₂ non\nvalorisé','CO₂\névité (PAT)'],'CO₂ (t/an)',['#ff9100','#00e676']),
    ]:
        ax_e.set_facecolor('#060d18')
        ax_e.tick_params(colors='#7aa8d4',labelsize=9)
        ax_e.title.set_color('#4FC3F7')
        for spine in ax_e.spines.values(): spine.set_edgecolor('#1e4d8c')
        ax_e.spines['top'].set_visible(False); ax_e.spines['right'].set_visible(False)
        ax_e.grid(axis='y',alpha=.15,linestyle='--',color='#1e4d8c')
        ax_e.tick_params(axis='x',colors='#c8d8f0')
        bars=ax_e.bar(labels,vals,color=colors,width=0.5,edgecolor='#060d18',lw=1.5)
        for b,v in zip(bars,vals):
            ax_e.text(b.get_x()+b.get_width()/2,b.get_height()+max(vals)*0.02,f'{v:.0f}',ha='center',fontsize=11,fontweight='bold',color='white')
        ax_e.set_title(title,fontsize=11,fontweight='bold')

    fig_eco.suptitle(f'Bilan Avant/Après PAT | Q={Q_reseau:.0f}m³/h | ΔP={dP_total:.0f}bar | {N_pat}×PAT D₂={D2_real:.0f}mm',
                     fontsize=11,fontweight='bold',color='#4FC3F7')
    plt.tight_layout(); st.pyplot(fig_eco); plt.close()

    st.markdown("---")
    c1f,c2f,c3f,c4f,c5f = st.columns(5)
    arbres = int(CO2*1000/25)
    for col,(v,u,l,c) in zip([c1f,c2f,c3f,c4f,c5f],[
        (f"{gain/1e6:.3f}","M MAD/an","Gain annuel","kpi kpi-g"),
        (f"{CO2:.1f}","t CO₂/an","CO₂ évité","kpi kpi-p"),
        (f"{E_an:.0f}","MWh/an","Énergie récup.","kpi kpi-g"),
        (f"{P_total/P_disque*100:.0f}","%","Taux récupération","kpi kpi-o"),
        (f"≈{arbres:,}","arbres/an","Équiv. arbres","kpi"),
    ]):
        col.markdown(f'<div class="{c}"><div class="kl">{l}</div>'
                     f'<div class="kv">{v}</div><div class="ku">{u}</div></div>',unsafe_allow_html=True)

st.markdown("---")
st.markdown("""<div style='text-align:center;color:#bbb;font-size:.78rem;'>
PFE 2025–2026 — École Mohammadia d'Ingénieurs | Weir Minerals North Africa|
ANSYS CFX SST k-ω | Warman 10/8 M D₂=549mm | H_BEP=37.27m | Q_BEP=905.7m³/h
</div>""", unsafe_allow_html=True)
