from flask import Flask, request
import pika
import os
import json
from dotenv import load_dotenv

load_dotenv()

application = Flask(__name__)
amqp_url = os.environ.get('CLOUDAMQP_URL','empty')
exchange_name = os.environ.get('EXCHANGE_NAME','empty')

params = pika.URLParameters(amqp_url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

@application.route('/')
def hello_world():
    return 'Hello!'
  
@application.route('/create_deal', methods = ['POST'])
def create_deal():
    body = request.get_json()
    print(body)
    publish('create_deal_1', body)
    return " [x] Sent: %s" % body
  
@application.route('/create_deal_test', methods = ['POST'])
def create_deal_test():
    body = request.get_json()
    print(body)
    publish('create_deal_test_1', body)
    return " [x] Sent: %s" % body

@application.route('/update_payment_state', methods = ['POST'])
def update_payment_state():
    body = request.get_json()
    print(request.form)
    publish('update_payment_state_1', request.form)
    return 'OK'
    
@application.route('/update_paid_amount', methods = ['POST'])
def update_paid_amount():
    body = request.get_json()
    print(body)
    publish('update_paid_amount_1', body)
    return " [x] Sent: %s" % body
    
@application.route('/create_payment', methods = ['POST'])
def create_payment():
    body = request.get_json()
    print(body)
    publish('create_payment_1', body)
    return " [x] Sent: %s" % body
    
@application.route('/create_lead', methods = ['POST'])
def create_lead():
    print(request.form)
    if(request.form.get('test') == None):
        publish('create_lead_1', request.form)
        return " [x] Sent: %s" % request.form
    else:
        return 'done'
    
@application.route('/set_payment_type', methods = ['POST'])
def set_payment_type():
    body = request.get_json()
    print(body)
    if(body.get('paymentType') == 'Tinkoff' and body.get('amount') > 0):
        method = 'set_payment_type_1'#tinkoff
    else:
        method = 'set_payment_type_2'#zoho
    print(method)
    publish(method, body)
    return " [x] Sent: %s" % body
    
    
@application.route('/send_welcome_message', methods = ['POST'])
def send_welcome_message():
    body = request.get_json()
    print(body)
    publish('send_welcome_message_1', body)
    return " [x] Sent: %s" % body
    
    
@application.route('/send_suburb', methods = ['POST'])
def send_suburb():
    body = request.get_json()
    print(body)
    publish('send_suburb_1', body)
    return " [x] Sent: %s" % body

def publish(routing_key, body):
    params = pika.URLParameters(amqp_url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=json.dumps(body),
        properties=pika.BasicProperties(
            delivery_mode=2),  # make message persistent
        )
    connection.close()
    
if __name__ == '__main__':
    application.run(host='0.0.0.0')