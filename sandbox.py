import sys, os
this_path = os.path.dirname(os.path.abspath(__file__))
path=this_path.split( '/')
path.pop(len(path)-1)
portfolio_path = "/".join(path)
sys.path.insert(0, portfolio_path)

import kafka.kafka_utils as kafka_utils
from web_scrapers import google_scraper as gs
from confluent_kafka import SerializingProducer, DeserializingConsumer, TopicPartition
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from data import google
from datetime import datetime
import pytz
import time

test_messages =['test message 1', 'test message 2', 'test message 3', 'test message 4']
topic = 'christian_test'
conf = kafka_utils.read_config(this_path+'/kafka/kafka.config')
schema_registry_conf = {'url': conf['schema.registry.url']}
schema_registry_client = SchemaRegistryClient(schema_registry_conf) 
key_schema_file = this_path + conf['google.key.schema.file']
value_schema_file =this_path + conf['google.value.schema.file']  
key_schema, value_schema = kafka_utils.load_avro_schema_from_file(key_schema_file, value_schema_file)
key_avro_serializer = AvroSerializer(key_schema,
                                      schema_registry_client,
                                      google.Key.key_to_dict)
value_avro_serializer = AvroSerializer(value_schema,
                                       schema_registry_client,
                                       google.Value.value_to_dict)
key_avro_deserializer = AvroDeserializer(key_schema,
                                      schema_registry_client,
                                      google.Key.dict_to_key)
value_avro_deserializer = AvroDeserializer(value_schema,
                                       schema_registry_client,
                                       google.Value.dict_to_value)


error = "not ready"
tries = 0
print(schema_registry_client.get_schema(3).schema_str)

# while error is not None:
#     try:
#         info = schema_registry_client.get_schema(1).schema_str
#         print(info)
#         error = None
#         print("schema detected after {} tries".format(tries))
#     except:
#         error ="not ready"
#         tries += 1
#         print('try {} failed'.format(tries))
#         print(info)
#         time.sleep(5)
#     if tries >= 10:
#         exit('could not connect to kafka topic after 10 tries')