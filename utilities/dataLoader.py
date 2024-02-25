# import libraries
import trino
import pandas as pd
import time
import mysql.connector


def load_data_from_livedb(query, attempts=3, delay=2):
    attempt = 1

    # Connect to db
    config = {
        "host": "maxscale-prod.internal.glovoapp.com",
        "user": "gs_weekly_pay",
        "password": "zuusija2eiYohngah1me",
        "database": "glovo_live",
    }
    while attempt < attempts + 1:
        try:
            cnx = mysql.connector.connect(**config)
        except:
            time.sleep(delay ** attempt)
            attempt += 1

    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            result = cursor.execute(query)
            rows = cursor.fetchall()
        cnx.close()
        return pd.DataFrame(rows)
    else:
        print("Could not connect")
        return None


def load_data_from_starburst(query):

    HOST = 'starburst.g8s-data-platform-prod.glovoint.com'
    PORT = 443
    conn_details = {
        'host': HOST,
        'port': PORT,
        'http_scheme': 'https',
        'auth': trino.auth.OAuth2Authentication()
    }
    with trino.dbapi.connect(**conn_details) as conn:
        df = pd.read_sql_query(query, conn)
    return df
