#!/usr/bin/env python

import sys, os
this_path = os.path.dirname(os.path.abspath(__file__))

import kafka_utils
from confluent_kafka import DeserializingConsumer, TopicPartition
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from data import google
from redis import Redis
import logging


if __name__ == '__main__':

    # logging.basicConifg()

    # Read arguments and configurations and initialize
    print("starting consumer")
    args = kafka_utils.parse_args(sys.argv[1:])
    config_file = args.config_file
    topic = args.topic
    conf = kafka_utils.read_config(config_file, 'consumer_google_chicago_redis')

    #Create the kafka consumer interface
    schema_registry_conf = {
        'url': conf['schema.registry.url']}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf) 
    key_schema_path = this_path + conf['google.key.schema.file']
    value_schema_path = this_path + conf['google.value.schema.file']
    key_schema, value_schema = kafka_utils.load_avro_schema_from_file(key_schema_path, value_schema_path)
    
    key_avro_deserializer = AvroDeserializer(key_schema,
                                          schema_registry_client,
                                          google.Key.dict_to_key)
    value_avro_deserializer = AvroDeserializer(value_schema,
                                           schema_registry_client,
                                           google.Value.dict_to_value)
    consumer_config = {
        'bootstrap.servers': conf['bootstrap.servers'],
        'key.deserializer': key_avro_deserializer,
        'value.deserializer': value_avro_deserializer,
        'group.id': '1'}
    consumer = DeserializingConsumer(consumer_config)
 
    #create the redis interface
    r = Redis(host="redis_1",port=7001, decode_responses=True)
    r_wordCounts = Redis(host="redis_1",port=7001, decode_responses=True, db=1)

    #Wait until the kafka topic is up before proceeding
    kafka_utils.wait_topic(consumer, topic)

    #assign partitions to consumer
    partitions = []
    partition = TopicPartition(topic=topic, partition=0, offset=0)
    partitions.append(partition)
    consumer.assign(partitions) 
        #maybe should change this to subscribe so we can use the on_assign and on_revoke callbacks           


    #there is an infinite loop within this function that won't break until it sees a keyboard interupt
    msg = kafka_utils.consume_messages(consumer, r, kafka_utils.send_ngrams_redis) 


    # After you exit the poll loop commit the final offsets and close the consumer
    consumer.commit(message=msg, asynchronous=False)
    consumer.close()
    #finally disconnect from redis server
    r.connection_pool.disconnect()

