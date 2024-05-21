import os
import configparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
import multiprocessing as mp

def get_property_urls(url, output_path):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7","Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7","Accept-Encoding": "gzip, deflate, br, zstd"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_links = []

    # Get all links from all pages
    pages = soup.select_one("p.searchResults > span").text.split(' ')[-1]
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
            df = pd.DataFrame(columns=['unit', 'beds', 'baths', 'maxrent', 'sqft', 'availability'])
            soup = BeautifulSoup(open(os.path.join(html_store_path, file), 'rb'), 'html.parser')
        # with open(os.path.join(info_store_path, "venture-madison-wi.json"), 'wb') as f:
        #    soup = BeautifulSoup(open(os.path.join(html_store_path, "venture-madison-wi.html"), 'rb'), 'html.parser')
            unit_info = soup.select("li.unitContainer.js-unitContainer")
            for unit in unit_info:
                # extract sqft info
                sqft_info = unit.select_one("div.sqftColumn.column")
                sqft = sqft_info.text.strip().split(' ')[-1]
                # extract availability info
                avail_info = unit.select_one("span.dateAvailable")
                if avail_info.text.strip().split(' ')[-1].isdigit():
                    availability = avail_info.text.strip().split(' ')[-2]+' '+avail_info.text.strip().split(' ')[-1]
                else:
                    availability = avail_info.text.strip().split(' ')[-1]
                curr_unit = pd.DataFrame([[unit['data-unit'], unit['data-beds'], unit['data-baths'], unit['data-maxrent'], sqft, availability]], columns=df.columns)
                df = pd.concat([df, curr_unit], ignore_index=True)
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

    get_property_urls(search_URL, property_urls_file)
    get_property_html(property_urls_file, property_html_path)
    test_property_html(property_urls_file, property_html_path)
    extract_property_info(property_html_path, property_info_path)
    compile_and_export_results(property_info_path, result_file)

if __name__ == '__main__':
    main()