#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3 as lite
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationships, sessionmaker
import os

name_db = 'database.db'
path_db = os.path.join(os.getcwd(), name_db)


class Connect(object):
    def __init__(self):
        self.check_db()
        self.con = lite.connect(name_db)
        #con.row_factory = lite.Row

    @staticmethod
    def check_db():
        # проверка на существование базы данных
        if not os.path.exists(path_db):
            try:
                # создание базы данных
                con = lite.connect(name_db)
                cur = con.cursor()
                # создание таблиц + наполнение
                cur.executescript("""
                begin transaction;
                create table users(user_id integer primary key AUTOINCREMENT NOT NULL, login text unique, 
                    create_date text);
                create table avatars(ava_id integer primary key AUTOINCREMENT NOT NULL, data blob);
                create table user_details(user_user_id integer, first_name text, last_name text, password text, 
                    ava_ava_id integer, start_date text, end_date text);
                create table messages(msg_id integer primary key AUTOINCREMENT NOT NULL, 
                    message_text text, user_from_id integer, user_to_id integer, send_date text, recieve_date text);
                commit;""")
                con.commit()
            except lite.Error as e:
                print('Ошибка БД: ' + str(e))

    def set_avatar(self, fname, login):
        file = open(fname, 'rb')
        img = file.read()
        binary = lite.Binary(img)
        cur = self.con.cursor()
        sql = "insert into avatars (data) values (?)"
        cur.execute(sql, binary)
        ava_id = cur.lastrowid
        user_id = self.get_user_id(login)
        sql = "update user_details " \
              "   set ava_ava_id = ?" \
              " where user_user_id = ? " \
              "   and datetime('now') between start_date and end_date"
        cur.execute(sql, (ava_id, user_id))
        self.con.commit()
        file.close()

    def get_user_id(self, login):
        user_id = None
        cur = self.con.cursor()
        sql = "select user_id " \
              "  from users " \
              " where login = ?"
        cur.execute(sql, login)
        data = cur.fetchone()
        if data:
            user_id = data[0]
        return user_id

    def get_last_user_detail(self, login):
        detail = None
        user_id = self.get_user_id(login)
        if user_id:
            cur = self.con.cursor()
            sql = "select rowid, * " \
                  "  from user_details " \
                  " where user_user_id = ? " \
                  "  and datetime('now') between start_date and end_date"
            cur.execute(sql, str(user_id))
            detail = cur.fetchone()
        return detail

    def check_password(self, login, password):
        detail = self.get_last_user_detail(login)
        if detail is None:
            self.set_pass_for_user(login, password)
            return True
        else:
            return password == detail[4]

    def set_pass_for_user(self, login, password):
        user_id = self.get_user_id(login)
        if user_id is None:
            user_id = self.create_user(login)
        cur = self.con.cursor()
        sql = "insert into user_details(user_user_id, password, start_date, end_date) " \
              "values(?, ?, datetime('now'), '2999-12-31 23:59:59')"
        cur.execute(sql, (user_id, password))
        self.con.commit()

    def create_user(self, login):
        cur = self.con.cursor()
        sql = "insert into users (login, create_date) " \
              "values (?, datetime('now'))"
        cur.execute(sql, login)
        user_id = cur.lastrowid
        self.con.commit()
        return user_id

    def send_message(self, login_to, response):
        login_from, message, time = (response['user'], response['data'], response['time'])
        cur = self.con.cursor()
        user_from = self.get_user_id(login_from)
        user_to = self.get_user_id(login_to)
        sql = "insert into messages (message_text, user_from_id, user_to_id, send_date) " \
              "values (?,?,?,datetime('now'))"
        cur.execute(sql, (message, user_from, user_to))
        msg_id = cur.lastrowid
        self.con.commit()
        return msg_id

    def get_messages(self, login):
        user_id = self.get_user_id(login)
        cur = self.con.cursor()
        sql = "select uf.login, m.message_text " \
              "  from messages m, users uf" \
              " where uf.user_id = m.user_from_id " \
              "   and m.user_to_id = ?"
        for rec in cur.execute(sql, user_id):
            yield rec
