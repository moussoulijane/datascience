"""LSTM Autoencoder pour extraction de features temporelles.

Architecture:
    Input (sequence_length, 1)
        -> LSTM(lstm_units, return_sequences=False)
        -> Dropout(dropout_rate)
        -> Dense(latent_dim, relu)          [ESPACE LATENT]
        -> Dense(lstm_units, relu)
        -> Dropout(dropout_rate)
        -> RepeatVector(sequence_length)
        -> LSTM(lstm_units, return_sequences=True)
        -> Dense(1)                         [RECONSTRUCTION]
"""

import os
import pickle

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Dense, Dropout, Input, LSTM, RepeatVector
from tensorflow.keras.models import Model


class LSTMEncoder:
    """LSTM Autoencoder pour extraire des representations latentes
    depuis des sequences temporelles de soldes bancaires.

    Args:
        latent_dim: Dimension de l'espace latent (nombre de features extraites).
        lstm_units: Nombre d'unites LSTM dans encoder/decoder.
        dropout_rate: Taux de dropout pour regularisation.
    """

    def __init__(
        self,
        latent_dim: int = 16,
        lstm_units: int = 32,
        dropout_rate: float = 0.2,
    ):
        self.latent_dim = latent_dim
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.model = None
        self.encoder_model = None
        self.scaler = StandardScaler()
        self.sequence_length = None

    def _build_autoencoder(self, sequence_length: int):
        """Construit l'architecture autoencoder complet + encoder seul."""
        input_seq = Input(shape=(sequence_length, 1), name="input_sequence")

        # Encoder
        encoded = LSTM(
            self.lstm_units, return_sequences=False, name="lstm_encoder"
        )(input_seq)
        encoded = Dropout(self.dropout_rate)(encoded)

        # Espace latent
        latent = Dense(
            self.latent_dim, activation="relu", name="latent_space"
        )(encoded)

        # Decoder
        decoded = Dense(self.lstm_units, activation="relu")(latent)
        decoded = Dropout(self.dropout_rate)(decoded)
        decoded = RepeatVector(sequence_length)(decoded)
        decoded = LSTM(self.lstm_units, return_sequences=True)(decoded)

        # Sortie (reconstruction)
        output_seq = Dense(1, name="output_sequence")(decoded)

        autoencoder = Model(
            inputs=input_seq, outputs=output_seq, name="lstm_autoencoder"
        )
        encoder = Model(
            inputs=input_seq, outputs=latent, name="lstm_encoder_only"
        )

        return autoencoder, encoder

    def fit(
        self,
        df: pd.DataFrame,
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.2,
        verbose: int = 1,
    ):
        """Entraine l'autoencoder sur les sequences temporelles.

        Args:
            df: DataFrame contenant les colonnes jour_*.
            epochs: Nombre d'epoques d'entrainement.
            batch_size: Taille des batchs.
            validation_split: Proportion pour validation.
            verbose: Niveau de verbosite.

        Returns:
            History object de Keras.
        """
        print("  Preparation des sequences temporelles...")
        X_sequences = self._prepare_sequences(df)  # (n, L)

        print("  Normalisation des donnees...")
        X_normalized = self.scaler.fit_transform(X_sequences).reshape(-1, self.sequence_length, 1)

        print("  Construction de l'architecture LSTM...")
        self.model, self.encoder_model = self._build_autoencoder(
            self.sequence_length
        )

        self.model.compile(optimizer="adam", loss="mse", metrics=["mae"])

        if verbose:
            self.model.summary()

        early_stop = EarlyStopping(
            monitor="val_loss",
            patience=10,
            restore_best_weights=True,
            verbose=1,
        )

        print("  Entrainement de l'autoencoder...")
        history = self.model.fit(
            X_normalized,
            X_normalized,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[early_stop],
            verbose=verbose,
        )

        print("  Entrainement termine!")
        return history

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extrait les features latentes depuis les sequences.

        Args:
            df: DataFrame contenant les colonnes jour_*.

        Returns:
            DataFrame avec colonnes lstm_feature_0 .. lstm_feature_N.

        Raises:
            ValueError: Si le modele n'a pas encore ete entraine.
        """
        if self.encoder_model is None:
            raise ValueError("Le modele doit etre entraine avant transform()!")

        X_sequences = self._prepare_sequences(df)  # (n, L)

        X_normalized = self.scaler.transform(X_sequences).reshape(-1, self.sequence_length, 1)

        latent_features = self.encoder_model.predict(X_normalized, verbose=0)

        feature_names = [
            f"lstm_feature_{i}" for i in range(self.latent_dim)
        ]
        return pd.DataFrame(
            latent_features, columns=feature_names, index=df.index
        )

    def fit_transform(
        self,
        df: pd.DataFrame,
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.2,
        verbose: int = 1,
    ) -> pd.DataFrame:
        """Entraine et transforme en une seule operation."""
        self.fit(df, epochs, batch_size, validation_split, verbose)
        return self.transform(df)

    def _prepare_sequences(self, df: pd.DataFrame) -> np.ndarray:
        """Extrait et organise les colonnes jour_* en sequences.

        Returns:
            np.array de shape (n_samples, sequence_length).

        Raises:
            ValueError: Si aucune colonne jour_* n'est trouvee.
        """
        jour_cols = sorted([c for c in df.columns if c.startswith("jour_")])

        if len(jour_cols) == 0:
            raise ValueError("Aucune colonne 'jour_*' trouvee!")

        self.sequence_length = len(jour_cols)

        sequences = df[jour_cols].values  # (n, L)
        return np.nan_to_num(sequences, nan=0.0)

    def save(self, directory: str = "models/lstm_encoder"):
        """Sauvegarde le modele, encoder, scaler et metadonnees."""
        os.makedirs(directory, exist_ok=True)

        self.model.save(os.path.join(directory, "autoencoder.h5"))
        self.encoder_model.save(os.path.join(directory, "encoder.h5"))

        with open(os.path.join(directory, "scaler.pkl"), "wb") as f:
            pickle.dump(self.scaler, f)

        metadata = {
            "latent_dim": self.latent_dim,
            "lstm_units": self.lstm_units,
            "dropout_rate": self.dropout_rate,
            "sequence_length": self.sequence_length,
        }
        with open(os.path.join(directory, "metadata.pkl"), "wb") as f:
            pickle.dump(metadata, f)

        print(f"  Modele LSTM sauvegarde dans {directory}")

    @classmethod
    def load(cls, directory: str = "models/lstm_encoder") -> "LSTMEncoder":
        """Charge un modele sauvegarde.

        Args:
            directory: Repertoire contenant les fichiers du modele.

        Returns:
            Instance LSTMEncoder prete pour transform().
        """
        with open(os.path.join(directory, "metadata.pkl"), "rb") as f:
            metadata = pickle.load(f)

        instance = cls(
            latent_dim=metadata["latent_dim"],
            lstm_units=metadata["lstm_units"],
            dropout_rate=metadata["dropout_rate"],
        )
        instance.sequence_length = metadata["sequence_length"]

        instance.model = tf.keras.models.load_model(
            os.path.join(directory, "autoencoder.h5"),
            compile=False,
        )
        instance.encoder_model = tf.keras.models.load_model(
            os.path.join(directory, "encoder.h5"),
            compile=False,
        )

        with open(os.path.join(directory, "scaler.pkl"), "rb") as f:
            instance.scaler = pickle.load(f)

        print(f"  Modele LSTM charge depuis {directory}")
        return instance
