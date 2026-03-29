import pickle
import pandas as pd

# Load saved bundle
with open("lightfm_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("lightfm_dataset.pkl", "rb") as f:
    dataset = pickle.load(f)

# Load items
items = pd.read_csv("dynamic_vpp_synth_dataset/items.csv")

# Get mappings
user_id_map, _, item_id_map, _ = dataset.mapping()
inv_item_map = {v: k for k, v in item_id_map.items()}


def recommend_replacement(user_id, detected_category):
    if user_id not in user_id_map:
        return "User not found."

    candidates = items[items["category"] == detected_category]

    if len(candidates) == 0:
        return "No items found for this category."

    user_index = user_id_map[user_id]
    item_indices = [
        item_id_map[i]
        for i in candidates["item_id"]
        if i in item_id_map
    ]

    if not item_indices:
        return "No valid items for ranking."

    scores = model.predict(user_index, item_indices)
    best_item_index = item_indices[scores.argmax()]
    best_item_id = inv_item_map[best_item_index]

    brand_name = items[items["item_id"] == best_item_id]["brand_name"].values[0]

    return brand_name


# CLI loop
while True:
    user_id = input("\nEnter user ID (or 'exit'): ")
    if user_id.lower() == "exit":
        break

    category = input("Enter detected object category: ")

    result = recommend_replacement(user_id, category)
    print("Recommended replacement:", result)
