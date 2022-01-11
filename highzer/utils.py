import json
import subprocess
import timeit
import numpy as np

import os
import time
from datetime import date, datetime
from decorator import decorator


@decorator
def retry(func, amount=3, interval=30, *args, **kwargs):
    counter = 0
    while 1:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # TODO print the error
            counter += 1

            if counter >= amount:
                raise e

            time.sleep(interval)


def get_ident(game, period, n):
    pg = game.replace(" ", "").lower()
    return f"{period[0]}{n}_{pg}"


def get_week():
    return date.today().isocalendar()[1]


def get_day():
    return datetime.now().timetuple().tm_yday


def _sec_to_time(secs):
    # pretty print seconds to hour:minute:seconds
    hours = secs // 3600
    minutes = secs // 60 - hours * 60
    seconds = secs - (hours * 60 + minutes) * 60
    return hours, minutes, seconds


def pretty_time(secs):
    hours, minutes, seconds = _sec_to_time(secs)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def now():
    return datetime.now().timestamp()


def pretty_short_time(secs):
    _, minutes, seconds = _sec_to_time(secs)
    return f"{minutes:02}:{seconds:02}"


def pprint(data):
    print(json.dumps(data, indent=2, sort_keys=True))


def log(ident, *args):
    timestamp = datetime.now().strftime("%d/%m-%H:%M:%S")
    print(f"{timestamp} - {ident} - ", *args)


def run(*args):
    # return subprocess.run([str(arg) for arg in args], check=True)
    # subprocess.run(["bash", "-c", "'ls data'"])
    return os.system(" ".join([str(x) for x in args]))

    os.system("bash -c 'ls data'")

    joined = " ".join([str(arg) for arg in args])
    return subprocess.run(["bash", "-c", f"'{joined}'"], check=True)


def array_chunk(arr, size):
    amount = int(len(arr) / size)
    split = np.array_split(arr[: amount * size], amount)
    # append the last chunk which is < size
    split.append(arr[-(len(arr) - size * amount) :])
    return split


@decorator
def timer(func, *args, **kwargs):
    start_time = timeit.default_timer()

    return_value = func(*args, **kwargs)

    elapsed = timeit.default_timer() - start_time
    print(f"Function {func.__name__} took {elapsed} seconds to complete.")

    return return_value


def get_base_folder():
    folder = "data"

    if not os.path.exists(folder):
        os.makedirs(folder)

    return folder


def locate_folder(ident):
    folder = f"{get_base_folder()}/{ident}"

    if not os.path.exists(folder):
        os.makedirs(folder)

    return folder


def convert_data(arr, chunk_size):
    pretty = []
    for index, data in enumerate(arr):
        now = index * chunk_size
        pretty.append(
            {
                "value": data,
                "chunk": index,
                "pretty": pretty_time(now),
                "from": now,
                "length": chunk_size,
                "to": now + chunk_size,
            }
        )

    return pretty
