import streamlit as st

from src.ingest import load_pharmacies, load_inventory
from src.normalize import normalize_inventory
from src.rules import filter_eligible_inventory

st.set_page_config(page_title="Medicine Search", layout="wide")

st.title("Medicine Search")
st.write("Search for a medicine and see which pharmacies currently have it.")

# Load data
pharmacies = load_pharmacies("data/sample/pharmacies.csv")
inventory = load_inventory("data/sample/inventory.csv")

normalized_inventory = normalize_inventory(inventory)
eligible_inventory = filter_eligible_inventory(normalized_inventory)

inventory_with_pharmacy = eligible_inventory.merge(
    pharmacies,
    on="pharmacy_id",
    how="left"
)

search_term = st.text_input(
    "Search for a medicine",
    placeholder="e.g. Levothyroxine"
)

filtered_inventory = inventory_with_pharmacy.copy()

if search_term:
    filtered_inventory = filtered_inventory[
        filtered_inventory["medicine_name"].str.contains(search_term, case=False, na=False)
    ]

st.metric("Matching Records", len(filtered_inventory))

st.subheader("Pharmacies Containing This Medicine")

if filtered_inventory.empty:
    st.info("No matching medicines found.")
else:
    display_df = filtered_inventory[
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

    st.dataframe(display_df, use_container_width=True)