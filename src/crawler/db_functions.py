from sqlalchemy import create_engine
import mysql.connector
import pandas as pd
import os

def dump_df_to_db(df):
    engine = create_engine("mysql+mysqlconnector://root:admpw@localhost/apartment_db")
    sql = "INSERT INTO unit (name, address) VALUES (%s, %s)"
    df.to_sql('unit', con=engine, if_exists='append', index=False)

def main():
    # Set paths    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, '../../'))
    result_path = os.path.join(base_dir, 'data/result/')
    df = pd.read_csv(os.path.join(result_path, "result.csv"))
    dump_df_to_db(df)

if __name__ == '__main__':
    main()