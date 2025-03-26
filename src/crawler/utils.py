import time
import functools

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