
#Add the portfolio directory to the PYPATH so it can see the web_scrapers pakcage
import sys, os
this_path = os.path.dirname(os.path.abspath(__file__))
path=this_path.split( '/')
path.pop(len(path)-1)
portfolio_path = "/".join(path)
sys.path.insert(0, portfolio_path)

import kafka.kafka_utils as kafka_utils
from confluent_kafka.admin import TopicMetadata
from confluent_kafka import Producer, Consumer
import pytest

class TestKafkaUtils:


    def test_read_config(self):
        config = kafka_utils.read_config(this_path + '/librdkafka.config')
        control_config = {'bootstrap.servers':'broker:9092', 'schema.registry.url':'http://schema-registry:8081', 'google.key.schema.file':'/avro/google-scraper-key.avsc'
        ,'google.value.schema.file':'/avro/google-scraper-value.avsc'}
        assert config == control_config

    def test_create_kafka_topic(self):
        #topic was already created in circlCI set up (config.yml step 6).  Just checking that it's still up
        conf = kafka_utils.read_config(portfolio_path + '/kafka/librdkafka.config')
        producer_config = {'bootstrap.servers': conf['bootstrap.servers']}
        p = Producer(producer_config)
        info = p.list_topics()
        topic = info.topics['christian_test'].topic
        partitions = info.topics['christian_test'].partitions
        num_partitions = list(partitions.keys())
        result = (topic, len(num_partitions))
        
        assert result == ('christian_test', 1)

    def test_load_avro_schema_from_file(self):
        key_schema, value_schema = kafka_utils.load_avro_schema_from_file(this_path + '/key-schema-test.avsc', this_path + '/value-schema-test.avsc')
        key_schema_control = '''
{
  "namespace": "io.portfolio.googlescraper",
  "type": "record",
  "name": "GoogleScraper",
  "fields": [
    {
      "name": "key",
      "type": "string"
    }
  ]
}'''
        value_schema_control = '''
{
  "namespace": "io.portfolio.googlescraper",
  "type": "record",
  "name": "GoogleScraper",
  "fields": [
    {
      "name": "url",
      "type": "string"
    },
    {
      "name": "text",
      "type": "string"
    },
    {
      "name": "scraper_dt",
      "type": "string"
    }
  ]
}'''
        schemas = [key_schema, value_schema]
        controls = [key_schema_control, value_schema_control]
        assert schemas == controls

