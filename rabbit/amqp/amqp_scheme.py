# -*- coding: utf-8 -*-
import pika
import os
from dotenv import load_dotenv

load_dotenv()

print(os.environ.get('CLOUDAMQP_URL','empty'))
retry_delay = os.environ.get('RETRY_DELAY',60000)
amqp_url = os.environ.get('CLOUDAMQP_URL','empty')

main_ex_name = 'enso'
dlx_exchange_r1_name = 'retry'

def declare_main_queue(channel, queue_name, routing_keys):
    channel.queue_declare(queue=queue_name, durable=True, arguments={'x-dead-letter-exchange' : dlx_exchange_r1_name})
    for k in routing_keys:
        channel.queue_bind(exchange=main_ex_name, queue=queue_name, routing_key=k)#Основная ex
        channel.queue_bind(exchange=dlx_exchange_r1_name, queue=logger_queue_name, routing_key=k)#DLX ex
        channel.queue_bind(exchange=ex_wait, queue=ttl_queue_name, routing_key=k)#DLX ex



params = pika.URLParameters(amqp_url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

#Основной обменник
channel.exchange_declare(exchange=main_ex_name, exchange_type='direct', durable=True)

#DLX Нужно для повторной отправки сообщений и ожидания
#Первый DLX dlx_exchange_r1_name
channel.exchange_declare(exchange=dlx_exchange_r1_name, exchange_type='direct', durable=True)

#Очередь логгера logger_queue_name. Сюда приходит первично на логирование
logger_queue_name = 'retry.logger'
channel.queue_declare(queue=logger_queue_name, durable=True, arguments={ 'x-dead-letter-exchange' : dlx_exchange_r1_name})
#ex wait(можно сделать несколько. Одну на 6с, вторую на 60с)
ex_wait = 'wait'
channel.exchange_declare(exchange=ex_wait, exchange_type='direct', durable=True)
#Очередь ожидания ttl_queue_name
ttl_queue_name = 'wait.ttl'
channel.queue_declare(queue=ttl_queue_name, durable=True, arguments={ 'x-message-ttl' : int(retry_delay), 'x-dead-letter-exchange' : main_ex_name})




#Основные очереди
#Интеграция с Zoho
queue_name = 'enso.zoho'
declare_main_queue(channel, queue_name, ['create_deal_1', 'create_payment_1', 'update_payment_state_1','set_payment_type_2', 'update_paid_amount_1', 'create_lead_1', 'get_courier_text_1', 'send_welcome_message_1', 'send_suburb_1', 'print_stickers_1'])

#Интеграция с Tinkoff
queue_name = 'enso.tinkoff'
declare_main_queue(channel, queue_name, ['set_payment_type_1'])

#Интеграция с Wazzup
queue_name = 'enso.wazzup'
declare_main_queue(channel, queue_name, ['set_payment_type_3', 'send_welcome_message_2', 'send_suburb_2'])

#test
queue_name = 'enso.test'
declare_main_queue(channel, queue_name, ['get_test_1'])






#Интеграция с Telegram

#Интеграция с МойСклад

#Интеграция с Tilda

#Логи

