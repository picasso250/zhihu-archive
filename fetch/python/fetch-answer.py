#coding: utf-8

import zhihu

base_url = 'http://www.zhihu.com'

count = zhihu.getNotFetchedUserCount()
print( "there are count user to fetch\n")
n = 0
while True:
    if len(sys.argc) > 1:
        username = sys.argv[1]
    else:
        username = zhihu.getNotFetchedUserName(n)
    if username is None:
        print('Complete!')
        break
    zhihu.update_user_by_name(username, {'fetch': zhihu.FETCH_ING})
    n += 1
    url = "{}/people/username/answers".format(base_url)
    print( "\nfetch No.n username\t")
    zhihu.timer()
    code, content = zhihu.uget(url)
    t = zhihu.timer()
    avg = int(zhihu.get_average(t, 'user page'))
    print( "[code]\tt ms\tAvg: avg ms\n")
    if code == 404:
        slog("user username fetch fail, code code")
        zhihu.update_user_by_name(username, {'fetch': zhihu.FETCH_FAIL})
        print( "没有这个用户 username\n")
        continue
    if code != 200:
        slog("user username fetch fail, code code")
        zhihu.update_user_by_name(username, {'fetch': zhihu.FETCH_FAIL})
        print( "奇奇怪怪的返回码 code\n")
        continue
    
    src = zhihu.get_avatar_src(content)
    
    zhihu.update_user_by_name(username, {'avatar': src})

    link_list = get_answer_link_list(content)
    rs = zhihu.saveAnswer(base_url, username, link_list)

    num = zhihu.get_page_num(content)
    if num > 1:
        for i in range(2, num):
            print( "\nNo. n fetch page i\t")
            url_page = "{}?page={:d}".format(url, i)
            zhihu.timer()
            code, content = zhihu.uget(url_page)
            t = zhihu.timer()
            avg = int(zhihu.get_average(t, 'user page'))
            slog("url_page [code]")
            print( "[code]\tt ms\tAvg: avg ms\n")
            if code != 200:
                print( "奇奇怪怪的返回码 code\n")
                continue
            
            link_list = get_answer_link_list(content)
            zhihu.saveAnswer(base_url, username, link_list)
        
    
    zhihu.update_user_by_name(username, {'fetch': zhihu.FETCH_OK})

