#coding: utf-8

import html
from html.parser import HTMLParser

def is_alone(tag):
    return tag in ['br', 'hr', 'img', 'meta', 'link']

class DomNode(object):
    """docstring for DomNode"""
    def __init__(self, tag):
        super(DomNode, self).__init__()
        self.tag = tag
        self.attrs = None
        self.children = []
        self.value = None
        self.decl = None
        self.is_alone = False

    def __str__(self):
        attrs = dict(self.attrs)
        if 'id' in attrs:
            return '<{} id="{}">'.format(self.tag, attrs['id'])
        if 'name' in attrs:
            return '<{} name="{}">'.format(self.tag, attrs['name'])
        return '<{}>'.format(self.tag)

    def c14n(self):
        if self.children:
            inner = ''.join([e.c14n()+'' for e in self.children])
        else:
            inner = self.value
        if self.tag == 'root':
            if self.decl is None:
                return inner
            return '<!{}>\n{}'.format(self.decl, inner)
        elif self.tag == 'text':
            if len(self.value.strip()) == 0:
                return ''
            return self.value
        else:
            attrs = ''.join([' {}="{}"'.format(k, html.escape(v)) for k, v in self.attrs])
            if self.is_alone:
                return '<{0}{1} />\n'.format(self.tag, attrs)
            if inner is None:
                return '<{0}{1}></{0}>\n'.format(self.tag, attrs)
            if len(inner) > 0 and inner[0] == '<':
                inner = '\n'+inner
            return '<{0}{1}>{2}</{0}>\n'.format(self.tag, attrs, inner)

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

        self.root = self.build_node('root') # current element, when parse finish, it become root
        self.parents = [] # the parents of current element
        self.state = None
        self.i = 0

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
        node = self.build_node(tag, attrs)
        self._handle_starttag(tag, attrs, node)

    def _handle_starttag(self, tag, attrs, node):
        self.i += 1
        # attrs_dict = dict(attrs)
        # if 'data-widget' in attrs_dict:
        #     print("{}. Start <{}> {}".format(self.i, tag, attrs), end='\n')
        # self.print_path()
        if self.root is None:
            raise Exception('no elem? impossible')
        if self.root.tag == 'text':
            raise Exception('text will not be the parent of current tag')
        if self.state == self.STATE_OPEN and is_alone(self.root.tag):
            # it must be sibling of current tag
            # print('{} go into parents '.format(self.root))
            self.root.is_alone = True
            self.parents[-1].children.append(self.root) # brother go into parent, and we close self.root
            self.root = node
        elif self.state == self.STATE_OPEN or self.state == self.STATE_CLOSE or self.state is None:
            # tag node have parent
            # we are going deeper
            self.parents.append(self.root)
            self.root = node
        else:
            raise Exception('{} is not sibling or parent of {}'.format(self.root.tag, tag))

        self.state = self.STATE_OPEN
        # self.print_path()

    def handle_decl(self, decl):
        self.root.decl = decl

    def handle_startendtag(self, tag, attrs):
        node = self.build_node(tag, attrs)
        node.is_alone = True
        self._handle_starttag(tag, attrs, node)
        self.handle_endtag(tag)

    # pre-condition
    #  1. we are leaving the current node
    #  2. `self.root` is the current node(who has been build), or the last child of the current node
    #  3. if `self.root` is the last child of the current node, that child should be alone, and should be not put into current node yet
    #  4. `self.state` can be any state but not `None`
    # post-condition
    #  1. `self.root` is the parent of leaving node
    #  3. `self.state` is `self.STATE_CLOSE`
    def handle_endtag(self, tag):
        # print("End <{}>".format(tag))
        if self.state is None:
            raise Exception('state is None')
        if len(self.parents) == 0:
            # root will never close
            raise Exception('no parents')

        if self.root is None:
            raise Exception('root is None')
        if self.root.tag != tag:
            if self.state == self.STATE_OPEN and is_alone(self.root.tag):
                current = self.parents.pop()
                # print('{} go into parent'.format(self.root))
                current.children.append(self.root)
                parent = self.parents.pop()
                parent.children.append(current)
                self.root = parent
                self.state = self.STATE_CLOSE
                return
            else:
                raise Exception('not equal tag, we are leaving <{}>, but current is <{}>'.format(tag, self.root.tag))
        # close root
        parent = self.parents.pop()
        # print('{} go into parent'.format(self.root))
        parent.children.append(self.root)
        self.root = parent

        self.state = self.STATE_CLOSE
        # self.print_path()

    # pre-condition
    #  1. we are encounting the text node, whose value is `data`
    #  2. `self.root` is the parent or the sibling of the text node
    #  5. `self.state` can be any state include `None`
    # post-condition
    #  1. `self.root` is the parent of leaving text node, and it contains the text node now
    #  3. `self.state` remains
    def handle_data(self, data):
        # print('data', repr(data))
        if self.root is None:
            raise Exception('root can not be None')
        text_node = self.build_text_node(data)
        if self.state == self.STATE_OPEN and is_alone(self.root.tag):
            # brother not go into parent now because it will be handdled in endtag
            self.parents[-1].children.append(text_node)
            return
        self.root.children.append(text_node)
        # self.print_path()

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
    if len(parser.parents) > 0:
        raise Exception('root has parents')
    return parser.root

with open('last.html') as f:
    dom = html2dom(f.read())
    # print(dom.c14n())
    print(dom.get_element_by_id('js-reg-with-mail-in-top').c14n())
