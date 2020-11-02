import os
import time
import pickle
from datetime import datetime
from kafka import KafkaProducer, KafkaClient
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError

from essential_generators import DocumentGenerator

kafka_servers_env = os.environ.get("KAFKA_SERVERS", "localhost:9092")
kafka_servers = kafka_servers_env.split(",")

topic_name = "sentences"


print("Brokers : ", kafka_servers, flush=True)
print("Preparing clusers...", flush=True)

# Setting up brokers with topic
topic_list = [
    NewTopic(
        name=topic_name,
        num_partitions=1,
        replication_factor=1,
        topic_configs={'retention.ms': '3600000'}
    )
]

# Retrieving already-created list of topics
client = KafkaClient(bootstrap_servers=kafka_servers)
metadata = client.cluster
future = client.cluster.request_update()
client.poll(future=future)
broker_topics = metadata.topics()

# Deleting topic if it already exists.
# This is NOT recommended in production. Deletion must 
admin_client = KafkaAdminClient(bootstrap_servers=kafka_servers)
if topic_name in broker_topics:
    deletion = admin_client.delete_topics([topic_name])
    try:
        future = client.cluster.request_update()
        client.poll(future=future)
    except KafkaError as e:
        print(e)
        pass
admin_client.create_topics(new_topics=topic_list, validate_only=False)

# Setting up producer
print("Connecting producer to cluser...", flush=True)
producer = KafkaProducer(
    bootstrap_servers=kafka_servers,
    max_block_ms=10000,  # connection timeout
    value_serializer=lambda x: pickle.dumps(x)
)

# Sending a random sentence every 3 seconds
gen = DocumentGenerator()
while(1):
    payload = {
        "datetime": datetime.now(),
        "sentence": gen.gen_sentence()
    }
    print("Sending : ", payload, flush=True)
    producer.send(topic_name, payload)
    print("Sent.\n", flush=True)
    time.sleep(3)
