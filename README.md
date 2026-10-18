# 📊 Comparateur de VAN — application Streamlit

Application de finance d'entreprise pour **comparer deux projets d'investissement** et
visualiser leurs indicateurs de rentabilité :

- **VAN** (valeur actuelle nette) au taux d'actualisation choisi ;
- **TRI** (taux de rentabilité interne) de chaque projet ;
- **Taux de Fisher** : taux d'actualisation où les deux VAN sont égales (point
  d'indifférence, affiché sur le graphique) ;
- **DRCI** (délai de récupération actualisé) ;
- **Scénarios de sensibilité** : impact d'une variation des flux d'exploitation sur la
  VAN, seuils de rentabilité, scénarios pessimiste / base / optimiste et export CSV.

## Prérequis

- Python 3.10 ou plus récent (3.12 conseillé).

## Installation

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

## Lancement

```powershell
.venv\Scripts\python -m streamlit run app.py
```

L'application s'ouvre sur <http://localhost:8501>.

## Utilisation

1. Dans la **barre latérale** : réglez le taux d'actualisation, la durée des projets et,
   si besoin, une variation de sensibilité sur les flux de chaque projet.
2. Saisissez le **nom**, l'**investissement initial** (année 0) et les **flux nets
   annuels** de chaque projet dans le tableau.
3. Consultez les **résultats** : cartes VAN / TRI / DRCI, verdict et interprétation du
   conflit éventuel VAN–TRI, profil de VAN avec taux de Fisher, courbe de récupération,
   puis scénarios de sensibilité (exportables en CSV).

L'exemple par défaut (Projet A : 100 000 € investis, 30 000 € par an pendant 5 ans ;
Projet B : 200 000 € investis, flux croissants) est construit pour illustrer le **conflit
classique VAN / TRI** : à 8 %, le projet B a la meilleure VAN mais le projet A le
meilleur TRI ; les courbes se croisent au **taux de Fisher ≈ 11,9 %**.

## Définitions

| Indicateur | Formule | Lecture |
|---|---|---|
| VAN | Σ fluxₜ / (1 + r)ᵗ | Valeur créée, en €, à actualiser au coût du capital r. |
| TRI | r tel que VAN(r) = 0 | Taux de rendement intrinsèque du projet. |
| Taux de Fisher | r tel que VAN_A(r) = VAN_B(r) | Taux d'indifférence : au-delà, le classement des projets s'inverse (TRI des flux différentiels). |
| DRCI | Année où la VAN cumulée ≥ 0 | Vitesse de récupération de l'investissement, en valeur actualisée. |

## Structure

```
Fintech/
├── app.py                    # interface Streamlit (graphiques Plotly, mise en page)
├── finance.py                # logique financière (VAN, TRI, Fisher, DRCI, sensibilité)
├── requirements.txt          # dépendances
├── tests/test_finance.py     # tests unitaires de la logique
└── .streamlit/config.toml    # thème de l'application
```

## Tests

```powershell
.venv\Scripts\python tests/test_finance.py
```

## Hypothèses et limites

- Flux perçus **en fin de période**, taux d'actualisation **constant**.
- Projets de **même durée** (l'horizon est commun aux deux projets).
- Flux nets d'impôt ; le taux retenu représente le coût du capital.
- Flux non conventionnels : le TRI peut ne pas exister ou être multiple ; la VAN reste
  alors le critère de référence.
- Les montants sont saisis en euros, sans gestion de l'inflation (raisonnez en €
  constants ou intégrez une prime d'inflation dans le taux).
