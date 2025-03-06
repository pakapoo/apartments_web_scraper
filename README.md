# Apartments.com web scraper
The tool allows user to scrape data from Apartments.com and provides an interactive webpage to search, filter, and sort data based on factors such as price, location, number of bedrooms/bathrooms to find the units that meet their needs.
### Infrastructure
* The ETL pipeline is fully-deployed with **Docker**, orchestrated with **Docker Compose** and scheduled by **Airflow**, which makes it easy to deploy and maintain.
* The webscraper is developed with **Python** with hybrid approach (Selenium + requests) to overcome anti-scraping mechanism.
* Data is upserted to **MySQL** database in default, while user may specify `--no_dump_db` flag to store as csv and json files.
* The interactive webpage is developed with **Flask**, **Javascript**, and **CSS**.
<p>

<img width="750" alt="workflow" src="https://github.com/user-attachments/assets/7e874f5e-6267-46d3-8211-3a0587c1d15c" />

### What is Special
* Unit-level granularity: scrapes unit-level data, allowing user to search for ideal unit directly. Currently, there are no tools offering this granularity.
* Short processing time with optimized parallelism: multiple approaches are tested and multiprocessing (apply_async) is adopted.

https://github.com/pakapoo/apartments_web_scraper/assets/45991312/5f9af489-51f5-4978-869c-25cfe101d698

## Quickstart
1. Update the search_URL in `src/crawler/config/config.ini` to specify apartments.com search URL of your interest.
2. Build and run Airflow, MySQL, web app, web scraper containers with **Docker Compose**. Create a shared network for containers to communicate with each other.
```bash
docker network create shared-network
docker-compose -f ./src/backend/docker-compose.yaml up -d
docker-compose -f ./src/Airflow/docker-compose.yaml up -d
```
3. You can choose to manually run the web scraper as below, or wait for Airflow to trigger the workflow daily.
```bash
docker exec -it web_scraper bash
python ./web_scraper.py
```
4. See the result in your local browser `http://127.0.0.1:5001/`. You may **search**, **filter** or **sort** by column(s) to find your desired housing.

## Note:
If you do not want to store data to the database but output the files, run the following command in your terminal. The result will be compiled as csv and json files under `./src/crawler/data/result/`.
```bash
python ./src/crawler/web_scraper.py --no_dump_db
```
For MacOS or Linux user, you may also schedule the workflow in crontab. For example, the below will update the database every 8 hours. <br>
```bash
0 */8 * * * <python executable> <location of the project>/apartments_web_scraper/src/crawler/web_scraper.py
```
If there's any issue in docker-compose, try below to reboot all containers. Optionally, user can clean the data in /src/backend/mysql-db-volume to clear the database:
```bash
docker-compose -f ./src/backend/docker-compose.yaml down
docker-compose -f ./src/Airflow/docker-compose.yaml down
docker-compose -f ./src/backend/docker-compose.yaml up -d
docker-compose -f ./src/Airflow/docker-compose.yaml up -d
```
For debug, user may enter interactive mode to interact with the MySQL database container with SQL commands.
```bash
docker exec -it backend-mysql-1 sh
mysql -h 127.0.0.1 -u root -p
```

## Parallelism tuning (TODO)
Here, I have tested multiple approaches to speed up in-memory html parsing: <p>
**200 urls (6464 units)**
1. Without any parallelism
* 15.53s
2. (Multithreading - ThreadPoolExecutor) Submit each housing as a task for processes to pick up
* pool size = 8
* 15.73s
3. (Multiprocessing - apply_async) Submit each housing as a task for processes to pick up
* pool size = 8
* 11.62s
4. (Multiprocessing - apply_async + chunked data) Group multiple housings as a chunk and submit as a task for processes to pick up
* pool size = 8
* data splitting into 24 chunks
* 13.64s
5. (Multiprocessing - map)
* pool size = 8
* 
6. (Multiprocessing - map + chunked data)
* pool size = 8
* 
7. Asyncio
* 

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
