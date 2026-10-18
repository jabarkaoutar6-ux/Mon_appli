"""Tests de finance.actualisation : VAN, VAN cumulée, DRCI, profil."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from finance import (
    delai_recuperation_actualise,
    profil_van,
    van,
    van_cumulee_actualisee,
)

# Projets d'exemple de l'application.
PROJET_A = [-100_000.0, 30_000.0, 30_000.0, 30_000.0, 30_000.0, 30_000.0]


def test_van_taux_nul():
    assert van(0.0, PROJET_A) == 50_000.0


def test_van_taux_positif():
    assert abs(van(0.08, PROJET_A) - 19_781.4) < 1.0


def test_van_profil():
    taux, valeurs = profil_van(PROJET_A, 0.0, 0.3, 50)
    assert len(taux) == len(valeurs) == 50
    assert taux[0] == 0.0 and abs(taux[-1] - 0.3) < 1e-9
    assert valeurs[0] == van(0.0, PROJET_A)


def test_van_cumulee_actualisee():
    cumuls = van_cumulee_actualisee(0.08, PROJET_A)
    assert len(cumuls) == len(PROJET_A)
    assert cumuls[0] == -100_000.0
    assert abs(cumuls[-1] - van(0.08, PROJET_A)) < 1e-9


def test_drci_projet_a():
    delai = delai_recuperation_actualise(0.08, PROJET_A)
    assert delai is not None and abs(delai - 4.0288) < 0.01


def test_drci_non_atteint():
    assert delai_recuperation_actualise(0.10, [-1_000.0, 10.0, 10.0]) is None


if __name__ == "__main__":
    import _outils

    _outils.executer(globals())
