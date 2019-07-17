#!/user/bin/python2.7
# -*- coding: utf-8 -*-
from login import *
import global_sessions as g


def fetch_list(username, password, session_key, captcha=None):
    search_list_url = 'http://202.114.234.163/jsxsd/kscj/cjcx_list'
    user_agent = r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36' \
                 r' (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}

    if not captcha:
        g.global_sessions.update({session_key: {'session': requests.session()}})
        login_response = login(username, password, session_key)
        if not login_response:
            return None
        if type(login_response) == str and login_response != "login_success":
            return login_response
    else:
        login_response = login_with_captcha(username, password, session_key, captcha)
        if not login_response:
            return None
        if type(login_response) == str and login_response != "login_success":
            return login_response


    # need fix
    try_get_list_response = g.global_sessions[session_key]['session'].get(search_list_url,
                                                                          headers=headers, timeout=5)
    if try_get_list_response.status_code != 200:
        return "sites_dead"

    list_soup = BeautifulSoup(try_get_list_response.content.decode('utf-8'))
    all_tr = list_soup.find_all('tr')
    term_dict = {}
    for j in range(2, len(all_tr)):
        all_td = all_tr[j].find_all('td')
        if len(all_td) <= 10:
            break
        dict_to_be_inserted = {}
        dict_to_be_inserted.update(lesson_name=all_td[4].string,
                                   grade=all_td[7].a.string,
                                   credit=all_td[8].string,
                                   gpa=all_td[10].string)
        if all_td[1].string in term_dict.keys():
            term_dict[all_td[1].string].append(dict_to_be_inserted)
        else:
            term_dict.update({all_td[1].string: [dict_to_be_inserted]})

    # transform the data format to older version
    to_be_returned_list = []
    for k, v in term_dict.items():
        to_be_returned_list.append({
            'term': k,
            'grade': v
        })

    return to_be_returned_list

