from dotenv import load_dotenv
load_dotenv()

import pika
import os
import traceback
import sys
from SDKInitializer import SDKInitializer
import create_payment_1 as cp
import set_payment_type_2 as spt
import update_payment_state_1 as ups
import update_paid_amount_1 as upa
import create_lead_1 as cl1
import get_courier_text_1 as gct1
import send_welcome_message_1 as swm1
import send_suburb_1 as ss1
import print_stickers_1 as ps1
import json

max_retries = int(os.environ.get('MAX_RETRIES',5))
amqp_url = os.environ.get('CLOUDAMQP_URL','asdf')
queue_name = os.environ.get('QUEUE_NAME','enso.zoho')
exchange_name = os.environ.get('EXCHANGE_NAME','enso')
print(amqp_url)
params = pika.URLParameters(amqp_url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

SDKInitializer.initialize(False)

def publish(exchange_name, routing_key, body, correlation_id):
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=json.dumps(body),
        properties=pika.BasicProperties(
            delivery_mode = 2,# make message persistent
            correlation_id = correlation_id),
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
    print(" [x] %r:%r %r" % (method.routing_key, body, properties))
    print(" [retry_count] : %s" % count)
    print(" [reason] : %s" % reason)
    try:
        if(method.routing_key == 'create_payment_1'):
            cp.create(d_body)
        elif(method.routing_key == 'set_payment_type_2'):
            spt.create(d_body)
            if(d_body.get('paymentType') != 'Наличные'):
                publish(exchange_name,'set_payment_type_3', d_body, None)
        elif(method.routing_key == 'update_payment_state_1'):#tinkoff
            d_body = json.loads(list(d_body.keys())[0])
            deal_id = ups.update(d_body)
            if(deal_id != None):
                d_body['Deal'] = deal_id
                publish(exchange_name,'update_paid_amount_1', d_body, None)
        elif(method.routing_key == 'update_paid_amount_1'):
            upa.update(d_body)
        elif(method.routing_key == 'create_lead_1'):
            cl1.create(d_body)
        elif(method.routing_key == 'get_courier_text_1'):
            #rpc
            resp = gct1.get(d_body)
            publish('',properties.reply_to, resp, properties.correlation_id)
        elif(method.routing_key == 'send_welcome_message_1'):
            result = swm1.generate(d_body)
            publish(exchange_name,'send_welcome_message_2', result, None)
        elif(method.routing_key == 'send_suburb_1'):
            result = ss1.generate(d_body)
            if(result.get('message') != ''):
                publish(exchange_name,'send_suburb_2', result, None)
        elif(method.routing_key == 'print_stickers_1'):
            #rpc
            resp = ps1.get(d_body)
            publish('',properties.reply_to, resp, properties.correlation_id)
        else:
            raise Exception('Unknown method - '+ method)
        print('acking')
        ch.basic_ack(delivery_tag = method.delivery_tag)
    except Exception as ex:
        PrintException()
        #ЛОГИРОВАНИЕ ex
        print('rejecting (retry via DLX)')
        ch.basic_reject(delivery_tag = method.delivery_tag, requeue=False)
    print('stop wait')


print(' [*] Waiting for message. To exit press CTRL+C')

channel.basic_consume(queue=queue_name, on_message_callback=callback)

channel.start_consuming()

