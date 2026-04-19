import streamlit as st

from src.ingest import load_pharmacies, load_inventory
from src.normalize import normalize_inventory
from src.rules import filter_eligible_inventory, split_surplus_shortage
from src.auth import init_auth, require_role, get_current_user, logout_user

init_auth()
require_role(["super_admin", "manager"])
user = get_current_user()
st.sidebar.success(f"Logged in as: {user['full_name']}")
st.sidebar.write(f"Role: {user['role']}")
if user["pharmacy_id"]:
    st.sidebar.write(f"Pharmacy: {user['pharmacy_id']}")

if st.sidebar.button("Logout"):
    logout_user()
    st.rerun()

st.set_page_config(page_title="Surplus Explorer", layout="wide")

st.title("Surplus Explorer")
st.write("Search medicines that are currently in surplus.")

# Load data
pharmacies = load_pharmacies("data/sample/pharmacies.csv")
inventory = load_inventory("data/sample/inventory.csv")

normalized_inventory = normalize_inventory(inventory)
eligible_inventory = filter_eligible_inventory(normalized_inventory)

user = get_current_user()

# Restrict data based on role
if user["role"] != "super_admin" and user["pharmacy_id"]:
    eligible_inventory = eligible_inventory[
        eligible_inventory["pharmacy_id"] == user["pharmacy_id"]
    ]
surplus_df, _ = split_surplus_shortage(eligible_inventory)

surplus_with_pharmacy = surplus_df.merge(
    pharmacies,
    on="pharmacy_id",
    how="left"
)

search_term = st.text_input(
    "Search surplus medicines",
    placeholder="e.g. Ibuprofen"
)

filtered_surplus = surplus_with_pharmacy.copy()

if search_term:
    filtered_surplus = filtered_surplus[
        filtered_surplus["medicine_name"].str.contains(search_term, case=False, na=False)
    ]

st.metric("Surplus Matches", len(filtered_surplus))

st.subheader("Medicines in Surplus")

if filtered_surplus.empty:
    st.info("No surplus records found.")
else:
    display_df = filtered_surplus[
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