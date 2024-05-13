import pandas as pd
from io import StringIO

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

MOFKA_SERVICE = start_mofka()

def create_mofka_producer(
    topic_name: str,
    producer_name: str,
) -> any:
    # create topic
    try:
        validator = mofka.Validator.from_metadata()
        selector = mofka.PartitionSelector.from_metadata()
        serializer = mofka.Serializer.from_metadata()
        MOFKA_SERVICE.create_topic(topic_name=topic_name, validator=validator, selector=selector, serializer=serializer)
        MOFKA_SERVICE.add_memory_partition(topic_name, 0)
    except:
        pass # topic has already been created

    topic = MOFKA_SERVICE.open_topic(topic_name)

    batchsize = mofka.AdaptiveBatchSize
    thread_pool = mofka.ThreadPool(1)
    ordering = mofka.Ordering.Strict
    producer = topic.producer(producer_name, batchsize, thread_pool, ordering)
    
    return producer

def create_mofka_consumer(
    topic_name: str,
    consumer_name: str,
) -> any:
    try:
        validator = mofka.Validator.from_metadata()
        selector = mofka.PartitionSelector.from_metadata()
        serializer = mofka.Serializer.from_metadata()
        MOFKA_SERVICE.create_topic(topic_name=topic_name, validator=validator, selector=selector, serializer=serializer)

        MOFKA_SERVICE.add_memory_partition(topic, 0, 'abt_pool')
    except:
        pass

    topic = MOFKA_SERVICE.open_topic(topic_name)
    consumer_name = "mofka_consumer"
    consumer = topic.consumer(
        name=consumer_name,
        batch_size=1,
        data_broker=my_data_broker,
        data_selector=my_data_selector
    )

    return consumer

def load_from_event(topic_name) -> pd.DataFrame:
    c = create_mofka_consumer(topic_name=topic_name, consumer_name='mofka-compute-consumer')
    f = c.pull()
    event = f.wait()
    
    data = StringIO(event.data[0].decode('utf-8', 'replace'))
    return pd.read_csv(data)

def load_sources(source_1: int = 1, source_2: int = 2):
    topic_1 = 'source_1'
    topic_2 = 'source_2'

    d_1 = load_from_event(topic_name=topic_1)
    d_2 = load_from_event(topic_name=topic_2)
    
    return d_1, d_2
    

def compute(d1: pd.DataFrame, d2: pd.DataFrame) -> pd.DataFrame:
    report = d1.join(d2, how='outer')
    return report

def write_report(report: pd.DataFrame) -> None:
    producer = create_mofka_producer('report', f'mofka-compute-producer')
    
    f = producer.push(
        {
            "action": "save_output",
            "name": 'example-app',
            "description": 'example mofka application app "report"',
            "sources": [1, 2]
        },

        bytes(report.to_csv(), encoding='utf-8'))
    f.wait()
    producer.flush() 


def main():
    d_1, d_2 = load_sources()
    r = compute(d_1, d_2)
    write_report(r)
    
if __name__ == '__main__':
    main()
    
    