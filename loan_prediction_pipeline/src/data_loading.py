"""Chargement et fusion des donnees sources."""

import pandas as pd

from config.config import COMMON_FILES


def load_base(files: list[str], sep: str = ";") -> pd.DataFrame:
    """Charge et concatene plusieurs fichiers CSV.

    Args:
        files: Liste de chemins vers fichiers CSV.
        sep: Separateur CSV.

    Returns:
        DataFrame concatene.
    """
    parts = [pd.read_csv(f, sep=sep, low_memory=False) for f in files]
    base = pd.concat(parts, ignore_index=True)
    print(f"  {len(files)} fichiers charges : {base.shape[0]:,} lignes")
    return base


def merge_common(base: pd.DataFrame) -> pd.DataFrame:
    """Enrichit la base avec des fichiers communs via LEFT JOIN sur id_client.

    Args:
        base: DataFrame principal.

    Returns:
        DataFrame enrichi.
    """
    for name, (path, sep) in COMMON_FILES.items():
        df = pd.read_csv(path, sep=sep, low_memory=False)
        print(f"  Fusion avec {name} ({df.shape[0]:,} lignes)")
        base = base.merge(df, on="id_client", how="left")

    print(f"  Base enrichie : {base.shape[1]} colonnes")
    return base
