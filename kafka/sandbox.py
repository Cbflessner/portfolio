from sqlalchemy import create_engine, Table, Column, String, MetaData, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pytz
import datetime

db_string = 'postgresql://docker:password@postgres:5432/Ngrams'

db = create_engine(db_string)

tz = pytz.timezone('US/Mountain')
d = datetime.datetime(2020, 10, 5, 6, 34,26, tzinfo=tz)

####################################Phase 1 raw sql######################################
# db.execute("INSERT INTO urls (url, kafka_offset, kafka_produce_time) VALUES ('www.example2.com',4, CURRENT_DATE+CURRENT_TIME)")

# result_set = db.execute("SELECT * FROM urls")
# print(result_set)
# print(type(result_set))
# for r in result_set:
    # print(r)
    # for i in r:
    #     print(i)
    #     print(type(i))

########################################Phase 2 SQL Expression Language #################################
# meta = MetaData(db)

# url_table = Table('urls', meta,
#                     Column('url', String),
#                     Column('kafka_offset', Integer),
#                     Column('kafka_produce_time', DateTime)) 

# with db.connect() as conn:
    # url_table.create()
    # insert_statement = url_table.insert().values(url='www.example3.com',
    #     kafka_offset=5, kafka_produce_time=d)
    # conn.execute(insert_statement)

    # select_statement = url_table.select()
    # result_set = conn.execute(select_statement)
    # for r in result_set:
    #     print(r)


######################################SQL ORM#############################################
base = declarative_base()

class Urls(base):
    __tablename__ = 'urls'

    url = Column(String, primary_key=True)
    kafka_offset = Column(Integer)
    kafka_produce_time = Column(DateTime)

Session = sessionmaker(db)
example4 = Urls(url='www.example4.com', kafka_offset=12, kafka_produce_time=d)

session = Session()
session.add(example4)
session.commit()
# base.metadata.create_all(db)


