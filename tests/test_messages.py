#Add the portfolio directory to the PYPATH so it can see the web_scrapers pakcage
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
path=myPath.split( '/')
path.pop(len(path)-1)
new_path = "/".join(path)
sys.path.insert(0, new_path)

import kafka.kafka_utils as kafka_utils
from web_scrapers import google_scraper as gs
from confluent_kafka import SerializingProducer, DeserializingConsumer, TopicPartition
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from data import google
from datetime import datetime
import pytz



class TestMessages:
    test_messages =['test message with newlines (backslash n) \n\n', 'test message with carriage retruns (backslash r)\r\r'
    ,'test message with \t\t\t tabs', '          test message with leading whitespace', 'test message with trailing whitespace       ']
    topic = 'christian_test'
    conf = kafka_utils.read_config(new_path+'/kafka/librdkafka.config')
    schema_registry_conf = {
        'url': conf['schema.registry.url']}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)    
    key_schema, value_schema = kafka_utils.load_avro_schema_from_file(conf['google.key.schema.file'], conf['google.value.schema.file'])
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
            news = gs.clean_news(text, 20)
            scraper_dt = datetime.now(pytz.timezone('America/Denver'))
            scraper_dt = scraper_dt.strftime("%Y/%m/%d %H:%M:%S %z")
            value_obj = google.Value(url=url, text=text, scraper_dt=scraper_dt)
            key_obj = google.Key(key=str(hash(url)))
            producer.produce(topic=self.topic, key=key_obj, value=value_obj, on_delivery=kafka_utils.acked)
            delivered_records += producer.poll()
        producer.flush()

        assert delivered_records == 5


    def test_consumer(self):
        consumer_config = {
            'bootstrap.servers': self.conf['bootstrap.servers'],
            'key.deserializer': self.key_avro_deserializer,
            'value.deserializer': self.value_avro_deserializer,
            'group.id': '1',
            'auto.offset.reset': 'earliest' }

        consumer = DeserializingConsumer(consumer_config)

        partitions = []
        partition = TopicPartition(topic=self.topic, partition=0)
        partitions.append(partition)
        consumer.assign(partitions)

        # Process messages
        result = []
        print('entering loop for topic', self.topic)        
        while True:
            try:
                msg = consumer.poll(1.0)
                if msg is None:
                    print("No messages to consume")
                    break
                elif msg.error():
                    print('error: {}'.format(msg.error()))
                    break
                else:
                    value_object = msg.value()
                    text = value_object.text
                    result.append(text)
                    print('message retrieved')
            except KeyboardInterrupt:
                print('user exit')
                break
            except SerializerError as e:
                # Report malformed record, discard results, continue polling
                print("Message deserialization failed {}".format(e))
                break

        # Leave group and commit final offsets
        consumer.close()
        return result
