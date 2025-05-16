import psycopg2
import psycopg2.extras
from settings import DB_CONFIG

import redis
from settings import REDIS_CONFIG

import psycopg2
import psycopg2.extras
from settings import DB_CONFIG
import redis

import psycopg2
import psycopg2.extras
from settings import DB_CONFIG
import redis



def cache_all_products_prices():
    r = redis.Redis(**REDIS_CONFIG)
    query = """
        SELECT DISTINCT ON (barcode) barcode, price
        FROM prices
        ORDER BY barcode, start_date DESC
    """

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                results = cur.fetchall()

                for barcode, price in results:
                    try:
                        r.setex(f'price:{barcode}', 86400, float(price))
                    except (redis.RedisError, ValueError) as e:
                        print(f"Ошибка кэширования {barcode}: {str(e)}")
    except psycopg2.Error as e:
        print(f"Ошибка БД при кэшировании товаров: {str(e)}")


def get_products():
    print("Получение продуктов")
    r = redis.Redis(**REDIS_CONFIG)

    cache_all_products_prices()

    query_products = "SELECT barcode, name FROM products;"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query_products)
            products = cur.fetchall()

    cached_prices = {}
    try:
        pipeline = r.pipeline()
        for product in products:
            pipeline.get(f'price:{product["barcode"]}')
        prices = pipeline.execute()

        for i, product in enumerate(products):
            barcode = product["barcode"]
            price = prices[i]
            cached_prices[barcode] = float(price) if price else get_current_price_from_db(barcode)
    except redis.RedisError as e:
        print(f"Ошибка Redis: {e}")
        for product in products:
            barcode = product["barcode"]
            cached_prices[barcode] = get_current_price_from_db(barcode)

    return [{
        'name': product['name'],
        'barcode': product['barcode'],
        'price': cached_prices.get(product['barcode'], 0.0)
    } for product in products]


def get_current_price_from_db(barcode):
    query = """
        SELECT price
        FROM prices
        WHERE barcode = %s
        ORDER BY start_date DESC
        LIMIT 1;
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (barcode,))
                result = cur.fetchone()
                return float(result[0]) if result else 0.0
    except psycopg2.Error as e:
        print(f"Ошибка БД при получении цены для {barcode}: {e}")
        return 0.0

def get_products_filter(id_category):
    print("Получение продуктов фильтра")
    query = """SELECT p.name, p.barcode, pr.price
                    FROM products p
                    JOIN prices pr 
                    ON p.barcode = pr.barcode
                    WHERE category_id = %s;"""
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (id_category,))
            return cur.fetchall()



def get_categories() -> list[dict]:
    print("Получение категорий продуктов")
    query = "SELECT name, category_id FROM categories;"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

def get_count_product(barcode) -> int:
    print("Получение количества продукта по штирхкоду")
    query = """SELECT COALESCE(dc.quantity, 0) - COALESCE(sd.quantity, 0) AS remaining_quantity
                FROM (SELECT barcode, SUM(quantity) AS quantity FROM delivery_contents GROUP BY barcode) AS dc
                LEFT JOIN (SELECT barcode, SUM(quantity) AS quantity FROM sales_details GROUP BY barcode) AS sd
                ON dc.barcode = sd.barcode
                WHERE dc.barcode = %s;"""
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (barcode,))
            return cur.fetchone()


