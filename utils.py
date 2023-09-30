import os
import typing
import shutil
import logging
from threading import Timer
from inspect import signature
import time

def create_folder(folder_name: typing.AnyStr):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.makedirs(folder_name)

def get_logger(name):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fhandler  = logging.FileHandler('my.log')
    fhandler.setLevel(logging.DEBUG)
    fhandler.setFormatter(formatter)
    chandler = logging.StreamHandler()
    chandler.setLevel(logging.DEBUG)
    chandler.setFormatter(formatter)
    logger.addHandler(fhandler)
    logger.addHandler(chandler)
    logger.setLevel(logging.DEBUG)
    return logger

def throttle(s, keep=60):
    """
    a decorator for throtting in python
    """
    def decorate(f):

        caller = {}

        def wrapped(*args, **kwargs):
            nonlocal caller

            called_args = '{}'.format(*args)
            t_ = time.time()

            if caller.get(called_args, None) is None or t_ - caller.get(called_args, 0) >= s:
                result = f(*args, **kwargs)

                caller = {key: val for key, val in caller.items() if t_ - val > keep}
                caller[called_args] = t_
                return result

            # Keep only calls > keep
            caller = {key: val for key, val in caller.items() if t_ - val > keep}
            caller[called_args] = t_

        return wrapped

    return decorate


def debounce(wait: int):
    """
    a decorator for debouncing in python
    """
    def decorator(fn):
        sig = signature(fn)
        caller = {}

        def debounced(*args, **kwargs):
            nonlocal caller

            try:
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                called_args = fn.__name__ + str(dict(bound_args.arguments))
            except:
                called_args = ''

            t_ = time.time()

            def call_it(key):
                try:
                    # always remove on call
                    caller.pop(key)
                except:
                    pass

                fn(*args, **kwargs)

            try:
                # Always try to cancel timer
                caller[called_args].cancel()
            except:
                pass

            caller[called_args] = Timer(wait, call_it, [called_args])
            caller[called_args].start()

        return debounced

    return decorator
