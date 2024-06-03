# apartments_web_scraper
Web scraper for apartments.com

## Database
### Build and run MYSQL image
```bash
docker build -t mysql-apartments:1.0 -f ./mysql/DockerfileDB ./mysql
docker run -d --name=mysqldb -p 3306:3306 mysql-apartments:1.0
```
### Enter interactive mode
```bash
docker exec -it mysqldb sh
mysql -h 127.0.0.1 -u root -p
```

TODO:
<python>
scroll and scrape
README.md and illustration
<python good to have>
distributed web scraping
Google map API, calculate distance
<Azure>
Python dockerize
MySQL
Airflow
<Other>
Line API, email sending