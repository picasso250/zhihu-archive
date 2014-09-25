#coding: utf-8

import re
from html.parser import HTMLParser

class AnswersParser(HTMLParser):
    def init(self):
        self.in_zh_pm_page_wrap = False
        self.in_zh_profile_answer_list = False
        self.question_link_list = []

    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag, attrs)
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

class QuestionParser(HTMLParser):
    def init(self):
        self.regex = re.compile('/people/(.+)$')
        self.link = None
        self.users = {}

    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag, attrs)
        attrs = dict(attrs)
        if tag == 'a' and 'href' in attrs:
            matches = self.regex.search(attrs['href'])
            if matches is not None:
                self.link = matches.group(1)
            else:
                pass # do nothing

    def handle_data(self, data):
        if self.link is not None:
            self.users[self.link] = data
            self.link = None
            return False

class ZhihuParser(HTMLParser):
    def init(self):
        self.in_zh_question_answer_wrap = False
        self.in_zh_question_title = False
        self.in_zh_question_detail = False
        self.in_count = False
        self.in_title = False
        self.in_detail = False
        self.in_content = False
        self.title = ''
        self.detail = ''
        self.content = ''
        self.stack = []

    def handle_starttag(self, tag, attrs):
        # print("Start tag:", tag, attrs)
        attrs = dict(attrs)

        if self.in_zh_question_answer_wrap and not self.in_content and tag == 'div':
            if 'class' in attrs and attrs['class'] == 'question_link':
                class_list = attrs['class'].split(' ')
                if 'zm-editable-content' in class_list:
                    print('we find div.zm-editable-content')
                    self.in_content = True
                    self.stack = []
                return False
        if 'id' in attrs and attrs['id'] == 'zh-question-answer-wrap':
            self.in_zh_question_answer_wrap = True
        if self.in_zh_question_answer_wrap and tag == 'span':
            # print("Encountered a start tag:", tag, attrs)
            if 'class' in attrs and attrs['class'] == 'count':
                self.in_count = True

        if self.in_zh_question_title and tag == 'a':
            # print('#zh-question-title a')
            self.in_title = True
        if 'id' in attrs and attrs['id'] == 'zh-question-title':
            self.in_zh_question_title = True
            # print('in_zh_question_title')

        if self.in_zh_question_detail and not self.in_detail and tag == 'div':
            # print('#zh-question-detail div')
            self.in_detail = True
            self.stack = []
        if 'id' in attrs and attrs['id'] == 'zh-question-detail':
            self.in_zh_question_detail = True
            # print('#zh-question-detail')

        if self.in_detail or self.in_content:
            self.stack.append(tag)
            # print('stack',self.stack)

    def handle_endtag(self, tag):
        # print("End tag :", tag)
        if self.in_detail or self.in_content:
            if len(self.stack) == 0:
                self.in_detail = False
                self.in_content = False
            else:
                while True:
                    pop_tag = self.stack.pop()
                    if pop_tag != tag:
                        if pop_tag in ['br', 'hr', 'img']:
                            continue
                        else:
                            print(self.stack)
                            raise Exception('pop '+pop_tag+', but end '+tag)
                    break
    def handle_data(self, data):
        if self.in_count:
            print('count', data)
            data = data.strip()
            if len(data) > 0:
                self.count = int(data)
                self.in_count = False
        if self.in_title:
            self.title += data
            self.in_title = False
        if self.in_detail:
            self.detail += data
        if self.in_content:
            self.content += data

