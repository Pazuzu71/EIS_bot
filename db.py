import sqlite3
from sqlite3 import Error
from datetime import datetime


def sql_connection():
    try:
        conn = sqlite3.connect('base.db')
        print('Соединение открыто')
        return conn
    except Error:
        print(Error)


def conn_close(conn):
    print('Соединение закрыто')
    return conn.close()


def create_table(conn):
    cur = conn.cursor()
    cur.execute('''create table if not exists journal_dg_tmp
    (
        id         INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        zipname    TEXT,
        xmlname    TEXT,
        createdate TEXT
    );''')
    conn.commit()


def insert(conn, entities):
    cur = conn.cursor()
    cur.execute('''insert into journal_dg_tmp(zipname, xmlname, createdate) values (?, ?, ?)''', entities)
    conn.commit()
    print('Записано!')


def select(conn, column):
    cur = conn.cursor()
    cur.execute('''select zipname from journal_dg_tmp where xmlname = ?''', (column,))
    records = cur.fetchall()
    print('select_records', records)
    return records


def xmlname_like(conn, column):
    cur = conn.cursor()
    cur.execute('''select zipname from journal_dg_tmp where xmlname like ?''', ('%' + column + '%',))
    records = cur.fetchall()
    print('xmlname_like_records', records)
    return records


def zipname_like(conn, column):
    cur = conn.cursor()
    cur.execute('''select zipname from journal_dg_tmp where zipname like ?''', ('%' + column + '%',))
    records = cur.fetchall()
    print('zipname_like_records', records)
    return records


def select_like(conn, column1, column2):
    cur = conn.cursor()
    cur.execute('''select zipname from journal_dg_tmp where zipname like ? and xmlname like ?''', ('%' + column1 + '%', '%' + column2 + '%'))
    records = cur.fetchall()
    print('select_like_records', records)
    return records


if __name__ == '__main__':
    conn = sql_connection()
    create_table(conn)
    entities = ('contract_Tulskaja_obl_2022051100_2022051200_001.xml.zip', 'contract_1710405073922000045_73202813.xml',
               datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))
    insert(conn, entities)