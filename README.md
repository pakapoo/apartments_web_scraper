# Apartments.com web scraper
The tool allows user to scrape data from Apartments.com with **Python** and persist data in **MySQL** database. The pipeline is fully-deployed with **Docker** and triggered by **Airflow**. It then displays the data on a webpage developed with **Flask**, **Javascript**, and **CSS**. Users can search, filter, and sort data based on factors such as price, location, number of bedrooms/bathrooms to find the units that meet their needs.

<img width="700" alt="workflow" src="https://github.com/user-attachments/assets/7e874f5e-6267-46d3-8211-3a0587c1d15c" />

### What is Special
* Unit-level granularity: Scrapes unit-level data, allowing user to search for ideal unit directly.
* Short processing time for I/O bound task: Uses **multithreading** to speed up html parsing.
* Bypass authentification: Use hybrid approach (Selenium + requests) to overcome anti-scraping techniques.

https://github.com/pakapoo/apartments_web_scraper/assets/45991312/5f9af489-51f5-4978-869c-25cfe101d698

## Quickstart
1. Update the search_URL parameter in `./config/config.ini`, pointing to your desired apartments.com search URL.
2. Build and run Airflow, MySQL, Web app, Web scraper containers.
```bash
docker network create shared-network
docker-compose -f ./src/backend/docker-compose.yaml up -d
docker-compose -f ./src/Airflow/docker-compose.yaml up -d
```
3. Either manually run the web scraper script as below, or wait for Airflow to trigger the workflow.
```bash
docker exec -it web_scraper bash
python ./web_scraper.py
```
4. See the result with the following url: `http://127.0.0.1:5001/`. You may **search** or **sort** by column to find your desired housing.

## Note:
If you do not want to store data to the database but output the files, run the following command in your terminal. The result will be compiled as csv and json files under `./data/result`.
```bash
python ./src/crawler/web_scraper.py --no_dump_db
```
For MacOS or Linux user, you may also schedule in crontab. For example, the below will update the database every 8 hours. <br>
```bash
0 */8 * * * <python executable> <location of the project>/apartments_web_scraper/src/crawler/web_scraper.py
```
If there's any issue in docker-compose, try below which will restart all containers. Optionally, clean the data in /src/backend/mysql-db-volume to clear the database:
```bash
docker-compose -f ./src/backend/docker-compose.yaml down
docker-compose -f ./src/Airflow/docker-compose.yaml down
docker-compose -f ./src/backend/docker-compose.yaml up -d
docker-compose -f ./src/Airflow/docker-compose.yaml up -d
```
You may enter interactive mode to interact with the MySQL database container with SQL commands.
```bash
docker exec -it apartments_web_scraper-mysql-1 sh
mysql -h 127.0.0.1 -u root -p
```

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
