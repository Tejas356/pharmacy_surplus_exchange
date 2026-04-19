import streamlit as st
import pandas as pd

from src.ingest import load_pharmacies, load_inventory
from src.normalize import normalize_inventory
from src.rules import filter_eligible_inventory, split_surplus_shortage
from src.optimizer import optimize_transfers
from src.recommend import build_recommendation_messages


st.set_page_config(page_title="NHS Pharmacy Surplus Exchange", layout="wide")

st.title("NHS Pharmacy Surplus Exchange MVP")
st.write("Identify surplus medicine transfer opportunities between pharmacies.")

pharmacies = load_pharmacies("data/sample/pharmacies.csv")
inventory = load_inventory("data/sample/inventory.csv")

normalized_inventory = normalize_inventory(inventory)
eligible_inventory = filter_eligible_inventory(normalized_inventory)
surplus, shortage = split_surplus_shortage(eligible_inventory)
recommendations = optimize_transfers(pharmacies, surplus, shortage)
recommendations = build_recommendation_messages(recommendations)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Records", len(normalized_inventory))
col2.metric("Eligible Records", len(eligible_inventory))
col3.metric("Shortages", len(shortage))
col4.metric("Recommendations", len(recommendations))

st.subheader("Recommendations")
if recommendations.empty:
    st.warning("No transfer recommendations available.")
else:
    st.dataframe(
        recommendations[
            [
                "medicine_name",
                "source_pharmacy_id",
                "target_pharmacy_id",
                "transfer_qty",
                "distance_km",
                "estimated_savings",
                "recommendation_text",
            ]
        ],
        use_container_width=True
    )

    total_savings = recommendations["estimated_savings"].sum()
    total_transfers = recommendations["transfer_qty"].sum()

    col5, col6 = st.columns(2)
    col5.metric("Estimated Savings (£)", f"{total_savings:.2f}")
    col6.metric("Total Units Redistributed", int(total_transfers))

st.subheader("Eligible Inventory")
st.dataframe(eligible_inventory, use_container_width=True)

st.subheader("Pharmacies")
st.dataframe(pharmacies, use_container_width=True)