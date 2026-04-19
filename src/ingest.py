import pandas as pd


def load_pharmacies(filepath: str) -> pd.DataFrame:
    """Load pharmacies CSV."""
    return pd.read_csv(filepath)


def load_inventory(filepath: str) -> pd.DataFrame:
    """Load inventory CSV."""
    return pd.read_csv(filepath)