"""Configuration centrale du pipeline de prediction credit consommation."""

# =============================================================================
# Fichiers de donnees
# =============================================================================

TRAIN_FILES = [
    "data/raw/train_base_part1.csv",
    "data/raw/train_base_part2.csv",
    "data/raw/train_base_part3.csv",
]

INFER_FILES = [
    "data/raw/inference_data.csv",
]

COMMON_FILES = {
    "demographics": ("data/raw/client_demographics.csv", ";"),
    "financials": ("data/raw/client_financials.csv", ";"),
}

# =============================================================================
# Seuil de revenu pour separation des modeles
# =============================================================================

revenu_treshold = 7000  # MAD

# =============================================================================
# Features categorielles
# =============================================================================

CAT_FEATURES = [
    "type_revenu",
    "segment",
]

# =============================================================================
# Features LSTM (generees si --use_lstm)
# =============================================================================

LSTM_FEATURES = [f"lstm_feature_{i}" for i in range(16)]

# =============================================================================
# Features utilisees par les modeles CatBoost
# =============================================================================

FEATURE_COLS = [
    # Features de base
    "count_simul",
    "count_simul_mois_n_1",
    "age",
    "mensualite_immo",
    "total_mensualite_actif",
    "duree_restante_ponderee",
    "revenu_principal",
    # Features categorielles
    "type_revenu",
    "segment",
    # Features calculees dans preprocessing
    "total_mensualite_conso_immo",
    "taux_endettement",
    # Features statistiques des soldes (feature_engineering)
    "solde_moyen",
    "solde_min",
    "solde_max",
    "solde_std",
    "solde_volatilite",
    "solde_nb_negatif",
    "solde_dernier_jour",
    "solde_variation_moy",
    "solde_tendance",
    # Features LSTM (ajoutees si --use_lstm)
    *LSTM_FEATURES,
]

# =============================================================================
# Parametres CatBoost
# =============================================================================

MODEL_PARAMS = {
    "iterations": 1000,
    "learning_rate": 0.05,
    "depth": 6,
    "loss_function": "Logloss",
    "eval_metric": "AUC",
    "random_seed": 42,
    "verbose": 100,
    "early_stopping_rounds": 50,
}
