from unittest.mock import right

from streamlit import button

import streamlit as st
import jwt
#from services.auth import decode
from jwt import DecodeError, ExpiredSignatureError
from repositories.users import add_user
import re
from repositories.users import restrict_rights

def user_rights():
    st.title("Выберите пользователя, которому вы хотите ограничить права доступа или восстановить права")
    username = st.text_input("Введите имя пользователя")
    right_button = st.selectbox("Выберите TRUE, если вы хотите восстановить права, введите FALSE, если вы хотите ограничить права", ["TRUE", "FALSE"])
    button_apply = st.button("Применить изменения")
    if button_apply:
        right_change = restrict_rights(right_button, username)
        if right_change:
            st.success("Пользовательские првава были изменены!")
        else:
            st.error("Пользователя с таким именем не существует!")

def add_user_or_admin():
    st.title("Добавть пользователя или админа")

    with st.form("register_form"):
        username = st.text_input("Введите логин")
        password = st.text_input("Введите пароль", type="password")
        confirm_password = st.text_input("Повторите пароль", type="password")
        role = st.selectbox("Выберите роль", ["user", "admin"])
        active = True
        email = st.text_input("Введите адрес электронной почты")
        submit_button = st.form_submit_button("Зарегистрировать")

        if submit_button:
            if not username or not password or not confirm_password or not role or not email:
                st.warning("Все поля обязательны для заполнения.")
                return

            if not re.match(r"^[a-zA-Z0-9_]+$", username):
                st.error("Имя пользователя может содержать только буквы, цифры и _.")
                return

            if len(password) < 6:
                st.error("Пароль должен быть длиной не менее 6 символов.")
                return

            if password != confirm_password:
                st.error("Пароли не совпадают.")
                return

            try:
                add_user(username, password, role, email, active)
                st.success(f"Пользователь {username} успешно зарегистрирован!")
            except ValueError as e:
                st.error(str(e))



