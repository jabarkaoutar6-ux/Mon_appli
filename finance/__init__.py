"""Logique financière pure de l'application (sans dépendance à Streamlit).

Exemple d'utilisation :

    from finance import van, tri, taux_fisher
"""

from finance.actualisation import (
    delai_recuperation_actualise,
    profil_van,
    van,
    van_cumulee_actualisee,
)
from finance.rentabilite import taux_fisher, tri
from finance.sensibilite import appliquer_variation, variation_critique

__all__ = [
    "van",
    "van_cumulee_actualisee",
    "delai_recuperation_actualise",
    "profil_van",
    "tri",
    "taux_fisher",
    "appliquer_variation",
    "variation_critique",
]
