import kafka.kafka_utils as kafka_utils
from confluent_kafka.admin import TopicMetadata
from confluent_kafka import Producer, Consumer
import pytest

class TestKafkaUtils:


    def test_read_config(self):
        config = kafka_utils.read_config('/home/christian/portfolio/tests/librdkafka.config')
        control_config = {'bootstrap.servers':'localhost:9092', 'schema.registry.url':'http://localhost:8081', 'schema.file':'./avro/google-scraper.avsc'}
        assert config == control_config

    def test_create_kafka_topic(self):
        conf = {'bootstrap.servers':'localhost:9092'}
        kafka_utils.create_topic(conf=conf, topic='christian_test', num_partitions=1, replication_factor=1) 

        p = Producer(conf)
        info = p.list_topics()

        topic = info.topics['christian_test'].topic
        partitions = info.topics['christian_test'].partitions
        num_partitions = list(partitions.keys())
        result = (topic, len(num_partitions))
        
        assert result == ('christian_test', 1)

    def test_load_avro_schema_from_file(self):
        key_schema, value_schema = kafka_utils.load_avro_schema_from_file('/home/christian/portfolio/tests/key-schema-test.avsc', '/home/christian/portfolio/tests/value-schema-test.avsc')
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