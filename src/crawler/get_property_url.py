import os
import configparser
from bs4 import BeautifulSoup
import requests

def get_property_urls(URL, output_path):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7","Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7","Accept-Encoding": "gzip, deflate, br, zstd"}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_links = []
    pages = soup.find('p', {'class': "searchResults"}).find('span').text.split(' ')[-1]

    # Get all links from all pages
    for page in range(1, int(pages)+1):
        print("processing page: ", page)
        response = requests.get(URL+'/'+str(page), headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', {'class': "property-link"})
        unique_links = list(set(link['href'] for link in links))
        all_links.extend(unique_links)
    # Save all links to json file
    with open(output_path, 'wb') as f:
        f.write(str(all_links).encode('utf-8'))

def get_property_info(URL):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7","Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7","Accept-Encoding": "gzip, deflate, br, zstd"}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

def main():
    # Read config file
    config = configparser.ConfigParser()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '../../config/config.ini')
    config.read(config_path)
    search_URL = config['user_config']['search_URL']
    chromedriver = config['user_config']['chromedriver_dir'] 

    property_urls_path = os.path.join(current_dir, '../../data/properties_links.json')
    get_property_urls(search_URL, property_urls_path)

if __name__ == '__main__':
    main()