from pages.selling_products import show_selling_products_page
import streamlit as st
from pages.login import login, check_role
from pages.register import show_register_page
from pages.user_management import user_rights, add_user_or_admin
from pages.add_products import add_products_admin
from pages.update_prices import update_price
import redis
from settings import REDIS_CONFIG
from streamlit_autorefresh import st_autorefresh
import logging
from services.auth import revoke_token
import time
from repositories.products import cache_all_products_prices  # Добавлен импорт

logger = logging.getLogger(__name__)


def init_redis():
    try:
        r = redis.Redis(**REDIS_CONFIG)
        pubsub = r.pubsub()
        pubsub.subscribe('new_orders')
        return pubsub
    except Exception as e:
        st.error(f"Ошибка подключения к Redis: {str(e)}")
        logger.error(f"Redis connection error: {str(e)}")
        return None


def main():
    cache_all_products_prices()

    st.sidebar.title("Навигация")
    if "last_action" not in st.session_state:
        st.session_state.last_action = time.time()

    if "auth_token" in st.session_state:
        time_diff = time.time() - st.session_state.get("last_action", 0)
        if time_diff > 90:
            revoke_token(st.session_state.auth_token)
            st.session_state.pop("auth_token", None)
            st.rerun()

    st_autorefresh(interval=2000, key="notifications_refresh")

    if "notifications" not in st.session_state:
        st.session_state.notifications = []

    if "pubsub" not in st.session_state:
        st.session_state.pubsub = init_redis()

    if st.session_state.pubsub:
        try:
            msg = st.session_state.pubsub.get_message()
            if msg and msg['type'] == 'message':
                notification = msg['data'].decode()
                st.session_state.notifications.append(notification)
                logger.info(f"Получено уведомление: {notification}")
        except Exception as e:
            st.error(f"Ошибка чтения сообщений: {str(e)}")
            logger.error(f"Message read error: {str(e)}")

    with st.sidebar:
        st.subheader("Последние заказы")
        if st.session_state.notifications:
            for notification in reversed(st.session_state.notifications[-5:]):
                st.info(notification)
        else:
            st.info("Новых заказов пока нет")

    if "auth_token" not in st.session_state:
        page = st.sidebar.radio(
            "Выберите действие", ["Вход", "Регистрация"]
        )
        if page == "Вход":
            login()
        elif page == "Регистрация":
            show_register_page()
    else:
        if check_role("user"):
            page = st.sidebar.radio(
                "Перейти к странице",
                ["Сделать заказ", "Выйти"],
            )
            if page == "Сделать заказ":
                show_selling_products_page()
            elif page == "Выйти":
                if st.button("Выйти"):
                    token = st.session_state.get("auth_token")
                    if token:
                        revoke_token(token)
                    st.session_state.pop("auth_token", None)
                    st.success("Сессия завершена")
        elif check_role("admin"):
            page = st.sidebar.radio(
                "Перейти к странице",
                ["Сделать заказ", "Управление пользовательскими правами",
                 "Добавить пользователя или админа", "Добавить товар, категорию, поставщика",
                 "Обновить цену", "Выйти"],
            )
            if page == "Сделать заказ":
                show_selling_products_page()
            elif page == "Управление пользовательскими правами":
                user_rights()
            elif page == "Добавить пользователя или админа":
                add_user_or_admin()
            elif page == "Добавить товар, категорию, поставщика":
                add_products_admin()
            elif page == "Обновить цену":
                update_price()
            elif page == "Выйти":
                if st.button("Выйти"):
                    token = st.session_state.get("auth_token")
                    if token:
                        revoke_token(token)
                    st.session_state.pop("auth_token", None)
                    st.success("Сессия администратора завершена")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    main()