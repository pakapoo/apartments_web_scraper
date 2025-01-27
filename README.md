# Apartments.com web scraper
The tool allows user to scrape data from Apartments.com with **Python (beautifulsoup)** and export data to **MySQL** database deployed with **Docker**. It then displays data on a webpage developed with **Flask**, **Javascript**, and **CSS**. <p>
Users can search, filter, and sort data based on factors such as price, location, number of bedrooms/bathrooms to find the units that meet their needs.

### What is Special
* Unit-level granularity: Scrapes unit-level data, allowing user to search for ideal unit directly.
* Short processing time: Utilizes **multiprocessing** technique that speeds up html parsing.

### Sample Output
You may find data scraped from the searched URL compiled altogether as csv and json files under `./data/result`.

## Quickstart
1. Update the search_URL parameter in `./config/config.ini`, pointing to your desired apartments.com search URL.
2. Build and run MySQL docker image on your laptop
```bash
docker build -t mysql-apartments:1.0 -f ./mysql/DockerfileDB ./mysql
docker run -d --name=mysqldb -p 3306:3306 mysql-apartments:1.0
```
3. Run the web scraper script
```bash
python ./src/crawler/web_scraper.py
```
For MacOS or Linux user, you may also schedule in crontab. For example, the below will update the database every 8 hours. <br>
```bash
0 */8 * * * <python executable> <location of the project>/apartments_web_scraper/src/crawler/web_scraper.py
```
4. See the result with the following url: `http://127.0.0.1:5000/`. You may **search** or **sort** by column to find your desired housing.

Note: If you only need to scrape data from Apartments.com, run the following command in your terminal. The result will be compiled as csv and json files under `./data/result`.
```bash
python ./src/crawler/web_scraper.py --no_dump_db
```

### Useful Tips
You may enter interactive mode to execute SQL commands in the Docker container.
```bash
docker exec -it mysqldb sh
mysql -h 127.0.0.1 -u root -p
```

## Future Release
The ultimate goal is to build a real-time App that pushes notification to Line/Whatsapp when there are new units that fit ones need. Here are some features and enhancement that I plan to add:
### Infrustracture
* Dockerization: Containerize the web crawler, MySQL, Flask web application, Airflow, and Redash dashboard to Google Cloud Run
    * Make sure the web crawler can store data to MySQL database
    * Make sure data persist even the MySQL database is down
    * Make sure Flask container can connect and use data from MySQL container
* Scheduling: set up Google Cloud Composer or Airflow for time trigger the crawler
* Extract and load to datawarehouse: move data from MySQL to Bigquery with Google Cloud Functions (event trigger)
* Docker Compose: Create a Docker Compose file for local deployment
* Terraform: Create terraform scripts for cloud deployment
### Analytics
* Data Visualization with Redash: Visualize housing data for better insights
* Spark/dbt: Perform the analytics engineering in Bigquery
    * Google Maps API: Calculate the distance from a targeted location
### Good to have
* Scrape data from different sources
* Enable user to scrape multiple districts
* Distributed scraping to avoid anti-scraping
* Notification Service: Integrate with apps like Line, Whatsapp to receive instant notifications about ideal housing options

Feel free to contribute to the project with a pull request (PR) or reach out if you have any suggestions or feedback!