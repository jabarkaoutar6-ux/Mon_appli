"""Lanceur de tests minimal, sans pytest.

En bas d'un fichier de tests :

    if __name__ == "__main__":
        import _outils

        _outils.executer(globals())
"""

from __future__ import annotations


def executer(espace: dict) -> None:
    """Exécute toutes les fonctions ``test_*`` de l'espace de noms donné."""
    import traceback

    echecs = 0
    for nom, fonction in sorted(espace.items()):
        if nom.startswith("test_") and callable(fonction):
            try:
                fonction()
            except AssertionError:
                echecs += 1
                print(f"ÉCHEC {nom}")
                traceback.print_exc()
            else:
                print(f"OK    {nom}")
    if echecs:
        raise SystemExit(f"{echecs} échec(s).")
    print("Tous les tests sont passés.")
