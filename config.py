import os
basedir = os.path.abspath(os.path.dirname(__file__))

#Tworzy token zabezpieczający użytkownika tokenem własnym, gdyby taki nie istaniał to stałym
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    #Zmienna środowiskowa DATABASE_URL automatyczna lub statyczna app.db z basedir jesli nie znajdzie w
    #Baza danych SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
    #Wysyłanie sygnału przed każdą zmianą w bazie
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #Wysyłanie wiadomości E-mail z błędem, pobieranie wszystkich potrzebnych zmiennych
    #Serwer
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    #Port
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    #TLS
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    #Nazwa Użytkownika
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    #Haslo
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    #Email na który zostanie wysłany email
    ADMINS = ['proxy4848@gmail.com']

    #Paginacja
    POSTS_PER_PAGE = 25