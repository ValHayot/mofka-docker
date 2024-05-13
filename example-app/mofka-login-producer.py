import random
import string
import sys
from io import StringIO

from pymargo.core import Engine
from pymargo.core import server as server_mode
import pymofka_client as mofka
import pyssg

from dsaas_client.api import get_file


def main():
    ssg_file = 'mofka.ssg'
    mofka_protocol = 'ofi+tcp'

    engine = Engine(mofka_protocol, use_progress_thread=True)
    client = mofka.Client(engine.mid)
    pyssg.init()
    service = client.connect(ssg_file)

    topic_name = sys.argv[1]
    source_id = int(sys.argv[2])

    producer_name = 'mofka_login_producer'
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

    data = StringIO()
    get_file(source_id=source_id).to_csv(data)
    f = producer.push({"version_id": 'latest'}, bytes(data.getvalue(), encoding='utf-8'))
    f.wait()
    producer.flush()

if __name__ == '__main__':
    main()

