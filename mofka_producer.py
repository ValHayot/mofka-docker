import random
import string

from pymargo.core import Engine
from pymargo.core import server as server_mode
import pymofka_client as mofka
import pyssg

ssg_file = 'mofka.ssg'
mofka_protocol = 'ofi+tcp'

engine = Engine(mofka_protocol, use_progress_thread=True)
client = mofka.Client(engine.mid)
pyssg.init()
service = client.connect(ssg_file)

# create topic
try:
    name = "mofka_test"
    validator = mofka.Validator.from_metadata()
    selector = mofka.PartitionSelector.from_metadata() #{"__type__":"my_partition_selector:./custom/libmy_partition_selector.so"})
    serializer = mofka.Serializer.from_metadata() #({"__type__":"my_serializer:./custom/libmy_serializer.so"})
    service.create_topic(topic_name=name, validator=validator, selector=selector, serializer=serializer)
    service.add_memory_partition(name, 0)
except:
    pass # topic has already been created

topic = service.open_topic(name)

batchsize = mofka.AdaptiveBatchSize
thread_pool = mofka.ThreadPool(1)
ordering = mofka.Ordering.Strict
producer = topic.producer("mofka_producer", batchsize, thread_pool, ordering)

for i in range(10):
    r = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    print(r)
    f = producer.push({"action": "get_result"}, bytes(r, encoding='utf-8'))
    f.wait()
    producer.flush()