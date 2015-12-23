# -*- coding: utf-8 -*-
from wechat_response.models import *
from wechat_response.data import *
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from wechat_response.data import *
from wechat_treasure_ring.settings import *
import json
import time
import urllib


def ifregistered(request, openid):
    if RingUser.objects.filter(user_id=openid).exists():
        user = RingUser.objects.filter(user_id=openid)[0]
        user_info = {
            "ifregistered": True,
            "sex": user.sex,
            "age": user.age,
            "height": user.height,
            "weight": user.weight,
            "goal_step": user.target,
        }
        return HttpResponse(json.dumps(user_info))
    else:
        user_info = {"ifregistered": False}
        return HttpResponse(json.dumps(user_info))

@csrf_exempt
def add_guess_subject(request):
    subject = GuessSubject()
    subject.content = request.POST.get('content')
    subject.choiceA = request.POST.get('choiceA')
    subject.choiceB = request.POST.get('choiceB')
    if subject.choiceA and subject.choiceB and subject.content:
        subject.stepsA = 0
        subject.stepsB = 0
        subject.disabled = False
        subject.save()
        return HttpResponse("success")
    else:
        return HttpResponse("failure")


@csrf_exempt
def save_user_bet(request):
    subid = request.GET.get("subid")
    openid = request.GET.get("openid")
    steps = int(request.GET.get("steps"))
    choice = request.GET.get("choice")
    if not RingUser.objects.filter(user_id=openid).exists():
        return HttpResponse("failure")
    user = RingUser.objects.filter(user_id=openid)[0]
    user.steps_totalused += steps
    all_num = get_today_step(user)
    if user.steps_totalused > all_num:
        result = {
            'success':False
        }
        return HttpResponse(json.dumps(result))
    activity = GuessSubject.objects.filter(id=int(subid))[0]
    if choice == 'A':
        activity.stepsA = activity.stepsA + steps
    elif choice == 'B':
        activity.stepsB = activity.stepsB + steps
    activity.save()
    if GuessInfomation.objects.filter(user_id=openid, sub_id=int(subid), choice=choice).exists():
        data_object = GuessInfomation.objects.filter(user_id=openid, sub_id=int(subid), choice=choice)[0]
        data_object.steps += steps
        data_object.save()
    else:
        data_object = GuessInfomation(user_id=openid, sub_id=int(subid), choice = choice, steps = steps)
        data_object.save()
    user.save()
    result = {
        'success':True
    }
    return HttpResponse(json.dumps(result))


@csrf_exempt
def get_guess_subject(request):
    code = request.GET.get('code')
    get_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code'%(AppID,AppSecret,code)
    try:
        f = urllib.urlopen(get_url)
        string_json = f.read()
        reply = json.loads(string_json)
        openid = reply[u'openid']
    except:
        return HttpResponse("Invalid code")
        #openid = "oDetGv9_dqQBv1V-0ySwyDqdLtLs"
    subjects = []
    for dbitem in GuessSubject.objects.filter(disabled=False):
        item = {
            'id':dbitem.id,
            'content':dbitem.content,
            'choiceA':dbitem.choiceA,
            'choiceB':dbitem.choiceB,
            'stepsA':dbitem.stepsA,
            'stepsB':dbitem.stepsB
        }
        subjects.append(item)
    result = {
        'openid':openid,
        'data':subjects
    }
    return HttpResponse(json.dumps(result))


@csrf_exempt
def freeze_activity(request):
    subid = int(request.GET.get("subid"))
    activity = GuessSubject.objects.filter(id=int(subid))
    if activity:
        activity[0].disabled = True
        activity[0].save()
        return HttpResponse("success")
    else:
        return HttpResponse("failure")


@csrf_exempt
def calculate(request):
    subid = int(request.GET.get("subid"))
    choice = request.GET.get("choice")
    activity = GuessSubject.objects.filter(id=int(subid))[0]
    if activity.disabled:
        if activity.result:
            return HttpResponse("already calculated")
        if choice == "A":
            activity.result = "A"
            if activity.stepsA != 0:
                rate = float(activity.stepsB + activity.stepsA) / float(activity.stepsA)
            else:
                rate = 0
            people = GuessInfomation.objects.filter(sub_id=subid, choice='A')
        elif choice == "B":
            activity.result = "B"
            if activity.stepsB != 0:
                rate = float(activity.stepsB + activity.stepsA) / float(activity.stepsB)
            else:
                rate = 0
            people = GuessInfomation.objects.filter(sub_id=subid, choice='B')
        for val in people:
            personal_info = RingUser.objects.filter(user_id=val.user_id)
            singleperson = personal_info[0]
            singleperson.steps_totalused = personal_info[0].steps_totalused - int(rate * val.steps)
            singleperson.save()
        return HttpResponse("success")
    else:
        return HttpResponse("failure")


@csrf_exempt
def auto_save(request):
    sleep = int(request.GET.get('sleep'))
    exercise_and_time = int(request.GET.get('exercise_and_time'))
    if sleep == 1:
        step_user = RingUser.objects.all()
        for user in step_user:
            save_sleep_data(user)
    elif exercise_and_time == 1:
        step_user = RingUser.objects.all()
        for user in step_user:
            save_exercise_data(user)
            save_time_line(user)
        clear_activity()
    return HttpResponse('success')


def clear_activity():
    not_valid = GuessSubject.objects.filter(disabled=True)
    for val in not_valid:
        if val.result:
            GuessInfomation.objects.filter(sub_id=val.id).delete()
            val.delete()


@csrf_exempt
def register(request):
    user_sex = request.GET.get("sex")
    user_age = request.GET.get("age")
    user_height = request.GET.get("height")
    user_wight = request.GET.get("weight")
    user_goal = request.GET.get("goal_step")
    user_openid = request.GET.get("openid")
    if not ((user_sex and user_age and user_height and user_goal and user_wight and user_goal and user_openid) and (user_wight.isdigit() and user_age.isdigit() and user_height.isdigit())):
        return HttpResponse("failure")
    get_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'%(AppID,AppSecret)
    f = urllib.urlopen(get_url)
    string_json = f.read()
    reply = json.loads(string_json)
    #print reply
    access_token = reply[u'access_token']
    get_url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN'%(access_token , user_openid)
    f = urllib.urlopen(get_url)
    string_json = f.read()
    reply = json.loads(string_json)
    nickname = reply[u'nickname']
    headimgurl = reply[u'headimgurl']
    if RingUser.objects.filter(user_id=user_openid).exists():
        user = RingUser.objects.filter(user_id=user_openid)[0]
        user.sex = user_sex
        user.age=user_age
        user.height=user_height
        user.weight=user_wight
        user.target=user_goal
        user.headimgurl = headimgurl
        user.nickname = nickname
        user.save()
    else:
        user_new = RingUser(
            user_id=user_openid,
            sex=user_sex,
            age=user_age,
            height=user_height,
            weight=user_wight,
            target=user_goal,
            last_record=0,
            steps_totalused=0,
            headimgurl=headimgurl,
            nickname=nickname
        )
        user_new.save()
        user_bird = BirdUser(
            openid=user_openid,
            steps_used=0,
            score_today=0,
            score_total=0
        )
        user_jump = JumpUser(
            openid=user_openid,
            steps_used=0,
            score_today=0,
            score_total=0
        )
        user_bird.save()
        user_jump.save()
    return HttpResponse("add info successfully")


def ingame_rank(request):
    openid = request.GET.get("openid")
    game = request.GET.get("game")
    if game == "bird":
        today_objects = BirdUser.objects.all().order_by('-score_today')
        total_objects = BirdUser.objects.all().order_by('-score_total')
    elif game == "jump":
        today_objects = JumpUser.objects.all().order_by('-score_today')
        total_objects = JumpUser.objects.all().order_by('-score_total')
    today_entries = get_partial_ranklist(openid, today_objects, 'today')
    total_entries = get_partial_ranklist(openid, total_objects, 'total')
    result = {
        "today": today_entries,
        "total": total_entries
    }
    return HttpResponse(json.dumps(result))


def get_partial_ranklist(openid, objects, type):
    l = len(objects)
    entries = []
    n = 0
    for item in objects:
        if item.openid == openid:
            break
        else:
            n += 1
    if n == 0:
        indexlist = [0, 1, 2, 3]
    elif n == l - 1 or n == l - 2:
        indexlist = [l - 4, l - 3, l - 2, l - 1]
    else:
        indexlist = [n - 1, n, n + 1, n + 2]
    if l <= 4:
        indexlist = range(l)
    for i in indexlist:
        entry_object = objects[i]
        entry_user = RingUser.objects.get(user_id=entry_object.openid)
        if type == "today":
            score = entry_object.score_today
        else:
            score = entry_object.score_total
        entry = {
            "openid": entry_object.openid,
            "nickname": entry_user.nickname,
            "score": score,
            "rank": i+1,
            "headimgurl": entry_user.headimgurl
        }
        entries.append(entry)
    return entries


def steps_info(request):
    openid = request.GET.get("openid")
    users = RingUser.objects.filter(user_id=openid)
    if len(users) == 0:
        return HttpResponse("no user")
    user = users[0]
    steps_total = get_today_step(user)
    steps_left = steps_total - user.steps_totalused
    result = {
        "total": steps_total,
        "left": steps_left
    }
    return HttpResponse(json.dumps(result))


def start_game(request):
    openid = request.GET.get("openid")
    users = RingUser.objects.filter(user_id=openid)
    if len(users) == 0:
        return HttpResponse(json.dumps({"result": "nouser"}))
    user = users[0]
    game = request.GET.get("game")

    if game == "bird":
        gameuser = BirdUser.objects.get(openid=openid)
        user.steps_totalused += 1000
        gameuser.steps_used += 1000
        user.save()
        gameuser.save()
    elif game == "jump":
        gameuser = JumpUser.objects.get(openid=openid)
        user.steps_totalused += 1000
        gameuser.steps_used += 1000
        user.save()
        gameuser.save()
    return HttpResponse(json.dumps({"result": "success"}))


def end_game(request):
    openid = request.GET.get("openid")
    game = request.GET.get("game")
    score = request.GET.get("score")
    if game == "bird":
        gameusers = BirdUser.objects.filter(openid=openid)
        if len(gameusers) == 0:
            return HttpResponse("no user")
        gameuser = gameusers[0]
        gameuser.score_today += int(score)
        gameuser.score_total += int(score)
        gameuser.save()
    elif game == "jump":
        gameusers = JumpUser.objects.filter(openid=openid)
        if len(gameusers) == 0:
            return HttpResponse("no user")
        gameuser = gameusers[0]
        gameuser.score_today += int(score)
        gameuser.score_total += int(score)
        gameuser.save()
    return HttpResponse(json.dumps({"result": "success"}))


@csrf_exempt
def game_rank(request):
    game = request.GET.get('game')
    start = request.GET.get('start')
    end = request.GET.get('end')
    openid = request.GET.get('openid')
    attention = RecordAttention.objects.filter(source_user_id=openid)
    attention_list = []
    for val in attention:
        attention_list.append(val.target_user_id)
    if game == "bird":
        results_today = BirdUser.objects.all().order_by('-score_today')[start:end]
        results_total = BirdUser.objects.all().order_by('-score_total')[start:end]
    elif game == "jump":
        results_today = JumpUser.objects.all().order_by('-score_today')[start:end]
        results_total = JumpUser.objects.all().order_by('-score_total')[start:end]
    ranklist_today = []
    ranklist_total = []
    for item in results_today:
        itemuser = RingUser.objects.get(user_id=item.openid)
        if item.openid in attention_list:
            is_attention = True
        else:
            is_attention = False
        rankitem = {
            "openid": item.openid,
            "nickname": itemuser.nickname,
            "headimgurl": itemuser.headimgurl,
            "score": item.score_today,
            "is_attention": is_attention
        }
        ranklist_today.append(rankitem)
    for item in results_total:
        itemuser = RingUser.objects.get(user_id=item.openid)
        if item.openid in attention_list:
            is_attention = True
        else:
            is_attention = False
        rankitem = {
            "openid": item.openid,
            "nickname": itemuser.nickname,
            "headimgurl": itemuser.headimgurl,
            "score": item.score_total,
            "is_attention": is_attention
        }
        ranklist_total.append(rankitem)
    result = {
        "today":ranklist_today,
        "total":ranklist_total
    }
    return HttpResponse(json.dumps(result))


def get_rankList(results, attention_list):
    ranklist = []
    for item in results:
        itemuser = RingUser.objects.get(user_id=item.openid)
        if item.openid in attention_list:
            is_attention = True
        else:
            is_attention = False
        rankitem = {
            "openid": item.openid,
            "nickname": itemuser.nickname,
            "headimgurl": itemuser.headimgurl,
            "score": item.score_today,
            "is_attention": is_attention
        }
        ranklist.append(rankitem)
    return ranklist


def get_game_rank(request):
    code = request.GET.get('code')
    get_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code'%(AppID,AppSecret,code)
    try:
        f = urllib.urlopen(get_url)
        string_json = f.read()
        reply = json.loads(string_json)
        openid = reply[u'openid']
    except:
        return HttpResponse("Invalid code")
        #openid = "oDetGv9_dqQBv1V-0ySwyDqdLtLs"

    attention = RecordAttention.objects.filter(source_user_id=openid)
    attention_list = []
    for val in attention:
        attention_list.append(val.target_user_id)
    results_today_bird = BirdUser.objects.all().order_by('-score_today')[0:100]
    results_total_bird = BirdUser.objects.all().order_by('-score_total')[0:100]
    results_today_jump = JumpUser.objects.all().order_by('-score_today')[0:100]
    results_total_jump = JumpUser.objects.all().order_by('-score_total')[0:100]

    ranklist_today_bird = get_rankList(results_today_bird, attention_list)
    ranklist_total_bird = get_rankList(results_total_bird, attention_list)
    ranklist_today_jump = get_rankList(results_today_jump, attention_list)
    ranklist_total_jump = get_rankList(results_total_jump, attention_list)
    result = {
        "openid":openid,
        "today_bird":ranklist_today_bird,
        "total_bird":ranklist_total_bird,
        "today_jump":ranklist_today_jump,
        "total_jump":ranklist_total_jump
    }
    return HttpResponse(json.dumps(result))


def get_sleepdata(request):
    code = request.GET.get('code')
    get_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code'%(AppID,AppSecret,code)
    try:
        f = urllib.urlopen(get_url)
        string_json = f.read()
        reply = json.loads(string_json)
        openid = reply[u'openid']
    except:
        return HttpResponse("Invalid code")
    #return HttpResponse(json.dumps({'isnull':True}))
    data = {}
    if not RingUser.objects.filter(user_id=openid).exists():
        data['isnull'] = True
        return HttpResponse(json.dumps(data))
    data = access_sleeping(openid)
    data['isnull'] = False
<<<<<<< HEAD
    return HttpResponse(json.dumps(data))
=======
    print data
    data['anxious'] = 1
    result = {
        "openid":openid,
        "data":data
    }
    return HttpResponse(json.dumps(result))
>>>>>>> jingao/rest_framework


def get_sportsdata(request):
    code = request.GET.get('code')
    get_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code'%(AppID,AppSecret,code)
    try:
        f = urllib.urlopen(get_url)
        string_json = f.read()
        reply = json.loads(string_json)
        openid = reply[u'openid']
    except:
        return HttpResponse("Invalid code")
    #return HttpResponse(json.dumps({'isnull':True}))
    data = {}
    if not RingUser.objects.filter(user_id=openid).exists():
        data['isnull'] = True
        return HttpResponse(json.dumps(data))
    data = access_exercising(openid)
    data['isnull'] = False
    result = {
        "data":data,
        "openid":openid
    }
    return HttpResponse(json.dumps(result))


def get_time_line_data(request):
    code = request.GET.get('code')
    get_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code'%(AppID,AppSecret,code)
    try:
        f = urllib.urlopen(get_url)
        string_json = f.read()
        reply = json.loads(string_json)
        openid = reply[u'openid']
    except:
        return HttpResponse("Invalid code")
    data = {}
    if not RingUser.objects.filter(user_id=openid).exists():
        data['isnull'] = True
    else:
        save_time_line(RingUser.objects.filter(user_id=openid)[0])
        data['isnull'] = False
        data['data'] = []
        try:
            data['data'].append(get_today_time_line(RingUser.objects.filter(user_id=openid)[0]))
        except:
            data['isnull'] = True
            return HttpResponse(json.dumps(data))
        i = 1
        while(True):
            if i == 7:
                break
            if ActivityRecord.objects.filter(user_name=openid, day_num = i).exists():
                data['data'].append(ActivityRecord.objects.filter(user_name=openid, day_num=i))[0]
                i += 1
            else:
                break
<<<<<<< HEAD
    return HttpResponse(json.dumps(data))
=======
        print data
    result = {
        'data':data,
        'openid':openid
    }
    return HttpResponse(json.dumps(result))
>>>>>>> jingao/rest_framework





def cancel_follow(request, message):
    source_id, target_id = message.split('@')
    RecordAttention.objects.get(source_user_id=source_id, target_user_id=target_id).delete()
    return HttpResponse('OK')


def add_follow(request, message):
    source_id, target_id = message.split('@')
    new_relation = RecordAttention(
        source_user_id=source_id,
        target_user_id=target_id,
        attentionTime=int(time.time())
    )
    new_relation.save()
    return HttpResponse('OK')