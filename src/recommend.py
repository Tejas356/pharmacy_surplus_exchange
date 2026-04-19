import pandas as pd


def build_recommendation_messages(df: pd.DataFrame) -> pd.DataFrame:
    """Add human-readable recommendation text."""
    if df.empty:
        return df

    df = df.copy()
    df["recommendation_text"] = df.apply(
        lambda row: (
            f"Move {int(row['transfer_qty'])} units of {row['medicine_name']} "
            f"from {row['source_pharmacy_id']} to {row['target_pharmacy_id']} "
            f"({row['distance_km']} km away). Estimated savings: £{row['estimated_savings']}."
        ),
        axis=1,
    )
    return df