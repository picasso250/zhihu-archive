#coding: utf-8

import time, re, sys
import threading
import sqlite3
import db
import timer
import dom
import http.client

# logic

FETCH_ING = 1
FETCH_OK = 2
FETCH_FAIL = 3

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

def get_user_id_by_name(username):
    cursor = db.connect().cursor()
    sql = 'SELECT id FROM user WHERE name=? LIMIT 1'
    # print(sql, username)
    cursor.execute(sql, (username,))
    row = cursor.fetchone()
    if row is None:
        return None
    user_id = row[0]
    return user_id

def saveUser(username, nickname):
    user_id = get_user_id_by_name(username)
    update = {'name': username, 'nick_name': nickname}
    if user_id is None:
        return db.insert_table('user', update)
    else:
        return db.update_table('user', update, {'name': username})

def getNotFetchedUserCount():
    cursor = db.connect().cursor()
    cursor.execute('SELECT COUNT(*) FROM user WHERE fetch=0')
    row = cursor.fetchone()
    return row[0]

def getNotFetchedUserName():
    cursor = db.connect().cursor()
    cursor.execute('SELECT `name` FROM `user` WHERE `fetch`=0 LIMIT 1')
    row = cursor.fetchone()
    if row is None:
        return None
    return row[0]

def update_user_by_name(username, args):
    return db.update_table('user', args, {'name': username})

def getUids():
    u = get_table('user')
    where = {
        'has_fetch': {'exists': false},
        'name': {'exists': true},
    }
    c = u.find(where).fields({'name': true})
    ret = []
    for v in c:
        ret.append(v['name'])
    return ret

def get_answer_link_list(content):
    doc = dom.html2dom(content.decode())
    wrap = doc.get_element_by_id('zh-profile-answer-list')
    node_list = wrap.iter('a')
    question_link_list = get_list_by_attrib(node_list, 'class', 'question_link')
    return [e.get('href') for e in question_link_list]

def insert_user(args):
    user_id = db.insert_table('user', args)
    print('user_id', user_id)
    return user_id

def _saveAnswer(aid, qid, username, content, vote):
    user_id = get_user_id_by_name(username)
    if user_id is None:
        raise Exception('no user {}'.format(username))
    args = {
        'id': aid,
        'q_id': qid,
        'user_id': user_id,
        'text': content,
        'vote': vote,
        'fetch_time': int(time.time())
    }
    return db.insert_table('answer', args)

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
    a = q[0][0]
    question = a.text
    
    descript = doc.get_element_by_id('zh-question-detail')
    descript = ''.join([dom.c14n(e) for e in descript[0]])
    
    return (question, descript, answer, vote)

def get_url(url):
    conn = http.client.HTTPConnection('www.zhihu.com')
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
            saveQuestion(qid, question, descript)
            _saveAnswer(aid, qid, username, content, vote)
    if success_ratio is not None and avg is not None:
        success_ratio = int(success_ratio*100)
        print("\tAvg: {} ms\tsuccess_ratio: {}%".format(avg, success_ratio))

def set_question_fetch(qid, fetch):
    sets = {'fetch': fetch}
    where = {'id': qid}
    return db.update_table('question', sets, where)

def get_question_by_id(qid):
    cursor = db.connect().cursor()
    sql = 'SELECT id FROM question WHERE id=? LIMIT 1'
    # print(sql, username)
    cursor.execute(sql, (qid,))
    row = cursor.fetchone()
    if row is None:
        return None
    return row[0]

def saveQuestion(qid, question, description):
    question_id = get_question_by_id(qid)
    args = {
        'id': qid,
        'title': question,
        'description': description,
        'fetch_time': int(time.time()),
        'fetch': 0
    }
    if question_id is None:
        return db.insert_table('question', args)
    else:
        return db.update_table('question', args, {'id': qid})

def next_question_id():
    cursor = db.connect().cursor()
    sql = 'SELECT id FROM `question` WHERE fetch=0 LIMIT 1'
    # print(sql)
    cursor.execute(sql)
    row = cursor.fetchone()
    if row is None:
        return None
    return row[0]

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
    conn.request("GET", url_page)
    response = conn.getresponse()
    t = timer.timer()
    avg = int(get_average(t, 'user page'))
    code = response.status
    print("[{}]\t{} ms\tAvg: {} ms".format(code, t, avg))
    if code == 404:
        slog("user username fetch fail, code code")
        update_user_by_name(username, {'fetch': FETCH_FAIL})
        print( "没有这个用户", username)
        return None
    if code != 200:
        slog("user username fetch fail, code code")
        update_user_by_name(username, {'fetch': FETCH_FAIL})
        print( "奇奇怪怪的返回码", code)
        return None
    content = response.read()
    return content
