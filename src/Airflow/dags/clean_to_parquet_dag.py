from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import boto3
import pandas as pd
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
COLUMN_TRANSFORMS = {
    "unit_price": {
        "type": "numeric",
        "round": 2
    },
    "unit_avail": {
        "type": "datetime"
    },
    "built": {
        "type": "integer"
    },
    "units": {
        "type": "integer"
    },
    "stories": {
        "type": "integer"
    }
}

def clean_csv_to_parquet(**context):
    s3 = boto3.client("s3")

    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    s3_raw_key = f"raw/{date_str}/result.csv"
    local_csv = f"/tmp/sample_output/raw/{date_str}/result.csv"
    local_clean_csv = f"/tmp/sample_output/cleaned/{date_str}/result.csv"
    local_clean_parquet = f"/tmp/sample_output/cleaned/{date_str}/result.parquet"
    s3_cleaned_key_csv = f"cleaned/{date_str}/result.csv"
    s3_cleaned_key_parquet = f"cleaned/{date_str}/result.parquet"

    os.makedirs(f"/tmp/sample_output/raw/{date_str}", exist_ok=True)
    os.makedirs(f"/tmp/sample_output/cleaned/{date_str}", exist_ok=True)

    s3.download_file(S3_BUCKET_NAME, s3_raw_key, local_csv)
    print(f"Downloaded {s3_raw_key} from {S3_BUCKET_NAME}")

    df = pd.read_csv(local_csv)
    if df.empty:
        print("DataFrame is empty, skipping parquet upload.")
        return

    df = df.drop_duplicates()

    for col, rules in COLUMN_TRANSFORMS.items():
        if col not in df.columns:
            continue
        if rules["type"] == "numeric":
            df[col] = pd.to_numeric(df[col], errors="coerce")
            if "round" in rules:
                df[col] = df[col].round(rules["round"])
        elif rules["type"] == "integer":
            df[col] = pd.to_numeric(df[col], errors="coerce", downcast="integer").astype("Int64")
        elif rules["type"] == "datetime":
            df[col] = pd.to_datetime(df[col].astype(str), errors="coerce", format="%Y%m%d")

    df.to_csv(local_clean_csv, index=False)
    s3.upload_file(local_clean_csv, S3_BUCKET_NAME, s3_cleaned_key_csv)
    print(f"Uploaded cleaned CSV to {s3_cleaned_key_csv}")

    df.to_parquet(local_clean_parquet, engine="pyarrow", index=False, coerce_timestamps="us")
    s3.upload_file(local_clean_parquet, S3_BUCKET_NAME, s3_cleaned_key_parquet)
    print(f"Uploaded cleaned parquet to {s3_cleaned_key_parquet}")

with DAG(
    dag_id="clean_to_parquet_dag",
    start_date=days_ago(1),
    schedule_interval=None,
    catchup=False,
    tags=["etl", "s3", "parquet"],
) as dag:

    clean_task = PythonOperator(
        task_id="clean_csv_to_parquet",
        python_callable=clean_csv_to_parquet,
    )
