import sys
import time

from typing import Literal

from globus_compute_sdk import Executor


from mocto.mofka import conf_mofka
from mocto.mofka import mofka_produce
from mocto.octopus import octopus_consume


topic = "proxystream"
topic_o = "octopus-test2"

try:
    exp = int(sys.argv[2])
except Exception as e:
    exp = 5

octopus_endpoint = ""  # laptop
mofka_endpoint = ""  # polaris


REGION = "us-east-1"


def invoke_exchange(
    producer_type: Literal["octopus", "mofka"],
    consumer_type: Literal["octopus", "mofka"],
    topic_mofka: str,
    topic_octopus: str,
    endpoints=list[str],
    subscriber_name="exc",
    groupfile="mofka.json",
):
    import time
    from proxystore_ex.stream.exchange import Exchange

    if consumer_type == "mofka":
        from mocto.mofka import mconsumer

        consumer = mconsumer(
            topic=topic_mofka, subscriber_name=subscriber_name, groupfile=groupfile
        )
    else:
        from mocto.octopus import oconsumer

        consumer = oconsumer(topic=topic_octopus)

    if producer_type == "mofka":
        from mocto.mofka import mproducer

        producer = mproducer(topic=topic_mofka, groupfile=groupfile)
    else:
        from pathlib import Path
        from mocto.octopus import oproducer

        producer = oproducer(topic=topic_octopus, endpoints=endpoints)

    e = Exchange(producer=producer, consumer=consumer)

    start_f = time.perf_counter_ns()
    e.forward(topic=topic_octopus)
    end_f = time.perf_counter_ns()

    e.close(topics=[topic_octopus])
    return f"{consumer_type}:{producer_type},forward,0,{start_f},{end_f},{(end_f - start_f)/10**9}"


def distributed_m2o(
    mofka_endpoint: str, octopus_endpoint: str, exp: int = 5, events: int = 1
):
    topic = "proxystream"
    topic_o = "octopus-test2"
    groupfile = "/lus/eagle/projects/Diaspora/valerie/mofka-docker/mofka.json"
    endpoints = [
        "1926a2db-90b2-47c1-90e4-611edd61194c",
        "2e5c79dc-86e3-408e-b9da-8fcba840588a",
    ]

    with Executor(endpoint_id=mofka_endpoint) as gce:

        print("Executing mofka 2 octopus")
        # f = gce.submit(conf_mofka, topic=topic)
        # f.result()
        # print("Submitted config")

        f_mproduce = gce.submit(
            mofka_produce,
            topic=topic,
            exp=exp,
            events=events,
            groupfile=groupfile,
        )
        print("Produced data")

    with Executor(endpoint_id=octopus_endpoint) as gce:
        f_oconsume = gce.submit(octopus_consume, topic=topic_o)
        print("consumed data")

    with Executor(endpoint_id=mofka_endpoint) as gce:
        f_exchange = gce.submit(
            invoke_exchange,
            producer_type="octopus",
            consumer_type="mofka",
            topic_mofka=topic,
            topic_octopus=topic_o,
            groupfile=groupfile,
            endpoints=endpoints,
        )
        print("Exchanged data")
    print(f_mproduce.result())
    print(f_exchange.result())
    print(f_oconsume.result())


def distributed_o2m(
    octopus_endpoint: str, mofka_endpoint: str, exp: int = 5, events: int = 1
):
    pass


if __name__ == "__main__":

    start_time = time.perf_counter_ns()
    distributed_m2o(
        mofka_endpoint="361e399a-911d-4ef8-a2ac-b5b3e6aa9dc8",
        octopus_endpoint="819b0a9d-68bd-4707-a056-2c152ff3054b",
    )
    end_time = time.perf_counter_ns()

    print(f"Total runtime: {(end_time - start_time)/10**9}s")
