#coding: utf-8

import sqlite3

def connect():
    return sqlite3.connect("zhihu.db")
