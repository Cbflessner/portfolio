import sys, os
this_path = os.path.dirname(os.path.abspath(__file__))
path=this_path.split( '/')
path.pop(len(path)-1)
portfolio_path = "/".join(path)
sys.path.insert(0, portfolio_path)
from confluent_kafka.schema_registry import SchemaRegistryClient
import kafka.kafka_utils as kafka_utils


conf = kafka_utils.read_config(portfolio_path+'/kafka/kafka.config')
schema_registry_conf = {'url': conf['schema.registry.url']}
schema_registry_client = SchemaRegistryClient(schema_registry_conf) 

value_schema = schema_registry_client.get_latest_version('google_scraper-value')
print("christian_test value schema Id is", value_schema.schema_id)
key_schema = schema_registry_client.get_latest_version('google_scraper-key')
print("christian_test key schema Id is", key_schema.schema_id)
