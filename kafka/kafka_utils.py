import argparse, sys, os
from confluent_kafka import avro, KafkaError, Producer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.error import KeyDeserializationError, ValueDeserializationError, ConsumeError
from uuid import uuid4
import pandas as pd
from redis import Redis, WatchError
import numpy as np
import time

offset = 0

def parse_args(args):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-t", required=True, help="Topic name", dest="topic")
    arg_parser.add_argument("-f", required=True, help="Kafka config file should be in portfolio/.confluent", dest='config_file')

    return arg_parser.parse_args()


def read_config(config_file, client_id):
    this_path = os.path.dirname(os.path.abspath(__file__))
    kafka_config_path=this_path+'/configs/'
    f = kafka_config_path+config_file
    print(f)
    conf = {}
    with open(f) as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                conf[parameter] = value.strip()
    conf['client.id'] = client_id
    return conf


def create_topic(conf, topic, num_partitions, replication_factor):
    #Create a topic if needed
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
    global offset
    if err is not None:
        print("Failed to deliver message: {}".format(err))
    else:
        print("Produced record to topic {} partition [{}] @ offset {} and time {}"
              .format(msg.topic(), msg.partition(), msg.offset(), msg.timestamp()))
    offset = msg.offset()


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


#need more error handling, what happens if we loose our connection to redis
def send_ngrams_redis(r, url, offset, text, n):
    grams = np.arange(n)+1
    grams = grams[1:]
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
                    for i in grams: 
                        n_grams = create_ngrams(text, i)
                        for elem in n_grams:
                            redis_key = ' '.join([str(word) for word in elem[:-1]])
                            redis_value = elem[-1]
                            pipe.zincrby(redis_key, 1, redis_value)
                    pipe.execute()  
                    print("ngrams sent to redis, offsets committed") 
                    break 
                else:
                    pipe.unwatch()
                    print('URL has come through redis before, ngrams not sent')
                    break
            except WatchError:
                error_count += 1
                print("WatchError {} for url {}; retrying",
                    error_count, url)


def send_ngrams_postgres(db, url, offset, text, n):
    grams = np.arange(n)+1
    grams = grams[1:]
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
                    for i in grams: 
                        n_grams = create_ngrams(text, i)
                        for elem in n_grams:
                            redis_key = ' '.join([str(word) for word in elem[:-1]])
                            redis_value = elem[-1]
                            pipe.zincrby(redis_key, 1, redis_value)
                    pipe.execute()  
                    print("ngrams sent to redis, offsets committed") 
                    break 
                else:
                    pipe.unwatch()
                    print('URL has come through redis before, ngrams not sent')
                    break
            except WatchError:
                error_count += 1
                print("WatchError {} for url {}; retrying",
                    error_count, url)                


def consume_messages(consumer, r, process_and_send):
    #setting n=5 means we'll create all coresponding 5 grams, 4 grams, 3 grams, and 2 grams
    #for a given unit of text
    n=5
    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                # No message available within timeout.
                # print("Waiting for message or event/error in poll()")
                continue
            else:
                #message returned
                key_object = msg.key()
                value_object = msg.value()
                text = value_object.text
                url = key_object.url
                print("url is:",url)
                process_and_send(r, url, msg.offset(), text, n)
                consumer.commit(message=msg, asynchronous=True)   
        except KeyboardInterrupt:
            break
        except ConsumeError as ce:
            print("Consume error encountered while polling. Message failed {}".format(ke))
            continue             
        except KeyDeserializationError as ke:
            # Report malformed record, discard results, continue polling
            print("Message key deserialization failed {}".format(ke))
            continue
        except ValueDeserializationError as ve:
            # Report malformed record, discard results, continue polling
            print("Message value deserialization failed {}".format(ve))
            continue  
    return msg                


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