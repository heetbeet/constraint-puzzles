import time
from contextlib import contextmanager

@contextmanager
def timeme(message = "Took "):
    try:
        a = time.time()
        yield None
    finally:
        print(message+str(time.time()-a)+'s')
        