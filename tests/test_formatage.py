"""Tests de ui.formatage : nombres au format français."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.formatage import duree_texte, euros, pourcent, texte_drci, texte_tri


def test_euros():
    assert euros(19_781.4) == "19\u202f781 €"
    assert euros(-16_514.0) == "-16\u202f514 €"


def test_pourcent():
    assert pourcent(0.1524) == "15,2 %"
    assert pourcent(-0.1651) == "-16,5 %"


def test_duree():
    assert duree_texte(4.0288) == "4,03 ans"


def test_texte_tri():
    assert texte_tri(None) == "—"
    assert texte_tri(0.10) == "10,0 %"


def test_texte_drci():
    assert texte_drci(None, 5) == "> 5 ans"
    assert texte_drci(4.03, 5) == "4,03 ans"


if __name__ == "__main__":
    import _outils

    _outils.executer(globals())
