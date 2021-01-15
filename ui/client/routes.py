from client import app, db, r_ngram, r_words, pred_id
from client.sql_models import User
from flask import render_template, flash, redirect, url_for, request, jsonify
from client.forms import LoginForm, NextWordForm, RegistrationForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from redis import Redis
from datetime import datetime, timezone

@app.route('/',  methods=['GET','POST'])
@app.route('/index',  methods=['GET','POST'])
@login_required
def index():
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
    predictions = []
    global pred_id 
    pred_id += 1
    form = NextWordForm()
    if form.validate_on_submit():
        key = form.text.data
        predictions = r_ngram.zrange(key, 0, 2)
    return render_template("index.html", title='Home', ngrams=ngrams
        ,form=form, predictions=predictions, pred_id=pred_id)

@app.route('/login', methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template("login.html", titel="Sign In", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    #This is a read-modify-write cycle, should be an atomic update statement
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been save')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/predict', methods=['POST'])
@login_required
def predict_word():
    return jsonify({'prediction': r_ngram.zrange(request.form['key'],
                                                request.form['begin'], 
                                                request.form['end'])})