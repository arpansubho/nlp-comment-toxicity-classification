from googleapiclient.discovery import build
import time

API_KEY = "AIzaSyALy02MP_Wt8FMu6DQEyuBsnUHWsPPf26Q"  # Replace with your actual API key

# Initialize the YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_live_chat_id(video_id):
    """
    Fetch the active live chat ID for a given YouTube video ID.
    Returns None if no live chat is available.
    """
    response = youtube.videos().list(
        part='liveStreamingDetails',
        id=video_id
    ).execute()

    items = response.get('items', [])
    if items:
        return items[0]['liveStreamingDetails'].get('activeLiveChatId')
    return None

def get_live_chat_messages(live_chat_id, next_token=None, max_messages=100):
    messages_collected = 0
    collected_messages = []

    response = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part='snippet,authorDetails',
        pageToken=next_token
    ).execute()

    for item in response['items']:
        author = item['authorDetails']['displayName']
        message = item['snippet'].get('displayMessage')
        timestamp = item['snippet']['publishedAt']

        if not message:
            continue  # Skip system messages

        collected_messages.append((timestamp, author, message))
        messages_collected += 1
        if messages_collected >= max_messages:
            break

    # ⏱ Respect YouTube's suggested polling interval
    time.sleep(response.get('pollingIntervalMillis', 2000) / 1000.0)

    return collected_messages, response.get('nextPageToken')