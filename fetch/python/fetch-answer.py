#coding: utf-8

import sys
import http.client
import zhihu
import timer

conn = http.client.HTTPConnection('www.zhihu.com')

count = zhihu.getNotFetchedUserCount()
print("there are", count, "user to fetch")
n = 0
while True:
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = zhihu.getNotFetchedUserName()
    if username is None:
        print('Complete!')
        break
    zhihu.update_user_by_name(username, {'fetch': zhihu.FETCH_ING})
    n += 1
    url = "/people/{}/answers".format(username)
    print("\nFetch", n, "username\t")
    timer.timer()
    # print(url)
    conn.request("GET", url)
    response = conn.getresponse()
    t = timer.timer()
    avg = int(zhihu.get_average(t, 'user page'))
    if response is None:
        print('can not open', url)
    code = response.status
    print( "[code]\tt ms\tAvg: avg ms\n")
    if code == 404:
        zhihu.slog("user username fetch fail, code code")
        zhihu.update_user_by_name(username, {'fetch': zhihu.FETCH_FAIL})
        print( "没有这个用户", username)
        continue
    if code != 200:
        zhihu.slog("user username fetch fail, code code")
        zhihu.update_user_by_name(username, {'fetch': zhihu.FETCH_FAIL})
        print( "奇奇怪怪的返回码", code)
        continue
    content = response.read()
    
    src = zhihu.get_avatar_src(content)
    
    zhihu.update_user_by_name(username, {'avatar': src})

    link_list = zhihu.get_answer_link_list(content)
    rs = zhihu.saveAnswer(base_url, username, link_list)

    num = zhihu.get_page_num(content)
    if num > 1:
        for i in range(2, num):
            print( "\nNo. n fetch page i\t")
            url_page = "{}?page={:d}".format(url, i)
            timer.timer()
            conn.request("GET", url_page)
            response = conn.getresponse()
            t = timer.timer()
            avg = int(zhihu.get_average(t, 'user page'))
            code = response.status
            zhihu.slog("url_page [code]")
            print( "[code]\tt ms\tAvg: avg ms\n")
            if code != 200:
                print( "奇奇怪怪的返回码 code\n")
                continue
            content = response.read()
            link_list = get_answer_link_list(content)
            zhihu.saveAnswer(base_url, username, link_list)
    
    zhihu.update_user_by_name(username, {'fetch': zhihu.FETCH_OK})

