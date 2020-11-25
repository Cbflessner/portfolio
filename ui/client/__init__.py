from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from redis import Redis

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
r_ngram = Redis(host="redis_1",port=7001, decode_responses=True, db=0)
r_words =  Redis(host="redis_1",port=7001, decode_responses=True, db=1)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

from client import routes, sql_models, errors