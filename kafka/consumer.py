#!/usr/bin/env python

import sys, os
this_path = os.path.dirname(os.path.abspath(__file__))

import kafka_utils
from confluent_kafka import DeserializingConsumer, TopicPartition
from confluent_kafka.error import KeyDeserializationError, ValueDeserializationError, ConsumeError
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
    conf = kafka_utils.read_config(config_file)


    #Create the kafka consumer
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

    print("connecting to broker")
    consumer = DeserializingConsumer(consumer_config)
    print("broker connection succeeded")

    #create the redis interface
    r = Redis(host="redis_1",port=7001, decode_responses=True)
    r_wordCounts = Redis(host="redis_1",port=7001, decode_responses=True, db=1)

    #Wait until the kafka topic is up before proceeding
    kafka_utils.wait_topic(consumer, topic)

    partitions = []
    partition = TopicPartition(topic=topic, partition=0, offset=0)
    partitions.append(partition)
    consumer.assign(partitions) 
        #maybe should change this to subscribe so we can use the on_assign and on_revoke callbacks           

    # Process messages
    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                # No message available within timeout.
                # print("Waiting for message or event/error in poll()")
                continue
            else:
                #message returned
                key_object = msg.key()
                value_object = msg.value()
                text = value_object.text
                url = key_object.url
                print("url is:",url)
                #need more error handling, what happens if we can't connect to redis
                kafka_utils.send_ngrams(r, url, msg.offset(), text)
                consumer.commit(message=msg, asynchronous=True)   
        except KeyboardInterrupt:
            break
        except ConsumeError as ce:
            print("Consume error encountered while polling. Message failed {}".format(ke))
            continue             
        except KeyDeserializationError as ke:
            # Report malformed record, discard results, continue polling
            print("Message key deserialization failed {}".format(ke))
            continue
        except ValueDeserializationError as ve:
            # Report malformed record, discard results, continue polling
            print("Message value deserialization failed {}".format(ve))
            continue   

    # After you exit the poll loop commit the final offsets and close the consumer
    consumer.commit(message=msg, asynchronous=False)
    consumer.close()
    #finally disconnect from redis server
    r.connection_pool.disconnect()

