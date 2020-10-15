import argparse, sys
from confluent_kafka import avro, KafkaError, Producer
from confluent_kafka.admin import AdminClient, NewTopic
from uuid import uuid4


def parse_args():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("-t", required=True, help="Topic name", dest="topic")
    arg_parser.add_argument("-f", required=True, help="Kafka config file should be in portfolio/.confluent", dest='config_file')

    return arg_parser.parse_args()

def read_config(config_file):
    """Read Confluent Cloud configuration for librdkafka clients"""

    conf = {}
    with open(config_file) as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                conf[parameter] = value.strip()

    return conf

def create_topic(conf, topic, num_partitions, replication_factor):
    """
        Create a topic if needed
        Examples of additional admin API functionality:
        https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/adminapi.py
    """

    a = AdminClient({
           'bootstrap.servers': conf['bootstrap.servers']
    })

    fs = a.create_topics([NewTopic(
         topic,
         num_partitions=num_partitions,
         replication_factor=replication_factor
    )])
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic {} created".format(topic))
        except Exception as e:
            # Continue if error code TOPIC_ALREADY_EXISTS, which may be true
            # Otherwise fail fast
            if e.args[0].code() != KafkaError.TOPIC_ALREADY_EXISTS:
                print("Failed to create topic {}: {}".format(topic, e))
                sys.exit(1)
    p = Producer(conf)
    info = p.list_topics()
    print(topic, f)
    print(info.topics)


# Optional per-message on_delivery handler (triggered by poll() or flush())
# when a message has been successfully delivered or
# permanently failed delivery (after retries).
delivered_records = 0
def acked(err, msg):
    global delivered_records
    """Delivery report handler called on 
    successful or failed delivery of message
    """
    if err is not None:
        print("Failed to deliver message: {}".format(err))
    else:
        delivered_records += 1
        print("Produced record to topic {} partition [{}] @ offset {}"
              .format(msg.topic(), msg.partition(), msg.offset()))

def load_avro_schema_from_file(key_schema_file, value_schema_file):
    with open(key_schema_file) as ksf:
        key_schema = ksf.read()

    with open(value_schema_file) as vsf:
        value_schema = vsf.read()
    
    return key_schema, value_schema        