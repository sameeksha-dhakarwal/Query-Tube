import os
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv
from tqdm import tqdm
from utils import ensure_dir, save_csv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

youtube = build("youtube", "v3", developerKey=API_KEY)

# ---------------------------------------------------
# Fetch channel details + uploads playlist ID
# ---------------------------------------------------
def get_channel_details():
    req = youtube.channels().list(
        part="snippet,statistics,contentDetails",
        id=CHANNEL_ID
    ).execute()

    c = req["items"][0]
    
    uploads_playlist = c["contentDetails"]["relatedPlaylists"]["uploads"]

    return {
        "channel_id": CHANNEL_ID,
        "channel_title": c["snippet"]["title"],
        "channel_description": c["snippet"]["description"],
        "channel_country": c["snippet"].get("country"),
        "channel_thumbnail": c["snippet"]["thumbnails"]["high"]["url"],
        "channel_subscriberCount": c["statistics"].get("subscriberCount"),
        "channel_videoCount": c["statistics"].get("videoCount"),
        "uploads_playlist": uploads_playlist
    }


# ---------------------------------------------------
# Fetch EXACT 50 videos from uploads playlist
# ---------------------------------------------------
def get_video_ids(playlist_id):
    video_ids = []
    next_page = None

    while len(video_ids) < 50:
        req = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page
        ).execute()

        for item in req["items"]:
            video_ids.append(item["contentDetails"]["videoId"])
            if len(video_ids) == 50:
                break

        next_page = req.get("nextPageToken")
        if not next_page:
            break

    return video_ids[:50]


# ---------------------------------------------------
# Fetch video metadata
# ---------------------------------------------------
def get_video_details(video_ids):
    result = []

    for i in tqdm(range(0, len(video_ids), 50)):
        chunk = video_ids[i:i+50]

        req = youtube.videos().list(
            part="snippet,contentDetails,statistics,status",
            id=",".join(chunk)
        ).execute()

        for v in req["items"]:
            sn = v["snippet"]
            st = v.get("statistics", {})
            cd = v.get("contentDetails", {})
            stt = v.get("status", {})

            result.append({
                "id": v["id"],
                "title": sn["title"],
                "description": sn.get("description"),
                "publishedAt": sn["publishedAt"],
                "tags": ", ".join(sn.get("tags", [])),
                "categoryId": sn.get("categoryId"),
                "defaultLanguage": sn.get("defaultLanguage"),
                "defaultAudioLanguage": sn.get("defaultAudioLanguage"),
                "thumbnail_default": sn["thumbnails"]["default"]["url"],
                "thumbnail_high": sn["thumbnails"]["high"]["url"],

                "duration": cd.get("duration"),

                "viewCount": st.get("viewCount"),
                "likeCount": st.get("likeCount"),
                "commentCount": st.get("commentCount"),

                "privacyStatus": stt.get("privacyStatus")
            })

    return result


# ---------------------------------------------------
# Main
# ---------------------------------------------------
def main():
    ensure_dir("../data")

    print("Fetching channel info...")
    channel = get_channel_details()

    print("Fetching EXACT 50 uploads...")
    video_ids = get_video_ids(channel["uploads_playlist"])
    print(f"Fetched {len(video_ids)} video IDs")

    print("Fetching metadata...")
    videos = get_video_details(video_ids)

    df = pd.DataFrame(videos)

    # attach channel metadata
    for k, v in channel.items():
        df[k] = v

    save_csv(df, "E:\Internship\Infosys Springboard\Infosys Task1\INFOSYS TASK1\data\Tech_with_Tim.csv")
    print("[✓] Saved: ../data/Tech_with_Tim.csv")


if __name__ == "__main__":
    main()
