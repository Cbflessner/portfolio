#!/usr/bin/env python

import google_scraper as gs
import os.path
import kafka_utils
from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer, IntegerSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from data import google
import time
from datetime import datetime
import pytz



if __name__ == '__main__':

    # Read arguments and configurations and initialize
    args = kafka_utils.parse_args()
    config_file = args.config_file
    topic = args.topic
    conf = kafka_utils.read_config(config_file)

    # Create topic if needed
    kafka_utils.create_topic(conf, topic) 

    # time.sleep(1000)
    # print('execution resumed')

    schema_registry_conf = {
        'url': conf['schema.registry.url']}


    schema_registry_client = SchemaRegistryClient(schema_registry_conf)    
    
    key_schema, value_schema = kafka_utils.load_avro_schema_from_file(conf['schema.file'])
    
    key_avro_serializer = AvroSerializer(key_schema,
                                          schema_registry_client,
                                          google.Key.key_to_dict)
    value_avro_serializer = AvroSerializer(value_schema,
                                           schema_registry_client,
                                           google.Value.value_to_dict)

    producer_config = {
        'bootstrap.servers': conf['bootstrap.servers'],
        'key.serializer': key_avro_serializer,
        'value.serializer': value_avro_serializer}

    producer = SerializingProducer(producer_config)

    #Set number of articles to read
    num_articles=3

    google_news = gs.google_top_results(num_articles, '/search?q=chicago&tbm=nws')
    for num in range(len(google_news)):
        url = google_news.iloc[num]
        text = gs.html_to_string(url)
        news = gs.clean_news(text, 20)
        scraper_dt = datetime.now(pytz.timezone('America/Denver'))
        scraper_dt = scraper_dt.strftime("%Y/%m/%d %H:%M:%S %z")
        value_obj = google.Value(url=url, text=news.to_string(index=False), scraper_dt=scraper_dt)
        key_obj = google.Key(key=str(hash(url)))
        print("Producing record: {}\t{}".format(key_obj.key, value_obj.text[:10]))
        producer.produce(topic=topic, key=key_obj, value=value_obj, on_delivery=kafka_utils.acked)
        producer.poll(0)

    producer.flush()

    print("{} messages were produced to topic {}!".format(kafka_utils.delivered_records, topic))

