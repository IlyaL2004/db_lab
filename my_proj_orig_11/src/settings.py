import os
from dotenv import load_dotenv

load_dotenv("env.env")

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

POOL_MIN_CONN = int(os.getenv("POOL_MIN_CONN", 1))
POOL_MAX_CONN = int(os.getenv("POOL_MAX_CONN", 10))



REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST"),
    "port": os.getenv("REDIS_PORT"),
}


REDIS_TOKEN_TTL = int(os.getenv("REDIS_TOKEN_TTL", 90))
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", 90))

POOL_MIN_CONN = int(os.getenv("POOL_MIN_CONN", 1))
POOL_MAX_CONN = int(os.getenv("POOL_MAX_CONN", 10))

