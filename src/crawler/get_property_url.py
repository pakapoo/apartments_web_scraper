import os
import configparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
import multiprocessing as mp

import extraction_functions

def get_property_urls(url, output_path):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7","Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7","Accept-Encoding": "gzip, deflate, br, zstd"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_links = []

    # Get number of pages for this search URL
    try:
        pages = soup.select_one("p.searchResults > span").text.split(' ')[-1]
        # testing
        pages = 2
    except:
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
    print("{} property urls are scraped.".format(len(all_links)))

def get_property_html(urls_file, html_store_path):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7","Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7","Accept-Encoding": "gzip, deflate, br, zstd"}
    with open(urls_file, 'rb') as f:
        urls = eval(f.read().decode('utf-8'))
        for url in urls:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            with open(os.path.join(html_store_path, url.split('/')[-3]+'.html'), 'wb') as f:
                f.write(soup.prettify().encode('utf-8'))

def test_property_html(urls_file, html_store_path):
    for _, _, files in os.walk(html_store_path):
        with open(urls_file, 'rb') as f:
            urls = eval(f.read().decode('utf-8'))
            urls_not_scraped = set([url.split('/')[-3] for url in urls]) - set([file.split('.')[-2] for file in files])
            if urls_not_scraped:
                print("The following url are not scraped: {}.".format(urls_not_scraped))
                print("This may due to removal of the property or the website has changed.")
            else:
                print("All urls are scraped.")

def extract_property_info(html_store_path, info_store_path):
    for _, _, files in os.walk(html_store_path):
        for file in files:
            df = pd.DataFrame(columns=['name', 
                                       'tel', 
                                       'address',
                                       'city',
                                       'state',
                                       'zip',
                                       'neighborhood',
                                       'built',
                                       'units', 
                                       'stories',
                                       'management',
                                       'unit_no',
                                       'unit_beds',
                                       'unit_baths',
                                       'unit_price', 
                                       'unit_sqft', 
                                       'unit_avail'])
            soup = BeautifulSoup(open(os.path.join(html_store_path, file), 'rb'), 'html.parser')
            
            # extract property info
            name = extraction_functions.name(soup, "h1.propertyName")
            tel = extraction_functions.tel(soup, "div.phoneNumber span")
            address = extraction_functions.address(soup, "div.propertyAddressContainer span.delivery-address span:nth-child(1)")
            city = extraction_functions.city(soup, "div.propertyAddressContainer span:nth-child(2)")
            state = extraction_functions.state(soup, "div.propertyAddressContainer span.stateZipContainer span:nth-child(1)")
            zip = extraction_functions.zip(soup, "div.propertyAddressContainer span.stateZipContainer span:nth-child(2)")
            neighborhood = extraction_functions.neighborhood(soup, "div.propertyAddressContainer span.neighborhoodAddress > a")
            built, units, stories = extraction_functions.built_units_stories(soup, "section.feesSection.feesSectionV2.js-viewAnalyticsSection div#profileV2FeesWrapper > div:nth-child(3) > div:nth-child(2)")
            management = extraction_functions.management(soup, "img.logo")

            # extract units info
            plan_info = soup.select("div.pricingGridItem.multiFamily.hasUnitGrid")
            for plan in plan_info:
                unit_beds = extraction_functions.beds(plan, "span.detailsTextWrapper > span:nth-child(1)")
                unit_baths = extraction_functions.baths(plan, "span.detailsTextWrapper > span:nth-child(2)")
                unit_info = plan.select("li.unitContainer.js-unitContainer")
                for unit in unit_info:
                    unit_no = extraction_functions.unit_no(unit, "div.unitColumn.column span:nth-child(2)")
                    unit_price = extraction_functions.unit_price(unit, "div.pricingColumn.column span:nth-child(2)")
                    unit_sqft = extraction_functions.unit_sqft(unit, "div.sqftColumn.column span:nth-child(2)")
                    unit_avail = extraction_functions.unit_avail(unit, "div.availableColumn.column span:nth-child(1)")
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
                                            unit_avail]], columns=df.columns)
                    df = pd.concat([df, curr_unit], ignore_index=True)

            # save to json and csv
            if not df.empty:
                df = df.drop_duplicates()
                df.to_json(os.path.join(info_store_path, "json", file.split('.')[-2]+".json"), orient='records', lines=True)
                df.to_csv(os.path.join(info_store_path, "csv", file.split('.')[-2]+".csv"), index=False)

def compile_and_export_results(info_store_path, result_file):
    pass

def main():
    # Read config file
    config = configparser.ConfigParser()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '../../config/config.ini')
    config.read(config_path)
    search_URL = config['user_config']['search_URL']
    chromedriver = config['user_config']['chromedriver_dir']
    
    # Set up input and output paths
    property_urls_file = os.path.join(current_dir, '../../data/property_urls.json')
    property_html_path = os.path.join(current_dir, '../../data/property_html/')
    property_info_path = os.path.join(current_dir, '../../data/property_info/')
    result_file = os.path.join(current_dir, '../../data/results.csv')

    #get_property_urls(search_URL, property_urls_file)
    #get_property_html(property_urls_file, property_html_path)
    #test_property_html(property_urls_file, property_html_path)
    extract_property_info(property_html_path, property_info_path)
    compile_and_export_results(property_info_path, result_file)

if __name__ == '__main__':
    main()