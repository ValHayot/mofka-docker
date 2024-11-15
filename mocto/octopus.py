import os

from confluent_kafka import Consumer, Producer
from aws_msk_iam_sasl_signer import MSKAuthTokenProvider

from proxystore.connectors.file import FileConnector
from proxystore.store import Store
from proxystore.stream import StreamConsumer
from proxystore.stream import StreamProducer

from proxystore.stream.shims.kafka import KafkaPublisher
from proxystore.stream.shims.kafka import KafkaSubscriber

from mocto.helpers import consume_data
from mocto.helpers import produce_data


def octopus_conf():
    REGION = "us-east-1"
    assert os.environ["AWS_ACCESS_KEY_ID"]
    assert os.environ["AWS_SECRET_ACCESS_KEY"]

    def oauth_cb(oauth_config):
        auth_token, expiry_ms = MSKAuthTokenProvider.generate_auth_token(REGION)
        return auth_token, expiry_ms / 1000

    conf = {
        "bootstrap.servers": "b-1-public.diaspora.fy49oq.c9.kafka.us-east-1.amazonaws.com:9198,b-2-public.diaspora.fy49oq.c9.kafka.us-east-1.amazonaws.com:9198",
        "security.protocol": "SASL_SSL",
        "sasl.mechanisms": "OAUTHBEARER",
        "oauth_cb": oauth_cb,
        "group.id": "mygroup",
        "auto.offset.reset": "earliest",
    }

    return conf


def oproducer(
    topic: str,
    store_name: str = "example",
    store_dir: str = "./octopus_dir",
    exp: int = 5,
    events: int = 1,
):
    conf = octopus_conf()

    producer = Producer(conf)
    publisher = KafkaPublisher(client=producer)
    store = Store(store_name, FileConnector(store_dir))
    oprod = StreamProducer(publisher=publisher, stores={topic: store})
    return oprod


def oconsumer(topic: str):
    conf = octopus_conf()
    consumer = Consumer(conf)
    consumer.subscribe([topic])
    subscriber = KafkaSubscriber(client=consumer)
    oconsumer = StreamConsumer(subscriber=subscriber)
    return oconsumer


def octopus_produce(
    topic: str,
    store_name: str = "example",
    store_dir: str = "./octopus_dir",
    exp: int = 5,
    events: int = 1,
):
    oprod = oproducer(
        topic=topic, store_name=store_name, store_dir=store_dir, exp=exp, events=events
    )
    bench = produce_data(oprod, run_conf="octopus", topic=topic, exp=exp, events=events)
    return bench


def octopus_consume(topic: str):
    consumer = oconsumer(topic=topic)
    bench = consume_data(consumer, run_conf="octopus")
    consumer.close()
    return bench
