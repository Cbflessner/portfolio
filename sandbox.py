# from tests import test_kafka_utils as t

# test = t.TestKafkaUtils()
# test.test_create_kafka_topic()

import sys, os

myPath = os.path.dirname(os.path.abspath(__file__))
path=myPath.split( '/')
path.pop(len(path)-1)
new = "/".join(path)
sys.path.insert(0, new)
print(sys.path)


from web_scrapers import google_scraper as gs