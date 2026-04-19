import streamlit as st
import pandas as pd

from src.ingest import load_pharmacies, load_inventory
from src.normalize import normalize_inventory
from src.rules import filter_eligible_inventory
from src.database import (
    create_custom_thresholds_table,
    insert_custom_threshold,
    load_custom_thresholds,
    delete_custom_threshold,
)

st.set_page_config(page_title="Customise Low Stock", layout="wide")

st.title("Customise Low Stock Alerts")
st.write("Set custom low-stock thresholds for medicines at a specific pharmacy.")

# Ensure the table exists
create_custom_thresholds_table()

# Load source data
pharmacies = load_pharmacies("data/sample/pharmacies.csv")
inventory = load_inventory("data/sample/inventory.csv")
normalized_inventory = normalize_inventory(inventory)
eligible_inventory = filter_eligible_inventory(normalized_inventory, min_days_to_expiry=5)

# Merge pharmacy names
inventory_with_pharmacy = eligible_inventory.merge(pharmacies, on="pharmacy_id", how="left")

# Build pharmacy dropdown
pharmacy_options = pharmacies.sort_values("pharmacy_name")
selected_pharmacy_name = st.selectbox(
    "Select pharmacy",
    pharmacy_options["pharmacy_name"].tolist()
)

selected_pharmacy_row = pharmacy_options[pharmacy_options["pharmacy_name"] == selected_pharmacy_name].iloc[0]
selected_pharmacy_id = selected_pharmacy_row["pharmacy_id"]

# Filter medicines available for that pharmacy
pharmacy_inventory = inventory_with_pharmacy[
    inventory_with_pharmacy["pharmacy_id"] == selected_pharmacy_id
].copy()

medicine_options = pharmacy_inventory[["medicine_name", "medicine_code"]].drop_duplicates().sort_values("medicine_name")

if medicine_options.empty:
    st.warning("No medicines found for this pharmacy.")
else:
    medicine_display_options = [
        f"{row['medicine_name']} ({row['medicine_code']})"
        for _, row in medicine_options.iterrows()
    ]

    selected_medicine_display = st.selectbox(
        "Select medicine",
        medicine_display_options
    )

    selected_medicine_row = medicine_options.iloc[medicine_display_options.index(selected_medicine_display)]
    selected_medicine_name = selected_medicine_row["medicine_name"]
    selected_medicine_code = selected_medicine_row["medicine_code"]

    threshold_value = st.number_input(
        "Flag as low stock when units fall below:",
        min_value=1,
        value=10,
        step=1
    )

    if st.button("Save threshold"):
        insert_custom_threshold(
            pharmacy_id=selected_pharmacy_id,
            medicine_name=selected_medicine_name,
            medicine_code=selected_medicine_code,
            low_stock_threshold=int(threshold_value),
        )
        st.success(
            f"Saved: {selected_pharmacy_name} | {selected_medicine_name} will be flagged below {threshold_value} units."
        )

# Load thresholds after possible insert
thresholds_df = load_custom_thresholds()

st.subheader("Saved Threshold Rules")

if thresholds_df.empty:
    st.info("No custom thresholds saved yet.")
else:
    thresholds_with_names = thresholds_df.merge(pharmacies, on="pharmacy_id", how="left")
    st.dataframe(
        thresholds_with_names[
            ["pharmacy_name", "medicine_name", "medicine_code", "low_stock_threshold"]
        ],
        use_container_width=True
    )

# Show current flagged medicines
st.subheader("Currently Flagged as Low Stock")

if thresholds_df.empty:
    st.info("No low-stock checks available yet.")
else:
    flagged_df = eligible_inventory.merge(
        thresholds_df,
        on=["pharmacy_id", "medicine_name", "medicine_code"],
        how="inner"
    )

    flagged_df = flagged_df[flagged_df["quantity"] < flagged_df["low_stock_threshold"]].copy()
    flagged_df = flagged_df.merge(pharmacies, on="pharmacy_id", how="left")

    if flagged_df.empty:
        st.success("No medicines are currently below their custom low-stock threshold.")
    else:
        st.dataframe(
            flagged_df[
                [
                    "pharmacy_name",
                    "medicine_name",
                    "medicine_code",
                    "quantity",
                    "low_stock_threshold",
                    "expiry_date",
                    "days_to_expiry",
                ]
            ],
            use_container_width=True
        )

# Optional delete section
st.subheader("Delete a Threshold Rule")

if not thresholds_df.empty:
    thresholds_with_names = thresholds_df.merge(pharmacies, on="pharmacy_id", how="left")
    delete_options = [
        f"{row['pharmacy_name']} | {row['medicine_name']} ({row['medicine_code']}) | threshold {row['low_stock_threshold']}"
        for _, row in thresholds_with_names.iterrows()
    ]

    selected_delete = st.selectbox("Select a rule to delete", delete_options)

    if st.button("Delete selected rule"):
        selected_index = delete_options.index(selected_delete)
        selected_row = thresholds_with_names.iloc[selected_index]

        delete_custom_threshold(
            pharmacy_id=selected_row["pharmacy_id"],
            medicine_code=selected_row["medicine_code"],
        )

        st.success("Threshold rule deleted.")