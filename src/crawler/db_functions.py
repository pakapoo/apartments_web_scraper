from sqlalchemy import create_engine
import mysql.connector
import pandas as pd
import os

DB_USER = "root"
DB_PASSWORD = "admpw"
DB_HOST = "localhost"
DB_NAME = "apartment_db"

def dump_df_to_db(df, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME):
    engine = create_engine("mysql+mysqlconnector://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_HOST + "/" + DB_NAME)
    df.to_sql('unit', con=engine, if_exists='append', index=False)

def regerate_table_schema(table, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME):
    init_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../mysql/sqls/init.sql"))
    drop_command = "DROP TABLE IF EXISTS " + table + ";"
    create_command = open(init_script_path, "r").read()
    conn = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME)
    cursor = conn.cursor()
    cursor.execute(drop_command)
    cursor.execute(create_command)
    cursor.close()
    conn.close()

def test_db_dump():
    # Set paths    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, '../../'))
    result_path = os.path.join(base_dir, 'data/result/')
    df = pd.read_csv(os.path.join(result_path, "result.csv"))
    dump_df_to_db(df, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)