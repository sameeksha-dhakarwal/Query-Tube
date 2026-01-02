import pandas as pd
import re

# Load CSVs
df_twt = pd.read_csv(r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\data\twt_merged.csv")
df_yt = pd.read_csv(r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\data\cleaned_youtube_data.csv")

# Merge
df_merged = pd.concat([df_yt, df_twt], ignore_index=True)

# ---------------- TEXT CLEANING ---------------- #
def clean_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)     # remove special chars
    text = re.sub(r'\s+', ' ', text).strip()
    return text

columns_to_clean = ['title', 'description', 'transcript']

for col in columns_to_clean:
    if col in df_merged.columns:
        df_merged[col] = df_merged[col].astype(str).apply(clean_text)

# ---------------- DURATION CLEANING ---------------- #
def duration_to_seconds(duration):
    if pd.isna(duration):
        return 0
    duration = str(duration).strip().lower()

    # Case 1: Normal HH:MM:SS or MM:SS
    if ":" in duration:
        parts = duration.split(":")
        parts = [int(p) if p.isdigit() else 0 for p in parts]
        if len(parts) == 3:     # HH:MM:SS
            return parts[0]*3600 + parts[1]*60 + parts[2]
        elif len(parts) == 2:   # MM:SS
            return parts[0]*60 + parts[1]

    # Case 2: "5m 20s" format
    minutes = re.search(r'(\d+)m', duration)
    seconds = re.search(r'(\d+)s', duration)
    total = 0
    if minutes:
        total += int(minutes.group(1)) * 60
    if seconds:
        total += int(seconds.group(1))
    if total > 0:
        return total

    # Case 3: ISO 8601 duration: PT1H2M10S
    iso = re.match(r'pt(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?', duration)
    if iso:
        h = int(iso.group(1)) if iso.group(1) else 0
        m = int(iso.group(2)) if iso.group(2) else 0
        s = int(iso.group(3)) if iso.group(3) else 0
        return h*3600 + m*60 + s

    return 0  # fallback if unknown format

# Apply if column exists
if 'duration' in df_merged.columns:
    df_merged['duration_seconds'] = df_merged['duration'].apply(duration_to_seconds)

# ---------------- SAVE OUTPUT ---------------- #
df_merged.to_csv(
    r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\data\merged_cleaned_output.csv",
    index=False
)

print("Merged + cleaned + duration converted successfully!")
