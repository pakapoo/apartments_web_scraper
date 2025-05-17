from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import PythonOperator
from airflow.operators.email_operator import EmailOperator
from docker.types import Mount
from airflow import DAG
from dotenv import dotenv_values
from datetime import datetime, timedelta
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

env_config = dotenv_values("/opt/airflow/dags/.env")

# create directory in airflow container (which is already mounted to host)
def create_output_dir():
    os.makedirs('/opt/airflow/crawler/output/dif', exist_ok=True)

with DAG(
    dag_id='web_scraper_dag',
    default_args=default_args,
    description='Run web scraper every day at UTC 00:00',
    schedule_interval='@daily',  # trigger daily
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
        working_dir="/app",
        mounts=[
        Mount(source=os.path.join(env_config.get("HOST_PROJECT_PATH", ""), "src/crawler"), target = "/app", type = "bind"),
        ], # as airflow is spinning up a new container, note that source refers to directory on "host" but not airflow container!
    )

    create_dir_task = PythonOperator(
        task_id='create_output_dir',
        python_callable=create_output_dir,
    )

    to_emails = env_config.get("email", "").split(",")
    send_email = EmailOperator(
        task_id='send_email',
        to=to_emails,
        subject='Daily Unit Update',
        html_content="""
            <p>Hello,</p>
            <p>Please find attached the CSVs for new and updated units.</p>
        """,
        files=[
            '/opt/airflow/crawler/output/dif/new_units.csv',
            '/opt/airflow/crawler/output/dif/updated_units.csv'
        ],
    )

    create_dir_task >> scrape_task >> send_email