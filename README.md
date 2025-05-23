# Apartments.com web scraper
The tool scrapes data from Apartments.com and provides an interactive webpage for searching, filtering, and sorting listings by price, location, number of bedrooms/bathrooms, and more at the unit level.

### Key Features
- **Unit-level detail**  
  Unlike most scrapers that stop at the building level, this tool captures fine-grained data for each unit, allowing more accurate and meaningful apartment searches.

- **Optimized performance**  
  Scraping large volumes of data can be slow. This project aims to implement and benchmark multiple parallelism strategies and find out the bottleneck for each stage.
  * For HTML parsing, we achieve a **27% speedup**! [See detailed analysis](./parallelismAnalysis.md). *(More performance optimization of other stages coming soon.)*

- **Easy deployment**  
  Fully containerized with **Docker Compose**. Get started in minutes by following the [Quickstart](#quickstart) guide.

- **Bypasses anti-scraping defenses**  
  Uses a hybrid approach of **Selenium** and **requests** to effectively handle dynamic content and anti-bot mechanisms on Apartments.com.
  
- **Email notification**  
  Remind you about new and updated listing daily with Airflow automation.

### Infrastructure
<img width="700" alt="project_wf_0517" src="https://github.com/user-attachments/assets/93d7fec3-1736-453c-a724-50868966f49c" />


### Demo
https://github.com/pakapoo/apartments_web_scraper/assets/45991312/5f9af489-51f5-4978-869c-25cfe101d698

## Quickstart
1. Configurations
* Update the search_URL in `src/crawler/config/config.ini` to specify apartments.com search URL of your interest.
* Update the email (email receiver(s)) and HOST_PROJECT_PATH (project directory) in `src/airflow/dags/.env`.
* Currently I'm testing email functions with **mailtrap**, you may want to update the SMTP settings in `src/airflow/docker-compose.yaml` to use a different email delivery platform.
2. Build and run Airflow, MySQL, web app, web scraper containers with **Docker Compose**. Create a shared network for containers to communicate with each other.
```bash
docker network create shared-network
find ./src/database/mysql-db-volume -mindepth 1 -delete # start fresh by cleaning mysql volume
docker-compose -f ./src/docker-compose.yaml up -d
docker-compose -f ./src/Airflow/docker-compose.yaml up -d
```
If there's any issue in docker-compose, fix the code and try below to reboot all containers:
```bash
docker-compose -f ./src/docker-compose.yaml down
docker-compose -f ./src/Airflow/docker-compose.yaml down
find ./src/database/mysql-db-volume -mindepth 1 -delete
docker-compose -f ./src/docker-compose.yaml up -d
docker-compose -f ./src/Airflow/docker-compose.yaml up -d
```
3. You can choose to manually run the web scraper inside the container as below, or wait for Airflow to trigger the workflow daily. If you do not want to store data to the database but output the files, specify the `--no_dump_db` flag. The result will be stored as csv and json files under `./src/crawler/data/result/`.
```bash
docker exec -it web_scraper bash
python ./web_scraper.py <--no_dump_db>
```
4. See the result in your local browser `http://127.0.0.1:5001/`. You may **search**, **filter** or **sort** by different attributes to find your desired housing.


## Future Release
The goal is to build a real-time App that sends email or pushes notification when there are new units that fit ones need. Here are some features and enhancement that I plan to add:
#### Infrustracture
* Cloud deployment: deploy to Google Cloud Run
* Scheduling: compare Google Cloud Composer with Airflow
* Extract and load to datawarehouse: move data from MySQL to Bigquery with Google Cloud Functions (event trigger)
* Terraform: Create terraform scripts for cloud deployment
#### Analytics
* Data Visualization with Redash: Visualize housing data for better insights
* Spark/dbt: Perform the analytics engineering in Bigquery
    * Google Maps API: Calculate the distance from a targeted location
#### Good to have
* Scrape data from different sources
* Enable user to scrape multiple districts
* Distributed scraping to avoid anti-scraping
* Notification Service: Integrate with apps like Line, Whatsapp to receive instant notifications about ideal housing options

Feel free to contribute to the project with a pull request (PR) or reach out if you have any suggestions or feedback!
