import pandas as pd
from src.utils import calculate_distance_km


def optimize_transfers(pharmacies_df: pd.DataFrame, surplus_df: pd.DataFrame, shortage_df: pd.DataFrame) -> pd.DataFrame:
    """Match shortage records to surplus records and recommend transfers."""
    recommendations = []

    pharmacy_lookup = pharmacies_df.set_index("pharmacy_id").to_dict("index")

    for _, shortage in shortage_df.iterrows():
        target_id = shortage["pharmacy_id"]
        medicine_code = shortage["medicine_code"]
        required_qty = shortage["quantity"]

        eligible_sources = surplus_df[
            (surplus_df["medicine_code"] == medicine_code) &
            (surplus_df["pharmacy_id"] != target_id)
        ].copy()

        if eligible_sources.empty:
            continue

        target_pharmacy = pharmacy_lookup.get(target_id)
        if not target_pharmacy:
            continue

        scored_sources = []

        for _, source in eligible_sources.iterrows():
            source_id = source["pharmacy_id"]
            source_pharmacy = pharmacy_lookup.get(source_id)
            if not source_pharmacy:
                continue

            distance_km = calculate_distance_km(
                source_pharmacy["latitude"],
                source_pharmacy["longitude"],
                target_pharmacy["latitude"],
                target_pharmacy["longitude"],
            )

            days_to_expiry = source.get("days_to_expiry", 999)
            available_qty = source["quantity"]

            # Lower score is better
            score = distance_km + (days_to_expiry / 100)

            scored_sources.append({
                "source_pharmacy_id": source_id,
                "target_pharmacy_id": target_id,
                "medicine_code": medicine_code,
                "medicine_name": source["medicine_name"],
                "available_qty": available_qty,
                "required_qty": required_qty,
                "transfer_qty": min(available_qty, required_qty),
                "distance_km": round(distance_km, 2),
                "days_to_expiry": int(days_to_expiry),
                "unit_cost": source["unit_cost"],
                "score": round(score, 2),
            })

        if not scored_sources:
            continue

        best = sorted(scored_sources, key=lambda x: x["score"])[0]
        best["estimated_savings"] = round(best["transfer_qty"] * best["unit_cost"], 2)
        recommendations.append(best)

    return pd.DataFrame(recommendations)