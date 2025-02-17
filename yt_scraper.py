import requests
import re
import csv
import pandas as pd
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from datetime import datetime
import isodate

# YouTube Data API key
API_KEY = " "  # Replace with your API key
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Function to extract video ID or channel ID from URL
def extract_id_from_url(url):
    try:
        # Check if it's a video URL
        if "watch?v=" in url:
            match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)  
            if match:
                return match.group(1), "video"
        
        # Check if it's a channel URL
        elif "channel/" in url:
            match = re.search(r"channel/([a-zA-Z0-9_-]+)", url)
            if match:
                return match.group(1), "channel"
        
        # Check if it's a shortened video URL (e.g., youtu.be)
        elif "youtu.be/" in url:
            match = re.search(r"youtu\.be/([a-zA-Z0-9_-]{11})", url)
            if match:
                return match.group(1), "video"
            
        #check if @channel_name
        elif "/@" in url:
            match = re.search(r"/@([a-zA-Z0-9_-]+)", url)
            if match:
                channel_id = get_channel_id(API_KEY, match.group(1))
                return channel_id, "channel"
        
        # If no match, raise an error
        raise ValueError("Invalid YouTube URL or unsupported format")
    
    except Exception as e:
        raise ValueError(f"Error extracting ID from URL: {e}")

def get_channel_id(api_key, channel_username):
    try:
        _youtube = build('youtube', 'v3', developerKey=api_key)
        response = _youtube.search().list(
            part="snippet",
            q=channel_username,
            type="channel",
            maxResults=1
        ).execute()

        if 'items' in response and response['items']:
            channel_item = response['items'][0]
            return channel_item['snippet']['channelId']
        else:
            page_source = requests.get(f'https://www.youtube.com/{channel_username}').text
            channel_id_start_index = page_source.find('"channelId":"') + len('"channelId":"')
            channel_id_end_index = page_source.find('"', channel_id_start_index)
            channel_id = page_source[channel_id_start_index:channel_id_end_index]
            return channel_id
    except HttpError as e:
        if e.resp.status == 403 and b"quotaExceeded" in e.content:
           
            print("API Quota exhausted... Try using after 24 hours")
        else:
            raise Exception('Channel ID not found.')

def format_duration(duration):
    duration_obj = isodate.parse_duration(duration)
    hours = duration_obj.total_seconds() // 3600
    minutes = (duration_obj.total_seconds() % 3600) // 60
    seconds = duration_obj.total_seconds() % 60

    formatted_duration = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    return formatted_duration

def convert_datetime(published_at):
    datetime_obj = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
    return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
      
# Fetch video details via API
def fetch_video_details(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id={video_id}&key={API_KEY}"
    response = requests.get(url).json()
    if "items" in response and len(response["items"]) > 0:
        video = response["items"][0]
        snippet = video["snippet"]
        stats = video["statistics"]
        details = video["contentDetails"]
        return {
            "Video Title": snippet["title"],
            "Description": snippet["description"],
            "Channel Name": snippet["channelTitle"],
            "Upload Date": snippet["publishedAt"],
            "Duration": format_duration(details["duration"]),
            "Views": stats.get("viewCount", "N/A"),
            "Likes": stats.get("likeCount", "N/A"),
            "Dislikes": stats.get("dislikeCount", "N/A")
        }
    else:
        raise ValueError("Video not found")

# Fetch channel details via API
def fetch_channel_details(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={API_KEY}"
    response = requests.get(url).json()
    if "items" in response and len(response["items"]) > 0:
        channel = response["items"][0]
        snippet = channel["snippet"]
        stats = channel["statistics"]
        return {
            "Channel Name": snippet["title"],
            "Channel ID": channel_id,
            "Description": snippet["description"],
            "Total Views": stats.get("viewCount", "N/A"),
            "Subscribers": stats.get("subscriberCount", "N/A"),
            "Number of Videos": stats.get("videoCount", "N/A")
        }
    else:
        raise ValueError("Channel not found")



def scrape_comment_with_replies(video_id):
    List = [['Name', 'Comment','Likes', 'time', 'Reply Count']]
    data = youtube.commentThreads().list(part='snippet', videoId=video_id, maxResults='100', textFormat="plainText").execute()

    for i in data["items"]:

        name = i["snippet"]['topLevelComment']["snippet"]["authorDisplayName"]
        comment = i["snippet"]['topLevelComment']["snippet"]["textDisplay"]
        likes = i["snippet"]['topLevelComment']["snippet"]['likeCount']
        published_at = convert_datetime(i["snippet"]['topLevelComment']["snippet"]['publishedAt'])
        replies = i["snippet"]['totalReplyCount']

        List.append([name, comment, likes, published_at, replies])

        TotalReplyCount = i["snippet"]['totalReplyCount']

        if TotalReplyCount > 0:

            parent = i["snippet"]['topLevelComment']["id"]

            data2 = youtube.comments().list(part='snippet', maxResults='100', parentId=parent,
                                            textFormat="plainText").execute()

            for i in data2["items"]:
                name = i["snippet"]["authorDisplayName"]
                comment = i["snippet"]["textDisplay"]
                likes = i["snippet"]['likeCount']
                published_at = convert_datetime(i["snippet"]['publishedAt'])
                replies = ""

                List.append([name, comment, published_at, likes, replies])

    while ("nextPageToken" in data):

        data = youtube.commentThreads().list(part='snippet', videoId=video_id, pageToken=data["nextPageToken"],
                                             maxResults='100', textFormat="plainText").execute()

        for i in data["items"]:
            name = i["snippet"]['topLevelComment']["snippet"]["authorDisplayName"]
            comment = i["snippet"]['topLevelComment']["snippet"]["textDisplay"]
            likes = i["snippet"]['topLevelComment']["snippet"]['likeCount']
            published_at = convert_datetime(i["snippet"]['topLevelComment']["snippet"]['publishedAt'])
            replies = i["snippet"]['TotalReplyCount']

            List.append([name, comment, likes, published_at, replies])

            TotalReplyCount = i["snippet"]['TotalReplyCount']

            if TotalReplyCount > 0:

                parent = i["snippet"]['topLevelComment']["id"]

                data2 = youtube.comments().list(part='snippet', maxResults='100', parentId=parent,
                                                textFormat="plainText").execute()

                for i in data2["items"]:
                    name = i["snippet"]["authorDisplayName"]
                    comment = i["snippet"]["textDisplay"]
                    likes = i["snippet"]['likeCount']
                    published_at = convert_datetime(i["snippet"]['publishedAt'])
                    replies = ''

                    List.append([name, comment, likes, published_at, replies])
    
    #this conversion is not working.
    df = pd.DataFrame({'Name': [i[0] for i in List], 'Comment': [i[1] for i in List], 'Likes': [i[2] for i in List], 'Time': [i[3] for i in List],
                       'Reply Count': [i[4] for i in List]})
    df.to_csv(f"{video_id}_comments.csv", index=False)
    return f"Comments saved to {video_id}_comments.csv"

def fetch_video_comments(_youtube, video_id, max_results=10):
    try:
        comments_response = _youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_results
        ).execute()
    except HttpError as e:
        if e.resp.status == 403:
            print("API Quota exhausted... Try using after 24 hours")
            return {}
        else:
            raise

    comments = comments_response['items']
    
    video_comments = {}
    
    for idx, comment in enumerate(comments):
        comment_id = comment['snippet']['topLevelComment']['id']
        comment_text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
        comment_author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
        comment_published_at = convert_datetime(comment['snippet']['topLevelComment']['snippet']['publishedAt'])

        video_comments[f'Comment_{idx+1}'] = {
            'Comment_Id': comment_id,
            'Comment_Text': comment_text,
            'Comment_Author': comment_author,
            'Comment_PublishedAt': comment_published_at
        }
    
    return video_comments

def fetch_channel_data(api_key, channel_id):
    global channel_name
    
    try:
        _youtube = build('youtube', 'v3', developerKey=api_key)

        channel_response = _youtube.channels().list(part='snippet, statistics, contentDetails, status', id=channel_id).execute()
        channel_items = channel_response.get('items', [])
        
        if channel_items:
            channel_item = channel_items[0]
            channel_name = channel_item['snippet']['title']
            subscription_count = int(channel_item['statistics']['subscriberCount'])
            view_count = int(channel_item['statistics']['viewCount'])
            if channel_item['snippet']['description'] == '':
                channel_description = 'NA'
            else:
                channel_description = channel_item['snippet']['description']
            uploads_playlist_id = channel_item['contentDetails']['relatedPlaylists']['uploads']
            channel_status = channel_item['status']['privacyStatus']
        else:
            channel_name = 'NA'
            subscription_count = 0
            view_count = 0
            channel_description = 'NA'
            uploads_playlist_id = 'NA'
            channel_status = 'NA'
            
        playlists = []
        next_page_token = None

        while True:
            playlists_response = _youtube.playlists().list(
                part='snippet',
                channelId=channel_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            playlists.extend(playlists_response.get('items', []))

            next_page_token = playlists_response.get('nextPageToken')

            if next_page_token is None:
                break

        video_details = {}
        video_index = 1
        added_video_ids = set()

        for playlist in playlists:
            playlist_id = playlist['id']
            playlist_name = playlist['snippet']["title"]

            next_page_token = None
            videos = []

            while True:
                playlist_items_response = _youtube.playlistItems().list(
                    part='snippet',
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()

                videos.extend(playlist_items_response.get('items', []))

                next_page_token = playlist_items_response.get('nextPageToken')

                if next_page_token is None:
                    break

            for item in videos:
                video_id = item['snippet']['resourceId']['videoId']

                if video_id in added_video_ids:
                    continue

                video_response = _youtube.videos().list(
                    part='snippet,contentDetails,statistics',
                    id=video_id
                ).execute()
                video_items = video_response.get('items', [])

                if video_items:
                    video_snippet = video_items[0]['snippet']
                    video_stats = video_items[0]['statistics']
                    video_name = video_snippet['title']
                    video_description = video_snippet['description']
                    video_tags = video_snippet.get('tags', [])
                    published_at = convert_datetime(video_snippet['publishedAt'])
                    view_count = int(video_stats.get('viewCount', 0))
                    like_count = int(video_stats.get('likeCount', 0))
                    dislike_count = int(video_stats.get('dislikeCount', 0))
                    favorite_count = int(video_stats.get('favoriteCount', 0))
                    comment_count = int(video_stats.get('commentCount', 0))
                    duration = format_duration(video_items[0]['contentDetails']['duration'])
                    thumbnail = video_snippet['thumbnails']['default']['url']
                    caption_status = video_snippet.get('caption', 'Not available')
                else:
                    continue

                video_key = f'Video_{video_index}'
                video_comments = fetch_video_comments(_youtube, video_id)
                    
                video_details[video_key] = {
                    'Playlist_Id': playlist_id,
                    'Video_Id': video_id,
                    'Playlist_Name': playlist_name,
                    'Video_Name': video_name,
                    'Video_Description': video_description,
                    'Tags': video_tags,
                    'PublishedAt': published_at,
                    'View_Count': view_count,
                    'Like_Count': like_count,
                    'Dislike_Count': dislike_count,
                    'Favorite_Count': favorite_count,
                    'Comment_Count': comment_count,
                    'Duration': duration,
                    'Thumbnail': thumbnail,
                    'Caption_Status': caption_status,
                    'Comments': video_comments
                }

                added_video_ids.add(video_id)
                video_index += 1

        next_page_token = None
        remaining_videos = []

        while True:
            remaining_videos_response = _youtube.search().list(
                part='snippet',
                channelId=channel_id,
                maxResults=50,
                type='video',
                pageToken=next_page_token
            ).execute()

            remaining_videos.extend(remaining_videos_response.get('items', []))

            next_page_token = remaining_videos_response.get('nextPageToken')

            if next_page_token is None:
                break

        for item in remaining_videos:
            video_id = item['id']['videoId']

            if video_id in added_video_ids:
                continue

            video_response = _youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            ).execute()
            video_items = video_response.get('items', [])

            if video_items:
                video_snippet = video_items[0]['snippet']
                video_stats = video_items[0]['statistics']
                video_name = video_snippet['title']
                video_description = video_snippet['description']
                video_tags = video_snippet.get('tags', [])
                published_at = convert_datetime(video_snippet['publishedAt'])
                view_count = int(video_stats.get('viewCount', 0))
                like_count = int(video_stats.get('likeCount', 0))
                dislike_count = int(video_stats.get('dislikeCount', 0))
                favorite_count = int(video_stats.get('favoriteCount', 0))
                comment_count = int(video_stats.get('commentCount', 0))
                duration = format_duration(video_items[0]['contentDetails']['duration'])
                thumbnail = video_snippet['thumbnails']['default']['url']
                caption_status = video_snippet.get('caption', 'Not available')
            else:
                continue

            video_key = f'Video_{video_index}'
            video_comments = fetch_video_comments(_youtube, video_id)

            video_details[video_key] = {
                'Playlist_Id': 'NA',
                'Video_Id': video_id,
                'Playlist_Name': 'NA',
                'Video_Name': video_name,
                'Video_Description': video_description,
                'Tags': video_tags,
                'PublishedAt': published_at,
                'View_Count': view_count,
                'Like_Count': like_count,
                'Dislike_Count': dislike_count,
                'Favorite_Count': favorite_count,
                'Comment_Count': comment_count,
                'Duration': duration,
                'Thumbnail': thumbnail,
                'Caption_Status': caption_status,
                'Comments': video_comments
            }

            added_video_ids.add(video_id)
            video_index += 1

        channel_details = {
            'Channel_Id': channel_id,
            'Channel_Name': channel_name,
            'Uploads_Playlist_Id': uploads_playlist_id,
            'Subscription_Count': subscription_count,
            'Channel_Views': view_count,
            'Channel_Description': channel_description,
            'Channel_Status': channel_status
        }
        
        data = {
            '_id': channel_id,
            'Channel_Details': channel_details,
            'Video_Details': video_details
        }

        return data

    except HttpError as e:
        if e.resp.status == 403 and b"quotaExceeded" in e.content:
            print("API Quota exhausted... Try using after 24 hours")
        else:
            raise Exception('API request broke...Try again...')
        
# Main function to handle input and process accordingly
def main(url = None):
   
    if not url:
        url = input("Enter a YouTube video or channel URL: ").strip()
    print("------------------------------------------------------------------------------------------------")
    print("------------------------------------------------------------------------------------------------")
    try:
        id_or_url, url_type = extract_id_from_url(url)
        if url_type == "video":
            video_data = fetch_video_details(id_or_url)
            print("Video Details:")
            print(video_data)
            print("------------------------------------------------------------------------------------------------")
            print("------------------------------------------------------------------------------------------------")
            comment_data = scrape_comment_with_replies(id_or_url)
            print("Comment details:")
            print(comment_data)
            print("------------------------------------------------------------------------------------------------")
            print("------------------------------------------------------------------------------------------------")
        elif url_type == "channel":
            channel_data = fetch_channel_details(id_or_url)
            print("Channel Details:")
            print(channel_data)
            print("------------------------------------------------------------------------------------------------")
            print("------------------------------------------------------------------------------------------------")
            # save_to_csv(channel_data, channel_data["Channel Name"])
    except Exception as e:
        print("Error:", e)

# Run the program
if __name__ == "__main__":
    main()
