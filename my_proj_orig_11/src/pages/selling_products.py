from itertools import product
from narwhals.selectors import string
from pygments.lexer import default
from unicodedata import category
import streamlit as st
import repositories.products
import pandas as pd
from datetime import date
from services.sales import SalesService
import random
import time

def update_total_sum():
    st.session_state.total_sum = st.session_state.sales_table["Суммарная цена"].sum()


def get_everything_quantity_product(product_barcode):
    return repositories.products.get_count_product(product_barcode)


def get_quantity_product_from_basket(product_barcode):
    product_row = st.session_state.sales_table.loc[st.session_state.sales_table['Barcode'] == product_barcode]
    if not product_row.empty:
        return product_row['Количество'].values[0]
    else:
        return 0


def add_product_event(product_name, product_barcode, product_quantity, product_price):
    everything_quantity_product = get_everything_quantity_product(product_barcode)[0]
    quantity_product_from_basket = get_quantity_product_from_basket(product_barcode)
    if everything_quantity_product >= product_quantity + quantity_product_from_basket:
        if product_barcode in st.session_state.sales_table['Barcode'].values:
            st.session_state.sales_table.loc[
                st.session_state.sales_table['Barcode'] == product_barcode, 'Количество'] += product_quantity
            st.session_state.sales_table.loc[
                st.session_state.sales_table['Barcode'] == product_barcode, 'Суммарная цена'] = (
                    st.session_state.sales_table.loc[
                        st.session_state.sales_table['Barcode'] == product_barcode, 'Количество'] * product_price
            )
        else:
            new_row = pd.DataFrame({
                "Название продукта": [product_name],
                "Barcode": [product_barcode],
                "Количество": [product_quantity],
                "Цена за штуку": [product_price],
                "Суммарная цена": [float(product_quantity) * float(product_price)]
            })
            st.session_state.sales_table = pd.concat([st.session_state.sales_table, new_row], ignore_index=True)
        update_total_sum()
    else:
        st.error(f"Недостаточно товара. Доступно: {everything_quantity_product}")


#@st.cache_data
def get_products():
    products = repositories.products.get_products()
    return {product["name"]: {"barcode": product["barcode"], "price": float(product["price"])} for product in products}


@st.cache_data
def get_products_filter(id_category):
    products = repositories.products.get_products_filter(id_category)
    return {product["name"]: {"barcode": product["barcode"], "price": float(product["price"])} for product in products}


@st.cache_data
def get_categories():
    categories = repositories.products.get_categories()
    return {'Категория не выбрана': 0, **{category["name"]: category["category_id"] for category in categories}}


def clear_table_event():
    st.session_state.sales_table = pd.DataFrame(
        columns=["Название продукта", "Barcode", "Количество", "Цена за штуку", "Суммарная цена"]
    )
    st.session_state.total_sum = 0.0


def upload_sales(sales_table, total_sum, address, phone_number):
    sale_date = date(2024, random.randint(1, 12), random.randint(1, 28))
    sale_id = SalesService().process_sale(sale_date, sales_table, total_sum, address, phone_number)
    return sale_id


def show_selling_products_page():
    if "sales_table" not in st.session_state:
        st.session_state.sales_table = pd.DataFrame(
            columns=["Название продукта", "Barcode", "Количество", "Цена за штуку", "Суммарная цена"]
        )
    if "total_sum" not in st.session_state:
        st.session_state.total_sum = 0.0

    st.title("Продажа продуктов")
    categories = get_categories()
    selected_category = st.selectbox("Выберите категорию", categories.keys())

    if st.button("Применить фильтр") and categories[selected_category] != 0:
        products = get_products_filter(categories[selected_category])
    else:
        products = get_products()

    options = [f"{name} | Штрих-код: {info['barcode']} | Цена: {info['price']} руб."
               for name, info in products.items()]
    selected_product = st.selectbox("Выберите продукт", options)

    if selected_product:
        selected_name = selected_product.split(" | ")[0]
        selected_barcode = selected_product.split(" | ")[1].split(": ")[1]
        selected_price = float(selected_product.split(" | ")[2].split(": ")[1].replace(" руб.", ""))

    quantity = st.number_input("Количество", min_value=1, value=1)

    if st.button("Добавить продукт"):
        st.session_state.last_action = time.time()
        st.session_state.button_click = True
        add_product_event(selected_name, selected_barcode, quantity, selected_price)

    address = st.text_input("Адрес доставки")
    phone = st.text_input("Номер телефона")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Очистить корзину"):
            st.session_state.last_action = time.time()
            clear_table_event()
    with col2:
        if st.button("Оформить заказ") and not st.session_state.sales_table.empty:
            st.session_state.last_action = time.time()
            if not address or not phone:
                st.warning("Заполните адрес и телефон!")
            else:
                try:
                    sale_id = upload_sales(st.session_state.sales_table, st.session_state.total_sum, address, phone)
                    st.success(f"Заказ №{sale_id} оформлен!")
                    clear_table_event()
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")

    st.subheader("Текущий заказ")
    st.dataframe(st.session_state.sales_table)
    st.markdown(f"**Итого: {st.session_state.total_sum:.2f} руб.**")