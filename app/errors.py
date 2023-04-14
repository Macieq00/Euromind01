from flask import render_template
from app import app, db

#Custom page for Error 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


#Custom page for Error 500
@app.errorhandler(500)
def internal_error(error):
    #Wyłącza sesje żeby możliwa sesja wywołująca błąd nie kolidowała z sesją nową po błędzie
    db.session.rollback()
    return render_template('500.html'), 500
