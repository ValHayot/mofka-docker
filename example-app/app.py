import pandas as pd
from io import StringIO

import helpers

from pymargo.core import Engine
from pymargo.core import client as client_mode
import pymofka_client as mofka
import pyssg

engine = Engine(helpers.mofka_protocol, use_progress_thread=True)
client = mofka.Client(engine.mid)
pyssg.init()
MOFKA_SERVICE = client.connect(helpers.ssg_file)


def load_from_event(topic_name) -> pd.DataFrame:
    c = helpers.create_mofka_consumer(
        topic_name=topic_name,
        consumer_name='mofka-compute-consumer',
        service=MOFKA_SERVICE
    )
    f = c.pull()
    event = f.wait()
    
    data = StringIO(event.data[0].decode('utf-8', 'replace'))
    return pd.read_csv(data)

def load_sources(source_1: int = 1, source_2: int = 2):
    topic_1 = 'source_1'
    topic_2 = 'source_2'

    d_1 = load_from_event(topic_name=topic_1)
    print('loaded d1')
    d_2 = load_from_event(topic_name=topic_2)
    print('loaded d2')
    
    return d_1, d_2
    

def compute(d1: pd.DataFrame, d2: pd.DataFrame) -> pd.DataFrame:
    report = d1.join(d2, how='outer', rsuffix='d2')
    return report

def write_report(report: pd.DataFrame) -> None:
    producer = helpers.create_mofka_producer(
        'report',
        f'mofka-compute-producer',
        service=MOFKA_SERVICE
    )
    
    print('pushing producer event')
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
    print('event pushed')


def main():
    d_1, d_2 = load_sources()
    r = compute(d_1, d_2)
    write_report(r)
    print('app complete')
    
if __name__ == '__main__':
    main()
    print('exiting')
    
    