import bcrypt
import jwt
import datetime
import psycopg2
import psycopg2.extras
from settings import DB_CONFIG, REDIS_CONFIG, REDIS_TOKEN_TTL
import redis
import logging

logger = logging.getLogger(__name__)

SECRET_KEY = "your_secret_key"


def clean_expired_tokens():
    pass

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_jwt(user_id: int, role: str) -> str:
    from settings import JWT_EXPIRE_HOURS

    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRE_HOURS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    try:
        r = redis.Redis(**REDIS_CONFIG)
        r.setex(f"token:{token}", REDIS_TOKEN_TTL, str(user_id))
        logger.info(f"Токен сохранен в Redis для пользователя {user_id}")
    except Exception as e:
        logger.error(f"Ошибка Redis: {str(e)}")
        raise

    return token


def revoke_token(token: str):
    try:
        r = redis.Redis(**REDIS_CONFIG)
        deleted = r.delete(f"token:{token}")
        logger.info(f"Токен удален: {deleted}")
    except Exception as e:
        logger.error(f"Ошибка удаления токена: {str(e)}")


def verify_token(token: str) -> bool:
    try:
        r = redis.Redis(**REDIS_CONFIG)
        exists = r.exists(f"token:{token}")
        logger.debug(f"Проверка токена: {exists}")
        return exists == 1
    except Exception as e:
        logger.error(f"Ошибка проверки токена: {str(e)}")
        return False


def authenticate_user(username: str, password: str):
    query = "SELECT user_id, password_hash, role FROM users WHERE username = %s;"
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (username,))
                user = cur.fetchone()
                if user:
                    user_id, password_hash, role = user
                    if verify_password(password, password_hash):
                        return generate_jwt(user_id, role)
    except Exception as e:
        logger.error(f"Ошибка аутентификации: {str(e)}")

    return None


def active_user(username):
    query = "SELECT active FROM users WHERE username = %s;"
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (username,))
                result = cur.fetchone()
                return result[0] if result else None
    except Exception as e:
        logger.error(f"Ошибка проверки активности: {str(e)}")
        return None