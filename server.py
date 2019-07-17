#!/user/bin/python2.7
# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
import json
from fetch_list import *
import global_sessions as g

app = Flask(__name__)
app.debug = False

default_announcement = "个人开发小程序，能力有限，多多包涵。遇到卡顿可能是由于教务部网站无法登陆，也有可能是我的服务器性能太渣。若有意向与我一同维护该项目，请联系我。qq:1021777674"


host = 'http://202.114.234.143'
login_url = 'http://202.114.234.143/authserver/login?service=http%3A%2F%2F202.114.234.160%2Fjsxsd%2Fkscj%2Fcjcx_query%3FVes632DSdyV%3DNEW_XSD_XJCJ'
to_get_captcha_url = 'http://202.114.234.143/authserver/captcha.html'
get_url = 'http://202.114.234.160/jsxsd/kscj/cjcx_query?Ves632DSdyV=NEW_XSD_XJCJ'
search_list_url = 'http://202.114.234.160/jsxsd/kscj/cjcx_list'

user_agent = r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36' \
                 r' (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}


@app.route('/')
def index():
    return 'Hello,World'


@app.route('/get_userinfo', methods=['POST'])
def get_userinfo():
    if request.method == 'POST':
        JSCODE = request.form['JSCODE']
        appid = 'wxdeee740ab9784055'
        secret = '9dcffb72be54ae459f895d657a4f78ff'
        response = requests.get(url='https://api.weixin.qq.com/sns/jscode2session?appid='
                                + appid
                                + '&secret='
                                + secret
                                + '&js_code='
                                + JSCODE
                                + '&grant_type=authorization_code')
        row_data = response.content.decode('utf-8')
        json_data = json.loads(row_data)
        json_data['session_key'] = json_data['session_key'].replace("+", "z")
        json_data['session_key'] = json_data['session_key'].replace("/", "s")
        return json.dumps(json_data)
    else:
        pass


@app.route('/get_captcha', methods=['GET'])
def get_captcha():
    session_key = request.args.get('session_key')
    session_key.replace(" ", "+")
    copied_headers = headers.copy()
    copied_headers.update({"content-type": "application/x-jpg"})
    if session_key not in g.global_sessions.keys():
        return "no session key found"
    img_response = g.global_sessions[session_key]['session'].get(url=to_get_captcha_url, headers=copied_headers, timeout=5)
    temp_file_path = './static/tempImgs/temp_' + session_key + '.jpg'
    with open(temp_file_path, 'wb') as fb:
        fb.write(img_response.content)
    return temp_file_path[2:]


@app.route('/fetchList', methods=['GET', 'POST'])
def sign_in_fetch_list():
    username = request.form['username']
    password = request.form['password']
    session_key = request.form['session_key']
    fetched_list = fetch_list(username, password, session_key)
    if type(fetched_list) == str:
        return fetched_list
    if fetched_list is None:
        return "unable to fetch"

    g.global_sessions.pop(session_key)
    json_data = json.dumps(fetched_list)
    return json_data


@app.route('/fetchListWithCaptcha', methods=['GET', 'POST'])
def sign_in_fetch_list_with_captcha():
    username = request.form['username']
    password = request.form['password']
    session_key = request.form['session_key']
    captchaResponse = request.form['captchaResponse']
    if session_key not in g.global_sessions.keys():
        return "no session key found"
    else:
        fetched_list = fetch_list(username, password, session_key, captcha=captchaResponse)
        if type(fetched_list) == str:
            return fetched_list
        if fetched_list is None:
            return "unable to fetch"
        g.global_sessions.pop(session_key)
        json_data = json.dumps(fetched_list)
        return json_data


@app.route('/setAnnouncement', methods=['POST'])
def set_announcement():
    global default_announcement
    default_announcement = request.form['content']
    return "success"


@app.route('/getAnnouncement', methods=['GET'])
def get_announcement():
    return default_announcement


@app.route('/setAnnouncement', methods=['GET'])
def get_setting_a_page():
    return '''
    <form action='/setAnnouncement' method="post" style="width: 500px;">
        <input type="text" name="content" value="{}"></input>
        <input type="submit" value="提交"/>
    </form>
    '''.format(default_announcement)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
