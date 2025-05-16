from unittest.mock import right

from repositories.products_for_admin import check_product, check_supplier, check_category, push_supplier, get_id_supplier, push_date, push_category, push_product, get_id_category, push_delivery_contents, get_id_delivery, push_price
from streamlit import button
from repositories.update_prices_products import update_price_product

import streamlit as st
import jwt
#from services.auth import decode
from jwt import DecodeError, ExpiredSignatureError
import re

from unittest.mock import right
from repositories.products_for_admin import check_product
from repositories.update_prices_products import update_price_product

import streamlit as st
import jwt
from jwt import DecodeError, ExpiredSignatureError
import re


def update_price():
    st.title("Здесь можно обновить цену")

    barcode_product = st.text_input("Введите barcode товара")
    weight_product = st.text_input("Введите вес товара")
    name_product = st.text_input("Введите название товара")
    start_date_product = st.text_input("Введите дату уствновки цены")
    price = st.text_input("Введите цену товара")
    update_price_button = st.button("Обновить цену товара")

    if update_price_button:
        if check_product(barcode_product, name_product, weight_product):
            st.success(f"Такой товар есть!")
            try:
                update_price_product(barcode_product, start_date_product, price)
                st.success(f"Цена товара обновлена!")
                #cache_popular_products()
            except Exception as e:
                st.error(f"Ошибка обновления: {str(e)}")
        else:
            st.success(f"Такого товара нету!")