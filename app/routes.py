from flask import render_template
from app import app
from app.forms import LoginForm
from flask import flash, redirect, url_for
from flask_login import current_user, login_user
from app.models import User
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm
from datetime import datetime
from app.forms import EditProfileForm
from app.forms import EmptyForm
from app.forms import PostForm
from app.models import Post
from app.forms import ResetPasswordRequestForm
from app.email import send_password_reset_email
from app.forms import ResetPasswordForm




#Funkcje wyświetlające elementy na stronie

#Zapisywanie last seen użytkownika zanim złoży jakiekolwiek żądanie
#Executed before view functions
@app.before_request
def before_request():
    if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()

#Pod jakim adresem dana rzecz będzie dostępna
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])

#Dodanie tego ustawia, że aby zobaczyć tą stronę należy być zalogowanym
@login_required

#Funckja wywołująca stronę główną
def index():
    
    #Wywołuje formularz dodający posty
    form = PostForm()

    #Jeśli formularz wypełniony prawidłowo
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()

        flash('Your post is now live!')
        return redirect(url_for('index'))
    
    #Posty
    posts = current_user.followed_posts().all()

    
    #Paginacja
    #Zbiera z request numer strony
    page = request.args.get('page', 1, type=int)

    #Wyświetla tylko 3 posty
    posts = current_user.followed_posts().paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    
    ##Next_Url dostanie wartość z url_for wtedy i tylko wtedy jeśli jest na tyle postów by powstało więcej stron
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    
    #Zwracanie strony
    return render_template('index.html', title='Home', form=form,posts=posts.items, next_url=next_url,prev_url=prev_url)


#Pod adresem /login będzie dostępny formularz i deklaruje używane metody, default to GET
@app.route('/login', methods=['GET', 'POST'])

#Funkcja wywołująca logowanie
def login():

    #Sprawdza czy użytkownik jest już zautoryzowany 
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    #Wywołuje formularz LoginForm z pliku forms
    form = LoginForm()

    #Validate_on_submit() sprawdza metodę jeśli GET to pomija kod, zwracając FALSE, jeśli POST to zbiera dane i wykonuje kod w środku zwracając TRUE  
    if form.validate_on_submit():

        #Niech user to wyszukiwanie w bazie username takiego jak podany w formularzu i wybranie pierwszego wyniku
        user = User.query.filter_by(username=form.username.data).first()

        #Sprawdzanie jeśli podany użytkownik istnieje lub czy podane hasło się zgadza
        if user is None or not user.check_password(form.password.data):

            #Zapisuje w pamięci podręcznej dane lub tu wiadomość error użyte w Formularzu
            # flash('Login requested for user {}, remember_me={}'.format(
            # form.username.data, form.remember_me.data))
            flash('Invalid username or password')
            #Zwraca przekierowanie do strony z logowaniem od nowa
            return redirect(url_for('login'))
        
        #Jeśli się zgadza loguje użytkownika i go zapamiętuje jeśli tak chciał user 
        login_user(user, remember=form.remember_me.data)
        
        #Następna strona przy forced login
        #Zbiera konkretne żądanie użytkownika po logowaniu, żeby wiedzieć na którą stronę go z powrotem wrzucić po wymuszonym logowaniu
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

        #Przekierowywuje do strony głównej
        return redirect(url_for('index'))
    
    #Wywołuje template login.html
    return render_template('login.html', title='Sign In', form=form)


#Wylogowanie
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index')) 


#Rejestracja
@app.route('/register', methods=['GET', 'POST'])
def register():
    #Jeśli już zalogowany to główna
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    
    if form.validate_on_submit():

        #Dodawanie użytkownika
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        #Message
        flash('Congratulations, you are now a registered user!')
        
        #Do zaloguj
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


#Profile
@app.route('/user/<username>')
@login_required


def user(username):

    #Wyszukuję użytkownika jeśli nie istnieje to błąd 404
    user = User.query.filter_by(username=username).first_or_404()

    #Kradnie numer strony z żądania
    page = request.args.get('page', 1, type=int)

    #Wyświetla posty i je paginuje
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form)



#Edycja Profilu
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required

def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():

        #Ustawia username użytkownika i jego pole O mnie
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        
        #Zapisuje i powiadamia o zmianach
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', username = current_user.username))
    
    #To samo ale dla metody GET
    elif request.method == 'GET':

        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    #Zwracanie, wywołanie strony, template z formularzem
    return render_template('edit_profile.html', title='Edit Profile', form=form)


#Followowanie
@app.route('/follow/<username>', methods=['POST'])
@login_required

 
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
       
        #Wyszukuje użytkownika
        user = User.query.filter_by(username=username).first()
        if user is None:
            
            #Jeśli nie znalazło  
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        
        #Jeśli próba samego siebie
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        
        #Jeśli poprawnie
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


#Unfollowowanie 
@app.route('/unfollow/<username>', methods=['POST'])
@login_required
  
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        
        #Wyszukuje użytkownika
        user = User.query.filter_by(username=username).first()
        
        #Jeśli nie znajdzie
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        
        #Jeśli siebie samego
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        
        #Jeśli poprawnie
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


#Explore Page
@app.route('/explore')
def explore():
    #Paginacja
    #Zbiera numer strony z requestu
    page = request.args.get('page', 1, type=int)

    #Wyświetla określoną ilośc postów
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    
    #Next_Url dostanie wartość z url_for wtedy i tylko wtedy jeśli jest na tyle postów by powstało więcej stron
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    
    #Zwracanie
    return render_template("index.html", title='Explore', posts=posts.items,
                          next_url=next_url, prev_url=prev_url)

# has_next: True if there is at least one more page after the current one
# has_prev: True if there is at least one more page before the current one
# next_num: page number for the next page
# prev_num: page number for the previous page


#Mail resetowania hasła
@app.route('/reset_password_request', methods=['GET', 'POST'])

def reset_password_request():

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)

        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    
    return render_template('reset_password_request.html', title='Reset Password', form=form)


#Resetowanie hasła
@app.route('/reset_password/<token>', methods=['GET', 'POST'])

def reset_password(token):

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    user = User.verify_reset_password_token(token)

    if not user:
        return redirect(url_for('index'))
    
    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()

        flash('Your password has been reset.')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', form=form)