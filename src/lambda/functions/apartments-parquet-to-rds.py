import boto3, os, json
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text

def lambda_handler(event, context):
    region = "us-west-1"
    s3 = boto3.client("s3", region_name=region)
    secrets = boto3.client("secretsmanager", region_name=region)
    secret_arn = os.environ["DB_SECRET_ARN"]
    creds = json.loads(secrets.get_secret_value(SecretId=secret_arn)["SecretString"])

    DB_USER = creds["username"]
    DB_PASSWORD = creds["password"]
    DB_HOST = os.environ["DB_HOST"]
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "apartment_db")
    S3_BUCKET = os.environ["S3_BUCKET_NAME"]

    today_str = event["date_str"]
    resp = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix="cleaned/")
    all_dates = sorted({obj["Key"].split("/")[1] for obj in resp.get("Contents", []) if obj["Key"].count("/") >= 2})
    yesterday_str = max([d for d in all_dates if d < today_str], default=None)

    s3_today_key = f"cleaned/{today_str}/result.parquet"
    local_today = "/tmp/result_today.parquet"
    s3.download_file(S3_BUCKET, s3_today_key, local_today)
    df_today = pd.read_parquet(local_today)

    df_yesterday = pd.DataFrame()
    if yesterday_str:
        try:
            s3_yesterday_key = f"cleaned/{yesterday_str}/result.parquet"
            local_yesterday = "/tmp/result_yesterday.parquet"
            s3.download_file(S3_BUCKET, s3_yesterday_key, local_yesterday)
            df_yesterday = pd.read_parquet(local_yesterday)
        except Exception as e:
            print(f"No previous data: {e}")

    # Diff logic
    inserted, updated = [], []
    if not df_yesterday.empty:
        yesterday_dict = {(r["id"], r["unit_no"]): r.to_dict() for _, r in df_yesterday.iterrows()}
        for _, row in df_today.iterrows():
            key = (row["id"], row["unit_no"])
            if key not in yesterday_dict:
                inserted.append(row.to_dict())
            elif any(str(row[c]) != str(yesterday_dict[key].get(c)) for c in df_today.columns):
                updated.append(row.to_dict())
    else:
        inserted = df_today.to_dict(orient="records")

    # Write to RDS
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    df_today["ingested_at"] = pd.to_datetime(today_str, format="%Y%m%d").date()
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM unit WHERE ingested_at = :today"),
            {"today": df_today["ingested_at"].iloc[0]},
        )
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

    local_new = "/tmp/new_units.csv"
    local_upd = "/tmp/updated_units.csv"
    pd.DataFrame(inserted).to_csv(local_new, index=False)
    pd.DataFrame(updated).to_csv(local_upd, index=False)

    s3_new = f"diffs/{today_str}/new.csv"
    s3_upd = f"diffs/{today_str}/updated.csv"
    s3.upload_file(local_new, S3_BUCKET, s3_new)
    s3.upload_file(local_upd, S3_BUCKET, s3_upd)

    return {
        "s3_new": f"s3://{S3_BUCKET}/{s3_new}",
        "s3_upd": f"s3://{S3_BUCKET}/{s3_upd}",
        "date_str": today_str
    }
