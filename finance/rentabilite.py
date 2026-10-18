"""Taux de rentabilité : TRI et taux de Fisher (recherche de racines)."""

from __future__ import annotations

from collections.abc import Sequence

from finance.actualisation import van

BORNE_INF_TRI = -0.9999
BORNE_SUP_TRI = 10.0
_NB_PAS_RECHERCHE = 2200


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

    pas = (BORNE_SUP_TRI - BORNE_INF_TRI) / _NB_PAS_RECHERCHE
    r_prec, v_prec = BORNE_INF_TRI, f(BORNE_INF_TRI)
    for i in range(1, _NB_PAS_RECHERCHE + 1):
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
