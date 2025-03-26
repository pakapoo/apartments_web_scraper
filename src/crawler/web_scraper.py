import os
import time
import multiprocessing as mp
import argparse
import configparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions


import custom_extraction_functions
import db_functions
import utils
import parallelism_testing

PAGE_NUMBER_SELECTOR = "p.searchResults > span"
LINKS_SELECTOR = "a.property-link"

NAME_SELECTOR = "h1.propertyName"
TEL_SELECTOR = "div.phoneNumber span"
ADDRESS_SELECTOR = "div.propertyAddressContainer span.delivery-address > span:nth-child(1)"
CITY_SELECTOR = "div.propertyAddressContainer span:nth-child(2)"
STATE_SELECTOR = "div.propertyAddressContainer span.stateZipContainer > span:nth-child(1)"
ZIP_SELECTOR = "div.propertyAddressContainer span.stateZipContainer > span:nth-child(2)"
NEIGHBORHOOD_SELECTOR = "div.propertyAddressContainer span.neighborhoodAddress > a.neighborhood"
BUILT_UNITS_STORIES_SELECTOR = "section.feesSection.feesSectionV2.js-viewAnalyticsSection div#profileV2FeesWrapper"
MANAGEMENT_SELECTOR = "img.logo"

PLAN_SELECTOR = "div.tab-section.active div.pricingGridItem.multiFamily.hasUnitGrid"
UNIT_SELECTOR = "li.unitContainer.js-unitContainerV3"

UNIT_BEDS_SELECTOR = "span.detailsTextWrapper > span:nth-child(1)"
UNIT_BATHS_SELECTOR = "span.detailsTextWrapper > span:nth-child(2)"
UNIT_NO_SELECTOR = "div.unitColumn.column span:nth-child(2)"
UNIT_PRICE_SELECTOR1 = "div.pricingColumn.column span:nth-child(2)"
UNIT_PRICE_SELECTOR2 = "div.pricingColumn.column div.rent-estimate-button.js-view-rent-estimate > span"
UNIT_SQFT_SELECTOR = "div.sqftColumn.column span:nth-child(2)"
UNIT_AVAIL_SELECTOR = "div.availableColumn.column span:nth-child(1)"


class Property:
    def __init__(self, id, url, name, tel, address, city, state, zip, neighborhood, built, units, stories, management):
        self.id = id
        self.url = url
        self.name = name
        self.tel = tel
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip
        self.neighborhood = neighborhood
        self.built = built
        self.units = units
        self.stories = stories
        self.management = management
     
class Unit(Property):
    def __init__(self, id, url, name, tel, address, city, state, zip, neighborhood, built, units, stories, management, unit_no, unit_beds, unit_baths, unit_price, unit_sqft, unit_avail):
        Property.__init__(self, id, url, name, tel, address, city, state, zip, neighborhood, built, units, stories, management)
        self.unit_no = unit_no
        self.unit_beds = unit_beds
        self.unit_baths = unit_baths
        self.unit_price = unit_price
        self.unit_sqft = unit_sqft
        self.unit_avail = unit_avail

@utils.time_stats
def init_config():
    global search_URL, result_path, headers, args, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME

    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(current_dir)

    # Read config file
    config = configparser.ConfigParser()
    config_path = os.path.join(base_dir, 'config/config.ini')
    config.read(config_path)
    search_URL = config['user_config']['search_URL']

    # Set paths    
    result_path = os.path.join(base_dir, config['path']['tmp_output_folder'])
    os.makedirs(result_path, exist_ok=True)

    # generate the required 'cookie' parameter of headers with selenium
    chromedriver_path = os.path.join(base_dir, config['path']['chromedriver_path'])
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    # service = ChromeService(chromedriver_path)
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    # user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"

    geckodriver_path = os.path.join(base_dir, config['path']['geckodriver_path'])
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.binary_location = "/usr/bin/firefox-esr"
    service = FirefoxService(geckodriver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    user_agent = driver.execute_script("return navigator.userAgent;")

    driver.get(search_URL)
    cookies = driver.get_cookies()
    
    headers = {
            'User-Agent': f"{user_agent}",\
            "Upgrade-Insecure-Requests": "1",\
            "DNT": "1",\
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",\
            "Accept-Encoding": "gzip, deflate, br, zstd",\
            "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",\
            "cookie": f"{cookies}"
            }

    parser = argparse.ArgumentParser(description='Web scraper for apartment listings')
    parser.add_argument('-N', '--no_dump_db', action='store_true', help='Do not dump data to database')
    args = parser.parse_args()
    print("Do not dump data to database: ", args.no_dump_db)

    # MySQL config
    DB_USER = config['DB']['DB_USER']
    DB_PASSWORD = config['DB']['DB_PASSWORD']
    DB_HOST = config['DB']['DB_HOST']
    DB_NAME = config['DB']['DB_NAME']

@utils.time_stats
def get_property_urls(search_URL):
    """
    Fetches property URLs from the given search URL and stores them in a list.

    Parameters:
    search_URL (str): The URL to fetch property URLs from.

    Returns:
    all_links (list): A list of property URLs.
    """
    response = requests.get(search_URL, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_links = []

    # Get number of pages for this search URL
    try:
        pages = soup.select_one(PAGE_NUMBER_SELECTOR).get_text().split(' ')[-1]
        print("Total pages: ", pages)
    except AttributeError:
        print("No pages information found.")
        pages = 1
    # Loop through all pages and scrape the property links
    for page in range(1, int(pages)+1):
        print("processing page: ", page)
        response = requests.get(search_URL+'/'+str(page), headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.select(LINKS_SELECTOR)
        unique_links = list(set(link['href'] for link in links))
        all_links.extend(unique_links)
    print("Total properties: ", len(all_links))
    return all_links

@utils.time_stats
def get_property_html(all_links):
    """
    Get the HTML for each property URL as soup object, and store them in a list.

    Parameters:
    all_links (list): A list of URLs to fetch HTML from.

    Returns:
    soup_list (list): A list of soup objects.
    """
    soup_list = []
    for count, url in enumerate(all_links):
        response = requests.get(url, headers=headers)
        # soup = BeautifulSoup(response.text, 'html.parser')
        soup_list.append((url, response.text))
        if count == (len(all_links)-1):
            print("All {} urls are processed!".format(count + 1)) 
        elif (count+1) % 10 == 0 and count != 0:
            print("{} urls processed".format(count + 1))
    return soup_list

def extract_property_info(data, unit_list):
    """
    Extract property information from the soup object and store in a list of dictionary shared among multi-processes.

    Parameters:
    soup (BeautifulSoup): The soup object to extract information from.
    columns (list): A list of column names for the DataFrame.
    unit_list (list): A list to store the extracted information.

    Returns:
    None
    """
    tmp_unit_list = []
    soup = BeautifulSoup(data[1], 'html.parser')
    # soup = data[1]
    
    # extract property info
    id = data[0].split('/')[-2]
    url = data[0].strip()
    name = custom_extraction_functions.name(soup, NAME_SELECTOR)
    tel = custom_extraction_functions.tel(soup, TEL_SELECTOR)
    address = custom_extraction_functions.address(soup, ADDRESS_SELECTOR)
    city = custom_extraction_functions.city(soup, CITY_SELECTOR)
    state = custom_extraction_functions.state(soup, STATE_SELECTOR)
    zip = custom_extraction_functions.zip(soup, ZIP_SELECTOR)
    neighborhood = custom_extraction_functions.neighborhood(soup, NEIGHBORHOOD_SELECTOR)
    built, units, stories = custom_extraction_functions.built_units_stories(soup, BUILT_UNITS_STORIES_SELECTOR)
    management = custom_extraction_functions.management(soup, MANAGEMENT_SELECTOR)

    # extract units info
    plan_info = soup.select(PLAN_SELECTOR)
    for plan in plan_info:
        unit_beds = custom_extraction_functions.beds(plan, UNIT_BEDS_SELECTOR)
        unit_baths = custom_extraction_functions.baths(plan, UNIT_BATHS_SELECTOR)
        unit_info = plan.select(UNIT_SELECTOR)
        for unit in unit_info:
            unit_no = custom_extraction_functions.unit_no(unit, UNIT_NO_SELECTOR)
            unit_price = custom_extraction_functions.unit_price(unit, UNIT_PRICE_SELECTOR1, UNIT_PRICE_SELECTOR2)
            unit_sqft = custom_extraction_functions.unit_sqft(unit, UNIT_SQFT_SELECTOR)
            unit_avail = custom_extraction_functions.unit_avail(unit, UNIT_AVAIL_SELECTOR)
            unit_data = Unit(id, url, name, tel, address, city, state, zip, neighborhood, built, units, stories, management, unit_no, unit_beds, unit_baths, unit_price, unit_sqft, unit_avail)
            tmp_unit_list.append(vars(unit_data))
    unit_list.extend(tmp_unit_list)

def extract_property_info_wrapper(soup_list, unit_list):
    tmp_unit_list = []
    for soup in soup_list:
        extract_property_info(soup, tmp_unit_list)
    unit_list.extend(tmp_unit_list)

def main():
    # STEP 0: init configurations
    init_config()
    # custom_extraction_functions.test_connection(headers)

    # STEP1: Get property URLs
    print("step 1: get property URLs")
    all_links = get_property_urls(search_URL)

    # STEP2: Get property HTML
    print("step 2: get property html")
    soup_list = get_property_html(all_links)

    # test parallelism
    # import pickle
    # with open("soup_list_mid_soup.pkl", "wb") as f:
    #     pickle.dump(soup_list, f)
    # return

    # STEP3: Extract property information
    print("step 3: extract property information")
    # parallelism_testing.non_parallel(soup_list)
    unit_list = parallelism_testing.apply_async(soup_list)
    # parallelism_testing.map(soup_list)
    # parallelism_testing.chunk_apply_async(soup_list, 3)
    # parallelism_testing.chunk_apply_async(soup_list, 1000)
    # parallelism_testing.chunk_map(soup_list, 10)
    # parallelism_testing.multithread(soup_list)
    
    # STEP4: Save the extracted information (list of dictionaries) to json and csv files
    print("step 4: save extracted information")
    df = pd.DataFrame(unit_list[:])
    print(df.head())
    if not df.empty:
        df = df.drop_duplicates()
        df.to_json(os.path.join(result_path, "result.json"), orient='records', lines=True)
        df.to_csv(os.path.join(result_path, "result.csv"), index=False)
        # re-create table and dump the new data
        if not args.no_dump_db:
            print("store to db")
            # db_functions.regenerate_table_schema('unit', DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
            db_functions.dump_df_to_db(df, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

if __name__ == '__main__':
    main()