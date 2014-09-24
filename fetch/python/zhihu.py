#coding: utf-8

# logic

FETCH_ING = 1
FETCH_OK = 2
FETCH_FAIL = 3

def get_avatar_src(content):
    dom = loadHTML(content)
    dom = dom.getElementById('zh-pm-page-wrap')
    for node in dom.getElementsByTagName('img'):
        attr = node.getAttribute('class')
        if attr == 'zm-profile-header-img zg-avatar-big zm-avatar-editor-preview':
            src = (node.getAttribute('src'))

data = {}
def get_average(n, tag = 'default'):
    if tag not in data:
        data[tag] = {'cnt': 0, 'sum': 0}
    data[tag]['cnt'] += 1
    data[tag]['sum'] += n
    return data[tag]['sum']/data[tag]['cnt']

def get_table(t):
    pass
def saveUser(username, nickname):
    u = get_table('user')
    update = {'name': username, 'nick_name': nickname}
    where = {'name': username}
    rs = u.update(where, {'set': update}, {'upsert': true})
    if (not rs['ok']):
        print(rs['err'])
    return rs

def getNotFetchedUserCount():
    u = get_table('user')
    where = {
        'has_fetch': {'exists': False},
        'name': {'exists': True},
    }
    c = u.find(where).count()
    return c

def getNotFetchedUserName(i = 1):
    if i == 0 and isset(argv[1]):
        return argv[1]
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
    if (empty(args)):
        return true
    u = get_table('user')
    newdata = {'set': args}
    rs = u.update({"name": username}, newdata, {'upsert': true})
    if (not rs['ok']):
        print(rs['err'])
    return rs

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
