"""Fonctions financières : VAN, TRI, délai de récupération actualisé, taux de Fisher.

Convention : flux[0] = année 0 (investissement, souvent négatif) ; flux[t] = flux net
de l'année t ; flux en fin de période ; taux d'actualisation constant.
"""

from __future__ import annotations

from collections.abc import Sequence

BORNE_INF_TRI = -0.9999
BORNE_SUP_TRI = 10.0


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


def _bissection(f, a: float, b: float, fa: float, iterations: int = 120) -> float:
    """Racine de f sur [a, b], f(a) et f(b) étant de signes opposés."""
    for _ in range(iterations):
        m = 0.5 * (a + b)
        fm = f(m)
        if fm == 0.0:
            return m
        if (fa < 0.0) != (fm < 0.0):
            b = m
        else:
            a, fa = m, fm
    return 0.5 * (a + b)


def tri(flux: Sequence[float]) -> float | None:
    """Taux de rentabilité interne : taux annulant la VAN.

    Balayage de ]−100 % ; +1 000 %] puis bissection. None si la VAN ne change
    pas de signe (flux non conventionnels sans TRI).
    """
    flux = list(flux)
    if not flux or all(f >= 0.0 for f in flux) or all(f <= 0.0 for f in flux):
        return None

    def f(r: float) -> float:
        return van(r, flux)

    nb_pas = 2200
    pas = (BORNE_SUP_TRI - BORNE_INF_TRI) / nb_pas
    r_prec, v_prec = BORNE_INF_TRI, f(BORNE_INF_TRI)
    for i in range(1, nb_pas + 1):
        r = BORNE_INF_TRI + i * pas
        v = f(r)
        if v == 0.0:
            return r
        if (v_prec < 0.0) != (v < 0.0):
            return _bissection(f, r_prec, r, v_prec)
        r_prec, v_prec = r, v
    return None


def taux_fisher(flux_1: Sequence[float], flux_2: Sequence[float]) -> float | None:
    """Taux de Fisher : taux pour lequel VAN(flux_1) = VAN(flux_2).

    Égal au TRI des flux différentiels ; séries alignées sur la plus longue.
    """
    n = max(len(flux_1), len(flux_2))
    difference = [
        (flux_1[t] if t < len(flux_1) else 0.0) - (flux_2[t] if t < len(flux_2) else 0.0)
        for t in range(n)
    ]
    return tri(difference)


def profil_van(
    flux: Sequence[float], taux_min: float, taux_max: float, nb_points: int = 200
) -> tuple[list[float], list[float]]:
    """Échantillonne le profil de VAN entre deux taux. Retourne (taux, valeurs)."""
    nb_points = max(nb_points, 2)
    pas = (taux_max - taux_min) / (nb_points - 1)
    taux = [taux_min + i * pas for i in range(nb_points)]
    return taux, [van(r, flux) for r in taux]


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
