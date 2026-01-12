# run_posts_job.py
import os
import time
import requests
from models import db, Subreddit, Post

def run_posts_job():
    # Safety check: avoid duplicates
    # if Post.query.first():
    #     print("Posts already fetched")
    #     return

    # Requesting a new access token using a refresh token
    REDDIT_REFRESH_TOKEN = os.environ.get('REDDIT_REFRESH_TOKEN')
    USER_CREDENTIALS = os.environ.get('USER_CREDENTIALS')

    resp = requests.post(
        'https://www.reddit.com/api/v1/access_token',
        headers={
            'Authorization': f'Basic {USER_CREDENTIALS}',
            'User-Agent': 'macOS:BZNskmtfWcf3Ug:v0.0.1 (by /u/Wonderful_Force_8506)'
        },
        params={
            "grant_type": "refresh_token",
            "refresh_token": REDDIT_REFRESH_TOKEN
        }
    )

    data = resp.json()
    access_token = data.get("access_token")
    print("Access token:", access_token)

    if not access_token:
        print("❌ NO ACCESS TOKEN", data)
        return

    # Fetch one top post per subreddit
    subreddits = Subreddit.query.all()
    for sub in subreddits:
        subreddit_url = sub.url
        resp = requests.get(
            f"https://oauth.reddit.com/r/{subreddit_url}/top",
            headers={
                'Authorization': f'Bearer {access_token}',
                'User-Agent': 'macOS:BZNskmtfWcf3Ug:v0.0.1 (by /u/Wonderful_Force_8506)'
            },
            params={"limit": 1, "t": "week"}
        )

        print(subreddit_url, resp.status_code)

        data = resp.json()
        if not data['data']['children']:
            print(f"No posts found for /r/{subreddit_url}")
            continue

        post_data = data['data']['children'][0]['data']
        title = post_data['title']
        url = post_data['permalink']

        new_post = Post(
            url=url,
            title=title,
            subreddit_id=sub.id
        )

        db.session.add(new_post)
        db.session.commit()

        time.sleep(5)  # avoid Reddit rate limits

    print("✅ Posts fetched successfully")
