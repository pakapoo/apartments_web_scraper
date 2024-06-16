# Apartments.com web scraper
The tool allows user to scrape data from Apartments.com with **Python (beautifulsoup)** and export data to **MySQL** database. The database is deployed with a customized **Dockerfile**. It then displays data on a webpage developed with **Flask**, **Javascript**, and **CSS**. Users can search, filter, and sort data based on factors such as price, location, number of bedrooms/bathrooms to find the units that meet their needs.

### What is Special
* Unit-level granularity: Each unit within a apartment is presented as a row of data, allowing user to search for ideal unit directly in tabular format, instead of clicking into each apartment.
* Short processing time: The script is designed with **multiprocessing** that speed up html parsing for each apartment.

### Sample Output
You may find unit data compiled altogether as csv and json files under `./data/result`.

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
The ultimate goal is to build a real-time App that pushes notification when there are new units that fit ones need. Please submit a pull request (PR) if you find any bug or have ideas to improve the project. Here are some features and enhancement that I plan to add:
* Scheduling with Airflow: Automate the web scraping process.
* Data Visualization with Redash: Visualize housing data for better insights.
* Dockerization: Dockerize the web crawler, web application, Airflow, and dashboard.
* Docker Compose: Create a Docker Compose file for easy configuration.
* Cloud Deployment: Deploy the application on a cloud platform for accessibility and scalability.
* Google Maps API: Calculate the distance from a targeted location.
* Notification Service: Integrate with messaging apps like Line, Whatsapp to receive instant notifications about ideal housing options.

Feel free to contribute to the project or reach out if you have any suggestions or feedback!