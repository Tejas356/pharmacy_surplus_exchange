import pandas as pd


def normalize_inventory(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize inventory data."""
    df = df.copy()

    # Standardize column names
    df.columns = [col.strip().lower() for col in df.columns]

    # Clean medicine name
    df["medicine_name"] = df["medicine_name"].astype(str).str.strip().str.title()

    # Standardize status values
    df["status"] = df["status"].astype(str).str.strip().str.lower()

    # Standardize storage type
    df["storage_type"] = df["storage_type"].astype(str).str.strip().str.lower()

    # Numeric fields
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_cost"] = pd.to_numeric(df["unit_cost"], errors="coerce")

    # Dates
    df["expiry_date"] = pd.to_datetime(df["expiry_date"], errors="coerce")

    # Drop rows with critical missing fields
    required_cols = [
        "pharmacy_id",
        "medicine_name",
        "medicine_code",
        "quantity",
        "expiry_date",
        "status",
        "storage_type",
        "unit_cost",
    ]
    df = df.dropna(subset=required_cols)

    return df