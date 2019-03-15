import os
import sqlite3

from flask import(Flask, request, session, g, redirect,
url_for, abort, render_template, flash)

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY=os.urandom(16),
    USERNAME='admin',
    PASSWORD='default'
)

#app.config.from_envar('FLASKR_SETTINGS', silent=True)

def connect_db():
    '''Connects to the specific database.'''

    con = sqlite3.connect(app.config['DATABASE'])
    con.row_factory = sqlite3.Row
    return con

'''Incase the system is not equiped with sqlite3 command. This function 
   the database'''
def init_db():
    db = get_db()

    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

    db.commit()


@app.cli.command('initdb')
def initdb_command():
    '''Initializes the database.'''

    init_db()
    print('Initialized the database.')

def get_db():
    '''Opens a new database connection if there 
    is none yet for the current application context'''
  #  if not hasattr(g, 'sqlite_db'):
    g.sqlite_db = connect_db()
    return g.sqlite_db

#@app.teardown_appcontext
#def close_db(error):
    '''closes the db again at the end f the request'''
#    if hassattr(g, 'sqlite_db'):
 #       g.sqlite_db.close()

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        if not session.get('logged_in'):
            abort(401)
        db = get_db()
        db.execute('insert into entries (title, text) values (?, ?)',
                [request.form['title'], request.form['text']])
        db.commit()
        flash('New entry was successfully posted')
        return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error=None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run(debug=True)
