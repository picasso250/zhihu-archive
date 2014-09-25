#coding: utf-8

from html.parser import HTMLParser

class DomNode(object):
    """docstring for DomNode"""
    def __init__(self, tag):
        super(DomNode, self).__init__()
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

# when any method called or after, `self.parents` should be the chain of parents of `self.root`
class DomParser(HTMLParser):
    def init(self):
        self.STATE_OPEN = 1
        self.STATE_CLOSE = 2
        self.STATE_TEXT = 3

        self.root = self.build_node('root') # current element, when parse finish, it become root
        self.parents = [] # the parents of current element
        self.state = None
        self.i = 0

    def build_node(self, tag, attrs = None):
        elem = DomNode(tag)
        elem.attrs = attrs
        return elem

    def is_alone(self, tag):
        return tag in ['br', 'hr', 'img', 'meta', 'link']

    # pre-condition:
    #  1. we are encounting a node, whose tag is `tag`, attributes is `attr`, we call it _next node_
    #  2. `self.root` is the parent of next node(`parent condition`), or sibling(`sibling condition`, meta, img or link, etc.)
    #  4. sibling-condition
    #   3. if `self.state` is `self.STATE_OPEN` and `self.root` type is alone (we encount a unclosed tag last time)
    #  3. parent-condition, when not in sibling condition and
    #   1. `self.state` is `self.STATE_OPEN` or `self.STATE_CLOSE` (the most _normal_ condition)
    #   2. `self.state` is `None` (when we encouter first `<html>`)
    #  3. `self.root`'s type will not be _text_
    #  5. `self.state` can be any state include `None`
    # post-condition
    #  1. after we encounting a node, we call that node _current node_
    #  1. `self.root` is current node
    #  3. if `self.root` is sbling, it has go into it's parent
    #  3. `self.state` is `self.STATE_OPEN`
    def handle_starttag(self, tag, attrs):
        self.i += 1
        print("{}. Start <{}> ".format(self.i, tag), end='')
        self.print_path()
        if self.root is None:
            raise Exception('no elem? impossible')
        if self.root.tag == 'text':
            raise Exception('text will not be the parent of current tag')
        if self.state == self.STATE_OPEN and self.is_alone(self.root.tag):
            # it must be sibling of current tag
            parent = self.parents.pop()
            parent.children.append(self.root) # brother go into parents, and we colse self.root
            self.parents.append(parent)
            self.root = self.build_node(tag, attrs)
        elif self.state == self.STATE_OPEN or self.state == self.STATE_CLOSE or self.state is None:
            # tag node have parent
            # we are going deeper
            self.parents.append(self.root)
            self.root = self.build_node(tag, attrs)
        else:
            raise Exception('{} is not sibling or parent of {}'.format(self.root.tag, tag))

        self.state = self.STATE_OPEN
        self.print_path()

    # pre-condition
    #  1. we are leaving the current node
    #  2. `self.root` is the current node(who has been build), or the last child of the current node
    #  3. if `self.root` is the last child of the current node, that child should be alone, and should be not put into current node yet
    #  4. `self.state` can be any state but not `None`
    # post-condition
    #  1. `self.root` is the parent of leaving node
    #  3. `self.state` is `self.STATE_CLOSE`
    def handle_endtag(self, tag):
        print("End <{}>".format(tag))
        if self.state is None:
            raise Exception('state is None')
        if len(self.parents) == 0:
            # root will never close
            raise Exception('no parents')


        if self.root is None:
            raise Exception('root is None')
        if self.root.tag != tag:
            if self.state == self.STATE_OPEN and self.is_alone(self.root.tag):
                current = self.parents.pop()
                current.children.append(self.root)
                parent = self.parents.pop()
                parent.children.append(current)
                self.root = parent
                return
            else:
                raise Exception('not equal tag, we are leaving <{}>, but current is <{}>'.format(tag, self.root.tag))
        # close root
        parent = self.parents.pop()
        parent.children.append(self.root)
        self.root = parent

        self.state = self.STATE_CLOSE
        self.print_path()

    # pre-condition
    #  1. we are encounting the text node, whose value is `data`
    #  2. `self.root` is the parent or the sibling of the text node
    #  5. `self.state` can be any state include `None`
    # post-condition
    #  1. `self.root` is the parent of leaving text node, and it contains the text node now
    #  3. `self.state` remains
    def handle_data(self, data):
        print('data', repr(data))
        if self.root is None:
            raise Exception('root can not be None')
        text_node = self.build_text_node(data)
        if self.state == self.STATE_OPEN and self.is_alone(self.root.tag):
            self.parents[-1].children.append(self.root) # brother go into parents
            self.parents[-1].children.append(text_node)
        self.root.children.append(text_node)
        self.print_path()

    def print_path(self):
        print('\t==>', end='')
        for p in self.parents:
            print(',',p, end='')
        print('\t|', self.root)

    def build_text_node(self, value):
        text_node = self.build_node('text')
        text_node.value = value
        return text_node

def html2dom(content):
    parser = DomParser()
    parser.init()
    parser.feed(content)
    return parser.root

with open('last.html') as f:
    dom = html2dom(f.read())
    # print(dom.c14n())
