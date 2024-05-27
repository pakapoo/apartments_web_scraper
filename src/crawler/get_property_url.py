import os
import configparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import multiprocessing as mp
import custom_extraction_functions

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

def get_property_urls(url, output_path):
    """
    Fetches property URLs from the given search URL and stores them in the specified file.

    Parameters:
    search_URL (str): The URL to fetch property URLs from.
    property_urls_file (str): The file to store the fetched property URLs.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7","Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7","Accept-Encoding": "gzip, deflate, br, zstd"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_links = []

    # Get number of pages for this search URL
    try:
        pages = soup.select_one("p.searchResults > span").text.split(' ')[-1]
        # testing
        pages = 2
    except AttributeError:
        print("No pages information found.")
        pages = 1
    # Loop through all pages and scrape the property links
    for page in range(1, int(pages)+1):
        print("processing page: ", page)
        response = requests.get(url+'/'+str(page), headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.select("a.property-link")
        unique_links = list(set(link['href'] for link in links))
        all_links.extend(unique_links)
    # Save all links to json file
    with open(output_path, 'wb') as f:
        f.write(str(all_links).encode('utf-8'))
    print("{} urls are scraped.".format(len(all_links)))

def get_property_html(urls_file, html_store_path):
    """
    Fetches the HTML of the properties whose URLs are stored in the specified file and stores the HTML in the specified directory.

    Parameters:
    property_urls_file (str): The file containing the property URLs.
    property_html_path (str): The directory to store the fetched HTML.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7","Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7","Accept-Encoding": "gzip, deflate, br, zstd"}
    with open(urls_file, 'rb') as f:
        urls = eval(f.read().decode('utf-8'))
        for url in urls:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            with open(os.path.join(html_store_path, url.split('/')[-3]+'.html'), 'wb') as f:
                f.write(soup.prettify().encode('utf-8'))

def test_property_html(urls_file, html_store_path):
    """
    Tests the fetched HTML of the properties whose URLs are stored in the specified file.

    Parameters:
    property_urls_file (str): The file containing the property URLs.
    property_html_path (str): The directory containing the fetched HTML.
    """
    for _, _, files in os.walk(html_store_path):
        with open(urls_file, 'rb') as f:
            urls = eval(f.read().decode('utf-8'))
            urls_not_scraped = set([url.split('/')[-3] for url in urls]) - set([file.split('.')[-2] for file in files])
            if urls_not_scraped:
                print("The following url are not scraped: {}.".format(urls_not_scraped))
                print("This may due to removal of the property or the website has changed.")
            else:
                print("All urls are scraped successfully.")

def extract_property_info(html_store_path, file, info_store_path, cols):
    """
    Extract property information from the HTML files stored in the given path.

    Parameters:
    html_store_path (str): The path where the HTML files are stored.
    file (str): The name of the HTML file to process.
    info_store_path (str): The path where the extracted information should be stored.
    cols (list): The columns for the DataFrame that will store the extracted information.

    Returns:
    df (DataFrame): A DataFrame containing the extracted information.
    """
    df = pd.DataFrame(columns=cols)
    soup = BeautifulSoup(open(os.path.join(html_store_path, file), 'rb'), 'html.parser')
    mtime = os.stat(os.path.join(html_store_path, file)).st_mtime
    dttm = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

    # extract property info
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
            unit_price = custom_extraction_functions.unit_price(unit, UNIT_PRICE_SELECTOR)
            unit_sqft = custom_extraction_functions.unit_sqft(unit, UNIT_SQFT_SELECTOR)
            unit_avail = custom_extraction_functions.unit_avail(unit, UNIT_AVAIL_SELECTOR)
            curr_unit = pd.DataFrame([[name, 
                                    tel, 
                                    address,
                                    city,
                                    state,
                                    zip,
                                    neighborhood,
                                    built,
                                    units,
                                    stories,
                                    management,
                                    unit_no, 
                                    unit_beds, 
                                    unit_baths, 
                                    unit_price, 
                                    unit_sqft, 
                                    unit_avail,
                                    dttm]], columns=cols)
            df = pd.concat([df, curr_unit], ignore_index=True)

    # save to json and csv
    if not df.empty:
        df = df.drop_duplicates()
        df.to_json(os.path.join(info_store_path, "json", file.split('.')[-2]+".json"), orient='records', lines=True)
        df.to_csv(os.path.join(info_store_path, "csv", file.split('.')[-2]+".csv"), index=False)

def compile_and_export_results(info_store_path, result_file):
    """
    Compiles and exports the extracted property information.

    Parameters:
    property_info_path (str): The path where the extracted information is stored.
    result_file (str): The file to export the compiled results to.
    """
    pass

def cleanup_dir(path):
    """
    Cleans up the specified directory by removing all files in it.

    Parameters:
    directory_path (str): The path to the directory to clean up.
    """
    for root, _, files in os.walk(path):
        for file in files:
            try:
                os.remove(os.path.join(root, file))
            except OSError as e:
                print(f"Error: {e.filename} - {e.strerror}.")

def main():
    # Read config file
    config = configparser.ConfigParser()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, '../../'))
    config_path = os.path.join(base_dir, 'config/config.ini')
    config.read(config_path)
    search_URL = config['user_config']['search_URL']
    chromedriver = config['user_config']['chromedriver_dir']

    # Set up input and output paths
    property_urls_file = os.path.join(base_dir, 'data/property_urls.json')
    property_html_path = os.path.join(base_dir, 'data/property_html/')
    property_info_path = os.path.join(base_dir, 'data/property_info/')
    result_file = os.path.join(base_dir, 'data/results.csv')

    # STEP1: Get property URLs
    get_property_urls(search_URL, property_urls_file)

    # STEP2: Get property HTML
    cleanup_dir(property_html_path)
    get_property_html(property_urls_file, property_html_path)
    test_property_html(property_urls_file, property_html_path)

    # STEP3: Extract property info
    cleanup_dir(property_info_path)
    columns = ['name', 'tel', 'address', 'city', 'state', 'zip', 'neighborhood', 'built', 'units', 'stories', 'management', 'unit_no', 'unit_beds', 'unit_baths', 'unit_price', 'unit_sqft', 'unit_avail', 'dttm']
    pool = mp.Pool(POOL_SIZE)
    for _, _, files in os.walk(property_html_path):
        for file in files:
            pool.apply_async(extract_property_info, args=(property_html_path, file, property_info_path, columns))
    pool.close()
    pool.join()

    # STEP4: Compile and export results
    compile_and_export_results(property_info_path, result_file)

if __name__ == '__main__':
    main()