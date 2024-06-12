# Apartments.com web scraper
### About the Project
I will be enrolling as a graduate student at UW-Madison this fall, and my first priority is to find ideal housing. Factors such as price, location, number of bedrooms, and number of bathrooms are crucial considerations for me. To streamline this process, I developed a web scraper to gather relevant housing data from Apartments.com.

### About Apartments.com
Apartments.com is a widely used online platform for apartment listings, allowing users to search for housing options in specific areas. It is a valuable resource for renters seeking detailed information about available properties.

### Tech Stack
* Crawler: Python beautifulsoup
* Web: Flask, Javascript, CSS
* Database: MySQL (docker)

### Instructions for Using the Web Scraper Only
1. Modify the search_URL parameter in `./config/config.ini` to search for your targeted area
2. Run the web scraper Python script
```bash
python ./src/crawler/web_scraper.py --no_dump_db
```
3. The result will be compiled as csv and json files under `./data/result`

### Instructions for Configuring the Full-Stack Project
1. Build and Run MySQL Image on Localhost
```bash
docker build -t mysql-apartments:1.0 -f ./mysql/DockerfileDB ./mysql
docker run -d --name=mysqldb -p 3306:3306 mysql-apartments:1.0
```
2. Enter interactive mode to make SQL statement to the MySQL database in the Docker container
```bash
docker exec -it mysqldb sh
mysql -h 127.0.0.1 -u root -p
```

## TODO
Please submit a pull request (PR) if you find any bugs or have ideas to improve the project. Here are some features and enhancements I plan to implement:
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