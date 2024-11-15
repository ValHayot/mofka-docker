import subprocess
import time


def produce_data(producer, topic: str, run_conf: str, exp: int, events: int):
    start = time.perf_counter_ns()
    for i in range(events):
        producer.send(topic, "1" * 10**exp, evict=True)
    end = time.perf_counter_ns()
    producer.close(topics=[topic])
    return f"{run_conf},produce,{10**exp},{start},{end},{(end - start)/10**9}"


def consume_data(consumer, run_conf: str):
    start = time.perf_counter_ns()
    while True:
        try:
            event = next(consumer)
            size = len(event)
        except Exception as e:
            print(e)
            break
    end = time.perf_counter_ns()
    return f"{run_conf},consume,{size},{start},{end},{(end - start)/10**9}"

    consumer.close()
