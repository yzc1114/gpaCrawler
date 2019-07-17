#!/user/bin/python2.7
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import global_sessions as g


def login(username, password, session_key):
    host = 'http://202.114.234.143'
    login_url = 'http://202.114.234.163/jsxsd/kscj/cjcx_query?Ves632DSdyV=NEW_XSD_XJCJ'
    login_postdata = {'username': username,
                      'password': password,
                      'lt': '',
                      'execution': '',
                      '_eventId': 'submit',
                      }

    user_agent = r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36' \
                 r' (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}

    try:
        login_response = g.global_sessions[session_key]['session'].get(login_url, headers=headers, timeout=5)
    except:
        return None
    if str(login_response.status_code)[0] != "2":
        return "sites_dead"
    login_page_soup = BeautifulSoup(login_response.content.decode('utf-8'))

    href = login_page_soup.find_all('script')[0].contents[0]
    href = href.split("href='")[-1][:-2]
    new_login_url = href

    try:
        login_response = g.global_sessions[session_key]['session'].get(new_login_url, headers=headers, timeout=5)
    except:
        return None
    login_page_soup = BeautifulSoup(login_response.content.decode('utf-8'))

    new_login_url = host + login_page_soup.form['action']

    print(new_login_url)
    all_input = login_page_soup.find_all('input')
    if len(all_input) <= 5:
        return None
    lt = all_input[2]['value']
    execution = all_input[3]['value']
    _eventId = all_input[4]['value']
    login_postdata['lt'] = lt
    login_postdata['execution'] = execution
    login_postdata['_eventId'] = _eventId

    try:
        post_response = g.global_sessions[session_key]['session'].post(url=new_login_url, data=login_postdata,
                                                                     headers=headers, timeout=5)
    except:
        return None
    if str(post_response.status_code)[0] != "2":
        return "sites_dead"
    cookies_dict = g.global_sessions[session_key]['session'].cookies.get_dict()
    post_response_soup = BeautifulSoup(post_response.content.decode('utf-8'))
    form_list = post_response_soup.select('.form_list_user')

    if "CASTGC" in cookies_dict.keys():
        return "login_success"

    if len(form_list) == 3:
        g.global_sessions[session_key].update({'new_login_url': new_login_url, 'login_postdata': login_postdata})
        return "need_captcha"
    if len(form_list) == 2:
        return "login_fail"

    return "login_success"


def login_with_captcha(username, password, session_key, captchaResponse):
    login_postdata = g.global_sessions[session_key]['login_postdata']
    login_postdata.update({
        'username': username,
        'password': password,
        'captchaResponse': captchaResponse
    })
    user_agent = r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36' \
                 r' (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}
    try:
        post_response = g.global_sessions[session_key]['session'].post(url=g.global_sessions[session_key]['new_login_url'],
                                                                     data=login_postdata, headers=headers, timeout=5)
    except:
        return None
    if str(post_response.status_code)[0] != "2":
        return "sites_dead"
    cookies_dict = g.global_sessions[session_key]['session'].cookies.get_dict()
    post_response_soup = BeautifulSoup(post_response.content.decode('utf-8'))
    form_list = post_response_soup.select('.form_list_user')
    if "CASTGC" in cookies_dict.keys():
        return "login_success"

    if len(form_list) == 3:
        return "login_fail_need_refresh"
    elif len(form_list) == 2:
        return "login_fail_no_need_refresh"
    else:
        return "login_success"
