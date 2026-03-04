"""Predictions sur nouvelles donnees."""

import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

from config.config import FEATURE_COLS


def run_inference(
    df: pd.DataFrame,
    model,
    output_path: str,
    threshold: float = 0.5,
) -> pd.DataFrame:
    """Execute les predictions et sauvegarde les resultats.

    Args:
        df: DataFrame avec features (et optionnellement target).
        model: Modele CatBoost entraine.
        output_path: Chemin de sortie (.csv ou .parquet).
        threshold: Seuil de decision pour la classe positive (defaut 0.5).

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
    y_proba = model.predict_proba(X)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)

    # Construction du DataFrame de sortie
    output_data = {
        "id_client": ids,
        "target_pred": y_pred,
        "proba_pred": y_proba,
    }

    if y_true is not None:
        output_data["target_reel"] = y_true

    output_df = pd.concat(
        [pd.DataFrame(output_data), X.reset_index(drop=True)], axis=1
    )

    # Evaluation si labels disponibles
    if y_true is not None:
        print(f"\n  Performance sur donnees d'inference ({len(y_true):,} echantillons) :")
        print(f"  Seuil applique : {threshold:.2f}")
        print(f"\n  Distribution reelle  : {int((y_true == 0).sum()):,} negatifs | {int((y_true == 1).sum()):,} positifs")
        print(f"  Distribution predite : {int((y_pred == 0).sum()):,} negatifs | {int((y_pred == 1).sum()):,} positifs")
        print("\n  Classification Report :")
        print(classification_report(y_true, y_pred))
        print("  Confusion Matrix :")
        print(confusion_matrix(y_true, y_pred))

    # Sauvegarde
    if output_path.endswith(".parquet"):
        output_df.to_parquet(output_path, index=False)
    else:
        output_df.to_csv(output_path, index=False)

    print(f"\n  Predictions sauvegardees -> {output_path}")

    return output_df
