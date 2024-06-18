import pika
import os
import json
import traceback
import sys
import set_payment_type_1 as spt
from dotenv import load_dotenv

load_dotenv()

max_retries = int(os.environ.get('MAX_RETRIES',5))
amqp_url = os.environ.get('CLOUDAMQP_URL','amqps://ifdhuibo:PqNtEV2d6fhTXz8DF0wlCLyWNTCDtbu5@stingray.rmq.cloudamqp.com/ifdhuibo')
queue_name = os.environ.get('QUEUE_NAME','enso.tinkoff')
exchange_name = os.environ.get('EXCHANGE_NAME','enso')

params = pika.URLParameters(amqp_url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

def publish(routing_key, body):
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=json.dumps(body),
        properties=pika.BasicProperties(
            delivery_mode=2),  # make message persistent
        )

def PrintException():
    try:
        exc_info = sys.exc_info()

        # do you usefull stuff here
        # (potentially raising an exception)
        try:
            raise TypeError("Again !?!")
        except:
            pass
        # end of useful stuff


    finally:
        # Display the *original* exception
        traceback.print_exception(*exc_info)
        del exc_info

def callback(ch, method, properties, body):
    d_body = json.loads(body.decode('utf-8'))
    if(properties.headers == None):
        count = 0
        reason = 'none'
    else:
        count = properties.headers['x-death'][0]['count']
        reason = (properties.headers['x-death'][0]['reason'])
    print(" [x] %r:%r %r" % (method.routing_key, d_body, properties))
    print(" [retry_count] : %s" % count)
    print(" [reason] : %s" % reason)
    if(count < max_retries):
        try:
            if(method.routing_key == 'set_payment_type_1'):
                result = spt.create(d_body)
                print(result)
                d_body['link'] = result['PaymentURL']
                d_body['tinkoffPaymentID'] = result['PaymentId']
                publish('set_payment_type_2', d_body)
            else:
                raise Exception('Unknown method - '+ method)
            print('acking')
            ch.basic_ack(delivery_tag = method.delivery_tag)
        except Exception as ex:
            PrintException()
            #ЛОГИРОВАНИЕ ex
            print('rejecting (retry via DLX)')
            ch.basic_reject(delivery_tag = method.delivery_tag, requeue=False)
    else:
        print('max retries reached - acking')
        #ДОБАВИТЬ ЛОГИРОВАНИЕ!!!!!!!!!!!!!!!!!!
        ch.basic_ack(delivery_tag = method.delivery_tag)
    print('stop wait')


print(' [*] Waiting for message. To exit press CTRL+C')

channel.basic_consume(queue=queue_name, on_message_callback=callback)

channel.start_consuming()