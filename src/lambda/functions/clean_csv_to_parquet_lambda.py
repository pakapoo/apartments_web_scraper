import boto3, os
import pandas as pd
from datetime import datetime, timezone

S3_BUCKET = os.environ["S3_BUCKET_NAME"]

COLUMN_TRANSFORMS = {
    "unit_price": {"type": "numeric", "round": 2},
    "unit_avail": {"type": "datetime"},
    "built": {"type": "integer"},
    "units": {"type": "integer"},
    "stories": {"type": "integer"},
}

def lambda_handler(event, context):
    s3 = boto3.client("s3", region_name="us-west-1")
    date_str = event.get('date_str')

    s3_raw_key = f"raw/{date_str}/result.csv"
    local_csv = f"/tmp/result.csv"
    local_clean_csv = f"/tmp/result_clean.csv"
    local_clean_parquet = f"/tmp/result.parquet"
    s3_clean_csv = f"cleaned/{date_str}/result.csv"
    s3_clean_parquet = f"cleaned/{date_str}/result.parquet"

    s3.download_file(S3_BUCKET, s3_raw_key, local_csv)
    df = pd.read_csv(local_csv)
    if df.empty:
        print("Empty DataFrame, skip downstream.")
        return {"skip_downstream": True}

    df = df.drop_duplicates()
    for col, rules in COLUMN_TRANSFORMS.items():
        if col not in df.columns:
            continue
        if rules["type"] == "numeric":
            df[col] = pd.to_numeric(df[col], errors="coerce").round(rules.get("round", 0))
        elif rules["type"] == "integer":
            df[col] = pd.to_numeric(df[col], errors="coerce", downcast="integer").astype("Int64")
        elif rules["type"] == "datetime":
            df[col] = df[col].astype(str).str.strip() # since there's missing value, pandas read_csv will read this column as float
            df[col] = df[col].apply(lambda x: x.split('.')[0] if '.' in x else x)
            df[col] = df[col].apply(lambda x: x if x.isdigit() and len(x) == 8 else None)
            df[col] = pd.to_datetime(df[col], format="%Y%m%d", errors="coerce") # since there are missing values, pandas will read in as float, that's why we don't use %Y-%m-%d

    df.to_csv(local_clean_csv, index=False)
    s3.upload_file(local_clean_csv, S3_BUCKET, s3_clean_csv)

    df.to_parquet(local_clean_parquet, engine="pyarrow", index=False)
    s3.upload_file(local_clean_parquet, S3_BUCKET, s3_clean_parquet)

    return {"date_str": date_str}
