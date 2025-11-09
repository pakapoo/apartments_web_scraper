from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

RDS_HOST = os.getenv("DB_HOST")
RDS_USER = os.getenv("DB_USER")
RDS_PASSWORD = os.getenv("DB_PASSWORD")
RDS_PORT = int(os.getenv("DB_PORT", 3306))
RDS_DB = os.getenv("DB_NAME", "apartment_db")

def init_schema():
    conn = pymysql.connect(
        host=RDS_HOST,
        user=RDS_USER,
        password=RDS_PASSWORD,
        port=RDS_PORT
    )
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {RDS_DB};")
    cur.execute(f"USE {RDS_DB};")

   # -----------------
    # Main fact/serving table (append-only, snapshot by day)
    # -----------------
    cur.execute("DROP TABLE IF EXISTS unit;")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS unit (
        unit_id BIGINT AUTO_INCREMENT PRIMARY KEY,
        id VARCHAR(255) NOT NULL,
        unit_no VARCHAR(255) NOT NULL,
        url VARCHAR(255),
        name VARCHAR(255),
        tel VARCHAR(255),
        address VARCHAR(255),
        city VARCHAR(255),
        state VARCHAR(255),
        zip VARCHAR(255),
        neighborhood VARCHAR(255),
        built INT,
        units INT,
        stories INT,
        management VARCHAR(255),
        unit_beds DECIMAL(3,1),
        unit_baths DECIMAL(3,1),
        unit_price DECIMAL(10,2),
        unit_sqft DECIMAL(10,2),
        unit_avail DATE,
        rating DECIMAL(4,2),
        num_ratings INT,
        ingested_at DATE NOT NULL,
        INDEX idx_unit_ingested (ingested_at) -- for serving most recent housing data in Flask
    );
    """)

    # -----------------
    # Aggregates
    # -----------------
    cur.execute("DROP TABLE IF EXISTS top_management;")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS top_management (
        management VARCHAR(255),
        avg_rating DECIMAL(4,2),
        rating_count INT,
        PRIMARY KEY (management)
    );
    """)

    cur.execute("DROP TABLE IF EXISTS top_neighborhood;")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS top_neighborhood (
        neighborhood VARCHAR(255),
        avg_price_per_sqft DECIMAL(12,2),
        unit_count INT,
        PRIMARY KEY (neighborhood)
    );
    """)

    conn.commit()
    cur.close()
    conn.close()

with DAG(
    dag_id="init_rds_schema",
    start_date=days_ago(1),
    schedule_interval=None,  # manual trigger (only need to run once)
    catchup=False,
    tags=["apartment_etl", "rds"]
) as dag:

    init_schema_task = PythonOperator(
        task_id="init_schema",
        python_callable=init_schema
    )
