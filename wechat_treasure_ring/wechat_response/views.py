# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
import wechat_sdk as sdk
from wechat_response.models import *
from wechat_response.data import *
from wechat_treasure_ring.settings import *
from wechat_treasure_ring.define import *
from wechat_sdk.messages import (
    EventMessage,
    TextMessage
)

import urllib
import json
import sys
import wechat_response.data as data_tool
import time

reload(sys)
sys.setdefaultencoding('UTF-8')


@csrf_exempt
def weixin(request):
    # 实例化 We_chat_Basic
    we_chat = WechatBasic(
        token=WECHAT_TOKEN,
        appid=AppID,
        appsecret=AppSecret
    )
    if request.method == "GET":
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        if not we_chat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
            return HttpResponse("Verify failed")
        else:
            return HttpResponse(request.GET.get("echostr"), content_type="text/plain")
    else:
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        if not we_chat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
            return HttpResponse("Verify failed")
        try:       
            we_chat.parse_data(data=request.body)
        except ParseError:
            return HttpResponseBadRequest('Invalid XML Data')
        message = we_chat.get_message()
        if isinstance(message, TextMessage):
            result = process_text_message(message)
            response = we_chat.response_text(result)
            return HttpResponse(response)
        elif isinstance(message, EventMessage):
            if message.type == 'subscribe':
                response = we_chat.response_text(u'''欢迎来到‘珍环传’运动手环微信公众平台，请先点击‘个人信息’按钮进行注册哦～。
输入‘关注’+‘昵称’关注好友
输入‘我的关注’或者‘关注列表’查看我关注的与关注我的人
输入‘取消关注’+‘昵称’取消关注好友
输入‘查看信息’+‘昵称’查看关注好友的信息''')
                return HttpResponse(response)
            elif message.type == 'click':
                if RingUser.objects.filter(user_id=message.source).exists():
                    if message.key == 'STEP_COUNT':
                        step_user = RingUser.objects.filter(user_id=message.source)[0]
                        try:
                            target = step_user.target
                            step = get_today_step(step_user)
                            goal_completion = int(float(step) / target * 100)
                            left_step = step - step_user.steps_totalused
                            response = we_chat.response_text(u'跑了' + str(step) + u'步咯，完成今日目标：' + str(goal_completion) + u'%，剩余可用步数' + str(left_step))
                        except Exception as e:
                            print e
                        # 里面的数字应由其他函数获取
                    elif message.key == 'RANK_LIST':
                        response = RESPONSE_RANKLIST % (message.source, message.target)
                    elif message.key == 'DOJUMP':
                        response = we_chat.response_news([{
                                'title': u'Let us play Dodo_jump together',
                                'description': 'a simple but interesting game',
                                'picurl': 'http://7xn2s5.com1.z0.glb.clouddn.com/jump.png',
                                'url': 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+AppID+'&redirect_uri=http%3a%2f%2f'+LOCAL_IP+'%2fdodojump.html'+'&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'}])
                    elif message.key == 'FLAPPY':
                        response = we_chat.response_news([{
                                'title': u'Let us play Flappy Bird together',
                                'description': 'a simple but interesting game',
                                'picurl': 'http://7xn2s5.com1.z0.glb.clouddn.com/flappy_bird.jpg',
                                'url': 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+AppID+'&redirect_uri=http%3a%2f%2f'+LOCAL_IP+'%2fbird.html'+'&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'}])
                    elif message.key == 'SLEEP_CHART':
                        response = we_chat.response_news([{
                            'title': u'睡眠质量分析',
                            'description': '综合一周睡眠情况和过去一个月的睡眠情况给出最权威的睡眠建议',
                            'picurl': 'http://7xn2s5.com1.z0.glb.clouddn.com/sleep.jpg',
                            'url': 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+AppID+'&redirect_uri=http%3a%2f%2f'+LOCAL_IP+'%2fsleepAnalysis.html'+'&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'}])
                    elif message.key == 'EXERCISE_CHART':
                        response = we_chat.response_news([{
                            'title': u'运动质量分析',
                            'description': '图文并茂，专家指导，你值得拥有！',
                            'picurl': 'http://7xn2s5.com1.z0.glb.clouddn.com/info.jpg',
                            'url': 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+AppID+'&redirect_uri=http%3a%2f%2f'+LOCAL_IP+'%2fexerciseAnalysis.html'+'&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'}])
                    elif message.key == 'TIME_LINE':
                        response = we_chat.response_news([{
                            'title': u'时间线',
                            'description': '看看一天各个时段的运动状况',
                            'picurl': 'http://7xn2s5.com1.z0.glb.clouddn.com/sport.png',
                            'url': 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+AppID+'&redirect_uri=http%3a%2f%2f'+LOCAL_IP+'%2ftimeline.html'+'&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'}])
                    elif message.key == 'SCORE_RANK':
                        response = we_chat.response_news([{
                            'title': u'游戏龙虎榜',
                            'description': '龙虎榜',
                            'picurl': 'http://7xn2s5.com1.z0.glb.clouddn.com/rank.png',
                            'url': 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+AppID+'&redirect_uri=http%3a%2f%2f'+LOCAL_IP+'%2frank.html'+'&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'}])
                    elif message.key == 'CHEER':
                        response = we_chat.response_text(u'We are family!')
                    elif message.key == 'GUESS':
                        response = we_chat.response_news([{
                            'title': u'欢迎参加竞猜',
                            'description': '欢迎参加竞猜，用步数当赌注，竞猜体育赛事等当下活动，竞猜获得的步数可用于当日的游戏活动。',
                            'picurl': 'http://'+LOCAL_IP+'/guess/guess.png',
                            'url': 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+AppID+'&redirect_uri=http%3a%2f%2f'+LOCAL_IP+'%2fguess.html'+'&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'}])
                    return HttpResponse(response)
                else:
                    response = we_chat.response_text(u'请先注册哦~~(点击个人信息按钮即可注册)')
                    return HttpResponse(response)
            return HttpResponse('OK')


def get_userinfo(request):
    code = request.GET.get("code")
    get_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code'%(AppID,AppSecret,code)
    try:
        f = urllib.urlopen(get_url)
        string_json = f.read()
        reply = json.loads(string_json)
        openid = reply[u'openid']
    except:
        return HttpResponse("Invalid code")
    result = {
        'openid':openid
    }
    return HttpResponse(json.dumps(result))


def process_text_message(msg):
    con = msg.content.split(" ")
    argus = len(con)
    if con[0] == u"关注":
        if argus == 1:
            return u"输入‘关注’+‘用户名’关注别人"
        step_user = RingUser.objects.filter(nickname=con[1])
        relation = RecordAttention.objects.filter(source_user_id=msg.source)
        if step_user:
            for var in relation:
                if var.target_user_id == step_user[0].user_id:
                    return u"你已经关注此人了"
            new_relation = RecordAttention(
                source_user_id=msg.source,
                target_user_id=step_user[0].user_id,
                attentionTime=int(time.time())
            )
            new_relation.save()
            message_return = u"关注:" + con[1] + u" 成功"
            return message_return
        else:
            return u"没有此用户或此用户没有注册><"
    elif con[0] == u"查看信息":
        if argus == 1:
            return u"输入‘查看信息’+‘昵称’查看关注人的运动信息"
        step_user = RingUser.objects.filter(nickname=con[1])
        relation = RecordAttention.objects.filter(source_user_id=msg.source)
        if step_user:
            for var in relation:
                if var.target_user_id == step_user[0].user_id:
                    target = step_user[0].target
                    step = get_today_step(step_user[0])
                    left_step = step - step_user[0].steps_totalused
                    goal_completion = int(float(step) / target * 100)
                    message_return = con[1] + u"已经走了" + str(step) + u"步了，" + u"完成今日目标：" + str(goal_completion) + u'%，剩余可用步数：' + str(left_step)
                    return message_return
            return u"你没有关注"+con[1]+u",不能查看他的信息"
        else:
            return u"没有此用户或此用户没有注册><"
    elif con[0] == u"关注列表" or con[0] == u"我的关注":
        name_list = ""
        step_user = RecordAttention.objects.filter(source_user_id=msg.source)
        for val in step_user:
            target_user_id = val.target_user_id
            target_user = RingUser.objects.filter(user_id=target_user_id)[0]
            name_list += target_user.nickname + "\n"
        length = len(name_list)
        if length == 0:
            return u"你还没有关注任何人那～"
        name_list = name_list[0:(length-1)]
        return name_list
    elif con[0] == u"谁关注我" or con[0] == u"关注我的人":
        name_list = ""
        relation = RecordAttention.objects.filter(target_user_id=msg.source)
        for val in relation:
            source_user_id = val.source_user_id
            source_user = RingUser.objects.filter(user_id=source_user_id)[0]
            name_list += source_user.nickname + "\n"
        length = len(name_list)
        if length == 0:
            return u"没有任何人关注你哦～"
        name_list = name_list[0:(length-1)]
        return name_list
    elif con[0] == u"取消关注":
        if argus == 1:
            return u"输入‘取消关注’+‘用户名’取消关注他人"
        target_user = RingUser.objects.filter(nickname=con[1])
        if target_user:
            step_user = RecordAttention.objects.filter(source_user_id=msg.source)
            temp = 0
            for val in step_user:
                if val.target_user_id == target_user[0].user_id:
                    temp = 1
                    break
            if temp == 1:
                RecordAttention.objects.get(source_user_id=msg.source, target_user_id=target_user[0].user_id).delete()
                message_return = u"取消关注:" + con[1] + u" 成功"
            else:
                message_return = u"你并没有关注此人"
            return message_return
        else:
            return u"没有此用户或此用户没有注册><"
    elif con[0] == u"竞猜":
        result_str = ''
        activity_list = get_user_bet(msg)
        if activity_list == []:
            return u"你还没有参与任何竞彩活动"
        for val in activity_list:
            if val[u"state"][0] == u"1":
                result = val[u"state"][1:] + u"赢了"
            else:
                result = u"比赛仍在进行中"
            result_str += val[u"content"] + u"：你在" + val[u"choiceA"] + u"下注" + str(val[u"stepsA"]) + u"步， " + val[u"choiceB"] + u"下注" + str(val[u"stepsB"]) + u"步，" + result + u"\n"
        if result_str == "":
            result_str = u"你还没有参加竞猜活动，请点击 玩玩游戏->竞猜 来参与竞猜"
        return result_str


def get_user_bet(msg):
    openid = msg.source
    print openid
    bet_list = []
    if GuessInfomation.objects.filter(user_id=openid).exists():
        data_objects = GuessInfomation.objects.filter(user_id=openid)
        sub_list = []
        for val in data_objects:
            if not (val.sub_id in sub_list):
                sub_list.append(val.sub_id)
        for val in sub_list:
            activity = GuessSubject.objects.filter(id=int(val))[0]
            datas = GuessInfomation.objects.filter(user_id=openid, sub_id=val)
            Astep = 0
            Bstep = 0
            for data in datas:
                if data.choice == "A":
                    Astep = Astep + data.steps
                elif data.choice == "B":
                    Bstep += data.steps
            if activity.disabled == 1:
                if activity.result == "A":
                    bet_list.append({"content":activity.content, "choiceA":activity.choiceA, "choiceB":activity.choiceB, "stepsA":Astep, "stepsB":Bstep, "state":("1" + activity.choiceA)})
                elif activity.result == "B":
                    bet_list.append({"content":activity.content, "choiceA":activity.choiceA, "choiceB":activity.choiceB, "stepsA":Astep, "stepsB":Bstep, "state":("1" + activity.choiceB)})
            else:
                bet_list.append({"content":activity.content, "choiceA":activity.choiceA, "choiceB":activity.choiceB, "stepsA":Astep, "stepsB":Bstep, "state":("0" + str(activity.result))})
    return bet_list

@csrf_exempt
def getid_register(request):
    code = request.GET.get('code')
    get_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code'%(AppID,AppSecret,code)
    try:
        f = urllib.urlopen(get_url)
        string_json = f.read()
        reply = json.loads(string_json)
        #print reply
        openid = reply[u'openid']
        #print openid
        if RingUser.objects.filter(user_id=openid).exists():
            user = RingUser.objects.filter(user_id=openid)[0]
            result = {
                "ifregistered": True,
                "sex": user.sex,
                "age": user.age,
                "height": user.height,
                "weight": user.weight,
                "goal_step": user.target,
                "openid": openid
            }
        else:
            result = {
                "openid":openid,
                "ifregistered":False
            }
    except:
        return HttpResponse("Invalid code")
    return HttpResponse(json.dumps(result))
