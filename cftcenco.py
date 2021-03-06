# -*- coding: utf-8 -*-
# Basado en Flaskr de by Armin Ronacher.

from sqlite3 import dbapi2 as sqlite3
from flask.ext.bootstrap import Bootstrap
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack

# configuration
DATABASE   = 'cenco.db'
DEBUG      = True
SECRET_KEY = '06bd432afb9bf5895ba330a734739aba'
USERNAME   = 'cftcenco'
PASSWORD   = '941c424545d4'

# create our little application :)
app = Flask(__name__)
Bootstrap(app)
app.config.from_object(__name__)
app.config.from_envvar('CENCO_SETTINGS', silent=True)


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
    cur = db.execute('select id, title, text, image from entries order by id desc')
    entries = cur.fetchall()
    add_visit()
    return render_template('show_entries.html', entries=entries)

@app.route('/noticias/<int:entry_id>')
def show_entry(entry_id):
    db = get_db()
    cur = db.execute('select id, title, text, image, reference from entries where id = ?', [entry_id])
    entry = cur.fetchone()
    return render_template('show_entry.html', entry=entry)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('INSERT into entries (title, text, image, reference) values (?, ?, ?, ?)',
                 [request.form['title'], request.form['text'], request.form['image'], request.form['reference']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/mensajes', methods=['GET', 'POST'])
def messages():
    #if not session.get('logged_in'):
    #    abort(401)
    db = get_db()
    if request.method == 'POST':
        db.execute('insert into messages (name, email, message, location) values (?, ?, ?, ?)',
                 [request.form['name'], request.form['email'], request.form['message'], request.form['location']])
        db.commit()
        cur = db.execute('SELECT COUNT(*) FROM messages where read = 0')
        session['message_count'] = cur.fetchone()[0]
        flash('Su mensaje ha sido enviado.')
    else:
        cur = db.execute('SELECT id, name, email, message, location from messages where read = 0 order by id desc')
        unread = cur.fetchall()
        cur = db.execute('SELECT id, name, email, message, location from messages where read = 1 order by id desc')
        read = cur.fetchall()
        return render_template('messages.html', unread=unread, read=read)

    return redirect(url_for('show_entries'))

@app.route('/mensajes/<int:entry_id>/archivar', methods=['GET'])
def archive_message(entry_id):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('update messages set read = 1 where id = ?', [ entry_id ] )
    db.commit()
    cur = db.execute('SELECT COUNT(*) FROM messages where read = 0')
    session['message_count'] = cur.fetchone()[0]
    return redirect(url_for('messages'))


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
            cur = db.execute('SELECT COUNT(*) FROM messages where read = 0')
            session['logged_in'] = True
            session['message_count'] = cur.fetchone()[0]
            flash( 'You were logged in' )
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/sedes/<string:sede>')
def sedes_static(sede):
    return render_template('sedes/'+ sede +'.html', sede=sede)

@app.route('/articulos/<string:articulo>')
def articulos_static(articulo):
    return render_template('articulos/'+ articulo +'.html', articulo=articulo)

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

def get_value(name):
    db = get_db()
    cur = db.execute('SELECT value FROM stats where name = ?', [name])
    return cur.fetchone()[0]

def set_value(name, value):
    db = get_db()
    cur = db.execute('UPDATE stats set value = ? where name = ?', [value, name])
    db.commit()

def add_visit():
    db = get_db()
    visits = get_value('visits')
    set_value('visits', visits + 1)

@app.context_processor
def visits():
    return dict(visits=get_value('visits'))

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0")
