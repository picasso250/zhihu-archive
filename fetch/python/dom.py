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
    def c14n(self):
        if self.children:
            inner = '\n'.join([e.c14n() for e in self.children])
        else:
            inner = self.value
        if self.tag == 'root':
            return inner
        elif self.tag == 'text':
            return self.value
        else:
            attrs = ''.join([' {}="{}"'.format(k, v) for k, v in self.attrs])
            return '<{0}{1}>\n{2}\n</{0}>'.format(self.tag, attrs, inner)

class DomParser(HTMLParser):
    def init(self):
        self.root = self.build_elem('root') # current element, when parse finish, it become root
        self.parents = [] # the parents of current element

    def build_elem(self, tag, attrs = None):
        elem = DomElement(tag)
        elem.attrs = attrs
        return elem

    def is_alone(self, tag):
        return tag in ['br', 'hr', 'img', 'meta', 'link']

    def handle_starttag(self, tag, attrs):
        print("Start tag :", tag)
        if self.root is not None and not self.is_alone(self.root.tag):
            # root have parent
            # we are going deeper
            self.parents.append(self.root)
        self.root = self.build_elem(tag, attrs)

    def handle_endtag(self, tag):
        # untill here, we have had build the current element
        # so let's see where should we put the element
        print("End tag :", tag)
        if len(self.parents) == 0:
            raise Exception('no parents')

        print('\tparents', end='')
        for p in self.parents:
            print(',',p, end='')
        print()
        print('\tcur_elem', self.root)

        if self.root is None:
            raise Exception('root is None')
        if self.root.tag == tag:
            # close root
            parent = self.parents.pop()
            parent.children.append(self.root)
            self.root = parent
        else:
            raise Exception('what the fuck')

    def handle_data(self, data):
        # print(data)
        if self.root is not None:
            self.root.value = data
        else:
            data = data.strip()
            if len(data) > 0:
                if self.root is not None and not self.is_alone(self.root.tag):
                    # root have parent
                    # we are going deeper
                    self.parents.append(self.root)
                self.root = self.build_elem('text')

def html2dom(content):
    parser = DomParser()
    parser.init()
    parser.feed(content)
    return parser.root

with open('last.html') as f:
    dom = html2dom(f.read())
    print(dom.c14n())
