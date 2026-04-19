import streamlit as st

from src.ingest import load_pharmacies, load_inventory
from src.normalize import normalize_inventory
from src.rules import filter_eligible_inventory
from src.database import (
    create_surplus_thresholds_table,
    insert_surplus_threshold,
    load_surplus_thresholds,
    delete_surplus_threshold,
)

st.set_page_config(page_title="Customise Surplus", layout="wide")

st.title("Customise Surplus Alerts")
st.write("Set custom surplus rules for medicines at a specific pharmacy.")

# Ensure DB table exists
create_surplus_thresholds_table()

# Load data
pharmacies = load_pharmacies("data/sample/pharmacies.csv")
inventory = load_inventory("data/sample/inventory.csv")
normalized_inventory = normalize_inventory(inventory)
eligible_inventory = filter_eligible_inventory(normalized_inventory, min_days_to_expiry=5)

inventory_with_pharmacy = eligible_inventory.merge(pharmacies, on="pharmacy_id", how="left")

# Select pharmacy
pharmacy_options = pharmacies.sort_values("pharmacy_name")
selected_pharmacy_name = st.selectbox(
    "Select pharmacy",
    pharmacy_options["pharmacy_name"].tolist()
)

selected_pharmacy_row = pharmacy_options[pharmacy_options["pharmacy_name"] == selected_pharmacy_name].iloc[0]
selected_pharmacy_id = selected_pharmacy_row["pharmacy_id"]

# Filter medicines for this pharmacy
pharmacy_inventory = inventory_with_pharmacy[
    inventory_with_pharmacy["pharmacy_id"] == selected_pharmacy_id
].copy()

medicine_options = pharmacy_inventory[
    ["medicine_name", "medicine_code", "quantity", "days_to_expiry"]
].drop_duplicates().sort_values("medicine_name")

if medicine_options.empty:
    st.warning("No medicines found for this pharmacy.")
else:
    medicine_display_options = [
        f"{row['medicine_name']} ({row['medicine_code']}) | Current qty: {row['quantity']} | Days to expiry: {row['days_to_expiry']}"
        for _, row in medicine_options.iterrows()
    ]

    selected_medicine_display = st.selectbox(
        "Select medicine",
        medicine_display_options
    )

    selected_medicine_row = medicine_options.iloc[
        medicine_display_options.index(selected_medicine_display)
    ]

    surplus_threshold = st.number_input(
        "Flag as surplus when units are above:",
        min_value=1,
        value=20,
        step=1
    )

    expiry_days_threshold = st.number_input(
        "Flag as surplus when days to expiry are less than or equal to:",
        min_value=1,
        value=30,
        step=1
    )

    if st.button("Save surplus rule"):
        insert_surplus_threshold(
            pharmacy_id=selected_pharmacy_id,
            medicine_name=selected_medicine_row["medicine_name"],
            medicine_code=selected_medicine_row["medicine_code"],
            surplus_threshold=int(surplus_threshold),
            expiry_days_threshold=int(expiry_days_threshold),
        )
        st.success(
            f"Saved surplus rule: {selected_pharmacy_name} | "
            f"{selected_medicine_row['medicine_name']} above {surplus_threshold} units "
            f"and <= {expiry_days_threshold} days to expiry."
        )

# Load saved surplus rules
surplus_rules_df = load_surplus_thresholds()

st.subheader("Saved Surplus Rules")

if surplus_rules_df.empty:
    st.info("No surplus rules saved yet.")
else:
    surplus_rules_with_names = surplus_rules_df.merge(pharmacies, on="pharmacy_id", how="left")
    st.dataframe(
        surplus_rules_with_names[
            [
                "pharmacy_name",
                "medicine_name",
                "medicine_code",
                "surplus_threshold",
                "expiry_days_threshold"
            ]
        ],
        use_container_width=True
    )

# Show currently flagged medicines
st.subheader("Currently Flagged as Surplus")

if surplus_rules_df.empty:
    st.info("No surplus checks available yet.")
else:
    flagged_surplus_df = eligible_inventory.merge(
        surplus_rules_df,
        on=["pharmacy_id", "medicine_name", "medicine_code"],
        how="inner"
    )

    flagged_surplus_df = flagged_surplus_df[
        (flagged_surplus_df["quantity"] > flagged_surplus_df["surplus_threshold"]) &
        (flagged_surplus_df["days_to_expiry"] <= flagged_surplus_df["expiry_days_threshold"])
    ].copy()

    flagged_surplus_df = flagged_surplus_df.merge(pharmacies, on="pharmacy_id", how="left")

    if flagged_surplus_df.empty:
        st.success("No medicines are currently flagged as surplus under the custom rules.")
    else:
        st.dataframe(
            flagged_surplus_df[
                [
                    "pharmacy_name",
                    "medicine_name",
                    "medicine_code",
                    "quantity",
                    "surplus_threshold",
                    "days_to_expiry",
                    "expiry_days_threshold",
                    "expiry_date",
                ]
            ],
            use_container_width=True
        )

# Delete rule section
st.subheader("Delete Surplus Rule")

if not surplus_rules_df.empty:
    surplus_rules_with_names = surplus_rules_df.merge(pharmacies, on="pharmacy_id", how="left")
    surplus_delete_options = [
        f"{row['pharmacy_name']} | {row['medicine_name']} ({row['medicine_code']}) | "
        f"surplus above {row['surplus_threshold']} and <= {row['expiry_days_threshold']} days"
        for _, row in surplus_rules_with_names.iterrows()
    ]

    selected_surplus_delete = st.selectbox(
        "Select surplus rule to delete",
        surplus_delete_options
    )

    if st.button("Delete surplus rule"):
        selected_index = surplus_delete_options.index(selected_surplus_delete)
        selected_row = surplus_rules_with_names.iloc[selected_index]

        delete_surplus_threshold(
            pharmacy_id=selected_row["pharmacy_id"],
            medicine_code=selected_row["medicine_code"],
        )
        st.success("Surplus rule deleted.")