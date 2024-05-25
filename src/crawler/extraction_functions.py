import re

def name(soup, selector):
    name_soup = soup.select_one(selector)
    return name_soup.get_text(strip=True) if name_soup else ""

def tel(soup, selector):
    tel_soup = soup.select_one(selector)
    return tel_soup.get_text(strip=True) if tel_soup else ""

def address(soup, selector):
    address_soup = soup.select_one(selector)
    return address_soup.get_text(strip=True) if address_soup else ""

def city(soup, selector):
    city_soup = soup.select_one(selector)
    return city_soup.get_text(strip=True) if city_soup else ""

def state(soup, selector):
    state_soup = soup.select_one(selector)
    return state_soup.get_text(strip=True) if state_soup else ""

def zip(soup, selector):
    zip_soup = soup.select_one(selector)
    return zip_soup.get_text(strip=True) if zip_soup else ""

def neighborhood(soup, selector):
    neighborhood_soup = soup.select_one(selector)
    return neighborhood_soup.get_text(strip=True) if neighborhood_soup else ""

def built_units_stories(soup, selector):
    unitsstories_soup = soup.select_one(selector)
    if unitsstories_soup:
        content = unitsstories_soup.get_text()
        built_regex = re.compile(r'(Built in)(\s+)(\d+)')
        built_match = built_regex.search(content)
        built = built_match.group(3) if built_match else 0
        units_regex = re.compile(r'(\d+)(\s+)(units)')
        units_match = units_regex.search(content)
        units = units_match.group(1) if units_match else 0
        stories_regex = re.compile(r'(\d+)(\s+)(stories)')
        stories_match = stories_regex.search(content)
        stories = stories_match.group(1) if stories_match else 0
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
            management = ""
    else:
        management = ""
    return management

def beds(soup, selector):
    beds_soup = soup.select_one(selector)
    if beds_soup:
        beds = beds_soup.get_text(strip=True)
        beds_regex = re.compile(r'(\d+)(\s+)(bed)')
        beds_match = beds_regex.search(beds)
        beds = beds_match.group(1) if beds_match else 0
    else:
        beds = 0
    return beds

def baths(soup, selector):
    baths_soup = soup.select_one(selector)
    if baths_soup:
        baths = baths_soup.get_text(strip=True)
        baths_regex = re.compile(r'(\d+)(\s+)(bath)')
        baths_match = baths_regex.search(baths)
        baths = baths_match.group(1) if baths_match else 0
    else:
        baths = 0
    return baths

def unit_no(soup, selector):
    unit_no_soup = soup.select_one(selector)
    return unit_no_soup.get_text(strip=True) if unit_no_soup else ""

def unit_price(soup, selector):
    unit_price_soup = soup.select_one(selector)
    return int(unit_price_soup.get_text(strip=True).replace('$', '').replace(',', '')) if unit_price_soup else ""

def unit_sqft(soup, selector):
    unit_sqft_soup = soup.select_one(selector)
    return int(unit_sqft_soup.get_text(strip=True).replace(',', '')) if unit_sqft_soup else ""

def unit_avail(soup, selector):
    unit_avail_soup = soup.select_one(selector)
    if unit_avail_soup:
        unit_avail_soup = unit_avail_soup.get_text(strip=True)
        if unit_avail_soup.split(' ')[-1].isdigit():
            unit_avail = unit_avail_soup.split(' ')[-2] + ' ' + unit_avail_soup.split(' ')[-1]
        else:
            unit_avail = unit_avail_soup.split(' ')[-1]
    else:
        unit_avail = ""
    return unit_avail
