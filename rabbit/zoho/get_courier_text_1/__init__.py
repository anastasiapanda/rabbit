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

default_payment_type = 'Не выбрано'

#/app
def get(body):
    result = ''
    try:
        print('body: ', body)
        main_deal = get_record(body.get('id'), 'Deals')
        deals = get_coql(get_query_text(main_deal))
        deals_sorted = sorted(deals, key=lambda deal: (deal.get_key_value('DeliveryNumber') is None, deal.get_key_value('DeliveryNumber')))
        for deal in deals_sorted:
            closing_date = datetime.strptime(deal.get_key_value("Closing_Date"), '%Y-%m-%d')
            #DailyID ДОБАВИТЬ
            result += (deal.get_key_value('DeliveryNumber') + ' - ') if deal.get_key_value('DeliveryNumber') else ''
            result += str(deal.get_key_value('DailyID')) + '|||'
            result += str(deal.get_key_value('id')) + '|||'
            result += closing_date.strftime('%d-%m-%Y') + ' ' + deal.get_key_value('deliveryTime') + '|||';
            result += 'Позиций: ' + str(deal.get_key_value('goods_count')) + '|||'
            result += 'Заказчик: ' + deal.get_key_value('Contact_Name.Last_Name') + ' ' + deal.get_key_value('Contact_Name.Phone') + '|||'
            
            if(deal.get_key_value('approve') is not None and deal.get_key_value('approve') == 'Не звонить вообще'):
                result += 'Получатель: ' + (deal.get_key_value('receiverName') if deal.get_key_value('receiverName') else '') + ' (По всем вопросам звонить заказчику)|||'
            else:
                if(deal.get_key_value('receiverPhone') is not None):
                    result += 'Получатель: ' + (deal.get_key_value('receiverName') if deal.get_key_value('receiverName') else '') + ' ' + deal.get_key_value('receiverPhone') + '|||'
            if(deal.get_key_value('is_call_before_leaving') is not None and deal.get_key_value('is_call_before_leaving') == True):
                result += 'Позвонить перез выездом|||'
            result += deal.get_key_value('deliveryAddress') + '|||'
            if(deal.get_key_value('addInfo') is not None):
                result += deal.get_key_value('addInfo') + '|||'
            if(deal.get_key_value('courierInfo') is not None):
                result += deal.get_key_value('courierInfo') + '|||'
            paymentState = deal.get_key_value('PaymentState')
            if(paymentState == 'Полностью'):
                result += 'Оплачен'
            else:
                result += 'К оплате ' + str(deal.get_key_value('Amount') - (deal.get_key_value('PaidAmount') if deal.get_key_value('PaidAmount') else 0))
            result += '|||' + '|||'
    except Exception as ex:
        PrintException()
        result = str(ex)
        #ЛОГИРОВАНИЕ ex
    print(result)
    return result

def get_query_text(deal):
    select_query = '''
    select id, DailyID, orderID, DeliveryNumber, Closing_Date, goods_count, deliveryTime, Contact_Name.Last_Name, Contact_Name.Phone, receiverPhone, receiverName, is_call_before_leaving, deliveryAddress, addInfo, courierInfo, PaymentState, Amount, PaidAmount, approve
    from Deals
    where (((Closing_Date =\''''+str(deal.get_key_value('Closing_Date'))+'''\' and Probability<90) and Probability!=0) and courier '''
    if(deal.get_key_value('courier') == None):
        select_query += 'is null'
    else:
        select_query += '=\''+deal.get_key_value('courier').get_value()+'\''
    select_query += ')\nlimit 200'
    return select_query
    
    
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
        
def get_coql(select_query):
    # Get instance of BodyWrapper Class that will contain the request body
    body_wrapper = q.BodyWrapper()

    body_wrapper.set_select_query(select_query)
    response = q.QueryOperations().get_records(body_wrapper)
    
    data = get_response_data(response)
    if(data == None):
        return []
    else:
        return data
    

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