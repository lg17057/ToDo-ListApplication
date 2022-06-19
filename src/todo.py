#------------------------------------------------------------------------------------------------------------#
# IMPORTING REQUIRED ITEMS-----------------------------------------------------------------------------------# IMPORTING REQUIRED ITEMS
#------------------------------------------------------------------------------------------------------------#
from select import select
import re
import sqlite3 as sql
from sqlite3 import *
from bottle import route, run, debug, template, request, static_file, error, view, default_app
from bottle import *
from datetime import date
import hashlib # Allows password Hashing #


message1=''
message2=''
message3=''
username=''

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR LOGIN PAGE---------------------------------------------------------------------------------# LOGIN PAGE
#------------------------------------------------------------------------------------------------------------#


@route('/loginPage')
def login():
    response.set_cookie("loginstatus", value="False", secret='some-secret-key')
    print("Login status set to false")
    return template('src/html/loginPage.html')

@route('/loginPage', method='POST')
def do_login():
    response.set_cookie("loginstatus", value="False", secret='some-secret-key')
    global username
    sesskey = 0
    username = request.forms.get('username')
    password = hashlib.sha512(request.forms.get('password').encode('utf8')).hexdigest()
    conn = sql.connect('src/db/users.db')
    cur = conn.execute("SELECT password FROM user_data WHERE username = ?", (username,))
    key = cur.fetchone()
    print(key)
    if password == key[0]:
        response.set_cookie("loginstatus", value="True", secret='some-secret-key')
        response.set_cookie("user_id", username)
        print("Accessing table name {}, using password {}, key={}".format(username,password,key))
        sesskey=1
        conn.close()
        return template('src/html/loginSuccess.html',message1='Accessing User Id {}'.format(username),message2='',message3='', sesskey=sesskey)
    elif password != key[0]:
        response.set_cookie("loginstatus", value="False", secret='some-secret-key')
        print("Attempted accessing table name {}, using password {}, unsuccessfull".format(username,password))
        sesskey=0
        conn.close()
        return template('src/html/loginFailure.html', sesskey=sesskey)
    


###### LOGIN PAGE ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION PAGE FOR USER NOT LOGGED IN MESSAGE -----------------------------------------------------------#
#------------------------------------------------------------------------------------------------------------#

@route('/loginstatus')
def usernotloggedin():
    return template('src/html/logoutstatus.html')

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR SIGN UP PAGE-------------------------------------------------------------------------------# SIGN UP PAGE
#------------------------------------------------------------------------------------------------------------#

###### SIGN UP PAGE ######
@route('/signUp')
def signUp():
    return template('src/html/signUp')

@post('/signUp')
def userSignUp():
    conn = sql.connect('src/db/users.db')
    c = conn.cursor()
    username = request.forms.get('username')
    global tableforuser
    tableforuser = username
    password = hashlib.sha512(request.forms.get('password').encode('utf8')).hexdigest()
    cur = c.execute('SELECT username FROM user_data WHERE username=?', (username,)) 
    checkUsername = cur.fetchall() # sets the result of SQL query to a varible, str
    now = datetime.now()
    date_created = now.strftime("%d/%m/%Y %H:%M")
    if checkUsername != 0:
        table_exists = "SELECT username FROM user_data WHERE username = ?"
        if not conn.execute(table_exists, (tableforuser,)).fetchone():
           createTable = f"CREATE TABLE [{tableforuser}](id INTEGER PRIMARY KEY, task char(100) NOT NULL, status bool NOT NULL, date_due TEXT NOT NULL, date_created TEXT NOT NULL)"
           insertTable = f"INSERT INTO [{tableforuser}](task,status,date_due,date_created) VALUES ('This is your first database entry, {tableforuser}',0,'Never','{date_created}')"
           time.sleep(1)
           conn.execute(createTable)
           time.sleep(1.5)
           conn.execute(insertTable)       
        conn.execute("INSERT INTO user_data (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        redirect('/loginPage')
    else:

        signuperror = "There was an error with creating user with name {}".format(username)
        return template('src/html/index.html', message1=signuperror,message2='',message3='',username='')
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
    loginstatus = request.get_cookie("loginstatus")
    return template('src/html/index.html',loginstatus=loginstatus,message2='',message3='',username='',message1='')
    
###### INDEX ROUTE ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR EMAIL FORM---------------------------------------------------------------------------------# ITEM NOT FOUND
#------------------------------------------------------------------------------------------------------------#


@route('/contact_form')
def emailForm():
    userOutput = template('src/html/email_form.html')
    return userOutput

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
        itemupdated="The Selected Item No#{} has been updated".format(no)
        return template('src/html/index.html', message1=itemupdated,message2='',message3='',username='', no=no)
    else:
        conn = sql.connect('src/db/todo.db')
        c = conn.cursor()
        c.execute("SELECT task FROM todo WHERE id LIKE ?", (no,))
        cur_data = c.fetchone()
        item_invalid="The Selected Item No#{} does not exist".format(no)
        if not cur_data:
            return template('src/html/index.html', message1=item_invalid,message2='',message3='',username='')
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
# DESIGNATION OR USER TO DELETE ALL ITEMS-------------------------------------------------------------------# DELETE ALL
#------------------------------------------------------------------------------------------------------------# 

##### DELETE ALL ITEMS ####
@route('/deleteAllitems')
def deleteALLitems():
    if request.GET.save:
        conn = sql.connect('src/db/todo.db')
        c = conn.cursor()
        result = c.fetchall()
        c.execute("DELETE FROM todo")
        conn.commit()
        c.close()

        if not result:
            noitemsindatabase = "There are currently no entries in the database"
            return template('src/html/index.html',message1=noitemsindatabase,message2='',message3='',username='')
        deleteallitemsuccess="Successfully deleted all items in database"
        return template('src/html/index.html', message1=deleteallitemsuccess,message2='',message3='',username='')
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
            delete_failure="Unable to delete selected item No#{}".format(no)
            return template('src/html/index.html', message1=delete_failure, no=no,message2='',message3='',username='')
        delete_success="Item No#{} successfully deleted"
        return template('src/html/index.html', message1=delete_success, no=no,message2='',message3='',username='')

    else:
        conn = sql.connect('src/db/todo.db')
        c = conn.cursor()
        c.execute("SELECT task FROM todo WHERE id LIKE ?", (no,))
        cur_data = c.fetchone()
        item_invalid="The Selected Item No#{} does not exist".format(no)
        if not cur_data:
            return template('src/html/index.html', message1=item_invalid,message2='',message3='',username='')
        return template('src/html/delete.html', old=cur_data, no=no,message2='',message3='',username='')
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

###### VIEW ALL OPEN ITEMS ######
@route('/todo')
def todo_list():
    conn = sql.connect('src/db/users.db')
    c = conn.cursor()
    loginstatus = request.get_cookie("loginstatus", secret='some-secret-key')
    username = request.get_cookie("user_id")

    print(loginstatus)
    if loginstatus == "True":
        print("Login status is true, continuing to todo list page")
        select_items = f'''SELECT * FROM [{username}]'''
        print(username)
        c.execute(select_items)
        print("Accessing table name {}".format(username))
        result = c.fetchall()
        conn.close()
        return template('src/html/make_table', diagnostic=username, rows=result )
    elif loginstatus == "False":
        print("Login status is false, redirecting to login status page")
        conn.close()
        redirect('/loginstatus')



#@route('/todo') execute("SELECT weight FROM Equipment WHERE name = :name AND price = :price",
#def todo_list():
#
#    conn = sql.connect('src/db/todo.db')
#    c = conn.cursor()
#    c.execute("SELECT id, task, date_created, date_due FROM todo WHERE status LIKE '1' LIMIT 50")
#    result = c.fetchall()
#    c.close()
#    if not result:
#        redirect('/no_items_in_database')
#    output = template('src/html/make_table', rows=result)
#    return output
#    
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
    c.execute("SELECT id, task, status, date_created, date_due FROM todo LIMIT 50") 
    result = c.fetchall()
    
    c.close()
    noitemsindatabase = "There are currently no entries in the database"
    if not result:
        return template('src/html/index.html', message1=noitemsindatabase,message2='',message3='',username='')
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
        conn = sql.connect('src/db/todo.db')
        c = conn.cursor()
        c.execute('SELECT COUNT (*) from todo')
        cur_result = c.fetchone()
        rows = cur_result[0]
        if rows < 50:
            new = request.GET.task.strip()
            date_due = request.GET.date_due.strip()
            conn = sql.connect('src/db/todo.db')
            c = conn.cursor()
            now = datetime.now()
            date_created = now.strftime("%d/%m/%Y %H:%M")
            c.execute("INSERT INTO todo (task,status,date_due,date_created) VALUES (?,?,?,?)", (new, 1, date_due, date_created))
            new_id = c.lastrowid
            conn.commit()
            c.close()
            return template('src/html/index.html', rows=rows,message1='Create New Item Success',message2='',message3='',username='')
        elif rows > 50:
            toomanyitems="There are currently too many entries in the database."
            toomanyitems2="Please delete entries to create a new entry"
            toomanyitems3="Maximum of 50 items in a database"
            return template('src/html/index.html', message1=toomanyitems,message2=toomanyitems2,message3=toomanyitems3,username='')
            #'<h2 style="font-family: open-sans, sans-serif;font-weight: 300;font-style: normal;">It appears there are too many entries in the database.</h2><h3 style="font-family: open-sans, sans-serif;font-weight: 300;font-style: normal;">Please Delete Current entries up to 50 to create new entries.</h3><form action="/" method="GET"><input style="font-family: open-sans,sans-serif;font-weight: 300;font-style: normal;padding: 14px 28px;border: 2px solid #555555;text-decoration: none;font-size: 16px;color: #000000;cursor: pointer;background-color: #ffffff;display: block;transition: 0.3s;" type="submit" name="homebutton" value="Return Home" ></form>'
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




#------------------------------------------------------------------------------------------------------------#
# RUNS THE WEBSITE ------------------------------------------------------------------------------------------# HOST
#------------------------------------------------------------------------------------------------------------#

run(host='127.1.0.1', port=5500, reloader=True, debug=True)
response.set_cookie("loginstatus", value="False", secret='some-secret-key')
