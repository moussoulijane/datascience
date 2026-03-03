"""Nettoyage des donnees et creation de features de base."""

import numpy as np
import pandas as pd


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les donnees et cree des features calculees.

    Etapes:
        1. Remplir les NaN numeriques par 0.
        2. Convertir les colonnes jour_* (string avec virgule -> float).
        3. Convertir les colonnes avec virgules (total_mensualite_actif, etc.).
        4. Creer des features calculees (taux endettement, etc.).

    Args:
        df: DataFrame brut.

    Returns:
        DataFrame nettoye avec features calculees.
    """
    print("\n  Preprocessing des donnees...")

    # 1. Remplir les NaN numeriques
    for col in ["count_simul", "count_simul_mois_n_1", "age", "mensualite_immo"]:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # 2. Convertir colonnes jour_* (string -> float)
    jour_cols = [c for c in df.columns if c.startswith("jour_")]
    print(f"   Conversion de {len(jour_cols)} colonnes temporelles...")

    for col in jour_cols:
        if df[col].dtype == object:
            df[col] = (
                df[col]
                .str.replace(",", ".", regex=False)
                .astype(float)
            )
        df[col] = df[col].fillna(0)

    # 3. Convertir colonnes avec virgules
    for col in ["total_mensualite_actif", "duree_restante_ponderee"]:
        if col in df.columns and df[col].dtype == object:
            df[col] = (
                df[col]
                .str.replace(",", ".", regex=False)
                .astype(float)
            )

    # 4. Creer features calculees
    if "total_mensualite_actif" in df.columns and "mensualite_immo" in df.columns:
        df["total_mensualite_conso_immo"] = (
            df["total_mensualite_actif"] + df["mensualite_immo"]
        )

    if "total_mensualite_conso_immo" in df.columns and "revenu_principal" in df.columns:
        df["taux_endettement"] = (
            df["total_mensualite_conso_immo"] / (1 + df["revenu_principal"])
        )

    print(f"  Preprocessing termine : {df.shape}")
    return df
