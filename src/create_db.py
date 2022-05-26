import sqlite3
#from todo.py import username variable
#this python file contains how the original file was created

conn = sqlite3.connect('todo.db') 
def create_table():
    conn.execute("CREATE TABLE todo (id INTEGER PRIMARY KEY, task char(100) NOT NULL, status bool NOT NULL)")
    conn.execute("INSERT INTO todo (task,status) VALUES ('Welcome to your To-Do List, {}',0)")
    conn.commit()