import os
import typing
import shutil
import logging
from threading import Timer
from inspect import signature
import time
import numpy
import cv2

def get_homography_martix(points_1, points_2):
    A: numpy.ndarray = numpy.zeros(shape=( len(points_1) * 2 ,  9), dtype=int)
    for i in range(len(points_1)):
        x1, y1 = points_1[i]
        x2, y2 = points_2[i]
        # -x1 * h11 - y1 * h12 - h13 + x2 = 0
        # -x1 * h21 - y1 * h22 - h23 + y2 = 0
        idx = i + i
        A[idx, 0] = -x1
        A[idx, 1] = -y1
        A[idx, 2] = -1
        A[idx, 3:6] = 0
        A[idx, 6] = x1 * x2
        A[idx, 7] = y1 * x2
        A[idx, 8] = x2
        idx += 1
        A[idx, 0:3] = 0
        A[idx, 3] = -x1
        A[idx, 4] = -y1
        A[idx, 5] = -1
        A[idx, 6] = x1 * y2
        A[idx, 7] = y1 * y2
        A[idx, 8] = y2

    _, _, Vt = numpy.linalg.svd(A)

    H = Vt[-1].reshape(3, 3)
    H /= H[2, 2]
    return H

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


@throttle(0.5)
def select_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
        point_list = param.get("point_list")
        arr_len = param.get("len", 4)
        if len(point_list) < arr_len:
            cv2.circle(param.get("image"), (x, y), 3, (255, 0, 0), 2)
            point_list.append((x,y))


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
