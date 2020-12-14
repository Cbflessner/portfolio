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
import json
import pprint



if __name__ == '__main__':

    # def print_stats(stats_json_str):
    #     stats = json.loads(stats_json_str)
    #     pprint.pprint(stats)

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
        # 'stats_cb': print_stats,
        # 'statistics.interval.ms': 1000}

    producer = SerializingProducer(producer_config)  

    #wait until the kafka topic and schema registry are up before proceeding
    kafka_utils.wait_topic(producer, topic)
    kafka_utils.wait_schemaRegistry(schema_registry_client)

    #Set number of articles to read
    num_articles=3
    delivered_records =0
    google_news = gs.google_top_results(num_articles, '/search?q=chicago&tbm=nws')
    print('loop should run {} times'.format(len(google_news)))
    print("for these url's", google_news)
    for num in range(len(google_news)):
        # print("begin producing record {}".format(num+1))
        url = google_news.iloc[num]
        # print("url key for message is", url)
        text = gs.html_to_string(url)
        # print("dirty text for message is", text[:20])
        news = gs.clean_news(text, 20)
        # print("cleaned news value for message is", news)
        scraper_dt = datetime.now(pytz.timezone('America/Denver'))
        scraper_dt = scraper_dt.strftime("%Y/%m/%d %H:%M:%S %z")
        value_obj = google.Value(text=news.to_string(index=False), scraper_dt=scraper_dt)
        key_obj = google.Key(url=str(url))
        print("Producing record: {}\t{}".format(key_obj.url, value_obj.text[:10]))
        producer.produce(topic=topic, key=key_obj, value=value_obj, on_delivery=kafka_utils.acked)
        delivered_records += producer.poll()

    producer.flush()

    print("{} messages were produced to topic {}!".format(delivered_records, topic))
