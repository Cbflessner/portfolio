#Add the portfolio directory to the PYPATH so it can see the web_scrapers pakcage
import sys, os
this_path = os.path.dirname(os.path.abspath(__file__))
path=this_path.split( '/')
path.pop(len(path)-1)
portfolio_path = "/".join(path)
sys.path.insert(0, portfolio_path)

from kafka import kafka_utils
import kafka.web_scrapers.google_scraper as gs
from confluent_kafka import SerializingProducer, DeserializingConsumer, TopicPartition
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from kafka.data import google
from datetime import datetime
import pytz
import time



class TestMessages:
    test_messages =['test message 1', 'test message 2', 'test message 3', 'test message 4']
    topic = 'christian_test'
    conf = kafka_utils.read_config('producer_google_chicago_1.config', 'producer_google_chicago_1')
    schema_registry_conf = {'url': conf['schema.registry.url']}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf) 
    key_schema_file = portfolio_path + "/kafka" + conf['google.key.schema.file']
    value_schema_file = portfolio_path + "/kafka" + conf['google.value.schema.file']  
    key_schema, value_schema = kafka_utils.load_avro_schema_from_file(key_schema_file, value_schema_file)
    key_avro_serializer = AvroSerializer(key_schema,
                                          schema_registry_client,
                                          google.Key.key_to_dict)
    value_avro_serializer = AvroSerializer(value_schema,
                                           schema_registry_client,
                                           google.Value.value_to_dict)
    key_avro_deserializer = AvroDeserializer(key_schema,
                                          schema_registry_client,
                                          google.Key.dict_to_key)
    value_avro_deserializer = AvroDeserializer(value_schema,
                                           schema_registry_client,
                                           google.Value.dict_to_value)

    def test_producer(self):
        # Read arguments and configurations and initialize
        producer_config = {
            'bootstrap.servers': self.conf['bootstrap.servers'],
            'key.serializer': self.key_avro_serializer,
            'value.serializer': self.value_avro_serializer}
        producer = SerializingProducer(producer_config)

        delivered_records = 0
        for text in self.test_messages:
            url = 'www.test.com'
            scraper_dt = datetime.now(pytz.timezone('America/Denver'))
            scraper_dt = scraper_dt.strftime("%Y/%m/%d %H:%M:%S %z")
            value_obj = google.Value(text=text, scraper_dt=scraper_dt)
            key_obj = google.Key(url=(url))
            producer.produce(topic=self.topic, key=key_obj, value=value_obj, on_delivery=kafka_utils.acked)
            delivered_records += producer.poll()
        producer.flush()

        assert delivered_records == len(self.test_messages)


    def test_consumer(self):
        consumer_config = {
            'bootstrap.servers': self.conf['bootstrap.servers'],
            'key.deserializer': self.key_avro_deserializer,
            'value.deserializer': self.value_avro_deserializer,
            'group.id': '1',
            'auto.offset.reset': 'earliest' }
        offset = kafka_utils.offset - len(self.test_messages) + 1
        consumer = DeserializingConsumer(consumer_config)
        partitions = []
        partition = TopicPartition(topic=self.topic, partition=0, offset=offset)
        partitions.append(partition)
        consumer.assign(partitions)
        # Process messages
        result = []  
        attempt =0
        while len(result)<len(self.test_messages):
            try:
                msg = consumer.poll(1.0)
                attempt += 1
                if msg is None:
                    print("no message received")
                    if attempt <10:
                        pass
                    else:
                        break
                elif msg.error():
                    break
                else:
                    value_object = msg.value()
                    text = value_object.text
                    print("adding {} to result".format(text))
                    result.append(text)
            except KeyboardInterrupt:
                break
            except SerializerError as e:
                break
        # Leave group and commit final offsets
        consumer.close()

        assert result == self.test_messages
