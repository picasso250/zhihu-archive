#coding: utf-8

import sqlite3

def connect():
    return sqlite3.connect("zhihu.db")

def insert_table(table, args):
    conn = connect()
    cursor = conn.cursor()
    keys = args.keys()
    key_str = ','.join(['`{}`'.format(key) for key in keys])
    value_str = ','.join(['?' for key in keys])
    values = [str(e) for e in list(args.values())]
    sql_tpl = 'INSERT INTO `{}` ({}) VALUES ({})'
    sql = sql_tpl.format(table, key_str, value_str)
    # print(sql_tpl.format(table, key_str, ','.join(["'{}'".format(e) for e in list(args.values())])))
    cursor.execute(sql, tuple(values))
    conn.commit()
    return cursor.lastrowid

def update_table(table, args, where):
    conn = connect()
    cursor = conn.cursor()
    keys = args.keys()
    key_str = ','.join(['`{}`=?'.format(key) for key in keys])
    values = [str(e) for e in list(args.values())]
    where_str = ','.join(['`{}`=?'.format(key) for key in where.keys()])
    where_values = [str(e) for e in list(where.values())]
    values.append(*where_values)
    sql_tpl = 'UPDATE `{0}` SET {1} WHERE {2}'
    sql = sql_tpl.format(table, key_str, where_str)
    key_repr = ','.join(['`{}`="{}"'.format(key, str(value)) for key, value in args.items()])
    where_repr = ','.join(['`{}`="{}"'.format(key, value) for key, value in where.items()])
    # print(sql_tpl.format(table, key_repr, where_repr))
    cursor.execute(sql, tuple(values))
    return conn.commit()
