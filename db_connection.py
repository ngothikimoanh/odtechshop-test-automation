import psycopg2


def get_db_connection():
    return psycopg2.connect(
        dbname="od-tech-shop-local",
        user="od-tech-shop-user",
        password="od-tech-shop-password",
        host="localhost",
        port="5432",
    )
