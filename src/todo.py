#------------------------------------------------------------------------------------------------------------#
# IMPORTING REQUIRED ITEMS-----------------------------------------------------------------------------------# IMPORTING REQUIRED ITEMS
#------------------------------------------------------------------------------------------------------------#
import sqlite3 as sql
from sqlite3 import *
from bottle import route, run, debug, template, request, static_file, error, view, default_app
from bottle import *
from datetime import date
import hashlib # Allows password Hashing #

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR LOGIN PAGE---------------------------------------------------------------------------------# LOGIN PAGE
#------------------------------------------------------------------------------------------------------------#



###### LOGIN PAGE ######
@route('/loginPage')
def login_page():
    userOutput = template('src/html/loginPage')
    return userOutput
    

@post('/loginPage')
def loginpost():
    global sesskey
    username = request.forms.get('username')
    password = request.forms.get('password')
    conn = sql.connect('src/db/users.db')
    usernameCheck = conn.execute("SELECT password FROM user_data WHERE username = (?)", (username,)).fetchone()
    passwordCheck = conn.execute("SELECT username FROM user_data WHERE password = (?)", (password,)).fetchone()
    conn.close() 
    if username == usernameCheck and password == passwordCheck: 
        sesskey=1
        return template('src/html/loginSuccess.html')
    else:
        conn.close()
        sesskey=1
        return template('src/html/loginFailure.html', sesskey=sesskey)

@route('/status-inactive')
def whenUserStatusInactive():
    return template('src/html/userstatusinactive.html')

###### LOGIN PAGE ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR SIGN UP PAGE-------------------------------------------------------------------------------# SIGN UP PAGE
#------------------------------------------------------------------------------------------------------------#

###### SIGN UP PAGE ######
@route('/signUp')
def signUp_page():
    output = template('src/html/signUp')
    return output

@post('/signUp')
def userSignUp():
    conn = sql.connect('src/db/users.db')
    username = request.forms.get('username')
    password = request.forms.get('password')
    cur = conn.execute('SELECT username FROM user_data WHERE username=?', (username,)) 
    checkUsername = cur.fetchall() # sets the result of SQL query to a varible, str
    if checkUsername != 0:
        global tableforuser
        tableforuser = request.forms.get('username')
        table_exists = "SELECT username FROM user_data WHERE username = ?"
        if not conn.execute(table_exists, (tableforuser,)).fetchone():
           createTable = f'CREATE TABLE [{tableforuser}]("id" INTEGER PRIMARY KEY, "task" char(100) NOT NULL, status bool NOT NULL)'
           insertTable = f'INSERT INTO [{tableforuser}]("task",status) VALUES ("This is your first database entry, {tableforuser}",0)'
           time.sleep(3)
           conn.execute(createTable)
           time.sleep(1)
           conn.execute(insertTable)       
        conn.execute("INSERT INTO user_data (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        redirect('/loginPage')
    else:
        conn.close()
        return template('src/html/signUp')
###### SIGN UP PAGE ######



#------------------------------------------------------------------------------------------------------------#
# STATIC FILEPATH--------------------------------------------------------------------------------------------# STATIC FILEPATH
#------------------------------------------------------------------------------------------------------------#

###### IMPORT CSS / JAVASCRIPT #######
@route('/static/<filepath:path>')
def load_static(filepath):
    return static_file(filepath, root='C:/Users/liamg/Desktop/Actual Code/src/html/static')

###### IMPORT CSS / JAVASCRIPT #######

#------------------------------------------------------------------------------------------------------------#
# DEFAULT ROUTE----------------------------------------------------------------------------------------------# DEFAULT ROUTE
#------------------------------------------------------------------------------------------------------------#

###### INDEX ROUTE ######
@route('/')
def home_page(): 
    global sesskey
    sesskey=0
    return template('src/html/index', sesskey=sesskey)
###### INDEX ROUTE ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR USER TO EDIT SELECTED ITEM-----------------------------------------------------------------# EDIT 
#------------------------------------------------------------------------------------------------------------#

###### EDIT ITEM (INT) ######
@route('/edit/<no:int>', method='GET')
def edit_item(no):

    if request.GET.save:
        edit = request.GET.task.strip()
        status = request.GET.status.strip()

        if status == 'open':
            status = 1
        else:
            status = 0

        conn = sql.connect('src/db/todo.db')
        c = conn.cursor()
        c.execute("UPDATE todo SET task = ?, status = ? WHERE id LIKE ?", (edit, status, no))
        conn.commit()
        return template('src/html/itemUpdated.html', no=no)
    else:
        conn = sql.connect('src/db/todo.db')
        c = conn.cursor()
        c.execute("SELECT task FROM todo WHERE id LIKE ?", (no,))
        cur_data = c.fetchone()
        return template('src/html/edit_task.html', old=cur_data, no=no)
    
###### EDIT ITEM (INT) ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR PAGE FOR USER TO CHOOSE WHAT ITEM TO EDIT--------------------------------------------------# EDIT SELECTOR
#------------------------------------------------------------------------------------------------------------#

####### PRELIMINARY EDIT ######
@route('/edit/editSelect')
def uEditChoice():
   output = template('src/html/editSelect.html')
   return output
####### PRELIMINARY EDIT ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION  PAGE FOR USER TO CHOOSE TO DELETE ALL ITEMS OR DELETE ONE ITEM--------------------------------# DELETE SELECT SELECTOR
#------------------------------------------------------------------------------------------------------------#

@route('/deleteQ')
def delete_query():
    output = template('src/html/deleteQ.html')
    return output

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR USER TO DELETE ALL ITEMS-------------------------------------------------------------------# DELETE ALL
#------------------------------------------------------------------------------------------------------------# 

##### DELETE ALL ITEMS ####
@route('/deleteAllitems')
def deleteALLitems():
    if request.GET.save:
        conn = sql.connect('src/db/todo.db')
        c = conn.cursor()
        c.execute("DELETE FROM todo")
        conn.commit()
        c.close()
        return template('src/html/deleteALLitemsuccess')
    else:

        return template('src/html/deleteAllitems')

##### DELETE ALL ITEMS ####

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR USER TO DELETE SPECIFIC ITEM---------------------------------------------------------------# DELETE
#------------------------------------------------------------------------------------------------------------#

###### DELETE ITEM ######
@route('/delete/<no:int>')
def delete(no):
    if request.GET.save:
        edit = request.GET.task.strip()
        status = request.GET.status.strip()

        if status == 'Confirm Delete':
            conn = sql.connect('src/db/todo.db')
            c = conn.cursor()
            c.execute("Delete FROM todo where id = ?", (no,))
            conn.commit()
            c.close()
        else:
            return template('src/html/deleteFailure.html', no=no)
        return template('src/html/deleteSuccess.html', no=no)

    else:
        conn = sql.connect('src/db/todo.db')
        c = conn.cursor()
        c.execute("SELECT task FROM todo WHERE id LIKE ?", (no,))
        cur_data = c.fetchone()
        return template('src/html/delete.html', old=cur_data, no=no)
###### DELETE ITEM ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR PAGE FOR USER TO CHOOSE WHAT ITEM TO DELETE------------------------------------------------# DELETE SELECT
#------------------------------------------------------------------------------------------------------------#

####### PRELIMINARY Delete ######
@route('/delete/deleteSelect')
def uDeleteChoice():
    output = template('src/html/deleteSelect.html')
    return output
####### PRELIMINARY Delete ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION PAGE FOR USER TO VIEW ITEMS IN todo LIST-------------------------------------------------------# VIEW 
#------------------------------------------------------------------------------------------------------------#

####### VIEW ALL OPEN ITEMS ######
#@route('/todo')
#def todo_list():
#    TableName = request.forms.get('username')
#    DynamicTable = TableName
#    conn = sql.connect('src/db/users.db')
#    c = conn.cursor()
#    data_fetch = "SELECT id,task FROM sqlite_master WHERE type='table' and name = ?"
#    conn.execute(data_fetch, (DynamicTable,)).fetchall() is not None
#    result = c.fetchall()
#    conn.close()
#    output = template('src/html/make_table', diagnostic=TableName, rows=result )
#    return output

@route('/todo')
def todo_list():
    conn = sql.connect('src/db/todo.db')
    c = conn.cursor()
    data_fetch = "SELECT id, task FROM todo WHERE status = 0"
    conn.execute(data_fetch)
    result = c.fetchall()
    conn.close()
    output = template('src/html/make_table', rows=result )
    return output
    
###### VIEW ALL OPEN ITEMS ######

#query = "SELECT 1 FROM sqlite_master WHERE type='table' and name = ?"
#    return db.execute(query, (name,)).fetchone() is not None

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION PAGE FOR USER TO VIEW CLOSED AND OPEN ITEMS IN todo LIST---------------------------------------# VIEW ALL
#------------------------------------------------------------------------------------------------------------#

@route('/allItems')
def todo_list_all():

    conn = sql.connect('src/db/todo.db')
    c = conn.cursor()
    c.execute("SELECT id, task, status, date_due, date_created FROM todo") 
    result = c.fetchall()
    c.close()
    print(result)
    output = template('src/html/ALLitems.html', rows=result)
    return output

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION PAGE FOR USER TO VIEW CLOSED AND OPEN ITEMS IN todo LIST---------------------------------------# VIEW QUERY
#------------------------------------------------------------------------------------------------------------#

@route('/userSelectTodo')
def todo_list_query():
    output = template('src/html/todoQ.html')
    return output

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR USER TO CREATE NEW todo ITEM---------------------------------------------------------------# CREATE 
#------------------------------------------------------------------------------------------------------------#

###### CREATE NEW ITEM ######
@route('/new', method='GET')
def new_item():

        if request.GET.save:

            new = request.GET.task.strip()
            date_due = request.GET.date_due.strip()
            conn = sql.connect('src/db/todo.db')
            c = conn.cursor()
            now = datetime.now()
            date_created = now.strftime("%d/%m/%Y %H:%M")
            #CODE FOR FINDING TIME AND DATE
            #SELECT strftime('%Y/%m/%d/%H:%M','now','localtime');
            #CODE FOR FINDING NUMBER OF DAYS,HOURS AND MINUTES SINCE ITEM CREATED
            #SELECT strftime('%d %h','now','localtime') - strftime('%s','2014-10-07 02:34:56');

            c.execute("INSERT INTO todo (task,status,date_due,date_created) VALUES (?,?,?,?)", (new, 1, date_due, date_created))
            new_id = c.lastrowid

            conn.commit()
            c.close()

            return template('src/html/itemCreated.html')
            
        else:
            return template('src/html/new_task.html')
###### CREATE NEW ITEM ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR USER QUERY TO CREATE NEW ITEM -------------------------------------------------------------# CREATE NEW PROMPT
#------------------------------------------------------------------------------------------------------------#

##### MAKE ANOTHER ITEM? #####
@route('/anotheritem')
def makeAnother():
    return template('src/html/anotheritem.html')
#### MAKE ANOTHER ITEM? #####

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR PAGE ABOUT ME -----------------------------------------------------------------------------# ABOUT ME
#------------------------------------------------------------------------------------------------------------#

####### ABOUT ME PAGE #######
@route('/aboutMe')
def about_me():
    output = template('src/html/about_me.html')
    return output

####### ABOUT ME PAGE #######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR USER HELP PAGE ----------------------------------------------------------------------------# HELP
#------------------------------------------------------------------------------------------------------------#

####### HELP THING #######
@route('/help')
def help():
    output = template('src/html/help.html')
    return output
####### HELP THING #######

#------------------------------------------------------------------------------------------------------------#
# validating? uses regular expressions ----------- ----------------------------------------------------------# SHOW ITEM
#------------------------------------------------------------------------------------------------------------#

####### SHOW ITEM #######
@route('/item<item:re:[0-9]+>')
def show_item(item):

        conn = sql.connect('src/db/todo.db')
        c = conn.cursor()
        c.execute("SELECT task FROM todo WHERE id LIKE ?", (item,))
        result = c.fetchall()
        c.close()

        if not result:
            return 'This item number does not exist!'
        else:
            return 'Task: %s' % result[0]
####### SHOW ITEM #######

#------------------------------------------------------------------------------------------------------------#
# Validating with expressions -------------------------------------------------------------------------------# SHOW JSON
#------------------------------------------------------------------------------------------------------------#

####### JSON  #######
@route('/json<json:re:[0-9]+>')
def show_json(json):

    conn = sql.connect('src/db/todo.db')
    c = conn.cursor()
    c.execute("SELECT task FROM todo WHERE id LIKE ?", (json,))
    result = c.fetchall()
    c.close()

    if not result:
        return {'task': 'This item number does not exist!'}
    else:
        return {'task': result[0]}
####### JSON  #######

#------------------------------------------------------------------------------------------------------------#
# Used to catch user URL erors ------------------- ----------------------------------------------------------# 404/403
#------------------------------------------------------------------------------------------------------------#

#######  ERROR CONTAINMENT #######
@error(403)
def mistake403(code):
    output = template('src/html/403.html')
    return output

@error(404)
def mistake404(code):
    output = template('src/html/404.html')
    return output

@error(405)
def mistake405():
    output = template('src/html/404.html')
    return output

#######  ERROR CONTAINMENT #######

#------------------------------------------------------------------------------------------------------------#
# Used to create pages between processes being run ----------------------------------------------------------# LOAD PAGES
#------------------------------------------------------------------------------------------------------------#
###### LOAD PAGEs #######
@route('/loadPage')
def load_func():
    output = template('src/html/loadPage.html')
    return output

@route('/loadPage2')
def loadPage():
    output = template('src/html/loadPage2.html')
    return output

@route('/loadPage3')
def loadPage():
    output = template('src/html/loadPage3')
    return output
###### LOAD PAGES ####

#------------------------------------------------------------------------------------------------------------#
# EXPERIMENTAL SECTION FOR USER SUPPORT _ TO BE IMPLEMENTED LATER ON IN DEVELOPMENT--------------------------# COLOUR OPTIONS / EMAIL FORM
#------------------------------------------------------------------------------------------------------------#

##### COLOUR OPTION #####
@route('/colourSelect')
def colourselect():
    userOutput = template('src/html/colourOptions.html')
    return userOutput

##### COLOUR OPTION ######

##### EMAIL FORM #####
@route('/emailForm')
def emailForm():
    userOutput = template('src/html/emailForm.html')
    return userOutput

@route('/contact-form-process')
def emailform():
    userOutput = template('src/php/contact-form-process.html')
    return userOutput
#### PHP EMAIL FORM ####


#------------------------------------------------------------------------------------------------------------#
# RUNS THE WEBSITE ------------------------------------------------------------------------------------------# HOST
#------------------------------------------------------------------------------------------------------------#

run(host='127.1.0.1', port=5500, reloader=True, debug=True)
