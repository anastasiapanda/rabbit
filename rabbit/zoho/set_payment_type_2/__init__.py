import json
from zcrmsdk.src.com.zoho.crm.api.record import Record as ZCRMRecord
import zcrmsdk.src.com.zoho.crm.api.record as rec
from zcrmsdk.src.com.zoho.crm.api.util import Choice, StreamWrapper


#/app
def create(body):
    record = ZCRMRecord()
    record.add_key_value('PaymentType', Choice(body.get('paymentType')))
    if('tinkoffPaymentID' in body):
        record.add_key_value('Link', body.get('link'))
        record.add_key_value('TinkoffPaymentID', body.get('tinkoffPaymentID'))
    update_record(int(body.get('paymentID')), 'Payments', record)


''''''''''''''''''''''''''''''''''''
'''''''''GET МЕТОДЫ НАЧАЛО'''''''''
''''''''''''''''''''''''''''''''''''



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
        throw_error(data[0])
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