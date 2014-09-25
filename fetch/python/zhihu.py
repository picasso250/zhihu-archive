#coding: utf-8

import time, re, sys
import sqlite3
import db
import timer
import parse

# logic

FETCH_ING = 1
FETCH_OK = 2
FETCH_FAIL = 3

def slog(msg):
    pass

def get_avatar_src(content):
    parser = parse.AnswersParser()
    parser.init()
    parser.feed(content.decode())
    return parser.avatar

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
    parser = parse.AnswersParser()
    parser.init()
    parser.feed(content.decode())
    return parser.question_link_list

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
    parser = parse.ZhihuParser()
    parser.init()
    parser.feed(content.decode())
    print(parser.title, parser.detail, parser.content, parser.count)
    return parser.title, parser.detail, parser.content, parser.count

def saveAnswer(conn, username, answer_link_list):
    regex = re.compile(r'^/question/(\d+)/answer/(\d+)')

    success_ratio = None
    avg = None
    for url in answer_link_list:
        matches = regex.search(url)
        if matches is None:
            raise Exception('url not good')
        qid = matches.group(1)
        aid = matches.group(2)
        print("\t{}".format(url), end='')
        sys.stdout.flush()
        timer.timer('saveAnswer')
        conn.request("GET", url)
        response = conn.getresponse()
        if response is None:
            raise Exception('no response')
        code = response.status
        print("\t[{}]".format(code), end='')
        if code != 200: # fail fast
            print("\tfail\n")
            slog("url [code] error")
            success_ratio = get_average(0, 'success_ratio')
            continue
        else:
            success_ratio = get_average(1, 'success_ratio')
        content = response.read()
        t = timer.timer('saveAnswer')
        avg = int(get_average(t))
        print("\t{} ms".format(t))
        if len(content) == 0:
            print("content is empty\n")
            slog("url [code] empty")
            return False
        question, descript, content, vote = parse_answer_pure(content)
        slog("url [code] ^vote\tquestion")

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
    parser = parse.QuestionParser()
    parser.init()
    parser.feed(content.decode())
    return parser.users
