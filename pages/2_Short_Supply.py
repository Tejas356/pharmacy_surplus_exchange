import streamlit as st

from src.ingest import load_pharmacies, load_inventory
from src.normalize import normalize_inventory
from src.rules import filter_eligible_inventory, split_surplus_shortage

st.set_page_config(page_title="Short Supply Explorer", layout="wide")

st.title("Short Supply Explorer")
st.write("Search medicines that are currently in short supply.")

# Load data
pharmacies = load_pharmacies("data/sample/pharmacies.csv")
inventory = load_inventory("data/sample/inventory.csv")

normalized_inventory = normalize_inventory(inventory)
eligible_inventory = filter_eligible_inventory(normalized_inventory)
_, shortage_df = split_surplus_shortage(eligible_inventory)

shortage_with_pharmacy = shortage_df.merge(
    pharmacies,
    on="pharmacy_id",
    how="left"
)

search_term = st.text_input(
    "Search short supply medicines",
    placeholder="e.g. Paracetamol"
)

filtered_shortage = shortage_with_pharmacy.copy()

if search_term:
    filtered_shortage = filtered_shortage[
        filtered_shortage["medicine_name"].str.contains(search_term, case=False, na=False)
    ]

st.metric("Short Supply Matches", len(filtered_shortage))

st.subheader("Medicines in Short Supply")

if filtered_shortage.empty:
    st.info("No short supply records found.")
else:
    display_df = filtered_shortage[
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

    st.dataframe(display_df, use_container_width=True)