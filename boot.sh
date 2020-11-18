source venv/bin/activate
flask db upgrade
flask translate compile
exec gunicorn -b :5000 --access-logfile - --error-logfile - --worker-tmp-dir /dev/shm next_word_engine:app