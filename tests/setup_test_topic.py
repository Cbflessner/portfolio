#Add the portfolio directory to the PYPATH so it can see the kafka pakcage
import sys, os
this_path = os.path.dirname(os.path.abspath(__file__))
path=this_path.split( '/')
path.pop(len(path)-1)
portfolio_path = "/".join(path)
sys.path.insert(0, portfolio_path)

import kafka.kafka_utils as kafka_utils
from confluent_kafka.admin import TopicMetadata
from confluent_kafka import Producer
import time

#configure and create the producer we will use to check the status of our new topic 
conf = {'bootstrap.servers':'localhost:9092'}
kafka_utils.create_topic(conf=conf, topic='christian_test', num_partitions=1, replication_factor=1) 
p = Producer(conf)
#set our loop variables
error = "not ready"
tries = 0
#Wait until the kafka topic is up before proceeding
while error is not None:
    info = p.list_topics('christian_test')
    topic = info.topics['christian_test']
    if topic.error is None:
        error = topic.error
    else:
        tries += 1
        print('try {} failed'.format(tries))
        time.sleep(5)
    if tries >= 10:
        exit('could not create kafka topic after')

