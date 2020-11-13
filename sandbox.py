import os

# this_path = os.path.dirname(os.path.abspath(__file__))
this_path = os.path.abspath(os.path.dirname(__file__))
new = 'sqlite:///' + os.path.join(this_path, 'app.db')
print(new)