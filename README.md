# RentRadar – Housing Data Insights Platform
A cloud-native pipeline that scrapes apartment listings, processes housing data on AWS, and delivers daily insights via email and dashboard.

### Tech Stack
AWS (Lambda, ECS, ECR, S3, RDS, EC2, Secrets Manager, IAM, CloudWatch) · Apache Airflow · Postgres · Docker · Flask

### Highlights
- **AWS-native design** — separation of orchestration (Airflow) and compute (Lambda, ECS) for scalibility.

- **Automated ETL** — daily and replayable Airflow DAGs for processing and backfilling data.

- **Optimized performance** — resolved multiprocessing bottleneck in scraper, achieving ~27% faster parsing. [See detailed analysis](./parallelismAnalysis.md)

- **Structured data flow** — raw S3 layer as immutable record source, transformed into transactional and analytical tables in RDS.

- **Secure by design** — Secrets Manager and least-privilege IAM.

- **Email and metrics serving** — automated email alerts and a Flask dashboard for housing metrics.

### Architecture Overview
The architecture separates orchestration, transformation, and serving layers for modularity and fault isolation.
<img width="800" alt="rentRadar drawio" src="https://github.com/user-attachments/assets/2b07568c-1d26-44e0-8f8f-2fcc808d4b80" />


### Dashboard View


### Email Notification


## Future Release
#### Infrastructure
* **IaC**: AWS CDK or Terraform for provisioning AWS resources

#### Analytics
* Google Maps API: Calculate the distance from a targeted location with a subscription database

#### Other
* Scrape data from different websites
* Cold start for ECS scraper
* Distributed scraping to speed up and avoid potential anti-scraping


Contributions and feedback are welcome! Please submit a pull request (PR) or open an issue to get involved.
