#!/usr/bin/env python

import sys, os
this_path = os.path.dirname(os.path.abspath(__file__))
from kafka import kafka_utils
from confluent_kafka import DeserializingConsumer, TopicPartition
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from data import google
import time
from rediscluster import RedisCluster


if __name__ == '__main__':

    # Read arguments and configurations and initialize
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
        'group.id': '1',
        'auto.offset.reset': 'earliest' }
    consumer = DeserializingConsumer(consumer_config)

    #create the redis writer
    startup_nodes = [{"host": "10.0.0.11", "port": "7001"}]
    rc = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

    #Wait until the kafka topic is up before proceeding
    error = "not ready"
    tries = 0
    while error is not None:
        info = consumer.list_topics(topic)
        topic_info = info.topics[topic]
        if topic_info.error is None:
            error = topic_info.error
        else:
            tries += 1
            print('try {} failed'.format(tries))
            time.sleep(5)
        if tries >= 10:
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
                print("Waiting for message or event/error in poll()")
                continue
            elif msg.error():
                #Error returned
                print('error: {}'.format(msg.error()))
            else:
                #message returned
                key_object = msg.key()
                value_object = msg.value()
                text = value_object.text
                five_grams =kafka_utils.ngrams(text, 5)
                redis_key = ' '.join([str(elem) for elem in five_grams])
                rc.ZINCRBY(redis_key,1, five_grams[-1])
        except KeyboardInterrupt:
            break
        except SerializerError as e:
            # Report malformed record, discard results, continue polling
            print("Message deserialization failed {}".format(e))
            pass

    # Leave group and commit final offsets
    consumer.close()
