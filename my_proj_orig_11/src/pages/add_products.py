from unittest.mock import right

from repositories.products_for_admin import check_product, check_supplier, check_category, push_supplier, get_id_supplier, push_date, push_category, push_product, get_id_category, push_delivery_contents, get_id_delivery, push_price
from streamlit import button

import streamlit as st
import jwt
#from services.auth import decode
from jwt import DecodeError, ExpiredSignatureError
import re







def add_products_admin():
    st.title("Добавть товар, категорию или поставщика")

    st.title("Здесь вы можете определить существует ли такой продукт")

    barcode_product = st.text_input("Введите barcode товара")
    name_product = st.text_input("Введите название товара")
    weight_product = st.text_input("Введите вес товара")

    check_product_button = st.button("Проверить товар на складе")
    if check_product_button:
        if check_product(barcode_product, name_product, weight_product):
            st.success(f"Такой товар есть!")
        else:
            st.success(f"Такого товара нету!")


    st.title("Здесь вы можете определить существует ли такой поставщик")


    phone_supplier = st.text_input("Введите телефон поставщика")
    name_supplier = st.text_input("Введите имя поставщика")

    check_supplier_button = st.button("Проверить поставщика")
    if check_supplier_button:
        if check_supplier(name_supplier, phone_supplier):
            st.success(f"Такой поставщик есть!")
        else:
            st.success(f"Такого поставщика нету!")

    st.title("Здесь вы можете определить существует ли такая категория")

    name_category = st.text_input("Введите название категори")

    check_category_button = st.button("Проверить категорию")
    if check_category_button:
        if check_category(name_category):
            st.success(f"Такая категория есть!")
        else:
            st.success(f"Такой категории нету!")


    st.title("Введите имя поставщика, телефон поставщика, адрес поставщика и дату поставки")
    phone_supplier = st.text_input("Введите телефон поставщик")
    name_supplier = st.text_input("Введите имя поставщик")
    address_supplier = st.text_input("Введите адрес поставщик")
    date_supply = st.text_input("Введите дату поставки")

    push_date_and_supplier_button = st.button("Добавить дату поставки и поставщика")

    if push_date_and_supplier_button:
        if not check_supplier(name_supplier, phone_supplier):
            push_supplier(name_supplier, phone_supplier, address_supplier)
        else:
            st.success(f"Такой поставщик существует!")
        id_supplier = get_id_supplier(name_supplier)
        push_date(id_supplier, date_supply)
        st.success(f"Поставка добавлена!")

    st.title("Введите категорию")
    name_category = st.text_input("Введите название категории")
    push_category_button = st.button("Добавьте категорию")

    if push_category_button:
        if not check_category(name_category):
            push_category(name_category)
            st.success(f"Категория добавлена!")
        else:
            st.success(f"Такая категория существует!")

    st.title("Узнать id последней поставки")
    get_id_delivery_button = st.button("Узнать id последней поставки")
    if get_id_delivery_button:
        id_delivery = get_id_delivery()
        st.success(f"id последней поставки {id_delivery}")

    st.title("Введите товар и храктеристики товара, который вы хотите добавить")
    quantity_product = st.text_input("Введите количество товар")
    barcode_product = st.text_input("Введите barcode товар")
    name_product = st.text_input("Введите название товар")
    weight_product = st.text_input("Введите вес товар")
    package_size_product = st.text_input("Введите размер товар")
    name_category = st.text_input("Введите название категор")
    delivery_id = st.text_input("Введите id поставки")
    start_date_product = st.text_input("Введите дату уствновки цены")
    price = st.text_input("Введите цену товара")

    push_products_button = st.button("Добавить товар")

    if push_products_button:
        if not check_product(barcode_product, name_product, weight_product):
            if not check_category(name_category):
                push_category(name_category)
                st.success(f"Категория добавлена!")
            else:
                st.success(f"Такая категория существует!")
            id_category = get_id_category(name_category)
            push_product(barcode_product, name_product, package_size_product, weight_product, id_category)
            st.success(f"Новый товар добавлен!")
            push_price(barcode_product, start_date_product, price)
            st.success(f"Цена добавлена!")

        else:
            st.success(f"Характеристики такого товара уже существуют!")
        push_delivery_contents(delivery_id, barcode_product, quantity_product)
        st.success(f"Товар добавлен!")








