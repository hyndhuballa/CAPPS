print("Script started")

import pandas as pd
# import pickle
from lightfm import LightFM
from lightfm.data import Dataset
from lightfm.evaluation import precision_at_k

# Load
interactions = pd.read_csv("dynamic_vpp_synth_dataset/interactions.csv")
print("Loaded interactions:", len(interactions))

# Dataset
dataset = Dataset()
dataset.fit(
    users=interactions["user_id"].unique(),
    items=interactions["item_id"].unique()
)

(inter_mat, weights) = dataset.build_interactions(
    [(row["user_id"], row["item_id"], row["rating"])
     for _, row in interactions.iterrows()]
)

print("Building model...")

model = LightFM(loss="logistic", item_alpha=1e-6, user_alpha=1e-6)

print("Training...")
model.fit(inter_mat, sample_weight=weights, epochs=5, verbose=True)

print("Evaluating...")
precision = precision_at_k(model, inter_mat, k=5).mean()

print("Training complete.")
print("Precision@5:", precision)


# with open("lightfm_model.pkl", "wb") as f:
#     pickle.dump(model, f)

# # Save dataset (important for mappings)
# with open("lightfm_dataset.pkl", "wb") as f:
#     pickle.dump(dataset, f)

# print("Model and dataset saved successfully.")