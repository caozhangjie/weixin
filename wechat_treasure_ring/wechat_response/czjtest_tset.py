import time
import urllib
from threading import Timer


def get_sleep():
    req = urllib.urlopen(url='http://127.0.0.1/weixin?exercise_and_time=0&sleep=1')
    Timer(40, get_sleep, ()).start()


def get_exercise():
    req = urllib.urlopen(url='http://127.0.0.1/weixin?exercise_and_time=1&sleep=0')
    Timer(40, get_exercise, ()).start()


def align_exercise_time():
    return 30


def align_sleep_time():
    now_time = time.localtime()
    next_time = time.mktime(time.struct_time([now_time.tm_year, now_time.tm_mon, now_time.tm_mday, 0, 1, 0, 0, 0, 0]))
    next_time += 24 * 3600
    return (next_time - time.time())

if __name__ == "__main__":
    print align_sleep_time()