#!/usr/bin/env python

import sys, os
this_path = os.path.dirname(os.path.abspath(__file__))

import kafka_utils
from confluent_kafka import DeserializingConsumer, TopicPartition
from confluent_kafka.error import KeyDeserializationError, ValueDeserializationError, ConsumeError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from data import google
import time
from redis import Redis


if __name__ == '__main__':

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
    error = "not ready"
    tries = 0
    while error is not None:
        info = consumer.list_topics(topic)
        topic_info = info.topics[topic]
        if topic_info.error is None:
            error = topic_info.error
            print("topic {} found.  Partion {}".format(topic_info.topic, topic_info.partitions))
        else:
            tries += 1
            print('try {} failed'.format(tries))
            time.sleep(1)
        if tries >= 50:
            exit('could not connect to kafka topic after 10 tries')

    partitions = []
    partition = TopicPartition(topic=topic, partition=0, offset=0)
    partitions.append(partition)
    consumer.assign(partitions)            

    # Process messages
    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                # No message available within timeout.
                # print("Waiting for message or event/error in poll()")
                continue
            elif msg.error():
                #Error returned
                print('error: {}'.format(msg.error()))
            else:
                #message returned
                key_object = msg.key()
                value_object = msg.value()
                text = value_object.text
                url = key_object.url
                print("url is:",url)
                five_grams = kafka_utils.ngrams(text, 5)
                for elem in five_grams:
                    redis_key = ' '.join([str(word) for word in elem[:-1]])
                    r.zincrby(redis_key,1, elem[-1])
                four_grams = kafka_utils.ngrams(text, 4)
                for elem in four_grams:
                    redis_key = ' '.join([str(word) for word in elem[:-1]])
                    r.zincrby(redis_key,1, elem[-1])
                three_grams = kafka_utils.ngrams(text, 3)
                for elem in three_grams:
                    redis_key = ' '.join([str(word) for word in elem[:-1]])
                    r.zincrby(redis_key,1, elem[-1])
                two_grams = kafka_utils.ngrams(text, 2)
                for elem in two_grams:
                    redis_key = ' '.join([str(word) for word in elem[:-1]])
                    r.zincrby(redis_key,1, elem[-1])
                one_gram = kafka_utils.ngrams(text,1)
                for elem in one_gram:
                    redis_key = elem[0]
                    r_wordCounts.incrby(redis_key,1)    
                print("ngrams sent to redis")
        except KeyboardInterrupt:
            break
        except KeyDeserializationError as ke:
            # Report malformed record, discard results, continue polling
            print("Message key deserialization failed {}".format(ke))
            pass
        except ValueDeserializationError as ve:
            # Report malformed record, discard results, continue polling
            print("Message value deserialization failed {}".format(ve))
            pass  
        except ConsumeError as ce:
            print("Consume error encountered while polling. Message failed {}".format(ke))
            pass                      

    # Leave group and commit final offsets
    consumer.close()
