from airflow.providers.docker.operators.docker import DockerOperator
from airflow import DAG
from dotenv import dotenv_values
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

env_config = dotenv_values("/opt/airflow/dags/.env")

with DAG(
    dag_id='web_scraper_dag',
    default_args=default_args,
    description='Run web scraper every 5 minutes',
    schedule_interval='*/60 * * * *',  # trigger every 60 minutes
    start_date=datetime(2024, 1, 1),
    catchup=False,  # don't allows missed DAG Runs to be scheduled again that are missed for somehow reason
    tags=['scraper'],
) as dag:

    scrape_task = DockerOperator(
        task_id='run_scraper',
        image='web_scraper:latest',
        command='python ./web_scraper.py',
        docker_url='unix://var/run/docker.sock',
        network_mode='shared-network',
        auto_remove=True,
        mount_tmp_dir=False,
        environment=env_config,
    )
