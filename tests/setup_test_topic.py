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
from confluent_kafka.schema_registry import SchemaRegistryClient

#configure and create the producer we will use to check the status of our new topic 
conf = kafka_utils.read_config(portfolio_path+'/kafka/kafka.config')
producer_config = {'bootstrap.servers': conf['bootstrap.servers']}
kafka_utils.create_topic(conf=producer_config, topic='christian_test', num_partitions=1, replication_factor=1) 
p = Producer(producer_config)
#set our loop variables
error = "not ready"
tries = 1
#Wait until the kafka topic is up before proceeding
while error is not None:
    info = p.list_topics('christian_test')
    topic = info.topics['christian_test']
    if topic.error is None:
        error = topic.error
    else:
        print('try {} failed'.format(tries))
        tries += 1
        time.sleep(5)
    if tries >= 10:
        exit('could not create kafka topic after')


# error = "not ready"
# tries = 1
# #Wait until the kafka topic is up before proceeding
# while error is not None:
#     try:
#         info = schema_registry_client.get_schema(1).schema_str
#         error = None
#         print("schema detected after {} tries".format(tries))
#     except:
#         error ="not ready"
#         print('try {} failed'.format(tries))
#         tries += 1
#         time.sleep(2)
#     if tries >= 10:
#         exit('could not reach schema registry after {} tries'.format(tries))        

