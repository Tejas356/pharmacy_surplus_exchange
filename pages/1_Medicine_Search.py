import streamlit as st
import pandas as pd

from src.ingest import load_pharmacies, load_inventory
from src.normalize import normalize_inventory
from src.rules import filter_eligible_inventory, split_surplus_shortage

st.set_page_config(page_title="Medicine Search", layout="wide")

st.title("Medicine Search & Stock Explorer")
st.write("Search for a medicine and explore which pharmacies have shortages or surplus stock.")

# Load data
pharmacies = load_pharmacies("data/sample/pharmacies.csv")
inventory = load_inventory("data/sample/inventory.csv")

normalized_inventory = normalize_inventory(inventory)
eligible_inventory = filter_eligible_inventory(normalized_inventory)
surplus_df, shortage_df = split_surplus_shortage(eligible_inventory)

# Merge pharmacy names into inventory data
inventory_with_pharmacy = eligible_inventory.merge(
    pharmacies,
    on="pharmacy_id",
    how="left"
)

surplus_with_pharmacy = surplus_df.merge(
    pharmacies,
    on="pharmacy_id",
    how="left"
)

shortage_with_pharmacy = shortage_df.merge(
    pharmacies,
    on="pharmacy_id",
    how="left"
)

# Search box
search_term = st.text_input(
    "Search for a medicine",
    placeholder="e.g. Levothyroxine"
)

# Start with unfiltered copies
filtered_inventory = inventory_with_pharmacy.copy()
filtered_surplus = surplus_with_pharmacy.copy()
filtered_shortage = shortage_with_pharmacy.copy()

if search_term:
    filtered_inventory = filtered_inventory[
        filtered_inventory["medicine_name"].str.contains(search_term, case=False, na=False)
    ]
    filtered_surplus = filtered_surplus[
        filtered_surplus["medicine_name"].str.contains(search_term, case=False, na=False)
    ]
    filtered_shortage = filtered_shortage[
        filtered_shortage["medicine_name"].str.contains(search_term, case=False, na=False)
    ]

# Top metrics
col1, col2, col3 = st.columns(3)
col1.metric("Matching Records", len(filtered_inventory))
col2.metric("Short Supply Matches", len(filtered_shortage))
col3.metric("Surplus Matches", len(filtered_surplus))

# Table 1: pharmacies containing searched medicine
st.subheader("Pharmacies Containing This Medicine")

if filtered_inventory.empty:
    st.info("No matching medicines found.")
else:
    pharmacies_with_medicine = filtered_inventory[
        [
            "pharmacy_id",
            "pharmacy_name",
            "medicine_name",
            "medicine_code",
            "quantity",
            "status",
            "expiry_date",
            "days_to_expiry"
        ]
    ].sort_values(["medicine_name", "pharmacy_name"])

    st.dataframe(pharmacies_with_medicine, use_container_width=True)

# Table 2: medicines in short supply
st.subheader("Medicines in Short Supply")

if filtered_shortage.empty:
    st.info("No short supply records found for this search.")
else:
    shortage_table = filtered_shortage[
        [
            "pharmacy_id",
            "pharmacy_name",
            "medicine_name",
            "medicine_code",
            "quantity",
            "expiry_date",
            "days_to_expiry"
        ]
    ].sort_values(["medicine_name", "pharmacy_name"])

    st.dataframe(shortage_table, use_container_width=True)

# Table 3: medicines in surplus
st.subheader("Medicines in Surplus")

if filtered_surplus.empty:
    st.info("No surplus records found for this search.")
else:
    surplus_table = filtered_surplus[
        [
            "pharmacy_id",
            "pharmacy_name",
            "medicine_name",
            "medicine_code",
            "quantity",
            "expiry_date",
            "days_to_expiry"
        ]
    ].sort_values(["medicine_name", "pharmacy_name"])

    st.dataframe(surplus_table, use_container_width=True)

# Optional summary section
st.subheader("Summary by Medicine")

if filtered_inventory.empty:
    st.info("No summary available.")
else:
    summary = (
        filtered_inventory.groupby(["medicine_name", "status"], as_index=False)
        .agg(
            total_quantity=("quantity", "sum"),
            pharmacy_count=("pharmacy_id", "nunique")
        )
        .sort_values(["medicine_name", "status"])
    )

    st.dataframe(summary, use_container_width=True)