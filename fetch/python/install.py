#coding: utf-8

import db

with open('install.sql') as f:
    sql = f.read()
    # print('sql', sql)
    c = db.connect()
    for sql_create in sql.split(';'):
        # print('sql_create', sql_create)
        sql_create = sql_create.strip()
        if len(sql_create) > 0:
            print(sql_create)
            cursor = c.cursor()
            cursor.execute(sql_create)
print('OK')
