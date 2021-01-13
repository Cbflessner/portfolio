from data.ngram_models import Urls
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import pytz

engine = create_engine("postgres://postgres:password@postgres:5432/ngrams")
Session = sessionmaker(bind = engine)
db = Session()
q = db.query(Urls)


u = Urls(url='www.example.com',kafka_offset=5, kafka_produce_time=datetime.now(pytz.timezone('America/Denver')))
v = Urls(url='www.example.com',kafka_offset=5, kafka_produce_time=datetime.now(pytz.timezone('America/Denver')))


# db.add(u)
# db.commit()

try:
    db.add(v)
    db.commit()
except IntegrityError:
    print("url has already been skipped because it was processed previously")
