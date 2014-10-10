#coding: utf-8

import time
import db
import timer

# logic

FETCH_ING = 1
FETCH_OK = 2
FETCH_FAIL = 3

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
