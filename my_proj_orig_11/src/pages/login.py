import streamlit as st
from services.auth import authenticate_user, active_user, verify_token, revoke_token
import jwt
from jwt import DecodeError, ExpiredSignatureError
import logging
import redis
from settings import REDIS_CONFIG, REDIS_TOKEN_TTL
import time
import logging

logger = logging.getLogger(__name__)
SECRET_KEY = "your_secret_key"

def login():
    st.title("Вход")

    username = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")

    if st.button("Войти"):
        user_active = active_user(username)
        if user_active is None:
            st.error("Пользователь не найден")
            return

        if not user_active:
            st.error("Аккаунт заблокирован")
            return

        token = authenticate_user(username, password)
        if token:
            st.session_state["auth_token"] = token
            st.session_state.last_action = time.time()
            st.success("Вход выполнен!")
        else:
            st.error("Неверные учетные данные")

def check_role(required_role: str) -> bool:
    token = st.session_state.get("auth_token")
    if not token:
        st.error("Требуется авторизация")
        return False

    try:
        r = redis.Redis(**REDIS_CONFIG)

        if not r.exists(f"token:{token}"):
            st.session_state.pop("auth_token", None)
            st.error("Сессия истекла")
            return False

        current_ttl = r.ttl(f"token:{token}")
        if current_ttl < REDIS_TOKEN_TTL:
            r.expire(f"token:{token}", REDIS_TOKEN_TTL)

        if "last_action" in st.session_state:
            time_diff = time.time() - st.session_state.last_action
            if time_diff > 90:
                revoke_token(token)
                st.session_state.pop("auth_token", None)
                st.error("Сессия истекла из-за бездействия")
                return False

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["role"] == required_role

    except (DecodeError, ExpiredSignatureError) as e:
        revoke_token(token)
        logger.error(f"Ошибка токена: {str(e)}")
        return False