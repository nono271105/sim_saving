"""
╔══════════════════════════════════════════════════════════════════╗
║         COMPARATEUR DE PLACEMENTS — FRANCE                       ║
║         Rendements Bruts & Nets · Fiscalité 2026                 ║
╚══════════════════════════════════════════════════════════════════╝

Lancer avec : streamlit run comparateur_placements.py
Dépendances  : pip install streamlit plotly pandas numpy
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional
import math
import html as html_lib   # pour html.escape() dans les fiches produits

# ─────────────────────────────────────────────
# CONFIG PAGE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Comparateur de Placements · France",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS — STYLE GOLDMAN SACHS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --bg-0:       #08090C;
    --bg-1:       #0E1017;
    --bg-2:       #131620;
    --bg-3:       #191D2B;
    --bg-4:       #1F2436;
    --gold-light: #D4AF6A;
    --gold:       #B8922A;
    --gold-dim:   rgba(196,164,88,0.18);
    --gold-line:  rgba(196,164,88,0.28);
    --white:      #F2EEE7;
    --grey-1:     #B8BCC8;
    --grey-2:     #7A8094;
    --grey-3:     #454A5A;
    --grey-4:     #2A2E3D;
    --positive:   #6BAF72;
    --negative:   #C0584E;
    --blue:       #5B8DB8;
    --border:     rgba(255,255,255,0.055);
}

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; color: var(--grey-1); }
.stApp { background: var(--bg-0); }
::-webkit-scrollbar { width: 5px; background: var(--bg-1); }
::-webkit-scrollbar-thumb { background: var(--grey-4); border-radius: 3px; }

/* Header */
.gs-header {
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid var(--gold-line);
    padding: 1.6rem 0 1.2rem; margin-bottom: 1.6rem;
}
.gs-wordmark { font-family:'IBM Plex Sans',sans-serif; font-weight:600; font-size:0.7rem; letter-spacing:3px; text-transform:uppercase; color:var(--gold-light); }
.gs-title { font-family:'Playfair Display',serif; font-size:1.9rem; font-weight:700; color:var(--white); margin:0.15rem 0 0.1rem; letter-spacing:-0.3px; }
.gs-subtitle { font-size:0.72rem; color:var(--grey-2); letter-spacing:2px; text-transform:uppercase; font-weight:400; }
.gs-badge-date { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:var(--grey-2); border:1px solid var(--grey-4); padding:4px 10px; border-radius:3px; letter-spacing:1px; }

/* KPI row */
.gs-kpi-row { display:grid; grid-template-columns:repeat(5,1fr); gap:1px; margin-bottom:1.6rem; }
.gs-kpi { background:var(--bg-2); padding:1.2rem 1.4rem; border-top:2px solid var(--gold); }
.gs-kpi-val { font-family:'IBM Plex Mono',monospace; font-size:1.5rem; font-weight:500; color:var(--white); line-height:1.1; }
.gs-kpi-lbl { font-size:0.65rem; color:var(--grey-2); text-transform:uppercase; letter-spacing:1.2px; margin-top:0.35rem; font-weight:500; }

/* Banners */
.gs-banner { background:rgba(196,164,88,0.06); border-left:2px solid var(--gold); padding:0.65rem 1rem; margin:0.6rem 0 1rem; font-size:0.78rem; color:var(--grey-1); line-height:1.6; }
.gs-warning { background:rgba(192,88,78,0.07); border-left:2px solid var(--negative); padding:0.65rem 1rem; margin:0.4rem 0; font-size:0.78rem; color:var(--grey-1); }

/* Section */
.gs-section { font-family:'Playfair Display',serif; font-size:1.05rem; color:var(--white); padding-bottom:0.4rem; margin-bottom:0.8rem; border-bottom:1px solid var(--grey-4); }
.gs-section-line { display:inline-block; width:24px; height:2px; background:var(--gold); margin-right:8px; vertical-align:middle; }

/* Cards Fiches */
.gs-card { background:var(--bg-2); border:1px solid var(--border); border-top:1px solid var(--gold-line); padding:1.2rem 1.4rem; margin-bottom:10px; }
.gs-card-head { display:flex; align-items:center; gap:10px; margin-bottom:0.8rem; flex-wrap:wrap; }
.gs-card-name { font-family:'Playfair Display',serif; font-size:1.05rem; color:var(--white); font-weight:600; }
.gs-pill { display:inline-block; font-size:0.6rem; font-weight:600; letter-spacing:0.8px; text-transform:uppercase; padding:2px 7px; border-radius:2px; }
.pill-green  { background:rgba(107,175,114,0.14); color:#6BAF72; border:1px solid rgba(107,175,114,0.3); }
.pill-gold   { background:rgba(196,164,88,0.12); color:var(--gold-light); border:1px solid var(--gold-line); }
.pill-orange { background:rgba(192,138,60,0.13); color:#C8844A; border:1px solid rgba(192,138,60,0.3); }
.pill-red    { background:rgba(192,88,78,0.12); color:#C0584E; border:1px solid rgba(192,88,78,0.3); }
.gs-card-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:0.8rem; margin-bottom:0.8rem; padding:0.8rem 0; border-top:1px solid var(--grey-4); border-bottom:1px solid var(--grey-4); }
.gs-card-stat-lbl { font-size:0.6rem; color:var(--grey-2); text-transform:uppercase; letter-spacing:1px; font-weight:600; }
.gs-card-stat-val { font-family:'IBM Plex Mono',monospace; font-size:1rem; color:var(--white); margin-top:2px; }
.gs-card-stat-val.gold { color:var(--gold-light); }
.gs-card-note { font-size:0.77rem; color:var(--grey-2); line-height:1.65; padding:0.5rem 0.7rem; border-left:2px solid var(--gold-dim); }

/* Sidebar */
[data-testid="stSidebar"] { background:var(--bg-1); border-right:1px solid var(--border); }
[data-testid="stSidebar"] .stMarkdown h5 { color:var(--grey-2); font-size:0.65rem; text-transform:uppercase; letter-spacing:2px; font-family:'IBM Plex Sans',sans-serif; border-bottom:1px solid var(--grey-4); padding-bottom:4px; margin-bottom:8px; }

/* Tabs */
[data-baseweb="tab-list"] { border-bottom:1px solid var(--grey-4) !important; gap:0 !important; }
[data-baseweb="tab"] { font-size:0.72rem !important; font-weight:500 !important; letter-spacing:1px !important; text-transform:uppercase !important; color:var(--grey-2) !important; padding:8px 16px !important; border-radius:0 !important; }
[aria-selected="true"] { color:var(--gold-light) !important; border-bottom:2px solid var(--gold) !important; background:transparent !important; }

/* Download */
.stDownloadButton button { background:transparent !important; border:1px solid var(--gold-line) !important; color:var(--gold-light) !important; font-size:0.72rem !important; letter-spacing:1px !important; text-transform:uppercase !important; border-radius:2px !important; padding:6px 16px !important; }
.stDownloadButton button:hover { background:var(--gold-dim) !important; }

/* Footer */
.gs-footer { text-align:center; padding:2rem 0 1rem; color:var(--grey-3); font-size:0.68rem; border-top:1px solid var(--grey-4); margin-top:2.5rem; letter-spacing:0.5px; line-height:1.8; }

/* ── Recommendation module ── */
.rec-hero {
    background: linear-gradient(135deg, #0E1017 0%, #131620 60%, #1a1608 100%);
    border: 1px solid var(--gold-line);
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative; overflow: hidden;
}
.rec-hero::after {
    content: '';
    position: absolute; top: -80px; right: -80px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(196,164,88,0.07) 0%, transparent 70%);
    pointer-events: none;
}
.rec-hero-label { font-size:0.62rem; color:var(--gold); letter-spacing:3px; text-transform:uppercase; font-weight:600; margin-bottom:0.4rem; }
.rec-hero-title { font-family:'Playfair Display',serif; font-size:1.5rem; color:var(--white); margin-bottom:0.3rem; }
.rec-hero-sub { font-size:0.78rem; color:var(--grey-2); line-height:1.6; }

/* Score bars */
.score-row { display:flex; align-items:center; gap:10px; margin-bottom:8px; }
.score-label { font-size:0.68rem; color:var(--grey-2); text-transform:uppercase; letter-spacing:0.8px; width:120px; flex-shrink:0; }
.score-bar-bg { flex:1; height:5px; background:var(--grey-4); border-radius:2px; }
.score-bar-fill { height:5px; border-radius:2px; background:var(--gold); transition:width 0.4s; }
.score-val { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:var(--gold-light); width:32px; text-align:right; }

/* Podium cards */
.podium-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:1.5rem; }
.podium-card {
    background:var(--bg-2); border:1px solid var(--border);
    padding:1.2rem 1.4rem; position:relative; overflow:hidden;
}
.podium-card.rank-1 { border-top:2px solid var(--gold); }
.podium-card.rank-2 { border-top:2px solid #7A8094; }
.podium-card.rank-3 { border-top:2px solid #8B6914; }
.podium-rank { font-family:'IBM Plex Mono',monospace; font-size:2rem; font-weight:500; opacity:0.12; position:absolute; top:8px; right:12px; color:var(--white); }
.podium-nom { font-family:'Playfair Display',serif; font-size:0.95rem; color:var(--white); margin-bottom:0.3rem; }
.podium-score { font-family:'IBM Plex Mono',monospace; font-size:1.4rem; color:var(--gold-light); font-weight:500; }
.podium-score-lbl { font-size:0.6rem; color:var(--grey-2); text-transform:uppercase; letter-spacing:1px; }
.podium-reason { font-size:0.73rem; color:var(--grey-2); margin-top:0.6rem; line-height:1.55; border-top:1px solid var(--grey-4); padding-top:0.6rem; }

/* Contrainte tag */
.tag-ok      { display:inline-block; font-size:0.58rem; font-weight:700; padding:1px 6px; border-radius:2px; letter-spacing:0.5px; background:rgba(107,175,114,0.12); color:#6BAF72; border:1px solid rgba(107,175,114,0.25); margin:2px; }
.tag-warning { display:inline-block; font-size:0.58rem; font-weight:700; padding:1px 6px; border-radius:2px; letter-spacing:0.5px; background:rgba(192,138,60,0.12); color:#C8844A; border:1px solid rgba(192,138,60,0.25); margin:2px; }
.tag-ko      { display:inline-block; font-size:0.58rem; font-weight:700; padding:1px 6px; border-radius:2px; letter-spacing:0.5px; background:rgba(192,88,78,0.12); color:#C0584E; border:1px solid rgba(192,88,78,0.25); margin:2px; }

/* Narrative box */
.narrative {
    background: var(--bg-2); border-left: 3px solid var(--gold);
    padding: 1.4rem 1.8rem; line-height: 1.9;
    font-size: 0.84rem; color: var(--grey-1);
}
.narrative b { color: var(--gold-light); font-weight: 600; }
.narrative h4 { font-family:'Playfair Display',serif; color:var(--white); font-size:1rem; margin:1rem 0 0.4rem; }

/* Questionnaire */
.q-block { background:var(--bg-2); border:1px solid var(--border); border-left:2px solid var(--gold); padding:1.2rem 1.4rem; margin-bottom:1rem; }
.q-title { font-size:0.65rem; color:var(--gold); letter-spacing:2px; text-transform:uppercase; font-weight:600; margin-bottom:0.6rem; }

/* Allocation bar */
.alloc-row { display:flex; align-items:center; gap:12px; margin-bottom:10px; }
.alloc-name { font-size:0.75rem; color:var(--grey-1); width:180px; flex-shrink:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.alloc-bar-bg { flex:1; height:8px; background:var(--grey-4); border-radius:2px; }
.alloc-bar-fill { height:8px; border-radius:2px; }
.alloc-pct { font-family:'IBM Plex Mono',monospace; font-size:0.7rem; color:var(--grey-2); width:38px; text-align:right; }

/* Full-width score table */
.score-table { width:100%; border-collapse:collapse; font-size:0.76rem; }
.score-table th { font-size:0.58rem; color:var(--grey-2); text-transform:uppercase; letter-spacing:1px; font-weight:600; padding:6px 10px; border-bottom:1px solid var(--grey-4); text-align:left; }
.score-table td { padding:8px 10px; border-bottom:1px solid rgba(255,255,255,0.03); color:var(--grey-1); }
.score-table tr:hover td { background:rgba(255,255,255,0.02); }
.score-num { font-family:'IBM Plex Mono',monospace; color:var(--gold-light); }
.score-rank-badge { display:inline-block; width:20px; height:20px; line-height:20px; text-align:center; font-size:0.65rem; font-weight:700; border-radius:2px; background:var(--grey-4); color:var(--grey-2); }
.score-rank-badge.r1 { background:rgba(196,164,88,0.2); color:var(--gold-light); }
.score-rank-badge.r2 { background:rgba(120,120,120,0.2); color:#aaa; }
.score-rank-badge.r3 { background:rgba(139,105,20,0.15); color:#a07830; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FISCALITE FRANCE 2026
# ─────────────────────────────────────────────

TAUX_PS     = 0.172
TAUX_IR_PFU = 0.128
TAUX_PFU    = 0.30

TRANCHES_IR = [
    (11_497,       0.00),
    (29_315,       0.11),
    (83_823,       0.30),
    (180_294,      0.41),
    (float('inf'), 0.45),
]

def taux_marginal_ir(revenu_fiscal: float) -> float:
    tmi, prec = 0.0, 0
    for plafond, taux in TRANCHES_IR:
        if revenu_fiscal <= prec:
            break
        tmi = taux
        prec = plafond
    return tmi


# ─────────────────────────────────────────────
# DATACLASS PRODUIT
# ─────────────────────────────────────────────

@dataclass
class Produit:
    nom: str
    code: str
    categorie: str
    taux_rendement_brut: float
    taux_rendement_min: float = 0.0
    taux_rendement_max: float = 0.0
    plafond_depot: float = float('inf')
    plafond_versement: float = float('inf')
    duree_min_ans: int = 0
    exonere_ir: bool = False
    exonere_ps: bool = False
    pfu_apres_ans: Optional[int] = None
    abattement_8ans: float = 4_600
    soumis_ir_foncier: bool = False
    reglement_special: str = ""
    emoji: str = "o"
    risque: str = "Faible"
    liquidite: str = "Haute"
    garantie_capital: bool = True


# ─────────────────────────────────────────────
# CATALOGUE — TAUX 2026
# ─────────────────────────────────────────────

PRODUITS: dict[str, "Produit"] = {

    "livret_a": Produit(
        nom="Livret A", code="livret_a", categorie="Livrets reglements",
        taux_rendement_brut=0.015,
        plafond_depot=22_950,
        exonere_ir=True, exonere_ps=True,
        risque="Nul", liquidite="Haute", garantie_capital=True,
        reglement_special=(
            "Taux reglemente fixe a 2,4% depuis le 1er fevrier 2025. "
            "Totalement exonere d'IR et de prelevements sociaux. "
            "Plafond de depot 22 950 EUR. Interets calcules par quinzaine."
        ),
    ),
    "ldds": Produit(
        nom="LDDS", code="ldds", categorie="Livrets reglements",
        taux_rendement_brut=0.02,
        plafond_depot=12_000,
        exonere_ir=True, exonere_ps=True,
        risque="Nul", liquidite="Haute", garantie_capital=True,
        reglement_special=(
            "Livret de Developpement Durable et Solidaire. "
            "Taux identique au Livret A : 2,4% depuis fevrier 2025. "
            "Exonere d'impots et de PS. Plafond 12 000 EUR."
        ),
    ),
    "lep": Produit(
        nom="LEP", code="lep", categorie="Livrets reglements",
        taux_rendement_brut=0.025,
        plafond_depot=10_000,
        exonere_ir=True, exonere_ps=True,
        risque="Nul", liquidite="Haute", garantie_capital=True,
        reglement_special=(
            "Livret Epargne Populaire. Taux bonifie a 3,5% depuis fevrier 2025. "
            "Reserve aux foyers sous conditions de ressources (RFR <= 22 419 EUR pour 1 part). "
            "Exonere d'IR et de PS. Plafond 10 000 EUR."
        ),
    ),
    "livret_b": Produit(
        nom="Livret Bancaire", code="livret_b", categorie="Livrets bancaires",
        taux_rendement_brut=0.015,
        exonere_ir=False, exonere_ps=False,
        risque="Nul", liquidite="Haute", garantie_capital=True,
        reglement_special=(
            "Taux libre fixe par la banque, generalement 0,5 a 2% en 2026. "
            "Soumis au PFU 30% (12,8% IR + 17,2% PS) ou option bareme. "
            "Aucun plafond reglementaire."
        ),
    ),
    "pel": Produit(
        nom="PEL", code="pel", categorie="Epargne logement",
        taux_rendement_brut=0.0175,
        plafond_depot=61_200,
        exonere_ir=False, exonere_ps=False,
        pfu_apres_ans=0, duree_min_ans=4,
        risque="Nul", liquidite="Faible", garantie_capital=True,
        reglement_special=(
            "PEL ouvert depuis janvier 2025 : taux 1,75%. "
            "Soumis au PFU 30% (12,8% IR + 17,2% PS) des la 1re annee. "
            "Duree minimum 4 ans, maximum 10 ans. Versements minimum 540 EUR/an. "
            "Plafond 61 200 EUR."
        ),
    ),
    "cel": Produit(
        nom="CEL", code="cel", categorie="Epargne logement",
        taux_rendement_brut=0.015,
        plafond_depot=15_300,
        exonere_ir=False, exonere_ps=False,
        pfu_apres_ans=0,
        risque="Nul", liquidite="Moyenne", garantie_capital=True,
        reglement_special=(
            "Compte Epargne Logement. Taux environ 1,5% en 2026. "
            "Soumis au PFU 30%. Plafond 15 300 EUR. "
            "Ouvre droit a un pret immobilier complementaire."
        ),
    ),
    "av_euros": Produit(
        nom="Assurance Vie Fonds Euros", code="av_euros", categorie="Assurance Vie",
        taux_rendement_brut=0.038,
        exonere_ir=False, exonere_ps=False,
        abattement_8ans=4_600, pfu_apres_ans=8,
        risque="Faible", liquidite="Moyenne", garantie_capital=True,
        reglement_special=(
            "Taux moyen fonds euros 2024 : 3,6 a 4,0%. Capital garanti net de frais. "
            "Avant 8 ans : PFU 30%. "
            "Apres 8 ans : 7,5% IR + 17,2% PS avec abattement 4 600 EUR (9 200 EUR couple). "
            "Les prelevements sociaux sont preleves annuellement sur les fonds euros."
        ),
    ),
    "av_uc": Produit(
        nom="Assurance Vie UC", code="av_uc", categorie="Assurance Vie",
        taux_rendement_brut=0.065,
        taux_rendement_min=-0.20, taux_rendement_max=0.18,
        exonere_ir=False, exonere_ps=False,
        abattement_8ans=4_600, pfu_apres_ans=8,
        risque="Modere", liquidite="Moyenne", garantie_capital=False,
        reglement_special=(
            "Unites de Compte : capital non garanti, investi en actions/obligations/immobilier. "
            "Hypothese neutre : 6,5%/an (peut varier entre -20% et +18% selon marches). "
            "Meme fiscalite AV apres 8 ans. PS preleves uniquement lors du rachat."
        ),
    ),
    "pea": Produit(
        nom="PEA", code="pea", categorie="Epargne en actions",
        taux_rendement_brut=0.07,
        taux_rendement_min=-0.30, taux_rendement_max=0.25,
        plafond_depot=150_000, plafond_versement=150_000,
        exonere_ir=False, exonere_ps=False,
        pfu_apres_ans=5, duree_min_ans=5,
        risque="Eleve", liquidite="Moyenne", garantie_capital=False,
        reglement_special=(
            "Plan Epargne en Actions. Hypothese neutre : 7%/an (long terme indices europeens). "
            "Apres 5 ans : 0% IR + 17,2% PS sur les plus-values uniquement. "
            "Avant 5 ans : cloture du plan et PFU 30%. "
            "Plafond 150 000 EUR. Actions et fonds europeens uniquement."
        ),
    ),
    "pea_pme": Produit(
        nom="PEA-PME", code="pea_pme", categorie="Epargne en actions",
        taux_rendement_brut=0.065,
        taux_rendement_min=-0.40, taux_rendement_max=0.30,
        plafond_depot=225_000, plafond_versement=225_000,
        exonere_ir=False, exonere_ps=False,
        pfu_apres_ans=5,
        risque="Eleve", liquidite="Faible", garantie_capital=False,
        reglement_special=(
            "Dedie aux PME/ETI europeennes. Hypothese neutre : 6,5%/an. "
            "Meme fiscalite que le PEA apres 5 ans. "
            "Plafond 225 000 EUR cumule avec le PEA. Volatilite superieure au PEA classique."
        ),
    ),
    "cto": Produit(
        nom="Compte Titres CTO", code="cto", categorie="Epargne en actions",
        taux_rendement_brut=0.07,
        taux_rendement_min=-0.35, taux_rendement_max=0.28,
        exonere_ir=False, exonere_ps=False,
        risque="Eleve", liquidite="Haute", garantie_capital=False,
        reglement_special=(
            "Aucun plafond ni contrainte geographique. "
            "Hypothese neutre : 7%/an (rendement moyen actions monde long terme). "
            "PFU 30% sur dividendes et plus-values chaque annee. "
            "Option bareme progressif IR possible si TMI inferieur a 12,8%."
        ),
    ),
    "scpi": Produit(
        nom="SCPI", code="scpi", categorie="Immobilier papier",
        taux_rendement_brut=0.047,
        taux_rendement_min=0.025, taux_rendement_max=0.07,
        exonere_ir=False, exonere_ps=False,
        soumis_ir_foncier=True, duree_min_ans=8,
        risque="Modere", liquidite="Faible", garantie_capital=False,
        reglement_special=(
            "SCPI : TDVM moyen 4,7% en 2024. "
            "Revenus fonciers soumis au bareme IR + 17,2% PS. "
            "Frais de souscription entre 8 et 10%. Horizon recommande : 8 a 10 ans. "
            "Capital non garanti, possible erosion de la valeur de part."
        ),
    ),
    "obligations": Produit(
        nom="OAT 10 ans", code="obligations", categorie="Obligataire",
        taux_rendement_brut=0.034,
        taux_rendement_min=0.02, taux_rendement_max=0.05,
        exonere_ir=False, exonere_ps=False,
        risque="Faible", liquidite="Haute", garantie_capital=True,
        reglement_special=(
            "Obligations Assimilables du Tresor 10 ans. Rendement environ 3,4% debut 2026. "
            "PFU 30% sur les coupons et les plus-values. "
            "Garantie de l'Etat francais. Sensible aux variations de taux."
        ),
    ),
    "crypto": Produit(
        nom="Cryptomonnaies", code="crypto", categorie="Actifs alternatifs",
        taux_rendement_brut=0.12,
        taux_rendement_min=-0.70, taux_rendement_max=1.00,
        exonere_ir=False, exonere_ps=False,
        risque="Tres eleve", liquidite="Haute", garantie_capital=False,
        reglement_special=(
            "Hypothese neutre de long terme : 12%/an (tres incertain, volatilite extreme). "
            "PFU 30% sur les cessions nettes. Exonere si cessions annuelles inferieures a 305 EUR. "
            "Aucune protection legale ni garantie de l'Etat. Risque de perte totale."
        ),
    ),
    "fcpi_fip": Produit(
        nom="FCPI / FIP", code="fcpi_fip", categorie="Capital-investissement",
        taux_rendement_brut=0.05,
        taux_rendement_min=-0.20, taux_rendement_max=0.25,
        exonere_ir=False, exonere_ps=False,
        duree_min_ans=7,
        risque="Eleve", liquidite="Tres faible", garantie_capital=False,
        reglement_special=(
            "Reduction IR a l'entree : 18% FCPI ou 25% FIP Corse/Outre-mer. "
            "Blocage 7 a 10 ans. Plus-values exonerees d'IR, prelevements sociaux dus a la sortie. "
            "Hypothese neutre : 5%/an. Capital non garanti, risque de perte partielle ou totale."
        ),
    ),
}


# ─────────────────────────────────────────────
# MOTEUR FISCAL
# ─────────────────────────────────────────────

def calculer_fiscalite(
    produit: Produit,
    capital_final: float,
    capital_investi: float,
    plus_value: float,
    duree_ans: int,
    revenu_fiscal: float,
    couple: bool = False,
) -> dict:

    ir, ps, abattement = 0.0, 0.0, 0.0
    note = ""
    tmi  = taux_marginal_ir(revenu_fiscal)

    # Livrets exoneres
    if produit.exonere_ir and produit.exonere_ps:
        return dict(capital_brut=capital_final, plus_value_brute=plus_value,
                    abattement=0, plus_value_imposable=0, ir=0, ps=0, total_taxes=0,
                    capital_net=capital_final, plus_value_nette=plus_value,
                    note="Exonere d'IR et de prelevements sociaux", taux_effectif_global=0)

    # PEA apres 5 ans
    if produit.code in ("pea", "pea_pme") and duree_ans >= 5:
        ps = plus_value * TAUX_PS
        return dict(capital_brut=capital_final, plus_value_brute=plus_value,
                    abattement=0, plus_value_imposable=plus_value, ir=0, ps=ps,
                    total_taxes=ps, capital_net=capital_final - ps,
                    plus_value_nette=plus_value - ps,
                    note="PEA >5 ans : 0% IR + 17,2% PS sur plus-values",
                    taux_effectif_global=(ps/plus_value*100) if plus_value > 0 else 0)

    # Assurance Vie
    if produit.code in ("av_euros", "av_uc"):
        abattement_max = 9_200 if couple else 4_600
        if duree_ans >= 8:
            abattement  = min(plus_value, abattement_max)
            pv_imposable = max(0, plus_value - abattement)
            ir_forfait  = pv_imposable * 0.075
            ir_bareme   = pv_imposable * tmi
            ir = min(ir_forfait, ir_bareme)
            ps = plus_value * TAUX_PS if produit.code == "av_uc" else 0.0
            taux_ir_str = "7,5%" if ir == ir_forfait else f"{tmi*100:.0f}%"
            note = (f"AV >8 ans : {taux_ir_str} IR + 17,2% PS, abattement {abattement_max:,.0f} EUR"
                    + (" (PS annuels inclus)" if produit.code == "av_euros" else ""))
        else:
            ir   = plus_value * TAUX_IR_PFU
            ps   = plus_value * TAUX_PS
            note = "AV <8 ans : PFU 30% (12,8% IR + 17,2% PS)"
        total = ir + ps
        return dict(capital_brut=capital_final, plus_value_brute=plus_value,
                    abattement=abattement, plus_value_imposable=max(0, plus_value-abattement),
                    ir=ir, ps=ps, total_taxes=total, capital_net=capital_final-total,
                    plus_value_nette=plus_value-total, note=note,
                    taux_effectif_global=(total/plus_value*100) if plus_value > 0 else 0)

    # SCPI revenus fonciers
    if produit.soumis_ir_foncier:
        ir_base = plus_value * tmi
        csg_ded = plus_value * 0.068 * tmi
        ir  = max(0, ir_base - csg_ded)
        ps  = plus_value * TAUX_PS
        tot = ir + ps
        note = f"Revenus fonciers : TMI {tmi*100:.0f}% + 17,2% PS (CSG ded. {csg_ded:,.0f} EUR)"
        return dict(capital_brut=capital_final, plus_value_brute=plus_value,
                    abattement=0, plus_value_imposable=plus_value,
                    ir=ir, ps=ps, total_taxes=tot, capital_net=capital_final-tot,
                    plus_value_nette=plus_value-tot, note=note,
                    taux_effectif_global=(tot/plus_value*100) if plus_value > 0 else 0)

    # FCPI/FIP
    if produit.code == "fcpi_fip":
        reduction = capital_investi * 0.18
        ps  = plus_value * TAUX_PS
        tot = ps - reduction
        note = f"FCPI/FIP : reduction IR {reduction:,.0f} EUR + 17,2% PS sur PV"
        return dict(capital_brut=capital_final, plus_value_brute=plus_value,
                    abattement=reduction, plus_value_imposable=plus_value,
                    ir=-reduction, ps=ps, total_taxes=tot,
                    capital_net=capital_final-ps+reduction, plus_value_nette=plus_value-tot,
                    note=note,
                    taux_effectif_global=(tot/plus_value*100) if plus_value > 0 else 0)

    # Cas general PFU / bareme
    ir_pfu    = plus_value * TAUX_IR_PFU
    ir_bareme = plus_value * tmi
    ps        = plus_value * TAUX_PS
    if ir_bareme < ir_pfu:
        ir   = ir_bareme
        note = f"Option bareme IR {tmi*100:.0f}% + 17,2% PS (bareme plus avantageux que PFU)"
    else:
        ir   = ir_pfu
        note = "PFU 30% : 12,8% IR + 17,2% prelevements sociaux"
    tot = ir + ps
    return dict(capital_brut=capital_final, plus_value_brute=plus_value,
                abattement=0, plus_value_imposable=plus_value,
                ir=ir, ps=ps, total_taxes=tot, capital_net=capital_final-tot,
                plus_value_nette=plus_value-tot, note=note,
                taux_effectif_global=(tot/plus_value*100) if plus_value > 0 else 0)


# ─────────────────────────────────────────────
# SIMULATION
# ─────────────────────────────────────────────

def simuler(
    produit: Produit,
    capital_initial: float,
    versement_mensuel: float,
    duree_ans: int,
    revenu_fiscal: float,
    taux_personalise: Optional[float] = None,
    couple: bool = False,
    inflation: float = 0.025,
) -> dict:
    taux_annuel  = taux_personalise if taux_personalise is not None else produit.taux_rendement_brut
    taux_mensuel = (1 + taux_annuel) ** (1/12) - 1

    cap_eff       = min(capital_initial, produit.plafond_depot)
    vmax          = min(versement_mensuel,
                        max(0, produit.plafond_versement - cap_eff) / max(1, duree_ans * 12))
    capital       = cap_eff
    cap_inv_total = cap_eff
    hist_brut     = [capital]
    hist_inv      = [cap_eff]

    for mois in range(1, duree_ans * 12 + 1):
        cap_inv_total += vmax
        capital = capital * (1 + taux_mensuel) + vmax
        if capital > produit.plafond_depot:
            capital = produit.plafond_depot
        if mois % 12 == 0:
            hist_brut.append(capital)
            hist_inv.append(min(cap_inv_total, capital))

    cap_final     = capital
    cap_inv_total = min(cap_inv_total, cap_final)
    plus_value    = max(0, cap_final - cap_inv_total)

    fisc = calculer_fiscalite(
        produit=produit, capital_final=cap_final,
        capital_investi=cap_inv_total, plus_value=plus_value,
        duree_ans=duree_ans, revenu_fiscal=revenu_fiscal, couple=couple,
    )

    cap_net      = fisc["capital_net"]
    taux_net_an  = (cap_net / cap_inv_total) ** (1/duree_ans) - 1 if cap_inv_total > 0 else 0
    taux_reel    = (1 + taux_net_an) / (1 + inflation) - 1

    return dict(
        produit=produit,
        capital_investi=cap_inv_total,
        capital_final_brut=cap_final,
        capital_final_net=cap_net,
        plus_value_brute=plus_value,
        plus_value_nette=fisc["plus_value_nette"],
        total_taxes=fisc["total_taxes"],
        ir=fisc["ir"],
        ps=fisc["ps"],
        taux_effectif=fisc["taux_effectif_global"],
        taux_net_annualise=taux_net_an,
        taux_brut_annualise=taux_annuel,
        taux_reel=taux_reel,
        note_fiscale=fisc["note"],
        historique_brut=hist_brut,
        historique_investi=hist_inv,
        capital_plafonne=(cap_eff < capital_initial),
    )


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

def sidebar_params():
    st.sidebar.markdown('<div style="padding:1rem 0 0.3rem"><span style="font-size:0.6rem;color:#B8922A;letter-spacing:3px;text-transform:uppercase;font-weight:600">Investment Simulator</span></div>', unsafe_allow_html=True)
    st.sidebar.markdown("##### Capital & Versements")
    capital_initial   = st.sidebar.number_input("Capital initial (EUR)", 0, 10_000_000, 10_000, 500)
    versement_mensuel = st.sidebar.number_input("Versement mensuel (EUR)", 0, 100_000, 200, 50)
    duree_ans         = st.sidebar.slider("Duree (annees)", 1, 40, 10)

    st.sidebar.markdown("##### Situation fiscale")
    revenu_fiscal = st.sidebar.number_input("Revenu fiscal de reference (EUR)", 0, 1_000_000, 45_000, 1_000)
    couple        = st.sidebar.checkbox("Couple marie / pacse (abattements doubles)", value=False)

    st.sidebar.markdown("##### Parametres macro")
    inflation = st.sidebar.slider("Inflation annuelle (%)", 0.0, 10.0, 2.5, 0.1) / 100

    st.sidebar.markdown("##### Selection des produits")
    cats: dict = {}
    for p in PRODUITS.values():
        cats.setdefault(p.categorie, []).append(p)

    defaut = {"livret_a", "lep", "pel", "av_euros", "pea", "cto", "scpi", "obligations"}
    sel    = []
    for cat, prods in cats.items():
        with st.sidebar.expander(cat, expanded=True):
            for p in prods:
                if st.checkbox(p.nom, value=(p.code in defaut), key=f"sel_{p.code}"):
                    sel.append(p.code)

    st.sidebar.markdown("##### Taux personnalises")
    taux_custom: dict = {}
    if sel:
        with st.sidebar.expander("Modifier les hypotheses"):
            for code in sel:
                p = PRODUITS[code]
                taux_custom[code] = st.number_input(
                    f"{p.nom} (%/an)",
                    min_value=-50.0, max_value=100.0,
                    value=round(p.taux_rendement_brut * 100, 2),
                    step=0.05, key=f"taux_{code}"
                ) / 100

    return dict(capital_initial=capital_initial, versement_mensuel=versement_mensuel,
                duree_ans=duree_ans, revenu_fiscal=revenu_fiscal, couple=couple,
                inflation=inflation, produits=sel, taux_custom=taux_custom)


# ─────────────────────────────────────────────
# THEME GRAPHIQUES
# ─────────────────────────────────────────────

GS_COLORS = [
    "#C4A458","#7EB8D4","#6BAF72","#C0584E",
    "#A07CC5","#D4956A","#5B8DB8","#9BC4AE",
    "#E8D5A3","#8BA5C2","#B89C6E","#7AA880",
]

def gs_layout(**kw):
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color="#7A8094", size=11),
        legend=dict(bgcolor="rgba(13,16,23,0.9)", bordercolor="rgba(255,255,255,0.06)",
                    borderwidth=1, font=dict(color="#B8BCC8", size=10)),
        margin=dict(l=8, r=8, t=36, b=8), colorway=GS_COLORS,
    )
    base.update(kw)
    return base

def gs_axes(fig):
    opts = dict(gridcolor="rgba(255,255,255,0.04)", zerolinecolor="rgba(255,255,255,0.08)",
                linecolor="rgba(255,255,255,0.06)", tickcolor="rgba(255,255,255,0.15)",
                tickfont=dict(color="#7A8094", size=10))
    fig.update_xaxes(**opts)
    fig.update_yaxes(**opts)
    return fig

def title_style(txt):
    return dict(text=txt, font=dict(color="#F2EEE7", size=13))


# ─────────────────────────────────────────────
# GRAPHIQUES
# ─────────────────────────────────────────────

def g_evolution(res):
    fig = go.Figure()
    for i, r in enumerate(res):
        c = GS_COLORS[i % len(GS_COLORS)]
        fig.add_trace(go.Scatter(
            x=list(range(len(r["historique_brut"]))), y=r["historique_brut"],
            name=r["produit"].nom, line=dict(color=c, width=2), mode="lines",
            hovertemplate="%{y:,.0f} EUR<extra>" + r["produit"].nom + "</extra>"))
    fig.add_trace(go.Scatter(
        x=list(range(len(res[0]["historique_investi"]))), y=res[0]["historique_investi"],
        name="Capital investi", line=dict(color="#454A5A", width=1.5, dash="dot"),
        hovertemplate="%{y:,.0f} EUR<extra>Capital investi</extra>"))
    fig.update_layout(title=title_style("Evolution du capital brut"),
                      xaxis_title="Annees", yaxis_title="Capital (EUR)", yaxis_tickformat=",.0f",
                      **gs_layout())
    return gs_axes(fig)


def g_barres(res):
    noms  = [r["produit"].nom for r in res]
    bruts = [r["capital_final_brut"] for r in res]
    nets  = [r["capital_final_net"]  for r in res]
    taxes = [r["total_taxes"]        for r in res]
    fig   = go.Figure()
    fig.add_trace(go.Bar(name="Capital brut", x=noms, y=bruts,
                         marker_color="#2A2E3D",
                         text=[f"{v:,.0f}" for v in bruts], textposition="outside",
                         textfont=dict(size=9, color="#7A8094")))
    fig.add_trace(go.Bar(name="Capital net", x=noms, y=nets,
                         marker_color="#C4A458",
                         text=[f"{v:,.0f}" for v in nets], textposition="outside",
                         textfont=dict(size=9, color="#C4A458")))
    fig.add_trace(go.Bar(name="Taxes totales", x=noms, y=taxes,
                         marker_color="#C0584E",
                         text=[f"{v:,.0f}" for v in taxes], textposition="outside",
                         textfont=dict(size=9, color="#C0584E")))
    fig.update_layout(title=title_style("Capital final : Brut / Net / Taxes"),
                      barmode="group", yaxis_tickformat=",.0f", xaxis_tickangle=-20,
                      **gs_layout())
    return gs_axes(fig)


def g_donuts(res):
    n    = len(res)
    cols = min(n, 3)
    rows = math.ceil(n / cols)
    specs = [[{"type": "domain"}] * cols for _ in range(rows)]
    fig   = make_subplots(rows=rows, cols=cols, specs=specs,
                          subplot_titles=[r["produit"].nom for r in res])
    for idx, r in enumerate(res):
        values = [r["capital_investi"], max(0, r["plus_value_nette"]), max(0, r["total_taxes"])]
        fig.add_trace(go.Pie(
            labels=["Investi", "PV nette", "Taxes"], values=values, hole=0.6,
            marker_colors=["#2A2E3D", "#6BAF72", "#C0584E"],
            textinfo="percent", showlegend=(idx == 0),
            hovertemplate="%{label}: %{value:,.0f} EUR<extra></extra>",
        ), row=idx//cols+1, col=idx%cols+1)
    fig.update_layout(title=title_style("Repartition : Capital / Plus-value nette / Taxes"),
                      height=max(280, 280*rows), **gs_layout())
    return fig


def g_taux(res, inflation):
    noms  = [r["produit"].nom for r in res]
    bruts = [r["taux_brut_annualise"]*100 for r in res]
    nets  = [r["taux_net_annualise"]*100  for r in res]
    reels = [r["taux_reel"]*100           for r in res]
    fig   = go.Figure()
    fig.add_trace(go.Bar(y=noms, x=bruts, name="Brut", orientation="h",
                         marker_color="#2A2E3D",
                         text=[f"{v:.2f}%" for v in bruts], textposition="outside",
                         textfont=dict(size=9, color="#7A8094")))
    fig.add_trace(go.Bar(y=noms, x=nets, name="Net fiscal", orientation="h",
                         marker_color="#C4A458",
                         text=[f"{v:.2f}%" for v in nets], textposition="outside",
                         textfont=dict(size=9, color="#C4A458")))
    fig.add_trace(go.Bar(y=noms, x=reels, name=f"Reel (inflation {inflation*100:.1f}%)",
                         orientation="h", marker_color="#6BAF72",
                         text=[f"{v:.2f}%" for v in reels], textposition="outside",
                         textfont=dict(size=9, color="#6BAF72")))
    fig.update_layout(title=title_style("Taux annualises : Brut / Net / Reel"),
                      barmode="group", xaxis=dict(ticksuffix="%"),
                      height=max(320, len(res)*72), **gs_layout())
    return gs_axes(fig)


def g_bulle(res):
    risque_map = {"Nul": 0, "Faible": 1, "Modere": 2, "Eleve": 3, "Tres eleve": 4}
    fig = go.Figure()
    for i, r in enumerate(res):
        p   = r["produit"]
        col = GS_COLORS[i % len(GS_COLORS)]
        fig.add_trace(go.Scatter(
            x=[risque_map.get(p.risque, 2)], y=[r["taux_net_annualise"]*100],
            mode="markers+text", name=p.nom, text=[p.nom],
            textposition="top center", textfont=dict(size=8, color=col),
            marker=dict(size=max(14, r["capital_final_net"]/5000), color=col,
                        opacity=0.85, line=dict(width=1, color="rgba(255,255,255,0.12)")),
            hovertemplate=(f"<b>{p.nom}</b><br>Rendement net : %{{y:.2f}}%<br>"
                           f"Risque : {p.risque}<extra></extra>"),
        ))
    fig.update_layout(
        title=title_style("Profil risque / rendement net"),
        xaxis=dict(tickvals=[0,1,2,3,4],
                   ticktext=["Nul","Faible","Modere","Eleve","Tres eleve"],
                   title="Niveau de risque"),
        yaxis_title="Rendement net annualise (%)",
        showlegend=False, **gs_layout())
    return gs_axes(fig)


# ─────────────────────────────────────────────
# TABLEAU
# ─────────────────────────────────────────────

def tableau_recap(res) -> pd.DataFrame:
    rows = []
    for r in res:
        p = r["produit"]
        rows.append({
            "Produit":              p.nom,
            "Categorie":            p.categorie,
            "Capital investi":      f"{r['capital_investi']:,.0f} EUR",
            "Capital brut":         f"{r['capital_final_brut']:,.0f} EUR",
            "PV brute":             f"{r['plus_value_brute']:,.0f} EUR",
            "IR":                   f"{r['ir']:,.0f} EUR",
            "PS":                   f"{r['ps']:,.0f} EUR",
            "Total taxes":          f"{r['total_taxes']:,.0f} EUR",
            "Capital net":          f"{r['capital_final_net']:,.0f} EUR",
            "PV nette":             f"{r['plus_value_nette']:,.0f} EUR",
            "Taux brut/an":         f"{r['taux_brut_annualise']*100:.2f}%",
            "Taux net/an":          f"{r['taux_net_annualise']*100:.2f}%",
            "Taux reel/an":         f"{r['taux_reel']*100:.2f}%",
            "Taux fiscal effectif": f"{r['taux_effectif']:.1f}%",
            "Risque":               p.risque,
            "Liquidite":            p.liquidite,
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# FICHES PRODUITS
# ─────────────────────────────────────────────

RISQUE_PILL    = {"Nul":"pill-green","Faible":"pill-gold","Modere":"pill-orange",
                  "Eleve":"pill-red","Tres eleve":"pill-red"}
LIQUIDITE_PILL = {"Haute":"pill-green","Moyenne":"pill-orange",
                  "Faible":"pill-red","Tres faible":"pill-red"}

def render_fiche(p: Produit, taux: float):
    rp  = RISQUE_PILL.get(p.risque, "pill-gold")
    lp  = LIQUIDITE_PILL.get(p.liquidite, "pill-orange")
    cap = f"{p.plafond_depot:,.0f} EUR" if p.plafond_depot < 1e9 else "Illimite"
    gv  = "Oui" if p.garantie_capital else "Non"
    gc  = "pill-green" if p.garantie_capital else "pill-red"
    # IMPORTANT : on escape tout le texte dynamique pour éviter
    # que des caractères spéciaux (~ - & etc.) cassent le rendu HTML/Markdown
    nom_e  = html_lib.escape(p.nom)
    rq_e   = html_lib.escape(p.risque)
    lq_e   = html_lib.escape(p.liquidite)
    note_e = html_lib.escape(p.reglement_special)

    html_card = (
        '<div class="gs-card">'
          '<div class="gs-card-head">'
            f'<span class="gs-card-name">{nom_e}</span>'
            f'<span class="gs-pill {rp}">Risque {rq_e}</span>'
            f'<span class="gs-pill {lp}">Liquidite {lq_e}</span>'
            f'<span class="gs-pill {gc}">Garantie {gv}</span>'
          '</div>'
          '<div class="gs-card-grid">'
            '<div>'
              '<div class="gs-card-stat-lbl">Taux brut indicatif</div>'
              f'<div class="gs-card-stat-val gold">{taux*100:.2f}&nbsp;%</div>'
            '</div>'
            '<div>'
              '<div class="gs-card-stat-lbl">Plafond depot</div>'
              f'<div class="gs-card-stat-val">{cap}</div>'
            '</div>'
            '<div>'
              '<div class="gs-card-stat-lbl">Capital garanti</div>'
              f'<div class="gs-card-stat-val">{gv}</div>'
            '</div>'
          '</div>'
          f'<div class="gs-card-note">{note_e}</div>'
        '</div>'
    )
    st.markdown(html_card, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# MODULE RECOMMANDATION PERSONNALISEE
# ═══════════════════════════════════════════════════════════════════

# ── Mappings de scores ───────────────────────────────────────────────

RISQUE_SCORE  = {"Nul": 0, "Faible": 1, "Modere": 2, "Eleve": 3, "Tres eleve": 4}
LIQUIDITE_SCORE = {"Haute": 3, "Moyenne": 2, "Faible": 1, "Tres faible": 0}

# Quel objectif correspond à quel(s) produit(s) (bonus objectif)
OBJECTIF_PRODUITS: dict[str, list[str]] = {
    "Epargne securite":          ["livret_a", "ldds", "lep", "livret_b", "cel"],
    "Retraite long terme":       ["pea", "pea_pme", "av_euros", "av_uc", "fcpi_fip", "scpi"],
    "Projet moyen terme":        ["pel", "cel", "av_euros", "obligations", "livret_a"],
    "Constitution de patrimoine":["pea", "av_uc", "scpi", "cto", "pea_pme"],
    "Revenus complementaires":   ["scpi", "obligations", "cto", "av_euros"],
    "Speculation / performance": ["crypto", "cto", "pea", "pea_pme", "fcpi_fip"],
}

# Situation professionnelle → sensibilité fiscale
SITUATION_TMI_ADJUST: dict[str, float] = {
    "Salarie":       0.0,
    "Independant":   0.05,   # souvent TMI plus élevé
    "Retraite":     -0.05,   # TMI souvent plus bas
    "Sans activite":-0.10,
    "Fonctionnaire": 0.0,
}


# ── Dataclass Profil ─────────────────────────────────────────────────

@dataclass
class ProfilInvestisseur:
    age: int                      = 35
    age_retraite: int             = 65
    situation_pro: str            = "Salarie"
    objectif_principal: str       = "Constitution de patrimoine"
    horizon_ans: int              = 10
    tolerance_risque: int         = 2   # 0=tres prudent … 4=tres dynamique
    besoin_liquidite: str         = "Moyenne"
    capital_disponible: float     = 10_000
    capacite_epargne_mois: float  = 200
    a_deja_pea: bool              = False
    a_deja_av: bool               = False
    tmi: float                    = 0.30
    couple: bool                  = False
    enfants: int                  = 0
    patrimoine_immo: float        = 0.0   # % du patrimoine déjà en immobilier


# ── Questionnaire UI ─────────────────────────────────────────────────

def profil_questionnaire() -> ProfilInvestisseur:
    """Affiche le questionnaire investisseur et retourne le profil rempli."""

    st.markdown('<div class="rec-hero">'
                '<div class="rec-hero-label">Etape 1 / 1 &mdash; Questionnaire</div>'
                '<div class="rec-hero-title">Votre profil investisseur</div>'
                '<div class="rec-hero-sub">'
                'Renseignez vos parametres pour obtenir une recommandation personnalisee. '
                'Toutes les reponses restent locales, aucune donnee n\'est transmise.'
                '</div>'
                '</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="q-block"><div class="q-title">Situation personnelle</div>', unsafe_allow_html=True)
        age = st.slider("Age actuel", 18, 80, 35)
        age_retraite = st.slider("Age de depart en retraite vise", age + 1, 90,
                                 max(age + 5, min(65, 90)))
        situation_pro = st.selectbox("Situation professionnelle",
            ["Salarie", "Independant", "Fonctionnaire", "Retraite", "Sans activite"])
        couple   = st.checkbox("En couple (marie / pacse)", value=False)
        enfants  = st.number_input("Nombre d'enfants a charge", 0, 10, 0)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="q-block"><div class="q-title">Situation patrimoniale</div>', unsafe_allow_html=True)
        capital_dispo = st.number_input("Capital disponible a investir (EUR)", 0, 5_000_000, 10_000, 500)
        capacite_mois = st.number_input("Capacite d\'epargne mensuelle (EUR)", 0, 50_000, 200, 50)
        patrimoine_immo = st.slider("Part de l'immobilier dans votre patrimoine actuel (%)", 0, 100, 30)
        a_pea = st.checkbox("Je detiens deja un PEA ouvert", value=False)
        a_av  = st.checkbox("Je detiens deja une Assurance Vie", value=False)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="q-block"><div class="q-title">Objectifs & horizon</div>', unsafe_allow_html=True)
        objectif = st.selectbox("Objectif principal",
            list(OBJECTIF_PRODUITS.keys()))
        horizon = st.slider("Horizon d'investissement (annees)", 1, 40,
                             min(age_retraite - age, 30))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="q-block"><div class="q-title">Profil de risque</div>', unsafe_allow_html=True)
        RISQUE_LABELS = [
            "0 — Tres prudent (capital garanti avant tout)",
            "1 — Prudent (pertes < 5% acceptables)",
            "2 — Equilibre (pertes < 15% acceptables)",
            "3 — Dynamique (pertes < 30% acceptables)",
            "4 — Tres dynamique (pertes importantes tolerees)",
        ]
        tol_risque_idx = st.select_slider("Tolerance au risque", options=list(range(5)),
                                           format_func=lambda x: RISQUE_LABELS[x], value=2)
        besoin_liq = st.select_slider(
            "Besoin de liquidite (pouvoir sortir rapidement)",
            options=["Faible", "Moyenne", "Haute"], value="Moyenne")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="q-block"><div class="q-title">Situation fiscale</div>', unsafe_allow_html=True)
        # On récupère le TMI du sidebar via session state s'il est calculé
        tmi_val = st.select_slider(
            "Tranche marginale d'imposition (TMI)",
            options=[0, 11, 30, 41, 45],
            format_func=lambda x: f"{x} %",
            value=30,
        ) / 100
        st.markdown('</div>', unsafe_allow_html=True)

    return ProfilInvestisseur(
        age=age,
        age_retraite=age_retraite,
        situation_pro=situation_pro,
        objectif_principal=objectif,
        horizon_ans=horizon,
        tolerance_risque=tol_risque_idx,
        besoin_liquidite=besoin_liq,
        capital_disponible=capital_dispo,
        capacite_epargne_mois=capacite_mois,
        a_deja_pea=a_pea,
        a_deja_av=a_av,
        tmi=tmi_val,
        couple=couple,
        enfants=enfants,
        patrimoine_immo=patrimoine_immo / 100,
    )


# ── Moteur de scoring ────────────────────────────────────────────────

def scorer_produit(p: Produit, profil: ProfilInvestisseur) -> dict:
    """
    Score un produit sur 100 points selon 6 dimensions.
    Retourne le score global et le détail par axe.
    """
    scores = {}
    contraintes = []
    avantages   = []

    # ── 1. Compatibilite horizon (20 pts) ──────────────────────
    if p.duree_min_ans > profil.horizon_ans:
        scores["horizon"] = 0
        contraintes.append(f"Duree min {p.duree_min_ans} ans > horizon {profil.horizon_ans} ans")
    elif p.duree_min_ans == 0:
        scores["horizon"] = 20
        avantages.append("Aucune contrainte de duree")
    else:
        ratio = min(1.0, profil.horizon_ans / max(p.duree_min_ans * 1.5, 1))
        scores["horizon"] = round(ratio * 20)
        if ratio >= 0.9:
            avantages.append(f"Horizon compatible ({profil.horizon_ans} ans)")

    # ── 2. Adequation risque (20 pts) ──────────────────────────
    p_risk  = RISQUE_SCORE.get(p.risque, 2)
    u_risk  = profil.tolerance_risque
    delta   = abs(u_risk - p_risk)
    # Sur-risque (produit + risque que tolérance) → pénalité double
    if p_risk > u_risk:
        score_risque = max(0, 20 - delta * 7)
        if delta >= 2:
            contraintes.append(f"Risque {p.risque} depasse votre tolerance")
    else:
        score_risque = max(0, 20 - delta * 4)
        if p_risk < u_risk and delta >= 2:
            contraintes.append("Rendement potentiel sous-optimal pour votre profil")
    scores["risque"] = score_risque
    if delta == 0:
        avantages.append("Niveau de risque ideal pour votre profil")

    # ── 3. Liquidite (15 pts) ───────────────────────────────────
    p_liq  = LIQUIDITE_SCORE.get(p.liquidite, 1)
    u_liq  = LIQUIDITE_SCORE.get(profil.besoin_liquidite, 2)
    if p_liq >= u_liq:
        scores["liquidite"] = 15
        if profil.besoin_liquidite == "Haute":
            avantages.append("Disponibilite immediate compatible")
    else:
        deficit = u_liq - p_liq
        scores["liquidite"] = max(0, 15 - deficit * 6)
        if deficit >= 2:
            contraintes.append(f"Liquidite {p.liquidite} insuffisante pour vos besoins")

    # ── 4. Optimisation fiscale (20 pts) ───────────────────────
    score_fisc = 0
    if p.exonere_ir and p.exonere_ps:
        score_fisc = 20
        avantages.append("Exoneration totale IR + PS")
    elif p.code in ("pea", "pea_pme") and profil.horizon_ans >= 5:
        score_fisc = 18 if profil.tmi >= 0.30 else 14
        avantages.append("Exoneration IR PEA apres 5 ans")
        if profil.a_deja_pea:
            score_fisc = max(score_fisc - 4, 10)
            contraintes.append("PEA deja ouvert : plafond partiel")
    elif p.code in ("av_euros", "av_uc") and profil.horizon_ans >= 8:
        base = 16 if profil.tmi >= 0.30 else 12
        score_fisc = base + (2 if profil.couple else 0)
        avantages.append("Fiscalite AV avantageuse apres 8 ans")
        if profil.a_deja_av:
            score_fisc = min(score_fisc + 3, 20)
            avantages.append("AV deja ouverte : horloge fiscale avancee")
    elif p.soumis_ir_foncier:
        # Revenus fonciers : pénalité si TMI élevé
        score_fisc = max(0, 14 - int(profil.tmi * 30))
        if profil.tmi >= 0.41:
            contraintes.append(f"Revenus fonciers lourdement taxes a {profil.tmi*100:.0f}% TMI")
        if profil.patrimoine_immo > 0.40:
            score_fisc = max(0, score_fisc - 5)
            contraintes.append("Concentration immobiliere deja elevee dans votre patrimoine")
    elif p.code == "fcpi_fip":
        score_fisc = 12 + (4 if profil.tmi >= 0.30 else 0)
        avantages.append("Reduction IR a l'entree selon eligibilite")
    else:
        # PFU 30 % standard
        score_fisc = 8 if profil.tmi >= 0.30 else 12
        if profil.tmi == 0:
            score_fisc = 16
    scores["fiscalite"] = min(20, score_fisc)

    # ── 5. Compatibilite objectif (15 pts) ─────────────────────
    produits_objectif = OBJECTIF_PRODUITS.get(profil.objectif_principal, [])
    if p.code in produits_objectif:
        rank = produits_objectif.index(p.code)
        score_obj = max(9, 15 - rank * 2)
        avantages.append(f"Recommande pour : {profil.objectif_principal}")
    else:
        score_obj = 4
    scores["objectif"] = score_obj

    # ── 6. Accessibilite & praticite (10 pts) ──────────────────
    score_acc = 10
    if p.plafond_depot < 1e9:
        if profil.capital_disponible > p.plafond_depot:
            ratio_excess = (profil.capital_disponible - p.plafond_depot) / profil.capital_disponible
            score_acc = max(2, int((1 - ratio_excess) * 10))
            contraintes.append(f"Plafond {p.plafond_depot:,.0f} EUR depasse par votre capital")
        elif profil.capital_disponible > p.plafond_depot * 0.80:
            score_acc = 7
    # Bonus liquidite haute si pas de besoin urgent
    if p.code == "crypto" and profil.tolerance_risque < 3:
        score_acc = max(0, score_acc - 3)
    scores["accessibilite"] = score_acc

    total = sum(scores.values())

    # ── Alertes supplementaires ────────────────────────────────
    ans_avant_retraite = profil.age_retraite - profil.age
    if p.code in ("pea", "pea_pme") and ans_avant_retraite < 5:
        contraintes.append(f"Attention : retraite dans {ans_avant_retraite} ans, PEA non mature")
    if p.code == "fcpi_fip" and profil.besoin_liquidite == "Haute":
        contraintes.append("Blocage 7-10 ans incompatible avec besoin de liquidite eleve")
    if p.code == "crypto" and profil.enfants > 0:
        contraintes.append("Risque de perte totale : a limiter avec des personnes a charge")

    return dict(
        code=p.code,
        nom=p.nom,
        total=total,
        scores=scores,
        contraintes=contraintes,
        avantages=avantages,
        disqualifie=(scores["horizon"] == 0 or
                     (p.risque in ("Tres eleve",) and profil.tolerance_risque < 2)),
    )


def scorer_tous(profil: ProfilInvestisseur) -> list[dict]:
    """Score tous les produits et trie par score décroissant."""
    results = [scorer_produit(p, profil) for p in PRODUITS.values()]
    results.sort(key=lambda x: (not x["disqualifie"], x["total"]), reverse=True)
    return results


# ── Allocation suggérée ──────────────────────────────────────────────

def allocation_suggeree(profil: ProfilInvestisseur, scores: list[dict]) -> list[dict]:
    """
    Construit une allocation en % basée sur le top-5 des produits scorés,
    pondérée par le score et ajustée selon le profil.
    """
    eligibles = [s for s in scores if not s["disqualifie"] and s["total"] >= 40][:6]
    if not eligibles:
        eligibles = scores[:4]

    # Pondérations brutes
    total_score = sum(s["total"] for s in eligibles)
    alloc = []
    for s in eligibles:
        pct_raw = (s["total"] / total_score) * 100 if total_score > 0 else 100/len(eligibles)

        # Ajustements : éviter sur-concentration
        p = PRODUITS[s["code"]]
        if p.exonere_ir and p.exonere_ps:
            # Livrets : plafonner à 20% (sauf si épargne sécurité objectif)
            if profil.objectif_principal != "Epargne securite":
                pct_raw = min(pct_raw, 20)
        if p.code == "crypto":
            pct_raw = min(pct_raw, 10 if profil.tolerance_risque >= 3 else 5)
        if p.code == "scpi" and profil.patrimoine_immo > 0.35:
            pct_raw = min(pct_raw, 10)

        alloc.append({"code": s["code"], "nom": p.nom, "score": s["total"], "pct_raw": pct_raw})

    # Renormaliser à 100%
    total_raw = sum(a["pct_raw"] for a in alloc)
    for a in alloc:
        a["pct"] = round(a["pct_raw"] / total_raw * 100, 1)

    # Ajuster le premier pour arriver exactement à 100%
    diff = 100.0 - sum(a["pct"] for a in alloc)
    alloc[0]["pct"] = round(alloc[0]["pct"] + diff, 1)

    return sorted(alloc, key=lambda x: x["pct"], reverse=True)


# ── Analyse narrative ────────────────────────────────────────────────

def generer_narrative(profil: ProfilInvestisseur, scores: list[dict], alloc: list[dict]) -> str:
    """Génère une analyse textuelle personnalisée du profil et des recommandations."""

    top3     = [s for s in scores if not s["disqualifie"]][:3]
    ko_list  = [s for s in scores if s["disqualifie"]]

    # Libellés
    RISQUE_LABEL = {0:"tres prudent", 1:"prudent", 2:"equilibre", 3:"dynamique", 4:"tres dynamique"}
    risque_str   = RISQUE_LABEL.get(profil.tolerance_risque, "equilibre")
    ans_retraite = profil.age_retraite - profil.age
    horizon_str  = (f"{profil.horizon_ans} an" if profil.horizon_ans == 1
                    else f"{profil.horizon_ans} ans")
    tmi_str      = f"{profil.tmi*100:.0f}%"

    # Intro profil
    txt  = f"<h4>Synthese du profil</h4>"
    txt += (f"Vous avez <b>{profil.age} ans</b>, un profil <b>{risque_str}</b> "
            f"et un horizon d'investissement de <b>{horizon_str}</b>. "
            f"Votre objectif principal est <b>{profil.objectif_principal.lower()}</b>. ")

    if profil.tmi >= 0.30:
        txt += (f"Avec un TMI de <b>{tmi_str}</b>, la recherche d'enveloppes fiscalement "
                f"optimisees (PEA, assurance vie, livrets exoneres) est une priorite claire. ")
    elif profil.tmi == 0:
        txt += (f"Votre tranche a <b>0%</b> reduit l'interet des enveloppes defiscalisees. "
                f"Privilegiez le rendement brut et la liquidite. ")
    else:
        txt += (f"Votre TMI de <b>{tmi_str}</b> justifie d'evaluer l'option bareme "
                f"face au PFU selon les produits. ")

    if profil.patrimoine_immo > 0.40:
        txt += (f"Votre patrimoine est <b>deja fortement expose a l'immobilier ({profil.patrimoine_immo*100:.0f}%)</b>. "
                f"Il est conseille de limiter les SCPI supplementaires pour des raisons de diversification. ")

    if profil.besoin_liquidite == "Haute":
        txt += ("Votre <b>besoin de liquidite eleve</b> impose de conserver une poche d'epargne "
                "disponible immediatement (Livret A, LDDS) avant tout investissement de long terme. ")

    # Top recommandations
    txt += "<h4>Recommandations prioritaires</h4>"
    for i, s in enumerate(top3, 1):
        p = PRODUITS[s["code"]]
        avs_str = " &mdash; ".join(s["avantages"][:2]) if s["avantages"] else "Adapte a votre profil"
        txt += (f"<b>{i}. {p.nom}</b> (score {s['total']}/100) &mdash; "
                f"{avs_str}. ")
        if s["contraintes"]:
            txt += f"Point de vigilance : {s['contraintes'][0].lower()}. "
        txt += "<br>"

    # Allocation
    txt += "<h4>Strategie d'allocation suggeree</h4>"
    cap_total = profil.capital_disponible
    txt += (f"Sur la base de votre capital de <b>{cap_total:,.0f} EUR</b> "
            f"et d'une epargne mensuelle de <b>{profil.capacite_epargne_mois:,.0f} EUR/mois</b>, "
            f"voici une repartition equilibree : ")

    for a in alloc[:4]:
        montant = cap_total * a["pct"] / 100
        txt += f"<b>{a['pct']:.0f}% {a['nom']}</b> ({montant:,.0f} EUR), "
    txt = txt.rstrip(", ") + ". "

    # Horizon retraite
    if ans_retraite <= 15:
        txt += (f"<h4>Vigilance retraite</h4>"
                f"Avec <b>{ans_retraite} ans avant la retraite</b>, il est important de commencer "
                f"a securiser progressivement le capital a partir de {profil.age_retraite - 5} ans "
                f"en reduisant la part des actifs risques. ")

    # Produits disqualifies
    if ko_list:
        noms_ko = ", ".join(s["nom"] for s in ko_list[:3])
        txt += (f"<h4>Produits deconseilles pour votre profil</h4>"
                f"<b>{noms_ko}</b> ont ete ecartes en raison d'une incompatibilite "
                f"avec votre horizon ou votre tolerance au risque. ")

    # Disclaimer
    txt += ("<br><br><span style='font-size:0.72rem;color:var(--grey-3)'>"
            "Cette analyse est generee automatiquement a titre indicatif. "
            "Elle ne constitue pas un conseil en investissement au sens de la reglementation AMF. "
            "Consultez un conseiller en gestion de patrimoine (CGP) agree avant toute decision.</span>")

    return txt


# ── Graphiques du module recommandation ─────────────────────────────

def g_radar(s: dict) -> go.Figure:
    """Radar chart des 6 dimensions du score pour un produit."""
    dims   = ["Horizon", "Risque", "Liquidite", "Fiscalite", "Objectif", "Accessibilite"]
    maxs   = [20, 20, 15, 20, 15, 10]
    vals   = [s["scores"].get(k.lower(), 0) for k in
              ["horizon", "risque", "liquidite", "fiscalite", "objectif", "accessibilite"]]
    vals_n = [v / m * 100 for v, m in zip(vals, maxs)]

    fig = go.Figure(go.Scatterpolar(
        r=vals_n + [vals_n[0]],
        theta=dims + [dims[0]],
        fill="toself",
        fillcolor="rgba(196,164,88,0.12)",
        line=dict(color="#C4A458", width=2),
        hovertemplate="%{theta}: %{r:.0f}/100<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=8, color="#454A5A"),
                            gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.04)"),
            angularaxis=dict(tickfont=dict(size=9, color="#7A8094"),
                             gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.04)"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=20, b=20),
        height=220,
        showlegend=False,
    )
    return fig


def g_scores_barres(scores_list: list[dict]) -> go.Figure:
    """Barres horizontales du score total pour tous les produits."""
    eligibles   = [s for s in scores_list if not s["disqualifie"]]
    disqualifies = [s for s in scores_list if s["disqualifie"]]

    fig = go.Figure()
    if eligibles:
        noms   = [s["nom"] for s in eligibles]
        totaux = [s["total"] for s in eligibles]
        colors = [GS_COLORS[i % len(GS_COLORS)] for i in range(len(eligibles))]
        fig.add_trace(go.Bar(
            y=noms, x=totaux, orientation="h",
            marker=dict(color=colors, opacity=0.85),
            text=[f"{v}/100" for v in totaux], textposition="outside",
            textfont=dict(size=9, color="#B8BCC8"),
            name="Eligible",
            hovertemplate="%{y} : %{x}/100<extra></extra>",
        ))
    if disqualifies:
        noms_ko   = [s["nom"] for s in disqualifies]
        totaux_ko = [s["total"] for s in disqualifies]
        fig.add_trace(go.Bar(
            y=noms_ko, x=totaux_ko, orientation="h",
            marker=dict(color="#2A2E3D", opacity=0.6),
            text=[f"{v}/100 (incompatible)" for v in totaux_ko],
            textposition="outside",
            textfont=dict(size=9, color="#454A5A"),
            name="Disqualifie",
            hovertemplate="%{y} : %{x}/100 (disqualifie)<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="Score de compatibilite par produit (sur 100)", font=dict(color="#F2EEE7", size=13)),
        xaxis=dict(range=[0, 115]),
        barmode="overlay",
        height=max(300, (len(scores_list)) * 32 + 60),
        **gs_layout()
    )
    return gs_axes(fig)


def g_allocation_donut(alloc: list[dict]) -> go.Figure:
    """Donut de l'allocation suggérée."""
    fig = go.Figure(go.Pie(
        labels=[a["nom"] for a in alloc],
        values=[a["pct"] for a in alloc],
        hole=0.6,
        marker=dict(colors=GS_COLORS[:len(alloc)],
                    line=dict(color="#08090C", width=2)),
        textinfo="percent+label",
        textfont=dict(size=10, color="#B8BCC8"),
        hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Allocation suggeree", font=dict(color="#F2EEE7", size=13)),
        height=320,
        **gs_layout()
    )
    return fig


def g_detail_scores(scores_list: list[dict]) -> go.Figure:
    """Stacked bar des 6 dimensions de score pour tous les produits."""
    dims_labels = ["Horizon", "Risque", "Liquidite", "Fiscalite", "Objectif", "Accessibilite"]
    dims_keys   = ["horizon", "risque", "liquidite", "fiscalite", "objectif", "accessibilite"]
    cols        = ["#C4A458", "#7EB8D4", "#6BAF72", "#A07CC5", "#D4956A", "#5B8DB8"]
    noms        = [s["nom"] for s in scores_list]

    fig = go.Figure()
    for dim_key, dim_lbl, col in zip(dims_keys, dims_labels, cols):
        vals = [s["scores"].get(dim_key, 0) for s in scores_list]
        fig.add_trace(go.Bar(
            name=dim_lbl, y=noms, x=vals, orientation="h",
            marker_color=col, opacity=0.85,
            hovertemplate=f"{dim_lbl}: %{{x}} pts<extra>%{{y}}</extra>",
        ))

    fig.update_layout(
        title=dict(text="Detail du score par dimension", font=dict(color="#F2EEE7", size=13)),
        barmode="stack",
        xaxis=dict(range=[0, 105]),
        height=max(300, len(scores_list) * 32 + 60),
        **gs_layout()
    )
    return gs_axes(fig)


# ── Rendu de l'onglet recommandation ────────────────────────────────

def render_recommandation_tab():
    """Affiche l'onglet de recommandation personnalisée complet."""

    profil = profil_questionnaire()

    if st.button("Generer ma recommandation personnalisee", type="primary"):
        st.session_state["profil"]  = profil
        st.session_state["rec_done"] = True

    if not st.session_state.get("rec_done"):
        st.markdown(
            '<div class="gs-banner" style="margin-top:1.5rem">'
            'Remplissez le questionnaire ci-dessus puis cliquez sur le bouton pour '
            'obtenir votre analyse personnalisee.'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    profil = st.session_state.get("profil", profil)

    with st.spinner("Analyse en cours..."):
        all_scores = scorer_tous(profil)
        alloc      = allocation_suggeree(profil, all_scores)
        narrative  = generer_narrative(profil, all_scores, alloc)

    top3 = [s for s in all_scores if not s["disqualifie"]][:3]

    # ── Podium ────────────────────────────────────────
    st.markdown('<div class="gs-section"><span class="gs-section-line"></span>Top 3 — Recommandations personnalisees</div>', unsafe_allow_html=True)

    rank_cls = ["rank-1", "rank-2", "rank-3"]
    medails  = ["01", "02", "03"]

    cols_pod = st.columns(3)
    for i, (s, col) in enumerate(zip(top3, cols_pod)):
        p = PRODUITS[s["code"]]
        avs_html = "".join(f'<span class="tag-ok">{html_lib.escape(a[:40])}</span>' for a in s["avantages"][:3])
        ctr_html = "".join(f'<span class="tag-warning">{html_lib.escape(c[:40])}</span>' for c in s["contraintes"][:2])
        with col:
            st.markdown(
                f'<div class="podium-card {rank_cls[i]}">'
                f'<div class="podium-rank">{medails[i]}</div>'
                f'<div class="podium-nom">{html_lib.escape(p.nom)}</div>'
                f'<div class="podium-score">{s["total"]}<span style="font-size:0.8rem;color:var(--grey-2)">/100</span></div>'
                f'<div class="podium-score-lbl">Score de compatibilite</div>'
                f'<div class="podium-reason">{avs_html}{ctr_html}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Ligne : Radar #1 + Allocation ─────────────────
    c_radar, c_alloc = st.columns([1, 1])
    with c_radar:
        st.markdown(f'<div class="gs-section"><span class="gs-section-line"></span>Profil detail — {html_lib.escape(top3[0]["nom"])}</div>', unsafe_allow_html=True)
        st.plotly_chart(g_radar(top3[0]), use_container_width=True, config={"displayModeBar": False})

        # Score bars pour le #1
        dims_labels = ["Horizon", "Risque", "Liquidite", "Fiscalite", "Objectif", "Accessibilite"]
        dims_keys   = ["horizon", "risque", "liquidite", "fiscalite", "objectif", "accessibilite"]
        maxs        = [20, 20, 15, 20, 15, 10]
        bars_html   = ""
        for lbl, key, mx in zip(dims_labels, dims_keys, maxs):
            val = top3[0]["scores"].get(key, 0)
            pct = val / mx * 100
            bars_html += (
                f'<div class="score-row">'
                f'<span class="score-label">{lbl}</span>'
                f'<div class="score-bar-bg"><div class="score-bar-fill" style="width:{pct:.0f}%"></div></div>'
                f'<span class="score-val">{val}/{mx}</span>'
                f'</div>'
            )
        st.markdown(bars_html, unsafe_allow_html=True)

    with c_alloc:
        st.markdown('<div class="gs-section"><span class="gs-section-line"></span>Allocation suggeree</div>', unsafe_allow_html=True)
        st.plotly_chart(g_allocation_donut(alloc), use_container_width=True, config={"displayModeBar": False})

        # Barres d'allocation
        alloc_html = ""
        for i, a in enumerate(alloc):
            col_hex = GS_COLORS[i % len(GS_COLORS)]
            montant = profil.capital_disponible * a["pct"] / 100
            alloc_html += (
                f'<div class="alloc-row">'
                f'<span class="alloc-name">{html_lib.escape(a["nom"])}</span>'
                f'<div class="alloc-bar-bg">'
                f'<div class="alloc-bar-fill" style="width:{a["pct"]}%;background:{col_hex}"></div>'
                f'</div>'
                f'<span class="alloc-pct">{a["pct"]:.0f}%</span>'
                f'</div>'
            )
        st.markdown(alloc_html, unsafe_allow_html=True)
        st.markdown(
            f'<div class="gs-banner" style="margin-top:0.8rem;font-size:0.74rem">'
            f'Capital alloue : <b>{profil.capital_disponible:,.0f} EUR</b> &nbsp;|&nbsp; '
            f'Epargne mensuelle : <b>{profil.capacite_epargne_mois:,.0f} EUR/mois</b>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Score global tous produits ────────────────────
    st.markdown('<div class="gs-section"><span class="gs-section-line"></span>Scoring complet — Tous les produits</div>', unsafe_allow_html=True)
    c_bar, c_detail = st.columns([1, 1])
    with c_bar:
        st.plotly_chart(g_scores_barres(all_scores), use_container_width=True, config={"displayModeBar": False})
    with c_detail:
        st.plotly_chart(g_detail_scores(all_scores), use_container_width=True, config={"displayModeBar": False})

    # ── Tableau des scores ────────────────────────────
    st.markdown('<div class="gs-section"><span class="gs-section-line"></span>Tableau de scoring detaille</div>', unsafe_allow_html=True)
    table_rows = ""
    for rank, s in enumerate(all_scores, 1):
        rk_cls = "r1" if rank == 1 else ("r2" if rank == 2 else ("r3" if rank == 3 else ""))
        dq_style = "opacity:0.4;" if s["disqualifie"] else ""
        avs = " &mdash; ".join(s["avantages"][:2]) if s["avantages"] else "—"
        ctr = s["contraintes"][0] if s["contraintes"] else "—"
        sc  = s["scores"]
        table_rows += (
            f'<tr style="{dq_style}">'
            f'<td><span class="score-rank-badge {rk_cls}">{rank}</span></td>'
            f'<td style="color:var(--white);font-weight:500">{html_lib.escape(s["nom"])}</td>'
            f'<td class="score-num">{s["total"]}/100</td>'
            f'<td class="score-num">{sc.get("horizon",0)}/20</td>'
            f'<td class="score-num">{sc.get("risque",0)}/20</td>'
            f'<td class="score-num">{sc.get("liquidite",0)}/15</td>'
            f'<td class="score-num">{sc.get("fiscalite",0)}/20</td>'
            f'<td class="score-num">{sc.get("objectif",0)}/15</td>'
            f'<td class="score-num">{sc.get("accessibilite",0)}/10</td>'
            f'<td style="font-size:0.68rem;color:var(--grey-2)">{html_lib.escape(avs[:50])}</td>'
            f'<td style="font-size:0.68rem;color:var(--negative)">{html_lib.escape(ctr[:50])}</td>'
            f'</tr>'
        )
    st.markdown(
        '<table class="score-table"><thead><tr>'
        '<th>#</th><th>Produit</th><th>Score</th>'
        '<th>Horizon</th><th>Risque</th><th>Liquidite</th>'
        '<th>Fiscalite</th><th>Objectif</th><th>Acces</th>'
        '<th>Atout principal</th><th>Point de vigilance</th>'
        f'</tr></thead><tbody>{table_rows}</tbody></table>',
        unsafe_allow_html=True,
    )

    # ── Analyse narrative ─────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="gs-section"><span class="gs-section-line"></span>Analyse personnalisee</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="narrative">{narrative}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    st.markdown(
        '<div class="gs-header">'
          '<div>'
            '<div class="gs-wordmark">Investment Management &middot; France</div>'
            '<div class="gs-title">Comparateur de Placements</div>'
            '<div class="gs-subtitle">Rendements Bruts &amp; Nets &middot; Fiscalite 2026</div>'
          '</div>'
          '<div class="gs-badge-date">2026 &middot; FRANCE</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    params = sidebar_params()

    if not params["produits"]:
        st.warning("Selectionnez au moins un produit dans la barre laterale.")
        return

    # Calculs
    resultats = []
    for code in params["produits"]:
        p    = PRODUITS[code]
        taux = params["taux_custom"].get(code)
        res  = simuler(
            produit=p,
            capital_initial=params["capital_initial"],
            versement_mensuel=params["versement_mensuel"],
            duree_ans=params["duree_ans"],
            revenu_fiscal=params["revenu_fiscal"],
            taux_personalise=taux,
            couple=params["couple"],
            inflation=params["inflation"],
        )
        resultats.append(res)

    resultats.sort(key=lambda r: r["capital_final_net"], reverse=True)

    # KPI
    cap_total = params["capital_initial"] + params["versement_mensuel"] * 12 * params["duree_ans"]
    best      = resultats[0]
    worst     = resultats[-1]
    ecart     = best["capital_final_net"] - worst["capital_final_net"]
    tmi       = taux_marginal_ir(params["revenu_fiscal"])

    def kpi(val, lbl):
        return f'<div class="gs-kpi"><div class="gs-kpi-val">{val}</div><div class="gs-kpi-lbl">{lbl}</div></div>'

    st.markdown(
        '<div class="gs-kpi-row">'
        + kpi(f"{cap_total:,.0f}&nbsp;EUR", "Capital total investi")
        + kpi(f"{best['capital_final_net']:,.0f}&nbsp;EUR", "Meilleur net final")
        + kpi(f"{best['taux_net_annualise']*100:.2f}&nbsp;%", "Taux net max / an")
        + kpi(f"{ecart:,.0f}&nbsp;EUR", "Ecart max &minus; min")
        + kpi(f"{tmi*100:.0f}&nbsp;%", "Votre TMI")
        + '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="gs-banner">'
        f'<b>Hypotheses</b> &mdash; Fiscalite France 2026 &nbsp;|&nbsp; '
        f'PFU 30% (12,8% IR + 17,2% PS) &nbsp;|&nbsp; '
        f'TMI : {tmi*100:.0f}% &nbsp;|&nbsp; '
        f'Inflation : {params["inflation"]*100:.1f}%/an &nbsp;|&nbsp; '
        f'Duree : {params["duree_ans"]} ans &nbsp;|&nbsp; '
        f'{"Couple" if params["couple"] else "Celibataire"}'
        f'</div>',
        unsafe_allow_html=True,
    )

    for r in resultats:
        if r.get("capital_plafonne"):
            st.markdown(
                f'<div class="gs-warning">Plafond atteint &mdash; <b>'
                f'{html_lib.escape(r["produit"].nom)}</b> : '
                f'capital ramene a {r["produit"].plafond_depot:,.0f} EUR.</div>',
                unsafe_allow_html=True,
            )

    # Onglets
    tabs = st.tabs(["EVOLUTION", "COMPARAISON", "FISCALITE", "RENDEMENTS", "TABLEAU", "FICHES", "RECOMMANDATION"])

    with tabs[0]:
        st.markdown('<div class="gs-section"><span class="gs-section-line"></span>Evolution du capital au fil des annees</div>', unsafe_allow_html=True)
        st.plotly_chart(g_evolution(resultats), use_container_width=True, config={"displayModeBar": False})

    with tabs[1]:
        st.markdown('<div class="gs-section"><span class="gs-section-line"></span>Comparaison finale Brut / Net / Taxes</div>', unsafe_allow_html=True)
        st.plotly_chart(g_barres(resultats), use_container_width=True, config={"displayModeBar": False})

    with tabs[2]:
        st.markdown('<div class="gs-section"><span class="gs-section-line"></span>Decomposition fiscale par produit</div>', unsafe_allow_html=True)
        st.plotly_chart(g_donuts(resultats), use_container_width=True, config={"displayModeBar": False})
        st.markdown("---")
        st.markdown('<div class="gs-section"><span class="gs-section-line"></span>Detail par produit</div>', unsafe_allow_html=True)
        for r in resultats:
            c1, c2, c3, c4 = st.columns([2, 1, 1, 4])
            with c1: st.write(f"**{r['produit'].nom}**")
            with c2: st.metric("IR", f"{r['ir']:,.0f} EUR")
            with c3: st.metric("PS", f"{r['ps']:,.0f} EUR")
            with c4:
                st.markdown(
                    f'<div class="gs-banner" style="margin:0;font-size:0.74rem">'
                    f'{html_lib.escape(r["note_fiscale"])}</div>',
                    unsafe_allow_html=True,
                )

    with tabs[3]:
        st.markdown('<div class="gs-section"><span class="gs-section-line"></span>Taux annualises Brut / Net / Reel</div>', unsafe_allow_html=True)
        st.plotly_chart(g_taux(resultats, params["inflation"]), use_container_width=True, config={"displayModeBar": False})
        st.markdown('<div class="gs-section"><span class="gs-section-line"></span>Profil Risque / Rendement</div>', unsafe_allow_html=True)
        st.plotly_chart(g_bulle(resultats), use_container_width=True, config={"displayModeBar": False})

    with tabs[4]:
        st.markdown('<div class="gs-section"><span class="gs-section-line"></span>Tableau recapitulatif complet</div>', unsafe_allow_html=True)
        df = tableau_recap(resultats)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "Telecharger CSV", df.to_csv(index=False).encode("utf-8"),
            "comparateur_2026.csv", "text/csv",
        )

    with tabs[5]:
        st.markdown('<div class="gs-section"><span class="gs-section-line"></span>Fiches produits selectionnes</div>', unsafe_allow_html=True)
        for code in params["produits"]:
            p    = PRODUITS[code]
            taux = params["taux_custom"].get(code, p.taux_rendement_brut)
            render_fiche(p, taux)

    with tabs[6]:
        render_recommandation_tab()

    st.markdown(
        '<div class="gs-footer">'
        'Cette simulation est fournie a titre purement indicatif et ne constitue pas un conseil en investissement. &nbsp;|&nbsp; '
        'Les rendements passes ne prejugent pas des rendements futurs. &nbsp;|&nbsp; '
        'Fiscalite France 2026 : PFU 30% &middot; PS 17,2% &middot; Bareme IR 2026. &nbsp;|&nbsp; '
        'Consultez un conseiller en gestion de patrimoine (CGP) agree avant toute decision.'
        '</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()