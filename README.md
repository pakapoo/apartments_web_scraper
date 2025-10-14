# RentRadar – Housing Data Insights Platform
An automated data pipeline that scrapes unit-level listings from Apartments.com, built with a lightweight ELT architecture on AWS, and notifies users daily via email.
#### Note: The project is now fully on AWS with new web UI, the README will be updated soon (end of October 2025)

### Key Features
- **Unit-level detail**  
  Unlike most scrapers that stop at the building level, this tool captures fine-grained data for each unit, allowing more accurate and meaningful apartment searches.

- **Optimized performance**  
  Scraping large volumes of data can be slow. This project benchmarks multiple parallelism strategies and identifies bottlenecks.
  * Main bottleneck: For HTML parsing, we achieve a **27% speedup**! [See detailed analysis](./parallelismAnalysis.md).

- **Easy deployment**  
  Fully containerized with **Docker Compose**. Get started in minutes by following the [Quickstart](#quickstart) guide.
  
- **Email notification**  
  Sends daily email alerts about new and updated listings with **Airflow** automation.

### Infrastructure
<img width="800" alt="rentRadar drawio" src="https://github.com/user-attachments/assets/2b07568c-1d26-44e0-8f8f-2fcc808d4b80" />


### Demo
<This is outdated and will be updated soon>
https://github.com/pakapoo/apartments_web_scraper/assets/45991312/5f9af489-51f5-4978-869c-25cfe101d698

## Quickstart
1. Configure
* **Scraper**: update the `search_URL` in `src/crawler/config/config.ini` with your Apartments.com search link.
* **Email**: update recipient(s) and `HOST_PROJECT_PATH` in `src/airflow/dags/.env`.  
  * This project uses **Mailtrap** for testing. Update the SMTP settings in `src/airflow/docker-compose.yaml` to switch to your preferred email provider.
2. Create the shared network, reset the MySQL volume, and start all containers:
```bash
./scripts/manage_docker.sh start
```
When needed, restart with:
```bash
./scripts/manage_docker.sh restart
```
3. You will then receive email daily for any new/updated listing! Or you may also see all the listings in your local browser `http://127.0.0.1:5001/`.


## Future Release
Here are some features and enhancement that I plan to add:
#### Infrastructure - Moving to AWS
* **Airflow**: EC2 + docker-compose  
  * DAG flow:  
    * `ECSOperator`: trigger scraper container (ECS Fargate, image in ECR)  
    * `PythonOperator`: raw JSON (S3) → cleaned Parquet (partitioned by ingestion_date, Pandas/Pyarrow)  
    * `PythonOperator`: load Parquet into RDS (aggregations)  
    * `EmailOperator`: send alerts via SMTP  
* **Scraper**: ECS Fargate (image in ECR)  
* **Data Lake**: S3
  * Raw: immutable JSON  
  * Clean: schema-aligned Parquet, partitioned by ingestion_date  
* **Serving Layer**: RDS (MySQL), timestamped tables for historical queries  
* **Flask App**: separate EC2 instance querying RDS (filtering + summary stats)  
* **IaC**: AWS CDK for provisioning resources

#### Analytics
* Aggregation:
1. Top 5 management companies (by average rating, with >20 ratings)
2. Top 5 neighborhoods (lowest average price-per-sqft) 
* Google Maps API: Calculate the distance from a targeted location with a subscription database

#### Good to have
* Scrape data from different websites
* Speed up with distributed scraping to avoid anti-scraping

Contributions and feedback are welcome! Please submit a pull request (PR) or open an issue to get involved.
