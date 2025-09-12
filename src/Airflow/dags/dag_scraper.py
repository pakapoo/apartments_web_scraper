from datetime import datetime, timedelta
import os
from dotenv import dotenv_values
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import PythonOperator
from airflow.operators.email_operator import EmailOperator
from docker.types import Mount

default_args = {
    'owner': 'airflow',
    'depends_on_past': False, # doesn't stop because previous run fails
    'retries': 1,
    'retry_delay': timedelta(minutes=10), # applies to both regular DAG runs and catchup DAG runs
}

env_config = dotenv_values("/opt/airflow/dags/.env")

# def create_output_dir():
#     os.makedirs('/opt/airflow/crawler/output/dif', exist_ok=True)

with DAG(
    dag_id='web_scraper_dag',
    default_args=default_args,
    description='Run web scraper every day at UTC 00:00',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,  # rerun the missed runs since start_date
    tags=['scraper'],
) as dag:
    
    # Essentially spinning up a Docker container with the same configurations as ./src/docker-compose.yaml
    scrape_task = DockerOperator(
        task_id='run_scraper',
        image='web_scraper:latest',
        command='python ./src/web_scraper.py',
        docker_url='unix://var/run/docker.sock',
        network_mode='shared-network',
        auto_remove=True, # delete the container after done running
        environment=env_config,
        working_dir="/app",
        mounts=[
        Mount(source=os.path.join(env_config.get("HOST_PROJECT_PATH", ""), "src/crawler"), target = "/app", type = "bind"),
        ], # as airflow is spinning up a new container, note that source refers to directory on "host" but not airflow container!
    )

    # create directory in airflow container (which is already mounted to host)
    # create_dir_task = PythonOperator(
    #     task_id='create_output_dir',
    #     python_callable=create_output_dir,
    # )

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

    # create_dir_task >> scrape_task >> send_email

    scrape_task >> send_email