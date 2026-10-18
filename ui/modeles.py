"""Structures de données partagées entre les sections + calcul des résultats."""

from __future__ import annotations

from dataclasses import dataclass

from finance import delai_recuperation_actualise, taux_fisher, tri, van


@dataclass
class Parametres:
    """Réglages issus de la barre latérale."""

    taux: float        # taux d'actualisation (fraction, ex. 0.08)
    nb_annees: int
    var_a: float       # variation des flux du projet A, en %
    var_b: float       # variation des flux du projet B, en %


@dataclass
class Projets:
    """Projets saisis : flux de base (tableau) et flux ajustés (sensibilité)."""

    nom_a: str
    nom_b: str
    flux_a: list[float]
    flux_b: list[float]
    flux_a_ajuste: list[float]
    flux_b_ajuste: list[float]


@dataclass
class Resultats:
    """Indicateurs calculés pour les deux projets."""

    parametres: Parametres
    projets: Projets
    van_a: float
    van_b: float
    tri_a: float | None
    tri_b: float | None
    drci_a: float | None
    drci_b: float | None
    fisher: float | None

    @property
    def meilleur_van_nom(self) -> str:
        """Nom du projet à la VAN la plus élevée."""
        return self.projets.nom_a if self.van_a >= self.van_b else self.projets.nom_b

    @property
    def trophee_possible(self) -> bool:
        """Vrai si au moins un projet crée de la valeur."""
        return max(self.van_a, self.van_b) >= 0


def calculer_resultats(parametres: Parametres, projets: Projets) -> Resultats:
    """Calcule tous les indicateurs à partir des réglages et des projets."""
    taux = parametres.taux
    flux_a, flux_b = projets.flux_a_ajuste, projets.flux_b_ajuste
    return Resultats(
        parametres=parametres,
        projets=projets,
        van_a=van(taux, flux_a),
        van_b=van(taux, flux_b),
        tri_a=tri(flux_a),
        tri_b=tri(flux_b),
        drci_a=delai_recuperation_actualise(taux, flux_a),
        drci_b=delai_recuperation_actualise(taux, flux_b),
        fisher=taux_fisher(flux_a, flux_b),
    )
