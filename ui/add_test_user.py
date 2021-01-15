#!/bin/sh

from client import app, db
from client.sql_models import User


user = User(username="test", email="test@example.com")
user.set_password("test")
db.session.add(user)
db.session.commit()