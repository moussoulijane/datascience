# Pipeline ML - Prediction de Default de Credit Consommation

Pipeline complet de machine learning pour predire si un client va souscrire un credit a la consommation. Combine des features statistiques classiques et des features deep learning (LSTM Autoencoder) pour exploiter les sequences temporelles de soldes bancaires.

## Architecture

- **2 modeles CatBoost** segmentes par niveau de revenu :
  - **Modele LOW** : clients avec revenu <= 7000 MAD
  - **Modele HIGH** : clients avec revenu > 7000 MAD
- **LSTM Autoencoder** (optionnel) : extraction de features latentes depuis les sequences de soldes quotidiens (91 jours)

## Structure du projet

```
loan_prediction_pipeline/
├── config/
│   └── config.py                # Configuration centrale
├── src/
│   ├── data_loading.py          # Chargement et fusion donnees
│   ├── preprocessing.py         # Nettoyage et features de base
│   ├── feature_engineering.py   # Features statistiques + LSTM
│   ├── lstm_encoder.py          # LSTM Autoencoder
│   ├── training.py              # Entrainement des 2 modeles
│   └── inference.py             # Predictions
├── data/
│   ├── raw/                     # Donnees source (CSV)
│   └── processed/               # Caches Parquet
├── models/                      # Modeles sauvegardes
├── outputs/                     # Resultats inference
├── main.py                      # Point d'entree CLI
└── requirements.txt             # Dependances
```

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### Entrainement (sans LSTM)

```bash
python main.py train
```

### Entrainement (avec LSTM)

```bash
python main.py train --use_lstm --lstm_dim 16 --lstm_epochs 50
```

### Inference

```bash
python main.py infer --output outputs/predictions.csv
```

### Inference (avec LSTM)

```bash
python main.py infer --use_lstm --output outputs/predictions.csv
```

### Options

| Argument | Default | Description |
|---|---|---|
| `mode` | - | `train` ou `infer` |
| `--output` | `outputs/inference_results.csv` | Chemin de sortie inference |
| `--revenu_treshold` | `7000` | Seuil de revenu (MAD) |
| `--use_lstm` | `False` | Activer le LSTM Autoencoder |
| `--lstm_dim` | `16` | Dimension espace latent LSTM |
| `--lstm_epochs` | `50` | Epoques entrainement LSTM |

## Donnees attendues

Placer les fichiers CSV dans `data/raw/` :

- `train_base_part1.csv`, `train_base_part2.csv`, `train_base_part3.csv` : Donnees d'entrainement
- `client_demographics.csv`, `client_financials.csv` : Donnees d'enrichissement
- `inference_data.csv` : Donnees a scorer

### Colonnes temporelles

91 colonnes `jour_2024_09_01` a `jour_2024_11_30` contenant les soldes bancaires quotidiens (format string avec virgules).

## Features generees

### Features statistiques (9)

| Feature | Description |
|---|---|
| `solde_moyen` | Moyenne du solde |
| `solde_min` / `solde_max` | Extremums |
| `solde_std` | Ecart-type |
| `solde_volatilite` | Coefficient de variation |
| `solde_nb_negatif` | Jours en decouvert |
| `solde_dernier_jour` | Solde le plus recent |
| `solde_variation_moy` | Variation moyenne jour a jour |
| `solde_tendance` | Pente de regression lineaire |

### Features LSTM (16 par defaut)

`lstm_feature_0` a `lstm_feature_15` : representations latentes extraites par l'autoencoder LSTM.

## Sortie

Les resultats d'inference contiennent :

- `id_client` : Identifiant client
- `target_pred` : Prediction (0/1)
- `proba_souscription` : Probabilite de souscription
- `target_reel` : Target reelle (si disponible)
- Features utilisees pour la prediction
