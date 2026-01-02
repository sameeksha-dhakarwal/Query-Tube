import pandas as pd
import numpy as np
from tqdm import tqdm
import re

# -----------------------------
# PATHS (CHANGE IF NEEDED)
# -----------------------------
csv_path = r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\data\merged_cleaned_output.csv"
glove_path = r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\glove\glove.6B.300d.txt"   # <-- REPLACE with your actual GloVe file path

# -----------------------------
# Load the dataset
# -----------------------------
df = pd.read_csv(csv_path)
print("Loaded dataset with shape:", df.shape)

# -----------------------------
# Load GloVe 300d vectors
# -----------------------------
print("Loading GloVe embeddings... (This may take 1–2 minutes)")
glove = {}

with open(glove_path, "r", encoding="utf8") as f:
    for line in tqdm(f, desc="Reading GloVe"):
        values = line.split()
        word = values[0]
        vector = np.asarray(values[1:], dtype="float32")
        glove[word] = vector

print("Loaded GloVe word vectors:", len(glove))


# -----------------------------
# Function to clean & tokenize text
# -----------------------------
def tokenize(text):
    if pd.isna(text):
        return []
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)  # keep only letters/numbers/spaces
    tokens = text.split()
    return tokens

# -----------------------------
# Convert tokens to GloVe vectors & average them
# -----------------------------
def get_glove_embedding(text):
    tokens = tokenize(text)
    
    vectors = []
    for token in tokens:
        if token in glove:      # only use known words
            vectors.append(glove[token])
    
    if len(vectors) == 0:
        return np.zeros(300), 0   # no known tokens → return zero-vector
    
    vectors = np.array(vectors)
    avg_embedding = np.mean(vectors, axis=0)
    
    return avg_embedding, len(vectors)


combined_texts = []
embeddings_list = []
token_counts = []

print("Generating embeddings for each row...")

for i in tqdm(range(len(df)), desc="Embedding rows"):
    title = str(df.loc[i, "title"]) if "title" in df.columns else ""
    transcript = str(df.loc[i, "transcript"]) if "transcript" in df.columns else ""
    
    combined = title + " " + transcript
    combined_texts.append(combined)

    emb, token_count = get_glove_embedding(combined)
    embeddings_list.append(emb.tolist())        # store as list (for CSV)
    token_counts.append(token_count)

# Add new columns
df["combined_text"] = combined_texts
df["glove_embedding"] = embeddings_list
df["glove_token_count"] = token_counts

print("Embedding generation complete!")


# -----------------------------
# Save final CSV with embeddings
# -----------------------------

output_path = r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\data\embedded_output1.csv"   # you can change the name if you want

df.to_csv(output_path, index=False)

print("Saved successfully at:", output_path)

