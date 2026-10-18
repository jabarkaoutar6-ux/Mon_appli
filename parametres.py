"""Configuration centralisée : couleurs, bornes, valeurs par défaut, textes."""

# --------------------------------------------------------------------------
# Couleurs des graphiques
# --------------------------------------------------------------------------
COULEUR_A = "#1f6fb2"        # bleu  → projet A
COULEUR_B = "#e8833a"        # orange → projet B
COULEUR_NEUTRE = "#94a3b8"   # gris
COULEUR_FISHER = "#7d3c98"   # violet → taux de Fisher

# --------------------------------------------------------------------------
# Bornes des paramètres
# --------------------------------------------------------------------------
DUREE_MAX = 15
TAUX_MAX_PCT = 60.0
VARIATION_MAX = 50           # amplitude des scénarios de sensibilité, en %

# --------------------------------------------------------------------------
# Valeurs par défaut
# --------------------------------------------------------------------------
TAUX_DEFAUT_PCT = 8.0
DUREE_DEFAUT = 5

# Projets d'exemple (illustration du conflit classique VAN / TRI).
INVESTISSEMENT_A_DEFAUT = 100_000.0
INVESTISSEMENT_B_DEFAUT = 200_000.0
FLUX_A_DEFAUT = [30_000.0] * DUREE_MAX
FLUX_B_DEFAUT = [20_000.0, 40_000.0, 70_000.0, 90_000.0, 90_000.0] + [90_000.0] * (DUREE_MAX - 5)

# --------------------------------------------------------------------------
# Textes de l'interface
# --------------------------------------------------------------------------
TITRE = "📊 Comparateur de projets — VAN et rentabilité"
DESCRIPTION = (
    "Comparez deux projets d'investissement : VAN, TRI, taux de Fisher, délai de "
    "récupération actualisé et analyse de sensibilité. Tous les calculs se mettent "
    "à jour instantanément."
)
HYPOTHESES = (
    "**Hypothèses** — flux perçus en fin de période ; taux d'actualisation constant ; "
    "projets de même durée ; flux nets d'impôt, taux = coût du capital. Le TRI peut ne "
    "pas exister (flux non conventionnels) : la VAN reste alors le critère de référence."
)
