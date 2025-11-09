from datetime import datetime, timedelta, timezone
import os, json
import boto3
from dotenv import dotenv_values
from airflow import DAG
from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.lambda_function import LambdaInvokeFunctionOperator
from airflow.operators.email_operator import EmailOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.models.param import Param

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

env_config = dotenv_values("/opt/airflow/dags/.env") # for email notifications

dag_default_args = {
    "owner": "airflow",
    "depends_on_past": False, # won't stop when previous run fails
    "retries": 1,
    "retry_delay": timedelta(minutes=10), # applies to both regular DAG runs and catchup DAG runs
    "email_on_failure": True,  # notify when pipeline fails
    "email": env_config.get("pipeline_alert_email", "").split(","),
}

def download_diff_files(**context):
    ti = context["ti"]
    result = json.loads(ti.xcom_pull(task_ids="parquet_to_rds_lambda"))
    print(f"pull from parquet_to_rds_lambda: {result}")
    s3_new = result["s3_new"]
    s3_upd = result["s3_upd"]

    s3 = boto3.client("s3", region_name="us-west-1")

    for s3_path in [s3_new, s3_upd]:
        bucket, key = s3_path.replace("s3://", "").split("/", 1)
        local_path = f"/tmp/{os.path.basename(key)}"
        print(f"Downloading {s3_path} → {local_path}")
        s3.download_file(bucket, key, local_path)

    return True

def get_date_str_from_xcom(**context):
    import json
    ti = context['ti']
    result = ti.xcom_pull(task_ids='parquet_to_rds_lambda')
    result = json.loads(result)
    return f"Daily Unit Update - {result.get('date_str', 'N/A')}"

# ------------------
# DAG
# ------------------
with DAG(
    dag_id="e2e_pipeline_dag",
    default_args=dag_default_args,
    description="Run web scraper daily",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["apartment_etl"],
    params={
        "date_str": datetime.now(timezone.utc).strftime("%Y%m%d"),
    },
) as dag:

    scrape_task = EcsRunTaskOperator(
        task_id="run_scraper",
        cluster="apartment-scraper-cluster",
        task_definition="apartments-web-scraper",
        launch_type="FARGATE", # serverless
        aws_conn_id="aws_default", # set up in Airflow UI
        overrides={
            "containerOverrides": [
                {
                    "name": "scraper-container",
                    "command": ["python", "src/web_scraper.py"],
                    "environment": [
                        {"name": "S3_BUCKET_NAME", "value": S3_BUCKET_NAME},
                    ],
                }
            ]
        },
        network_configuration={
            "awsvpcConfiguration": {
                "subnets": [
                "subnet-06d68a8171cf0f313",
                "subnet-0cf148f75cd116d41"
            ],
                "securityGroups": ["sg-0443020b0c90476e5"], # allow outbound to internet (for scraper to store to S3)
                "assignPublicIp": "ENABLED",
            }
        },
    )

    clean_task = LambdaInvokeFunctionOperator(
        task_id="clean_csv_to_parquet_lambda",
        function_name="clean_csv_to_parquet_lambda",
        aws_conn_id="aws_default",
        invocation_type="RequestResponse",
        payload=json.dumps({
            "date_str": "{{ dag_run.conf.get('date_str', params.date_str) }}"
        }),
    )

    rds_task = LambdaInvokeFunctionOperator(
        task_id="parquet_to_rds_lambda",
        function_name="apartments-parquet-to-rds",
        aws_conn_id="aws_default",
        invocation_type="RequestResponse",
        payload="{{ ti.xcom_pull(task_ids='clean_csv_to_parquet_lambda') }}",
    )

    download_task = PythonOperator(
        task_id="download_diff_files",
        python_callable=download_diff_files,
    )

    get_subject = PythonOperator(
        task_id='get_subject',
        python_callable=get_date_str_from_xcom,
    )

    send_email = EmailOperator(
        task_id="send_email",
        to=env_config.get("email", "").split(","),
        subject="{{ (ti.xcom_pull(task_ids='get_subject')) }}",
        html_content="<p>Attached are the new and updated units for today.</p>",
        files=[
            "/tmp/new.csv",
            "/tmp/updated.csv",
        ],
        trigger_rule="all_success",
    )


    scrape_task >> clean_task >> rds_task >> download_task >> get_subject >> send_email
