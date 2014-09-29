#coding: utf-8

import http.client
import zhihu

conn = http.client.HTTPConnection('www.zhihu.com')

# print("there are ",count(ids)," questions to fetch\n")

count = 0
insert_count = 0
while True:
    qid = zhihu.next_question_id()
    if qid is None:
        break
    zhihu.set_question_fetch(qid, zhihu.FETCH_ING)
    url = "/question/{}".format(qid)
    conn.request("GET", url)
    response = conn.getresponse()
    if response is None:
        print('can not open', url)
    code = response.status
    print("{} [{}]".format(url, code))
    content = response.read()
    username_list = zhihu.get_username_list(content)

    for username, nickname in username_list.items():
        print("\t{:28s}{:8s}".format(username, nickname), end='')
        rs = zhihu.saveUser(username, nickname)
        if rs is not None:
            insert_count += 1
            print('\t+')
        else:
            print()
        count += 1
    print("\tRate {}%\n".format(int(insert_count/count * 100)))
    zhihu.set_question_fetch(qid, zhihu.FETCH_OK)

conn.close()
