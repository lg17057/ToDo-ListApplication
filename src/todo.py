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

class openDB():
    def __init__(self, file_name):
        self.obj = sql.connect(file_name)
        self.cursor = self.obj.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, value, traceback, type):
        time.sleep(1)
        self.obj.commit()
        self.obj.close()


class userLoggedin:
    def __enter__(self):
        status = request.get_cookie("loginstatus")
        if status == "True":
            return 
        else:
            redirect('/loginstatus')

    def __exit__(self, type, value, traceback):
        return
        

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR LOGIN PAGE---------------------------------------------------------------------------------# LOGIN PAGE
#------------------------------------------------------------------------------------------------------------#


@route('/loginPage')
def login():
    loginstatus = request.get_cookie("loginstatus")
    if loginstatus == "False":
        return template('src/html/loginPage.html', loginstatus=loginstatus)
    else:
        username = request.get_cookie("username")
        loginstatus="True"
        return template('src/html/loginSuccess.html',message1='',message2='',message3='',  loginmessage="You are already logged in.", loginstatus=loginstatus)

@route('/loginPage', method='POST')
def do_login():
    with openDB('src/db/users.db') as c:
        loginstatus = request.get_cookie('loginstatus')
        if loginstatus == "False":
            global username
            username = request.forms.get('username') #accesses username entered on login page
            password = hashlib.sha512(request.forms.get('password').encode('utf8')).hexdigest() #hashed password

            #if password == key[0]: #checks whether user inputted password is equal to existing password
            if username == "adminkey":
                response.set_cookie("loginstatus", value="True")
                response.set_cookie("admin", value="True")
                response.set_cookie("user_id", username)
                loginstatus = "True"
                return template('src/html/loginSuccess.html', message1='Logged in with admin credentials', message2='', message3='', loginmessage='', loginstatus=loginstatus)
            else:

                cur = c.execute("SELECT password FROM user_data WHERE username = ?", (username,)) #selects password from user data
                key = cur.fetchone() #fetches one value from table
                if password == None or key == None:
                    response.set_cookie("loginstatus", value="False")
                    #login value/status set to galse
                    loginstatus="False"
                    response.set_cookie("admin", value="False")

                    return template('src/html/loginFailure.html',  loginstatus=loginstatus)

                elif password == key[0]: #checks whether user inputted password is equal to existing password
                    response.set_cookie("loginstatus", value="True")
                    response.set_cookie("user_id", username)
                    #login status  set to True, username set to user entered data (if pasword check successful)
                    response.set_cookie("recent", value="No new items created")
                    num=0
                    response.set_cookie("recentnum", value=num, secret='secretkey' )
                    loginstatus="True"
                    response.set_cookie("admin", value="False")
                    return template('src/html/loginSuccess.html',message1='Accessing User Id {}'.format(username),message2='',message3='', loginmessage="Login to website success.", loginstatus=loginstatus)
                elif password != key[0]:
                #elif password != key[0]: #if user input password is not equal to existing password
                    response.set_cookie("loginstatus", value="False")
                    response.set_cookie("admin", value="False")
                    #login value/status set to galse
                    loginstatus="False"
                    return template('src/html/loginFailure.html', loginstatus=loginstatus)

        else:
            username = request.get_cookie('username')
            loginstatus="True"
            return template('src/html/loginSuccess.html',message1='',message2='',message3='',  loginmessage="You are already logged in with userID {}".format(username), loginstatus=loginstatus)



###### LOGIN PAGE ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION PAGE FOR SETTINGS OR ADMIN  PAGE ---------------------------------------------------------------------#
#------------------------------------------------------------------------------------------------------------#
@route('/settingspage')
def adminpage():
    adminstatus = request.get_cookie("admin")

    if adminstatus == "False":
        loginsess = 'True'
        return template('src/html/accountsettings.html', loginstatus=loginsess, login=loginsess)
    else:
        loginsess = 'True'
        return template('src/html/adminpage.html', loginstatus=loginsess, login=loginsess)

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION PAGE FOR LOGINSTATUS PAGE ---------------------------------------------------------------------#
#------------------------------------------------------------------------------------------------------------#

@route('/loginstatus')
def loginstatus():
    loginstatus = request.get_cookie("loginstatus")
    if loginstatus == "True":
        loginsess = 'True'
    else:
        loginsess='False'
    #page for when user is not logged in
    return template('src/html/logoutstatus.html', loginstatus=loginsess)

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION PAGE FOR USER NOT LOGGED IN MESSAGE -----------------------------------------------------------#
#-----------------------------------------------------------------------------------------------
    
@route('/logout', method=["GET", "POST"])
def logout():
    response.set_cookie("loginstatus", value="False")
    #sets loginstatus to false
    response.set_cookie("user_id", value='')
    #sets user_id/username to blank str
    if loginstatus == "True": #cookie based routing
        loginsess = 'True'
    else:
        loginsess = 'False'
    return template('src/html/logoutSuccess.html', loginstatus=loginsess)
        #sends user to a 401 page with specific message


#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR SIGN UP PAGE-------------------------------------------------------------------------------# SIGN UP PAGE
#------------------------------------------------------------------------------------------------------------#

###### SIGN UP PAGE ######
@route('/signUp')
def signUp():
    loginstatus = request.get_cookie("loginstatus")
    if loginstatus == "False":
        return template('src/html/signUp', loginstatus=loginstatus)
    else:
        username = request.get_cookie('username')
        loginstatus="True"
        return template('src/html/loginSuccess.html',message1='',message2='',message3='',  loginmessage="You are already logged in with userID {}".format(username), loginstatus=loginstatus)

@post('/signUp')
def userSignUp():
    with openDB('src/db/users.db') as c:

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
                if c.execute(table_exists, (tableforuser,)).fetchone(): #checks whether table with username trying to be entered exists
                   return template('src/html/userexists.html', loginstatus="False", message1="User already exists", message2='', message3='')
                elif not c.execute(table_exists, (tableforuser,)).fetchone(): #checks whether table with username trying to be entered exists
                   createTable = f"CREATE TABLE [{tableforuser}](id INTEGER PRIMARY KEY, task char(100) NOT NULL, status bool NOT NULL, date_due TEXT NOT NULL, date_created TEXT NOT NULL)"
                   insertTable = f"INSERT INTO [{tableforuser}](task,status,date_due,date_created) VALUES ('This is your first database entry, {tableforuser}',0,'Never','{date_created}')"
                   time.sleep(1.5)
                   response.set_cookie("recent", value="This is your first database entry, {}".format(tableforuser))

                   #fixes issues with database being locked
                   c.execute(createTable)
                   time.sleep(1.5)
                   c.execute(insertTable)       
                c.execute("INSERT INTO user_data (username, password) VALUES (?, ?)", (username, password))
                #commts username and hashed password data to user_data table

                #commits data to file and closes sqlite connection
                redirect('/loginPage')
        else: #if error occurs
            signuperror = "There was an error with creating user with name {}".format(username)
            return template('src/html/index.html',loginstatus=loginstatus, message1=signuperror,message2='',message3='',username='')
    
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
    loginstatus='False'
    loginstatus = request.get_cookie("loginstatus") #accesses cookie "loginstatus"
    if loginstatus == "True": #cookie based routing
        loginTrue = 'True'
        #^sets loginstatus message to true
        #^^fixes issue with login status being long string of letters/numbers
        return template('src/html/index.html',loginstatus=loginTrue, display1="block", message2='',message3='',username='',message1='')
    return template('src/html/index.html',loginstatus='No User Logged In', display2="none", message2='',message3='',username='',message1='')
    
    
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
    with openDB('src/db/users.db') as c:
        with userLoggedin():
            username = request.get_cookie("user_id") 
            loginsess='True'
            if request.GET.save:
                edit = request.GET.task.strip()
                status = request.GET.status.strip()
                if status == "Incomplete":
                    status = 0
                else:
                    status = 1
                select = f'''SELECT task FROM [{username}] WHERE id LIKE ?'''
                c.execute(select, (no,)) 
                cur_data = c.fetchone()
                update = f'''UPDATE [{username}] SET task = ?, status = ? WHERE id LIKE ?'''
                c.execute(update, (edit, status, no))
                itemupdated="The Selected Item No#{} has been updated".format(no)
                return template('src/html/alteritemsuccess.html', loginstatus=loginsess, message1="Item Value [{}] successfully edited".format(cur_data), no=no,message2="(Item No#{})".format(no),message3='',username='')
            else:
                select = f'''SELECT task FROM [{username}] WHERE id LIKE ?'''
                c.execute(select, (no,))
                cur_data = c.fetchone()
                item_invalid="The Selected Item No#{} does not exist".format(no)
                if not cur_data:
                    loginsess='True'
                    return template('src/html/alteritemsuccess.html', loginstatus=loginsess, message1=item_invalid,message2='',message3='',username='')
            return template('src/html/edit_task.html',loginstatus='True', old=cur_data, no=no)
            
    
    
###### EDIT ITEM (INT) ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR PAGE FOR USER TO CHOOSE WHAT ITEM TO EDIT--------------------------------------------------# EDIT SELECTOR
#------------------------------------------------------------------------------------------------------------#

####### PRELIMINARY EDIT ######
@route('/edit/editSelect')
def uEditChoice():
    with userLoggedin():
        username = request.get_cookie("user_id") 
        loginsess='True'
        recent_item = request.get_cookie("recent")
        recent_num = request.get_cookie("recentnumber",  secret='secretkey')
        output = template('src/html/editSelect.html', recent=recent_item, recentnum=recent_num, loginstatus=loginsess)
        return output
        
  
####### PRELIMINARY EDIT ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION  PAGE FOR USER TO CHOOSE TO DELETE ALL ITEMS OR DELETE ONE ITEM--------------------------------# DELETE SELECT SELECTOR
#------------------------------------------------------------------------------------------------------------#

@route('/deleteQ')
def delete_query():

    with userLoggedin():    
        username = request.get_cookie("user_id")
        output = template('src/html/deleteQ.html', loginstatus='True')
        return output

        

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION OR USER TO DELETE ALL ITEMS-------------------------------------------------------------------# DELETE ALL
#------------------------------------------------------------------------------------------------------------# 

##### DELETE ALL ITEMS ####
@route('/deleteAllitems')
def deleteALLitems():
    with userLoggedin():
        with openDB('src/db/users.db') as c:
            username = request.get_cookie("user_id") 
            if request.GET.save: #> user confirms delete all items

                result = c.fetchall() #fetches all items
                deleteall = f'''DELETE FROM [{username}]''' #deletes all items in table
                c.execute(deleteall) #executes 'deleteall'
                loginsess = 'True'
                if not result: #checks whether there are items in table
                    noitemsindatabase = "There are currently no entries in the database"
                    return template('src/html/index.html', loginstatus=loginsess,message1=noitemsindatabase,message2='',message3='',username='')
                deleteallitemsuccess="Successfully deleted all items in database"
                return template('src/html/alteritemsuccess.html', loginstatus=loginsess, message1=deleteallitemsuccess,message2='',message3='',username='')
            else:
                return template('src/html/deleteAllitems', loginstatus='True')
    

##### DELETE ALL ITEMS ####

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR USER TO DELETE SPECIFIC ITEM---------------------------------------------------------------# DELETE
#------------------------------------------------------------------------------------------------------------#

###### DELETE ITEM ######
@route('/delete/<no:int>')
def delete(no):
    with userLoggedin():
        with openDB('src/db/users.db') as c:
            username = request.get_cookie("user_id") 

            loginsess='True'
            if request.GET.save:
                status = request.GET.status.strip()
                if status == 'Confirm Delete':

                    delete = f'''Delete FROM [{username}] where id = ?'''
                    select = f'''SELECT task FROM [{username}] WHERE id LIKE ?'''
                    c.execute(select, (no,)) 
                    cur_data = c.fetchone()
                    c.execute(delete, (no,))
                else:
                    delete_failure="Unable to delete selected item No#{}".format(no)
                    return template('src/html/index.html', loginstatus=loginsess, message1=delete_failure, no=no,message2='',message3='',username='')
                return template('src/html/alteritemsuccess.html', loginstatus=loginsess, message1="Item Value [{}] successfully deleted".format(cur_data), no=no,message2=" (Item No#{})".format(no),message3='',username='')
            else:
                select = f'''SELECT task FROM [{username}] WHERE id LIKE ?'''
                c.execute(select, (no,)) 
                cur_data = c.fetchone()
                item_invalid="The Selected Item No#{} does not exist".format(no)
                if not cur_data:
                    return template('src/html/index.html', loginstatus=loginsess, message1=item_invalid,message2='',message3='',username='')
                return template('src/html/delete.html', loginstatus=loginsess, old=cur_data, no=no,message2='',message3='',username='')
       

    
###### DELETE ITEM ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR PAGE FOR USER TO CHOOSE WHAT ITEM TO DELETE------------------------------------------------# DELETE SELECT
#------------------------------------------------------------------------------------------------------------#

####### PRELIMINARY Delete ######
@route('/delete/deleteSelect')
def uDeleteChoice():
    with userLoggedin():
        username = request.get_cookie("user_id") 

        loginsess='True'
        recent_item = request.get_cookie("recent")
        recentnum = request.get_cookie("recentnumber", secret='secretkey')
        output = template('src/html/deleteSelect.html',recent=recent_item, recentnum=recentnum, loginstatus=loginsess)
        return output


        
####### PRELIMINARY Delete ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION PAGE FOR USER TO VIEW ITEMS IN todo LIST-------------------------------------------------------# VIEW 
#------------------------------------------------------------------------------------------------------------#

###### VIEW ALL OPEN ITEMS ######
@route('/todo')
def todo_list(): 
    with userLoggedin():   
        with openDB('src/db/users.db') as c:
            loginsess='True'
            username = request.get_cookie("user_id") 
            #gathers cookie "username" for current userame
            #^allows program to access user-username specific content
            select_items = f'''SELECT * FROM [{username}]''' #selects user specific content from table
            c.execute(select_items)
            result = c.fetchall() #fetches all items in database
            if not result:
                noitemsindatabase = "There are currently no entries in the database"
                return template('src/html/index.html', loginstatus=loginsess, message1=noitemsindatabase,message2='',message3='',username='')
            return template('src/html/make_table', loginstatus=loginsess, diagnostic=username, rows=result )

    
###### VIEW ALL OPEN ITEMS ######
    

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR USER TO CREATE NEW todo ITEM---------------------------------------------------------------# CREATE 
#------------------------------------------------------------------------------------------------------------#

###### CREATE NEW ITEM ######
@route('/new', method='GET')
def new_item():
    with userLoggedin():
        with openDB('src/db/users.db') as c:
            username = request.get_cookie("user_id")#requests username 
            loginsess='True'
            if request.GET.save: #if user clicks 'save' button on new task page
                #if rows are less than maximum, continue
                    new = request.GET.task.strip()
                    date_due = request.GET.date_due.strip()
                    now = datetime.now()
                    date_created = now.strftime("%d/%m/%Y %H:%M")
                    #variable designated for date created, in years, months, days, hrs and minutes
                    time.sleep(1)
                    insert_data = f'''INSERT INTO [{username}] (task,status,date_due,date_created) VALUES (?,?,?,?)''' 
                    response.set_cookie("recent", value=new)
                    #chooses username specific table within database, based on cookie "username"
                    time.sleep(1)
                    c.execute(insert_data, (new, 0, date_due, date_created))
                    new_id = c.lastrowid
                    response.set_cookie("recentnumber", value=new_id, secret='secretkey')
                    time.sleep(1)
                    return template('src/html/index.html', loginstatus=loginsess,rows='',message1='Create New Item Success; {}'.format(new),message2='New Item ID#{};'.format(new_id),message3='',username='')
                ##if rows are over maxmimum, output error message
            else:
                return template('src/html/new_task.html', loginstatus=loginsess)

###### CREATE NEW ITEM ######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR USER QUERY TO CREATE NEW ITEM -------------------------------------------------------------# CREATE NEW PROMPT
#------------------------------------------------------------------------------------------------------------#

##### MAKE ANOTHER ITEM? #####
@route('/anotheritem')
def makeAnother():
    with userLoggedin():
        username = request.get_cookie("user_id") 
        loginsess = 'True'
        return template('src/html/anotheritem.html', loginstatus=loginsess)
    

   
#### MAKE ANOTHER ITEM? #####

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR PAGE ABOUT ME -----------------------------------------------------------------------------# ABOUT ME
#------------------------------------------------------------------------------------------------------------#

####### ABOUT ME PAGE #######
@route('/aboutMe')
def about_me():
    
    output = template('src/html/about_me.html', loginstatus=loginsess)
    return output

####### ABOUT ME PAGE #######

#------------------------------------------------------------------------------------------------------------#
# DESIGNATION FOR USER HELP PAGE ----------------------------------------------------------------------------# HELP
#------------------------------------------------------------------------------------------------------------#

####### HELP THING #######
@route('/help')
def help():
   
    output = template('src/html/help.html', loginstatus=loginsess)
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

def loginstatus():
    response.set_cookie("loginstatus", value="False")
    loginsess = "False"


#------------------------------------------------------------------------------------------------------------#
# RUNS THE WEBSITE ------------------------------------------------------------------------------------------# HOST
#---------------
# ---------------------------------------------------------------------------------------------#


loginsess="False"
run(host='127.1.0.1', port=5500, reloader=True, debug=True)
loginstatus()
