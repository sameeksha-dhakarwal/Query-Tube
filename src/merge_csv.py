import pandas as pd

# Paths
CSV_VIDEOS = r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\data\Tech_with_Tim.csv"
CSV_TRANSCRIPTS = r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\data\twt_transcripts.csv"
CSV_OUTPUT = r"E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\data\twt_merged.csv"

def main():
    print("📌 Loading CSV files...")

    df_videos = pd.read_csv(CSV_VIDEOS)
    df_trans = pd.read_csv(CSV_TRANSCRIPTS)

    print(f"➡️ Videos: {df_videos.shape[0]} rows")
    print(f"➡️ Transcripts: {df_trans.shape[0]} rows")

    # Merge on "id" column
    df_merged = df_videos.merge(df_trans, on="id", how="left")

    # Save
    df_merged.to_csv(CSV_OUTPUT, index=False)

    print(f"✅ Merge complete! Saved to:\n{CSV_OUTPUT}")

if __name__ == "__main__":
    main()
