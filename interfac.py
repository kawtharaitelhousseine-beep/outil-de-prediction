"""
=============================================================================
  OUTIL PAT — Système d'Aide à la Décision 
  Base CFD : Warman 10/8 M | D2=549mm | H_BEP=37.27m | Q_BEP=905.7 m³/h
  PFE 2025-2026 | EMI | Weir Minerals North Africa
  streamlit run interfac.py
=============================================================================
"""
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle

st.set_page_config(page_title="outil de prediction pour PAT", page_icon="⚡",
                   layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.hero{background:linear-gradient(135deg,#0d1b2a,#1F3864 50%,#2E75B6);
  color:white;padding:26px 36px;border-radius:14px;margin-bottom:20px;
  text-align:center;box-shadow:0 8px 32px rgba(31,56,100,.45);}
.hero h1{font-size:1.85rem;margin:0 0 6px 0;}
.hero p{margin:0;opacity:.85;font-size:.88rem;}
.kpi{background:white;border-radius:12px;padding:14px 16px;
  box-shadow:0 2px 12px rgba(0,0,0,.09);border-top:4px solid #2E75B6;text-align:center;}
.kpi-g{border-top-color:#2E7D32;}.kpi-g .kv{color:#2E7D32;}
.kpi-r{border-top-color:#C00000;}.kpi-r .kv{color:#C00000;}
.kpi-o{border-top-color:#E65100;}.kpi-o .kv{color:#E65100;}
.kpi-p{border-top-color:#6A0DAD;}.kpi-p .kv{color:#6A0DAD;}
.kv{font-size:1.6rem;font-weight:700;color:#1F3864;}
.ku{font-size:.78rem;color:#888;margin-top:2px;}
.kl{font-size:.7rem;font-weight:600;color:#aaa;text-transform:uppercase;
  letter-spacing:.7px;margin-bottom:2px;}
.sh{color:#1F3864;font-size:1.05rem;font-weight:700;
  border-bottom:2px solid #2E75B6;padding-bottom:4px;margin:14px 0 10px 0;}
.ad{background:#fff0f0;border-left:5px solid #C00000;border-radius:8px;
  padding:12px 16px;margin:8px 0;}
.aw{background:#fffbe6;border-left:5px solid #F9A825;border-radius:8px;
  padding:12px 16px;margin:8px 0;}
.aok{background:#f0fbf0;border-left:5px solid #2E7D32;border-radius:8px;
  padding:12px 16px;margin:8px 0;}
.weir-box{background:linear-gradient(135deg,#1a1a40,#1F3864);border-radius:10px;
  padding:14px 18px;color:white;margin:8px 0;border-left:4px solid #4FC3F7;}
.loss-box{background:linear-gradient(135deg,#2a0d0d,#5c1a1a);border-radius:12px;
  padding:16px 20px;text-align:center;color:white;margin:10px 0;}
.gain-box{background:linear-gradient(135deg,#0d2a14,#1a5c1a);border-radius:12px;
  padding:16px 20px;text-align:center;color:white;margin:10px 0;}
div[data-testid="metric-container"]{background:#f8faff;
  border:1px solid #d8e4f0;border-radius:10px;padding:8px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>⚡ Système d'Aide à la Décision </h1>
  <p>Récupération d'énergie hydraulique 
     CFD ANSYS CFX SST k-ω | Warman 10/8 M D₂=549mm | PFE 2025–2026 EMI</p>
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
    eta_m    = st.slider("η mécanique",    0.80, 1.00, 0.96, 0.01)
    eta_elec = st.slider("η électrique",   0.80, 1.00, 0.95, 0.01)

 st.markdown("---")
    st.markdown("## 🔧 Matériau & Érosion")
    MATS = {
        "PTFE": {
            "rho_m": 2150,
            "f": 0.32,
            "c": "#8E24AA",
            "comment": "Polytétrafluoroéthylène (Teflon) : Résistance chimique exceptionnelle et très faible coefficient de frottement. Idéal pour slurries corrosives et fines. Excellente tenue à l'érosion par impact doux. Limité en température (>150-200°C) et moins résistant aux particules très dures."
        },
        "PVC": {
            "rho_m": 1400,
            "f": 1.55,
            "c": "#F57C00",
            "comment": "Polyvinyl Chloride rigide : Bon marché et facile à mettre en œuvre. Résistance mécanique moyenne et sensibilité élevée à l'abrasion. Convient pour slurries peu agressives, basses pressions et températures modérées (<60°C). À éviter en milieu très abrasif."
        },
        "Caoutchouc": {
            "rho_m": 1150,
            "f": 0.82,
            "c": "#2E7D32",
            "comment": "Caoutchouc naturel ou synthétique : Excellent amortissement des chocs et absorption d'énergie des particules. Très bonne résistance à l'érosion par impact (fine à moyenne particules). Sensible aux huiles, solvants et hautes températures (>80-100°C)."
        },
        "Fonte au chrome": {
            "rho_m": 7800,
            "f": 0.48,
            "c": "#1B263B",
            "comment": "High Chrome White Iron (typ. 27% Cr) : Excellente résistance à l'abrasion par glissement et particules dures/anguleuses. Très haute dureté (≈60 HRC). Idéal pour slurries très abrasives (phosphate OCP). Moins performant en choc pur que les élastomères."
        }
    }
    mat_sel = st.selectbox("Matériau de revêtement / pièce d'usure", list(MATS.keys()))
    mat_tmp = MATS[mat_sel]
    st.caption(f"📋 {mat_tmp['comment']}")
    ep_sac  = st.slider("Épaisseur sacrificielle (mm)", min_value=3, max_value=80,
                         value=12 if mat_sel in ["PTFE","PVC","Caoutchouc"] else 25, step=1,
                         help="Plus élevée pour Fonte au chrome ; plus faible pour polymères")
    EP_MIN  = st.slider("Seuil sécurité minimum (mm)", min_value=1, max_value=15,
                         value=4 if mat_sel in ["PTFE","PVC","Caoutchouc"] else 8, step=1)
    K_local = st.slider("Facteur sévérité locale K", min_value=1, max_value=80,
                         value=18 if mat_sel in ["PTFE","PVC","Caoutchouc"] else 25, step=1,
                         help="K plus élevé pour Fonte au chrome dans pulpe très abrasive (OCP typique K=20-40)")
    tarif   = st.number_input("Tarif élec. (MAD/kWh)", value=1.10, step=0.05)
    H_AN    = st.number_input("Heures de fonctionnement / an", value=8000, step=100)
# ══════════════════════════════════════════════════════════════════════════════
# CALCULS PRINCIPAUX
# ══════════════════════════════════════════════════════════════════════════════
g       = 9.81
eta_g   = eta_h * eta_v * eta_m * eta_elec

# ── Architecture réseau ───────────────────────────────────────────────────────
dP_utile = max(dP_total - dP_disque, 0.1)           # bar utile pour PATs
H_utile  = dP_utile * 1e5 / (rho * g)               # m hauteur utile
H_total  = dP_total * 1e5 / (rho * g)               # m hauteur totale

# ── Similitude sur une PAT unitaire ──────────────────────────────────────────
S       = (Q_reseau / Q_bep) ** (1/3)
H_unit  = H_bep * S**2                               # m chaque PAT unitaire
D2_dim  = D2_base * S
N_dim   = N_base / S

# ── Nombre de PATs en série pour absorber H_utile ────────────────────────────
N_pat   = max(1, int(np.ceil(H_utile / H_unit)))     # arrondi supérieur
H_par_pat = H_utile / N_pat                          # hauteur réelle par PAT

# Recalculer S avec hauteur réelle par PAT
S_real  = (H_par_pat / H_bep) ** 0.5
D2_real = D2_base * S_real
N_real  = N_base / S_real
Q_real  = Q_bep * S_real**3                          # débit par PAT

# Puissance
Ph_base  = rho * g * (Q_bep/3600) * H_bep / 1000
Prec_base= Ph_base * eta_g
P_unit   = Prec_base * S_real**5                     # kW par PAT
P_total  = P_unit * N_pat                            # kW total

E_an    = P_total * H_AN / 1000                      # MWh/an
gain    = E_an * 1000 * tarif                        # MAD/an
CO2     = E_an * 0.72                                # tCO2/an

# Puissance dissipée vanne (avant PAT)
P_disque  = rho * g * (Q_reseau/3600) * H_total / 1000
E_perdue  = P_disque * H_AN / 1000

# ── Rendement volumétrique — validation Weir ─────────────────────────────────
Q_fuite_max_Ls = 0.70   # L/s — châssis E selon Weir manual 10/8 E-M
Q_fuite_max_m3h= Q_fuite_max_Ls * 3.6
Q_fuite_reel   = Q_real * (1 - eta_v)              # m³/h fuite estimée
weir_eta_v_ok  = Q_fuite_reel <= Q_fuite_max_m3h

# ── Érosion ──────────────────────────────────────────────────────────────────
mat      = MATS[mat_sel]
rho_poly = mat["rho_m"]
E_corr   = E0 * mat["f"] * K_local * (S_real ** 2.5)
Ev       = E_corr / rho_poly                         # m/s vitesse usure
ep_m     = ep_sac / 1000
duree_h  = (ep_m / Ev) / 3600 if Ev > 0 else 1e9
duree_an = duree_h / 24 / 365
usure_mm = Ev * H_AN * 3600 * 1000                  # mm/an
ep_res   = max(ep_sac - usure_mm, 0)

WEIR_INSP_H = 1800                                   # heures — cycle Weir
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

C1="#1F3864"; C2="#C00000"; C3="#2E7D32"; C4="#E65100"

# ─── TAB 1 — Performance & Scaling ───────────────────────────────────────────
with T1:
    st.markdown('<div class="sh">Dimensionnement par Loi de Similitude</div>',
                unsafe_allow_html=True)

    # Weir validation — calculs en arrière-plan, non affichés
    st.markdown("---")
    cA,cB = st.columns([1,1.8])
    with cA:
        df_sim = pd.DataFrame({
            "Paramètre":   ["D₂ (mm)","N (tr/min)","Q/PAT (m³/h)","H/PAT (m)","P/PAT (kW)","P totale (kW)"],
            "Base CFD":    [f"{D2_base:.0f}",f"{N_base:.0f}",f"{Q_bep:.1f}",f"{H_bep:.2f}",
                            f"{Prec_base:.2f}","—"],
            f"S={S_real:.3f}": [f"{D2_real:.0f}",f"{N_real:.1f}",f"{Q_real:.1f}",
                                 f"{H_par_pat:.2f}",f"{P_unit:.1f}",f"{P_total:.1f}"]
        })
        st.dataframe(df_sim, use_container_width=True, hide_index=True)

    with cB:
        fig,axes=plt.subplots(1,2,figsize=(10,4.5))
        S_r=np.linspace(0.5,2.5,200)

        ax=axes[0]
        ax.plot(S_r, Prec_base*(S_r**5), '-', color=C3, lw=2.5, label='P par PAT')
        ax.plot(S_r, Prec_base*(S_r**5)*np.ceil(H_utile/(H_bep*S_r**2)),
                '--', color=C1, lw=2, label='P totale (N×PAT)')
        ax.axvline(S_real, color=C2, ls='--', lw=2, label=f'S={S_real:.3f}')
        ax.scatter([S_real],[P_unit],color=C2,s=100,zorder=5,edgecolors='white',lw=1.5)
        ax.set_xlabel("Facteur S",fontsize=10,fontweight='bold')
        ax.set_ylabel("Puissance (kW)",fontsize=10,fontweight='bold')
        ax.set_title("Puissance vs S",fontsize=10,fontweight='bold',color=C1)
        ax.legend(fontsize=8.5); ax.grid(alpha=.22,linestyle='--')
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

        ax2=axes[1]
        ax2.plot(S_r, H_bep*S_r**2, '-', color=C1, lw=2.5, label='H/PAT requise')
        ax2.axhline(H_utile, color='orange', ls='--', lw=1.8, label=f'H utile={H_utile:.1f}m')
        ax2.axhline(H_total, color=C2, ls=':', lw=1.5, label=f'H totale={H_total:.1f}m')
        ax2.axvline(S_real, color=C2, ls='--', lw=2, label=f'S={S_real:.3f}')
        S_incompat = S_r[H_bep*S_r**2 > H_utile]
        if len(S_incompat):
            ax2.axvspan(S_incompat[0],S_r[-1],alpha=0.08,color='red',label='H > H_utile')
        ax2.set_xlabel("Facteur S",fontsize=10,fontweight='bold')
        ax2.set_ylabel("H (m)",fontsize=10,fontweight='bold')
        ax2.set_title("Hauteur vs S — Compatibilité",fontsize=10,fontweight='bold',color=C1)
        ax2.legend(fontsize=8); ax2.grid(alpha=.22,linestyle='--')
        ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)

        plt.tight_layout(); st.pyplot(fig); plt.close()

# ─── TAB 2 — Système Multi-PAT ───────────────────────────────────────────────
with T2:
    st.markdown('<div class="sh">Architecture Multi-PAT — Bilan de Pression</div>',
                unsafe_allow_html=True)

    # Bilan de pression
    c1p,c2p,c3p,c4p = st.columns(4)
    for col,(v,u,l,c) in zip([c1p,c2p,c3p,c4p],[
        (f"{dP_total:.1f}",  "bar","ΔP total réseau","kpi"),
        (f"{dP_disque:.1f}", "bar","ΔP disque orifice","kpi kpi-r"),
        (f"{dP_utile:.1f}",  "bar","ΔP utile PATs","kpi kpi-g"),
        (f"{N_pat}",          "PATs","Nombre en série","kpi kpi-o"),
    ]):
        col.markdown(f'<div class="{c}"><div class="kl">{l}</div>'
                     f'<div class="kv">{v}</div><div class="ku">{u}</div></div>',
                     unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)

    # Schéma réseau
    fig_r,ax_r=plt.subplots(figsize=(13,5.5))
    ax_r.set_xlim(0,13); ax_r.set_ylim(0,6); ax_r.axis('off')
    ax_r.set_facecolor('#0d1b2a'); fig_r.patch.set_facecolor('#0d1b2a')

    ax_r.text(6.5,5.55,f'Architecture réseau — {N_pat} PAT(s) en série | Jorf Lasfar OCP',
              ha='center',fontsize=12,fontweight='bold',color='white')

    def rbox(x,y,w,h,fc,ec,lw=2.0):
        p=FancyBboxPatch((x-w/2,y-h/2),w,h,
          boxstyle="round,pad=0.07",fc=fc,ec=ec,lw=lw,zorder=4)
        ax_r.add_patch(p)
    def arr(x1,y1,x2,y2,c='white',lw=2.2,label=''):
        ax_r.annotate('',xy=(x2,y2),xytext=(x1,y1),
                      arrowprops=dict(arrowstyle='->',color=c,lw=lw))
        if label:
            mx=(x1+x2)/2; my=(y1+y2)/2+0.2
            ax_r.text(mx,my,label,ha='center',fontsize=8,color=c,fontweight='bold')

    # Conduite entrée
    arr(0.1,3.0,0.9,3.0,'#2E75B6',3,f'Q={Q_reseau:.0f}m³/h')
    rbox(0.65,3.0,0.85,0.6,'#0d2550','#2E75B6')
    ax_r.text(0.65,3.0,'PULPE\nHaute P.',ha='center',va='center',
              fontsize=7,fontweight='bold',color='#64B5F6',zorder=6)
    ax_r.text(0.65,2.45,f'{dP_total:.0f}bar',ha='center',fontsize=7.5,color='#6ca8d4')

    # Disque de dissipation
    arr(1.1,3.0,1.85,3.0,'#C00000',2.5)
    rbox(2.1,3.0,0.55,0.8,'#2a0d0d','#EF5350',2.5)
    ax_r.text(2.1,3.05,'⊛',ha='center',va='center',fontsize=18,color='#EF5350',zorder=6)
    ax_r.text(2.1,2.45,f'Disque\n-{dP_disque:.0f}bar',ha='center',fontsize=7.5,
              color='#EF5350',fontweight='bold')
    ax_r.text(2.1,1.85,f'Dissipé:\n{dP_disque*1e5/(rho*g):.1f}m',
              ha='center',fontsize=7,color='#ff9999',style='italic')

    arr(2.4,3.0,2.9,3.0,'#FFA726',2,f'{dP_utile:.0f}bar')

    # PATs en série
    n_show = min(N_pat, 5)
    spacing = min(1.2, 5.5/max(n_show,1))
    x_start = 3.1
    for ni in range(n_show):
        xp = x_start + ni*spacing; yp = 3.0
        c_p=Circle((xp,yp),0.32,fc='#1F3864',ec='#4FC3F7',lw=2,zorder=5)
        ax_r.add_patch(c_p)
        for ang in range(0,360,72):
            th=np.radians(ang)
            ax_r.plot([xp+0.14*np.cos(th),xp+0.29*np.cos(th+np.radians(22))],
                      [yp+0.14*np.sin(th),yp+0.29*np.sin(th+np.radians(22))],
                      '-',color='#4FC3F7',lw=1.5,zorder=6)
        ax_r.text(xp,yp,'⚙',ha='center',va='center',fontsize=9,color='white',zorder=7)
        ax_r.text(xp,yp-0.55,f'PAT {ni+1}',ha='center',fontsize=7,color='#4FC3F7',fontweight='bold')
        ax_r.text(xp,yp-0.82,f'-{H_par_pat:.1f}m',ha='center',fontsize=6.5,color='#90CAF9')
        if ni<n_show-1:
            arr(xp+0.34,yp,xp+spacing-0.34,yp,'#4FC3F7',1.8)

    if N_pat > 5:
        ax_r.text(x_start+5*spacing,3.0,'...',ha='left',va='center',
                  fontsize=16,color='#4FC3F7',fontweight='bold')

    x_after = x_start+(n_show-1)*spacing+0.38
    arr(x_after,3.0,x_after+0.4,3.0,'#4FC3F7',2)
    xG=x_after+0.7
    rbox(xG,3.0,0.7,0.95,'#0d2a14','#66BB6A',2)
    ax_r.text(xG,3.0,'G',ha='center',va='center',fontsize=14,fontweight='bold',color='white',zorder=6)
    ax_r.text(xG,2.4,f'{P_total:.0f}kW',ha='center',fontsize=8,color='#A5D6A7',fontweight='bold')
    arr(xG+0.37,3.0,xG+0.65,3.0,'#66BB6A',2)
    xR=xG+0.95
    rbox(xR,3.0,0.65,0.9,'#0a1f0a','#69F0AE',2)
    ax_r.plot([xR,xR],[2.58,3.48],'-',color='#69F0AE',lw=2.5,zorder=6)
    ax_r.plot([xR-.28,xR+.28],[3.25,3.25],'-',color='#69F0AE',lw=2,zorder=6)
    ax_r.plot([xR-.2,xR+.2],[3.0,3.0],'--',color='#69F0AE',lw=1.5,zorder=6)
    ax_r.text(xR,2.32,'Réseau',ha='center',fontsize=7.5,color='#69F0AE',fontweight='bold')
    ax_r.text(xR,2.08,f'{E_an:.0f}MWh/an',ha='center',fontsize=7,color='#B9F6CA')

    # Bilan de pression (barres)
    bpdata = [
        (f'Disque ({dP_disque:.0f}bar)', dP_disque, '#C00000'),
        (f'PATs {N_pat}× ({dP_utile:.0f}bar)', dP_utile, '#2E7D32'),
    ]
    ax_r.text(0.2,1.55,'Bilan ΔP :',fontsize=8.5,fontweight='bold',color='white')
    x0b=0.2
    for lbl,val,c in bpdata:
        w=val/dP_total*5.5
        ax_r.barh(1.12,w,left=x0b,height=0.32,color=c,alpha=.9)
        ax_r.text(x0b+w/2,1.12,f'{val:.0f}bar',ha='center',va='center',
                  fontsize=8,color='white',fontweight='bold')
        x0b+=w
    ax_r.text(0.2,0.72,'Bilan P :',fontsize=8.5,fontweight='bold',color='white')
    p_items = [('P_disque',P_disque-P_total,'#C00000'),('P_récup',P_total,'#2E7D32')]
    x0p=0.2
    for lbl,val,c in p_items:
        w=max(val,0)/P_disque*5.5
        ax_r.barh(0.38,w,left=x0p,height=0.28,color=c,alpha=.88)
        ax_r.text(x0p+w/2,0.38,f'{val:.0f}kW',ha='center',va='center',
                  fontsize=7.5,color='white',fontweight='bold')
        x0p+=w

    plt.tight_layout(); st.pyplot(fig_r); plt.close()

    # Tableau comparatif 1→6 PATs
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
        configs.append({
            "N PATs":n,"S par PAT":f"{Sr:.3f}","D₂ (mm)":f"{D2n:.0f}",
            "N (tr/min)":f"{Nn:.0f}","H/PAT (m)":f"{He:.1f}",
            "P totale (kW)":f"{Pn:.1f}","Durée vie (ans)":f"{dvn:.1f}",
            "Ép. résid.":f"{ern:.2f}mm",
            "Conseil":"✅ Optimal" if 0.7<Sr<1.6 else("⚠️ Érosion" if Sr<2.2 else"❌ Éviter")
        })
    df_conf=pd.DataFrame(configs)
    def hi(row):
        return ['background-color:#e8f5e9']*len(row) if int(row["N PATs"])==N_pat else ['']*len(row)
    st.dataframe(df_conf.style.apply(hi,axis=1),use_container_width=True,hide_index=True)

# ─── TAB 3 — Maintenance & Usure ─────────────────────────────────────────────
with T3:
    st.markdown('<div class="sh">Maintenance & Durée de Vie — Validation Weir 1800h</div>',
                unsafe_allow_html=True)

    # Alertes
    if not weir_ok:
        st.markdown(f'<div class="ad">🚨 <b>CYCLE WEIR NON RESPECTÉ</b> — '
                    f'Durée vie calculée <b>{duree_h:,.0f} h</b> &lt; seuil Weir <b>{WEIR_INSP_H} h</b> — '
                    f'Planifier inspection à {WEIR_INSP_H} h d\'exploitation.</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="aok">✅ <b>Cycle Weir respecté</b> — Durée vie '
                    f'<b>{duree_h:,.0f} h</b> ≥ {WEIR_INSP_H} h — '
                    f'Prochaine inspection : {WEIR_INSP_H} h</div>',
                    unsafe_allow_html=True)

    if alerte=="DANGER":
        st.markdown(f'<div class="ad">🚨 <b>USURE CRITIQUE — {mat_sel.split("(")[0]}</b> : '
                    f'Ép. résiduelle <b>{ep_res:.2f} mm</b> ≤ seuil {EP_MIN} mm — '
                    f'Remplacement avant <b>{duree_an*365:.0f} jours ({duree_an:.2f} ans)</b></div>',
                    unsafe_allow_html=True)
    elif alerte=="WARNING":
        st.markdown(f'<div class="aw">⚠️ Ép. résiduelle <b>{ep_res:.2f} mm</b> — '
                    f'Inspection recommandée</div>',unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="aok">✅ Ép. résiduelle <b>{ep_res:.2f} mm</b> — '
                    f'Durée vie : <b>{duree_an:.1f} ans</b></div>',unsafe_allow_html=True)

    cM1,cM2 = st.columns(2)

    with cM1:
        st.markdown("#### Multi-matériaux")
        rows=[]
        for nm,p in MATS.items():
            Em=E0*p["f"]*K_local*(S_real**2.5); Evm=Em/p["rho_m"]
            dvn=(ep_m/Evm)/(3600*24*365) if Evm>0 else 999
            dvh=(ep_m/Evm)/3600 if Evm>0 else 999
            ern=max(ep_sac-Evm*H_AN*3600*1000,0)
            weir_chk = "✅" if dvh>=WEIR_INSP_H else "🚨"
            rows.append({"Matériau":nm.split('(')[0].strip(),
                         "E (kg/m²s)":f"{Em:.2e}",
                         "Durée (ans)":f"{dvn:.1f}",
                         "Durée (h)":f"{dvh:,.0f}",
                         "Ép. résid.":f"{ern:.2f}mm",
                         "Weir 1800h":weir_chk,
                         "État":"🚨" if ern<=EP_MIN else("⚠️" if ern<=EP_MIN*1.8 else"✅")})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

        # Formule érosion — utilisée en calcul, non affichée

    with cM2:
        # Épaisseur résiduelle dans le temps
        t_max=max(duree_an*1.3,3)
        t_r=np.linspace(0,t_max,400)
        fig_t,ax_t=plt.subplots(figsize=(6.5,4))
        for nm,p in MATS.items():
            Em=E0*p["f"]*K_local*(S_real**2.5); Evm=Em/p["rho_m"]
            ep_t=np.maximum(ep_sac-Evm*t_r*365*24*3600*1000,0)
            ax_t.plot(t_r,ep_t,'-',color=p["c"],lw=2.2,label=nm.split('(')[0].strip()[:16])
        ax_t.axhline(EP_MIN,color=C2,linestyle='--',lw=1.8,label=f'Seuil {EP_MIN}mm')
        ax_t.fill_between(t_r,0,EP_MIN,color='red',alpha=.08)
        # Ligne Weir 1800h
        t_weir_an = WEIR_INSP_H/(365*24)
        ax_t.axvline(t_weir_an,color='orange',linestyle=':',lw=1.8,
                     label=f'Weir {WEIR_INSP_H}h = {t_weir_an*12:.0f}mois')
        ax_t.set_xlabel("Temps (années)",fontsize=10,fontweight='bold')
        ax_t.set_ylabel("Épaisseur résiduelle (mm)",fontsize=10,fontweight='bold')
        ax_t.set_title(f"Usure paroi — S={S_real:.3f} | K={K_local}",
                       fontsize=10,fontweight='bold',color=C1)
        ax_t.set_ylim(0,ep_sac*1.12)
        ax_t.legend(fontsize=8.5); ax_t.grid(alpha=.22,linestyle='--')
        ax_t.spines['top'].set_visible(False); ax_t.spines['right'].set_visible(False)
        plt.tight_layout(); st.pyplot(fig_t); plt.close()

        # Durée de vie vs S
        S_range=np.linspace(0.5,2.0,200)
        dv_S=[]
        for sv in S_range:
            Em=E0*mat["f"]*K_local*(sv**2.5); Evm=Em/mat["rho_m"]
            dv_S.append((ep_m/Evm)/3600 if Evm>0 else 1e6)
        fig_s,ax_s=plt.subplots(figsize=(6.5,3.8))
        ax_s.plot(S_range,np.array(dv_S)/1000,'-',color=mat["c"],lw=2.5)
        ax_s.axvline(S_real,color=C2,ls='--',lw=2,label=f'S={S_real:.3f}')
        ax_s.axhline(WEIR_INSP_H/1000,color='orange',ls=':',lw=2,
                     label=f'Seuil Weir {WEIR_INSP_H}h')
        ax_s.set_xlabel("Facteur S",fontsize=10,fontweight='bold')
        ax_s.set_ylabel("Durée de vie (×1000 h)",fontsize=10,fontweight='bold')
        ax_s.set_title(f"Durée vie vs S — {mat_sel.split('(')[0]}",
                       fontsize=10,fontweight='bold',color=C1)
        ax_s.legend(fontsize=9); ax_s.grid(alpha=.22,linestyle='--')
        ax_s.spines['top'].set_visible(False); ax_s.spines['right'].set_visible(False)
        plt.tight_layout(); st.pyplot(fig_s); plt.close()

# ─── TAB 4 — Bilan Éco & CO₂ ─────────────────────────────────────────────────
with T4:
    st.markdown('<div class="sh">Bilan Économique & Impact Environnemental — Avant vs Après PAT</div>',
                unsafe_allow_html=True)

    c_av,c_mid,c_ap = st.columns(3)
    with c_av:
        st.markdown(f"""
        <div class="loss-box">
            <div style="font-size:1rem;font-weight:700;margin-bottom:8px;">
                🔴 AVANT — Vanne + Disque de dissipation
            </div>
            <div style="font-size:1.9rem;font-weight:700;">{P_disque:.1f} kW</div>
            <div style="opacity:.8;font-size:.83rem;">Puissance totale dissipée</div>
            <hr style="border-color:rgba(255,255,255,.2);margin:8px 0;">
            <div style="font-size:1.1rem;font-weight:600;">{E_perdue:.1f} MWh/an perdus</div>
            <div style="font-size:1rem;color:#ffb3b3;margin-top:5px;">
                {E_perdue*1000*tarif/1e6:.3f} M MAD perdus/an
            </div>
            <div style="margin-top:5px;color:#ffb3b3;font-size:.88rem;">
                🌍 {E_perdue*0.72:.1f} t CO₂ non valorisées
            </div>
        </div>""", unsafe_allow_html=True)

    with c_mid:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a1a2a,#1F3864);
             border-radius:12px;padding:16px;text-align:center;color:white;margin:10px 0;
             border:2px solid #4FC3F7;">
            <div style="font-size:1.3rem;font-weight:700;margin-bottom:8px;">⚡ INSTALLATION PAT</div>
            <div style="font-size:1rem;margin:6px 0;">
                {N_pat} PAT(s) × D₂={D2_real:.0f}mm
            </div>
            <div style="font-size:.9rem;opacity:.8;">S = {S_real:.3f}</div>
            <div style="font-size:.9rem;opacity:.8;">N = {N_real:.0f} tr/min</div>
            <div style="font-size:.9rem;opacity:.8;">ΔP disque = {dP_disque:.0f}bar conservé</div>
            <div style="margin-top:8px;font-size:.95rem;">η_global = {eta_g*100:.1f}%</div>
            <div style="font-size:.85rem;opacity:.7;margin-top:4px;">
                Matériau : {mat_sel.split("(")[0].strip()}
            </div>
        </div>""", unsafe_allow_html=True)

    with c_ap:
        st.markdown(f"""
        <div class="gain-box">
            <div style="font-size:1rem;font-weight:700;margin-bottom:8px;">
                🟢 APRÈS — Récupération PAT
            </div>
            <div style="font-size:1.9rem;font-weight:700;">{P_total:.1f} kW</div>
            <div style="opacity:.8;font-size:.83rem;">Puissance récupérée ({N_pat} PATs)</div>
            <hr style="border-color:rgba(255,255,255,.2);margin:8px 0;">
            <div style="font-size:1.1rem;font-weight:600;">{E_an:.1f} MWh/an récupérés</div>
            <div style="font-size:1rem;color:#b3ffb3;margin-top:5px;">
                {gain/1e6:.3f} M MAD gagnés/an
            </div>
            <div style="margin-top:5px;color:#b3ffb3;font-size:.88rem;">
                🌍 {CO2:.1f} t CO₂ évitées/an
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    # Graphiques comparatifs
    fig_eco,axes_eco=plt.subplots(1,3,figsize=(13,4.5))

    for ax_e,vals,labels,title,colors in [
        (axes_eco[0],
         [P_disque, P_total, P_disque-P_total],
         ['Dissipée\n(avant)','Récupérée\n(PAT)','Pertes\nnettes'],
         'Puissance (kW)',
         [C2,C3,'#888888']),
        (axes_eco[1],
         [E_perdue, E_an],
         ['Énergie perdue\n(avant)','Énergie récupérée\n(PAT)'],
         'Énergie (MWh/an)',
         [C2,C3]),
        (axes_eco[2],
         [E_perdue*0.72, CO2],
         ['CO₂ non\nvalorisé','CO₂\névité (PAT)'],
         'CO₂ (t/an)',
         ['#8B4513',C3]),
    ]:
        bars=ax_e.bar(labels,vals,color=colors,width=0.5,edgecolor='white',lw=1.8)
        for b,v in zip(bars,vals):
            ax_e.text(b.get_x()+b.get_width()/2,b.get_height()+max(vals)*0.02,
                      f'{v:.0f}',ha='center',fontsize=11,fontweight='bold')
        ax_e.set_title(title,fontsize=11,fontweight='bold',color=C1)
        ax_e.grid(axis='y',alpha=.22,linestyle='--')
        ax_e.spines['top'].set_visible(False); ax_e.spines['right'].set_visible(False)
        ax_e.tick_params(labelsize=9)

    fig_eco.suptitle(f'Bilan Avant/Après PAT | Q={Q_reseau:.0f}m³/h | '
                     f'ΔP={dP_total:.0f}bar | {N_pat}×PAT D₂={D2_real:.0f}mm',
                     fontsize=11,fontweight='bold',color=C1)
    plt.tight_layout(); st.pyplot(fig_eco); plt.close()

    # Métriques finales
    st.markdown("---")
    c1f,c2f,c3f,c4f,c5f = st.columns(5)
    arbres = int(CO2*1000/25)
    for col,(v,u,l,c) in zip([c1f,c2f,c3f,c4f,c5f],[
        (f"{gain/1e6:.3f}",       "M MAD/an", "Gain annuel",     "kpi kpi-g"),
        (f"{CO2:.1f}",            "t CO₂/an", "CO₂ évité",       "kpi kpi-p"),
        (f"{E_an:.0f}",           "MWh/an",   "Énergie récup.",  "kpi kpi-g"),
        (f"{P_total/P_disque*100:.0f}","%",   "Taux récupération","kpi kpi-o"),
        (f"≈{arbres:,}",          "arbres/an","Équiv. arbres",    "kpi"),
    ]):
        col.markdown(f'<div class="{c}"><div class="kl">{l}</div>'
                     f'<div class="kv">{v}</div><div class="ku">{u}</div></div>',
                     unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""<div style='text-align:center;color:#bbb;font-size:.78rem;'>
PFE 2025–2026 — École Mohammadia d'Ingénieurs | Weir Minerals North Africa|
ANSYS CFX SST k-ω | Warman 10/8 M  | AITELHOUSSEINE/MAHMANI 
</div>""", unsafe_allow_html=True)

