import argparse, sys
from confluent_kafka import avro, KafkaError, Producer
from confluent_kafka.admin import AdminClient, NewTopic
from uuid import uuid4
import pandas as pd
from redis import Redis, WatchError
import numpy as np
import time


def parse_args(args):
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



#callback function which gets passed to poll() (since flush calls poll() it will
#call this too).  msg metadata that gets returned is: topic, partition, offset,
#len (message value size in bytes).  key, value,  and timestamp
def acked(err, msg):
    """Delivery report handler called on 
    successful or failed delivery of message
    """
    if err is not None:
        print("Failed to deliver message: {}".format(err))
    else:
        print("Produced record to topic {} partition [{}] @ offset {} and time {}"
              .format(msg.topic(), msg.partition(), msg.offset(), msg.timestamp()))


def load_avro_schema_from_file(key_schema_file, value_schema_file):
    with open(key_schema_file) as ksf:
        key_schema = ksf.read()

    with open(value_schema_file) as vsf:
        value_schema = vsf.read()
    
    return key_schema, value_schema        


def remove_special(input):
    clean = ''.join(ch for ch in input if ch.isalnum())
    return clean


def create_ngrams(input, n):
    input = input.split(' ')
    clean = []
    output = []
    for word in input:
        clean.append(remove_special(word))
    for i in range(len(clean)-n+1):
        output.append(clean[i:i+n])
    return output


def ngram_factoral(pipe, n, text):
    grams = np.arange(n)+1
    grams = grams[1:]
    for i in grams: 
        n_grams = create_ngrams(text, i)
        for elem in n_grams:
            redis_key = ' '.join([str(word) for word in elem[:-1]])
            pipe.zincrby(redis_key,1, elem[-1])


def send_ngrams(r, url, offset, text):
    with r.pipeline() as pipe:
        error_count = 0
        while True:
            try:
                pipe.watch(url)
                #check if we've seen this url before
                if r.hexists('url', url) == 0:
                    #if not record the url and the offset it came over with
                    r.hset("url", key=url, value=offset)
                    #then break the text into n-grams and store them in redis
                    ngram_factoral(pipe, 5, text)
                    pipe.execute()  
                    print("ngrams sent to redis, offsets committed") 
                    break 
                else:
                    pipe.unwatch()
                    print('URL has come through redis before')
                    break
            except WatchError:
                error_count += 1
                print("WatchError {} for url {}; retrying",
                    error_count, url)


def wait_topic(kaf_con, topic):
    error = "not ready"
    tries = 0
    while error is not None:
        info = kaf_con.list_topics(topic)
        topic_info = info.topics[topic]
        if topic_info.error is None:
            error = topic_info.error
            print("topic {} found.  Partion {}".format(topic_info.topic, topic_info.partitions))
        else:
            tries += 1
            print('try {} failed'.format(tries))
            time.sleep(1)
        if tries >= 50:
            exit('could not connect to kafka topic after 10 tries')     


def wait_schemaRegistry(schema_registry_client):
    error = "not ready"
    tries = 1
    #Wait until the schema registry is up before proceeding
    while error is not None:
        try:  
            info = schema_registry_client.get_subjects()
            print("Schema registry detected subjects found are: ")
            print(info)
            error = None
            print("schema detected after {} tries".format(tries))
        except:
            print('connecting to schema registry try {} failed'.format(tries))
            tries += 1
            time.sleep(1)
        if tries >= 200:
            exit('could not reach schema registry after {} tries'.format(tries))                       
