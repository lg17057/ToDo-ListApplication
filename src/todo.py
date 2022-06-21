#------------------------------------------------------------------------------------------------------------#
# IMPORTING REQUIRED ITEMS-----------------------------------------------------------------------------------# IMPORTING REQUIRED ITEMS
#------------------------------------------------------------------------------------------------------------#
from select import select
import re
import sqlite3 as sql #connection between bottle/python and sqlite
from sqlite3 import *  #allows selecting from sqlite
from bottle import route, run, debug, template, request, static_file, error, view, default_app, abort #allows running of bottle website and its features
from bottle import *
from datetime import date #allows data_created data 
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
    return template('src/html/loginPage.html')

@route('/loginPage', method='POST')
def do_login():
    global username
    sesskey = 0
    username = request.forms.get('username') #accesses username entered on login page
    password = hashlib.sha512(request.forms.get('password').encode('utf8')).hexdigest() #hashed password
    conn = sql.connect('src/db/users.db')#connects database
    cur = conn.execute("SELECT password FROM user_data WHERE username = ?", (username,)) #selects password from user data
    key = cur.fetchone() #fetches one value from table
    print(key)
    if password == key[0]: #checks whether user inputted password is equal to existing password
        response.set_cookie("loginstatus", value="True")
        response.set_cookie("user_id", username)
        #login status  set to True, username set to user entered data (if pasword check successful)
        print("Accessing table name {}, using password {}, key={}".format(username,password,key))
        sesskey=1
        conn.close()
        return template('src/html/loginSuccess.html',message1='Accessing User Id {}'.format(username),message2='',message3='', sesskey=sesskey)
    elif password != key[0]: #if user input password is not equal to existing password
        response.set_cookie("loginstatus", value="False")
        #login value/status set to galse
        print("Attempted accessing table name {}, using password {}, unsuccessfull".format(username,password))
        sesskey=0
        response.set_cookie("sesskey", value="0")
        conn.close() #closes connection to sqlite3
        return template('src/html/loginFailure.html', sesskey=sesskey)
    


###### LOGIN PAGE ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION PAGE FOR LOGINSTATUS PAGE -----------------------------------------------------------#
#------------------------------------------------------------------------------------------------------------#

@route('/loginstatus')
def loginstatus():
    #page for when user is not logged in
    return template('src/html/logoutstatus.html')

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION PAGE FOR USER NOT LOGGED IN MESSAGE -----------------------------------------------------------#
#-----------------------------------------------------------------------------------------------
    
@route('/logout', method=["GET", "POST"])
def logout():
    response.set_cookie("loginstatus", value="False")
    #sets loginstatus to false
    response.set_cookie("user_id", value='')
    #sets user_id/username to blank str
    print("USER LOGGED OUT")
    return template('src/html/logoutSuccess.html')
        #sends user to a 401 page with specific message


#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR SIGN UP PAGE-------------------------------------------------------------------------------# SIGN UP PAGE
#------------------------------------------------------------------------------------------------------------#

###### SIGN UP PAGE ######
@route('/signUp')
def signUp():
    return template('src/html/signUp')

@post('/signUp')
def userSignUp():
    conn = sql.connect('src/db/users.db')#connects database
    c = conn.cursor()
    username = request.forms.get('username') 
    global tableforuser
    tableforuser = username
    password = hashlib.sha512(request.forms.get('password').encode('utf8')).hexdigest() #password hasing for security (using hashlib)
    cur = c.execute('SELECT username FROM user_data WHERE username=?', (username,)) 
    checkUsername = cur.fetchall() # sets the result of SQL query to a varible, str
    now = datetime.now()
    date_created = now.strftime("%d/%m/%Y %H:%M")
    #sets date variable
    if checkUsername != 0:
        #checks whether username is null/eqault to 0 (exists)
        #selects username from user_data table to see if user exists
        table_exists = "SELECT username FROM user_data WHERE username = ?"
        if not conn.execute(table_exists, (tableforuser,)).fetchone(): #checks whether table with username trying to be entered exists
           createTable = f"CREATE TABLE [{tableforuser}](id INTEGER PRIMARY KEY, task char(100) NOT NULL, status bool NOT NULL, date_due TEXT NOT NULL, date_created TEXT NOT NULL)"
           insertTable = f"INSERT INTO [{tableforuser}](task,status,date_due,date_created) VALUES ('This is your first database entry, {tableforuser}',0,'Never','{date_created}')"
           time.sleep(1.5)
           #fixes issues with database being locked
           conn.execute(createTable)
           time.sleep(1.5)
           conn.execute(insertTable)       
        conn.execute("INSERT INTO user_data (username, password) VALUES (?, ?)", (username, password))
        #commts username and hashed password data to user_data table
        conn.commit()
        conn.close()
        #commits data to file and closes sqlite connection
        redirect('/loginPage')
    else: #if error occurs
        signuperror = "There was an error with creating user with name {}".format(username)
        return template('src/html/index.html', message1=signuperror,message2='',message3='',username='')
###### SIGN UP PAGE ######


#------------------------------------------------------------------------------------------------------------#
# STATIC FILEPATH--------------------------------------------------------------------------------------------# STATIC FILEPATH
#------------------------------------------------------------------------------------------------------------#

###### IMPORT CSS / JAVASCRIPT #######
@route('/static/<filepath:path>')
def load_static(filepath):
    #allows program to access static files such as Cascading Stylsheets, Javascript Files and images, etc
    return static_file(filepath, root='C:/Users/liamg/Desktop/Actual Code/src/html/static')

###### IMPORT CSS / JAVASCRIPT #######

#------------------------------------------------------------------------------------------------------------#
# DEFAULT ROUTE----------------------------------------------------------------------------------------------# DEFAULT ROUTE
#------------------------------------------------------------------------------------------------------------#

###### INDEX ROUTE ######
@route('/')
def home_page(): 
    loginstatus = request.get_cookie("loginstatus") #accesses cookie "loginstatus"
    if loginstatus == True: #cookie based routing
        loginTrue = 'True'
        #^sets loginstatus message to true
        #^^fixes issue with login status being long string of letters/numbers
        return template('src/html/index.html',loginstatus=loginTrue,message2='',message3='',username='',message1='')
    return template('src/html/index.html',loginstatus='No User Logged In',message2='',message3='',username='',message1='')
    
    
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
    loginstatus = request.get_cookie("loginstatus")
    username = request.get_cookie("user_id") 
    print(loginstatus)
    if loginstatus == "True":
        print("Login status is true, continuing to todo list page")
        if request.GET.save:
            edit = request.GET.task.strip()
            status = request.GET.status.strip()

            if status == 'open':
                status = 1
            else:
                status = 0

            conn = sql.connect('src/db/users.db')#connects database
            c = conn.cursor()
            update = f'''UPDATE [{username}] SET task = ?, status = ? WHERE id LIKE ?'''
            c.execute(update, (edit, status, no))
            conn.commit()
            itemupdated="The Selected Item No#{} has been updated".format(no)
            return template('src/html/index.html', loginstatus=loginstatus, message1=itemupdated,message2='',message3='',username='', no=no)
        else:
            conn = sql.connect('src/db/users.db')#connects database
            c = conn.cursor()
            select = f'''SELECT task FROM [{username}] WHERE id LIKE ?'''
            c.execute(select, (no,))
            cur_data = c.fetchone()
            item_invalid="The Selected Item No#{} does not exist".format(no)
            if not cur_data:
                return template('src/html/index.html', loginstatus=loginstatus, message1=item_invalid,message2='',message3='',username='')
        return template('src/html/edit_task.html', old=cur_data, no=no)
    else:
        print("Login status is false, redirecting to login status page")
        redirect('/loginstatus')
    
    
###### EDIT ITEM (INT) ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR PAGE FOR USER TO CHOOSE WHAT ITEM TO EDIT--------------------------------------------------# EDIT SELECTOR
#------------------------------------------------------------------------------------------------------------#

####### PRELIMINARY EDIT ######
@route('/edit/editSelect')
def uEditChoice():
    loginstatus = request.get_cookie("loginstatus")
    username = request.get_cookie("user_id") 
    print(loginstatus)

    if loginstatus == "True":
        print("Login status is true, continuing to edit select page")
        output = template('src/html/editSelect.html')
        return output
    else:
        print("Login status is false, redirecting to login status page")
        redirect('/loginstatus')

  
####### PRELIMINARY EDIT ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION  PAGE FOR USER TO CHOOSE TO DELETE ALL ITEMS OR DELETE ONE ITEM--------------------------------# DELETE SELECT SELECTOR
#------------------------------------------------------------------------------------------------------------#

@route('/deleteQ')
def delete_query():
    loginstatus = request.get_cookie("loginstatus")
    username = request.get_cookie("user_id") 
    print(loginstatus)
    if loginstatus == "True":
        print("Login status is true, continuing to delete q page")
        output = template('src/html/deleteQ.html')
        return output
    else:
        print("Login status is false, redirecting to login status page")
        redirect('/loginstatus')
        

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION OR USER TO DELETE ALL ITEMS-------------------------------------------------------------------# DELETE ALL
#------------------------------------------------------------------------------------------------------------# 

##### DELETE ALL ITEMS ####
@route('/deleteAllitems')
def deleteALLitems():
    loginstatus = request.get_cookie("loginstatus")
    username = request.get_cookie("user_id") 

    if loginstatus == "True":
        print("Login status is true, continuing to todo list page")
        if request.GET.save: #> user confirms delete all items
            conn = sql.connect('src/db/users.db')#connects database
            c = conn.cursor()
            result = c.fetchall() #fetches all items
            deleteall = f'''DELETE FROM [{username}]''' #deletes all items in table
            c.execute(deleteall) #executes 'deleteall'
            conn.commit()
            c.close() #commits to database and closes

            if not result: #checks whether there are items in table
                noitemsindatabase = "There are currently no entries in the database"
                return template('src/html/index.html', loginstatus=loginstatus,message1=noitemsindatabase,message2='',message3='',username='')
            deleteallitemsuccess="Successfully deleted all items in database"
            return template('src/html/index.html', loginstatus=loginstatus, message1=deleteallitemsuccess,message2='',message3='',username='')
        else:
            return template('src/html/deleteAllitems')
    elif loginstatus == "False":
        print("Login status is false, redirecting to login status page")
        redirect('/loginstatus')

    

##### DELETE ALL ITEMS ####

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR USER TO DELETE SPECIFIC ITEM---------------------------------------------------------------# DELETE
#------------------------------------------------------------------------------------------------------------#

###### DELETE ITEM ######
@route('/delete/<no:int>')
def delete(no):
    loginstatus = request.get_cookie("loginstatus")
    username = request.get_cookie("user_id") 

    if loginstatus == "True":
        print("Login status is true, continuing to todo list page")
        if request.GET.save:
            status = request.GET.status.strip()

            if status == 'Confirm Delete':
                conn = sql.connect('src/db/users.db')#connects database
                c = conn.cursor()
                delete = f'''Delete FROM [{username}] where id = ?'''
                c.execute(delete, (no,))
                conn.commit()
                c.close()
            else:
                delete_failure="Unable to delete selected item No#{}".format(no)
                return template('src/html/index.html', loginstatus=loginstatus, message1=delete_failure, no=no,message2='',message3='',username='')
            delete_success="Item No#{} successfully deleted"
            return template('src/html/index.html', loginstatus=loginstatus, message1=delete_success, no=no,message2='',message3='',username='')

        else:
            conn = sql.connect('src/db/users.db')#connects database
            c = conn.cursor()
            select = f'''SELECT task FROM [{username}] WHERE id LIKE ?'''
            c.execute(select, (no,)) 
            cur_data = c.fetchone()
            item_invalid="The Selected Item No#{} does not exist".format(no)
            if not cur_data:
                return template('src/html/index.html', loginstatus=loginstatus, message1=item_invalid,message2='',message3='',username='')
            return template('src/html/delete.html', old=cur_data, no=no,message2='',message3='',username='')
    else:
        print("Login status is false, redirecting to login status page")
        redirect('/loginstatus')

    
###### DELETE ITEM ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR PAGE FOR USER TO CHOOSE WHAT ITEM TO DELETE------------------------------------------------# DELETE SELECT
#------------------------------------------------------------------------------------------------------------#

####### PRELIMINARY Delete ######
@route('/delete/deleteSelect')
def uDeleteChoice():
    loginstatus = request.get_cookie("loginstatus")
    username = request.get_cookie("user_id") 
    print(loginstatus)

    if loginstatus == "True":
        print("Login status is true, continuing to todo list page")
        output = template('src/html/deleteSelect.html')
        return output
    else:
        print("Login status is false, redirecting to login status page")
        redirect('/loginstatus')

        
####### PRELIMINARY Delete ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION PAGE FOR USER TO VIEW ITEMS IN todo LIST-------------------------------------------------------# VIEW 
#------------------------------------------------------------------------------------------------------------#

###### VIEW ALL OPEN ITEMS ######
@route('/todo')
def todo_list():

    conn = sql.connect('src/db/users.db')#connects database
    c = conn.cursor()
    loginstatus = request.get_cookie("loginstatus")

    print(loginstatus)
    if loginstatus == "True": #checks whether a user is logged in
        username = request.get_cookie("user_id") 
        #gathers cookie "username" for current userame
        #^allows program to access user-username specific content
        print("Login status is true, continuing to todo list page")
        select_items = f'''SELECT * FROM [{username}]''' #selects user specific content from table
        print(username)
        c.execute(select_items)
        print("Accessing table name {}".format(username))
        result = c.fetchall() #fetches all items in database
        conn.close()
        return template('src/html/make_table', diagnostic=username, rows=result )
    else:
        print("Login status is false, redirecting to login status page")
        conn.close()
        redirect('/loginstatus')
    
###### VIEW ALL OPEN ITEMS ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION PAGE FOR USER TO VIEW CLOSED AND OPEN ITEMS IN todo LIST---------------------------------------# VIEW ALL
#------------------------------------------------------------------------------------------------------------#

@route('/allItems')
def todo_list_all():

    conn = sql.connect('src/db/users.db')#connects database
    c = conn.cursor()
    c.execute("SELECT id, task, status, date_created, date_due FROM todo LIMIT 50") 
    result = c.fetchall()
    
    c.close()
    noitemsindatabase = "There are currently no entries in the database"
    if not result:
        return template('src/html/index.html', loginstatus=loginstatus, message1=noitemsindatabase,message2='',message3='',username='')
    print(result)
    output = template('src/html/ALLitems.html', rows=result)
    return output

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION PAGE FOR USER TO VIEW CLOSED AND OPEN ITEMS IN todo LIST---------------------------------------# VIEW QUERY
#------------------------------------------------------------------------------------------------------------#

@route('/userSelectTodo')
def todo_list_query():
    loginstatus = request.get_cookie("loginstatus")
    username = request.get_cookie("user_id") 

    if loginstatus == "True":
        print("Login status is true, continuing to user select page page")
        output = template('src/html/todoQ.html')
        return output
    else:
        print("Login status is false, redirecting to login status page")
        redirect('/loginstatus')

    

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR USER TO CREATE NEW todo ITEM---------------------------------------------------------------# CREATE 
#------------------------------------------------------------------------------------------------------------#

###### CREATE NEW ITEM ######
@route('/new', method='GET')
def new_item():
    loginstatus = request.get_cookie("loginstatus")# requests login status (true or false)
    username = request.get_cookie("user_id")#requests username 
    print(loginstatus)
    print(username)
    if loginstatus == "True":
        conn = sql.connect('src/db/users.db')#connects database#connects database
        c = conn.cursor()
        if request.GET.save: #if user clicks 'save' button on new task page
            #if rows are less than maximum, continue
                new = request.GET.task.strip()
                date_due = request.GET.date_due.strip()
                #
                now = datetime.now()
                date_created = now.strftime("%d/%m/%Y %H:%M")
                #variable designated for date created, in years, months, days, hrs and minutes
                time.sleep(1)
                insert_data = f'''INSERT INTO [{username}] (task,status,date_due,date_created) VALUES (?,?,?,?)''' 
                #chooses username specific table within database, based on cookie "username"
                time.sleep(1)
                c.execute(insert_data, (new, 1, date_due, date_created))
                new_id = c.lastrowid
                time.sleep(1)
                conn.commit()
                conn.close()
                print("NEw item success")
                return template('src/html/index.html', loginstatus=loginstatus,rows='',message1='Create New Item Success',message2='New Item ID#{}'.format(new_id),message3='',username='')
            ##if rows are over maxmimum, output error message
        else:
            print("returning new task page")
            return template('src/html/new_task.html')
    else:
        print("Login status is false, redirecting to login status page")
        redirect('/loginstatus')
###### CREATE NEW ITEM ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR USER QUERY TO CREATE NEW ITEM -------------------------------------------------------------# CREATE NEW PROMPT
#------------------------------------------------------------------------------------------------------------#

##### MAKE ANOTHER ITEM? #####
@route('/anotheritem')
def makeAnother():
    loginstatus = request.get_cookie("loginstatus")
    username = request.get_cookie("user_id") 
    print(loginstatus)
    
    if loginstatus == "True":
        print("Login status is true, continuing to make another item page")
        return template('src/html/anotheritem.html')
    else:
        print("Login status is false, redirecting to login status page")
        redirect('/loginstatus')

   
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

        conn = sql.connect('src/db/users.db')#connects database
        c = conn.cursor()
        select = f'''SELECT task FROM [{username}] WHERE id LIKE ?'''
        c.execute(select, (item,))
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

    conn = sql.connect('src/db/users.db')#connects database
    c = conn.cursor()
    select = f'''SELECT task FROM [{username}] WHERE id LIKE ?'''
    c.execute(select, (json,))
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

