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
        self.root = self.build_node('root') # current element, when parse finish, it become root
        self.parents = [] # the parents of current element
        self.STATE_OPEN = 1
        self.STATE_CLOSE = 2
        self.STATE_TEXT = 3

    def build_node(self, tag, attrs = None):
        elem = DomNode(tag)
        elem.attrs = attrs
        return elem

    def is_alone(self, tag):
        return tag in ['br', 'hr', 'img', 'meta', 'link']

    # pre-condition:
    #  1. we are encounting a node, whose tag is `tag`, attributes is `attr`, we call it _next node_
    #  2. `self.root` is the parent of next node, or sibling(meta, img or link, etc.)
    #  3. if `self.root` is sibling of next node, `self.state` is `self.STATE_OPEN` and `self.root` type is alone
    #  3. `self.root`'s type will not be _text_
    #  5. `self.state` can be any state include None
    # post-condition
    #  1. after we encounting a node, we call that node _current node_
    #  1. `self.root` is current node
    #  3. if `self.root` is sbling, it has go into it's parent
    #  3. `self.state` is `self.STATE_OPEN`
    def handle_starttag(self, tag, attrs):
        print("Start tag :", tag)
        if self.root is None:
            raise Exception('no elem? impossible')
        if self.root.tag == 'text':
            raise Exception('text will not be the parent of current tag')
        if self.state == self.STATE_OPEN:
            # generally speaking, we are going deeper
            if self.is_alone(self.root.tag):
                # it can not have children, so it must be sibling of current tag
                parent = self.parents.pop()
                parent.children.append(self.root) # brother go into parents
                self.parents.append(parent)
                self.root = self.build_node(tag, attrs)
                return
        # tag node have parent
        # we are going deeper
        self.parents.append(self.root)
        self.root = self.build_node(tag, attrs)

        self.state = self.STATE_OPEN

    # pre-condition
    #  1. we are leaving the current node
    #  2. `self.root` is the current node, who has been build
    #  4. `self.state` can be any state but not `None`
    # post-condition
    #  1. `self.root` is the parent of leaving node
    #  3. `self.state` is `self.STATE_CLOSE`
    def handle_endtag(self, tag):
        print("End tag :", tag)
        if self.state is None:
            raise Exception('state is None')
        if len(self.parents) == 0:
            # root will never close
            raise Exception('no parents')

        print('\tparents', end='')
        for p in self.parents:
            print(',',p, end='')
        print()
        print('\tcur_elem', self.root)

        if self.root is None:
            raise Exception('root is None')
        if self.root.tag != tag:
            raise Exception('not equal tag, we are leaving {}, but current is {}'.format(tag, self.root.tag))
        # close root
        parent = self.parents.pop()
        parent.children.append(self.root)
        self.root = parent

        self.state = self.STATE_CLOSE

    # pre-condition
    #  1. we are encounting the text node, whose value is `data`
    #  2. `self.root` is the parent of the text node
    #  5. `self.state` can be any state include `None`
    # post-condition
    #  1. `self.root` is the parent of leaving text node, and it contains the text node now
    #  3. `self.state` is `self.STATE_TEXT`
    def handle_data(self, data):
        # print(data)
        if self.root is None:
            raise Exception('root can not be None')
        if self.is_alone(self.root.tag):
            raise Exception(self.root.tag+' can not contain text')
        text_node = self.build_node('text')
        text_node.value = data
        self.root.children.append(text_node)

        self.state = self.STATE_TEXT

def html2dom(content):
    parser = DomParser()
    parser.init()
    parser.feed(content)
    return parser.root

with open('last.html') as f:
    dom = html2dom(f.read())
    print(dom.c14n())
