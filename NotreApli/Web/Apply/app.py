# All imports :
from flask import Flask
from flask_script import Manager
import os.path
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__) # create an instance of the Flask class for our web app
app.debug = True # set debug to "True" to print out possible Python errors on the web page
Bootstrap(app) # load Bootstrap to use new templates

manager = Manager(app)

def mkpath(p):
    return os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            p))

app.config['SQLALCHEMY_DATABASE_URI']=( #config the database which will be used in the app
    'sqlite:///'+mkpath('../tuto.db'))
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

db=SQLAlchemy(app) # get the database from the app and put it in db

app.config['SECRET_KEY']="f80e3c9d-4229-4e14-a302-7b624a52f6eb" # config the SECRET_KEY

login_manager = LoginManager(app) # To start using Flask-Login in our application we need to create
                                # an instance of LoginManager and initialize it with our application instance

login_manager.login_view = "login" # This will redirect users to the login view whenever they are required to be logged in
