# -*-coding:utf-8-*-
import os
import urllib2
import json
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
LOCAL_IP = os.environ.get('SITE_DOMAIN', "123")
AppID = os.environ.get('APP_ID', "123")
AppSecret = os.environ.get('APP_SECRET', "123")
MENU = """
{
    "button": [
        {
            "type": "view",
            "name": "个人信息",
            "url": "%s"
        },
        {
            "name": "健康功能",
            "sub_button": [
                {
                    "type": "click",
                    "name": "看步数",
                    "key": "STEP_COUNT"
                },
                {
                    "type": "view",
                    "name": "时间线",
                    "url": "%s"
                },
                {
                    "type": "click",
                    "name": "排行榜",
                    "key": "RANK_LIST"
                },
                {
                    "type": "click",
                    "name": "数据报表",
                    "key": "CHART"
                }
            ]
        },
        {
            "name": "玩玩游戏",
            "sub_button": [
                {
                    "type": "click",
                    "name": "2048",
                    "key": "2048"
                },
                {
                    "type": "click",
                    "name": "fp_bird",
                    "key": "FLAPPY"
                },
                {
                    "type": "view",
                    "name": "龙虎榜",
                    "url": "%s"
                }
            ]
        }
    ]
}
"""


USER_URL='https://open.weixin.qq.com/connect/oauth2/authorize?appid='+AppID+'&redirect_uri=http%3a%2f%2f'+LOCAL_IP+'%2fregister.html'+'&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'
RANK_URL='https://open.weixin.qq.com/connect/oauth2/authorize?appid='+AppID+'&redirect_uri=http%3a%2f%2f'+LOCAL_IP+'%2frank.html'+'&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'
TIME_URL='https://open.weixin.qq.com/connect/oauth2/authorize?appid='+AppID+'&redirect_uri=http%3a%2f%2f'+LOCAL_IP+'%2ftimeline.html'+'&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'

def create_menu():
    get_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (AppID,AppSecret)
    f = urllib2.urlopen(get_url)
    string_json = f.read()
    access_token = json.loads(string_json)['access_token']
    post_url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=" + access_token
    request = urllib2.urlopen(post_url, (MENU % (USER_URL,TIME_URL,RANK_URL)).encode('utf-8'))
    print request.read()

if __name__=='__main__':
    print LOCAL_IP
    create_menu()
