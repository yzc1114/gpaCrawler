import random
from flask import Flask
from flask import request
import requests
from bs4 import BeautifulSoup
import json
import datetime


app = Flask(__name__)
app.debug = True

global_sessions = {}

host = 'http://202.114.234.143'
login_url = 'http://202.114.234.143/authserver/login?service=http%3A%2F%2F202.114.234.160%2Fjsxsd%2Fkscj%2Fcjcx_query%3FVes632DSdyV%3DNEW_XSD_XJCJ'
to_get_captcha_url = 'http://202.114.234.143/authserver/captcha.html'
# get_url
get_url = 'http://202.114.234.160/jsxsd/kscj/cjcx_query?Ves632DSdyV=NEW_XSD_XJCJ'
search_list_url = 'http://202.114.234.160/jsxsd/kscj/cjcx_list'
# login_postdata = {'username': username,
#                   'password': password,
#                   'lt': '',
#                   'execution': '',
#                   '_eventId': 'submit',
#                   }

user_agent = r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36' \
                 r' (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}


@app.route('/')
def index():
    return 'Hello,World'


@app.route('/get_userinfo', methods=['GET', 'POST'])
def get_userinfo():
    if request.method == 'POST':
        # print("POST")
        # print(request.form)
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
        # print(row_data)
        json_data = json.loads(row_data)
        json_data['session_key'] = json_data['session_key'].replace("+", "z")
        json_data['session_key'] = json_data['session_key'].replace("/", "s")
        if 'openid' in json_data.keys():
            return json.dumps(json_data)
        else:
            return json.dumps(json_data)
    else:
        # print("ST")
        pass


@app.route('/get_captcha', methods=['GET'])
def get_captcha():
    global global_sessions
    session_key = request.args.get('session_key')
    session_key.replace(" ", "+")  # 
    copied_headers = headers.copy()
    copied_headers.update({"content-type": "application/x-jpg"})
    img_response = global_sessions[session_key]['session'].get(url=to_get_captcha_url, headers=copied_headers)
    temp_file_path = './tempImgs/temp_' + session_key + '.jpg'
    with open(temp_file_path, 'wb') as fb:
        fb.write(img_response.content)
    with open(temp_file_path, 'rb') as f:
        return f.read()



@app.route('/fetchList', methods=['GET', 'POST'])
def sign_in_fetch_list():
    global global_sessions
    username = request.form['username']
    password = request.form['password']
    session_key = request.form['session_key']
    fetched_list = fetch_list(username, password, session_key)
    if fetched_list:
        # print(fetched_list)
        json_data = json.dumps(fetched_list)
        return json_data
    else:
        return "unable to fetch"


@app.route('/fetchListWithCaptcha', methods=['GET', 'POST'])
def sign_in_fetch_list_with_captcha():
    global global_sessions
    username = request.form['username']
    password = request.form['password']
    session_key = request.form['session_key']
    captchaResponse = request.form['captchaResponse']
    if session_key not in global_sessions.keys():
        return "no session key found"
    else:
        fetched_list = fetch_list(username, password, session_key, captcha=captchaResponse)
        if fetched_list:
            print(fetched_list)
            json_data = json.dumps(fetched_list)
            return json_data
        else:
            return "unable to fetch"


def fetch_list(username, password, session_key, captcha=None):
    global global_sessions
    host = 'http://202.114.234.143'
    login_url = 'http://202.114.234.143/authserver/login?service=http%3A%2F%2F202.114.234.160%2Fjsxsd%2Fkscj%2Fcjcx_query%3FVes632DSdyV%3DNEW_XSD_XJCJ'
    to_get_captcha_url = 'http://202.114.234.143/authserver/captcha.html'
    # get_ur
    get_url = 'http://202.114.234.160/jsxsd/kscj/cjcx_query?Ves632DSdyV=NEW_XSD_XJCJ'
    search_list_url = 'http://202.114.234.160/jsxsd/kscj/cjcx_list'
    login_postdata = {'username': username,
                      'password': password,
                      'lt': '',
                      'execution': '',
                      '_eventId': 'submit',
                      }

    user_agent = r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36' \
                 r' (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}

    if not captcha:
        #
        global_sessions.update({session_key: {'session': requests.session()}})
        login_response = login(username, password, session_key)
        if not login_response:
            return None
        elif login_response == "sites_dead":
            return "sites_dead"
        elif login_response == "need_captcha":
            return "need_captcha"
        elif login_response == "login_fail":
            return "login_fail"
        else:
            pass
    else:
        #
        login_response = login_with_captcha(username, password, session_key, captcha)
        if not login_response:
            return None
        elif login_response == "sites_dead":
            return "sites_dead"
        elif login_response == "login_fail_need_refresh":
            return "login_fail_refresh_captcha"
        elif login_response == "login_fail_no_need_refresh":
            return "login_fail"
        else:
            pass
    curr_year = None
    if username[:2] == "20":
        curr_year = username[:4]
    else:
        curr_year = "20" + username[:2]
    now = datetime.datetime.now()
    now_year = now.strftime('%Y')
    now_month = now.strftime('%m')
    to_be_returned_list = []

    while curr_year <= now_year:
        
        kksj = curr_year + '-' + curr_year[:-1] + str(int(curr_year[-1]) + 1) + '-' + '1'

        search_list_postdata = {
            'kksj': kksj,
            'kcxz': '',
            'kcmc': '',
            'xsfs': 'all'
        }
        out = False
        for i in range(2):
            #
            if now_year == curr_year and int(now_month) < 12:
                out = True
            try:
                try_get_list_response = global_sessions[session_key]['session'].post(search_list_url,
                                                                          data=search_list_postdata,
                                                                          headers=headers)
            except:
                break
            if str(try_get_list_response.status_code)[0] != '2':
                return "sites_dead"
            #print(try_get_list_response.content.decode())
            list_soup = BeautifulSoup(try_get_list_response.content.decode('utf-8'))
            all_tr = list_soup.find_all('tr')
            #
            group_of_data = []
            if(len(all_tr) == 2):
                break
            else:
                for j in range(2, len(all_tr)):
                    # 
                    all_td = all_tr[j].find_all('td')
                    if len(all_td) <= 10:
                        break
                    dict_to_be_inserted = {}
                    dict_to_be_inserted.update(lesson_name=all_td[4].string,
                                               grade=all_td[7].a.string,
                                               credit=all_td[8].string,
                                               gpa=all_td[10].string)
                    group_of_data.append(dict_to_be_inserted)

            term_dict = {}
            term_dict.update(term=kksj, grade=group_of_data)
            to_be_returned_list.append(term_dict)
            kksj = kksj[:-1] + '2'
            search_list_postdata['kksj'] = kksj
            if (int(now_year) - int(curr_year) == 1) and int(now_month) < 5:
                out = True
                break
        if out:
            break
        curr_year = str(int(curr_year) + 1)
        # 
    return to_be_returned_list


def login(username, password, session_key):
    global global_sessions
    host = 'http://202.114.234.143'
    login_url = 'http://202.114.234.143/authserver/login?service=http%3A%2F%2F202.114.234.160%2Fjsxsd%2Fkscj%2Fcjcx_query%3FVes632DSdyV%3DNEW_XSD_XJCJ'
    to_get_captcha_url = 'http://202.114.234.143/authserver/captcha.html'
    #
    get_url = 'http://202.114.234.160/jsxsd/kscj/cjcx_query?Ves632DSdyV=NEW_XSD_XJCJ'
    search_list_url = 'http://202.114.234.160/jsxsd/kscj/cjcx_list'
    login_postdata = {'username': username,
                      'password': password,
                      'lt': '',
                      'execution': '',
                      '_eventId': 'submit',
                      }

    user_agent = r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36' \
                 r' (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}

    #
    # session = requests.session()

    try:
        login_response = global_sessions[session_key]['session'].get(login_url, headers=headers)
    except:
        # 
        return None
    if str(login_response.status_code)[0] != "2":
        return "sites_dead"
    login_page_soup = BeautifulSoup(login_response.content.decode('utf-8'))
    new_login_url = host + login_page_soup.form['action']

    
    all_input = login_page_soup.find_all('input')
    # print("all_input")
    # print(all_input)
    if len(all_input) <= 5:
        return None
    lt = all_input[2]['value']
    execution = all_input[3]['value']
    _eventId = all_input[4]['value']
    login_postdata['lt'] = lt
    login_postdata['execution'] = execution
    login_postdata['_eventId'] = _eventId

    #
    # print(login_postdata)
    try:
        post_response = global_sessions[session_key]['session'].post(url=new_login_url, data=login_postdata, headers=headers)
    except:
        return None
    # 
    if str(post_response.status_code)[0] != "2":
        return "sites_dead"
    cookies_dict = global_sessions[session_key]['session'].cookies.get_dict()
    # print(cookies_dict)
    # printst response")
    # print(post_response.content.decode())
    post_response_soup = BeautifulSoup(post_response.content.decode('utf-8'))
    form_list = post_response_soup.select('.form_list_user')
    # print(form_list)
    if "CASTGC" in cookies_dict.keys():
        return "login_success"

    if len(form_list) == 3:
        
        global_sessions[session_key].update({'new_login_url': new_login_url, 'login_postdata': login_postdata})
        return "need_captcha"
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # 
    if len(form_list) == 2:
        #
        return "login_fail"

    return "login_success"


def login_with_captcha(username, password, session_key, captchaResponse):
    global global_sessions
    host = 'http://202.114.234.143'
    login_url = 'http://202.114.234.143/authserver/login?service=http%3A%2F%2F202.114.234.160%2Fjsxsd%2Fkscj%2Fcjcx_query%3FVes632DSdyV%3DNEW_XSD_XJCJ'
    to_get_captcha_url = 'http://202.114.234.143/authserver/captcha.html'
    #
    get_url = 'http://202.114.234.160/jsxsd/kscj/cjcx_query?Ves632DSdyV=NEW_XSD_XJCJ'
    search_list_url = 'http://202.114.234.160/jsxsd/kscj/cjcx_list'
    login_postdata = global_sessions[session_key]['login_postdata']
    login_postdata.update({
        'username': username,
        'password': password,
        'captchaResponse': captchaResponse
    })
    user_agent = r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36' \
                 r' (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}
    #ost data")
    # print(login_postdata)
    try:
        post_response = global_sessions[session_key]['session'].post(url=global_sessions[session_key]['new_login_url'],
                                                                     data=login_postdata, headers=headers)
    except:
        return None
    if str(post_response.status_code)[0] != "2":
        return "sites_dead"
    # prin:")
    cookies_dict = global_sessions[session_key]['session'].cookies.get_dict()
    # print response")
    # print(post_response.content.decode())
    post_response_soup = BeautifulSoup(post_response.content.decode('utf-8'))
    form_list = post_response_soup.select('.form_list_user')
    # print(form_list)
    # print(cookies_dict)
    if "CASTGC" in cookies_dict.keys():
        return "login_success"

    if len(form_list) == 3:
        return "login_fail_need_refresh"
    elif len(form_list) == 2:
        return "login_fail_no_need_refresh"
    else:
        return "login_success"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
