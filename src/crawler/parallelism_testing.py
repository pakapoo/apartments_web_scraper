# This is a backup file for testing different parallelism techniques
import time
import pandas as pd
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
from web_scraper import extract_property_info_wrapper, extract_property_info, extract_property_info_map
import utils
import os

POOL_SIZE = os.cpu_count()
CHUNK_MULTIPLES = 3
result_path = "./"

@utils.time_stats
def non_parallel(soup_list):
    print("------non parallel------")
    unit_list = []
    for soup in soup_list:
        extract_property_info(soup, unit_list)
    print("length", len(unit_list))
    df = pd.DataFrame(unit_list[:])
    df.to_csv(f"{result_path}/df1.csv", index=False)
    return unit_list

@utils.time_stats
def apply_async(soup_list):
    print("------apply_async------")
    pool = mp.Pool(POOL_SIZE)
    manager = mp.Manager()
    mp_unit_list = manager.list()
    for soup in soup_list:
        pool.apply_async(func=extract_property_info, args=(soup, mp_unit_list))
    pool.close()
    pool.join()
    print("length", len(mp_unit_list))
    df = pd.DataFrame(mp_unit_list[:])
    print(f"{result_path}/df2.csv")
    df.to_csv(f"{result_path}df2.csv", index=False)
    return mp_unit_list

@utils.time_stats
def map(soup_list):
    print("------map------")
    pool = mp.Pool(POOL_SIZE)
    results = pool.map(func=extract_property_info_map, iterable=soup_list)
    pool.close()
    pool.join()
    mp_unit_list = [item for sublist in results for item in sublist]
    print("length", len(mp_unit_list))
    df = pd.DataFrame(mp_unit_list[:])
    df.to_csv(f"{result_path}/df3.csv", index=False)
    return mp_unit_list

@utils.time_stats
def chunk_apply_async(soup_list, CHUNK_MULTIPLES):
    print("------chunk_apply_async------")
    pool = mp.Pool(POOL_SIZE)
    manager = mp.Manager()
    mp_unit_list = manager.list()
    l = len(soup_list)
    chunk_size = max(1, l // (POOL_SIZE*CHUNK_MULTIPLES))
    chunked_soup_lists = [soup_list[i:i + chunk_size] for i in range(0, len(soup_list), chunk_size)]
    print(f"chunk size: {chunk_size}")
    for chunked_soup_list in chunked_soup_lists:
        pool.apply_async(func=extract_property_info_wrapper, args=(chunked_soup_list, mp_unit_list))
    pool.close()
    pool.join()
    print("length", len(mp_unit_list))
    df = pd.DataFrame(mp_unit_list[:])
    df.to_csv(f"{result_path}/df4.csv", index=False)
    return mp_unit_list

@utils.time_stats
def multithread(soup_list):
    print("------multithread------")
    mt_unit_list = []
    with ThreadPoolExecutor(max_workers=POOL_SIZE) as executor:
        futures = [executor.submit(extract_property_info, soup, mt_unit_list) for soup in soup_list]
        for future in futures:
            future.result()  # This waits for all the results
    print("length", len(mt_unit_list))
    df = pd.DataFrame(mt_unit_list[:])
    df.to_csv(f"{result_path}/df5.csv", index=False)
    return mt_unit_list