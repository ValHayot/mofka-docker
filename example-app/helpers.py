from pymargo.core import Engine
from pymargo.core import client as client_mode
import pymofka_client as mofka
import pyssg

ssg_file = 'mofka.ssg'
mofka_protocol = 'ofi+tcp'
topic = 'mofka_test'

def my_data_selector(metadata, descriptor):
    return descriptor

def my_data_broker(metadata, descriptor):
    data = bytearray(descriptor.size)
    return [data]

def start_mofka(ssg_file: str='mofka.ssg', mofka_protocol: str='ofi+tcp') -> object:
    engine = Engine(mofka_protocol, use_progress_thread=True)
    client = mofka.Client(engine.mid)
    pyssg.init()
    service = client.connect(ssg_file)

    return service

def create_mofka_producer(
    topic_name: str,
    producer_name: str,
    service,
) -> any:
    # create topic
    try:
        validator = mofka.Validator.from_metadata()
        selector = mofka.PartitionSelector.from_metadata()
        serializer = mofka.Serializer.from_metadata()
        service.create_topic(topic_name=topic_name, validator=validator, selector=selector, serializer=serializer)
        service.add_memory_partition(topic_name, 0)
    except:
        pass # topic has already been created

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
    try:
        validator = mofka.Validator.from_metadata()
        selector = mofka.PartitionSelector.from_metadata()
        serializer = mofka.Serializer.from_metadata()
        service.create_topic(topic_name=topic_name, validator=validator, selector=selector, serializer=serializer)

        service.add_memory_partition(topic, 0, 'abt_pool')
    except:
        pass

    topic = service.open_topic(topic_name)
    consumer_name = "mofka_consumer"
    consumer = topic.consumer(
        name=consumer_name,
        batch_size=1,
        data_broker=my_data_broker,
        data_selector=my_data_selector
    )

    return consumer