import json
from zcrmsdk.src.com.zoho.crm.api.record import Record as ZCRMRecord
import zcrmsdk.src.com.zoho.crm.api.record as rec
from zcrmsdk.src.com.zoho.crm.api.util import Choice, StreamWrapper
from zcrmsdk.src.com.zoho.crm.api import ParameterMap
import zcrmsdk.src.com.zoho.crm.api.query as q
import time

#/app
def update(body):
    deal_id = body.get('Deal')
    deal_info = get_record(deal_id, 'Deals')
    query = '''SELECT State, Amount
FROM Payments
WHERE Deal = ''' + str(deal_id)

    rr = get_coql(query)
    paid_amount = 0.0
    for r in rr:
        if(r.get_key_value('State') == 'Оплачено'):
            paid_amount += float(r.get_key_value('Amount'))
    rec = ZCRMRecord()
    rec.add_key_value('PaidAmount', paid_amount)
    if(deal_info.get_key_value('Amount') == paid_amount):
        rec.add_key_value('PaymentState', Choice('Полностью'))
    else:
        if(paid_amount != 0.0):
            rec.add_key_value('PaymentState', Choice('Частично'))
        else:
            rec.add_key_value('PaymentState', Choice('Нет'))
    if(deal_info.get_key_value('PaidAmount') != paid_amount):
        update_record(int(deal_id), 'Deals', rec)

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

def update_record(record_id, module_api_name, record):
    response = rec.RecordOperations().update_record(record_id, module_api_name, create_request([record]))
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
    return (isinstance(response_o, rec.APIException))
    
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