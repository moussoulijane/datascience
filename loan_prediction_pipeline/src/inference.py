"""Predictions sur nouvelles donnees."""

import pandas as pd

from config.config import FEATURE_COLS


def run_inference(
    df: pd.DataFrame,
    model,
    output_path: str,
) -> pd.DataFrame:
    """Execute les predictions et sauvegarde les resultats.

    Args:
        df: DataFrame avec features (et optionnellement target).
        model: Modele CatBoost entraine.
        output_path: Chemin de sortie (.csv ou .parquet).

    Returns:
        DataFrame avec predictions et probabilites.
    """
    df = df.reset_index(drop=True).copy()

    # Preparer X
    available_features = [f for f in FEATURE_COLS if f in df.columns]
    X = df[available_features + ["id_client"]]
    ids = X["id_client"]
    X = X.drop(columns=["id_client"])

    y_true = df["target"] if "target" in df.columns else None

    # Predictions
    y_pred = model.predict(X)
    y_proba = model.predict_proba(X)[:, 1]

    # Construction du DataFrame de sortie
    output_data = {
        "id_client": ids,
        "target_pred": y_pred,
        "proba_souscription": y_proba,
    }

    if y_true is not None:
        output_data["target_reel"] = y_true

    output_df = pd.concat(
        [pd.DataFrame(output_data), X.reset_index(drop=True)], axis=1
    )

    # Sauvegarde
    if output_path.endswith(".parquet"):
        output_df.to_parquet(output_path, index=False)
    else:
        output_df.to_csv(output_path, index=False)

    print(f"  Resultats sauvegardes -> {output_path}")
    print(f"   {len(output_df):,} predictions")

    return output_df
