# Apartments.com web scraper
The tool allows user to scrape data from Apartments.com and provides an interactive webpage to search, filter, and sort data based on factors such as price, location, number of bedrooms/bathrooms to find the units that meet their needs.
### Infrastructure
* The ETL pipeline is fully-deployed with **Docker**, orchestrated with **Docker Compose** and scheduled by **Airflow**, which makes it easy to deploy and maintain.
* The webscraper is developed with **Python** with hybrid approach (Selenium + requests) to overcome anti-scraping mechanism.
* Data is upserted to **MySQL** database by default, while user may specify `--no_dump_db` flag to store as csv and json files.
* The interactive webpage is developed with **Flask**, **Javascript**, and **CSS**.
<p>

<img width="750" alt="workflow" src="https://github.com/user-attachments/assets/7e874f5e-6267-46d3-8211-3a0587c1d15c" />

### What is Special
* Unit-level granularity: scrapes unit-level data, allowing user to search for ideal unit directly. Currently, there are no tools offering this granularity.
* Optimized parallelism: multiple parallelism approaches are tested and carefully analyzed.

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

## Parallelism Tuning for HTML Parsing

To optimize the performance of an HTML parsing pipeline, I experimented with various parallelization strategies using Python's `multiprocessing` and `multithreading` modules.

### Testing Dataset Overview

- **Pages**: 10  
- **Properties**: 400  
- **Units**: 4,504  
- **List building (BeautifulSoup)**: `256.8691 s`

---

### Benchmark: HTML Parsing Time (Before Optimization)

| Method                                                      | Time (s)  |
|-------------------------------------------------------------|-----------|
| Single process (base case)                                  | 19.1319   |
| `apply_async`                                               | 17.0994   |
| `apply_async` + large chunks (25 chunks)                    | 18.5841   |
| `apply_async` + small chunks (88 chunks)                    | 16.9023   |
| `map`                                                       | 18.0836   |
| `ThreadPoolExecutor` (multithread)                          | 20.3130   |
| `apply_async` + small chunks (run only **first 25**)        | **6.6897** |

---

### Investigation & Key Observations

Despite using `multiprocessing`, the performance improvement was **marginal**. Here’s the breakdown of findings:

#### Hypothesis 1: the shared data structure `Manager().list()` is the bottleneck
- Replacing `apply_async` with `map` to avoid shared state: **no effect**
- Commenting out logic that modifies `Manager().list()`: **no effect**
- Even returning early without running any parsing code: **no improvement**

#### Hypothesis 2: Process overhead?
- Reducing the number of tasks using chunking (25 vs. 88 chunks): **no effect**
- However, running **only the first 25 chunks** of the 88-chunk version was **significantly faster**

#### This led to the following insight:  
According to the [official Python documentation on `multiprocessing`](https://docs.python.org/3/library/multiprocessing.html),

> *"When using multiple processes, one generally uses message passing for communication between processes and avoids having to use any synchronization primitives like locks.... <p>
One difference from other Python queue implementations, is that multiprocessing queues serializes all objects that are put into them using pickle. The object return by the get method is a re-created object that does not share memory with the original object."*

In our case, **the main process must serialize large `BeautifulSoup` objects for every task**, which introduces significant overhead on a single core—especially when the actual parsing tasks are lightweight. As a result, `multiprocessing` brings only marginal improvement until we reduce the serialization cost.


---

### Optimization Strategy

**Refactor the code to pass lightweight HTML strings instead of `BeautifulSoup` objects.**  
Each worker then rebuilds the soup locally. This significantly reduces serialization cost and improves parallel throughput.

---

### Benchmark: After Refactoring

- **List building (without turning into soup object beforehand)**: `190.0905 s`

| Method                                   | Time (s)  |
|------------------------------------------|-----------|
| Single process (base case)               | 52.3781   |
| `apply_async`                            | 10.8709   |
| `apply_async` + large chunks (25)        | 11.1214   |
| `apply_async` + small chunks (88)        | 11.6920   |
| `map`                                    | 10.9354   |
| `ThreadPoolExecutor`                     | 57.2707   |

---

### Conclusion

- **Pass HTML strings instead of soup objects** to avoid heavy serialization.
- **Use `apply_async`** for simple, efficient parallelism.
- **Overall speed improvement: ~27%**

| Stage              | Before       | After        |
|--------------------|--------------|--------------|
| List building      | 256.8691 s   | 190.0905 s   |
| Parsing            | 19.1319 s    | 10.8709 s    |
| **Total**          | **276.001 s**| **200.9614 s**|

---

### TL;DR

> Avoid passing complex objects (like soup objects from `BeautifulSoup`) between processes. Instead, pass raw data (e.g., strings) and reconstruct them within the worker. This small change significantly improves performance and scalability.


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
