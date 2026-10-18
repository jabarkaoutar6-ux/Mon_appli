"""Mise en forme des nombres au format français (aucune dépendance Streamlit)."""

from __future__ import annotations


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
    """TRI formaté, ou tiret si indéfini."""
    return pourcent(valeur) if valeur is not None else "—"


def texte_drci(valeur: float | None, horizon: int) -> str:
    """DRCI formaté, ou « > horizon » si l'investissement n'est pas récupéré."""
    return duree_texte(valeur) if valeur is not None else f"> {horizon} ans"
