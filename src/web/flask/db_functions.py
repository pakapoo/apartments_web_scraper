import mysql.connector
import logging
logging.basicConfig(level=logging.DEBUG)

# Helper function - convert SQL rows to list of dicts
def query_to_dict(cursor, rows):
    """Helper: convert SQL rows to list of dicts"""
    result = []
    for row in rows:
        d = {}
        for i, col in enumerate(cursor.description):
            d[col[0]] = row[i]
        result.append(d)
    return result


def get_units(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME):
    conn = mysql.connector.connect(
        user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT, database=DB_NAME
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM unit
        WHERE ingested_at = (SELECT MAX(ingested_at) FROM unit)
    """)
    rows = cursor.fetchall()
    logging.debug(f"Fetched {len(rows)} rows from unit")
    if rows:
        logging.debug(f"Sample row: {rows[0]}")
    logging.debug(f"DEBUG Flask connecting to: {DB_HOST}, {DB_NAME}, {DB_USER}")

    result = query_to_dict(cursor, rows)
    cursor.close()
    conn.close()
    return result


def get_top_management(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME):
    conn = mysql.connector.connect(
        user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT, database=DB_NAME
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM top_management ORDER BY avg_rating DESC LIMIT 5")
    rows = cursor.fetchall()
    logging.debug(f"Fetched {len(rows)} rows from top_management")

    result = query_to_dict(cursor, rows)
    cursor.close()
    conn.close()
    return result


def get_top_neighborhood(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME):
    conn = mysql.connector.connect(
        user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT, database=DB_NAME
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM top_neighborhood ORDER BY avg_price_per_sqft LIMIT 5")
    rows = cursor.fetchall()
    logging.debug(f"Fetched {len(rows)} rows from top_neighborhood")

    result = query_to_dict(cursor, rows)
    cursor.close()
    conn.close()
    return result
