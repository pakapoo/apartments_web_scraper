# This is a backup file for testing different parallelism techniques
import time
import pandas as pd
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
from web_scraper import extract_property_info_wrapper, extract_property_info
import utils
import os
import pickle

POOL_SIZE = os.cpu_count()
CHUNK_MULTIPLES = 3
current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.abspath(current_dir)
result_path = os.path.join(base_dir, "../../data/")

@utils.time_stats
def non_parallel(soup_list):
    unit_list = []
    for soup in soup_list:
        extract_property_info(soup, unit_list)
    print("length", len(unit_list))
    df = pd.DataFrame(unit_list[:])
    df.to_csv(f"{result_path}df1.csv", index=False)
    return unit_list

@utils.time_stats
def apply_async(soup_list):
    pool = mp.Pool(POOL_SIZE)
    manager = mp.Manager()
    mp_unit_list = manager.list()
    # a1 = time.time()
    for soup in soup_list:
        pool.apply_async(func=extract_property_info, args=(soup, mp_unit_list))
    pool.close()
    pool.join()
    # elapsed_time = time.time() - a1
    # print(f"test: {elapsed_time:.4f} seconds")
    # print("length", len(mp_unit_list))
    df = pd.DataFrame(mp_unit_list[:])
    df.to_csv(f"{result_path}df2.csv", index=False)
    return mp_unit_list

@utils.time_stats
def map(soup_list):
    pool = mp.Pool(POOL_SIZE)
    results = pool.map(func=extract_property_info_map, iterable=soup_list)
    pool.close()
    pool.join()
    mp_unit_list = [item for sublist in results for item in sublist]
    print("length", len(mp_unit_list))
    df = pd.DataFrame(mp_unit_list[:])
    df.to_csv(f"{result_path}df3.csv", index=False)
    return mp_unit_list

@utils.time_stats
def chunk_apply_async(soup_list, CHUNK_MULTIPLES):
    pool = mp.Pool(POOL_SIZE)
    manager = mp.Manager()
    mp_unit_list = manager.list()
    l = len(soup_list)
    chunk_size = max(1, l // (POOL_SIZE*CHUNK_MULTIPLES))
    chunked_soup_lists = [soup_list[i:i + chunk_size] for i in range(0, len(soup_list), chunk_size)]
    # a1 = time.time()
    print(len(chunked_soup_lists))
    for chunked_soup_list in chunked_soup_lists[:25]:
        pool.apply_async(func=extract_property_info_wrapper, args=(chunked_soup_list, mp_unit_list))
    pool.close()
    pool.join()
    # elapsed_time = time.time() - a1
    # print(f"test: {elapsed_time:.4f} seconds")
    # print("length", len(mp_unit_list))
    df = pd.DataFrame(mp_unit_list[:])
    df.to_csv(f"{result_path}df4_{CHUNK_MULTIPLES}.csv", index=False)
    return mp_unit_list

@utils.time_stats
def chunk_map(soup_list, chunksize):
    pool = mp.Pool(POOL_SIZE)
    results = pool.map(func=extract_property_info_map, iterable=soup_list, chunksize=chunksize)
    pool.close()
    pool.join()
    mp_unit_list = [item for sublist in results for item in sublist]
    print("length", len(mp_unit_list))
    df = pd.DataFrame(mp_unit_list[:])
    df.to_csv(f"{result_path}df5_{chunksize}.csv", index=False)
    return mp_unit_list

@utils.time_stats
def multithread(soup_list):
    mt_unit_list = []
    with ThreadPoolExecutor(max_workers=POOL_SIZE) as executor:
        futures = [executor.submit(extract_property_info, soup, mt_unit_list) for soup in soup_list]
        for future in futures:
            future.result()  # This waits for all the results
    print("length", len(mt_unit_list))
    df = pd.DataFrame(mt_unit_list[:])
    df.to_csv(f"{result_path}df6.csv", index=False)
    return mt_unit_list

# def extract_property_info_map(data):
#     """
#     Extract property information from the soup object and store in a list of dictionary shared among multi-processes.

#     Parameters:
#     soup (BeautifulSoup): The soup object to extract information from.
#     columns (list): A list of column names for the DataFrame.
#     unit_list (list): A list to store the extracted information.

#     Returns:
#     None
#     """
#     tmp_unit_list = []
#     soup = BeautifulSoup(data[1], 'html.parser')
#     # soup = data[1]

#     # extract property info
#     id = data[0].split('/')[-2]
#     url = data[0].strip()
#     name = custom_extraction_functions.name(soup, NAME_SELECTOR)
#     tel = custom_extraction_functions.tel(soup, TEL_SELECTOR)
#     address = custom_extraction_functions.address(soup, ADDRESS_SELECTOR)
#     city = custom_extraction_functions.city(soup, CITY_SELECTOR)
#     state = custom_extraction_functions.state(soup, STATE_SELECTOR)
#     zip = custom_extraction_functions.zip(soup, ZIP_SELECTOR)
#     neighborhood = custom_extraction_functions.neighborhood(soup, NEIGHBORHOOD_SELECTOR)
#     built, units, stories = custom_extraction_functions.built_units_stories(soup, BUILT_UNITS_STORIES_SELECTOR)
#     management = custom_extraction_functions.management(soup, MANAGEMENT_SELECTOR)
#     # extract units info
#     plan_info = soup.select(PLAN_SELECTOR)
#     for plan in plan_info:
#         unit_beds = custom_extraction_functions.beds(plan, UNIT_BEDS_SELECTOR)
#         unit_baths = custom_extraction_functions.baths(plan, UNIT_BATHS_SELECTOR)
#         unit_info = plan.select(UNIT_SELECTOR)
#         for unit in unit_info:
#             unit_no = custom_extraction_functions.unit_no(unit, UNIT_NO_SELECTOR)
#             unit_price = custom_extraction_functions.unit_price(unit, UNIT_PRICE_SELECTOR1, UNIT_PRICE_SELECTOR2)
#             unit_sqft = custom_extraction_functions.unit_sqft(unit, UNIT_SQFT_SELECTOR)
#             unit_avail = custom_extraction_functions.unit_avail(unit, UNIT_AVAIL_SELECTOR)
#             unit_data = Unit(id, url, name, tel, address, city, state, zip, neighborhood, built, units, stories, management, unit_no, unit_beds, unit_baths, unit_price, unit_sqft, unit_avail)
#             tmp_unit_list.append(vars(unit_data))
#     return tmp_unit_list

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(current_dir)
    print(base_dir)
    with open(f"{base_dir}/soup_list_mid_soup.pkl", "rb") as f:
        soup_list = pickle.load(f)

    non_parallel(soup_list)
    apply_async(soup_list)
    map(soup_list)
    chunk_apply_async(soup_list, 3)
    chunk_apply_async(soup_list, 10)
    # chunk_map(soup_list, 10)
    # chunk_map(soup_list, 30)
    multithread(soup_list)
    pass