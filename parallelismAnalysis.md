# Parallelism Tuning for HTML Parsing

To optimize the performance of an HTML parsing pipeline, I experimented with various parallelization strategies using Python's `multiprocessing` and `multithreading` modules.

### Testing Dataset Overview

- **Pages**: 10  
- **Properties**: 400  
- **Units**: 4,504  
- **List building (BeautifulSoup)**: `256.8691 s`

---

### Benchmark: HTML Parsing Time (Before Optimization)

| Method                                                      | Time (s)  |
|-------------------------------------------------------------|-----------|
| Single process (base case)                                  | 19.1319   |
| `apply_async`                                               | 17.0994   |
| `apply_async` + large chunks (25 chunks)                    | 18.5841   |
| `apply_async` + small chunks (88 chunks)                    | 16.9023   |
| `map`                                                       | 18.0836   |
| `ThreadPoolExecutor` (multithread)                          | 20.3130   |
| `apply_async` + small chunks (run only **first 25**)        | **6.6897** |

---

### Investigation & Key Observations

Despite using `multiprocessing`, the performance improvement was **marginal**. Here’s the breakdown of findings:

#### Hypothesis 1: the shared data structure `Manager().list()` is the bottleneck
- Replacing `apply_async` with `map` to avoid shared state: **no effect**
- Commenting out logic that modifies `Manager().list()`: **no effect**
- Even returning early without running any parsing code: **no improvement**

#### Hypothesis 2: Process overhead?
- Reducing the number of tasks using chunking (25 vs. 88 chunks): **no effect**
- However, running **only the first 25 chunks** of the 88-chunk version was **significantly faster**

#### This led to the following insight:  
According to the [official Python documentation on `multiprocessing`](https://docs.python.org/3/library/multiprocessing.html),

> *"When using multiple processes, one generally uses message passing for communication between processes and avoids having to use any synchronization primitives like locks.... <p>
One difference from other Python queue implementations, is that multiprocessing queues serializes all objects that are put into them using pickle. The object return by the get method is a re-created object that does not share memory with the original object."*

In our case, **the main process must serialize large `BeautifulSoup` objects for every task**, which introduces significant overhead on a single core—especially when the actual parsing tasks are lightweight. As a result, `multiprocessing` brings only marginal improvement until we reduce the serialization cost.


---

### Optimization Strategy

**Refactor the code to pass lightweight HTML strings instead of `BeautifulSoup` objects.**  
Each worker then rebuilds the soup locally. This significantly reduces serialization cost and improves parallel throughput.

---

### Benchmark: After Refactoring

- **List building (without turning into soup object beforehand)**: `190.0905 s`

| Method                                   | Time (s)  |
|------------------------------------------|-----------|
| Single process (base case)               | 52.3781   |
| `apply_async`                            | 10.8709   |
| `apply_async` + large chunks (25)        | 11.1214   |
| `apply_async` + small chunks (88)        | 11.6920   |
| `map`                                    | 10.9354   |
| `ThreadPoolExecutor`                     | 57.2707   |

---

### Conclusion

- **Pass HTML strings instead of soup objects** to avoid heavy serialization.
- **Use `apply_async`** for simple, efficient parallelism.
- **Overall speed improvement: ~27%**

| Stage              | Before       | After        |
|--------------------|--------------|--------------|
| List building      | 256.8691 s   | 190.0905 s   |
| Parsing            | 19.1319 s    | 10.8709 s    |
| **Total**          | **276.001 s**| **200.9614 s**|

---

### TL;DR

> Avoid passing complex objects (like soup objects from `BeautifulSoup`) between processes. Instead, pass raw data (e.g., strings) and reconstruct them within the worker. This small change significantly improves performance and scalability.
