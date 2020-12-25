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
conf = kafka_utils.read_config('producer_google_chicago_1.config', 'producer_google_chicago_1')
producer_config = {'bootstrap.servers': conf['bootstrap.servers']}
topic = 'christian_test'
kafka_utils.create_topic(conf=producer_config, topic=topic, num_partitions=1, replication_factor=1) 
p = Producer(producer_config)
#create the schema registry client we will use to check the status of the schema registry
schema_registry_conf = {'url': conf['schema.registry.url']}
schema_registry_client = SchemaRegistryClient(schema_registry_conf) 
    
kafka_utils.wait_topic(p, topic)
kafka_utils.wait_schemaRegistry(schema_registry_client)  