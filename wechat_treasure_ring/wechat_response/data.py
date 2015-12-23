# -*- coding: UTF-8 -*-

# for sleeping assess
import urllib
import json
import time
import numpy as np
from wechat_response.models import *


def get_url(parameter, base_addr):
    if not parameter:
        return base_addr
    base_addr += "?"
    for val in parameter:
        base_addr += val + '=' + str(parameter[val]) + '&'
    base_addr = base_addr.strip("&")
    return base_addr


def get_data(type_list, start_time, end_time, user=0, type="", subType="", raw=False):
    param = {'startTime':start_time, 'endTime':end_time, 'user': user}
    if type:
        param["type"] = type
        if subType:
            param["subType"] = subType
    get_url(param, 'http://wrist.ssast2015.com/bongdata')
    req = urllib.urlopen(url=get_url(param, 'http://wrist.ssast2015.com/bongdata'))
    data = json.loads(req.read())
    if raw:
        return data
    return_data = dict()
    for type_name in type_list:
        return_data[type_name] = []
    for val in data:
        for type_name in type_list:
            return_data[type_name].append(val[type_name])
    return return_data


def get_raw_and_process_data(type_list, start_time, end_time, user=0, type="", subType="", raw=False):
    param = {'startTime':start_time, 'endTime':end_time, 'user': user}
    if type:
        param["type"] = type
        if subType:
            param["subType"] = subType
    get_url(param, 'http://wrist.ssast2015.com/bongdata')
    req = urllib.urlopen(url=get_url(param, 'http://wrist.ssast2015.com/bongdata'))
    data = json.loads(req.read())
    return_data = dict()
    for type_name in type_list:
        return_data[type_name] = []
    for val in data:
        for type_name in type_list:
            return_data[type_name].append(val[type_name])
    return [data, return_data]


# get "num" days list
def get_date_list(num):
    now_time = time.localtime()
    date = list()
    for i in range(num):
        date.append(str(now_time.tm_year) + "." + str(now_time.tm_mon) + "." + str(now_time.tm_mday))
        now_time = time.mktime(now_time)
        now_time -= 86400
        now_time = time.localtime(now_time)
    return date


def transfer_time(time_str):
    time_list = time_str.split(' ')
    year = time_list[0].strip()
    day = time_list[1].strip()
    year = year.split('-')
    day = day.split(':')
    time_list = [int(year[0]), int(year[1]), int(year[2]), int(day[0]), int(day[1]), int(day[2])]
    return time_list


def get_user_information(user_id):
    if RingUser.objects.filter(user_id=user_id).exists():
        user = RingUser.objects.filter(user_id=user_id)[0]
    else:
        user = None
    return user


# 把数据按天求和,第三个参数表示天数
def integrate_data(data, s_time, days, is_score=False):
    length = len(s_time)
    processing_day = list()
    new_day = list()
    new_data = list()
    temp_data = 0
    temp_num = 0
    
    temp_day = transfer_time(s_time[0])
    processing_day = [temp_day[0], temp_day[1], temp_day[2], 0, 0, 0, 0, 0, 0]
    processing_day = time.mktime(time.struct_time(processing_day))
    new_day = [temp_day[0], temp_day[1], temp_day[2], 0, 0, 0, 0, 0, 0]
    new_day = time.mktime(time.struct_time(new_day))
    j = 0
    for i in range(length):
        temp_day = transfer_time(s_time[i])       
        new_day = time.mktime(time.struct_time([temp_day[0], temp_day[1], temp_day[2], 0, 0, 0, 0, 0, 0]))
        if new_day == processing_day:
            if data[i] != 0:
                temp_num += 1
                temp_data += data[i]
        else: 
            if is_score:
                if temp_num != 0:
                    temp_data /= temp_num
                    temp_num = 0
            j += 1
            num_interval = int((new_day - processing_day) / 86400)
            temp_data /= num_interval
            for k in range(num_interval):
                new_data.append(temp_data)
            processing_day = new_day
            temp_data = 0
    if is_score:
        if temp_num != 0:
            temp_data /= float(temp_num)
            temp_num = 0
    new_data.append(temp_data)
    length = len(new_data)
    if days > length:
        residual = days - length
        if length > 0:
            if is_score:
                temp_data = 0
            else:    
                temp_data = new_data[0] / (residual + 1)
                new_data[0] = temp_data
        else:
            temp_data = 0
        for i in range(residual):
            new_data.insert(0, temp_data)
    else:
        new_data = new_data[(-1 * days):]
    return new_data


# 获取各时间段状态
def get_today_condition(user):
    now_time = time.localtime()
    last_time = time.mktime(time.struct_time([now_time.tm_year, now_time.tm_mon, now_time.tm_mday, 0, 0, 0, 0, 0, 0])) - 12 * 3600
    today = now_time.tm_mday
    last_time = time.localtime(last_time)
    start_time = process_num(last_time.tm_year) + "-" + process_num(last_time.tm_mon) + "-" + process_num(last_time.tm_mday) + " " + process_num(last_time.tm_hour) + ":" + process_num(last_time.tm_min) + ":" + process_num(last_time.tm_sec)
    end_time = process_num(now_time.tm_year) + "-" + process_num(now_time.tm_mon) + "-" + process_num(now_time.tm_mday) + " " + process_num(now_time.tm_hour) + ":" + process_num(now_time.tm_min) + ":" + process_num(now_time.tm_sec)
    data = get_data(["user", 'startTime', 'endTime', 'type', 'distance', 'calories', 'steps', 'subType', 'actTime', 'nonActTime', 'dsNum', 'lsNum', 'wakeNum', 'wakeTimes', 'score'], start_time, end_time, user.id, raw=True)   
    i = 0
    length = len(data)
    while data[i]["endTime"].split('-')[2].split(' ')[0] != str(today) and i < length:
        data.pop(0)
    new_data = integrate_by_class(data)
    calculate_time(new_data)
    new_data.pop(0)
    time_first = new_data[0]["endTime"].split('-')[2].split(' ')[1].split(':')
    time_first = time.mktime(time.struct_time([now_time.tm_year, now_time.tm_mon, now_time.tm_mday, int(time_first[0]), int(time_first[1]), int(time_first[2]), 0, 0, 0]))
    time_00 = time.mktime(time.struct_time([now_time.tm_year, now_time.tm_mon, now_time.tm_mday, 0, 0, 0, 0, 0, 0]))
    rate = float(time_first - time_00) / new_data[0]["allTime"]
    new_data[0]["allTime"] -= (time_first - time_00)
    new_data[0]["startTime"] = (str(now_time.tm_year) + "-" + str(now_time.tm_mon) + "-" + str(now_time.tm_mday) + " " + "00:00:00").encode("utf-8")
    new_data[0]["distance"] = int(new_data[0]["distance"] * rate)
    new_data[0]["steps"] = int(new_data[0]["steps"] * rate)
    new_data[0]["calories"] = int(new_data[0]["calories"] * rate)
    new_data[0]["dsNum"] = int(new_data[0]["dsNum"] * rate)
    new_data[0]["sleepNum"] = int(new_data[0]["sleepNum"] * rate)
    return new_data
    

# 把数据按种类结合
def integrate_by_class(data):
    new_data = list()
    one_data = init_temp()
    for val in data:
        if not judge_change(one_data, val):
            modify(one_data, val)
        else:
            one_data["endTime"] = val["startTime"]
            new_data.append(one_data)
            one_data = init_temp()
            one_data["startTime"] = val["startTime"]
            one_data["type"] = val["type"]
            one_data["subType"] = val["subType"]
            modify(one_data, val)
    one_data["endTime"] = data[-1]["endTime"]
    new_data.append(one_data)
    return new_data


def judge_change(one_data, val):
    if one_data["type"] == val["type"] and one_data["subType"] == val["subType"]:
        return False
    elif one_data["type"] == val["type"]:
        if one_data["type"] == 1:
            if ((one_data["subType"] == 1 or one_data["subType"] == 2) and (val["subType"] == 1 or val["subType"] == 2)) or ((one_data["subType"] == 0) and (val["subType"] == 0)):
                return False
            else:
                return True
        else:
            return True
    else: 
        return True


def modify(one_data, val):
    if val['type'] == 1:
        one_data["sleepNum"] += val["dsNum"] + val["lsNum"]
        if val['subType'] == 1:
            one_data["dsNum"] += val["dsNum"]
    elif val["type"] == 2:
        one_data["calories"] += val["calories"]
        one_data["distance"] += val["distance"]
        one_data["steps"] += val["steps"]
    elif val["type"] == 3:
        if val['subType'] == 2 or val['subType'] == 4:
            one_data["calories"] += val["calories"]
            one_data["distance"] += val["distance"]
            one_data["steps"] += val["steps"]


def init_temp():
    one_data = dict()
    one_data["distance"] = 0
    one_data["steps"] = 0
    one_data["calories"] = 0
    one_data["dsNum"] = 0
    one_data["sleepNum"] = 0
    one_data["score"] = 0
    one_data["startTime"] = "0-0-0 00:00:00"
    one_data["endTime"] = "0-0-0 00:00:00"
    one_data["allTime"] = 0
    one_data['type'] = 0
    one_data['subType'] = 0
    return one_data  


def calculate_time(data):
    length = len(data)
    all_time = list()
    for i in range(length):
        s = transfer_time(data[i]["startTime"])
        e = transfer_time(data[i]["endTime"])
        data[i]["allTime"] = (time.mktime(time.struct_time([e[0], e[1], e[2], e[3], e[4], e[5], 0, 0, 0])) - time.mktime(time.struct_time([s[0], s[1], s[2], s[3], s[4], s[5], 0, 0, 0])))


# 时间转换函数，补0
def process_num(x):
    if x < 10:
        return "0" + str(x)
    else:
        return str(x)


# 更新睡眠数据,每天12:01:00
def save_sleep_data(user):
    #now_time = time.localtime()
    now_time = time.time() - 86400
    now_time = time.localtime(now_time)
    last_time = time.mktime(time.struct_time([now_time.tm_year, now_time.tm_mon, now_time.tm_mday, 12, 0, 0, 0, 0, 0]))
    last_time -= 86400 * 33
    last_time = time.localtime(last_time)
    start_time = process_num(last_time.tm_year) + "-" + process_num(last_time.tm_mon) + "-" + process_num(last_time.tm_mday) + " " + process_num(last_time.tm_hour) + ":" + process_num(last_time.tm_min) + ":" + process_num(last_time.tm_sec)
    end_time = process_num(now_time.tm_year) + "-" + process_num(now_time.tm_mon) + "-" + process_num(now_time.tm_mday) + " " + process_num(now_time.tm_hour) + ":" + process_num(now_time.tm_min) + ":" + process_num(now_time.tm_sec)
    data = get_data(["user", "dsNum", "lsNum", "startTime", "endTime", "score"], start_time, end_time,  user.id - 1)
    length = len(data["dsNum"])
    data["sleepNum"] = list()
    for i in range(length):
        data["sleepNum"].append(data["dsNum"][i] + data["lsNum"][i])
    data["dsNum"] = integrate_data(data["dsNum"], data["startTime"], 30)
    data["sleepNum"] = integrate_data(data["sleepNum"], data["startTime"], 30)
    data["score"] = integrate_data(data["score"], data["startTime"], 30, True)
    data["date"] = get_date_list(30)
    if RecordByDay.objects.filter(user_name=user.user_id).exists():
        user_temp = RecordByDay.objects.filter(user_name=user.user_id)
        length_of_user = len(user_temp)
        for i in range(length_of_user):
            data["date"][i] = data["date"][i].split('.')
            user_temp[i].year = int(data["date"][i][0])
            user_temp[i].month = int(data["date"][i][1])
            user_temp[i].day = int(data["date"][i][2])
            user_temp[i].dsNum = data["dsNum"][i]
            user_temp[i].allNum = data["sleepNum"][i]
            user_temp[i].score = data["score"][i]
            user_temp[i].save()
        if length_of_user < 30:
            for i in range(length_of_user, 30):
                data["date"][i] = data["date"][i].split('.')
                user_temp = RecordByDay(
                    user_name=user.user_id,
                    year=int(data["date"][i][0]),
                    month=int(data["date"][i][1]),
                    day=int(data["date"][i][2]),
                    dsNum=data["dsNum"][i],
                    allNum=data["sleepNum"][i],
                    calories=0,
                    steps=0,
                    distance=0,
                    score=data["score"][i]
                )
                user_temp.save()

    else:
        for i in range(30):
            data["date"][i] = data["date"][i].split('.')
            user_temp = RecordByDay(
                user_name=user.user_id,
                year=int(data["date"][i][0]),
                month=int(data["date"][i][1]),
                day=int(data["date"][i][2]),
                dsNum=data["dsNum"][i],
                allNum=data["sleepNum"][i],
                calories=0,
                steps=0,
                distance=0,
                score=data["score"][i]
            )
            user_temp.save()
    


def get_sleep_data(user):
    data = dict()
    data["dsNum"] = range(30)
    data["sleepNum"] = range(30)
    data["score"] = range(30)
    if RecordByDay.objects.filter(user_name=user.user_id).exists():
        user_temp = RecordByDay.objects.filter(user_name=user.user_id)
        length = len(user_temp)
        for i in range(length):
            data["dsNum"][i] = user_temp[i].dsNum
            data["sleepNum"][i] = user_temp[i].sleepNum
            data["score"][i] = user_temp[i].score
    data["date"] = get_date_list(30)
    return data


 #  获取今天到目前为止的步数
def get_today_step(user):
    now_time = time.localtime()
    last_time = time.mktime(time.struct_time([now_time.tm_year, now_time.tm_mon, now_time.tm_mday, 0, 0, 0, 0, 0, 0]))
    last_time = time.localtime(last_time)
    start_time = process_num(last_time.tm_year) + "-" + process_num(last_time.tm_mon) + "-" + process_num(last_time.tm_mday) + " " + process_num(last_time.tm_hour) + ":" + process_num(last_time.tm_min) + ":" + process_num(last_time.tm_sec)
    end_time = process_num(now_time.tm_year) + "-" + process_num(now_time.tm_mon) + "-" + process_num(now_time.tm_mday) + " " + process_num(now_time.tm_hour) + ":" + process_num(now_time.tm_min) + ":" + process_num(now_time.tm_sec)
    try:
        data = get_data(["user", "steps", "startTime"], start_time, end_time, user.id)
        step = (integrate_data(data["steps"], data["startTime"],1))[0]
    except:
        step = 10000

    if step <= 2000:
        return 10000
    return step


def save_time_line(user):
    now_time = time.localtime()
    last_time = time.mktime(time.struct_time([now_time.tm_year, now_time.tm_mon, now_time.tm_mday, 0, 0, 0, 0, 0, 0]))
    last_time -= 86400 * 33
    last_time = time.localtime(last_time)
    start_time = process_num(last_time.tm_year) + "-" + process_num(last_time.tm_mon) + "-" + process_num(last_time.tm_mday) + " " + process_num(last_time.tm_hour) + ":" + process_num(last_time.tm_min) + ":" + process_num(last_time.tm_sec)
    end_time = process_num(now_time.tm_year) + "-" + process_num(now_time.tm_mon) + "-" + process_num(now_time.tm_mday) + " " + process_num(now_time.tm_hour) + ":" + process_num(now_time.tm_min) + ":" + process_num(now_time.tm_sec)
    data = get_data(["user", 'startTime', 'endTime', 'type', 'subType'], start_time, end_time,  user.id, raw=True)
    last_time = time.mktime(last_time)
    last_time += 3 * 86400
    last_time = time.localtime(last_time)
    today = last_time.tm_mday
    month = last_time.tm_mon
    year = last_time.tm_year
    temp_local_time = transfer_time(data[0]["endTime"])
    i = 0
    while (temp_local_time[0] < year) or (temp_local_time[0] == year and temp_local_time[1] < month) or (temp_local_time[0] == year and temp_local_time[1] == month and temp_local_time[2] < today):
        i += 1
        temp_local_time = transfer_time(data[i]["endTime"])
    new_data = split_condition(data[i:], today, month, year)
    length = len(new_data)
    for i in range(length-1):
        the_last_time = new_data[i][-1]["endTime"].split(" ")[1].split(":")
        last_all_time = (24 - int(the_last_time[0])) * 3600 - int(the_last_time[1]) * 60 - int(the_last_time[2])
        new_data[i].append({"type":new_data[i+1][-1]["type"], "subType":new_data[i+1][-1]["subType"], "startTime":new_data[i][-1]["endTime"], "endTime":((new_data[i][-1]["endTime"].split(" "))[0] + " 24:00:00"), "allTime":last_all_time})
    check_and_update(new_data, 30)
    new_data.pop()
    length = len(new_data)
    if ActivityRecord.objects.filter(user_name=user.user_id).exists():
        for i in range(length):
            user_temp = ActivityRecord.objects.filter(user_name=user.user_id, day_num=(i+1))
            if user_temp:
                user_temp[0].day_num = i + 1
                user_temp[0].data =json.dumps(new_data[i])
                user_temp[0].save()
            else:
                user_temp = ActivityRecord(user_name=user.user_id, day_num=(i+1), data=json.dumps(new_data[i]))
                user_temp.save()


def get_today_time_line(user):
    now_time = time.localtime()
    last_time = time.mktime(time.struct_time([now_time.tm_year, now_time.tm_mon, now_time.tm_mday, 0, 0, 0, 0, 0, 0]))
    last_time -= 86400 * 3
    last_time = time.localtime(last_time)
    start_time = process_num(last_time.tm_year) + "-" + process_num(last_time.tm_mon) + "-" + process_num(last_time.tm_mday) + " " + process_num(last_time.tm_hour) + ":" + process_num(last_time.tm_min) + ":" + process_num(last_time.tm_sec)
    end_time = process_num(now_time.tm_year) + "-" + process_num(now_time.tm_mon) + "-" + process_num(now_time.tm_mday) + " " + process_num(now_time.tm_hour) + ":" + process_num(now_time.tm_min) + ":" + process_num(now_time.tm_sec)
    data = get_data(["user", 'startTime', 'endTime', 'type', 'subType'], start_time, end_time,  user.id, raw=True)
    today = last_time.tm_mday
    month = last_time.tm_mon
    year = last_time.tm_year
    temp_local_time = transfer_time(data[0]["endTime"])
    i = 0
    while (temp_local_time[0] < year) or (temp_local_time[0] == year and temp_local_time[1] < month) or (temp_local_time[0] == year and temp_local_time[1] == month and temp_local_time[2] < today):
        i += 1
        temp_local_time = transfer_time(data[i]["endTime"])
    new_data = split_condition(data[i:], today, month, year)
    check_and_update(new_data, 1)
    return new_data.pop()


# 获取并存储按天算的运动数据,每天00:01:00更新
def save_exercise_data(user):
    now_time = time.localtime()
    last_time = time.mktime(time.struct_time([now_time.tm_year, now_time.tm_mon, now_time.tm_mday, 0, 0, 0, 0, 0, 0]))
    last_time -= 86400 * 33
    last_time = time.localtime(last_time)
    start_time = process_num(last_time.tm_year) + "-" + process_num(last_time.tm_mon) + "-" + process_num(last_time.tm_mday) + " " + process_num(last_time.tm_hour) + ":" + process_num(last_time.tm_min) + ":" + process_num(last_time.tm_sec)
    end_time = process_num(now_time.tm_year) + "-" + process_num(now_time.tm_mon) + "-" + process_num(now_time.tm_mday) + " " + process_num(now_time.tm_hour) + ":" + process_num(now_time.tm_min) + ":" + process_num(now_time.tm_sec)
    data = get_data(["user", 'startTime', 'endTime', 'type', 'distance', 'calories', 'steps', 'subType'], start_time, end_time,  user.id)
    data["distance"] = integrate_data(data["distance"], data["startTime"], 30)
    data["steps"] = integrate_data(data["steps"], data["startTime"], 30)
    data["calories"] = integrate_data(data["calories"], data["startTime"], 30)
    data["date"] = get_date_list(30)
    if RecordByDay.objects.filter(user_name=user.user_id).exists():
        user_temp = RecordByDay.objects.filter(user_name=user.user_id)
        length_of_user = len(user_temp)
        for i in range(length_of_user):
            data["date"][i] = data["date"][i].split('.')
            user_temp[i].year = int(data["date"][i][0])
            user_temp[i].month = int(data["date"][i][1])
            user_temp[i].day = int(data["date"][i][2])
            user_temp[i].calories = data["calories"][i]
            user_temp[i].steps = data["steps"][i]
            user_temp[i].distance = data["distance"][i]
        user_temp[i].save()
        if length_of_user < 30:
            for i in range(length_of_user, 30):
                data["date"][i] = data["date"][i].split('.')
                user_temp = RecordByDay(
                    user_name=user.user_id,
                    year=int(data["date"][i][0]),
                    month=int(data["date"][i][1]),
                    day=int(data["date"][i][2]),
                    dsNum=0,
                    allNum=0,
                    calories=data["calories"][i],
                    steps=data["steps"][i],
                    distance=data["distance"][i],
                    score=0
                )
                user_temp.save()
    else:
        for i in range(30):
            data["date"][i] = data["date"][i].split('.')
            user_temp = RecordByDay(
                    user_name=user.user_id,
                    year=int(data["date"][i][0]),
                    month=int(data["date"][i][1]),
                    day=int(data["date"][i][2]),
                    dsNum=0,
                    allNum=0,
                    calories=data["calories"][i],
                    steps=data["steps"][i],
                    distance=data["distance"][i],
                    score=0
                )
            user_temp.save()


# 检查用户是否在某一天没有活动
def check_and_update(new_data, day_number):
    now_time = time.localtime()
    last_time = time.mktime(time.struct_time([now_time.tm_year, now_time.tm_mon, now_time.tm_mday, 0, 0, 0, 0, 0, 0]))
    last_time -= 86400 * day_number
    i = 0
    j = 0
    while i < (day_number + 1):
        if j >= len(new_data):
            break
        time_str_ = new_data[j][0]["endTime"].split(" ")[0].split("-")
        time_now = time.mktime(time.struct_time([int(time_str_[0]), int(time_str_[1]), int(time_str_[2]), 0, 0, 0, 0, 0, 0]))
        if time_now > last_time:
            last_time = time.localtime(last_time)
            new_data.insert(j, [{"startTime":process_num(last_time.tm_year) + "-" + process_num(last_time.tm_mon) + "-" + process_num(last_time.tm_mday), "none":1}])
            j += 1
            i += 1
            last_time = time.mktime(last_time)
            last_time += 24 * 3600
        elif last_time == time_now:
            length = len(new_data[j])
            for k in range(length):
                if "none" in new_data[j][k]:
                    break
                new_data[j][k] = {"startTime":new_data[j][k]["startTime"], "endTime":new_data[j][k]["endTime"], "type":new_data[j][k]["type"], "subType":new_data[j][k]["subType"]}
            j += 1
            i += 1
            last_time += 24 * 3600
        else:
            new_data.pop(j)
    while i < (day_number + 1):
        last_time = time.localtime(last_time)
        new_data.append([{"startTime":process_num(last_time.tm_year) + "-" + process_num(last_time.tm_mon) + "-" + process_num(last_time.tm_mday), "none":1}])
        i += 1
        last_time = time.mktime(last_time)
        last_time += 24 * 3600


# 获取运动数据
def get_exercise_data(user):
    data = dict()
    data["distance"] = range(30)
    data["steps"] = range(30)
    data["calories"] = range(30)
    if RecordByDay.objects.filter(user_name=user.user_id).exists():
        user_temp = RecordByDay.objects.filter(user_name=user.user_id)
        length = len(user_temp)
        for i in range(length):
            data["distance"][i] = user_temp[i].distance
            data["steps"][i] = user_temp[i].steps
            data["calories"][i] = user_temp[i].calories
    data["date"] = get_date_list(30)
    return data


def split_condition(data, today, month, year):
    i = 0
    j = 0
    all_data = list()
    length = len(data)
    while i < length:
        temp_local_time = transfer_time(data[i]["endTime"])
        while temp_local_time[0] == year and temp_local_time[1] == month and temp_local_time[2] == today:
            i += 1
            if i >= length:
                break
            temp_local_time = transfer_time(data[i]["endTime"])
        temp_data = data[j:i]
        if temp_data:
            new_data = integrate_by_class(temp_data)
            calculate_time(new_data)
            new_data.pop(0)
            time_first = new_data[0]["endTime"].split('-')[2].split(' ')[1].split(':')
            time_first = time.mktime(time.struct_time([year, month, today, int(time_first[0]), int(time_first[1]), int(time_first[2]), 0, 0, 0]))
            time_00 = time.mktime(time.struct_time([year, month, today, 0, 0, 0, 0, 0, 0]))
            rate = float(time_first - time_00) / new_data[0]["allTime"]
            new_data[0]["allTime"] -= (time_first - time_00)
            new_data[0]["startTime"] = (str(year) + "-" + str(month) + "-" + str(today) + " " + "00:00:00").encode("utf-8")
            all_data.append(new_data)
            temp_time = time.mktime(time.struct_time([year, month, today, 0, 0, 0, 0, 0, 0]))
            temp_time += 86400
            temp_time = time.localtime(temp_time)
            today = temp_time.tm_mday
            month = temp_time.tm_mon
            year = temp_time.tm_year  
            j = i
        else:
            temp_time = time.mktime(time.struct_time([year, month, today, 0, 0, 0, 0, 0, 0]))
            temp_time += 86400
            temp_time = time.localtime(temp_time)
            today = temp_time.tm_mday
            month = temp_time.tm_mon
            year = temp_time.tm_year 
    return all_data
    

# update the data of the particular user defined by parameter user
def get_save(user):
    last_time = time.localtime(user.last_record)
    start_time = process_num(last_time.tm_year) + "-" + process_num(last_time.tm_mon) + "-" + process_num(last_time.tm_mday) + " " + process_num(last_time.tm_hour) + ":" + process_num(last_time.tm_min) + ":" + process_num(last_time.tm_sec)
    now_time = time.localtime()
    end_time = process_num(now_time.tm_year) + "-" + process_num(now_time.tm_mon) + "-" + process_num(now_time.tm_mday) + " " + process_num(now_time.tm_hour) + ":" + process_num(now_time.tm_min) + ":" + process_num(now_time.tm_sec)
    data = get_data(["user", 'startTime', 'endTime', 'type', 'distance', 'calories', 'steps', 'subType', 'actTime', 'nonActTime', 'dsNum', 'lsNum', 'wakeNum', 'wakeTimes', 'score'], start_time, end_time, user.id)
    time_list_start = process_time_data(data["startTime"])
    time_list_end = process_time_data(data["endTime"])
    save_data(data, time_list_start, time_list_end, user.user_id)
    new_record = time.time()
    if RingUser.objects.filter(user_id=user.user_id).exists():
        user_temp = RingUser.objects.filter(user_id=user.user_id)[0]
        user_temp.last_record = new_record
        user_temp.save()


# save data in the data base
def save_data(data, time_list_start, time_list_end, user_id):
    length = len(data["user"])
    for i in range(length):
        data_model = Record(
            user_name=user_id,
            startTime=time_list_start[i],
            endTime=time_list_end[i],
            type=data["type"][i],
            distance=data["distance"][i],
            calories=data["calories"][i],
            steps=data["steps"][i],
            subType=data["subType"][i],
            actTime=data["actTime"][i],
            nonActTime=data["nonActTime"][i],
            dsNum=data["dsNum"][i],
            lsNum=data["lsNum"][i],
            wakeNum=data["wakeNum"][i],
            wakeTimes=data["wakeTimes"][i],
            score=data["score"][i]
        )
        data_model.save()


# transform the string time to integer time
def process_time_data(time_list):
    new_list = list()
    for val in time_list:
        time_temp = transfer_time(val)
        new_list.append(time.mktime(time.struct_time([time_temp[0], time_temp[1], time_temp[2], time_temp[3], time_temp[4], time_temp[5], 0, 0, 0])))
    return new_list


def access_sleeping(user_id):
# get user information
    information = get_user_information(user_id)
    if information:
        data = get_sleep_data(information)
    else:
        return None

# set variation threshold and fft threshold
    var_threshold = 1
    reg_threshold = 0.01

# get 30-day sleeping data and 7-day sleeping data
    thirty_sleep = np.array(data["sleepNum"][-30:])
    thirty_deep_sleep = np.array(data["dsNum"][-30:])
    seven_sleep = thirty_sleep[-7:]
    seven_deep_sleep = thirty_deep_sleep[-7:]

# computer statistical data
    report = dict()
    report["date"] = data["date"]
    report["30-days-sleep"] = thirty_sleep
    report["30-days-deep-sleep"] = thirty_deep_sleep
    report["30-days-avg"] = np.average(thirty_sleep)
    report["30-days-var"] = np.abs(np.var(thirty_sleep))
    report["regular"] = 0
    for i in range(1, 30):
        report["30-days-reg"] = np.abs(np.fft.fft(thirty_sleep[0:i]))
        report["30-days-reg"][0] /= 30
        report["30-days-reg"][1:15] /= 15
        report["30-days-reg"] = report["30-days-reg"][0:15]
        if max(report["30-days-reg"]) / (np.median(report["30-days-reg"]) * 10000) > reg_threshold:
            report["regular"] = 1
    report["30-days-deep-avg"] = np.average(thirty_deep_sleep)
    if 0 in thirty_sleep:
        for i in range(len(thirty_sleep)):
            thirty_sleep[i] = 1
    report["30-days-deep-rate"] = np.divide(thirty_deep_sleep, thirty_sleep)
    report["30-days-avg-rate"] = np.average(report["30-days-deep-rate"])

    report["7-days-sleep"] = seven_sleep
    report["7-days-deep-sleep"] = seven_deep_sleep
    report["7-days-max"] = seven_sleep.max()
    report["7-days-min"] = seven_sleep.min()
    report["7-days-avg"] = np.average(seven_sleep)
    report["7-days-var"] = np.abs(np.var(seven_sleep))
    report["7-days-deep-avg"] = np.average(seven_deep_sleep)
    report["7-days-avg-rate"] = np.average(report["30-days-deep-rate"][-7:])

# compare some data and get report
    # whether sleep enough
    if information.age > 60:
        if report["7-days-avg"] > 7:
            report["sleep-time-enough"] = 1
        elif report["7-days-avg"] < 5.5:
            report["sleep-time-enough"] = 2
        else:
            report["sleep-time-enough"] = 3
    elif 30 < information.age <= 60:
        if report["7-days-avg"] > 8:
            report["sleep-time-enough"] = 1
        elif report["7-days-avg"] < 5.5:
            report["sleep-time-enough"] = 2
        else:
            report["sleep-time-enough"] = 3
    elif 13 < information.age <= 30:
        if report["7-days-avg"] > 9:
            report["sleep-time-enough"] = 1
        elif report["7-days-avg"] < 5.5:
            report["sleep-time-enough"] = 2
        else:
            report["sleep-time-enough"] = 3
    elif 4 < information.age <= 13:
        if report["7-days-avg"] > 12:
            report["sleep-time-enough"] = 1
        elif report["7-days-avg"] < 5.5:
            report["sleep-time-enough"] = 2
        else:
            report["sleep-time-enough"] = 3
    elif information.age <= 4:
        report["sleep-time-enough"] = 4

    # 7 days compare with 30 days
    if report["7-days-avg"] < report["30-days-avg"] and report["sleep-time-enough"] == 2:
        report["avg-compare"] = 1
    elif report["7-days-avg"] > report["30-days-avg"] and report["sleep-time-enough"] == 1:
        report["avg-compare"] = 2
    else:
        report["avg-compare"] = 0

    # whether fluctuate severely
    if report["7-days-var"] > var_threshold:
        report["7-days-flac"] = 0
    else:
        report["7-days-flac"] = 1
    if report["30-days-var"] > var_threshold:
        report["30-days-flac"] = 0
    else:
        report["30-days-flac"] = 1

    # whether the deep sleep rate is enough
    if report["30-days-avg-rate"] < 0.25:
        report["30-deep-avg"] = 0
    else:
        report["30-deep-avg"] = 1

    if report["7-days-avg-rate"] < 0.25:
        report["7-deep-avg"] = 0
    else:
        report["7-deep-avg"] = 1

    # whether you're anxious recently
    if report["7-deep-avg"] == 0 and report["30-deep-avg"] == 1:
        report["anxious"] = 1
    elif report["30-deep-avg"] == 0 and report["7-deep-avg"] == 0:
        report["anxious"] = 2
    else:
        report["anxious"] = 0

    # whether you have stark sleeping
    if report["7-days-max"] > 12:
        report["stark-sleep"] = 1
    elif report["7-days-min"] < 3:
        report["stark-sleep"] = 2
    else:
        report["stark-sleep"] = 0

    report["30-days-sleep"] = list(report["30-days-sleep"])
    report["30-days-deep-sleep"] = list(report["30-days-deep-sleep"])
    report["7-days-sleep"] = list(report["7-days-sleep"])
    report["7-days-deep-sleep"] = list(report["7-days-deep-sleep"])
    report['30-days-deep-rate'] = list(report['30-days-deep-rate'])
    return report


# assess your exercising data
def access_exercising(user_id):
    information = get_user_information(user_id)
    if information:
        data = get_exercise_data(information)
    else:
        return None

    report = dict()

# get statical data
    report["date"] = data["date"]
    report["7-days-dis"] = data["distance"][-7:]
    #report["7-days-speed"] = data["speed"][-7:]
    report["7-days-calories"] = data["calories"][-7:]
    report["7-days-steps"] = data["steps"][-7:]
    report["30-days-dis"] = data["distance"][-30:]
    #report["30-days-speed"] = data["speed"][-30:]
    report["30-days-calories"] = data["calories"][-30:]
    report["30-days-steps"] = data["steps"][-30:]

# compute exercising statical data
    report["7-days-dis-avg"] = np.average(data["distance"][-7:])
    #report["7-days-speed-avg"] = np.average(data["speed"][-7:])
    report["7-days-calories-avg"] = np.average(data["calories"][-7:])
    report["7-days-steps-avg"] = np.average(data["steps"][-7:])
    report["30-days-dis-avg"] = np.average(data["distance"])
    #report["30-days-speed-avg"] = np.average(data["speed"])
    report["30-days-calories-avg"] = np.average(data["calories"])
    report["30-days-steps-avg"] = np.average(data["steps"])

# compare data and get report
    # 0 female, 1 male
    if information.sex == 'male':
        report["BMR"] = 13.7516 * information.weight + 5.0033 * information.height - 6.7550 * information.age + 66.4730
    elif information.sex == 'female':
        report["BMR"] = 9.5634 * information.weight + 1.8496 * information.height - 4.6756 * information.age + 655.0955
    else:
        report["BMR"] = 0

    # BMR is the number of calories that you need every day if you don't exercise
    # Now compare the calories
    cb_rate = report["30-days-calories"][-1] / report["BMR"]
    report["yesterday-intensity"] = calc_intensity(cb_rate)
    cb_rate = report["7-days-calories-avg"] / report["BMR"]
    report["7-days-intensity"] = calc_intensity(cb_rate)

    return report


def calc_intensity(cb_rate):
    if cb_rate < 0.2:
        intensity = 0
    elif 0.2 < cb_rate < 0.375:
        intensity = 1
    elif 0.375 < cb_rate < 0.55:
        intensity = 2
    elif 0.55 < cb_rate < 0.725:
        intensity = 3
    elif 0.725 < cb_rate < 0.9:
        intensity = 4
    return intensity
