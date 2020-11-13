from client import app
from flask import render_template, flash, redirect, url_for
from client.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    user = {'username': "Christian"}
    ngrams = [
        {
            "ngram": "the quick fox jumps over",
            "value": 3
        },
        {
            "ngram": "the other day I thought",
            "value": 7            
        }
    ]
    return render_template("index.html", title='Home', user=user, ngrams=ngrams)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template("login.html", titel="Sign In", form=form)