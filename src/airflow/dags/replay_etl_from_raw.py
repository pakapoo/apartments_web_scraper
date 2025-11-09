from datetime import datetime, timedelta, timezone
import os, json
import boto3
import pandas as pd
from dotenv import dotenv_values
from airflow import DAG
from airflow.providers.amazon.aws.operators.lambda_function import LambdaInvokeFunctionOperator
from airflow.operators.python import PythonOperator
from airflow.operators.email_operator import EmailOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.models.param import Param

env_config = dotenv_values("/opt/airflow/dags/.env") # for email notifications

dag_default_args = {
    "owner": "airflow",
    "depends_on_past": False, # won't stop when previous run fails
    "retries": 1,
    "retry_delay": timedelta(minutes=10), # applies to both regular DAG runs and catchup DAG runs
    "email_on_failure": True,  # notify when pipeline fails
    "email": env_config.get("pipeline_alert_email", "").split(","),
}

def get_date_str_from_xcom(**context):
    import json
    ti = context['ti']
    result = ti.xcom_pull(task_ids='parquet_to_rds_lambda')
    result = json.loads(result)
    return f"Replay Successful - {result.get('date_str', 'N/A')}"

# ------------------
# DAG
# ------------------
with DAG(
    dag_id="replay_pipeline_dag",
    default_args=dag_default_args,
    description="Run web scraper daily",
    schedule_interval=None,
    catchup=False,
    tags=["apartment_etl"],
    params={
        "date_str": datetime.now(timezone.utc).strftime("%Y%m%d"),
    },
) as dag:

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

    get_subject = PythonOperator(
        task_id='get_subject',
        python_callable=get_date_str_from_xcom,
    )

    send_email = EmailOperator(
        task_id="send_email",
        to=env_config.get("email", "").split(","),
        subject="{{ (ti.xcom_pull(task_ids='get_subject')) }}",
        html_content="<p>Replay done.</p>",
        trigger_rule="all_success",
    )


    clean_task >> rds_task >> get_subject >> send_email
