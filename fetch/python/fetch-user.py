#coding: utf-8

import http.client
import zhihu

conn = http.client.HTTPConnection('www.zhihu.com')

# print("there are ",count(ids)," questions to fetch\n")

while True:
    qid = zhihu.next_question_id()
    if qid is None:
        break
    url = "/question/{}".format(qid)
    conn.request("GET", url)
    response = conn.getresponse()
    if response is None:
        print('can not open', url)
    code = response.status
    print("{} [{}]".format(url, code))
    content = response.read()
    username_list = zhihu.get_username_list(content)

    for username, nickname in username_list:
        print("\t{}".format(username))
        zhihu.saveUser(username, nickname)
    print("\n")
    zhihu.setFetched(qid)

conn.close()
