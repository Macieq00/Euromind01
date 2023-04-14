from flask import Flask
from flask_login import LoginManager
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment



app = Flask(__name__)
#Mail support
mail = Mail(app)
#Flask-login
login = LoginManager(app)
#Wywołuje plik konfiguracyjny z tokenem
app.config.from_object(Config)
#Bazy danych
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#Bootstrap
bootstrap = Bootstrap(app)
#Timezones
moment = Moment(app)

#Wymuszanie logowania i logowanie
login = LoginManager(app)
#Wartość to nazwa funkcji do wywołania z routes.py
login.login_view = 'login'

#Importuje funkcje wyświetlające i adresy oraz modele i errory
from app import routes, models, errors

#Wysłanie Maila z błędem

#Jeśli aplikacja nie działa w trybie debugowania
if not app.debug:
    #Jeśli jest serwer poczty
    if app.config['MAIL_SERVER']:
        auth = None
        #Jeśli jest nazwa i hasło użytkownika
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        #Jeśli jest TLS
        if app.config['MAIL_USE_TLS']:
            secure = ()
        
        #Wysyła maila
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    #Jeśli są logi do zapisanaia to je zapisze w microblog.log w folderze logs
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    #Ścieżka pliku, rozmiar, ile logów na backup
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    
    #Jak będzie wyglądać log
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    
    #Właściowści
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')