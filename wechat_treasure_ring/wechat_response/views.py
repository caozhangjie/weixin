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
        if "bet" in request.GET:
            return get_user_bet(request)
        if not we_chat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
            return HttpResponse("Verify failed")
        else:
            #create_menu()
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
        if isinstance(message, EventMessage):
            if message.type == 'click':
                if message.key == 'STEP_COUNT':
                    step_user = RingUser.objects.filter(user_id=message.source)[0]
                    if step_user:
                        try:
                            target = step_user.target
                            step = get_today_step(step_user)
                            goal_completion = int(float(step) / target * 100)
                            response = we_chat.response_text(u'跑了' + str(step) + u'步咯，完成今日目标：' + str(goal_completion) + u'%')
                        except Exception as e:
                            print e
                        # 里面的数字应由其他函数获取
                        return HttpResponse(response)
                    else:
                        response = we_chat.response_text(u'Sorry, there\' no data about you in our database.')
                        return HttpResponse(response)

                elif message.key == 'RANK_LIST':
                    response = RESPONSE_RANKLIST % (message.source, message.target)
                    return HttpResponse(response)  

                elif message.key == '2048':
                    response = we_chat.response_news([{
                            'title': u'Let us play 2048 together',
                            'description': 'a simple but interesting game',
                            'picurl': 'http://7xn2s5.com1.z0.glb.clouddn.com/2048.jpg',
                            'url': 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+AppID+'&redirect_uri=http%3a%2f%2f'+LOCAL_IP+'%2fdodojump.html'+'&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'}])
                    return HttpResponse(response)

                elif message.key == 'FLAPPY':
                    response = we_chat.response_news([{
                            'title': u'Let us play Flappy Bird together',
                            'description': 'a simple but interesting game',
                            'picurl': 'http://7xn2s5.com1.z0.glb.clouddn.com/flappy_bird.jpg',
                            'url': 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+AppID+'&redirect_uri=http%3a%2f%2f'+LOCAL_IP+'%2fflyingdog.html'+'&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'}])
                    return HttpResponse(response)

                elif message.key == 'CHART':
                    print "here"
                    response = we_chat.response_news([{
                        'title': u'Today\'s amount of exercise',
                        'description': 'data analysis',
                        'picurl': 'http://7xn2s5.com1.z0.glb.clouddn.com/info.jpg',
                        'url': 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+AppID+'&redirect_uri=http%3a%2f%2f'+LOCAL_IP+'%2fsleepAnalysis.html'+'&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'}])
                    return HttpResponse(response)

                elif message.key == 'CHEER':
                    response = we_chat.response_text(u'We are family!')
                    return HttpResponse(response)
            return HttpResponse('OK')


def get_userinfo(request):
    code = request.GET.get("code")
    #return 1
    get_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code'%(AppID,AppSecret,code)
    try:
        f = urllib.urlopen(get_url)
        string_json = f.read()
        reply = json.loads(string_json)
        openid = reply['openid']
        access_token = reply['access_token']
        get_url = 'https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN'%(access_token,openid)
        f = urllib.urlopen(get_url)
        string_json = f.read()
        reply = json.loads(string_json)
        result = {
            "openid":reply['openid'],
            "nickname":reply['nickname'],
            "headimgurl":reply['headimgurl']
        }
    except:
        return HttpResponse("Invalid code")
    if RingUser.objects.filter(user_id=openid).exists():
        user = RingUser.objects.get(user_id=openid)
        user.nickname = reply['nickname']
        user.headimgurl = reply['headimgurl']
        user.save()
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
    elif con[0] == u"关注列表" or con[0] == u"我的关注":
        name_list = ""
        step_user = RecordAttention.objects.filter(source_user_id=msg.source)
        for val in step_user:
            target_user_id = val.target_user_id
            target_user = RingUser.objects.filter(user_id=target_user_id)[0]
            name_list += target_user.nickname + "\n"
        length = len(name_list)
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
            print temp
            if temp == 1:
                RecordAttention.objects.get(source_user_id=msg.source, target_user_id=target_user[0].user_id).delete()
                message_return = u"取消关注:" + con[1] + u" 成功"
            else:
                message_return = u"你并没有关注此人"
            return message_return
        else:
            return u"没有此用户或此用户没有注册><"


def get_user_bet(request):
    openid = request.GET.get("openid")
    bet_list = list()
    if GuessInfomation.objects.filter(user_id=openid).exists():
        data_objects = GuessInfomation.objects.filter(user_id=openid)
        sub_list = list()
        for val in data_objects:
            if not (val.sub_id in sub_list):
                sub_list.append(val.sub_id)
        for val in sub_list:
            activity = GuessSubject.objects.filter(id=int(val))[0]
            datas = GuessInfomation.objects.filter(user_id=openid, id=val)
            Astep = 0
            Bstep = 0
            for data in datas:
                if data.choice == "A":
                    Astep += data.steps
                elif data.choice == "B":
                    Bstep += data.steps
            if activity.disabled:
                if activity.result == "A":
                    bet_list.append({"content":activity.content, "contentA":activity.choiceA, "contentB":activity.choiceB, "stepsA":Astep, "stepsB":Bstep, "state":("finished, result: " + activity.choiceA)})
                elif activity.result == "B":
                    bet_list.append({"content":activity.content, "contentA":activity.choiceA, "contentB":activity.choiceB, "stepsA":Astep, "stepsB":Bstep, "state":("finished, result: " + activity.choiceB)})
            else:
                bet_list.append({"content":activity.content, "contentA":activity.choiceA, "contentB":activity.choiceB, "stepsA":Astep, "stepsB":Bstep, "state":("processing" + str(activity.result))})
    return HttpResponse(json.dumps(bet_list))
