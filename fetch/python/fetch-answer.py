#coding: utf-8

import sys, threading
import http.client
import zhihu
import timer

MAX_THREAD_NUM = 4

dblock = threading.Lock()
count = zhihu.getNotFetchedUserCount()
print("there are", count, "user to fetch")
s = threading.Semaphore(MAX_THREAD_NUM)
finish = threading.Event()
finish.clear()

def fetch_proc(username, logid):
    with dblock:
        if username is None:
            username = zhihu.getNotFetchedUserName()
        else:
            zhihu.insert_user({'name': username, 'fetch': zhihu.FETCH_ING})
        if username is None:
            finish.set()
            print('Finish')
        zhihu.update_user_by_name(username, {'fetch': zhihu.FETCH_ING})
    conn = http.client.HTTPConnection('www.zhihu.com')
    content = zhihu.fetch_people_page(conn, username)
    if content is None:
        conn.close()
        return
    
    src = zhihu.get_avatar_src(content)
    with dblock:
        zhihu.update_user_by_name(username, {'avatar': src})

    link_list = zhihu.get_answer_link_list(content)
    rs = zhihu.saveAnswer(conn, username, link_list, dblock)

    num = zhihu.get_page_num(content)
    if num > 1:
        for i in range(2, num):
            content = zhihu.fetch_people_page(conn, username, i)
            if content is None:
                continue
            link_list = zhihu.get_answer_link_list(content)
            zhihu.saveAnswer(conn, username, link_list, dblock)
    with dblock:
        zhihu.update_user_by_name(username, {'fetch': zhihu.FETCH_OK})
    conn.close()
    zhihu.slog('### after saveAnswer ###')
    s.release()

if len(sys.argv) > 1:
    username = sys.argv[1]
    t = threading.Thread(target=fetch_proc, args=(username,0))
    t.start()
    t.join(1)
else:
    threads = []
    while not finish.is_set():
        zhihu.slog('while ----------')
        i = threading.active_count()
        print('active_count', i)
        s.acquire()
        t = threading.Thread(target=fetch_proc, args=(None,i))
        threads.append(t)
        t.start()
        zhihu.slog('start', t.name)
        for t in threads:
            t.join(0.1)
            if not t.is_alive():
                zhihu.slog(t.name, 'die')
    print('Complete')
