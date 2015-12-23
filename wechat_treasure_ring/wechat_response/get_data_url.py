import time
import urllib
from threading import Timer


def get_sleep():
    req = urllib.urlopen(url='http://127.0.0.1/autosave?exercise_and_time=0&sleep=1')
    Timer(24*3600, get_sleep, ()).start()


def get_exercise():
    req = urllib.urlopen(url='http://127.0.0.1/autosave?exercise_and_time=1&sleep=0')
    Timer(24*3600, get_exercise, ()).start()


def align_exercise_time():
    now_time = time.localtime()
    next_time = time.mktime(time.struct_time([now_time.tm_year, now_time.tm_mon, now_time.tm_mday, 0, 1, 0, 0, 0, 0]))
    next_time += 24 * 3600
    return (next_time - time.time())


def align_sleep_time():
    now_time = time.localtime()
    if now_time.tm_hour > 12 or (now_time.tm_hour == 12 and now_time.tm_min > 1):     
        next_time = time.mktime(time.struct_time([now_time.tm_year, now_time.tm_mon, now_time.tm_mday, 12, 1, 0, 0, 0, 0]))
        next_time += 24 * 3600
    else:
    	next_time = time.mktime(time.struct_time([now_time.tm_year, now_time.tm_mon, now_time.tm_mday, 12, 1, 0, 0, 0, 0]))
    return (next_time - time.time())


if __name__ = "__main__":
    Timer(align_exercise_time(), get_exercise, ()).start()
    Timer(align_sleep_time(), get_sleep, ()).start()


