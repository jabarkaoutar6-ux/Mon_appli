"""Barre latérale : taux d'actualisation, durée et sensibilité des flux."""

from __future__ import annotations

import streamlit as st

import parametres as cfg
from ui.modeles import Parametres


def rendre() -> Parametres:
    """Affiche la barre latérale et retourne les réglages saisis."""
    with st.sidebar:
        st.title("⚙️ Paramètres")
        taux_pct = st.number_input(
            "Taux d'actualisation (%)",
            min_value=0.0, max_value=cfg.TAUX_MAX_PCT,
            value=cfg.TAUX_DEFAUT_PCT, step=0.5,
            help="Coût du capital ou taux de rentabilité minimal exigé.",
        )
        nb_annees = st.slider(
            "Durée des projets (années)", 1, cfg.DUREE_MAX, cfg.DUREE_DEFAUT)

        st.divider()
        st.subheader("🧪 Sensibilité des flux")
        st.caption(f"Variation appliquée aux flux des années 1 à {nb_annees} "
                   "(investissement initial inchangé).")
        nom_a = st.session_state.get("nom_a", "Projet A")
        nom_b = st.session_state.get("nom_b", "Projet B")
        var_a = st.slider(
            f"Variation des flux — {nom_a} (%)",
            -cfg.VARIATION_MAX, cfg.VARIATION_MAX, 0, 5, key="var_a")
        var_b = st.slider(
            f"Variation des flux — {nom_b} (%)",
            -cfg.VARIATION_MAX, cfg.VARIATION_MAX, 0, 5, key="var_b")

    return Parametres(taux=taux_pct / 100.0, nb_annees=nb_annees,
                      var_a=var_a, var_b=var_b)
