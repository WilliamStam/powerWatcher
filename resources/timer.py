from contextlib import contextmanager
from time import perf_counter


@contextmanager
def timer() -> float:
    start = perf_counter()
    yield lambda: perf_counter() - start

#
# @contextmanager
# def timer():
#     start = time.time()
#     end = start
#     total = None
#     try:
#         yield total
#     finally:
#         end = time.time()
#         total = end - start