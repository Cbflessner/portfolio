#!/usr/bin/env python

import os.path
from kafka import kafka_utils
from confluent_kafka import DeserializingConsumer, TopicPartition
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from data import google


if __name__ == '__main__':

    # Read arguments and configurations and initialize
    args = kafka_utils.parse_args()
    config_file = args.config_file
    topic = args.topic
    conf = kafka_utils.read_config(config_file)

    # time.sleep(1000)
    # print('execution resumed')

    schema_registry_conf = {
        'url': conf['schema.registry.url']}


    schema_registry_client = SchemaRegistryClient(schema_registry_conf)    
    
    key_schema, value_schema = kafka_utils.load_avro_schema_from_file(conf['google.key.schema.file'],conf['google.value.schema.file'])
    
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

    partitions = []
    partition = TopicPartition(topic='test', partition=0)
    partitions.append(partition)
    consumer.assign(partitions)

    # Process messages
    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                # No message available within timeout.
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                print("Waiting for message or event/error in poll()")
                continue
            elif msg.error():
                print('error: {}'.format(msg.error()))
            else:
                key_object = msg.key()
                value_object = msg.value()
                text = value_object.text
                # total_count += count
                print("Consumed record with key {} and value {}"
                      .format(key_object.key, text))
        except KeyboardInterrupt:
            break
        except SerializerError as e:
            # Report malformed record, discard results, continue polling
            print("Message deserialization failed {}".format(e))
            pass

    # Leave group and commit final offsets
    consumer.close()
