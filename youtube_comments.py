import json
import os
import re
import streamlit as st
from googleapiclient.discovery import build
from concurrent.futures import ThreadPoolExecutor

API_KEYS_FILE = "api_keys.json"
HISTORY_FILE = "history.json"
COMMENTS_FILE = "comments.json"

def load_json(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}

def save_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file)

def extract_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_youtube_comments(api_key, video_id):
    youtube = build("youtube", "v3", developerKey=api_key)
    comments = []
    next_page_token = None

    while True:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            pageToken=next_page_token,
            maxResults=100
        )
        response = request.execute()

        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return comments

def get_video_title(api_key, video_id):
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.videos().list(part="snippet", id=video_id)
    response = request.execute()
    
    if "items" in response and len(response["items"]) > 0:
        return response["items"][0]["snippet"]["title"]
    return "Unknown Title"

def save_comments(video_ref_name, comments, comments_data):
    comments_data[video_ref_name] = comments
    save_json(COMMENTS_FILE, comments_data)

def fetch_and_display_comments(api_key, video_id, video_ref_name, comments_data):
    st.info("Fetching comments...")
    comments = get_youtube_comments(api_key, video_id)
    video_title = get_video_title(api_key, video_id)
    st.success(f"Fetched {len(comments)} comments from '{video_title}'")

    history = load_json(HISTORY_FILE)
    history[video_ref_name] = {"title": video_title, "video_id": video_id}
    save_json(HISTORY_FILE, history)
    save_comments(video_ref_name, comments, comments_data)

    comments_text = "\n".join(comments)
    st.text_area("Comments", value=comments_text, height=300)
    st.download_button(
        label="Download Comments as Text File",
        data=comments_text,
        file_name=f"{video_title}_comments.txt",
        mime="text/plain"
    )

def youtube_comments_feature():
    api_keys = load_json(API_KEYS_FILE)
    comments_data = load_json(COMMENTS_FILE)

    st.header("Fetch YouTube Comments")
    api_key_name = st.selectbox("Select an API Key", options=list(api_keys.keys()))
    api_key = api_keys.get(api_key_name, "")

    new_api_key_name = st.text_input("API Key Reference Name")
    new_api_key_value = st.text_input("Enter your YouTube API Key", value="")

    if st.button("Save New API Key"):
        if new_api_key_name and new_api_key_value:
            api_keys[new_api_key_name] = new_api_key_value
            save_json(API_KEYS_FILE, api_keys)
            st.success(f"API Key '{new_api_key_name}' saved")

    if st.button("Clear Selected API Key"):
        if api_key_name:
            del api_keys[api_key_name]
            save_json(API_KEYS_FILE, api_keys)
            st.success(f"API Key '{api_key_name}' cleared")

    video_url = st.text_input("Enter the YouTube Video Link")
    video_ref_name = st.text_input("Enter Reference Name for this Video")

    if st.button("Get Comments"):
        if not api_key or not video_url or not video_ref_name:
            st.error("Please enter API key, video link, and reference name for the video")
        else:
            video_id = extract_video_id(video_url)
            if not video_id:
                st.error("Invalid YouTube URL")
            else:
                fetch_and_display_comments(api_key, video_id, video_ref_name, comments_data)
