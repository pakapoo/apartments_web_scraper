import time
import functools
import requests
import os

def time_stats(func):
    """Decorator to measure and print the execution time of a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"--------{func.__name__}--------") 
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f"Execution time for {func.__name__}: {elapsed_time:.4f} seconds")
        return result
    return wrapper

def test_connection(headers):
    response = requests.get("https://www.apartments.com/madison-wi/", headers=headers)
    print(response.status_code)  # Should print 200 if successful
    print(response.json())  # Should print the response content in JSON format

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