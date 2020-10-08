# import set_package_attribute
# set_package_attribute.init()
print('__file__ =',__file__)
print('__name__ =',__name__)
print('__package__ =',__package__)

import sys
print(sys.path)
from tests import test_kafka_utils as t

# test = t.TestKafkaUtils()
# test.test_create_kafka_topic()