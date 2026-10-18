"""Analyse de sensibilité : variation des flux et seuils de rentabilité."""

from __future__ import annotations

from collections.abc import Sequence

from finance.actualisation import van


def appliquer_variation(flux: Sequence[float], variation_pct: float) -> list[float]:
    """Applique une variation (%) aux flux d'exploitation (années >= 1).

    L'investissement initial (année 0) reste inchangé.
    """
    facteur = 1.0 + variation_pct / 100.0
    return [flux[0]] + [f * facteur for f in flux[1:]]


def variation_critique(taux: float, flux: Sequence[float]) -> float | None:
    """Variation (%) des flux d'exploitation qui annule la VAN au taux donné.

    VAN(var) = flux[0] + (1 + var) × PV(exploitation) est linéaire en var :
    résolution directe. None si la VAN ne peut pas s'annuler (PV <= 0).
    """
    pv_exploitation = van(taux, [0.0] + list(flux[1:]))
    if pv_exploitation <= 0.0:
        return None
    return (-flux[0] / pv_exploitation - 1.0) * 100.0
