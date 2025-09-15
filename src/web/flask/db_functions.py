import mysql.connector
import logging
logging.basicConfig(level=logging.DEBUG)

def get_data(table, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME):
    conn = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    logging.debug(f"Fetched {len(rows)} rows from {table}")
    logging.debug(f"Sample rows: {rows[:3]}")
    logging.debug(f"DEBUG Flask connecting to: {DB_HOST}, {DB_NAME}, {DB_USER}")

    result = []
    for row in rows:
        d = {}
        for i, col in enumerate(cursor.description):
            d[col[0]] = row[i]
        result.append(d)
    cursor.close()
    conn.close()
    return result
