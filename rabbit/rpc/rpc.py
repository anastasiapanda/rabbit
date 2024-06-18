from flask import Flask, request
import pika
import os
import json
import uuid
from dotenv import load_dotenv

load_dotenv()

application = Flask(__name__)
amqp_url = os.environ.get('CLOUDAMQP_URL','empty')
exchange_name = os.environ.get('EXCHANGE_NAME','empty')

class RpcClient(object):

    def __init__(self, exchange, routing_key):
        params = pika.URLParameters(amqp_url)
        self.connection = pika.BlockingConnection(params)

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)
        self.exchange = exchange
        self.routing_key = routing_key

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, body):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.routing_key,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(body))
        while self.response is None:
            self.connection.process_data_events()
        return self.response

@application.route('/')
def hello_world():
    return 'Hello!'
  
@application.route('/get_courier_text', methods = ['POST'])
def get_courier_text():
    body = request.get_json()
    print(body)
    rpc = RpcClient(exchange_name, 'get_courier_text_1')
    print(" [x] Requesting: %s " % body)
    response = rpc.call(body)
    print(" [.] Got %r" % response.decode('unicode-escape'))
    return response.decode('unicode-escape')
  
@application.route('/print_stickers', methods = ['POST'])
def print_stickers():
    body = request.get_json()
    print(body)
    rpc = RpcClient(exchange_name, 'print_stickers_1')
    print(" [x] Requesting: %s " % body)
    response = rpc.call(body)
    print(" [.] Got %r" % response.decode('unicode-escape'))
    return response.decode('unicode-escape')
    
if __name__ == '__main__':
    application.run()