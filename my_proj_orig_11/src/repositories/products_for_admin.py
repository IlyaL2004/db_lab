import psycopg2
import psycopg2.extras
from settings import DB_CONFIG


def check_product(barcode, name, weight):
    query_check = "SELECT COUNT(*) FROM products WHERE barcode = %s AND name = %s AND weight = %s;"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query_check, (barcode, name, weight,))
            if cur.fetchone()[0] > 0:
                return True
            else:
                return False



def check_supplier(name, phone):
    query_check = "SELECT COUNT(*) FROM suppliers WHERE name = %s AND phone = %s;"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query_check, (name, phone,))
            if cur.fetchone()[0] > 0:
                return True
            else:
                return False

def check_category(name):
    query_check = "SELECT COUNT(*) FROM categories WHERE name = %s;"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query_check, (name,))
            if cur.fetchone()[0] > 0:
                return True
            else:
                return False

def push_supplier(name, phone, address):
    query = """
            INSERT INTO suppliers (name, phone, address)
            VALUES (%s, %s, %s);
        """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query,(name, phone, address))

def get_id_supplier(name):
    query = """SELECT supplier_id FROM suppliers WHERE name = %s;"""
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (name,))
            return cur.fetchone()

def get_id_category(name):
    query = """SELECT category_id FROM categories WHERE name = %s;"""
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (name,))
            return cur.fetchone()


def push_date(supplier_id, delivery_date):
    query = """
                INSERT INTO deliveries (supplier_id, delivery_date)
                VALUES (%s, %s);
            """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (supplier_id, delivery_date))

def push_category(name):
    query = """
                INSERT INTO categories (name)
                VALUES (%s);
            """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (name,))


def get_id_delivery():
    query = """SELECT MAX(delivery_id) FROM deliveries;"""
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()
            if result[0] is not None:
                return result[0]
            return None

def push_product(barcode, name, package_size, weight, category_id):
    query = """
                    INSERT INTO products (barcode, name, package_size, weight, category_id)
                    VALUES (%s, %s, %s, %s, %s);
                """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (barcode, name, package_size, weight, category_id))


def push_delivery_contents(delivery_id, barcode, quantity):
    query = """
                       INSERT INTO delivery_contents (delivery_id, barcode, quantity)
                       VALUES (%s, %s, %s);
                   """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (delivery_id, barcode, quantity))


import redis
from settings import REDIS_CONFIG


import psycopg2
from settings import DB_CONFIG
import redis

def push_price(barcode, start_date, price):
    query = """
        INSERT INTO prices (barcode, start_date, price)
        VALUES (%s, %s, %s);
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (barcode, start_date, price))
            conn.commit()

    try:
        price_float = float(price)
        r = redis.Redis(**REDIS_CONFIG)
        r.setex(f'price:{barcode}', 3600, price_float)
        print(f"Cached price for new product {barcode}: {price_float}")
    except (redis.RedisError, ValueError) as e:
        print(f"Ошибка записи в кэш: {e}")
