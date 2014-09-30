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


#insert data from mailing table to domains table
def insert_data():
    con = connect_to_database()

    c = con.cursor()
    c.execute("select * from mailing")
    addr_rows1 = c.fetchall()
    c.execute("select addr from domains")
    addr_rows2 = c.fetchall()


    for each_row in addr_rows1:

        if each_row not in addr_rows2:

            addr = str(each_row)[2:-3]#get the email address as a string

            addr_lst = addr.strip().split("@") #get the domain name
            domain_name = addr_lst[1]

            try:
                c.execute("INSERT INTO domains(domain_name,date_of_entry,addr) \
                         VALUES(%s,CURDATE(),%s)", (domain_name, addr) )

                con.commit()
            except:
                con.rollback()
    con.close()


# count the domain name,store the data in a dict and return it
def count_domain():
    con = connect_to_database()

    c = con.cursor()
    c.execute("SELECT domain_name,COUNT(*) from domains GROUP BY domain_name")
    count = c.fetchall()


    count_dic = {}

    for each_domain in count:
        domain = each_domain[0]
        num = int(each_domain[1])
        count_dic[domain] = num

    con.close()

    return count_dic


#count the domain names that added within 30 days,store the data in a dict and
#return it
def count_30_domain():
    con = connect_to_database()

    c = con.cursor()
    c.execute("SELECT domain_name,count(*) from domains \
               WHERE DATEDIFF(date_of_entry,CURDATE()) <= 30 \
               GROUP BY domain_name")
    count30 = c.fetchall()

    count30_dic = {}

    for each_domain in count30:
        domain = each_domain[0]
        num = int(each_domain[1])
        count30_dic[domain] = num

    con.close()

    return count30_dic


#get the top 50 domains by count sorted by percentage growth of the last 30 days
#compared to the total, store the data in list
def top50_domain():
    count_dic = count_domain()

    count30_dic = count_30_domain()
    growth_list = []
    for key in count_dic:

        count = count_dic[key]

        try:
            count30 = count30_dic[key]
        except:
            count30 = 0

        per = float(count30) /float(count)
        #1.0 means 100%
        growth_list.append((float(per),key))

    growth_list.sort()
    growth_list.reverse()

    i = 0
    print("Domain name       Percentage of Growth")
    while (i < 50):
        try:
            row = growth_list[i][1] + "              " + str(growth_list[i][0])
            print (row)

            #print(growth_list[i][1] + ' : ' + growth_list[i][0])
            i = i + 1
        except:
            break

insert_data()
top50_domain()
