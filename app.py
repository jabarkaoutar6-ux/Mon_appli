"""Comparateur de deux projets d'investissement — application Streamlit.

Point d'entrée : assemble les sections de l'interface. La logique métier vit
dans le package `finance/`, les composants d'interface dans `ui/`, et la
configuration dans `parametres.py`.

Lancement :  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

import parametres as cfg
from ui import barre_laterale, sections
from ui.modeles import calculer_resultats

st.set_page_config(page_title="Comparateur de VAN", page_icon="📊", layout="wide")

st.title(cfg.TITRE)
st.caption(cfg.DESCRIPTION)

parametres = barre_laterale.rendre()
projets = sections.saisir_projets(parametres)
resultats = calculer_resultats(parametres, projets)

sections.afficher_resultats(resultats)
sections.afficher_profil(resultats)
sections.afficher_drci(resultats)
sections.afficher_sensibilite(resultats)
sections.afficher_pied_de_page()
