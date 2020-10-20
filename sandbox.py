# import tests.test_messages as tm

# messageController = tm.TestMessages
# result = messageController.test_consumer(messageController)
# print(result)

import tests.test_kafka_utils as ku

kafka = ku.TestKafkaUtils
kafka.test_create_kafka_topic(kafka)