import os
import configparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import multiprocessing as mp
import custom_extraction_functions

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

PLAN_SELECTOR = "div.pricingGridItem.multiFamily.hasUnitGrid"
UNIT_SELECTOR = "li.unitContainer.js-unitContainer"

UNIT_BEDS_SELECTOR = "span.detailsTextWrapper > span:nth-child(1)"
UNIT_BATHS_SELECTOR = "span.detailsTextWrapper > span:nth-child(2)"
UNIT_NO_SELECTOR = "div.unitColumn.column span:nth-child(2)"
UNIT_PRICE_SELECTOR = "div.pricingColumn.column span:nth-child(2)"
UNIT_SQFT_SELECTOR = "div.sqftColumn.column span:nth-child(2)"
UNIT_AVAIL_SELECTOR = "div.availableColumn.column span:nth-child(1)"

POOL_SIZE = os.cpu_count()

class Property:
    def __init__(self, id, name, tel, address, city, state, zip, neighborhood, built, units, stories, management):
        self.id = id
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
    def __init__(self, id, name, tel, address, city, state, zip, neighborhood, built, units, stories, management, unit_no, unit_beds, unit_baths, unit_price, unit_sqft, unit_avail):
        super().__init__(self, id, name, tel, address, city, state, zip, neighborhood, built, units, stories, management)
        self.unit_no = unit_no
        self.unit_beds = unit_beds
        self.unit_baths = unit_baths
        self.unit_price = unit_price
        self.unit_sqft = unit_sqft
        self.unit_avail = unit_avail
    
    def __dict__(self):
        return {'id': self.id, 'name': self.name, 'tel': self.tel, 'address': self.address, 'city': self.city, 'state': self.state, 'zip': self.zip, 'neighborhood': self.neighborhood, 'built': self.built, 'units': self.units, 'stories': self.stories, 'management': self.management, 'unit_no': self.unit_no, 'unit_beds': self.unit_beds, 'unit_baths': self.unit_baths, 'unit_price': self.unit_price, 'unit_sqft': self.unit_sqft, 'unit_avail': self.unit_avail}

def get_property_urls(search_URL):
    """
    Fetches property URLs from the given search URL and stores them in a list.

    Parameters:
    search_URL (str): The URL to fetch property URLs from.

    Returns:
    all_links (list): A list of property URLs.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7","Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7","Accept-Encoding": "gzip, deflate, br, zstd"}
    response = requests.get(search_URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_links = []

    # Get number of pages for this search URL
    try:
        pages = soup.select_one(PAGE_NUMBER_SELECTOR).text.split(' ')[-1]
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

def get_property_html(all_links):
    """
    Get the HTML for each property URL as soup object, and store them in a list.

    Parameters:
    all_links (list): A list of URLs to fetch HTML from.

    Returns:
    soup_list (list): A list of soup objects.
    """
    soup_list = []
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7","Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7","Accept-Encoding": "gzip, deflate, br, zstd"}
    for count, url in enumerate(all_links):
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        soup_list.append((url, soup))
        if count == (len(all_links)-1):
            print("All {} urls are processed!".format(count + 1)) 
        elif (count+1) % 10 == 0 and count != 0:
            print("{} urls processed".format(count + 1))
    return soup_list

def extract_property_info(soup, unit_list):
    """
    Extract property information from the soup object and store in a list of dictionary shared among multi-processes.

    Parameters:
    soup (BeautifulSoup): The soup object to extract information from.
    columns (list): A list of column names for the DataFrame.
    unit_list (list): A list to store the extracted information.

    Returns:
    None
    """
    # extract property info
    id = soup[0].split('/')[-2]
    name = custom_extraction_functions.name(soup[1], NAME_SELECTOR)
    tel = custom_extraction_functions.tel(soup[1], TEL_SELECTOR)
    address = custom_extraction_functions.address(soup[1], ADDRESS_SELECTOR)
    city = custom_extraction_functions.city(soup[1], CITY_SELECTOR)
    state = custom_extraction_functions.state(soup[1], STATE_SELECTOR)
    zip = custom_extraction_functions.zip(soup[1], ZIP_SELECTOR)
    neighborhood = custom_extraction_functions.neighborhood(soup[1], NEIGHBORHOOD_SELECTOR)
    built, units, stories = custom_extraction_functions.built_units_stories(soup[1], BUILT_UNITS_STORIES_SELECTOR)
    management = custom_extraction_functions.management(soup[1], MANAGEMENT_SELECTOR)

    # extract units info
    plan_info = soup[1].select(PLAN_SELECTOR)
    for plan in plan_info:
        unit_beds = custom_extraction_functions.beds(plan, UNIT_BEDS_SELECTOR)
        unit_baths = custom_extraction_functions.baths(plan, UNIT_BATHS_SELECTOR)
        unit_info = plan.select(UNIT_SELECTOR)
        for unit in unit_info:
            unit_no = custom_extraction_functions.unit_no(unit, UNIT_NO_SELECTOR)
            unit_price = custom_extraction_functions.unit_price(unit, UNIT_PRICE_SELECTOR)
            unit_sqft = custom_extraction_functions.unit_sqft(unit, UNIT_SQFT_SELECTOR)
            unit_avail = custom_extraction_functions.unit_avail(unit, UNIT_AVAIL_SELECTOR)
            unit_data = Unit(id, name, tel, address, city, state, zip, neighborhood, built, units, stories, management, unit_no, unit_beds, unit_baths, unit_price, unit_sqft, unit_avail)
            unit_list.append(vars(unit_data))
            
def main():
    start_time = time.time()
    # Set paths    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, '../../'))
    result_path = os.path.join(base_dir, 'data/result/')

    # Read config file
    config = configparser.ConfigParser()
    config_path = os.path.join(base_dir, 'config/config.ini')
    config.read(config_path)
    search_URL = config['user_config']['search_URL']
    chromedriver = config['user_config']['chromedriver_dir']

    # STEP1: Get property URLs
    all_links = get_property_urls(search_URL)

    # STEP2: Get property HTML
    soup_list = get_property_html(all_links)

    # STEP3: Extract property information
    pool = mp.Pool(POOL_SIZE)
    manager = mp.Manager()
    unit_list = manager.list()
    for soup in soup_list:
        pool.apply_async(func=extract_property_info, args=(soup, unit_list))
    pool.close()
    pool.join()
    
    # STEP4: Save the extracted information (list of dictionaries) to json and csv files
    df = pd.DataFrame(unit_list[:])
    if not df.empty:
        df = df.drop_duplicates()
        df.to_json(os.path.join(result_path, "result.json"), orient='records', lines=True)
        df.to_csv(os.path.join(result_path, "result.csv"), index=False)

    print("Execution time: ", time.time()-start_time)

if __name__ == '__main__':
    main()