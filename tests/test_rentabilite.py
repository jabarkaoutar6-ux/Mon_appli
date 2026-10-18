"""Tests de finance.rentabilite : TRI et taux de Fisher."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from finance import taux_fisher, tri, van

PROJET_A = [-100_000.0, 30_000.0, 30_000.0, 30_000.0, 30_000.0, 30_000.0]
PROJET_B = [-200_000.0, 20_000.0, 40_000.0, 70_000.0, 90_000.0, 90_000.0]


def test_tri_flux_simple():
    racine = tri([-100.0, 110.0])
    assert racine is not None and abs(racine - 0.10) < 1e-6


def test_tri_annuite():
    racine = tri(PROJET_A)
    assert racine is not None and abs(racine - 0.1524) < 0.0002


def test_tri_sans_racine():
    assert tri([100.0, 50.0, 20.0]) is None


def test_taux_fisher():
    racine = taux_fisher(PROJET_A, PROJET_B)
    assert racine is not None and abs(racine - 0.1192) < 0.002
    # Cohérence : les deux VAN sont égales au taux de Fisher.
    assert abs(van(racine, PROJET_A) - van(racine, PROJET_B)) < 1.0


def test_taux_fisher_longueurs_differentes():
    # Séries de longueurs différentes : alignées sur la plus longue (zéros ajoutés).
    # -100 + 130/(1+r) = -100 + 151/(1+r)²  →  r = 151/130 - 1 ≈ 16,15 %.
    racine = taux_fisher([-100.0, 130.0], [-100.0, 0.0, 151.0])
    assert racine is not None and abs(racine - 0.1615) < 0.0005


if __name__ == "__main__":
    import _outils

    _outils.executer(globals())
