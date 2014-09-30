#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb


def connect_to_database():
    try:
        #con = mdb.connect('localhost', 'username', 'password', 'database_name')
        # you need to change this line
        con = mdb.connect("mysql.server","utmarty","999999","utmarty$Test")
        return con

    except:
        print "Unable to connect the database."
        return (-1)

def create_domains():
    con = connect_to_database()


    with con:

        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS domains")
        cur.execute("CREATE TABLE domains(Id INT PRIMARY KEY AUTO_INCREMENT, \
                     domain_name VARCHAR(50) NOT NULL, \
                     date_of_entry date NOT NULL, \
                     addr VARCHAR(255) NOT NULL)")
    con.close()

create_domains()
