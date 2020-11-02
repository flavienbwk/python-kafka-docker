import os
import time
import pickle
from datetime import datetime
from kafka import KafkaConsumer
from essential_generators import DocumentGenerator

kafka_servers_env = os.environ.get("KAFKA_SERVERS", "localhost:9092")
kafka_servers = kafka_servers_env.split(",")

# Specifying every Kafka broker in cluster and parameters
consumer = KafkaConsumer(
    'sentences',
    bootstrap_servers=kafka_servers,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-unique-group',
    value_deserializer=lambda x: pickle.loads(x)
)

# Reading messages
for message in consumer:
    print("\n", flush=True)
    print("Sent time     :", message.value["datetime"].strftime("%H:%M:%S.%f"), flush=True)
    print("Received time :", datetime.now().strftime("%H:%M:%S.%f"), flush=True)
    print("Sentence      :", message.value["sentence"], flush=True)
