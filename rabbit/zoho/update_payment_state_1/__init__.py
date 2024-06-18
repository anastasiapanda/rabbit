import json
from zcrmsdk.src.com.zoho.crm.api.record import Record as ZCRMRecord
import zcrmsdk.src.com.zoho.crm.api.record as rec
from zcrmsdk.src.com.zoho.crm.api.util import Choice, StreamWrapper
from zcrmsdk.src.com.zoho.crm.api import ParameterMap


#/app
def update(body):
    print(body)
    print(body.get('Status'))
    if(body.get('Status') == 'CONFIRMED'):
        p = search_records('(TinkoffOrderID:equals:'+body.get('OrderId')+')', 'Payments')
        if(p == None):
            raise Exception('I dont get payments')
        if(p[0].get_key_value('State') == None or p[0].get_key_value('State').get_value() != 'Оплачено'):
            record = ZCRMRecord()
            record.add_key_value('State', Choice('Оплачено'))
            update_record(int(p[0].get_key_value('id')), 'Payments', record)
            return p[0].get_key_value('Deal').get_id()
        else:
            return None
    else:
        return None


''''''''''''''''''''''''''''''''''''
'''''''''GET МЕТОДЫ НАЧАЛО'''''''''
''''''''''''''''''''''''''''''''''''

def search_records(criteria, module_name):
    param_instance = ParameterMap()
    param_instance.add(rec.SearchRecordsParam.criteria, criteria)
    response = rec.RecordOperations().search_records(module_name, param_instance)
    data = get_response_data(response)
    return data#Потому что только один ID может быть

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