#coding: utf-8

import sys, threading
import http.client
import zhihu
import dbhelper
import timer

MAX_THREAD_NUM = 4

dblock = threading.Lock()
count = dbhelper.getNotFetchedUserCount()
print("there are", count, "user to fetch")
s = threading.Semaphore(MAX_THREAD_NUM)
finish = threading.Event()
finish.clear()

def fetch_proc(username):
    with dblock:
        dbhelper.update_user_by_name(username, {'fetch': dbhelper.FETCH_ING})
    conn = zhihu.get_conn()
    content = zhihu.fetch_people_page(conn, username)
    if content is None:
        conn.close()
        return
    
    src = zhihu.get_avatar_src(content)
    with dblock:
        dbhelper.update_user_by_name(username, {'avatar': src})

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
        dbhelper.update_user_by_name(username, {'fetch': dbhelper.FETCH_OK})
    conn.close()
    zhihu.slog('### after saveAnswer ###')
    s.release()

if len(sys.argv) > 1:
    username = sys.argv[1]
    dbhelper.insert_user({'name': username, 'fetch': dbhelper.FETCH_ING})
    fetch_proc(username)
else:
    threads = []
    while True:
        i = threading.active_count()
        print('active_count', i)
        with dblock:
            username = dbhelper.getNotFetchedUserName()
        if username is None:
            print('finish')
            break
        s.acquire()
        t = threading.Thread(target=fetch_proc, args=(username,))
        threads.append(t)
        t.start()
        zhihu.slog('start', t.name)
        for t in threads:
            t.join(0.1)
            if not t.is_alive():
                zhihu.slog(t.name, 'die')
        threads = [t for t in threads if t.is_alive()]
    print('Complete')
