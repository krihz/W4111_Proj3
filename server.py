
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
import datetime
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash, session
from flask_sqlalchemy import SQLAlchemy

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
#db = SQLAlchemy(app)

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@35.243.220.243/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@35.243.220.243/proj1part2"
#   35.231.103.173
DATABASEURI = "postgresql://hh2816:5783@35.231.103.173/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#

# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def login():
	return render_template('Register.html')



@app.route('/login', methods=['POST'])
def home():
    username = request.form['username']
    password = request.form['pwd']
    result = g.conn.execute("SELECT password FROM Register WHERE username = username", {'username': username}) 
    result = result.first()[0]
    if result is None:
        flash('wrong username!')
        return render_template('Register.html')
    if password == result:
        session['username'] = request.form['username']
        session['logged_in'] = True
        return render_template('index.html')
    elif password != result:
        flash('wrong password!')
        return render_template('Register.html')

def getTime():
    utc = datetime.datetime.utcnow()
    return utc


@app.route('/Forum', methods=['POST'])
def Forum():
  name = request.form['name']
  name = '%' + name + '%'
  if (name != ''):
    cursor =  g.conn.execute("SELECT topic, theme, content,date_time FROM Forums WHERE topic LIKE %(name)s", {'name': name}) 
    names = []
    names.append(["Topic", "Theme", "Content","Date_Time"])
    for result in cursor:
      names.append(result)
    cursor.close()
    context = dict(data = names)

  else:
    names = []
    context = dict(data = names)

  return render_template("index.html", **context)

@app.route('/Meal', methods=['POST'])
def Meal():
  name = request.form['name']
  name = datetime.datetime.strptime(name, '%Y-%m-%d %H:%M:%S')
  username = session.get('username')
  # name = name + '%'
  if (name != ''):
    cursor =  g.conn.execute('select Meal_Diary.name, Meal_Diary.type, Meal_Diary.date_time from Meal_Diary, Register where Meal_Diary.creator_id = Register.id and Register.username = %(username)s and Meal_Diary.date_time = %(name)s',{'name': name,'username': username}) 
    names = []
    # names.append(["Name", "Type", "Date_Time"])
    for result in cursor:
      names.append(result)
    cursor.close()
    context = names

  else:
    names = []
    context = names
  context = context[0]
  return render_template("index.html", **context)

@app.route('/Food_calorie', methods=['POST'])
def Food_calorie():
  name = request.form['name']
  name = '%' + name + '%'
  if (name != ''):
    cursor =  g.conn.execute("SELECT food_name,calories,protein,fat FROM Food_Database WHERE food_name LIKE %(name)s", {'name': name}) 
    names = []
    names.append(["Food_Name", "Calories", "Protein","Fat"])
    for result in cursor:
      names.append(result)
    cursor.close()
    context = dict(data = names)
  else:
    names = []
    context = dict(data = names)

  return render_template("index.html", **context)

@app.route('/Exercise', methods=['POST'])
def Exercise():
  name = request.form['name']
  username = session.get('username')
  name = name + '%'
  if (name != ''):
    cursor =  g.conn.execute("SELECT Exercise_Diary.exercise_name, Exercise_Diary.calories, Exercise_Diary.date_time FROM Exercise_Diary, Register WHERE Exercise_Diary.id =Register.id and Register.username = %(username)s and TO_CHAR(Exercise_Diary.date_time) LIKE %(name)s", {'name': name,'username':username}) 
    names = []
    names.append(["Exercise_Name", "Calories", "Date_Time"])
    for result in cursor:
      names.append(result)
    cursor.close()
    context = dict(data = names)

  else:
    names = []
    context = dict(data = names)

  return render_template("index.html", **context)

@app.route('/add_exercise', methods=['POST'])
def add_exercise():
  e_name = request.form['e_name'] # exercise_name
  c = request.form['c'] # calories
  time = request.form['time'] # date_time
  username = session.get('username') # username
  u_id = g.conn.execute("SELECT ID FROM register WHERE username =  username",{'username':username}) # id
  e_id = g.conn.execute("SELECT max(exercise_id) FROM exercise_diary") + 1 # exercise_id
  cmd = "INSERT INTO Exercise_Diary(exercise_id,exercise_name,calories,date_time,id) VALUES (%s,%s,%s,%s,%s);"
  g.conn.execute(cmd,e_id,e_name,c,time)
  return redirect('/index.html')

@app.route('/add_meal', methods=['POST'])
def add_meal():
  t = request.form['t'] # type
  time = request.form['time'] # date_time
  name = request.form('name') # meal name
  f_name = request.form('f_name') # food name
  f_id = g.conn.execute("SELECT food_id FROM food_database WHERE food_name LIKE %f_name%",{'f_name':f_name})
  number = request.form('name') # food number
  username = session.get('username') # username
  c_id = g.conn.execute("SELECT ID FROM register WHERE username =  username",{'username':username}) # creator_id
  # check if new meal
  old_meal = g.conn.execute("SELECT meal_id FROM Meal_Diary WHERE date_time =  time",{'time':time})
  if(old_meal != ''):
      m_id = g.conn.execute("SELECT max(meal_id) FROM exercise_diary") + 1
      cmd1 = "INSERT INTO meal_diary(meal_id,type,date_time,name,creator_id) VALUES (%s,%s,%s,%s,%s);"
      g.conn.execute(cmd1,m_id,t,time,name,c_id)
  else:
      m_id = old_meal

  cmd2 = "INSERT INTO Make_Meal(meal_id,food_id,number) VALUES (%s,%s,%s);"
  g.conn.execute(cmd2,m_id,f_id,number)
  return redirect('/index.html')

@app.route('/add_food', methods=['POST'])
def add_food():
  f_name = request.form['f_name']
  c = request.form['c'] # calorie
  p = request.form['p'] # protein
  f = request.form['f'] # fat
  u_name = session.get('username')
  c_id = g.conn.execute("SELECT ID FROM register WHERE username =  u_name",{'u_name':u_name})
  f_id = g.conn.execute("SELECT max(food_id) FROM exercise_diary") + 1
  cmd = "INSERT INTO Exercise_Diary(food_id,food_name,calories,protein,fat,creator_id) VALUES (%s,%s,%s,%s,%s,%s);"
  g.conn.execute(cmd,f_id,f_name,c,p,f,c_id)
  return redirect('/index.html')


@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        result = g.conn.execute("SELECT * FROM Register WHERE username = \'%s\'" %(request.form['username']))
        user_id = g.conn.execute("SELECT max(id) FROM Register") +1
      
        if result.rowcount > 0:
            flash("Username Taken")
            return render_template('Newuser.html')  
        else:  
            g.conn.execute("INSERT INTO Register (id, first_name, last_name, username,email,password) VALUES (%s,\'%s\', \'%s\', \'%s\', \'%s\', %s);" %(user_id, request.form['First_Name'], request.form['Last_Name'], request.form['Username'],request.form['Email'],request.form['Password']))
            session['username'] = request.form['Username']
            session['logged_in'] = True	
            return home()
        
    else:
        return render_template('Newuser.html')
		    
		


# @app.route('/login')
# def login():
#     abort(401)
#     this_is_never_executed()


if __name__ == "__main__":
  app.secret_key = 'super secret key'
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
