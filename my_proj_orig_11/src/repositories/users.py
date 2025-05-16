from services.auth import hash_password
import psycopg2
import psycopg2.extras
from settings import DB_CONFIG


def add_user(username: str, password: str, role: str = "user", email: str = "non@yandex.ru", active: bool = True):
    query_check = "SELECT COUNT(*) FROM users WHERE username = %s;"
    query_insert = "INSERT INTO users (username, password_hash, role, email, active) VALUES (%s, %s, %s, %s, %s);"

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query_check, (username,))
            if cur.fetchone()[0] > 0:
                raise ValueError("Пользователь с таким логином уже существует.")

            password_hash = hash_password(password)

            cur.execute(query_insert, (username, password_hash, role, email, active))
            conn.commit()

def restrict_rights(right, username):
    query_check = "SELECT COUNT(*) FROM users WHERE username = %s;"
    query_update = "UPDATE users SET active = %s WHERE username = %s;"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query_check, (username,))
            if cur.fetchone()[0] == 0:
                return False
            else:
                cur.execute(query_update, (right, username))
                conn.commit()
                return True

