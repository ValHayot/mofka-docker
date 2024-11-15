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

run_conf = sys.argv[1]


def invoke_exchange(
    producer_type: Literal["octopus", "mofka"],
    consumer_type: Literal["octopus", "mofka"],
    topic_mofka: str,
    topic_octopus: str,
    subscriber_name="exc",
):
    import time
    from proxystore_ex.stream.exchange import Exchange

    if consumer_type == "mofka":
        from mocto.mofka import mconsumer

        consumer = mconsumer(topic=topic_mofka, subscriber_name=subscriber_name)
    else:
        from mocto.octopus import oconsumer

        consumer = oconsumer(topic=topic_octopus)

    if producer_type == "mofka":
        from mocto.mofka import mproducer

        producer = mproducer(topic=topic_mofka)
    else:
        from mocto.octopus import oproducer

        producer = oproducer(topic=topic_octopus)

    e = Exchange(producer=producer, consumer=consumer)

    start_f = time.perf_counter_ns()
    e.forward(topic=topic_o)
    end_f = time.perf_counter_ns()

    e.close(topics=[topic_o])
    return f"{run_conf},forward,0,{start_f},{end_f},{(end_f - start_f)/10**9}"


def distributed_m2o(
    mofka_endpoint: str, octopus_endpoint: str, exp: int = 5, events: int = 1
):
    topic = "proxystream"
    topic_o = "octopus-test2"

    with Executor(endpoint_id=mofka_endpoint) as gce:
        f = gce.submit(conf_mofka)
        f.result()

        f_mproduce = gce.submit(mofka_produce, topic=topic, exp=exp, events=events)
        f_exchange = gce.submit(
            invoke_exchange,
            producer_type="octopus",
            consumer_type="mofka",
            topic_mofka=topic,
            topic_octopus=topic_o,
        )

    with Executor(endpoint_id=octopus_endpoint) as gce:
        f_oconsume = gce.submit(octopus_consume, topic=topic_o)

    print(f_mproduce.result())
    print(f_exchange.result())
    print(f_oconsume.result())


def distributed_o2m(
    octopus_endpoint: str, mofka_endpoint: str, exp: int = 5, events: int = 1
):
    pass


if __name__ == "__main__":

    start_time = time.perf_counter_ns()
    distributed_m2o()
    end_time = time.perf_counter_ns()

    print(f"Total runtime for {run_conf}: {(end_time - start_time)/10**9}s")
