import sqlite3
from bottle import (several different features)


route(/static/<filepath:path>)
^^^
allows for css and js file routing


@route('/')
^^^
given route for home page
returns index.html file for page


@route('/delete')
^^^
given route for delete page
if/else statement for user to delete items


@route('/todo')
^^^
given route for viewing todo list page
program to fetch data and output table


@route('loginPage')
^^^
given route for login page 
returns loginPage html file


@route('signUp')
^^^
given route for sign up page
returns signUp page html file


@route('new')
^^^
given route for user to create new item
function new_item()
inserts item into database
returns new_task html file


@route('/delete/deleteSelect')
^^^
given route for user to choose which item to delete
returns deleteSelect html file


@route('/edit/editSelect')
^^^ 
given route for user to choose which item to edit 
returns editSelect html file


@route('/edit/<no:int>')
^^^
given route for user to edit an item of specific value
function fetchin data and commiting data overwriting
or
setting 1 to 0, making item complete and not visible in /todo
returns edit_task html file


@route('/aboutMe')
^^^
given route for page about me
returns html file 'aboutMe'


@route('help')
^^^ 
given route for help page
returns html file 'help'


@error403
^^^
given route for 403 error catching 
returns 403 html file


@error404
^^^
given route for 404 error catching
returns 404 html file


@route('loadPage')
^^^
given route for loading page
returns loadpage html file