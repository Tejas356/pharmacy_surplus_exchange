from src.ingest import load_pharmacies, load_inventory
from src.normalize import normalize_inventory
from src.rules import filter_eligible_inventory, split_surplus_shortage
from src.database import save_dataframe
from src.optimizer import optimize_transfers
from src.recommend import build_recommendation_messages


def run_pipeline():
    pharmacies = load_pharmacies("data/sample/pharmacies.csv")
    inventory = load_inventory("data/sample/inventory.csv")

    normalized_inventory = normalize_inventory(inventory)
    eligible_inventory = filter_eligible_inventory(normalized_inventory)

    surplus, shortage = split_surplus_shortage(eligible_inventory)

    recommendations = optimize_transfers(pharmacies, surplus, shortage)
    recommendations = build_recommendation_messages(recommendations)

    save_dataframe(pharmacies, "pharmacies")
    save_dataframe(normalized_inventory, "normalized_inventory")
    save_dataframe(eligible_inventory, "eligible_inventory")
    save_dataframe(recommendations, "recommendations")

    print("Pipeline completed.")
    print(recommendations[["recommendation_text"]])


if __name__ == "__main__":
    run_pipeline()