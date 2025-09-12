## Note:
To run the scraper on local laptop without docker container:
1. In `./src/crawler/config/config.ini`, uncomment line 13 and comment out line 14.
2. In `./src/crawler/web_scraper.py`, uncomment line 94~96 and comment out line 103~105.
---
For MacOS or Linux user, you may also schedule the workflow in crontab. For example, the below will update the database every 8 hours. <br>
```bash
0 */8 * * * <python executable> <location of the project>/apartments_web_scraper/src/crawler/web_scraper.py
```
---
#### MySQL CLI
For debug, user may enter interactive mode to interact with the MySQL database container with SQL commands.
```bash
docker exec -it mysql sh
mysql -h 127.0.0.1 -u root -p
```
---
#### Run scraper manually inside container
You can choose to manually run the web scraper inside the container as below, or wait for Airflow to trigger the workflow daily. If you do not want to store data to the database but output the files, specify the `--no_dump_db` flag. The result will be stored as csv and json files under `./src/crawler/data/result/`.
```bash
docker exec -it web_scraper bash
python src/crawler/src/web_scraper.py --no_dump_db
```