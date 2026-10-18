"""Comparateur de deux projets d'investissement : VAN, TRI, taux de Fisher,
délai de récupération actualisé et scénarios de sensibilité.

Lancement :  streamlit run app.py
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from finance import (
    appliquer_variation,
    delai_recuperation_actualise,
    profil_van,
    taux_fisher,
    tri,
    van,
    van_cumulee_actualisee,
    variation_critique,
)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
COULEUR_A = "#1f6fb2"        # bleu  → projet A
COULEUR_B = "#e8833a"        # orange → projet B
COULEUR_NEUTRE = "#94a3b8"   # gris
COULEUR_FISHER = "#7d3c98"   # violet → taux de Fisher
DUREE_MAX = 15
VARIATION_MAX = 50           # amplitude des scénarios de sensibilité, en %

INVESTISSEMENT_A_DEFAUT = 100_000.0
INVESTISSEMENT_B_DEFAUT = 200_000.0
FLUX_A_DEFAUT = [30_000.0] * DUREE_MAX
FLUX_B_DEFAUT = [20_000.0, 40_000.0, 70_000.0, 90_000.0, 90_000.0] + [90_000.0] * (DUREE_MAX - 5)

st.set_page_config(page_title="Comparateur de VAN", page_icon="📊", layout="wide")


# ---------------------------------------------------------------------------
# Mise en forme
# ---------------------------------------------------------------------------
def euros(montant: float) -> str:
    """Montant au format français : 12 500 €."""
    return f"{montant:,.0f}".replace(",", "\u202f") + " €"


def pourcent(valeur: float, decimales: int = 1) -> str:
    """Taux au format français : 8,5 %."""
    return f"{valeur * 100:.{decimales}f}".replace(".", ",") + " %"


def duree_texte(valeur: float) -> str:
    """Durée au format français : 4,03 ans."""
    return f"{valeur:.2f}".replace(".", ",") + " ans"


def texte_tri(valeur: float | None) -> str:
    return pourcent(valeur) if valeur is not None else "—"


def texte_drci(valeur: float | None, horizon: int) -> str:
    return duree_texte(valeur) if valeur is not None else f"> {horizon} ans"


# ---------------------------------------------------------------------------
# Interprétation
# ---------------------------------------------------------------------------
def phrase_croisement(fisher: float, flux_a, flux_b, nom_a: str, nom_b: str) -> str:
    """Compare les projets de part et d'autre du taux de Fisher."""
    ecart = max(0.01, abs(fisher) * 0.15)
    taux_bas = max(0.0, fisher - ecart)
    avantage_bas = van(taux_bas, flux_a) - van(taux_bas, flux_b)
    pref_bas, pref_haut = (nom_a, nom_b) if avantage_bas >= 0 else (nom_b, nom_a)
    return (f"En dessous de ce taux, **{pref_bas}** offre la VAN la plus élevée ; "
            f"au-dessus, **{pref_haut}** prend l'avantage.")


def verdict(taux, flux_a, flux_b, nom_a, nom_b, van_a, van_b, tri_a, tri_b,
            fisher) -> tuple[str, str]:
    """Synthèse de la comparaison : retourne (niveau d'alerte, message)."""
    if van_a < 0 and van_b < 0:
        return "error", (
            f"❌ Au taux de {pourcent(taux)}, **aucun des deux projets ne crée de valeur** : "
            f"VAN de {euros(van_a)} pour {nom_a} et de {euros(van_b)} pour {nom_b}. "
            "Sauf raison stratégique, mieux vaut renoncer à ces investissements à ce taux."
        )

    if (van_a >= 0) != (van_b >= 0):
        gagnant, perdant = (nom_a, nom_b) if van_a >= 0 else (nom_b, nom_a)
        van_gagnant, van_perdant = (van_a, van_b) if van_a >= 0 else (van_b, van_a)
        return "success", (
            f"✅ **{gagnant} est le seul projet rentable** au taux de {pourcent(taux)} : "
            f"VAN de {euros(van_gagnant)} contre {euros(van_perdant)} pour {perdant}."
        )

    meilleur_van = nom_a if van_a >= van_b else nom_b

    if tri_a is None or tri_b is None:
        return "success", (
            f"✅ **{meilleur_van} affiche la VAN la plus élevée** au taux de {pourcent(taux)} "
            f"({euros(max(van_a, van_b))} contre {euros(min(van_a, van_b))}). "
            "TRI non calculable pour au moins un projet (flux non conventionnels)."
        )

    meilleur_tri = nom_a if tri_a >= tri_b else nom_b

    if meilleur_van == meilleur_tri:
        return "success", (
            f"✅ **Les deux critères concordent : {meilleur_van} est préférable** au taux de "
            f"{pourcent(taux)}. VAN : {euros(max(van_a, van_b))} contre "
            f"{euros(min(van_a, van_b))} — TRI : {pourcent(max(tri_a, tri_b))} contre "
            f"{pourcent(min(tri_a, tri_b))}."
        )

    message = (
        f"⚠️ **Conflit VAN / TRI au taux de {pourcent(taux)}.** "
        f"Le TRI favorise **{meilleur_tri}** ({pourcent(max(tri_a, tri_b))} contre "
        f"{pourcent(min(tri_a, tri_b))}), mais la VAN — critère de référence pour maximiser "
        f"la valeur — désigne **{meilleur_van}** ({euros(max(van_a, van_b))} contre "
        f"{euros(min(van_a, van_b))}). "
    )
    if fisher is not None and fisher > 0:
        position = "au-dessus" if taux > fisher else "en dessous"
        message += (
            f"Ici le taux retenu ({pourcent(taux)}) est {position} du "
            f"**taux de Fisher ≈ {pourcent(fisher)}**. "
            + phrase_croisement(fisher, flux_a, flux_b, nom_a, nom_b)
        )
    else:
        message += "Les courbes de VAN ne se croisent pas dans la plage de taux usuels."
    return "warning", message


# ---------------------------------------------------------------------------
# Graphiques
# ---------------------------------------------------------------------------
def mise_en_forme(fig: go.Figure, titre_x: str, titre_y: str) -> go.Figure:
    fig.update_layout(
        xaxis_title=titre_x,
        yaxis_title=titre_y,
        template="plotly_white",
        height=430,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=40, b=10),
        hovermode="x unified",
    )
    return fig


def graphique_flux(flux_a, flux_b, nom_a, nom_b) -> go.Figure:
    annees = [f"Année {t}" for t in range(len(flux_a))]
    fig = go.Figure()
    fig.add_bar(x=annees, y=flux_a, name=nom_a, marker_color=COULEUR_A)
    fig.add_bar(x=annees, y=flux_b, name=nom_b, marker_color=COULEUR_B)
    fig.update_layout(barmode="group")
    fig.add_hline(y=0, line_color=COULEUR_NEUTRE, line_width=1)
    return mise_en_forme(fig, "", "Flux net (€)")


def graphique_profil_van(taux, flux_a, flux_b, nom_a, nom_b, tri_a, tri_b,
                         fisher) -> go.Figure:
    taux_max = 0.30
    for valeur in (tri_a, tri_b):
        if valeur is not None and valeur > 0:
            taux_max = max(taux_max, valeur * 1.35)
    taux_max = min(taux_max, 0.75)
    grille, valeurs_a = profil_van(flux_a, 0.0, taux_max, 220)
    _, valeurs_b = profil_van(flux_b, 0.0, taux_max, 220)
    x = [r * 100.0 for r in grille]

    fig = go.Figure()
    fig.add_scatter(x=x, y=valeurs_a, name=nom_a, line=dict(color=COULEUR_A, width=2.5))
    fig.add_scatter(x=x, y=valeurs_b, name=nom_b, line=dict(color=COULEUR_B, width=2.5))
    fig.add_hline(y=0, line_color=COULEUR_NEUTRE, line_width=1)
    fig.add_vline(x=taux * 100.0, line_dash="dash", line_color=COULEUR_NEUTRE,
                  line_width=1.5, annotation_text="Taux retenu",
                  annotation_position="top right", annotation_font_color=COULEUR_NEUTRE)
    for val_van, couleur in ((van(taux, flux_a), COULEUR_A), (van(taux, flux_b), COULEUR_B)):
        fig.add_scatter(x=[taux * 100.0], y=[val_van], mode="markers",
                        marker=dict(color=couleur, size=12, line=dict(color="white", width=1.5)),
                        showlegend=False, hoverinfo="skip")
    if fisher is not None and 0.0 < fisher <= taux_max:
        fig.add_scatter(x=[fisher * 100.0], y=[van(fisher, flux_a)], mode="markers+text",
                        marker=dict(color=COULEUR_FISHER, size=16, symbol="star"),
                        text=[f"Taux de Fisher ≈ {pourcent(fisher)}"],
                        textposition="bottom center", textfont=dict(color=COULEUR_FISHER),
                        showlegend=False, hoverinfo="skip")
    return mise_en_forme(fig, "Taux d'actualisation (%)", "VAN (€)")


def graphique_drci(taux, flux_a, flux_b, nom_a, nom_b, drci_a, drci_b) -> go.Figure:
    annees = list(range(len(flux_a)))
    fig = go.Figure()
    fig.add_scatter(x=annees, y=van_cumulee_actualisee(taux, flux_a), name=nom_a,
                    mode="lines+markers", line=dict(color=COULEUR_A, width=2.5),
                    marker=dict(size=7))
    fig.add_scatter(x=annees, y=van_cumulee_actualisee(taux, flux_b), name=nom_b,
                    mode="lines+markers", line=dict(color=COULEUR_B, width=2.5),
                    marker=dict(size=7))
    fig.add_hline(y=0, line_color=COULEUR_NEUTRE, line_width=1)
    marqueurs = ((drci_a, nom_a, COULEUR_A, "top center"),
                 (drci_b, nom_b, COULEUR_B, "bottom center"))
    for valeur, nom, couleur, position in marqueurs:
        if valeur is not None:
            fig.add_scatter(x=[valeur], y=[0.0], mode="markers+text",
                            marker=dict(color=couleur, size=13, symbol="diamond",
                                        line=dict(color="white", width=1.5)),
                            text=[f"{nom} : {duree_texte(valeur)}"], textposition=position,
                            textfont=dict(color=couleur), showlegend=False, hoverinfo="skip")
    return mise_en_forme(fig, "Année", "VAN cumulée (€)")


def graphique_sensibilite(taux, flux_a, flux_b, nom_a, nom_b, var_a, var_b) -> go.Figure:
    variations = list(range(-VARIATION_MAX, VARIATION_MAX + 1, 2))
    fig = go.Figure()
    for flux, nom, couleur in ((flux_a, nom_a, COULEUR_A), (flux_b, nom_b, COULEUR_B)):
        fig.add_scatter(x=variations,
                        y=[van(taux, appliquer_variation(flux, v)) for v in variations],
                        name=nom, line=dict(color=couleur, width=2.5))
    fig.add_hline(y=0, line_color=COULEUR_NEUTRE, line_width=1)
    for flux, couleur, var in ((flux_a, COULEUR_A, var_a), (flux_b, COULEUR_B, var_b)):
        fig.add_scatter(x=[var], y=[van(taux, appliquer_variation(flux, var))],
                        mode="markers",
                        marker=dict(color=couleur, size=12, line=dict(color="white", width=1.5)),
                        showlegend=False, hoverinfo="skip")
    for flux, nom, couleur in ((flux_a, nom_a, COULEUR_A), (flux_b, nom_b, COULEUR_B)):
        seuil = variation_critique(taux, flux)
        if seuil is not None and -VARIATION_MAX <= seuil <= VARIATION_MAX:
            fig.add_scatter(x=[seuil], y=[0.0], mode="markers+text",
                            marker=dict(color=couleur, size=11, symbol="x"),
                            text=[f"Seuil {nom} : {pourcent(seuil / 100.0)}"],
                            textposition="top center",
                            textfont=dict(color=couleur, size=11),
                            showlegend=False, hoverinfo="skip")
    return mise_en_forme(fig, "Variation des flux d'exploitation (%)", "VAN (€)")


# ---------------------------------------------------------------------------
# Barre latérale
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Paramètres")
    taux_pct = st.number_input("Taux d'actualisation (%)", min_value=0.0, max_value=60.0,
                               value=8.0, step=0.5,
                               help="Coût du capital ou taux de rentabilité minimal exigé.")
    taux = taux_pct / 100.0
    nb_annees = st.slider("Durée des projets (années)", 1, DUREE_MAX, 5)

    st.divider()
    st.subheader("🧪 Sensibilité des flux")
    st.caption(f"Variation appliquée aux flux des années 1 à {nb_annees} "
               "(investissement initial inchangé).")
    nom_a_apercu = st.session_state.get("nom_a", "Projet A")
    nom_b_apercu = st.session_state.get("nom_b", "Projet B")
    var_a = st.slider(f"Variation des flux — {nom_a_apercu} (%)",
                      -VARIATION_MAX, VARIATION_MAX, 0, 5, key="var_a")
    var_b = st.slider(f"Variation des flux — {nom_b_apercu} (%)",
                      -VARIATION_MAX, VARIATION_MAX, 0, 5, key="var_b")

# ---------------------------------------------------------------------------
# 1. Projets et flux
# ---------------------------------------------------------------------------
st.title("📊 Comparateur de projets — VAN et rentabilité")
st.caption("Comparez deux projets d'investissement : VAN, TRI, taux de Fisher, délai de "
           "récupération actualisé et analyse de sensibilité. Tous les calculs se mettent "
           "à jour instantanément.")

st.divider()
st.subheader("1️⃣ Projets et flux de trésorerie")

colonne_a, colonne_b = st.columns(2)
with colonne_a:
    nom_a = st.text_input("Nom du projet A", value="Projet A", key="nom_a")
    invest_a = st.number_input("Investissement initial — année 0 (€)", min_value=0.0,
                               value=INVESTISSEMENT_A_DEFAUT, step=5_000.0, key="invest_a")
with colonne_b:
    nom_b = st.text_input("Nom du projet B", value="Projet B", key="nom_b")
    invest_b = st.number_input("Investissement initial — année 0 (€)", min_value=0.0,
                               value=INVESTISSEMENT_B_DEFAUT, step=5_000.0, key="invest_b")

table_flux = pd.DataFrame({
    "Annee": [f"Année {t}" for t in range(1, nb_annees + 1)],
    "flux_a": FLUX_A_DEFAUT[:nb_annees],
    "flux_b": FLUX_B_DEFAUT[:nb_annees],
}).set_index("Annee")
table_flux.index.name = "Période"

edition = st.data_editor(
    table_flux,
    key=f"table_flux_{nb_annees}",
    use_container_width=True,
    column_config={
        "flux_a": st.column_config.NumberColumn(nom_a, format="%.0f",
                                                help="Flux net encaissé en fin d'année (€)."),
        "flux_b": st.column_config.NumberColumn(nom_b, format="%.0f",
                                                help="Flux net encaissé en fin d'année (€)."),
    },
)
st.caption("💡 Modifier la durée réinitialise les valeurs par défaut. Un flux peut être "
           "négatif (renouvellement d'équipement, charge exceptionnelle…).")

flux_a = [-invest_a] + edition["flux_a"].fillna(0.0).astype(float).tolist()
flux_b = [-invest_b] + edition["flux_b"].fillna(0.0).astype(float).tolist()

flux_a_ajuste = appliquer_variation(flux_a, var_a)
flux_b_ajuste = appliquer_variation(flux_b, var_b)

st.plotly_chart(graphique_flux(flux_a_ajuste, flux_b_ajuste, nom_a, nom_b),
                use_container_width=True)
if var_a != 0 or var_b != 0:
    st.caption("🧪 Sensibilité active : les flux affichés sont ajustés selon les variations "
               "de la barre latérale.")

# ---------------------------------------------------------------------------
# 2. Résultats
# ---------------------------------------------------------------------------
st.divider()
st.subheader("2️⃣ Résultats au taux retenu")

van_a = van(taux, flux_a_ajuste)
van_b = van(taux, flux_b_ajuste)
tri_a = tri(flux_a_ajuste)
tri_b = tri(flux_b_ajuste)
drci_a = delai_recuperation_actualise(taux, flux_a_ajuste)
drci_b = delai_recuperation_actualise(taux, flux_b_ajuste)
fisher = taux_fisher(flux_a_ajuste, flux_b_ajuste)

if var_a != 0 or var_b != 0:
    st.info(f"🧪 Sensibilité active — {nom_a} : {pourcent(var_a / 100.0)} · "
            f"{nom_b} : {pourcent(var_b / 100.0)} sur les flux d'exploitation.")

meilleur_van_nom = nom_a if van_a >= van_b else nom_b
trophee_possible = max(van_a, van_b) >= 0

colonne_a, colonne_b = st.columns(2)
cartes = ((colonne_a, nom_a, van_a, tri_a, drci_a),
          (colonne_b, nom_b, van_b, tri_b, drci_b))
for colonne, nom, val_van, val_tri, val_drci in cartes:
    with colonne:
        with st.container(border=True):
            entete = f"#### {nom}"
            if trophee_possible and nom == meilleur_van_nom:
                entete += "  🏆"
            st.markdown(entete)
            m1, m2, m3 = st.columns(3)
            m1.metric("VAN", euros(val_van), help="Valeur actuelle nette au taux retenu.")
            m2.metric("TRI", texte_tri(val_tri), help="Taux annulant la VAN du projet.")
            m3.metric("DRCI", texte_drci(val_drci, nb_annees),
                      help="Délai de récupération actualisé (VAN cumulée = 0).")

niveau, message = verdict(taux, flux_a_ajuste, flux_b_ajuste, nom_a, nom_b,
                          van_a, van_b, tri_a, tri_b, fisher)
{"success": st.success, "warning": st.warning, "error": st.error}[niveau](message)

# ---------------------------------------------------------------------------
# 3. Profil de VAN et taux de Fisher
# ---------------------------------------------------------------------------
st.divider()
st.subheader("3️⃣ Profil de VAN et taux de Fisher")
st.plotly_chart(
    graphique_profil_van(taux, flux_a_ajuste, flux_b_ajuste, nom_a, nom_b,
                         tri_a, tri_b, fisher),
    use_container_width=True,
)
if fisher is not None and fisher > 0:
    st.markdown(f"**Taux de Fisher ≈ {pourcent(fisher)}** — les courbes de VAN s'y croisent. "
                + phrase_croisement(fisher, flux_a_ajuste, flux_b_ajuste, nom_a, nom_b))
else:
    st.markdown("Les courbes ne se croisent pas dans la plage des taux positifs : un projet "
                "domine l'autre sur tout l'intervalle étudié.")

# ---------------------------------------------------------------------------
# 4. Délai de récupération actualisé
# ---------------------------------------------------------------------------
st.divider()
st.subheader("4️⃣ Délai de récupération actualisé")
st.plotly_chart(graphique_drci(taux, flux_a_ajuste, flux_b_ajuste, nom_a, nom_b,
                               drci_a, drci_b),
                use_container_width=True)
st.caption("Année où la VAN cumulée (flux actualisés cumulés) devient positive. "
           "« > horizon » signifie que l'investissement n'est pas récupéré sur la durée du projet.")

# ---------------------------------------------------------------------------
# 5. Scénarios de sensibilité
# ---------------------------------------------------------------------------
st.divider()
st.subheader("5️⃣ Scénarios de sensibilité")
st.plotly_chart(graphique_sensibilite(taux, flux_a, flux_b, nom_a, nom_b, var_a, var_b),
                use_container_width=True)
st.caption(f"Effet d'une variation uniforme des flux d'exploitation sur la VAN au taux de "
           f"{pourcent(taux)}. Les cercles marquent les variations retenues dans la barre "
           "latérale, les ✖ le seuil où la VAN s'annule.")

st.markdown("**Seuils de rentabilité** (variation des flux qui annule la VAN)")
lignes_seuils = []
for nom, flux in ((nom_a, flux_a), (nom_b, flux_b)):
    seuil = variation_critique(taux, flux)
    if seuil is None:
        lignes_seuils.append(f"- **{nom}** : la VAN reste négative sur toute la plage étudiée.")
    elif seuil < 0:
        quantite = f"{abs(seuil):.1f}".replace(".", ",")
        lignes_seuils.append(f"- **{nom}** : VAN nulle pour une baisse des flux de {quantite} % — "
                             "c'est la marge de sécurité avant de perdre la rentabilité.")
    else:
        quantite = f"{seuil:.1f}".replace(".", ",")
        lignes_seuils.append(f"- **{nom}** : la VAN ne devient positive qu'à partir d'une "
                             f"hausse des flux de {quantite} %.")
st.markdown("\n".join(lignes_seuils))

lignes = []
for libelle, variation in (("Pessimiste (−20 %)", -20.0), ("Base (0 %)", 0.0),
                           ("Optimiste (+20 %)", 20.0)):
    flux_a_scenario = appliquer_variation(flux_a, variation)
    flux_b_scenario = appliquer_variation(flux_b, variation)
    van_sa = van(taux, flux_a_scenario)
    van_sb = van(taux, flux_b_scenario)
    tri_sa = tri(flux_a_scenario)
    tri_sb = tri(flux_b_scenario)
    lignes.append({
        "Scénario": libelle,
        f"VAN — {nom_a} (€)": van_sa,
        f"VAN — {nom_b} (€)": van_sb,
        f"TRI — {nom_a} (%)": tri_sa * 100.0 if tri_sa is not None else None,
        f"TRI — {nom_b} (%)": tri_sb * 100.0 if tri_sb is not None else None,
        "Projet préféré (VAN)": nom_a if van_sa >= van_sb else nom_b,
    })
tableau_scenarios = pd.DataFrame(lignes).set_index("Scénario")

affichage = tableau_scenarios.copy()
for colonne in affichage.columns:
    if colonne.startswith("VAN"):
        affichage[colonne] = affichage[colonne].map(euros)
    elif colonne.startswith("TRI"):
        affichage[colonne] = affichage[colonne].map(
            lambda v: "—" if v is None or v != v else f"{v:.1f}".replace(".", ","))
st.dataframe(affichage, use_container_width=True)

st.download_button(
    "⬇️ Exporter les scénarios (CSV)",
    data=tableau_scenarios.to_csv(sep=";", decimal=",").encode("utf-8-sig"),
    file_name="scenarios_comparaison.csv",
    mime="text/csv",
)

st.divider()
st.caption("**Hypothèses** — flux perçus en fin de période ; taux d'actualisation constant ; "
           "projets de même durée ; flux nets d'impôt, taux = coût du capital. Le TRI peut ne "
           "pas exister (flux non conventionnels) : la VAN reste alors le critère de référence.")
