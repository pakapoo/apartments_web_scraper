import mysql.connector

def get_data(table, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME):
    conn = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM unit")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    result = []
    for row in rows:
        d = {}
        for i, col in enumerate(cursor.description):
            d[col[0]] = row[i]
        result.append(d)
    return result