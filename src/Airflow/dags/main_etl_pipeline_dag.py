from datetime import datetime, timedelta, timezone
import os
import boto3
import pandas as pd
from dotenv import dotenv_values
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.operators.email_operator import EmailOperator
from airflow.utils.trigger_rule import TriggerRule
from docker.types import Mount
from sqlalchemy import create_engine, text

# ------------------
# ENV + Config
# ------------------
env_config = dotenv_values("/opt/airflow/dags/.env")

S3_BUCKET_NAME = env_config.get("S3_BUCKET_NAME")
DB_USER = env_config.get("DB_USER")
DB_PASSWORD = env_config.get("DB_PASSWORD")
DB_HOST = env_config.get("DB_HOST")
DB_PORT = int(env_config.get("DB_PORT", 3306))
DB_NAME = env_config.get("DB_NAME", "apartment_db")

os.environ["AWS_ACCESS_KEY_ID"] = env_config.get("AWS_ACCESS_KEY_ID", "")
os.environ["AWS_SECRET_ACCESS_KEY"] = env_config.get("AWS_SECRET_ACCESS_KEY", "")
os.environ["AWS_DEFAULT_REGION"] = env_config.get("AWS_DEFAULT_REGION", "us-east-1")

COLUMN_TRANSFORMS = {
    "unit_price": {"type": "numeric", "round": 2},
    "unit_avail": {"type": "datetime"},
    "built": {"type": "integer"},
    "units": {"type": "integer"},
    "stories": {"type": "integer"},
}

dag_default_args = {
    "owner": "airflow",
    "depends_on_past": False, # doesn't stop because previous run fails
    "retries": 1,
    "retry_delay": timedelta(minutes=10), # applies to both regular DAG runs and catchup DAG runs
    "email_on_failure": True,  # notify when pipeline fails
    "email": env_config.get("pipeline_alert_email", "").split(","),
}

# ------------------
# Raw CSV -> Cleaned Parquet
# ------------------
def clean_csv_to_parquet(**context):
    s3 = boto3.client("s3")
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")

    s3_raw_key = f"raw/{date_str}/result.csv"
    local_csv = f"/tmp/result_{date_str}.csv"
    local_clean_csv = f"/tmp/result_clean_{date_str}.csv"
    local_clean_parquet = f"/tmp/result_{date_str}.parquet"
    s3_cleaned_key_csv = f"cleaned/{date_str}/result.csv"
    s3_cleaned_key_parquet = f"cleaned/{date_str}/result.parquet"

    s3.download_file(S3_BUCKET_NAME, s3_raw_key, local_csv)
    df = pd.read_csv(local_csv)

    if df.empty:
        print("DataFrame is empty, skip downstream tasks.")
        return False  # ShortCircuitOperator will stop the DAG

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

    df.to_parquet(local_clean_parquet, engine="pyarrow", index=False)
    s3.upload_file(local_clean_parquet, S3_BUCKET_NAME, s3_cleaned_key_parquet)

    for f in [local_csv, local_clean_csv, local_clean_parquet]:
        if os.path.exists(f):
            os.remove(f)

    return {"date_str": date_str}


# ------------------
# Parquet -> RDS + Upload diffs to S3
# ------------------
def parquet_to_rds(**context):
    s3 = boto3.client("s3")
    ti = context["ti"]
    today_str = ti.xcom_pull(task_ids="clean_csv_to_parquet")["date_str"]

    # find the most recent date < today, so that we can compare the diffs
    resp = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix="cleaned/")
    all_dates = sorted(
        {obj["Key"].split("/")[1] for obj in resp.get("Contents", []) if obj["Key"].count("/") >= 2}
    )
    yesterday_str = max([d for d in all_dates if d < today_str], default=None)

    print(f"Today = {today_str}, Yesterday = {yesterday_str}")

    s3_today_key = f"cleaned/{today_str}/result.parquet"
    local_today = f"/tmp/result_{today_str}.parquet"
    s3.download_file(S3_BUCKET_NAME, s3_today_key, local_today)
    df_today = pd.read_parquet(local_today)

    if df_today.empty:
        print("No data to insert into RDS.")
        return None

    # load yesterday if exists
    df_yesterday = pd.DataFrame()
    if yesterday_str:
        s3_yesterday_key = f"cleaned/{yesterday_str}/result.parquet"
        local_yesterday = f"/tmp/result_{yesterday_str}.parquet"
        try:
            s3.download_file(S3_BUCKET_NAME, s3_yesterday_key, local_yesterday)
            df_yesterday = pd.read_parquet(local_yesterday)
        except Exception as e:
            print(f"Warning: cannot load yesterday's parquet: {e}")

    # find diffs (new, updated)
    inserted, updated = [], []
    if not df_yesterday.empty:
        yesterday_dict = {
            (r["id"], r["unit_no"]): r.to_dict()
            for _, r in df_yesterday.iterrows()
        }
        for _, row in df_today.iterrows():
            key = (row["id"], row["unit_no"])
            if key not in yesterday_dict:
                inserted.append(row.to_dict())
            else:
                dif = any(str(row[c]) != str(yesterday_dict[key].get(c)) for c in df_today.columns)
                if dif:
                    updated.append(row.to_dict())
    else:
        inserted = df_today.to_dict(orient="records")

    engine = create_engine(
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    df_today["ingested_at"] = pd.to_datetime(today_str, format="%Y%m%d").date()
    df_today.to_sql("unit", con=engine, if_exists="append", index=False, method="multi")

    # Aggregates: only using today's data
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE top_management;"))
        conn.execute(text("""
        INSERT INTO top_management (management, avg_rating, rating_count)
        SELECT management, SUM(rating*num_ratings)/SUM(num_ratings) as avg_rating, SUM(num_ratings) as rating_count
        FROM (SELECT DISTINCT name, management, rating, num_ratings  
                        FROM unit
                        WHERE ingested_at = :today AND management IS NOT NULL AND num_ratings IS NOT NULL) as sub
        GROUP BY management
        ORDER BY avg_rating DESC, rating_count DESC
        """), {"today": df_today["ingested_at"].iloc[0]})

        conn.execute(text("TRUNCATE TABLE top_neighborhood;"))
        conn.execute(text("""
        INSERT INTO top_neighborhood (neighborhood, avg_price_per_sqft, unit_count)
        SELECT neighborhood,
               AVG(unit_price / unit_sqft) as avg_price_per_sqft,
               COUNT(*) as unit_count
        FROM unit
        WHERE ingested_at = :today AND neighborhood IS NOT NULL AND unit_price IS NOT NULL AND unit_sqft > 0
        GROUP BY neighborhood
        ORDER BY avg_price_per_sqft ASC
        """), {"today": df_today["ingested_at"].iloc[0]})

    local_new = f"/tmp/new_units_{today_str}.csv"
    local_upd = f"/tmp/updated_units_{today_str}.csv"
    pd.DataFrame(inserted).to_csv(local_new, index=False)
    pd.DataFrame(updated).to_csv(local_upd, index=False)

    return {
        "local_new": local_new,
        "local_upd": local_upd,
        "date_str": today_str,
    }


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
    tags=["etl", "s3", "rds"],
) as dag:

    scrape_task = DockerOperator(
        task_id="run_scraper",
        image="web_scraper:latest",
        command="python ./src/web_scraper.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="shared-network",
        auto_remove=True,
        environment=env_config,
        working_dir="/app",
        mounts=[
            Mount(
                source=os.path.join(env_config.get("HOST_PROJECT_PATH", ""), "src/crawler"),
                target="/app",
                type="bind",
            ),
        ],
    )

    clean_task = ShortCircuitOperator(
        task_id="clean_csv_to_parquet",
        python_callable=clean_csv_to_parquet,
    )

    rds_task = PythonOperator(
        task_id="parquet_to_rds",
        python_callable=parquet_to_rds,
    )

    send_email = EmailOperator(
        task_id="send_email",
        to=env_config.get("email", "").split(","),
        subject="Daily Unit Update",
        html_content="<p>Attached are the new and updated units for today.</p>",
        files=[
            "{{ ti.xcom_pull(task_ids='parquet_to_rds')['local_new'] }}",
            "{{ ti.xcom_pull(task_ids='parquet_to_rds')['local_upd'] }}",
        ],
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    scrape_task >> clean_task >> rds_task >> send_email
