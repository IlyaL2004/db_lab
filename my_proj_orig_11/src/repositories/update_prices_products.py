import psycopg2
import psycopg2.extras
from settings import DB_CONFIG
from datetime import date


def create_trigger_and_function():
    trigger_function_sql = """
    CREATE OR REPLACE FUNCTION audit_price_change() 
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO price_audit (barcode, old_price, new_price)
        VALUES (OLD.barcode, OLD.price, NEW.price);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql; 
    """

    trigger_sql = """
    CREATE TRIGGER price_update_trigger
    AFTER UPDATE ON prices
    FOR EACH ROW
    WHEN (OLD.price IS DISTINCT FROM NEW.price)
    EXECUTE FUNCTION audit_price_change();
    """

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(trigger_function_sql)
                cur.execute(trigger_sql)
                conn.commit()
                print("Trigger and function created successfully.")
    except Exception as e:
        print(f"Error creating trigger and function: {e}")


import redis
from settings import REDIS_CONFIG


import psycopg2
from settings import DB_CONFIG
import redis


def update_price_product(barcode, start_date, price):
    query_update = """
        UPDATE prices 
        SET end_date = CURRENT_DATE 
        WHERE barcode = %s AND end_date IS NULL;

        INSERT INTO prices (barcode, start_date, price)
        VALUES (%s, %s, %s);
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query_update, (barcode, barcode, start_date, price))
                conn.commit()

        r = redis.Redis(**REDIS_CONFIG)
        r.setex(f'price:{barcode}', 86400, float(price))
        print(f"Цена в кэше для {barcode} обновлена: {price}")

    except (psycopg2.Error, redis.RedisError, ValueError) as e:
        print(f"Ошибка обновления: {str(e)}")
        raise