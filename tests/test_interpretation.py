"""Tests de ui.interpretation : verdict, croisement de Fisher, seuils."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.interpretation import phrase_croisement, phrase_seuil, verdict
from ui.modeles import Parametres, Projets, calculer_resultats

FLUX_A = [-100_000.0, 30_000.0, 30_000.0, 30_000.0, 30_000.0, 30_000.0]
FLUX_B = [-200_000.0, 20_000.0, 40_000.0, 70_000.0, 90_000.0, 90_000.0]


def _resultats(taux: float):
    parametres = Parametres(taux=taux, nb_annees=5, var_a=0.0, var_b=0.0)
    projets = Projets(nom_a="A", nom_b="B", flux_a=FLUX_A, flux_b=FLUX_B,
                      flux_a_ajuste=FLUX_A, flux_b_ajuste=FLUX_B)
    return calculer_resultats(parametres, projets)


def _verdict(taux: float) -> tuple[str, str]:
    resultats = _resultats(taux)
    return verdict(resultats.parametres.taux, FLUX_A, FLUX_B, "A", "B",
                   resultats.van_a, resultats.van_b, resultats.tri_a,
                   resultats.tri_b, resultats.fisher)


def test_verdict_conflit_van_tri():
    niveau, message = _verdict(0.08)
    assert niveau == "warning"
    assert "Conflit" in message and "Fisher" in message


def test_verdict_aucun_projet_rentable():
    niveau, message = _verdict(0.50)
    assert niveau == "error"
    assert "aucun des deux projets ne crée de valeur" in message


def test_verdict_un_seul_projet_rentable():
    # À 14 % : A est rentable (+3 k€ environ), B ne l'est pas (−4,4 k€ environ).
    niveau, message = _verdict(0.14)
    assert niveau == "success"
    assert "seul projet rentable" in message


def test_phrase_croisement():
    # Sous le taux de Fisher, B domine ; au-dessus, A.
    phrase = phrase_croisement(0.1192, FLUX_A, FLUX_B, "A", "B")
    assert "**B**" in phrase and "**A**" in phrase


def test_phrase_seuil_baisse():
    assert "baisse" in phrase_seuil("A", -16.5)


def test_phrase_seuil_hausse():
    assert "hausse" in phrase_seuil("A", 63.8)


def test_phrase_seuil_absent():
    assert "reste négative" in phrase_seuil("A", None)


if __name__ == "__main__":
    import _outils

    _outils.executer(globals())
