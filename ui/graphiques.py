"""Figures Plotly de l'application (aucune dépendance à Streamlit)."""

from __future__ import annotations

from collections.abc import Sequence

import plotly.graph_objects as go

import parametres as cfg
from finance import (
    appliquer_variation,
    profil_van,
    van,
    van_cumulee_actualisee,
    variation_critique,
)
from ui.formatage import duree_texte, pourcent


def mise_en_forme(fig: go.Figure, titre_x: str, titre_y: str) -> go.Figure:
    """Applique le style commun (thème, légende, marges) à une figure."""
    fig.update_layout(
        xaxis_title=titre_x,
        yaxis_title=titre_y,
        template="plotly_white",
        height=430,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=40, b=10),
        hovermode="x unified",
    )
    return fig


def graphique_flux(
    flux_a: Sequence[float], flux_b: Sequence[float], nom_a: str, nom_b: str
) -> go.Figure:
    """Histogramme comparé des flux de trésorerie par année."""
    annees = [f"Année {t}" for t in range(len(flux_a))]
    fig = go.Figure()
    fig.add_bar(x=annees, y=list(flux_a), name=nom_a, marker_color=cfg.COULEUR_A)
    fig.add_bar(x=annees, y=list(flux_b), name=nom_b, marker_color=cfg.COULEUR_B)
    fig.update_layout(barmode="group")
    fig.add_hline(y=0, line_color=cfg.COULEUR_NEUTRE, line_width=1)
    return mise_en_forme(fig, "", "Flux net (€)")


def graphique_profil_van(
    taux: float, flux_a: Sequence[float], flux_b: Sequence[float],
    nom_a: str, nom_b: str,
    tri_a: float | None, tri_b: float | None, fisher: float | None,
) -> go.Figure:
    """Courbes de VAN en fonction du taux + point de croisement (Fisher)."""
    taux_max = 0.30
    for valeur in (tri_a, tri_b):
        if valeur is not None and valeur > 0:
            taux_max = max(taux_max, valeur * 1.35)
    taux_max = min(taux_max, 0.75)
    grille, valeurs_a = profil_van(flux_a, 0.0, taux_max, 220)
    _, valeurs_b = profil_van(flux_b, 0.0, taux_max, 220)
    x = [r * 100.0 for r in grille]

    fig = go.Figure()
    fig.add_scatter(x=x, y=valeurs_a, name=nom_a,
                    line=dict(color=cfg.COULEUR_A, width=2.5))
    fig.add_scatter(x=x, y=valeurs_b, name=nom_b,
                    line=dict(color=cfg.COULEUR_B, width=2.5))
    fig.add_hline(y=0, line_color=cfg.COULEUR_NEUTRE, line_width=1)
    fig.add_vline(x=taux * 100.0, line_dash="dash", line_color=cfg.COULEUR_NEUTRE,
                  line_width=1.5, annotation_text="Taux retenu",
                  annotation_position="top right",
                  annotation_font_color=cfg.COULEUR_NEUTRE)
    for val_van, couleur in ((van(taux, flux_a), cfg.COULEUR_A),
                             (van(taux, flux_b), cfg.COULEUR_B)):
        fig.add_scatter(x=[taux * 100.0], y=[val_van], mode="markers",
                        marker=dict(color=couleur, size=12,
                                    line=dict(color="white", width=1.5)),
                        showlegend=False, hoverinfo="skip")
    if fisher is not None and 0.0 < fisher <= taux_max:
        fig.add_scatter(x=[fisher * 100.0], y=[van(fisher, flux_a)], mode="markers+text",
                        marker=dict(color=cfg.COULEUR_FISHER, size=16, symbol="star"),
                        text=[f"Taux de Fisher ≈ {pourcent(fisher)}"],
                        textposition="bottom center",
                        textfont=dict(color=cfg.COULEUR_FISHER),
                        showlegend=False, hoverinfo="skip")
    return mise_en_forme(fig, "Taux d'actualisation (%)", "VAN (€)")


def graphique_drci(
    taux: float, flux_a: Sequence[float], flux_b: Sequence[float],
    nom_a: str, nom_b: str, drci_a: float | None, drci_b: float | None,
) -> go.Figure:
    """Courbes de VAN cumulée et points de récupération actualisée."""
    annees = list(range(len(flux_a)))
    fig = go.Figure()
    fig.add_scatter(x=annees, y=van_cumulee_actualisee(taux, flux_a), name=nom_a,
                    mode="lines+markers", line=dict(color=cfg.COULEUR_A, width=2.5),
                    marker=dict(size=7))
    fig.add_scatter(x=annees, y=van_cumulee_actualisee(taux, flux_b), name=nom_b,
                    mode="lines+markers", line=dict(color=cfg.COULEUR_B, width=2.5),
                    marker=dict(size=7))
    fig.add_hline(y=0, line_color=cfg.COULEUR_NEUTRE, line_width=1)
    marqueurs = ((drci_a, nom_a, cfg.COULEUR_A, "top center"),
                 (drci_b, nom_b, cfg.COULEUR_B, "bottom center"))
    for valeur, nom, couleur, position in marqueurs:
        if valeur is not None:
            fig.add_scatter(x=[valeur], y=[0.0], mode="markers+text",
                            marker=dict(color=couleur, size=13, symbol="diamond",
                                        line=dict(color="white", width=1.5)),
                            text=[f"{nom} : {duree_texte(valeur)}"],
                            textposition=position, textfont=dict(color=couleur),
                            showlegend=False, hoverinfo="skip")
    return mise_en_forme(fig, "Année", "VAN cumulée (€)")


def graphique_sensibilite(
    taux: float, flux_a: Sequence[float], flux_b: Sequence[float],
    nom_a: str, nom_b: str, var_a: float, var_b: float,
) -> go.Figure:
    """VAN selon la variation des flux d'exploitation + seuils d'annulation."""
    variations = list(range(-cfg.VARIATION_MAX, cfg.VARIATION_MAX + 1, 2))
    fig = go.Figure()
    for flux, nom, couleur in ((flux_a, nom_a, cfg.COULEUR_A),
                               (flux_b, nom_b, cfg.COULEUR_B)):
        fig.add_scatter(x=variations,
                        y=[van(taux, appliquer_variation(flux, v)) for v in variations],
                        name=nom, line=dict(color=couleur, width=2.5))
    fig.add_hline(y=0, line_color=cfg.COULEUR_NEUTRE, line_width=1)
    for flux, couleur, var in ((flux_a, cfg.COULEUR_A, var_a),
                               (flux_b, cfg.COULEUR_B, var_b)):
        fig.add_scatter(x=[var], y=[van(taux, appliquer_variation(flux, var))],
                        mode="markers",
                        marker=dict(color=couleur, size=12,
                                    line=dict(color="white", width=1.5)),
                        showlegend=False, hoverinfo="skip")
    for flux, nom, couleur in ((flux_a, nom_a, cfg.COULEUR_A),
                               (flux_b, nom_b, cfg.COULEUR_B)):
        seuil = variation_critique(taux, flux)
        if seuil is not None and -cfg.VARIATION_MAX <= seuil <= cfg.VARIATION_MAX:
            fig.add_scatter(x=[seuil], y=[0.0], mode="markers+text",
                            marker=dict(color=couleur, size=11, symbol="x"),
                            text=[f"Seuil {nom} : {pourcent(seuil / 100.0)}"],
                            textposition="top center",
                            textfont=dict(color=couleur, size=11),
                            showlegend=False, hoverinfo="skip")
    return mise_en_forme(fig, "Variation des flux d'exploitation (%)", "VAN (€)")
