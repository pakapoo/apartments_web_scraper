# Apartments.com web scraper
The tool allows user to scrape data from Apartments.com and provides an interactive webpage to search, filter, and sort data based on factors such as price, location, number of bedrooms/bathrooms to find the units that meet their needs.

### What is Special
* Unit-level granularity: scrapes unit-level data, allowing user to search for ideal unit directly. Currently, there are no tools offering this granularity.
* Short waiting time: multiple parallelism approaches are tested and carefully analyzed (27% performance gain in HTML parsing). Check [this](./parallelismAnalysis.md) out!
* Easy to setup: fully containerized with **Docker Compose**, which can be set up easily (refer to [Quickstart](#quickstart))
* Overcome anti-scraping mechanism: developed with **Python** with hybrid approach (Selenium + requests)

### Infrastructure
<p>

<img width="750" alt="workflow" src="https://github.com/user-attachments/assets/7e874f5e-6267-46d3-8211-3a0587c1d15c" />

https://github.com/pakapoo/apartments_web_scraper/assets/45991312/5f9af489-51f5-4978-869c-25cfe101d698

## Quickstart
1. Update the search_URL in `src/crawler/config/config.ini` to specify apartments.com search URL of your interest.
2. Build and run Airflow, MySQL, web app, web scraper containers with **Docker Compose**. Create a shared network for containers to communicate with each other.
```bash
docker network create shared-network
find ./src/backend/mysql-db-volume -mindepth 1 -delete # start fresh by cleaning mysql volume
docker-compose -f ./src/backend/docker-compose.yaml up -d
docker-compose -f ./src/Airflow/docker-compose.yaml up -d
```
If there's any issue in docker-compose, try below to reboot all containers.:
```bash
find ./src/backend/mysql-db-volume -mindepth 1 -delete
docker-compose -f ./src/backend/docker-compose.yaml down
docker-compose -f ./src/Airflow/docker-compose.yaml down
docker-compose -f ./src/backend/docker-compose.yaml up -d
docker-compose -f ./src/Airflow/docker-compose.yaml up -d
```
3. You can choose to manually run the web scraper inside the container as below, or wait for Airflow to trigger the workflow daily. If you do not want to store data to the database but output the files, specify the `--no_dump_db` flag. The result will be stored as csv and json files under `./src/crawler/data/result/`.
```bash
docker exec -it web_scraper bash
python ./web_scraper.py
```
4. See the result in your local browser `http://127.0.0.1:5001/`. You may **search**, **filter** or **sort** by column(s) to find your desired housing.


## Future Release
The goal is to build a real-time App that pushes notification to Line/Whatsapp when there are new units that fit ones need. Here are some features and enhancement that I plan to add:
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
