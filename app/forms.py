from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


#Logowanie
class LoginForm(FlaskForm):

    #Pole nazwy użytkownika, etykieta lub opis, walidacja czy pole może być puste
    #String zwykłe tekstowe
    username = StringField('Username', validators=[DataRequired()])
    #Ukryte pole tekstowe na hasło
    password = PasswordField('Password', validators=[DataRequired()])
    #Checkbox
    remember_me = BooleanField('Remember Me')
    #Zatwierdź
    submit = SubmitField('Sign In')


#Rejestracja
class RegistrationForm(FlaskForm):
    #Pola formularza
    username = StringField('Username', validators=[DataRequired()])
    #Email() sprawdza czy struktura maila sie zgadza 
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    #Sprawdza czy hasla sa zgodne equalto(pole)
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    #Szuka czy juz taki istnieje
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    #Szuka czy jest juz taki adres
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
        
#Edycja profilu
class EditProfileForm(FlaskForm):

    #Formularz i jego pola z właściowściami
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

      
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    #Sprawdza czy nazwa użytkownika nie jest już użyta w bazie danych
    def validate_username(self, username):
        #Sprawdza czy użytkownik wpisał już taką jaką ma lub jej nie ruszył
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
            
#Pusty formularz w celu poprawnego działania Follow & Unfollow funkcji
class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


#Formularz dodający posty
class PostForm(FlaskForm):
    post = TextAreaField('Say Something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')


#Mail resetowania hasła
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


#Resetowanie hasła
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')