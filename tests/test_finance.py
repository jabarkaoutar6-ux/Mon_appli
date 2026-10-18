"""Tests de la logique financière.

Lancement :
    python tests/test_finance.py
    ou :  pytest tests/
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from finance import (
    appliquer_variation,
    delai_recuperation_actualise,
    profil_van,
    taux_fisher,
    tri,
    van,
    van_cumulee_actualisee,
    variation_critique,
)

# Projets d'exemple de l'application.
PROJET_A = [-100_000.0, 30_000.0, 30_000.0, 30_000.0, 30_000.0, 30_000.0]
PROJET_B = [-200_000.0, 20_000.0, 40_000.0, 70_000.0, 90_000.0, 90_000.0]


def test_van_taux_nul():
    assert van(0.0, PROJET_A) == 50_000.0


def test_van_taux_positif():
    assert abs(van(0.08, PROJET_A) - 19_781.4) < 1.0


def test_van_profil():
    taux, valeurs = profil_van(PROJET_A, 0.0, 0.3, 50)
    assert len(taux) == len(valeurs) == 50
    assert taux[0] == 0.0 and abs(taux[-1] - 0.3) < 1e-9
    assert valeurs[0] == van(0.0, PROJET_A)


def test_tri_flux_simple():
    racine = tri([-100.0, 110.0])
    assert racine is not None and abs(racine - 0.10) < 1e-6


def test_tri_annuite():
    racine = tri(PROJET_A)
    assert racine is not None and abs(racine - 0.1524) < 0.0002


def test_tri_sans_racine():
    assert tri([100.0, 50.0, 20.0]) is None


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


if __name__ == "__main__":
    import traceback

    echecs = 0
    for nom, fonction in sorted(globals().items()):
        if nom.startswith("test_") and callable(fonction):
            try:
                fonction()
            except AssertionError:
                echecs += 1
                print(f"ÉCHEC {nom}")
                traceback.print_exc()
            else:
                print(f"OK    {nom}")
    print(f"\n{echecs} échec(s).")
    sys.exit(1 if echecs else 0)
