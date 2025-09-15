from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

RDS_HOST = os.getenv("RDS_HOST")
RDS_USER = os.getenv("RDS_USER")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")
RDS_PORT = int(os.getenv("RDS_PORT", 3306))

def init_schema():
    conn = pymysql.connect(
        host=RDS_HOST,
        user=RDS_USER,
        password=RDS_PASSWORD,
        port=RDS_PORT
    )
    cur = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS apartment_db;")
    cur.execute("USE apartment_db;")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS unit (
        id VARCHAR(255) NOT NULL,
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
        unit_no VARCHAR(255) NOT NULL,
        unit_beds DECIMAL(3, 1),
        unit_baths DECIMAL(3, 1),
        unit_price DECIMAL(10, 2),
        unit_sqft FLOAT,
        unit_avail DATE,
        PRIMARY KEY (id, unit_no)
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

with DAG(
    dag_id="init_rds_schema",
    start_date=days_ago(1),
    schedule_interval=None,  # manual trigger
    catchup=False,
    tags=["infra", "init"]
) as dag:

    init_schema_task = PythonOperator(
        task_id="init_schema",
        python_callable=init_schema
    )
