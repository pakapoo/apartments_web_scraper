import re
from datetime import datetime
import os

def cleanup_dir(directory_path):
    """
    Cleans up the specified directory by removing all files in it.

    Parameters:
    directory_path (str): The path to the directory to clean up.
    """
    for root, _, files in os.walk(directory_path):
        for file in files:
            try:
                os.remove(os.path.join(root, file))
            except OSError as e:
                print(f"Error: {e.filename} - {e.strerror}.")

def name(soup, selector):
    name_soup = soup.select_one(selector)
    return name_soup.get_text(strip=True) if name_soup else None

def tel(soup, selector):
    tel_soup = soup.select_one(selector)
    return tel_soup.get_text(strip=True) if tel_soup else None

def address(soup, selector):
    address_soup = soup.select_one(selector)
    return address_soup.get_text(strip=True) if address_soup else None

def city(soup, selector):
    city_soup = soup.select_one(selector)
    return city_soup.get_text(strip=True) if city_soup else None

def state(soup, selector):
    state_soup = soup.select_one(selector)
    return state_soup.get_text(strip=True) if state_soup else None

def zip(soup, selector):
    zip_soup = soup.select_one(selector)
    return zip_soup.get_text(strip=True) if zip_soup else None

def neighborhood(soup, selector):
    neighborhood_soup = soup.select_one(selector)
    return neighborhood_soup.get_text(strip=True) if neighborhood_soup else None

def built_units_stories(soup, selector):
    unitsstories_soup = soup.select_one(selector)
    if unitsstories_soup:
        content = unitsstories_soup.get_text("|", strip=True)
        built_regex = re.compile(r'(Built in)(\s+)(\d+)')
        built_match = built_regex.search(content)
        built = int(built_match.group(3)) if built_match else 0
        units_regex = re.compile(r'(\d+)(\s+)(units)')
        units_match = units_regex.search(content)
        units = int(units_match.group(1)) if units_match else 0
        stories_regex = re.compile(r'(\d+)(\s+)(stories)')
        stories_match = stories_regex.search(content)
        stories = int(stories_match.group(1)) if stories_match else 0
    else:
        built, units, stories = 0, 0, 0
    return built, units, stories


def management(soup, selector):
    management_soup = soup.select_one(selector)
    if management_soup:
        try:
            management_soup = re.split(r'\/|\.', management_soup['src'])[-2]
            management = ' '.join(management_soup.replace('-', ' ').split(' ')[:-2])
        except:
            management = None
    else:
        management = None
    return management

def beds(soup, selector):
    beds_soup = soup.select_one(selector)
    if beds_soup:
        beds = beds_soup.get_text(strip=True)
        beds_regex = re.compile(r'(\d+)(\s+)(bed)')
        beds_match = beds_regex.search(beds)
        beds = int(beds_match.group(1)) if beds_match else 0
    else:
        beds = 0
    return beds

def baths(soup, selector):
    baths_soup = soup.select_one(selector)
    if baths_soup:
        baths = baths_soup.get_text(strip=True)
        baths_regex = re.compile(r'(\d+)(\s+)(bath)')
        baths_match = baths_regex.search(baths)
        baths = int(baths_match.group(1)) if baths_match else 0
    else:
        baths = 0
    return baths

def unit_no(soup, selector):
    unit_no_soup = soup.select_one(selector)
    return unit_no_soup.get_text(strip=True) if unit_no_soup else None

def unit_price(soup, selector):
    unit_price_soup = soup.select_one(selector)
    if unit_price_soup:
        try:
            unit_price_tmp = int(unit_price_soup.get_text(strip=True).replace('$', '').replace(',', ''))
        except:
            unit_price_tmp = None
    return unit_price_tmp if unit_price_soup else None

def unit_sqft(soup, selector):
    unit_sqft_soup = soup.select_one(selector)
    return int(unit_sqft_soup.get_text(strip=True).replace(',', '')) if unit_sqft_soup else None

def unit_avail(soup, selector):
    unit_avail_soup = soup.select_one(selector)
    year = datetime.today().year
    if unit_avail_soup:
        unit_avail_soup = unit_avail_soup.get_text('|', strip=True).split('|')[-1].strip()
        if unit_avail_soup.split(' ')[-1].isdigit():
            unit_avail = datetime.strptime(str(year) + unit_avail_soup,'%Y%b. %d').strftime('%Y%m%d')
        elif unit_avail_soup.split(' ')[-1] == "Now":
            unit_avail = datetime.today().strftime('%Y%m%d')
        else:
            None
    else:
        unit_avail = None
    return unit_avail
