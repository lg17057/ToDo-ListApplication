import sqlite3
import time
#from todo.py import username variable


#This program is used to create users.db database file

conn = sqlite3.connect('users.db') 
def create_table():
    conn.execute("CREATE TABLE user_data ( user_id INTEGER PRIMARY KEY NOT NULL UNIQUE, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL )")
    conn.execute("INSERT INTO users (task,status) VALUES ('Welcome to your To-Do List, {}',0)")
    conn.commit()


#This program is a tester used to add dynamic/specific data to a table
conn = sqlite3.connect('src/db/users.db')
def add_data():
    global username
    username = input("Please enter your username:")
    password = input("Please enter your password:")
    value = input("Please enter last value:")
    time.sleep(4)
    conn.execute("INSERT INTO user_data (user_id, username, password) VALUES (?,?,?)",(value,username,password))
    print("Loading")
    conn.commit()


#This program is a tester used to view contet from a table
conn = sqlite3.connect('src/db/users.db')
def read_data():
    c = conn.cursor()
    user_id = 0
    user_id = input("Please enter the user id for the username you would like to fetch;")
    c.execute("SELECT username FROM user_data WHERE user_id LIKE ?",(user_id))
    username = c.fetchone()
    print(username)


#This program is a tester trying to create a table for a user once they create an account
def create_table(username):
    conn = sqlite3.connect('src/db/users.db')
    global tablename
    tablename = username
    table_exist = "SELECT username FROM user_data WHERE username = ?"
    if not conn.execute(table_exist, (tablename,)).fetchone():
        table_create = f"CREATE TABLE [{tablename}](id INTEGER PRIMARY KEY, task char(100) NOT NULL, status bool NOT NULL)"
        table_insert = f"INSERT INTO [{tablename}](task,status) VALUES ('This is your first database entry, {tablename}',0)"
        conn.execute(table_create)
        conn.execute(table_insert)
        conn.commit()
        print("Table created")

    else:
        "Table create failure"

def create_tododata(username):
    conn = sqlite3.connect('src/db/users.db')
    table_insert = f"INSERT INTO [{tablename}](task,status) VALUES ('This is your second database entry, {tablename}',0)"
    conn.execute(table_insert)
    conn.commit()


add_data()
time.sleep(5)
create_table(username)
time.sleep(5)
create_tododata(username)