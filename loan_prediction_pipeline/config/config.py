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

# Modele LOW : ratio de classe ~143:1, necessite une regularisation forte
# et un scale_pos_weight plafonne pour eviter la sur-correction.
MODEL_PARAMS_LOW = {
    "iterations": 1000,
    "learning_rate": 0.02,
    "depth": 5,
    "loss_function": "Logloss",
    "eval_metric": "F1",
    "random_seed": 42,
    "verbose": 100,
    "early_stopping_rounds": 80,
    "l2_leaf_reg": 10,
    "min_data_in_leaf": 100,
    "subsample": 0.8,
    "colsample_bylevel": 0.8,
}

# Modele HIGH : ratio de classe ~60:1, sur-ajustement tres rapide avec lr=0.05.
# Learning rate reduit + regularisation pour permettre plus d'iterations.
MODEL_PARAMS_HIGH = {
    "iterations": 1000,
    "learning_rate": 0.01,
    "depth": 4,
    "loss_function": "Logloss",
    "eval_metric": "F1",
    "random_seed": 42,
    "verbose": 100,
    "early_stopping_rounds": 100,
    "l2_leaf_reg": 15,
    "min_data_in_leaf": 50,
    "subsample": 0.8,
    "colsample_bylevel": 0.7,
}

# Plafond du scale_pos_weight pour eviter la sur-correction due au
# desequilibre extreme des classes (ex : ratio brut 143:1 -> plafonne a 20).
SCALE_POS_WEIGHT_MAX = 20.0
