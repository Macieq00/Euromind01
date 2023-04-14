#Importuje bazę danych z init
from app import db
#Autoryzacja uzytkownikow
from app import login
#Importowanie UserMixin
from flask_login import UserMixin
from datetime import datetime
#Biblioteka to hashowania haseł
from werkzeug.security import generate_password_hash, check_password_hash
#Gravatar
from hashlib import md5
#Forgot Password
from time import time
import jwt
from app import app

#Followers and Followed, zrobiona w ten sposób przechowuje tylko klucze obce
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

#User
class User(UserMixin, db.Model):

    #Kolumna Id, klucz główny
    id = db.Column(db.Integer, primary_key=True)
    #Kolumna username
    username = db.Column(db.String(64), index=True, unique=True)
    #Kolumna Email
    email = db.Column(db.String(120), index=True, unique=True)
    #Kolumna Hasło w hash, w celu dodatkowego zabezpieczenia
    password_hash = db.Column(db.String(128))

    #Relacja z tabelą Post
    #1. Many, Nowe Pole, Jak
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    #Relacja z Followers i Followed
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    #User - prawa strona relacji, ta sama klasa po obu stronach
    #Secondary - tabela użyta do many-to-many
    #PrimaryJoin - określa konekcje lewej z środkową (wartość przypisuje wartości ID followers)
    #SecondaryJoin - określa konekcje z prawej
    #Backref - jak działa relacja z prawej storny

    #O mnie
    about_me = db.Column(db.String(140))
    #Ostatnie zalogowanie
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    #Jak wyświetlać obiekty klasy User, tabeli
    def __repr__(self):
        #Zwraca User i nazwę użytkownika
        return '<User {}>'.format(self.username)
    
    #Ustawianie hasła hashowanego
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    #Sprawdzanie hasło
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    #Avatary - Gravatar
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    
    #Followowanie
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    #Unfollowowanie
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    #Sprawdza czy już followuje
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    
    #Odnajduje posty followowanych osób
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
    
    #Resetowanie hasła
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')    
    
    #Metoda Statyczna
    #Weryfikowanie tokenu JWT resetowania hasła
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


    

#Posts
class Post(db.Model):

    #Id
    id = db.Column(db.Integer, primary_key=True)
    #Treść
    body = db.Column(db.String(140))
    #Kiedy
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    #Id autora oraz oznaczenie klucza obcego z polem id tabeli User 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #Odpowiedz na zapytanie
    def __repr__(self):
        return '<Post {}>'.format(self.body)  
    

#ID użytkownika przechowywane, żeby serwer wiedział że to ten sam user
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


#Cheat Sheet
# >>> # get all posts written by a user
# >>> u = User.query.get(1)
# >>> u
# <User john>
# >>> posts = u.posts.all()
# >>> posts
# [<Post my first post!>]

# >>> # same, but with a user that has no posts
# >>> u = User.query.get(2)
# >>> u
# <User susan>
# >>> u.posts.all()
# []

# >>> # print post author and body for all posts
# >>> posts = Post.query.all()
# >>> for p in posts:
# ...     print(p.id, p.author.username, p.body)
# ...
# 1 john my first post!

# # get all users in reverse alphabetical order
# >>> User.query.order_by(User.username.desc()).all()
# [<User susan>, <User john>]