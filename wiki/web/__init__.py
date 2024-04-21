import os
import sqlite3
from datetime import datetime

from flask import current_app
from flask import Flask
from flask import g
from flask_login import LoginManager
from werkzeug.local import LocalProxy

import config
from wiki.core import Wiki
from wiki.web.user import UserManager


class WikiError(Exception):
    pass


def get_wiki():
    wiki = getattr(g, '_wiki', None)
    if wiki is None:
        wiki = g._wiki = Wiki(current_app.config['CONTENT_DIR'])
    return wiki


current_wiki = LocalProxy(get_wiki)


def get_users():
    users = getattr(g, '_users', None)
    if users is None:
        users = g._users = UserManager(current_app.config['USER_DIR'])
    return users


current_users = LocalProxy(get_users)


def create_app(directory):
    app = Flask(__name__)
    app.config['CONTENT_DIR'] = directory
    app.config['TITLE'] = 'wiki'
    try:
        app.config.from_pyfile(
            os.path.join(app.config.get('CONTENT_DIR'), 'config.py')
        )
    except IOError:
        msg = "You need to place a config.py in your content directory."
        raise WikiError(msg)

    loginmanager.init_app(app)

    from wiki.web.routes import bp
    app.register_blueprint(bp)

    initialize_db(app)

    return app


loginmanager = LoginManager()
loginmanager.login_view = 'wiki.user_login'


@loginmanager.user_loader
def load_user(name):
    return current_users.get_user(name)


def initialize_db(app):
    """
    This method initializes the SQLite database to store Wiki page history.
    """
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS wiki_pages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT NOT NULL,
                        version INTEGER,
                        content TEXT NOT NULL,
                        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        author TEXT NOT NULL,
                        approved BOOLEAN DEFAULT FALSE
    )''')

    if not page_exists("home"):
        home_page = (
        1, 'home', 1, 'title: Main tags: interesting World [[hello|abc]] [[world|world]] aaa bruh', datetime.now(),
        'sam', True)
        test_page = (2, 'testing', 1, 'title: Testing tags: testing Testing stuff here!', datetime.now(), 'sam', True)

        # Just for testing purposes (to reinitialize the table)
        cursor.execute('''INSERT INTO wiki_pages VALUES (?, ?, ?, ?, ?, ?, ?)''', home_page)
        cursor.execute('''INSERT INTO wiki_pages VALUES (?, ?, ?, ?, ?, ?, ?)''', test_page)

    # Init User History Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            url TEXT NOT NULL,
                            date_last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            count_accessed INTEGER NOT NULL,
                            user TEXT NOT NULL
        )''')

    conn.commit()
    conn.close()


def page_exists(query):
    conn = sqlite3.connect(config.DATABASE)
    cursor = conn.cursor()
    db_query = '''SELECT *
                FROM wiki_pages
                WHERE url = '%s\'''' % (query,)
    cursor.execute(db_query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    if not data:
        return False
    return True