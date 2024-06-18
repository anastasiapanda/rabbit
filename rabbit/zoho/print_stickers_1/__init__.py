import inspect#getfullargspec
import json
from datetime import datetime
import traceback
import sys

import zcrmsdk.src.com.zoho.crm.api.related_records as rel
from zcrmsdk.src.com.zoho.crm.api.record import Record as ZCRMRecord
import zcrmsdk.src.com.zoho.crm.api.record as rec
from zcrmsdk.src.com.zoho.crm.api.util import Choice, StreamWrapper
import zcrmsdk.src.com.zoho.crm.api.query as q
from zcrmsdk.src.com.zoho.crm.api.related_lists import *


#/app
def get(body):
    result = ''
    try:
        print('body: ', body)
        deals_ids = str(body.get('ids')).split('|||')
        packages = get_coql(get_query_texts(deals_ids))
        for deals in packages:
            for deal in deals:
                goods_count = deal.get_key_value('goods_count')
                is_first = True
                for p in range(1,goods_count+1):
                    result += '\\b' + str(deal.get_key_value('DailyID')) + '\\s\\s\\s\\s\\b'+ str(p) + '\\b/' + '\\b' + str(goods_count) + '|||'
                    for t in deal.get_key_value('pickerText').split('\n'):
                        result += t+'|||'
                    if(is_first):
                        is_first = False
                        result += 'Карточка:'+(deal.get_key_value('cardText')[:35] if deal.get_key_value('cardText') else '')+'//|'
                    else:
                        result += 'Карточка:'+('СМОТРИТЕ В ЗАЯВКЕ' if deal.get_key_value('cardText') else '')+'//|'
    except Exception as ex:
        PrintException()
        result = str(ex)
        #ЛОГИРОВАНИЕ ex
    print(result)
    return result

def get_query_texts(deals):
    result = []
    select_query = '''
    select id, DailyID, goods_count, pickerText, cardText
    from Deals
    where '''
    where_ids = ''
    is_first = True
    i = 0
    for d in deals:
        i += 1
        if(not is_first):
            where_ids = '(' + where_ids + ' or '
        where_ids += '(id=' + d + ')'
        if(is_first):
            is_first = False
        else:
            where_ids += ')'
        if(i == 24):
            is_first = True
            i = 0
            result.append(select_query + where_ids + '\nlimit 200')
            where_ids = ''
    if(i != 0):
        result.append(select_query + where_ids + '\nlimit 200')
    return result
    
    
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

''''''''''''''''''''''''''''''''''''
'''''''''GET МЕТОДЫ НАЧАЛО'''''''''
''''''''''''''''''''''''''''''''''''

def get_record(record_id, module_name):
    response = rec.RecordOperations().get_record(int(record_id), module_name, None, None)
    data = get_response_data(response)
    if(len(data)==0):
        return None
    else:
        return data[0]#Потому что только один ID может быть
    
def get_related_records(related_list_api_name, record_id, module_api_name):
    response = rel.RelatedRecordsOperations(related_list_api_name, record_id, module_api_name).get_related_records(None, None)
    data = get_response_data(response)
    if(data == None):
        return []
    else:
        return data
        
def get_coql(select_queries):
    result = []
    for select_query in select_queries:
        # Get instance of BodyWrapper Class that will contain the request body
        body_wrapper = q.BodyWrapper()

        body_wrapper.set_select_query(select_query)
        print(select_query)
        response = q.QueryOperations().get_records(body_wrapper)
        
        data = get_response_data(response)
        if(data != None):
            result.append(data)
        #else:
        #    return []
    return result
    

''''''''''''''''''''''''''''''''''''
''''''''''GET МЕТОДЫ КОНЕЦ'''''''''
''''''''''''''''''''''''''''''''''''
    
''''''''''''''''''''''''''''''''''''
'''''''''CHANGE МЕТОДЫ НАЧАЛО'''''''''
''''''''''''''''''''''''''''''''''''

def create_record(module_api_name, record):
    #Для одной записи. Поэтому в конце data[0]
    request = create_request([record])
    response = rec.RecordOperations().create_records(module_api_name, request)
    check_change_response(response)
    
def update_record(record_id, module_api_name, record):
    response = rec.RecordOperations().update_record(record_id, module_api_name, create_request([record]))
    check_change_response(response)
    
def delete_record(record_id, module_api_name):
    response = rec.RecordOperations().delete_record(record_id, module_api_name, None)
    check_change_response(response)
    
''''''''''''''''''''''''''''''''''''
'''''''''CHANGE МЕТОДЫ КОНЕЦ'''''''''
''''''''''''''''''''''''''''''''''''
    
''''''''''''''''''''''''''''''''''''''''''''''''''''''
'''''''''ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ НАЧАЛО'''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''

    #Генерим обёртку для change методов
def create_request(record_list):
    request = rec.BodyWrapper()
    request.set_data(record_list)
    # Set the list containing the trigger operations to be run
    # Хз, говорит нет такого метода
    #print(dir(request))
    #trigger = ["approval", "workflow", "blueprint"]
    #request.set_trigger(trigger)
    return request
    
    #Проверяем, что нет ошибок после выполнения change методов
def check_change_response(response):
    data = get_response_data(response)
    if exception_instance(data[0]):
        throw_error(response)
    else:
        # Get the Status
        print("Status: " + data[0].get_status().get_value())

        # Get the Code
        print("Code: " + data[0].get_code().get_value())

        print("Details")

        # Get the details dict
        details = data[0].get_details()

        for key, value in details.items():
            print(key + ' : ' + str(value))

        # Get the Message
        print("Message: " + data[0].get_message().get_value())
    
    #Проверить и получить данные из ответа
def get_response_data(response):
    if(response.get_status_code() == 204):#No Content. HTTP 204. There is no content available for the request. Только для 
        return None
    else:
        response_o = response.get_object()
        if exception_instance(response_o):
            throw_error(response_o)
        else:
            return response_o.get_data()
            
def exception_instance(response_o):
    return (isinstance(response_o, rec.APIException)) or (isinstance(response_o, rel.APIException)) or (isinstance(response_o, q.APIException))
    
    
def get_prod_for_payment(p_id, name, quantity, price):
    result = {}
    result['id'] = p_id
    result['name'] = name
    result['quantity'] = quantity
    result['price'] = price
    return result
    
    
def throw_error(response):
    # Get the Status
    error = "Status: " + response.get_status().get_value()
    # Get the Code
    error += "\nCode: " + response.get_code().get_value()
    
    # Get the details dict
    error += "\nDetails"
    details = response.get_details()
    for key, value in details.items():
        error += '\n' + key + ' : ' + str(value)
    # Get the Message
    error += "\nMessage: " + response.get_message().get_value()
    raise Exception(error)
    
''''''''''''''''''''''''''''''''''''''''''''''''''''''
'''''''''ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ КОНЕЦ'''''''''
''''''''''''''''''''''''''''''''''''''''''''''''''''''