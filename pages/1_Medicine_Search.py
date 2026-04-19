import streamlit as st

from src.auth import init_auth, require_role, get_current_user, logout_user
from src.ingest import load_pharmacies, load_inventory
from src.normalize import normalize_inventory
from src.rules import filter_eligible_inventory, split_surplus_shortage

init_auth()

if not st.session_state.get("authenticated", False):
    st.switch_page("pages/0_Login.py")

require_role(["super_admin", "manager", "pharmacist"])
user = get_current_user()

st.set_page_config(page_title="Medicine Search", layout="wide")

st.sidebar.success(f"Logged in as: {user['full_name']}")
st.sidebar.write(f"Role: {user['role']}")
if user["pharmacy_id"]:
    st.sidebar.write(f"Pharmacy: {user['pharmacy_id']}")

if st.sidebar.button("Logout"):
    logout_user()
    st.rerun()

st.title("Medicine Search")
st.write("Search for medicines currently in surplus across all pharmacies.")

# Load data
pharmacies = load_pharmacies("data/sample/pharmacies.csv")
inventory = load_inventory("data/sample/inventory.csv")

normalized_inventory = normalize_inventory(inventory)
eligible_inventory = filter_eligible_inventory(normalized_inventory, min_days_to_expiry=5)

surplus_df, _ = split_surplus_shortage(eligible_inventory)

surplus_with_pharmacy = surplus_df.merge(
    pharmacies,
    on="pharmacy_id",
    how="left"
)

search_term = st.text_input(
    "Search for a medicine in surplus",
    placeholder="e.g. Levothyroxine"
)

filtered_surplus = surplus_with_pharmacy.copy()

if search_term:
    filtered_surplus = filtered_surplus[
        filtered_surplus["medicine_name"].str.contains(search_term, case=False, na=False)
    ]

st.metric("Matching Surplus Records", len(filtered_surplus))

st.subheader("Pharmacies with This Medicine in Surplus")

if filtered_surplus.empty:
    st.info("No surplus medicines found for this search.")
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