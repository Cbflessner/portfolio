#!/usr/bin/env python

import sys, os
this_path = os.path.dirname(os.path.abspath(__file__))

from web_scrapers import google_scraper as gs
import kafka_utils 
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from data import google
from datetime import datetime
import pytz
import time



if __name__ == '__main__':

    # Read arguments and configurations and initialize
    print("starting producer")
    args = kafka_utils.parse_args(sys.argv[1:])
    config_file = args.config_file
    topic = args.topic
    conf = kafka_utils.read_config(config_file)

    # Create topic if needed
    print("connecting to server", conf['bootstrap.servers'])
    kafka_utils.create_topic(conf=conf, topic=topic, num_partitions=1, replication_factor=1) 

    schema_registry_conf = {
        'url': conf['schema.registry.url']}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)   
    key_schema_path = this_path + conf['google.key.schema.file']
    value_schema_path = this_path + conf['google.value.schema.file']
    key_schema, value_schema = kafka_utils.load_avro_schema_from_file(key_schema_path, value_schema_path)
    
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

    #set loop variables
    error = "not ready"
    tries = 0
    #Wait until the kafka topic is up before proceeding
    while error is not None:
        info = producer.list_topics(topic)
        topic_info = info.topics[topic]
        if topic_info.error is None:
            error = topic_info.error
            print('connected to topic: {}'.format(topic))
        else:
            tries += 1
            print('connecting to topic try {} failed'.format(tries))
            time.sleep(1)
        if tries >= 50:
            exit('could not connect to kafka topic after 10 tries')

    error = "not ready"
    tries = 1
    #Wait until the schema registry is up before proceeding
    while error is not None:
        try:  
            info = schema_registry_client.get_subjects()
            print("Schema registry detected subjects found are: ")
            print(info)
            error = None
            print("schema detected after {} tries".format(tries))
        except:
            print('connecting to schema registry try {} failed'.format(tries))
            tries += 1
            time.sleep(1)
        if tries >= 200:
            exit('could not reach schema registry after {} tries'.format(tries))


    #Set number of articles to read
    num_articles=3
    delivered_records =0
    google_news = gs.google_top_results(num_articles, '/search?q=chicago&tbm=nws')
    for num in range(len(google_news)):
        url = google_news.iloc[num]
        text = gs.html_to_string(url)
        news = gs.clean_news(text, 20)
        scraper_dt = datetime.now(pytz.timezone('America/Denver'))
        scraper_dt = scraper_dt.strftime("%Y/%m/%d %H:%M:%S %z")
        value_obj = google.Value(text=news.to_string(index=False), scraper_dt=scraper_dt)
        key_obj = google.Key(url=str(url))
        print("Producing record: {}\t{}".format(key_obj.url, value_obj.text[:10]))
        producer.produce(topic=topic, key=key_obj, value=value_obj, on_delivery=kafka_utils.acked)
        delivered_records += producer.poll()

    producer.flush()

    print("{} messages were produced to topic {}!".format(delivered_records, topic))
