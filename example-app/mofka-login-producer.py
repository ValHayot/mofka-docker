import sys
from io import StringIO

import helpers

from pymargo.core import Engine
from pymargo.core import client as client_mode
import pymofka_client as mofka
import pyssg

from dsaas_client.api import get_file


def main():
    engine = Engine(helpers.mofka_protocol, use_progress_thread=True)
    client = mofka.Client(engine.mid)
    pyssg.init()
    service = client.connect(helpers.ssg_file)
    # service = helpers.start_mofka()
    # print('mofka_started')

    topic_name = sys.argv[1]
    source_id = int(sys.argv[2])
    producer_name = 'mofka_login_producer'
    producer = helpers.create_mofka_producer(
        topic_name=topic_name,
        producer_name=producer_name,
        service=service
    )
    print('producer created')

    data = StringIO()
    get_file(source_id=source_id).to_csv(data)
    # print(data.getvalue()[0:100])
    data_b = bytes(data.getvalue(), encoding='utf-8')
    f = producer.push({"version_id": 'latest'}, data_b)
    f.wait()
    producer.flush()

if __name__ == '__main__':
    main()

