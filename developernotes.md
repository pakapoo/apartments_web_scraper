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