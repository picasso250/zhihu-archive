#coding: utf-8

from html.parser import HTMLParser

class DomElement(object):
    """docstring for DomElement"""
    def __init__(self, tag):
        super(DomElement, self).__init__()
        self.tag = tag
        self.attrs = None
        self.children = []
        self.value = None
    def __str__(self):
        return '<{}>'.format(self.tag)

class DomParser(HTMLParser):
    def init(self):
        self.dom = []
        self.cur_elem = None
        self.parents = [] # the parents of current element

    def build_elem(self, tag, attrs):
        elem = DomElement(tag)
        elem.attrs = attrs
        return elem

    def handle_starttag(self, tag, attrs):
        print("Start tag :", tag)
        if self.cur_elem is not None and self.cur_elem.tag not in ['br', 'hr', 'img', 'meta']:
            # cur_elem have parent
            # we are going deeper
            self.parents.append(self.cur_elem)
        self.cur_elem = self.build_elem(tag, attrs)
        if len(self.parents) > 0 and len(self.parents[-1].children) > 0:
            # cur_elem have siblings
            pass
            # we begin or we run through next sibling
            pass

    def handle_endtag(self, tag):
        # untill here, we have had build the current element
        # so let's see where should we put the element
        print("End tag :", tag)
        if len(self.parents) == 0:
            # current element do not have any parents,
            # so it should be apppended to root
            self.dom.append(self.cur_elem)
        else:
            print('parents', end='')
            for p in self.parents:
                print('---', p, end='')
            print()
            if self.cur_elem.tag == tag:
                # cur_elem has parents
                self.parents[-1].children.append(self.cur_elem)
                self.cur_elem = None
            elif self.parents[-1].tag == tag:
                # we will close a parent
                parent = self.parents.pop()
                self.parents[-1].children.append(parent)
                self.cur_elem = None
            else:
                raise Exception('what the fuck')

    def handle_data(self, data):
        # print(data)
        if self.cur_elem is not None:
            self.cur_elem.value = data

def html2dom(content):
    parser = DomParser()
    parser.init()
    parser.feed(content)
    return parser.dom

with open('last.html') as f:
    dom = html2dom(f.read())
    print(dom)
