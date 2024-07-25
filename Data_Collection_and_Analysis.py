import requests
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import time
from datetime import datetime

# Function to fetch top stories
def fetch_top_stories():
    top_stories_url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
    response = requests.get(top_stories_url)
    return response.json()


# Function to fetch story details
def fetch_story_details(story_id):
    story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
    response = requests.get(story_url)
    return response.json()

# Function to fetch comment details
def fetch_comment_details(comment_id):
    comment_url = f'https://hacker-news.firebaseio.com/v0/item/{comment_id}.json'
    response = requests.get(comment_url)
    return response.json()


def run():
    # Fetch top stories
    top_stories = fetch_top_stories()

    # Fetch details for each top story and save to CSV
    with open('top_stories.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'title', 'url', 'score', 'author', 'time', 'comments_count'])

        for story_id in top_stories[:10]:  # Limiting to top 50 stories for this example
            story_details = fetch_story_details(story_id)
            writer.writerow([
                story_details.get('id', ''),
                story_details.get('title', ''),
                story_details.get('url', ''),
                story_details.get('score', 0),
                story_details.get('by', ''),
                datetime.fromtimestamp(story_details.get('time', 0)),
                len(story_details.get('kids', []))
            ])
            time.sleep(0.5)  # To avoid hitting API rate limits

    # Fetch and save comments for each top story
    with open('top_comments.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'author', 'text', 'time', 'parent'])

        for story_id in top_stories[:10]:  # Limiting to top 50 stories for this example
            story_details = fetch_story_details(story_id)
            comment_ids = story_details.get('kids', [])

            for comment_id in comment_ids[:5]:
                comment_details = fetch_comment_details(comment_id)
                writer.writerow([
                    comment_details.get('id', ''),
                    comment_details.get('by', ''),
                    comment_details.get('text', ''),
                    datetime.fromtimestamp(story_details.get('time', 0)),
                    comment_details.get('parent', '')
                ])
                time.sleep(0.5) # To avoid hitting API rate limits

    # Load the collected data
    stories_df = pd.read_csv('top_stories.csv')
    comments_df = pd.read_csv('top_comments.csv')

    # Analyze data
    average_score = stories_df['score'].mean()
    average_comments = stories_df['comments_count'].mean()

    # Save summary statistics
    with open('summary_statistics.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['average_score', 'average_comments'])
        writer.writerow([average_score, average_comments])

    # Plot analysis results
    plt.figure(figsize=(10, 5))

    # Plot average score of top stories
    plt.subplot(1, 2, 1)
    sns.histplot(stories_df['score'], kde=True)
    plt.title('Distribution of Scores')
    plt.xlabel('Score')
    plt.ylabel('Frequency')

    # Plot average number of comments per story
    plt.subplot(1, 2, 2)
    sns.histplot(stories_df['comments_count'], kde=True)
    plt.title('Distribution of Number of Comments')
    plt.xlabel('Number of Comments')
    plt.ylabel('Frequency')

    plt.tight_layout()
    plt.savefig('analysis_results.png')
    plt.show()

    #The ratio between the score and the number of comments
    plt.figure(figsize= (10, 6))
    sns.scatterplot (x='comments_count', y='score', data=stories_df)
    plt.title('Ratio of Score to Number of Comments')
    plt.xlabel('Number of Comments')
    plt.ylabel('Score to Comment Ratio')
    plt.savefig('Ratio of Score to Number of Comments.png')
    plt.show()
