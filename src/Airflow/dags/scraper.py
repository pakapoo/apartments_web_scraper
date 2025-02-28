import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../crawler')))

from web_scraper import load_config, get_property_urls, get_property_html, extract_property_info
from db_functions import dump_df_to_db, regenerate_table_schema

default_args = {
    'start_date': days_ago(1),
    'retries': 1,
}

def load_config():
    """Initialize scraper configuration."""
    global search_URL, cookies, args, result_path
    search_URL, cookies, args, result_path = init_config()
    return {"search_URL": search_URL, "cookies": cookies, "args": args, "result_path": result_path}

def get_urls(**kwargs):
    """Retrieve property URLs from Apartments.com."""
    ti = kwargs['ti']
    config = ti.xcom_pull(task_ids='load_config')
    search_URL, cookies = config["search_URL"], config["cookies"]
    all_links = get_property_urls(search_URL, cookies)
    ti.xcom_push(key="all_links", value=all_links)

def get_html(**kwargs):
    """Retrieve property HTML pages."""
    ti = kwargs['ti']
    all_links = ti.xcom_pull(task_ids='get_property_urls', key="all_links")
    config = ti.xcom_pull(task_ids='load_config')
    cookies = config["cookies"]
    soup_list = get_property_html(all_links, cookies)
    ti.xcom_push(key="soup_list", value=soup_list)

def extract_info(**kwargs):
    """Extract property details from HTML."""
    ti = kwargs['ti']
    soup_list = ti.xcom_pull(task_ids='get_property_html', key="soup_list")
    unit_list = [extract_property_info(soup) for soup in soup_list]  # Avoid multiprocessing
    ti.xcom_push(key="unit_list", value=unit_list)

def save_and_store(**kwargs):
    """Save extracted data and store in MySQL."""
    import pandas as pd

    ti = kwargs['ti']
    unit_list = ti.xcom_pull(task_ids='extract_property_info', key="unit_list")
    config = ti.xcom_pull(task_ids='load_config')
    result_path, args = config["result_path"], config["args"]

    df = pd.DataFrame(unit_list)
    if not df.empty:
        df = df.drop_duplicates()
        df.to_json(os.path.join(result_path, "result.json"), orient='records', lines=True)
        df.to_csv(os.path.join(result_path, "result.csv"), index=False)

        if not args["no_dump_db"]:
            db_functions.regenerate_table_schema('unit', os.getenv("DB_USER"), os.getenv("DB_PASSWORD"),
                                    os.getenv("DB_HOST"), os.getenv("DB_NAME"))
            db_functions.dump_df_to_db(df, os.getenv("DB_USER"), os.getenv("DB_PASSWORD"),
                          os.getenv("DB_HOST"), os.getenv("DB_NAME"))

# scrape the data from apartments.com everyday
with DAG('apartments_com_scraper', default_args=default_args, start_date = days_ago(1), schedule_interval = "@daily", \
            catchup = False) as dag:
    task_load_config = PythonOperator(
        task_id='load_config',
        python_callable=load_config
    )

    task_get_urls = PythonOperator(
        task_id='get_property_urls',
        python_callable=get_urls,
        provide_context=True
    )

    task_get_html = PythonOperator(
        task_id='get_property_html',
        python_callable=get_html,
        provide_context=True
    )

    task_extract_info = PythonOperator(
        task_id='extract_property_info',
        python_callable=extract_info,
        provide_context=True
    )

    task_save_and_store = PythonOperator(
        task_id='save_and_store',
        python_callable=save_and_store,
        provide_context=True
    )

task_load_config >> task_get_urls >> task_get_html >> task_extract_info >> task_save_and_store
