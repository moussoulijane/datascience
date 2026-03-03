"""Creation de features statistiques et LSTM depuis les sequences temporelles."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from src.lstm_encoder import LSTMEncoder


def compute_slope(values: np.ndarray) -> float:
    """Calcule la pente (tendance) d'une serie temporelle via regression lineaire."""
    x = np.arange(len(values)).reshape(-1, 1)
    y = values.reshape(-1, 1)
    model = LinearRegression()
    model.fit(x, y)
    return model.coef_[0][0]


def add_balance_features(df: pd.DataFrame) -> pd.DataFrame:
    """Cree 9 features statistiques depuis les colonnes jour_*.

    Features creees:
        - solde_moyen: Moyenne du solde.
        - solde_min/max: Extremums.
        - solde_std: Ecart-type.
        - solde_volatilite: Coefficient de variation (std/mean).
        - solde_nb_negatif: Nombre de jours en decouvert.
        - solde_dernier_jour: Solde le plus recent.
        - solde_variation_moy: Variation moyenne jour a jour.
        - solde_tendance: Pente de regression lineaire.

    Args:
        df: DataFrame avec colonnes jour_*.

    Returns:
        DataFrame enrichi avec les 9 features statistiques.
    """
    jour_cols = sorted([col for col in df.columns if col.startswith("jour_")])

    agg = df[jour_cols].apply(
        lambda row: pd.Series(
            {
                "solde_moyen": row.mean(),
                "solde_min": row.min(),
                "solde_max": row.max(),
                "solde_std": row.std(),
                "solde_volatilite": (
                    row.std() / row.mean() if row.mean() != 0 else 0
                ),
                "solde_nb_negatif": (row < 0).sum(),
                "solde_dernier_jour": row.iloc[-1],
                "solde_variation_moy": row.diff().mean(),
                "solde_tendance": compute_slope(row.values),
            }
        ),
        axis=1,
    )

    return pd.concat([df, agg], axis=1)


def add_advanced_features(
    df: pd.DataFrame,
    use_lstm: bool = True,
    train_mode: bool = True,
    lstm_params: dict | None = None,
) -> pd.DataFrame:
    """Combine features statistiques classiques + features LSTM.

    Args:
        df: DataFrame avec colonnes jour_*.
        use_lstm: Si True, ajoute les features LSTM.
        train_mode: Si True, entraine le LSTM. Si False, charge modele existant.
        lstm_params: Dict de parametres LSTM:
            - latent_dim: Dimension espace latent (defaut: 16).
            - lstm_units: Unites LSTM (defaut: 32).
            - dropout_rate: Dropout (defaut: 0.2).
            - epochs: Epoques entrainement (defaut: 50).
            - batch_size: Taille batch (defaut: 32).
            - validation_split: Split validation (defaut: 0.2).

    Returns:
        DataFrame enrichi avec features statistiques + LSTM.
    """
    # 1. Features statistiques classiques
    df = add_balance_features(df)

    # 2. Features LSTM (optionnel)
    if use_lstm:

        default_params = {
            "latent_dim": 16,
            "lstm_units": 32,
            "dropout_rate": 0.2,
            "epochs": 50,
            "batch_size": 32,
            "validation_split": 0.2,
        }

        if lstm_params:
            default_params.update(lstm_params)

        model_params = {
            "latent_dim": default_params["latent_dim"],
            "lstm_units": default_params["lstm_units"],
            "dropout_rate": default_params["dropout_rate"],
        }

        train_params = {
            "epochs": default_params["epochs"],
            "batch_size": default_params["batch_size"],
            "validation_split": default_params["validation_split"],
        }

        if train_mode:
            lstm_encoder = LSTMEncoder(**model_params)
            lstm_features = lstm_encoder.fit_transform(
                df, **train_params, verbose=1
            )
            lstm_encoder.save()
        else:
            lstm_encoder = LSTMEncoder.load()
            lstm_features = lstm_encoder.transform(df)

        df = pd.concat([df, lstm_features], axis=1)

    return df
