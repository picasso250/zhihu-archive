#coding: utf-8

import time
import db
import timer

# logic

FETCH_ING = 1
FETCH_OK = 2
FETCH_FAIL = 3

from html.parser import HTMLParser

class ZhihuParser(HTMLParser):
    def init(self):
        self.in_zh_pm_page_wrap = False
        self.in_zh_profile_answer_list = False
        self.in_zh_question_answer_wrap = False
        self.in_zh_question_title = False
        self.in_zh_question_detail = False
        self.in_count = False
        self.in_title = False
        self.in_detail = False
        self.detail = ''
        self.content = ''
        self.question_link_list = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # print(attrs)
        if 'id' in attrs and attrs['id'] == 'zh-pm-page-wrap':
            # print('find #zh-pm-page-wrap')
            self.in_zh_pm_page_wrap = True
        if self.in_zh_pm_page_wrap and tag == 'img':
            # print("Encountered a start tag:", tag, attrs)
            if 'class' in attrs and attrs['class'] == 'zm-profile-header-img zg-avatar-big zm-avatar-editor-preview':
                # print('find img.')
                self.avatar = attrs['src']
                return False

        if 'id' in attrs and attrs['id'] == 'zh-profile-answer-list':
            self.in_zh_profile_answer_list = True
        if self.in_zh_profile_answer_list and tag == 'a':
            # print("Encountered a start tag:", tag, attrs)
            if 'class' in attrs and attrs['class'] == 'question_link':
                self.question_link_list.append(attrs['href'])
                return False

        if 'id' in attrs and attrs['id'] == 'zh-question-answer-wrap':
            self.in_zh_question_answer_wrap = True
        if self.in_zh_profile_answer_list and tag == 'div':
            # print("Encountered a start tag:", tag, attrs)
            if 'class' in attrs and attrs['class'] == 'question_link':
                class_list = attrs['class'].split(' ')
                if 'zm-editable-content' in class_list:
                    print('we find div.zm-editable-content')
                    self.in_content = True
                    self.stack = []
                return False
        if self.in_zh_profile_answer_list and tag == 'span':
            # print("Encountered a start tag:", tag, attrs)
            if 'class' in attrs and attrs['class'] == 'count':
                self.in_count = True

        if 'id' in attrs and attrs['id'] == 'zh-question-title':
            self.in_zh_question_title = True
        if self.in_zh_profile_answer_list and tag == 'a':
            self.in_title = True

        if 'id' in attrs and attrs['id'] == 'zh-question-detail':
            self.in_zh_question_detail = True
        if self.in_zh_profile_answer_list and tag == 'div':
            self.in_detail = True
            self.stack = []

        if self.in_detail or self.in_content:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        pop_tag = self.stack.pop()
        if pop_tag != tag:
            raise Exception('pop '+pop_tag+', but end '+tag)
    def handle_data(self, data):
        if self.in_count:
            self.count = data
            return False
        if self.in_title:
            self.title = data
            return False
        if self.in_detail:
            self.detail += data
        if self.in_content:
            self.content += data


def slog(msg):
    pass

def get_avatar_src(content):
    parser = ZhihuParser()
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

def saveUser(username, nickname):
    u = get_table('user')
    update = {'name': username, 'nick_name': nickname}
    where = {'name': username}
    rs = u.update(where, {'set': update}, {'upsert': true})
    if (not rs['ok']):
        print(rs['err'])
    return rs

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

def update_table(table, args, where):
    cursor = db.connect().cursor()
    keys = args.keys()
    key_str = ','.join(['`{}`=?'.format(key) for key in keys])
    values = [str(e) for e in list(args.values())]
    where_str = ','.join(['`{}`=?'.format(key) for key in where.keys()])
    where_values = [str(e) for e in list(where.values())]
    values.append(*where_values)
    return cursor.execute('UPDATE `{0}` SET {1} WHERE {2}'.format(table, key_str, where_str), tuple(values))

def update_user_by_name(username, args):
    return update_table('user', args, {'name': username})

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
    parser = ZhihuParser()
    parser.init()
    parser.feed(content.decode())
    return parser.question_link_list

def insert_table(table, args):
    cursor = db.connect().cursor()
    keys = args.keys()
    key_str = ','.join(['`{}`'.format(key) for key in keys])
    value_str = ','.join(['?' for key in keys])
    values = [str(e) for e in list(args.values())]
    return cursor.execute('INSERT INTO `{0}` ({}) VALUES {}'.format(table, key_str, values), tuple(values))

def _saveAnswer(aid, qid, username, content, vote):
    args = {'id': aid, 'q_id': qid, 'user_id': username, 'text': content, 'vote': vote, 'fetch_time': int(time.time())}
    return insert_table('answer', args)

def parse_answer_pure(content):
    parser = ZhihuParser()
    parser.init()
    parser.feed(content.decode())
    return parser.title, parser.detail, parser.content, parser.count

def saveAnswer(base_url, username, answer_link_list):
    regex = re.compile(r'^/question/(\d+)/answer/(\d+)')
    conn = http.client.HTTPConnection('www.zhihu.com')

    success_ratio = None
    avg = None
    for url in answer_link_list:
        matches = regex.search(url)
        if matches is None:
            raise Exception('url not good')
        qid = matches.group(1)
        aid = matches.group(2)
        print("\turl")
        timer.timer('saveAnswer')
        conn.request("GET", url)
        response = conn.getresponse()
        if response is None:
            raise Exception('no response')
        code = response.status
        print("\t[code]")
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
        print("\tt ms\n")
        if len(content) == 0:
            print("content is empty\n")
            slog("url [code] empty")
            return False
        question, descript, content, vote = parse_answer_pure(content)
        slog("url [code] ^vote\tquestion")

        zhihu.saveQuestion(qid, question, descript)

        zhihu._saveAnswer(aid, qid, username, content, vote)
    if success_ratio is not None and avg is not None:
        success_ratio = int(success_ratio*100)
        print("\tAvg: {} ms\tsuccess_ratio: {}%\n".format(avg, success_ratio))
