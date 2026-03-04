"""Chargement et fusion des donnees sources."""

import pandas as pd

from config.config import COMMON_FILES


def load_base(files, sep=";"):
    """Charge et concatene plusieurs fichiers CSV."""
    parts = [pd.read_csv(f, sep=sep, low_memory=False) for f in files]
    return pd.concat(parts)


def merge_common(base):
    """Enrichit la base avec des fichiers communs via LEFT JOIN sur id_client."""
    for _, (path, sep) in COMMON_FILES.items():
        df = pd.read_csv(path, sep=sep, low_memory=False)
        base = base.merge(df, on="id_client", how="left")
    return base
