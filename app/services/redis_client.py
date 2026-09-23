import os
import redis
from dotenv import load_dotenv

load_dotenv()

def get_redis_connection():
    """
    Creates and returns a connection to the Redis server.
    """
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    # decode_responses=True ensures we get strings instead of bytes
    return redis.from_url(redis_url, decode_responses=True)
