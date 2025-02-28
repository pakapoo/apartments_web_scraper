import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../crawler')))

from web_scraper import get_property_urls, get_property_html, extract_property_info

default_args = {
    'start_date': days_ago(1),
    'retries': 1,
}

dag = DAG(
    'apartment_scraper',
    default_args=default_args,
    description='Scrape apartment listings and store in MySQL',
    schedule_interval='@daily',
    catchup=False,
)



# scrape the data from apartments.com everyday
with DAG('apartments_com_scraper', start_date = days_ago(1), schedule_interval = "@daily", \
            catchup = False) as dag:
    PythonOperator(task_id='load_config', python_callable=load_config, dag=dag)

# store the data to MySQL database
with DAG('store_mysql', start_date = datetime(2025, 2, 13), schedule_interval = "@daily", \
            catchup = False) as dag:
    None
