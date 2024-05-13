# Example app

The goal of this example is to demonstrate how Mofka could be used within the DSaaS applications for data communication within sites where outbound connection is not available on compute nodes.

### How to run

The DSaaS client must be installed to run this code. To download:

`pip install git+https://github.com/nsf-resume/dsaas-client.git`

Start the Bedrock server

`bedrock ofi+tcp -c config.json &`

On a login node, fetch data from DSaaS and publish as an event. The example app requires two data inputs, therefore this needs to be executed twice for each input.

```
python example-app/mofka-login-producer.py source_1 1
python example-app/mofka-login-producer.py source_2 2
```

On a compute node, consume the events and retrieve associated data inputs, perform computation and publish the report as a event to Mofka

```
python example-app/app.py
```

Back on the login node, consume the report event and publish to DSaaS

```
python example-app/mofka-login-consumer.py
```


