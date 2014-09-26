#coding: utf-8

import html
from html.parser import HTMLParser
from xml.etree.ElementTree import TreeBuilder

def is_alone(tag):
    return tag in ['br', 'hr', 'img', 'meta', 'link']
def c14n(self):
    if len(list(self)) > 0:
        inner = ''.join([c14n(e)+'' for e in list(self)])
    else:
        inner = self.text
    if self.tag == 'text':
        if len(self.text.strip()) == 0:
            return ''
        return self.text
    attrs = ''.join([' '+k if v is None else ' {}="{}"'.format(k, html.escape(v)) for k, v in self.attrib.items()])
    if inner is None:
        return '<{0}{1}></{0}>\n'.format(self.tag, attrs)
    if len(inner) > 0 and inner[0] == '<':
        inner = '\n'+inner
    return '<{0}{1}>{2}</{0}>\n'.format(self.tag, attrs, inner)

def walk(self, callback):
    if not callback(self):
        return False
    if len(list(self)) > 0:
        for child in list(self):
            if not walk(child, callback):
                return False
    return True

def get_element_by_id(self, identity):
    node = None
    def search_by_id(e):
        nonlocal node
        if e.attrib is None:
            return True
        attrs = dict(e.attrib)
        if 'id' in attrs and attrs['id'] == identity:
            node = e
            return False
        return True
    walk(self, search_by_id)
    return node

class HtmlDoc(object):
    """docstring for HtmlDoc"""
    def __init__(self, root, decl = None):
        super(HtmlDoc, self).__init__()
        self.root = root
        self.decl = decl

    def c14n(self):
        inner = c14n(self.root)
        if self.decl is None:
            return inner
        return '<!{}>\n{}'.format(self.decl, inner)

    def get_element_by_id(self, identity):
        return get_element_by_id(self.root, identity)

    def walk(self, callback):
        walk(self.root, callback)

# when any method called or after, `self.parents` should be the chain of parents of `self.root`
class DomParser(HTMLParser):
    def init(self):
        self.STATE_OPEN = 1
        self.STATE_CLOSE = 2
        self.STATE_TEXT = 3

        self.tag = None
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
        if self.state is self.STATE_OPEN and is_alone(self.tag):
            self.tb.end(self.tag)
        self.tb.start(tag, dict(attrs))
        self.tag = tag
        self.state = self.STATE_OPEN

    def handle_decl(self, decl):
        self.decl = decl

    def handle_startendtag(self, tag, attrs):
        self.tb.start(tag, dict(attrs))
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
        # print('End </{}>'.format(tag))
        self.tb.end(tag)
        self.state = self.STATE_CLOSE

    # pre-condition
    #  1. we are encounting the text node, whose value is `data`
    #  2. `self.root` is the parent or the sibling of the text node
    #  5. `self.state` can be any state include `None`
    # post-condition
    #  1. `self.root` is the parent of leaving text node, and it contains the text node now
    #  3. `self.state` remains
    def handle_data(self, data):
        # print('data', repr(data))
        if self.state is self.STATE_OPEN and is_alone(self.tag):
            self.tb.end(self.tag)
            self.state = self.STATE_CLOSE
        if self.state is not None and len(data.strip()) > 0:
            self.tb.start('text', [('text', data)])
            self.tb.data(data)
            self.tb.end('text')

def html2dom(content):
    parser = DomParser()
    parser.init()
    parser.feed(content)
    e = parser.tb.close()
    doc = HtmlDoc(e, parser.decl)
    return doc

# test
if __name__ == '__main__':
    with open('last.html') as f:
        doc = html2dom(f.read())
        # print(doc.c14n())
        print(c14n(doc.get_element_by_id('ajax-error-message')))
