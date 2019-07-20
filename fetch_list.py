#!/user/bin/python2.7
# -*- coding: utf-8 -*-
from login import *
import global_sessions as g
import requests


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

    to_be_returned_list.sort(key=lambda s: s['term'])

    # [{'term':'2017-2018-1学期', 'grade':{lesson_name, grade, credit, gpa}}, ...]
    for i, term in enumerate(to_be_returned_list):
        term_all_credits = 0
        term_all_grades = 0
        term_weighting_credits = 0
        term_weighting_grades = 0
        for section in term['grade']:
            if float(section['grade']) >= 60:
                term_all_credits += float(section['credit'])
                term_all_grades += float(section['grade'])
                term_weighting_credits += float(section['credit']) * float(section['gpa'])
                term_weighting_grades += float(section['grade']) * float(section['credit'])
        term_average_gpa = term_weighting_credits / term_all_credits
        term_average_grades = term_weighting_grades / term_all_credits
        to_be_returned_list[i].update({'term_all_credits': round(term_all_credits, 1),
                                       'term_average_gpa': round(term_average_gpa, 2),
                                       'term_average_grades': round(term_average_grades, 2)})

    # calculate the whole average gpa and grade, except the case when two section has the same name.
    # When it comes to that case, we pick the one has higher grade.
    lesson_to_credits_grades_gpa = {}
    for i, term in enumerate(to_be_returned_list):
        for section in term['grade']:
            update = False
            if section['lesson_name'] not in lesson_to_credits_grades_gpa.keys():
                update = True
            else:
                if float(lesson_to_credits_grades_gpa[section['lesson_name']]['grade']) < float(section['grade']):
                    update = True
            if update:
                lesson_to_credits_grades_gpa[section['lesson_name']] = {
                    'grade': round(float(section['grade']), 2),
                    'credit': round(float(section['credit']), 1),
                    'gpa': round(float(section['gpa']), 2)
                }
    all_grades = 0
    all_credits = 0
    all_weighting_grades = 0
    all_weighting_credits = 0
    for item in lesson_to_credits_grades_gpa.values():
        if float(item['grade']) >= 60:
            all_grades += float(item['grade'])
            all_credits += float(item['credit'])
            all_weighting_grades += float(item['credit']) * float(item['grade'])
            all_weighting_credits += float(item['gpa']) * float(item['credit'])
    all_average_grades = all_weighting_grades / all_credits
    all_average_gpa = all_weighting_credits / all_credits
    to_be_returned_dict = {
        'all_info': {
            'all_credits': round(all_credits, 1),
            'all_average_grades': round(all_average_grades, 2),
            'all_average_gpa': round(all_average_gpa, 2)
        },
        'each_term': to_be_returned_list
    }

    return to_be_returned_dict

