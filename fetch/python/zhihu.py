#coding: utf-8

import db

# logic

FETCH_ING = 1
FETCH_OK = 2
FETCH_FAIL = 3

from html.parser import HTMLParser

class ZhihuParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # print(attrs)
        if 'id' in attrs and attrs['id'] == 'zh-pm-page-wrap':
            print('find #zh-pm-page-wrap')
            self.in_zh_pm_page_wrap = True
        if self.in_zh_pm_page_wrap and tag == 'img':
            # print("Encountered a start tag:", tag, attrs)
            if 'class' in attrs and attrs['class'] == 'zm-profile-header-img zg-avatar-big zm-avatar-editor-preview':
                print('find img.')
                self.avatar = attrs['src']
                return False
    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        pass
    def handle_data(self, data):
        pass


def slog(msg):
    pass

def get_avatar_src(content):
    parser = ZhihuParser()
    parser.in_zh_pm_page_wrap = False
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
    u = get_table('user')
    where = {
        'has_fetch': {'exists': false},
        'fetching': {'exists': false},
        'name': {'exists': true},
    }
    c = u.find(where).fields({'name': true}).limit(1)
    for v in c:
        return v['name']
    return false

def update_user_by_name(username, args):
    cursor = db.connect().cursor()
    keys = args.keys()
    key_str = ','.join([key+'=?' for key in keys])
    values = [str(e) for e in list(args.values())]
    values.append(username)
    return cursor.execute('UPDATE user set '+key_str+' where name=?', tuple(values))

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
