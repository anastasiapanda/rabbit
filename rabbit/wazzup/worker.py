from dotenv import load_dotenv
load_dotenv()

import pika
import os
import wazzup
import traceback
import sys
import json

amqp_url = os.environ.get('CLOUDAMQP_URL','')
queue_name = os.environ.get('QUEUE_NAME','')
exchange_name = os.environ.get('EXCHANGE_NAME','')

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
    print(" [x] %r:%r %r" % (method.routing_key, body, properties))
    print(" [retry_count] : %s" % count)
    print(" [reason] : %s" % reason)
    try:
        if(method.routing_key == 'set_payment_type_3'):
            if(d_body.get('paymentType') == 'Tinkoff'):
                if(d_body.get('amount')>=0):
                    message = 'Вот ссылка на оплату:\n'
                    message += d_body.get('link')
                    wazzup.send_message(d_body.get('phone'), message)
                else:
                    wazzup.send_message('79067955600', '1284329:'+d_body.get('orderID'))
            elif(d_body.get('amount')>=0):
                if(d_body.get('paymentType') == 'Перевод'):
                    message = 'Пожалуйста, отправьте скрин перевода для бухгалтерии. Номер телефона для перевода:\n+79772509980\nНомер карты Сбербанк для перевода:'
                    wazzup.send_message(d_body.get('phone'), message)
                    message = '5228600598844332'
                    wazzup.send_message(d_body.get('phone'), message)
                elif(d_body.get('paymentType') == 'Наличные'):
                    raise Exception('По типу "Наличные" не должны отправляться сообщения')
        elif(method.routing_key == 'send_welcome_message_2'):
            wazzup.send_message(d_body.get('phone'), d_body.get('message'))
        elif(method.routing_key == 'send_suburb_2'):
            wazzup.send_message(d_body.get('phone'), d_body.get('message'))
        else:
            raise Exception('Unknown method - '+ method.routing_key)
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

