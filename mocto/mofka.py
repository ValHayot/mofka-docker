import subprocess

from proxystore.stream import StreamConsumer
from proxystore.stream import StreamProducer

from proxystore.ex.stream.shims.mofka import MofkaSubscriber
from proxystore.ex.stream.shims.mofka import MofkaPublisher

from mocto.helpers import consume_data
from mocto.helpers import produce_data


def conf_mofka(topic: str):
    protocol = "tcp"
    bedrock_conf = "testing/configuration/mofka_config.json"
    groupfile = "mofka.json"

    # Start Bedrock
    _ = subprocess.Popen(
        ["bedrock", protocol, "-c", bedrock_conf],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Create topic
    cp = subprocess.run(
        ["mofkactl", "topic", "create", topic, "--groupfile", groupfile],
        check=False,
    )
    assert cp.returncode == 0

    # Add partition
    cp = subprocess.run(
        [
            "mofkactl",
            "partition",
            "add",
            topic,
            "--type",
            "memory",
            "--rank",
            "0",
            "--groupfile",
            groupfile,
        ],
        check=False,
    )
    assert cp.returncode == 0


def mproducer(topic: str, protocol: str = "tcp", groupfile: str = "mofka.json"):
    publisher = MofkaPublisher(protocol=protocol, group_file=groupfile)
    producer = StreamProducer(publisher)
    return producer


def mconsumer(
    topic: str,
    subscriber_name: str = "sub1",
    protocol: str = "tcp",
    groupfile: str = "mofka.json",
):
    subscriber = MofkaSubscriber(
        protocol=protocol,
        group_file=groupfile,
        topic_name=topic,
        subscriber_name=subscriber_name,
    )
    consumer = StreamConsumer(subscriber)
    return consumer


def mofka_produce(
    topic: str,
    exp: int,
    events: int,
    protocol: str = "tcp",
    groupfile: str = "mofka.json",
):
    producer = mproducer(topic=topic, protocol=protocol, groupfile=groupfile)
    bench = produce_data(
        producer, run_conf="mofka", topic=topic, exp=exp, events=events
    )
    producer.close(topics=[topic])
    return bench


def mofka_consume(
    topic: str,
    subscriber_name: str = "sub1",
    protocol: str = "tcp",
    groupfile: str = "mofka.json",
):
    consumer = mconsumer(
        topic=topic,
        subscriber_name=subscriber_name,
        protocol=protocol,
        groupfile=groupfile,
    )
    bench = consume_data(consumer, run_conf="mofka")
    consumer.close()
    return bench
