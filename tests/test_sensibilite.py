"""Tests de finance.sensibilite : variation des flux et seuil critique."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from finance import appliquer_variation, van, variation_critique

PROJET_A = [-100_000.0, 30_000.0, 30_000.0, 30_000.0, 30_000.0, 30_000.0]


def test_appliquer_variation():
    varie = appliquer_variation(PROJET_A, 10.0)
    assert varie[0] == -100_000.0
    assert all(abs(v - 33_000.0) < 1e-6 for v in varie[1:])
    assert appliquer_variation(PROJET_A, -50.0)[1] == 15_000.0


def test_variation_critique():
    seuil = variation_critique(0.08, PROJET_A)
    assert seuil is not None and abs(seuil - (-16.51)) < 0.05
    # Cohérence : la VAN s'annule à ce seuil.
    assert abs(van(0.08, appliquer_variation(PROJET_A, seuil))) < 1.0


def test_variation_critique_positive():
    # À 40 %, il faut augmenter les flux pour rendre le projet rentable.
    seuil = variation_critique(0.40, PROJET_A)
    assert seuil is not None and seuil > 0


def test_variation_critique_impossible():
    # PV d'exploitation nul (aucun flux positif) : aucune variation ne suffit.
    assert variation_critique(0.08, [-10_000.0, 0.0, 0.0, 0.0, 0.0, 0.0]) is None


if __name__ == "__main__":
    import _outils

    _outils.executer(globals())
