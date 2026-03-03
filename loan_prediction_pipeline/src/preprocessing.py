"""Nettoyage des donnees et creation de features de base."""

import pandas as pd


def preprocess(df):
    """Nettoie les donnees et cree des features calculees."""
    # Fill numeric NaNs
    df['count_simul'] = df['count_simul'].fillna(0)
    df['count_simul_mois_n_1'] = df['count_simul_mois_n_1'].fillna(0)
    df['age'] = df['age'].fillna(0)
    df['mensualite_immo'] = df['mensualite_immo'].fillna(0)

    # Convert jour_* columns (string with comma -> float)
    jour_cols = [c for c in df.columns if c.startswith('jour_')]
    df[jour_cols] = (
        df[jour_cols]
        .apply(lambda col: col.str.replace(",", ".", regex=False).astype(float))
        .fillna(0)
    )

    # Convert comma-formatted numeric columns
    df = df.assign(
        total_mensualite_actif=df['total_mensualite_actif']
            .str.replace(',', '.', regex=False).astype(float),
        duree_restante_ponderee=df['duree_restante_ponderee']
            .str.replace(',', '.', regex=False).astype(float),
    )

    # Derived features (second assign so first results are available)
    df = df.assign(
        total_mensualite_conso_immo=df['total_mensualite_actif'] + df['mensualite_immo'],
        taux_endettement=lambda x: x['total_mensualite_conso_immo'] / (1 + x['revenu_principal']),
    )

    return df
