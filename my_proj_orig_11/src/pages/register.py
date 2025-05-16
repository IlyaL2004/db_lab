import streamlit as st
from repositories.users import add_user
import re


def show_register_page():
    st.title("Регистрация пользователя")



    with st.form("register_form"):
        username = st.text_input("Введите логин")
        password = st.text_input("Введите пароль", type="password")
        confirm_password = st.text_input("Повторите пароль", type="password")
        role = "user"
        active = True
        email = st.text_input("Введите адрес электронной почты")
        submit_button = st.form_submit_button("Зарегистрироваться")

        if submit_button:
            if not username or not password or not confirm_password:
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
