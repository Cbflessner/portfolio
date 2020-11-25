#############################test_create_kafka_topics()################################
# import tests.test_kafka_utils as ku
# from confluent_kafka import Producer

# kafka = ku.TestKafkaUtils
# kafka.test_create_kafka_topic(kafka)

# conf = {'bootstrap.servers':'broker:9092'}
# p = Producer(conf)
# info = p.list_topics()
# topic = info.topics['christian_test'].topic
# print(topic)

# #############################test_producer()################################
# import tests.test_messages as tm

# messageController = tm.TestMessages
# result = messageController.test_producer(messageController)
# print(result)


# #############################test_consumer()################################
# import tests.test_messages as tm

# messageController = tm.TestMessages
# result = messageController.test_consumer(messageController)
# print(result)


###########################test_read_config()##############################
# import tests.test_kafka_utils as ku

# kafka = ku.TestKafkaUtils
# kafka.test_read_config(kafka)


############################ngrams################################
import kafka.kafka_utils as ku

test = 'the quick brown! fo#x jumped over the 4 lazy sheep'
ngrams = ku.ngrams(test, 3)
predictions = ku.ngram_predictions(ngrams)


