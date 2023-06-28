import requests
import random
import json
import csv


# replace with your own YouTube API key
# 自分の YouTube の API key を入力
YOUTUBE_API_KEY = ''

# video ID for collecting comments
# VIDEO_ID = 'LweW1RypjD4'
VIDEO_ID = 'i1HnnMd6rFI'

# This function collects and returns all comments for the specific YouTube Video
# input 1: api_key (the api key required to communicate with YouTube)
# input 2: video_id (the video ID of the video we want to collect the comments from)
def collect_comments_from_youtube_video(api_key, video_id):

    # get the top-level comments
    comments = []
    comment_url = f'https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&maxResults=10&videoId={video_id}&textFormat=plainText&key={api_key}'

    while True:
        comment_info = requests.get(comment_url).json()
        comments.extend(comment_info['items'])
        next_page_token = comment_info.get('nextPageToken')
        comment_url = f'https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&maxResults=10&videoId={video_id}&textFormat=plainText&key={api_key}&pageToken={next_page_token}'

        if next_page_token is None:
            break

    # get the replies
    for comment in comments:
        comment_id = comment['id']
        reply_url = f'https://www.googleapis.com/youtube/v3/comments?part=snippet&parentId={comment_id}&textFormat=plainText&key={api_key}'
        reply_info = requests.get(reply_url).json()

        if 'items' in reply_info and len(reply_info['items']) > 0:
            comment['replies'] = reply_info['items']

    all_comments = {}
    # print all the comment details
    for comment in comments:
        all_comments[comment['id']] = {"video_id": video_id,
                                       "author_channel_url": comment['snippet']['topLevelComment']['snippet']['authorChannelUrl'],
                                       "author_display_name": comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                       "comment": comment['snippet']['topLevelComment']['snippet']['textDisplay'],
                                       "comment_id": comment['id'],
                                       "comment_date": comment['snippet']['topLevelComment']['snippet']['publishedAt']}
        print(
            f"Comment by {comment['snippet']['topLevelComment']['snippet']['authorDisplayName']}: {comment['snippet']['topLevelComment']['snippet']['textDisplay']}")
        if 'replies' in comment:
            for reply in comment['replies']:
                all_comments[reply['id']] = {"video_id": video_id,
                                            "author_channel_url": reply['snippet']['authorChannelUrl'],
                                            "author_display_name": reply['snippet']['authorDisplayName'], 
                                            "comment": reply['snippet']['textDisplay'], 
                                            "comment_id": reply['id'],
                                            "comment_date": comment['snippet']['topLevelComment']['snippet']['publishedAt']}
                print(
                    f"Reply by {reply['snippet']['authorDisplayName']}: {reply['snippet']['textDisplay']}")

    return all_comments


# Collect all the comments from target video and store in variable
all_comments = collect_comments_from_youtube_video(api_key=YOUTUBE_API_KEY, video_id=VIDEO_ID)

# Pick out ALL the comments that contain any of the secret words and store them in a list
SECRET_WORDS = ['thank you', 'Josh', 'why']
random.shuffle(SECRET_WORDS)

comments_with_secret_words = list()

for secret_word in SECRET_WORDS:

    # variable 'word' contains the current secret word
    # check all comments to collect ones that contain current secret word
    for key, value in all_comments.items():
        if secret_word in value['comment']:
            if value not in comments_with_secret_words:
                comments_with_secret_words.append(value)

# From the list of the comments containing secret words, choose 2 comments for each secret word

random.shuffle(comments_with_secret_words)

for secret_word in SECRET_WORDS:

    # Write all winners to file
    csv_file = f'{secret_word}.csv'

    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file, delimiter='\t')
                
        # Append the data to the CSV file
        writer.writerow([
            'video_id',
            'author_channel_url',
            'author_display_name',
            'comment',
            'comment_id',
            'comment_date'
            ])


    for comment in comments_with_secret_words:
        if secret_word in comment['comment']:
            with open(csv_file, 'a', newline='') as file:
                writer = csv.writer(file, delimiter='\t')
                
                # Append the data to the CSV file
                writer.writerow([
                    comment['video_id'],
                    comment['author_channel_url'],
                    comment['author_display_name'],
                    comment['comment'].replace("\n", " "),
                    comment['comment_id'],
                    comment['comment_date']
                    ])

print("Finish")