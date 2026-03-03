"""Entrainement des 2 modeles CatBoost (LOW + HIGH revenu)."""

import os

import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from config.config import (
    CAT_FEATURES,
    FEATURE_COLS,
    MODEL_PARAMS,
    revenu_treshold,
)


def split_training_data(
    df: pd.DataFrame, revenu_treshold: int = revenu_treshold
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separe les donnees en 2 datasets selon le seuil de revenu.

    Strategie:
        - df_low: Tous les positifs (target=1) + negatifs avec revenu <= seuil.
        - df_high: Tous les positifs (target=1) + negatifs avec revenu > seuil.

    Les clients ayant souscrit (positifs) sont minoritaires et partages
    entre les 2 modeles pour maximiser le signal.

    Args:
        df: DataFrame complet avec colonnes target et revenu_principal.
        revenu_treshold: Seuil de revenu en MAD.

    Returns:
        Tuple (df_low, df_high).
    """
    df_pos = df[df["target"] == 1]
    df_neg_low = df[
        (df["target"] == 0) & (df["revenu_principal"] <= revenu_treshold)
    ]
    df_neg_high = df[
        (df["target"] == 0) & (df["revenu_principal"] > revenu_treshold)
    ]

    df_low = pd.concat([df_pos, df_neg_low])
    df_high = pd.concat([df_pos, df_neg_high])

    print(f"\n  Separation des donnees :")
    print(
        f"   LOW (<={revenu_treshold}) : {df_low.shape[0]:,} lignes "
        f"(souscripteurs={df_pos.shape[0]:,}, "
        f"non-souscripteurs={df_neg_low.shape[0]:,})"
    )
    print(
        f"   HIGH (>{revenu_treshold}) : {df_high.shape[0]:,} lignes "
        f"(souscripteurs={df_pos.shape[0]:,}, "
        f"non-souscripteurs={df_neg_high.shape[0]:,})"
    )

    return df_low, df_high


def train_two_models(
    df: pd.DataFrame,
    revenu_treshold: int = revenu_treshold,
    save_dir: str = "models",
) -> tuple[CatBoostClassifier, CatBoostClassifier]:
    """Entraine les 2 modeles CatBoost (LOW et HIGH revenu).

    Args:
        df: DataFrame complet avec features et target.
        revenu_treshold: Seuil de revenu en MAD.
        save_dir: Repertoire de sauvegarde des modeles.

    Returns:
        Tuple (model_low, model_high).
    """
    os.makedirs(save_dir, exist_ok=True)

    df_low, df_high = split_training_data(df, revenu_treshold)

    # Modele LOW
    print(f"\n{'=' * 70}")
    print(f"  ENTRAINEMENT MODELE LOW (revenu <= {revenu_treshold} MAD)")
    print(f"{'=' * 70}")

    model_low = _train_single_model(df_low, CAT_FEATURES, MODEL_PARAMS)
    model_low.save_model(
        os.path.join(save_dir, f"{revenu_treshold}_catboost_model_low.cbm")
    )

    feature_importance = model_low.get_feature_importance(prettified=True)
    importance_path = os.path.join(
        save_dir, f"{revenu_treshold}_catboost_model_low.csv"
    )
    feature_importance.to_csv(importance_path, index=False)
    print(f"  Feature importance -> {importance_path}")

    # Modele HIGH
    print(f"\n{'=' * 70}")
    print(f"  ENTRAINEMENT MODELE HIGH (revenu > {revenu_treshold} MAD)")
    print(f"{'=' * 70}")

    model_high = _train_single_model(df_high, CAT_FEATURES, MODEL_PARAMS)
    model_high.save_model(
        os.path.join(save_dir, f"{revenu_treshold}_catboost_model_high.cbm")
    )

    feature_importance = model_high.get_feature_importance(prettified=True)
    importance_path = os.path.join(
        save_dir, f"{revenu_treshold}_catboost_model_high.csv"
    )
    feature_importance.to_csv(importance_path, index=False)
    print(f"  Feature importance -> {importance_path}")

    return model_low, model_high


def _train_single_model(
    df: pd.DataFrame,
    cat_features: list[str],
    model_params: dict,
) -> CatBoostClassifier:
    """Entraine un modele CatBoost unique avec gestion robuste des features.

    Args:
        df: DataFrame avec features, target et id_client.
        cat_features: Liste des features categorielles.
        model_params: Parametres CatBoost.

    Returns:
        Modele CatBoost entraine.
    """
    # Filtrage des features disponibles
    available_features = [f for f in FEATURE_COLS if f in df.columns]
    missing_features = [f for f in FEATURE_COLS if f not in df.columns]

    if missing_features:
        print(f"\n  Features manquantes (ignorees) : {missing_features}")

    print(f"  Features utilisees : {len(available_features)}")

    X = df[available_features + ["id_client"]]
    y = df["target"]

    # Split train/test
    X_train_full, X_test_full, y_train, y_test = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=42
    )

    X_train = X_train_full.drop(columns=["id_client"])
    X_test = X_test_full.drop(columns=["id_client"])

    # Filtrage des cat_features valides
    valid_cat_features = [f for f in cat_features if f in X_train.columns]
    missing_cat_features = [
        f for f in cat_features if f not in X_train.columns
    ]

    if missing_cat_features:
        print(
            f"  Features categorielles manquantes (ignorees) : "
            f"{missing_cat_features}"
        )

    if valid_cat_features:
        print(f"  Features categorielles : {valid_cat_features}")
    else:
        print("  Aucune feature categorielle (modele tout numerique)")
        valid_cat_features = None

    # Gestion du desequilibre de classes (calculé sur la population complète)
    neg, pos = (y == 0).sum(), (y == 1).sum()
    scale_pos_weight = neg / pos

    print(f"\n  Balance des classes :")
    print(f"   Non-souscripteurs : {neg:,} | Souscripteurs : {pos:,}")
    print(f"   scale_pos_weight : {scale_pos_weight:.2f}")

    # Entrainement
    model = CatBoostClassifier(
        **model_params, scale_pos_weight=scale_pos_weight
    )

    print(f"\n  Entrainement CatBoost...")
    model.fit(
        X_train,
        y_train,
        cat_features=valid_cat_features,
        eval_set=(X_test, y_test),
        verbose=model_params.get("verbose", 100),
    )

    # Evaluation
    y_pred = model.predict(X_test)

    print(f"\n  Resultats sur test set ({len(y_test):,} echantillons) :")
    print(f"   Accuracy : {accuracy_score(y_test, y_pred):.4f}")
    print("\n  Classification Report :")
    print(classification_report(y_test, y_pred))
    print("\n  Confusion Matrix :")
    print(confusion_matrix(y_test, y_pred))

    return model
