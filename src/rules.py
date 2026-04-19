import pandas as pd


def filter_eligible_inventory(df: pd.DataFrame, min_days_to_expiry: int = 30) -> pd.DataFrame:
    """Filter records based on simple eligibility rules."""
    df = df.copy()

    today = pd.Timestamp.today().normalize()
    df["days_to_expiry"] = (df["expiry_date"] - today).dt.days

    # Basic rules
    df = df[df["quantity"] > 0]
    df = df[df["days_to_expiry"] >= min_days_to_expiry]
    df = df[df["storage_type"] != "cold_chain"]

    return df


def split_surplus_shortage(df: pd.DataFrame):
    """Split eligible inventory into surplus and shortage groups."""
    surplus_df = df[df["status"] == "surplus"].copy()
    shortage_df = df[df["status"] == "shortage"].copy()
    return surplus_df, shortage_df