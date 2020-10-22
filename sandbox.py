#############################test_create_kafka_topics()################################
import tests.test_kafka_utils as ku
from confluent_kafka import Producer

kafka = ku.TestKafkaUtils
kafka.test_create_kafka_topic(kafka)

conf = {'bootstrap.servers':'localhost:9092'}
p = Producer(conf)
info = p.list_topics()
topic = info.topics['christian_test'].topic
print(topic)

#############################test_producer()################################
import tests.test_messages as tm

messageController = tm.TestMessages
result = messageController.test_producer(messageController)
print(result)


#############################test_consumer()################################
import tests.test_messages as tm

messageController = tm.TestMessages
result = messageController.test_consumer(messageController)
print(result)

