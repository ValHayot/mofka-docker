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

engine = Engine(mofka_protocol, use_progress_thread=True)
client = mofka.Client(engine.mid)
pyssg.init()

service = client.connect(ssg_file)

try:
    validator = mofka.Validator.from_metadata()
    selector = mofka.PartitionSelector.from_metadata()
    serializer = mofka.Serializer.from_metadata()
    service.create_topic(topic_name=topic, validator=validator, selector=selector, serializer=serializer)
    service.add_memory_partition(topic, 0)
except:
    pass

topic = service.open_topic(topic)
consumer_name = "mofka_consumer"
consumer = topic.consumer(
    name=consumer_name,
    batch_size=1,
    data_broker=my_data_broker,
    data_selector=my_data_selector
)
# pull messages from provider
for i in range(10):
    f = consumer.pull()
    event = f.wait()
    data = event.data[0].decode("utf-8", "replace")
    try:
        metadata = eval(event.metadata)
        print(f"{data=}, {metadata=}")
    except:
        print("data failure: ", data, flush=True)