from sqlalchemy import create_engine, text
import mysql.connector
import pandas as pd
import os
import json
from datetime import datetime

def normalize(val):
    if pd.isna(val) or val is None:
        return None
    # str to datetime format str
    if isinstance(val, str):
        val = val.strip()
        if val.isdigit() and len(val) == 8:
            try:
                return str(datetime.strptime(val, "%Y%m%d").date())
            except:
                pass
    # float to int
    try:
        float_val = float(val)
        if float_val.is_integer():
            return int(float_val)
        return round(float_val, 2)
    except:
        pass

    return str(val)

def dump_df_to_db(df, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME):
    # engine = create_engine("mysql+mysqlconnector://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_HOST + "/" + DB_NAME)
    engine = create_engine(
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    inserted_rows = []
    updated_rows = []

    # sqlalchemy uses semicolon as placeholder, and later passes in a dictionary of parameter values
    check_sql = f"SELECT * FROM unit WHERE id = :unit_id AND unit_no = :unit_no"
    upsert_sql = f"""
    INSERT INTO unit ({', '.join(df.columns)}) 
    VALUES ({', '.join([f":{col}" for col in df.columns])})
    ON DUPLICATE KEY UPDATE 
    {', '.join([f"{col} = VALUES({col})" for col in df.columns])};
    """

    with engine.connect() as conn:
        for index, row in df.iterrows():
            unit_id = row['id']  # primary key
            unit_no = row['unit_no'] # primary key
            existing = conn.execute(text(check_sql), {"unit_id": unit_id, "unit_no": unit_no}).fetchone()
            
            params = {col: None if pd.isna(val) else val for col, val in row.items()}
            conn.execute(text(upsert_sql), params)
            conn.commit()

            # Generate dif result files for email attachment
            if existing is None:
                inserted_rows.append(row)
            else:
                is_updated = any(
                    normalize(row[col]) != normalize(existing._mapping.get(col)) 
                    for col in df.columns
                    if col in existing._mapping
                )
                if is_updated:
                    updated_rows.append(row)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM unit"))
        print("DEBUG count after insert:", result.scalar())

    print("Current directory:", os.getcwd()) # should be /app
    
    # cleanup old dif files
    os.makedirs("./output/dif", exist_ok=True)
    for file in os.listdir("./output/dif"):
        file_path = os.path.join("./output/dif", file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    if inserted_rows:
        pd.DataFrame(inserted_rows).to_csv("./output/dif/new_units.csv", index=False)
    else:
        pd.DataFrame(columns=df.columns).to_csv("./output/dif/new_units.csv", index=False)
    if updated_rows:
        pd.DataFrame(updated_rows).to_csv("./output/dif/updated_units.csv", index=False)
    else:
        pd.DataFrame(columns=df.columns).to_csv("./output/dif/updated_units.csv", index=False)

    print(f"Inserted: {len(inserted_rows)}, Updated: {len(updated_rows)}")

# Below are just for development and testing purpose
def regenerate_table_schema(table, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME):
    init_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/sqls/init.sql"))
    drop_command = "DROP TABLE IF EXISTS " + table + ";"
    create_command = open(init_script_path, "r").read()
    conn = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME)
    cursor = conn.cursor()
    cursor.execute(drop_command)
    cursor.execute(create_command)
    cursor.close()
    conn.close()

def get_data(table, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME):
    conn = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM " + table)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return json.dumps(data, default=str)

def test(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME):
    # Set paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, '../../'))
    result_path = os.path.join(base_dir, 'data/result/')

    data = get_data('unit', DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
    print(json.dumps(data, default=str))
    # df = pd.read_csv(os.path.join(result_path, "result.csv"))
    # dump_df_to_db(df, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

if __name__ == '__main__':
    test() 
