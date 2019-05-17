import time
from contextlib import contextmanager

@contextmanager
def timeme(message = "Took "):
    try:
        a = time.time()
        yield None
    finally:
        print(message+str(time.time()-a)+'s')
        
        
class dotdict(dict):    
    """A dot-able dictionary for easy access to items. Note stay clear from
    keys that clashes with dict internals like: copy, fromkeys,
    get, items, keys, pop, popitem, setdefault, update, and values.
    ...
    
    Examples
    --------
    >>> a = dotdict(val1=1)
    >>> a.val2 = 2
    >>> a
    {'val1': 1, 'val2': 2}
    >>> a['val1']
    1
    >>> a.val1
    1
    """
    def __init__(self, **kwds):
        self.update(kwds)
        self.__dict__ = self
