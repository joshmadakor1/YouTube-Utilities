import requests
import random
import os
import csv

# Replace with your own YouTube API key: https://console.cloud.google.com/apis/credentials
YOUTUBE_API_KEY = 'xxxxxxxxxxxxxxxxxxxxxx'

# Replace with the words viewers need to discover in the video
SECRET_WORDS = ['sandra', 'google', 'comptia', 'soc', 'cyber']

# Replace with the video ID of your target video: https://www.youtube.com/watch?v=CkkGGkr8_Wk
VIDEO_ID = 'CkkGGkr8_Wk'

# These are the headers for the CSV files containing the potential winners
CSV_HEADER = ['author_display_name', 'author_channel_url', 'comment', 'comment_link', 'comment_id', 'comment_date', 'video_id']

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

    # Create a dictionary to hold all top-level comments and replies
    all_comments = {}

    # print all the comment details
    for comment in comments:
        all_comments[comment['id']] = {
                                       "author_display_name": comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                       "author_channel_url": comment['snippet']['topLevelComment']['snippet']['authorChannelUrl'],
                                       "comment": comment['snippet']['topLevelComment']['snippet']['textDisplay'],
                                       "comment_id": comment['id'],
                                       "comment_date": comment['snippet']['topLevelComment']['snippet']['publishedAt'],
                                       "video_id": video_id
                                       }
        # If the top-level comment has replies in it
        if 'replies' in comment:
            for reply in comment['replies']:
                all_comments[reply['id']] = {
                                            "author_display_name": reply['snippet']['authorDisplayName'],
                                            "author_channel_url": reply['snippet']['authorChannelUrl'], 
                                            "comment": reply['snippet']['textDisplay'],
                                            "comment_id": reply['id'],
                                            "comment_date": comment['snippet']['topLevelComment']['snippet']['publishedAt'],
                                            "video_id": video_id}
                print(
                    f"Reply by {reply['snippet']['authorDisplayName']}: {reply['snippet']['textDisplay']}")

    return all_comments

def collect_comments_containing_secret_words(secret_words, all_comments):
    
    random.shuffle(secret_words)

    comments_with_secret_words = list()

    for secret_word in secret_words:
        for key, value in all_comments.items():
            if secret_word.lower() in value['comment'].lower():
                if value not in comments_with_secret_words:
                    comments_with_secret_words.append(value)
    
    return comments_with_secret_words

def delete_file_if_exists(filename):
    if os.path.isfile(filename):
        os.remove(filename)
        return True
    else:
        return False

def write_csv_header(filename, header):

    # Clean up old CSV file if it exists
    delete_file_if_exists(filename=filename)

    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file, delimiter='\t')
        
        # Append the data to the CSV file
        writer.writerow(header)

def remove_linebreaks(s):   
    # remove line breaks
    s = s.replace('\n', ' ').replace('\r', ' ')
    
    return s

def write_line_to_winner_file(filename, comment):
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file, delimiter='\t')
        
        # Replace all linebreaks with spaces.
        comment['comment'] = remove_linebreaks(comment['comment'])

        # Append the data to the CSV file
        writer.writerow([
            comment['author_display_name'],
            comment['author_channel_url'],
            comment['comment'],
            f"https://www.youtube.com/watch?v={comment['video_id']}&lc={comment['comment_id']}",
            comment['comment_id'],
            comment['comment_date'],
            comment['video_id']
            ])

def record_winners_of_each_secret_word_to_csv(secret_words, comments_with_secret_words):
    for secret_word in secret_words:

        # Write all winners to file
        filename = f'_{secret_word}.csv'

        # Create the CSV file and write the headers
        write_csv_header(filename=filename, header=CSV_HEADER)

        for comment in comments_with_secret_words:
            if secret_word.lower() in comment['comment'].lower():
                write_line_to_winner_file(filename=filename, comment=comment)

# Collect all the comments from target video and store in list
all_comments = collect_comments_from_youtube_video(api_key=YOUTUBE_API_KEY, video_id=VIDEO_ID)

# From all comments, select only the comments that contain secret words and store them in a list
comments_with_secret_words = collect_comments_containing_secret_words(secret_words=SECRET_WORDS, all_comments=all_comments)

# Shuffle the comments containing secret words (This is where the winners for each secret word will be determined)
random.shuffle(comments_with_secret_words)

# Write the comments containing secret words out to their own respective CSV Files
record_winners_of_each_secret_word_to_csv(secret_words=SECRET_WORDS, comments_with_secret_words=comments_with_secret_words)

print("fin")
