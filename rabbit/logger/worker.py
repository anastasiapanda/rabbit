import pika
import os
import json
import traceback
import sys
from getpass import getpass
from mysql.connector import connect, Error
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

max_retries = int(os.environ.get('MAX_RETRIES',5))
amqp_url = os.environ.get('CLOUDAMQP_URL','')
queue_name = os.environ.get('QUEUE_NAME','')
ttl_ex_name = os.environ.get('TTL_EXCHANGE_NAME','')
host_db = os.environ.get('DB_HOST','')
database_db = os.environ.get('DB_NAME','')
user_db = os.environ.get('DB_USER','')
password_db = os.environ.get('DB_PASS','')

params = pika.URLParameters(amqp_url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

def publish(routing_key, body, prop):
    channel.basic_publish(
        exchange=ttl_ex_name,
        routing_key=routing_key,
        body=json.dumps(body),
        properties=prop,  # make message persistent
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
    try:
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
        if(count < max_retries):
            print('retry')
            publish(method.routing_key, d_body, properties)
            ch.basic_ack(delivery_tag = method.delivery_tag)
        else:
            print('Reach limit. Write to DB.')
            cnx = connect(
                host=host_db,
                database=database_db,
                user=user_db,
                password=password_db,
            )
            cursor = cnx.cursor()
            add_log = ('INSERT INTO logger '
                      '(createdt,routing_key,body,properties) '
                      'VALUES (%s, %s, %s, %s)')

            data_log = (properties.headers['x-death'][0]['time'] + timedelta(hours = 3), method.routing_key, str(d_body), str(properties))
            cursor.execute(add_log, data_log)
            cnx.commit()

            cursor.close()
            cnx.close()
            ch.basic_ack(delivery_tag = method.delivery_tag)
    except Exception as ex:
        PrintException()
        #ЛОГИРОВАНИЕ ex
        ch.basic_ack(delivery_tag = method.delivery_tag)


print(' [*] Waiting for message. To exit press CTRL+C')

channel.basic_consume(queue=queue_name, on_message_callback=callback)

channel.start_consuming()