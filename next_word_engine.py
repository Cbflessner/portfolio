from client import app, db
from client.sql_models import User

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}