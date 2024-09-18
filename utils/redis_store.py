import os
import redis
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Redis configuration from environment variables
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_DECODE_RESPONSES = os.getenv('REDIS_DECODE_RESPONSES', 'True') == 'True'


class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # Initialize the Redis connection only once (singleton)
            cls._instance = redis.StrictRedis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=REDIS_DECODE_RESPONSES
            )
        return cls._instance


# Redis keys for storing hard and soft skills
REDIS_HARD_SKILLS_KEY = "hard_skills"
REDIS_SOFT_SKILLS_KEY = "soft_skills"


# Function to add hard and soft skills to Redis (only add if they don't exist)
def update_skills_in_redis(skills_json):
    # Get the Redis client instance
    redis_client = RedisClient()

    hard_skills = skills_json.get("hard_skills", [])
    soft_skills = skills_json.get("soft_skills", [])

    # Add hard skills to Redis set
    if hard_skills:
        redis_client.sadd(REDIS_HARD_SKILLS_KEY, *hard_skills)

    # Add soft skills to Redis set
    if soft_skills:
        redis_client.sadd(REDIS_SOFT_SKILLS_KEY, *soft_skills)


# Function to retrieve hard and soft skills from Redis
def get_skills_from_redis():
    # Get the Redis client instance
    redis_client = RedisClient()

    hard_skills = redis_client.smembers(REDIS_HARD_SKILLS_KEY)
    soft_skills = redis_client.smembers(REDIS_SOFT_SKILLS_KEY)

    return list(hard_skills), list(soft_skills)
