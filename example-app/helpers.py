import os

from pymargo.core import Engine
from pymargo.core import client as client_mode
import pymofka_client as mofka
import pyssg

ssg_file = 'mofka.ssg'
mofka_protocol = os.environ['MOFKA_PROTOCOL']

def my_data_selector(metadata, descriptor):
    return descriptor

def my_data_broker(metadata, descriptor):
    data = bytearray(descriptor.size)
    return [data]

def create_mofka_producer(
    topic_name: str,
    producer_name: str,
    service,
) -> any:
    topic = service.open_topic(topic_name)

    batchsize = mofka.AdaptiveBatchSize
    thread_pool = mofka.ThreadPool(1)
    ordering = mofka.Ordering.Strict
    producer = topic.producer(producer_name, batchsize, thread_pool, ordering)
    
    return producer

def create_mofka_consumer(
    topic_name: str,
    consumer_name: str,
    service,
) -> any:
    topic = service.open_topic(topic_name)
    consumer_name = "mofka_consumer"
    consumer = topic.consumer(
        name=consumer_name,
        batch_size=1,
        data_broker=my_data_broker,
        data_selector=my_data_selector
    )

    return consumer
