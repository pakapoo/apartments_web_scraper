from sqlalchemy import create_engine, text
import mysql.connector
import pandas as pd
import os
import json

def dump_df_to_db(df, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME):
    engine = create_engine("mysql+mysqlconnector://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_HOST + "/" + DB_NAME)
    # df.to_sql('unit', con=engine, if_exists='append', index=False)
    with engine.connect() as conn:
        for index, row in df.iterrows():
            placeholders = ', '.join([f":{col}" for col in df.columns])
            sql = f"""
            INSERT INTO unit ({', '.join(df.columns)}) 
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE 
            {', '.join([f"{col} = VALUES({col})" for col in df.columns])};
            """
            
            # Create a dictionary of parameter values
            params = {col: None if pd.isna(val) else val for col, val in row.items()}
            conn.execute(text(sql), params)
            conn.commit()


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
    # default=str handles Decimal and datatime columns that are not serializable
    print(json.dumps(data, default=str))
    # df = pd.read_csv(os.path.join(result_path, "result.csv"))
    # dump_df_to_db(df, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

# if __name__ == '__main__':
#     test() 
