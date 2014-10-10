#coding: utf-8

import time, re, sys
import threading
import sqlite3
import timer
import dbhelper
import dom
import http.client
import socket

# logic

def slog(*args):
    thread_name = threading.current_thread().name
    a = thread_name.split('-')
    if len(a) == 1:
        filename = '{}.log'.format(thread_name)
    else:
        _, i = a
        filename = 'Group-{}.log'.format(int(i) % 7)
    with open(filename, 'a') as f:
        f.write('[{}] [{}] {}\n'.format(time.strftime('%Y-%m-%d %H-%M-%S'), thread_name, ' '.join([str(e) for e in args])))

def get_list_by_attrib(node_list, key, value):
    ret = []
    for e in node_list:
        if e.get(key) == value:
            ret.append(e)
    return ret

def get_avatar_src(content):
    doc = dom.html2dom(content.decode())
    wrap = doc.get_element_by_id('zh-pm-page-wrap')
    # print(dom.c14n(wrap))
    img_list = wrap.iter('img')
    # if img_list is None:
    #     raise Exception('no .zh-pm-page-wrap img')
    img_list = get_list_by_attrib(img_list, 'class', 'zm-profile-header-img zg-avatar-big zm-avatar-editor-preview')
    img = img_list[0]
    return img.get('src')

data = {}
def get_average(n, tag = 'default'):
    if tag not in data:
        data[tag] = {'cnt': 0, 'sum': 0}
    data[tag]['cnt'] += 1
    data[tag]['sum'] += n
    return data[tag]['sum']/data[tag]['cnt']

def get_answer_link_list(content):
    doc = dom.html2dom(content.decode())
    wrap = doc.get_element_by_id('zh-profile-answer-list')
    node_list = wrap.iter('a')
    question_link_list = get_list_by_attrib(node_list, 'class', 'question_link')
    return [e.get('href') for e in question_link_list]

def parse_answer_pure(content):
    with open('last.html', 'w') as f:
        f.write(content.decode())

    doc = dom.html2dom(content.decode())
    answerdom = doc.get_element_by_id('zh-question-answer-wrap')
    if len(answerdom) == 0:
        slog('warinng: no #zh-question-answer-wrap')
        # file_put_contents('last_error.html', content)
        raise Exception("no #zh-question-answer-wrap")
    for div in answerdom.iter('div'):
        classes = div.get('class')
        if classes is not None:
            classes = classes.split(' ')
            if 'zm-editable-content' in classes:
                answer = ''.join([dom.c14n(e) for e in div])
    span = get_list_by_attrib(answerdom.iter('span'), 'class', 'count')[0]
    vote = int(span.text)
    
    q = doc.get_element_by_id('zh-question-title')
    try:
        a = q[0][0]
    except Exception as e:
        print(dom.c14n(q))
        raise e
    question = a.text
    
    descript = doc.get_element_by_id('zh-question-detail')
    descript = ''.join([dom.c14n(e) for e in descript[0]])
    
    return (question, descript, answer, vote)

def get_conn():
    return http.client.HTTPConnection('www.zhihu.com', timeout=7)

def get_url(url):
    conn = get_conn()
    conn.request("GET", url)
    while True:
        try:
            response = conn.getresponse()
        except http.client.ResponseNotReady as e:
            print('http.client.ResponseNotReady')
            continue
        except http.client.CannotSendRequest as e:
            print('http.client.CannotSendRequest')
            return None
        except socket.timeout as e:
            print('wtf! timeout')
            return None
        break
    code = response.status
    print('.',end='')
    slog("\t[{}]".format(code))
    if code != 200: # fail fast
        slog("\tfail\n")
        slog("url [code] error")
        success_ratio = get_average(0, 'success_ratio')
        return None
    else:
        success_ratio = get_average(1, 'success_ratio')
    content = response.read()
    return content

def saveAnswer(conn, username, answer_link_list, dblock):
    regex = re.compile(r'^/question/(\d+)/answer/(\d+)')

    success_ratio = None
    avg = None
    for url in answer_link_list:
        matches = regex.search(url)
        if matches is None:
            raise Exception('url not good')
        qid = matches.group(1)
        aid = matches.group(2)
        slog("\t{}".format(url))
        sys.stdout.flush()
        timer.timer('saveAnswer')
        content = get_url(url)
        if content is None:
            continue
        success_ratio = get_average(0 if content is None else 1, 'success_ratio')
        t = timer.timer('saveAnswer')
        avg = int(get_average(t))
        slog("\t{} ms".format(t))
        if len(content) == 0:
            slog("content is empty\n")
            slog("url [code] empty")
            return False
        question, descript, content, vote = parse_answer_pure(content)
        slog("{}\t^{}\t{}".format(url, vote, question))

        with dblock:
            dbhelper.saveQuestion(qid, question, descript)
            dbhelper._saveAnswer(aid, qid, username, content, vote)
    if success_ratio is not None and avg is not None:
        success_ratio = int(success_ratio*100)
        print("\tAvg: {} ms\tsuccess_ratio: {}%".format(avg, success_ratio))



def get_page_num(content):
    matches = re.findall(r'<a href="\?page=(\d+)', content.decode())
    if matches is None or len(matches) == 0:
        return 1
    # print(matches)
    return max([int(i) for i in matches])

def get_username_list(content):
    with open('last_question.html', 'w') as f:
        f.write(content.decode())

    doc = dom.html2dom(content.decode())
    ret = {}
    regex = re.compile('/people/(.+)')
    for node in doc.root.iter('a'):
        href = node.get('href')
        if href is not None:
            matches = regex.search(href)
            if matches is not None:
                username = matches.group(1)
                ret[username] = node.text
    return ret

def fetch_people_page(conn, username, page = 1):
    url = "/people/{}/answers".format(username)
    url_page = "{}?page={:d}".format(url, page)
    print("\n{}\t".format(url_page), end='')
    sys.stdout.flush()
    timer.timer()
    try:
        conn.request("GET", url_page)
    except socket.timeout as e:
        print('wow! timeout')
        raise e
    response = conn.getresponse()
    t = timer.timer()
    avg = int(get_average(t, 'user page'))
    code = response.status
    print("[{}]\t{} ms\tAvg: {} ms".format(code, t, avg))
    if code == 404:
        slog("user username fetch fail, code code")
        dbhelper.update_user_by_name(username, {'fetch': FETCH_FAIL})
        print( "没有这个用户", username)
        return None
    if code != 200:
        slog("user username fetch fail, code code")
        dbhelper.update_user_by_name(username, {'fetch': FETCH_FAIL})
        print( "奇奇怪怪的返回码", code)
        return None
    content = response.read()
    return content
