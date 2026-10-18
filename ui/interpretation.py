"""Génération des textes d'analyse : verdict, croisement de Fisher, seuils.

Fonctions pures (aucune dépendance à Streamlit), directement testables.
"""

from __future__ import annotations

from collections.abc import Sequence

from finance import van
from ui.formatage import euros, pourcent


def phrase_croisement(
    fisher: float, flux_a: Sequence[float], flux_b: Sequence[float],
    nom_a: str, nom_b: str,
) -> str:
    """Compare les projets de part et d'autre du taux de Fisher."""
    ecart = max(0.01, abs(fisher) * 0.15)
    taux_bas = max(0.0, fisher - ecart)
    avantage_bas = van(taux_bas, flux_a) - van(taux_bas, flux_b)
    pref_bas, pref_haut = (nom_a, nom_b) if avantage_bas >= 0 else (nom_b, nom_a)
    return (f"En dessous de ce taux, **{pref_bas}** offre la VAN la plus élevée ; "
            f"au-dessus, **{pref_haut}** prend l'avantage.")


def verdict(
    taux: float, flux_a: Sequence[float], flux_b: Sequence[float],
    nom_a: str, nom_b: str, van_a: float, van_b: float,
    tri_a: float | None, tri_b: float | None, fisher: float | None,
) -> tuple[str, str]:
    """Synthèse de la comparaison : retourne (niveau, message).

    Niveau à interpréter par l'interface : « success », « warning » ou « error ».
    """
    if van_a < 0 and van_b < 0:
        return "error", (
            f"❌ Au taux de {pourcent(taux)}, **aucun des deux projets ne crée de valeur** : "
            f"VAN de {euros(van_a)} pour {nom_a} et de {euros(van_b)} pour {nom_b}. "
            "Sauf raison stratégique, mieux vaut renoncer à ces investissements à ce taux."
        )

    if (van_a >= 0) != (van_b >= 0):
        gagnant, perdant = (nom_a, nom_b) if van_a >= 0 else (nom_b, nom_a)
        van_gagnant, van_perdant = (van_a, van_b) if van_a >= 0 else (van_b, van_a)
        return "success", (
            f"✅ **{gagnant} est le seul projet rentable** au taux de {pourcent(taux)} : "
            f"VAN de {euros(van_gagnant)} contre {euros(van_perdant)} pour {perdant}."
        )

    meilleur_van = nom_a if van_a >= van_b else nom_b

    if tri_a is None or tri_b is None:
        return "success", (
            f"✅ **{meilleur_van} affiche la VAN la plus élevée** au taux de {pourcent(taux)} "
            f"({euros(max(van_a, van_b))} contre {euros(min(van_a, van_b))}). "
            "TRI non calculable pour au moins un projet (flux non conventionnels)."
        )

    meilleur_tri = nom_a if tri_a >= tri_b else nom_b

    if meilleur_van == meilleur_tri:
        return "success", (
            f"✅ **Les deux critères concordent : {meilleur_van} est préférable** au taux de "
            f"{pourcent(taux)}. VAN : {euros(max(van_a, van_b))} contre "
            f"{euros(min(van_a, van_b))} — TRI : {pourcent(max(tri_a, tri_b))} contre "
            f"{pourcent(min(tri_a, tri_b))}."
        )

    message = (
        f"⚠️ **Conflit VAN / TRI au taux de {pourcent(taux)}.** "
        f"Le TRI favorise **{meilleur_tri}** ({pourcent(max(tri_a, tri_b))} contre "
        f"{pourcent(min(tri_a, tri_b))}), mais la VAN — critère de référence pour maximiser "
        f"la valeur — désigne **{meilleur_van}** ({euros(max(van_a, van_b))} contre "
        f"{euros(min(van_a, van_b))}). "
    )
    if fisher is not None and fisher > 0:
        position = "au-dessus" if taux > fisher else "en dessous"
        message += (
            f"Ici le taux retenu ({pourcent(taux)}) est {position} du "
            f"**taux de Fisher ≈ {pourcent(fisher)}**. "
            + phrase_croisement(fisher, flux_a, flux_b, nom_a, nom_b)
        )
    else:
        message += "Les courbes de VAN ne se croisent pas dans la plage de taux usuels."
    return "warning", message


def phrase_seuil(nom: str, seuil: float | None) -> str:
    """Décrit le seuil de rentabilité (variation des flux annulant la VAN)."""
    if seuil is None:
        return f"- **{nom}** : la VAN reste négative sur toute la plage étudiée."
    if seuil < 0:
        quantite = f"{abs(seuil):.1f}".replace(".", ",")
        return (f"- **{nom}** : VAN nulle pour une baisse des flux de {quantite} % — "
                "c'est la marge de sécurité avant de perdre la rentabilité.")
    quantite = f"{seuil:.1f}".replace(".", ",")
    return (f"- **{nom}** : la VAN ne devient positive qu'à partir d'une "
            f"hausse des flux de {quantite} %.")
