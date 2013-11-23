# -*- coding: utf-8 -*-
# Basado en Flaskr de by Armin Ronacher.

from sqlite3 import dbapi2 as sqlite3
from flask.ext.bootstrap import Bootstrap
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack

# configuration
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
Bootstrap(app)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        sqlite_db = sqlite3.connect(app.config['DATABASE'])
        sqlite_db.row_factory = sqlite3.Row
        top.sqlite_db = sqlite_db

    return top.sqlite_db


@app.teardown_appcontext
def close_db_connection(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select id, title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/noticias/<int:entry_id>')
def show_entry(entry_id):
    db = get_db()
    cur = db.execute('select id, title, text from entries where id = ?', [entry_id])
    entry = cur.fetchone()
    return render_template('show_entry.html', entry=entry)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/mensajes', methods=['GET', 'POST'])
def add_message():
    #if not session.get('logged_in'):
    #    abort(401)
    db = get_db()
    if request.method == 'POST':
        db.execute('insert into messages (name, email, message) values (?, ?, ?)',
                 [request.form['name'], request.form['email'], request.form['message']])
        db.commit()
        cur = db.execute('SELECT COUNT(*) FROM messages')
        session['message_count'] = cur.fetchone()[0]
        flash('Su mensaje ha sido enviado. Se le contactará a la brevedad.')
    else:
        cur = db.execute('SELECT id, name, email, message from messages order by id desc')
        messages = cur.fetchall()
        return render_template('messages.html', messages=messages)

    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            db = get_db()
            cur = db.execute('SELECT COUNT(*) FROM messages')
            session['logged_in'] = True
            session['message_count'] = cur.fetchone()[0]
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/sedes/<string:sede>')
def sedes_static(sede):
    return render_template('sedes.html', sede=sede)    

@app.route('/convenios')
def convenios_static():
    return render_template('convenios.html')

@app.route('/admision')
def admision_static():
    return render_template('sedes.html')
#    return render_template('admision.html')


@app.template_filter('shorten')
def shorten_filter(s):
    return s[0:97] + "..."

if __name__ == '__main__':
    init_db()
    app.run()
