import pickle

with open("metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

print("Total records:", len(metadata))
print("Keys in first record:", metadata[0].keys())
print("\nSample record:\n", metadata[0])
