from pandas import DataFrame
import psycopg2
from settings import DB_CONFIG
from datetime import date


def add_sale(user_id, sale_date: date, total_sum, address, phone_number) -> int:
    total_sum = float(total_sum)
    query = """
        INSERT INTO sales (user_id, total_sum, sale_date, address, phone_number)
        VALUES (%(user_id)s, %(total_sum)s, %(sale_date)s, %(address)s, %(phone_number)s) RETURNING sale_id;
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, {"user_id": user_id, "total_sum": total_sum, "sale_date": sale_date, "address": address, "phone_number": phone_number})
            return cur.fetchone()[0]


def add_sale_details(sales: DataFrame) -> None:
    query = """
        INSERT INTO sales_details (sale_id, barcode, quantity, price_per_piece, total_price)
        VALUES (%s, %s, %s, %s, %s);
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                query,
                sales[["sale_id", "barcode", "quantity", "price_per_piece", "total_price"]].itertuples(
                    index=False, name=None
                ),
            )
