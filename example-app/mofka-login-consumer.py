import pandas as pd
from io import StringIO

from pymargo.core import Engine
from pymargo.core import client as client_mode
import pymofka_client as mofka
import pyssg

from dsaas_client.api import save_output

import helpers

topic = 'report'
consumer_name = 'mofka-login-consumer'

engine = Engine(helpers.mofka_protocol, use_progress_thread=True)
client = mofka.Client(engine.mid)
pyssg.init()
MOFKA_SERVICE = client.connect(helpers.ssg_file)

consumer = helpers.create_mofka_consumer(
    topic_name=topic,
    consumer_name=consumer_name,
    service=MOFKA_SERVICE
)

# pull report from provider
f = consumer.pull()
event = f.wait()
data = event.data[0].decode("utf-8", "replace")
try:
    metadata = eval(event.metadata)

    print('saving output', metadata)
    print(pd.read_csv(StringIO(data)))
    if metadata['action'] == 'save_output':
        save_output(data=data, name=metadata['name'], description=metadata['description'], sources=metadata['sources'])
except:
    print("data failure: ", data, flush=True)

