import os
import configparser
import requests
from bs4 import BeautifulSoup

# Read config file
config = configparser.ConfigParser()
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, '../../config/config.ini')
config.read(config_path)
URL = config['user_config']['URL']
chromedriver = config['user_config']['chromedriver_dir']

