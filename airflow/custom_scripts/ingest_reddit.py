import pendulum
import praw
import json
import time
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "")
REDDIT_USERNAME = os.environ.get("REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.environ.get("REDDIT_PASSWORD", "")

def fetchObjects(mode, **kwargs):
    subreddit = kwargs.get("subreddit")
    logger.info(f"fetchObjects called with mode={mode}, subreddit={subreddit}")

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD
    )

    logger.info(f"Authenticated as: {reddit.user.me()}")

    results = []

    try:
        logger.info("Starting data fetch loop...")
        if mode == "submission":
            for submission in reddit.subreddit(subreddit).new(limit=None):
                created_utc = int(submission.created_utc)
                logger.debug(f"Submission: {submission.id}, created_utc: {created_utc}")
                obj = {
                    "id": submission.id,
                    "title": getattr(submission, "title", ""),
                    "author": str(submission.author) if submission.author else "",
                    "created_utc": created_utc,
                    "num_comments": getattr(submission, "num_comments", 0),
                    "total_awards_received": getattr(submission, "total_awards_received", 0)
                }
                results.append(obj)
        elif mode == "comment":
            for comment in reddit.subreddit(subreddit).comments(limit=None):
                created_utc = int(comment.created_utc)
                logger.debug(f"Comment: {comment.id}, created_utc: {created_utc}")
                obj = {
                    "id": comment.id,
                    "author": str(comment.author) if comment.author else "",
                    "created_utc": created_utc,
                    "body": getattr(comment, "body", ""),
                    "total_awards_received": getattr(comment, "total_awards_received", 0)
                }
                results.append(obj)
        else:
            logger.error("mode must be 'submission' or 'comment'")
            raise ValueError("mode must be 'submission' or 'comment'")
    except Exception as e:
        logger.error(f"Error occurred during data fetch: {e}", exc_info=True)

    logger.info(f"Returning {len(results)} objects from fetchObjects")
    return results

def extract_reddit_data(subreddit, mode, filepath, limit=100, start=None, end=None):
    logger.info(f"extract_reddit_data called with subreddit={subreddit}, mode={mode}, filepath={filepath}, limit={limit}")

    file = open(filepath, "w")
    total_written = 0

    logger.info("Calling fetchObjects...")
    objects = fetchObjects(mode, subreddit=subreddit)
    logger.info(f"Fetched {len(objects)} objects")

    for obj in objects:
        file.write(json.dumps(obj, sort_keys=True, ensure_ascii=True) + "\n")
        total_written += 1
        logger.info(f"Wrote object {obj['id']} to file (total_written={total_written})")
        if total_written >= limit:
            logger.info("Reached total_written limit, closing file and returning.")
            break

    file.close()
    logger.info(f"Finished writing {total_written} objects to {filepath}")

if __name__ == "__main__":
    extract_reddit_data(
        subreddit="stocks",
        mode="comment",
        filepath="test_output.json",
        limit=100
    )