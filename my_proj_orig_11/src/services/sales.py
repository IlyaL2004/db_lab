from datetime import datetime
from repositories.sales import add_sale, add_sale_details
from pandas import DataFrame
import jwt
from jwt import DecodeError, ExpiredSignatureError
import streamlit as st
import redis
from settings import REDIS_CONFIG
import logging

logger = logging.getLogger(__name__)


class SalesService:
    def process_sale(self, sale_date: datetime, items: DataFrame, total_sum, address, phone_number) -> int:
        items = items.rename(columns={
            "Количество": "quantity",
            "Barcode": "barcode",
            "Цена за штуку": "price_per_piece",
            "Суммарная цена": "total_price"
        })

        SECRET_KEY = "your_secret_key"
        token = st.session_state.get("auth_token")

        if not token:
            st.error("Вы не авторизованы")
            return False

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload["user_id"]
        except (DecodeError, ExpiredSignatureError) as e:
            st.error(f"Ошибка авторизации: {str(e)}")
            return False

        try:
            sale_id = add_sale(user_id, sale_date, total_sum, address, phone_number)
            items["sale_id"] = sale_id
            add_sale_details(items)

            logger.info(f"Публикуем сообщение в Redis: Новый заказ #{sale_id}")
            r = redis.Redis(**REDIS_CONFIG)
            response = r.publish('new_orders', f'Новый заказ #{sale_id} на сумму {float(total_sum):.2f}₽')
            logger.info(f"Ответ Redis: {response}")

            return sale_id

        except Exception as e:
            st.error(f"Ошибка обработки заказа: {str(e)}")
            logger.error(f"Ошибка: {str(e)}")
            return False