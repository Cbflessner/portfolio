#!/usr/bin/env python

import google_scraper as gs
import os.path
from confluent_kafka import Producer, KafkaError
import ccloud_lib


if __name__ == '__main__':

    # Read arguments and configurations and initialize
    args = ccloud_lib.parse_args()
    config_file = args.config_file
    topic = args.topic
    conf = ccloud_lib.read_ccloud_config(config_file)

    #Set number of articles to read
    num_articles=3

    # Create Producer instance
    producer = Producer({
        'bootstrap.servers': conf['bootstrap.servers']
    })

    # Create topic if needed
    ccloud_lib.create_topic(conf, topic)

    delivered_records = 0

    # Optional per-message on_delivery handler (triggered by poll() or flush())
    # when a message has been successfully delivered or
    # permanently failed delivery (after retries).
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


    google_news = gs.google_top_results(num_articles, '/search?q=chicago&tbm=nws')
    for num in range(len(google_news)):
        url = google_news.iloc[num]
        text = gs.html_to_string(url)
        news = gs.clean_news(text, 20)
        # gs.save_file('google_news/google_news', num, url, news)
        key = str(hash(news))
        print("Producing record: {}\t{}".format(key, news[:30]))
        producer.produce(topic, key=key, value=news, on_delivery=acked)
        producer.poll(0)

    producer.flush()

    print("{} messages were produced to topic {}!".format(delivered_records, topic))

