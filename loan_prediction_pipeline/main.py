"""Point d'entree principal du pipeline ML Credit Consommation.

Usage:
    Entrainement (sans LSTM):
        python main.py train

    Entrainement (avec LSTM):
        python main.py train --use_lstm --lstm_dim 16 --lstm_epochs 50

    Inference:
        python main.py infer --output outputs/predictions.csv

    Inference (avec LSTM):
        python main.py infer --use_lstm --output outputs/predictions.csv
"""

import argparse
import os

import pandas as pd
from catboost import CatBoostClassifier

from config.config import INFER_FILES, TRAIN_FILES
from src.data_loading import load_base, merge_common
from src.feature_engineering import add_advanced_features
from src.inference import run_inference
from src.preprocessing import preprocess
from src.training import split_training_data, train_two_models

# Chemins des caches Parquet
PROCESSED_PATH = "data/processed/modeling_base.parquet"
PROCESSED_INFER_PATH = "data/processed/inference_base.parquet"


def run_train(args):
    """Execute le mode entrainement."""
    print("\n" + "=" * 70)
    print("  MODE ENTRAINEMENT")
    print("=" * 70)

    if os.path.exists(PROCESSED_PATH):
        print(f"\n  Chargement du cache : {PROCESSED_PATH}")
        df = pd.read_parquet(PROCESSED_PATH)
    else:
        print("\n  Construction de la base de modelisation...")

        # 1. Chargement
        print("\n[1/4] Chargement des donnees...")
        df = load_base(TRAIN_FILES)

        # 2. Enrichissement
        print("\n[2/4] Enrichissement avec fichiers communs...")
        df = merge_common(df)

        # 3. Preprocessing
        print("\n[3/4] Preprocessing...")
        df = preprocess(df)

        # 4. Feature Engineering
        print("\n[4/4] Feature Engineering...")
        if args.use_lstm:
            print(
                f"  LSTM active (dim={args.lstm_dim}, "
                f"epochs={args.lstm_epochs})"
            )
            lstm_params = {
                "latent_dim": args.lstm_dim,
                "epochs": args.lstm_epochs,
                "batch_size": 32,
                "validation_split": 0.2,
            }
            df = add_advanced_features(
                df, use_lstm=True, train_mode=True, lstm_params=lstm_params
            )
        else:
            print("  Features statistiques uniquement (sans LSTM)")
            df = add_advanced_features(
                df, use_lstm=False, train_mode=True
            )

        # Sauvegarde du cache
        os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)
        df.to_parquet(PROCESSED_PATH, index=False)
        print(f"\n  Cache sauvegarde -> {PROCESSED_PATH}")

    # Entrainement des 2 modeles
    print("\n" + "=" * 70)
    print("  ENTRAINEMENT DES MODELES CATBOOST")
    print("=" * 70)
    model_low, model_high = train_two_models(
        df, revenu_treshold=args.revenu_treshold, save_dir="models"
    )

    print("\n" + "=" * 70)
    print("  ENTRAINEMENT TERMINE")
    print("=" * 70)
    print("  Modeles sauvegardes dans : models/")


def run_infer(args):
    """Execute le mode inference."""
    print("\n" + "=" * 70)
    print("  MODE INFERENCE")
    print("=" * 70)

    if os.path.exists(PROCESSED_INFER_PATH):
        print(f"\n  Chargement du cache : {PROCESSED_INFER_PATH}")
        df = pd.read_parquet(PROCESSED_INFER_PATH)
    else:
        print("\n  Construction de la base d'inference...")

        # 1. Chargement
        print("\n[1/4] Chargement des donnees...")
        df = load_base(INFER_FILES)

        # 2. Enrichissement
        print("\n[2/4] Enrichissement...")
        df = merge_common(df)

        # 3. Preprocessing
        print("\n[3/4] Preprocessing...")
        df = preprocess(df)

        # 4. Feature Engineering
        print("\n[4/4] Feature Engineering...")
        if args.use_lstm:
            print("  Chargement du LSTM Encoder pre-entraine")
            df = add_advanced_features(
                df, use_lstm=True, train_mode=False
            )
        else:
            print("  Features statistiques uniquement")
            df = add_advanced_features(
                df, use_lstm=False, train_mode=False
            )

        # Sauvegarde du cache
        os.makedirs(os.path.dirname(PROCESSED_INFER_PATH), exist_ok=True)
        df.to_parquet(PROCESSED_INFER_PATH, index=False)
        print(f"\n  Cache sauvegarde -> {PROCESSED_INFER_PATH}")

    # Separation LOW/HIGH
    print("\n  Separation des donnees selon revenu...")
    df_low, df_high = split_training_data(
        df, revenu_treshold=args.revenu_treshold
    )

    # Chargement des modeles
    print("\n  Chargement des modeles...")
    model_low = CatBoostClassifier()
    model_low.load_model(
        f"models/{args.revenu_treshold}_catboost_model_low.cbm"
    )
    print("    Modele LOW charge")

    model_high = CatBoostClassifier()
    model_high.load_model(
        f"models/{args.revenu_treshold}_catboost_model_high.cbm"
    )
    print("    Modele HIGH charge")

    # Inferences
    print("\n  Execution des predictions...")

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    out_low = args.output.replace(".csv", "_low.parquet")
    run_inference(df_low, model_low, out_low)

    out_high = args.output.replace(".csv", "_high.parquet")
    run_inference(df_high, model_high, out_high)

    print("\n" + "=" * 70)
    print("  INFERENCE TERMINEE")
    print("=" * 70)
    print(f"  Resultats dans : {args.output.replace('.csv', '_*.parquet')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pipeline ML Credit Consommation"
    )
    parser.add_argument(
        "mode",
        choices=["train", "infer"],
        help="Mode d'execution : train ou infer",
    )
    parser.add_argument(
        "--output",
        default="outputs/inference_results.csv",
        help="Chemin de sortie pour inference",
    )
    parser.add_argument(
        "--revenu_treshold",
        type=int,
        default=7000,
        help="Seuil de revenu pour separation des modeles (MAD)",
    )
    parser.add_argument(
        "--use_lstm",
        action="store_true",
        help="Utiliser LSTM Autoencoder pour features temporelles",
    )
    parser.add_argument(
        "--lstm_dim",
        type=int,
        default=16,
        help="Dimension de l'espace latent LSTM",
    )
    parser.add_argument(
        "--lstm_epochs",
        type=int,
        default=50,
        help="Nombre d'epoques d'entrainement LSTM",
    )

    args = parser.parse_args()

    if args.mode == "train":
        run_train(args)
    elif args.mode == "infer":
        run_infer(args)
