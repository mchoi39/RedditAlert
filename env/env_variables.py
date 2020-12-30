import praw

reddit = praw.Reddit(
    client_id="YOUR CLIENT ID",
    client_secret="YOUR CLIENT SECRET",
    user_agent="Anything",
    username="YOUR REDDIT USERNAME",
    password="YOUR REDDIT PASSWORD"
)
