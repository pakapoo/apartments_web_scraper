# Apartments.com web scraper
### About the Project
Apartments.com presents its data in a two-layer format, requiring users to click on individual apartment links and browse through the available units. This makes the house-searching process quite time-consuming. To simplify and expedite this process, I developed a web scraper that gathers housing data from Apartments.com and displays it in a searchable and sortable table on a webpage. This allows users to easily filter and sort apartments based on crucial factors such as price, location, number of bedrooms, and number of bathrooms, making the search for the ideal apartment much more efficient.

### About Apartments.com
Apartments.com is a popular online platform for apartment listings, enabling users to search for housing options in specific areas. It serves as a valuable resource for renters, providing detailed information about available properties.

### Sample Output
You may find the sample output as csv and json format in `./data/result` folder.

## Instructions
### Prerequisites
* Update the search_URL parameter in the config file `./config/config.ini` to the search URL of apartments.com website.
### Execution
If you only want to run the web scraper: 
1. Run the web scraper Python script.
```bash
python ./src/crawler/web_scraper.py --no_dump_db
```
2. The result will be compiled as csv and json files under `./data/result`.
<br><br>

If you want to build the entire full stack project:
1. Build and run MySQL image on localhost.
```bash
docker build -t mysql-apartments:1.0 -f ./mysql/DockerfileDB ./mysql
docker run -d --name=mysqldb -p 3306:3306 mysql-apartments:1.0
```
2. (optional) Enter interactive mode to make SQL statement to the MySQL database in the Docker container.
```bash
docker exec -it mysqldb sh
mysql -h 127.0.0.1 -u root -p
```
3. Run the webscraper Python script
```bash
python ./src/crawler/web_scraper.py
```
4. See the result with the following url: `http://127.0.0.1:5000/`. You may **search** or **sort** by column to find your desired housing.

## Tech Stack
* Web Scraper: **Python** beautifulsoup
* Web Backend: **Flask**
* Web Frontend: **Javascript**, **CSS**
* Database: **MySQL** deployed with **Docker**

## TODO
Please submit a pull request (PR) if you find any bugs or have ideas to improve the project. Here are some features and enhan

### Features
* Scheduling with Airflow: Automate the web scraping process.
* Data Visualization with Redash: Visualize housing data for better insights.
### Container and Cloud deployment
* Dockerization: Dockerize the web crawler, web application, Airflow, and dashboard.
* Docker Compose: Create a Docker Compose file for easy configuration.
* Cloud Deployment: Deploy the application on a cloud platform for accessibility and scalability.
### API Integration
* Google Maps API: Calculate the distance from a targeted location.
* Notification Service: Integrate with messaging apps like Line, Whatsapp to receive instant notifications about ideal housing options.

Feel free to contribute to the project or reach out if you have any suggestions or feedback!