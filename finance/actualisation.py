"""Actualisation des flux : VAN, VAN cumulée, délai de récupération, profil."""

from __future__ import annotations

from collections.abc import Sequence


def van(taux: float, flux: Sequence[float]) -> float:
    """Valeur actuelle nette : somme des flux[t] / (1 + taux)^t."""
    return sum(f / (1.0 + taux) ** t for t, f in enumerate(flux))


def van_cumulee_actualisee(taux: float, flux: Sequence[float]) -> list[float]:
    """VAN cumulée après chaque période (indice 0 = année 0)."""
    cumul, resultat = 0.0, []
    for t, f in enumerate(flux):
        cumul += f / (1.0 + taux) ** t
        resultat.append(cumul)
    return resultat


def delai_recuperation_actualise(taux: float, flux: Sequence[float]) -> float | None:
    """Délai (années, interpolé) pour que la VAN cumulée devienne >= 0.

    Retourne None si la VAN cumulée reste négative sur tout l'horizon.
    """
    cumuls = van_cumulee_actualisee(taux, flux)
    if not cumuls:
        return None
    if cumuls[0] >= 0:
        return 0.0
    for t in range(1, len(cumuls)):
        if cumuls[t] >= 0:
            flux_actualise = flux[t] / (1.0 + taux) ** t
            return (t - 1) + (-cumuls[t - 1] / flux_actualise)
    return None


def profil_van(
    flux: Sequence[float], taux_min: float, taux_max: float, nb_points: int = 200
) -> tuple[list[float], list[float]]:
    """Échantillonne le profil de VAN entre deux taux. Retourne (taux, valeurs)."""
    nb_points = max(nb_points, 2)
    pas = (taux_max - taux_min) / (nb_points - 1)
    taux = [taux_min + i * pas for i in range(nb_points)]
    return taux, [van(r, flux) for r in taux]
