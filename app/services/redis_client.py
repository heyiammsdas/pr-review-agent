import os
import redis
from dotenv import load_dotenv

load_dotenv()

def get_redis_connection():
    """
    Creates and returns a connection to the Redis server.
    Defaults to localhost:6379
    """
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", 6379))
    
    # decode_responses=True ensures we get strings instead of bytes
    return redis.Redis(host=host, port=port, decode_responses=True)
