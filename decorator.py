from configs import config
from functools import wraps
def connect_db(db=config.DB_DBNAME):
    def deco(func):
        def wrap(*args, **kwargs):
            return func(*args, **kwargs)
        return wrap
    return deco