import subprocess
import time


def produce_data(producer, topic: str, run_conf: str, exp: int, events: int):
    start = time.perf_counter_ns()
    for i in range(events):
        producer.send(topic, "1" * 10**exp, evict=True)
    end = time.perf_counter_ns()
    return f"{run_conf},produce,{10**exp},{start},{end},{(end - start)/10**9}"


def consume_data(consumer, run_conf: str):
    start = time.perf_counter_ns()
    size: int = 0

    # if run_conf == "octopus":
    #     with open(
    #         "/Users/valeriehayot-sasson/postdoc/mofka-docker/octopus-consumer.txt",
    #         "a+",
    #     ) as f:
    #         f.write("octopus consuming1")
    #         f.write("\n")

    while True:
        # if run_conf == "octopus":
        #     with open(
        #         "/Users/valeriehayot-sasson/postdoc/mofka-docker/octopus-consumer.txt",
        #         "a+",
        #     ) as f:
        #         f.write("in loop")
        #         f.write("\n")
        try:
            event = next(consumer)
            size += len(event)

            # if run_conf == "octopus":
            #     with open(
            #         "/Users/valeriehayot-sasson/postdoc/mofka-docker/octopus-consumer.txt",
            #         "a+",
            #     ) as f:
            #         f.write("event")
            #         f.write("\n")

        except Exception as e:
            # if run_conf == "octopus":
            #     with open(
            #         "/Users/valeriehayot-sasson/postdoc/mofka-docker/octopus-consumer.txt",
            #         "a+",
            #     ) as f:
            #         f.write("error " + str(e))
            #         f.write("\n")
            break
    end = time.perf_counter_ns()
    return f"{run_conf},consume,{size},{start},{end},{(end - start)/10**9}"
