#coding: utf-8

import html
from html.parser import HTMLParser
from xml.etree.ElementTree import TreeBuilder

def is_alone(tag):
    return tag in ['br', 'hr', 'img', 'meta', 'link']
def c14n(self):
    if self.hasChildNodes():
        inner = ''.join([c14n(e)+'' for e in self.childNodes])
    else:
        inner = self.value
    if self.tagName == 'root':
        if self.decl is None:
            return inner
        return '<!{}>\n{}'.format(self.decl, inner)
    elif self.tagName == 'text':
        if len(self.value.strip()) == 0:
            return ''
        return self.value
    else:
        if self.hasAttributes():
            attrs = self.attributes
            print(attrs)
        else:
            attrs = []
        attrs = ''.join([' {}="{}"'.format(k, html.escape(v)) for k, v in self.attrs])
        if self.is_alone:
            return '<{0}{1} />\n'.format(self.tagName, attrs)
        if inner is None:
            return '<{0}{1}></{0}>\n'.format(self.tagName, attrs)
        if len(inner) > 0 and inner[0] == '<':
            inner = '\n'+inner
        return '<{0}{1}>{2}</{0}>\n'.format(self.tagName, attrs, inner)

def get_element_by_id(self, identity):
    node = None
    def search_by_id(e):
        nonlocal node
        if e.attrs is None:
            return True
        attrs = dict(e.attrs)
        if 'id' in attrs and attrs['id'] == identity:
            node = e
            # print(node)
            return False
        return True
    self.walk(search_by_id)
    return node

def walk(self, callback):
    if not callback(self):
        return False
    if len(self.children) > 0:
        for c in self.children:
            if not c.walk(callback):
                return False
    return True

# when any method called or after, `self.parents` should be the chain of parents of `self.root`
class DomParser(HTMLParser):
    def init(self):
        self.STATE_OPEN = 1
        self.STATE_CLOSE = 2
        self.STATE_TEXT = 3

        self.parents = [] # the parents of current element
        self.state = None
        self.i = 0
        self.tb = TreeBuilder()

    def build_node(self, tag, attrs = None):
        elem = DomNode(tag)
        elem.attrs = attrs
        return elem

    # pre-condition:
    #  1. we are encounting a node, whose tag is `tag`, attributes is `attr`, we call it _next node_
    #  2. `self.root` is the parent of next node(`parent condition`), or sibling(`sibling condition`, meta, img or link, etc.)
    #  3. if previous node is closed correctly, `self.root` should be parent of next node
    #  4. sibling-condition
    #   1. if `self.state` is `self.STATE_OPEN` and `self.root` type is alone (we encount a unclosed tag last time)
    #  5. parent-condition, when not in sibling condition and
    #   1. `self.state` is `self.STATE_OPEN` or `self.STATE_CLOSE` (most _normal_ condition)
    #   2. `self.state` is `None` (when we encouter first `<html>`)
    #  6. `self.root`'s type will not be _text_
    #  7. `self.state` can be any state include `None`
    # post-condition
    #  1. after we encounting a node, we call that node _current node_
    #  2. `self.root` is current node
    #  3. if `self.root` is sbling, it has been put into it's parent
    #  4. `self.state` is `self.STATE_OPEN`
    def handle_starttag(self, tag, attrs):
        self.tb.start(tag, attrs)

    def handle_decl(self, decl):
        self.decl = decl

    def handle_startendtag(self, tag, attrs):
        self.tb.start(tag, attrs)
        self.tb.end(tag)

    # pre-condition
    #  1. we are leaving the current node
    #  2. `self.root` is the current node(who has been build), or the last child of the current node
    #  3. if `self.root` is the last child of the current node, that child should be alone, and should be not put into current node yet
    #  4. `self.state` can be any state but not `None`
    # post-condition
    #  1. `self.root` is the parent of leaving node
    #  3. `self.state` is `self.STATE_CLOSE`
    def handle_endtag(self, tag):
        self.tb.end(tag)

    # pre-condition
    #  1. we are encounting the text node, whose value is `data`
    #  2. `self.root` is the parent or the sibling of the text node
    #  5. `self.state` can be any state include `None`
    # post-condition
    #  1. `self.root` is the parent of leaving text node, and it contains the text node now
    #  3. `self.state` remains
    def handle_data(self, data):
        # print('data', repr(data))
        self.tb.data(data)

    def print_path(self):
        print('\t==>', end='')
        for p in self.parents:
            print(',',p, end='')
        print('\t|', self.root)

def html2dom(content):
    parser = DomParser()
    parser.init()
    parser.feed(content)
    e = parser.tb.close()
    return e

with open('last.html') as f:
    e = html2dom(f.read())
    print(c14n(e))
    # print(dom.get_element_by_id('js-reg-with-mail-in-top').c14n())
