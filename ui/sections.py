"""Sections de la page : saisie des projets, résultats, graphiques, scénarios."""

from __future__ import annotations

import pandas as pd
import streamlit as st

import parametres as cfg
from finance import appliquer_variation, tri, van, variation_critique
from ui import graphiques
from ui.formatage import euros, pourcent, texte_drci, texte_tri
from ui.interpretation import phrase_croisement, phrase_seuil, verdict
from ui.modeles import Parametres, Projets, Resultats

# Scénarios standard du tableau (libellé, variation en %).
SCENARIOS = (
    ("Pessimiste (−20 %)", -20.0),
    ("Base (0 %)", 0.0),
    ("Optimiste (+20 %)", 20.0),
)


# ---------------------------------------------------------------------------
# 1. Saisie des projets
# ---------------------------------------------------------------------------
def saisir_projets(parametres: Parametres) -> Projets:
    """Section 1 : noms, investissements initiaux, flux annuels et graphique."""
    st.divider()
    st.subheader("1️⃣ Projets et flux de trésorerie")

    colonne_a, colonne_b = st.columns(2)
    with colonne_a:
        nom_a = st.text_input("Nom du projet A", value="Projet A", key="nom_a")
        invest_a = st.number_input("Investissement initial — année 0 (€)", min_value=0.0,
                                   value=cfg.INVESTISSEMENT_A_DEFAUT, step=5_000.0,
                                   key="invest_a")
    with colonne_b:
        nom_b = st.text_input("Nom du projet B", value="Projet B", key="nom_b")
        invest_b = st.number_input("Investissement initial — année 0 (€)", min_value=0.0,
                                   value=cfg.INVESTISSEMENT_B_DEFAUT, step=5_000.0,
                                   key="invest_b")

    nb_annees = parametres.nb_annees
    table_flux = pd.DataFrame({
        "Annee": [f"Année {t}" for t in range(1, nb_annees + 1)],
        "flux_a": cfg.FLUX_A_DEFAUT[:nb_annees],
        "flux_b": cfg.FLUX_B_DEFAUT[:nb_annees],
    }).set_index("Annee")
    table_flux.index.name = "Période"

    edition = st.data_editor(
        table_flux,
        key=f"table_flux_{nb_annees}",
        use_container_width=True,
        column_config={
            "flux_a": st.column_config.NumberColumn(
                nom_a, format="%.0f", help="Flux net encaissé en fin d'année (€)."),
            "flux_b": st.column_config.NumberColumn(
                nom_b, format="%.0f", help="Flux net encaissé en fin d'année (€)."),
        },
    )
    st.caption("💡 Modifier la durée réinitialise les valeurs par défaut. Un flux peut être "
               "négatif (renouvellement d'équipement, charge exceptionnelle…).")

    flux_a = [-invest_a] + edition["flux_a"].fillna(0.0).astype(float).tolist()
    flux_b = [-invest_b] + edition["flux_b"].fillna(0.0).astype(float).tolist()
    flux_a_ajuste = appliquer_variation(flux_a, parametres.var_a)
    flux_b_ajuste = appliquer_variation(flux_b, parametres.var_b)

    st.plotly_chart(
        graphiques.graphique_flux(flux_a_ajuste, flux_b_ajuste, nom_a, nom_b),
        use_container_width=True)
    if parametres.var_a != 0 or parametres.var_b != 0:
        st.caption("🧪 Sensibilité active : les flux affichés sont ajustés selon les "
                   "variations de la barre latérale.")

    return Projets(nom_a=nom_a, nom_b=nom_b, flux_a=flux_a, flux_b=flux_b,
                   flux_a_ajuste=flux_a_ajuste, flux_b_ajuste=flux_b_ajuste)


# ---------------------------------------------------------------------------
# 2. Résultats et verdict
# ---------------------------------------------------------------------------
def afficher_resultats(resultats: Resultats) -> None:
    """Section 2 : cartes VAN / TRI / DRCI et synthèse de la comparaison."""
    parametres, projets = resultats.parametres, resultats.projets
    st.divider()
    st.subheader("2️⃣ Résultats au taux retenu")

    if parametres.var_a != 0 or parametres.var_b != 0:
        st.info(f"🧪 Sensibilité active — {projets.nom_a} : "
                f"{pourcent(parametres.var_a / 100.0)} · {projets.nom_b} : "
                f"{pourcent(parametres.var_b / 100.0)} sur les flux d'exploitation.")

    colonne_a, colonne_b = st.columns(2)
    cartes = (
        (colonne_a, projets.nom_a, resultats.van_a, resultats.tri_a, resultats.drci_a),
        (colonne_b, projets.nom_b, resultats.van_b, resultats.tri_b, resultats.drci_b),
    )
    for colonne, nom, val_van, val_tri, val_drci in cartes:
        with colonne:
            with st.container(border=True):
                entete = f"#### {nom}"
                if resultats.trophee_possible and nom == resultats.meilleur_van_nom:
                    entete += "  🏆"
                st.markdown(entete)
                m1, m2, m3 = st.columns(3)
                m1.metric("VAN", euros(val_van),
                          help="Valeur actuelle nette au taux retenu.")
                m2.metric("TRI", texte_tri(val_tri),
                          help="Taux annulant la VAN du projet.")
                m3.metric("DRCI", texte_drci(val_drci, parametres.nb_annees),
                          help="Délai de récupération actualisé (VAN cumulée = 0).")

    niveau, message = verdict(
        parametres.taux, projets.flux_a_ajuste, projets.flux_b_ajuste,
        projets.nom_a, projets.nom_b, resultats.van_a, resultats.van_b,
        resultats.tri_a, resultats.tri_b, resultats.fisher)
    {"success": st.success, "warning": st.warning, "error": st.error}[niveau](message)


# ---------------------------------------------------------------------------
# 3. Profil de VAN et taux de Fisher
# ---------------------------------------------------------------------------
def afficher_profil(resultats: Resultats) -> None:
    """Section 3 : courbes de VAN en fonction du taux et taux de Fisher."""
    parametres, projets = resultats.parametres, resultats.projets
    st.divider()
    st.subheader("3️⃣ Profil de VAN et taux de Fisher")
    st.plotly_chart(
        graphiques.graphique_profil_van(
            parametres.taux, projets.flux_a_ajuste, projets.flux_b_ajuste,
            projets.nom_a, projets.nom_b, resultats.tri_a, resultats.tri_b,
            resultats.fisher),
        use_container_width=True)
    if resultats.fisher is not None and resultats.fisher > 0:
        st.markdown(
            f"**Taux de Fisher ≈ {pourcent(resultats.fisher)}** — les courbes de VAN "
            "s'y croisent. "
            + phrase_croisement(resultats.fisher, projets.flux_a_ajuste,
                                projets.flux_b_ajuste, projets.nom_a, projets.nom_b))
    else:
        st.markdown("Les courbes ne se croisent pas dans la plage des taux positifs : un "
                    "projet domine l'autre sur tout l'intervalle étudié.")


# ---------------------------------------------------------------------------
# 4. Délai de récupération actualisé
# ---------------------------------------------------------------------------
def afficher_drci(resultats: Resultats) -> None:
    """Section 4 : VAN cumulée et points de récupération de l'investissement."""
    parametres, projets = resultats.parametres, resultats.projets
    st.divider()
    st.subheader("4️⃣ Délai de récupération actualisé")
    st.plotly_chart(
        graphiques.graphique_drci(
            parametres.taux, projets.flux_a_ajuste, projets.flux_b_ajuste,
            projets.nom_a, projets.nom_b, resultats.drci_a, resultats.drci_b),
        use_container_width=True)
    st.caption("Année où la VAN cumulée (flux actualisés cumulés) devient positive. "
               "« > horizon » signifie que l'investissement n'est pas récupéré sur la "
               "durée du projet.")


# ---------------------------------------------------------------------------
# 5. Scénarios de sensibilité
# ---------------------------------------------------------------------------
def afficher_sensibilite(resultats: Resultats) -> None:
    """Section 5 : courbe de sensibilité, seuils et scénarios standard."""
    parametres, projets = resultats.parametres, resultats.projets
    st.divider()
    st.subheader("5️⃣ Scénarios de sensibilité")
    st.plotly_chart(
        graphiques.graphique_sensibilite(
            parametres.taux, projets.flux_a, projets.flux_b,
            projets.nom_a, projets.nom_b, parametres.var_a, parametres.var_b),
        use_container_width=True)
    st.caption(f"Effet d'une variation uniforme des flux d'exploitation sur la VAN au "
               f"taux de {pourcent(parametres.taux)}. Les cercles marquent les variations "
               "retenues dans la barre latérale, les ✖ le seuil où la VAN s'annule.")

    st.markdown("**Seuils de rentabilité** (variation des flux qui annule la VAN)")
    st.markdown("\n".join(
        phrase_seuil(nom, variation_critique(parametres.taux, flux))
        for nom, flux in ((projets.nom_a, projets.flux_a),
                          (projets.nom_b, projets.flux_b))
    ))

    tableau = _tableau_scenarios(resultats)
    affichage = tableau.copy()
    for colonne in affichage.columns:
        if colonne.startswith("VAN"):
            affichage[colonne] = affichage[colonne].map(euros)
        elif colonne.startswith("TRI"):
            affichage[colonne] = affichage[colonne].map(
                lambda v: "—" if v is None or v != v else f"{v:.1f}".replace(".", ","))
    st.dataframe(affichage, use_container_width=True)

    st.download_button(
        "⬇️ Exporter les scénarios (CSV)",
        data=tableau.to_csv(sep=";", decimal=",").encode("utf-8-sig"),
        file_name="scenarios_comparaison.csv",
        mime="text/csv",
    )


def _tableau_scenarios(resultats: Resultats) -> pd.DataFrame:
    """VAN / TRI des deux projets pour les scénarios pessimiste, base, optimiste."""
    parametres, projets = resultats.parametres, resultats.projets
    lignes = []
    for libelle, variation in SCENARIOS:
        flux_a = appliquer_variation(projets.flux_a, variation)
        flux_b = appliquer_variation(projets.flux_b, variation)
        van_a, van_b = van(parametres.taux, flux_a), van(parametres.taux, flux_b)
        tri_a, tri_b = tri(flux_a), tri(flux_b)
        lignes.append({
            "Scénario": libelle,
            f"VAN — {projets.nom_a} (€)": van_a,
            f"VAN — {projets.nom_b} (€)": van_b,
            f"TRI — {projets.nom_a} (%)": tri_a * 100.0 if tri_a is not None else None,
            f"TRI — {projets.nom_b} (%)": tri_b * 100.0 if tri_b is not None else None,
            "Projet préféré (VAN)": projets.nom_a if van_a >= van_b else projets.nom_b,
        })
    return pd.DataFrame(lignes).set_index("Scénario")


# ---------------------------------------------------------------------------
# Pied de page
# ---------------------------------------------------------------------------
def afficher_pied_de_page() -> None:
    """Hypothèses et limites, en bas de page."""
    st.divider()
    st.caption(cfg.HYPOTHESES)
