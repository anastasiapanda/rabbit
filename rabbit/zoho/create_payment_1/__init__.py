from decimal import Decimal
import inspect#getfullargspec
import json
import zcrmsdk.src.com.zoho.crm.api.related_records as rel
from zcrmsdk.src.com.zoho.crm.api.record import Record as ZCRMRecord
import zcrmsdk.src.com.zoho.crm.api.record as rec
from zcrmsdk.src.com.zoho.crm.api.util import Choice, StreamWrapper

from zcrmsdk.src.com.zoho.crm.api.related_lists import *

default_payment_type = 'Не выбрано'

#/app
def create(body):
    print('body: ', body)
    so_id = int(body.get('soid'))
    so = get_record(so_id, 'Sales_Orders')
    deal = get_record(so.get_key_value('Deal_Name').get_key_value('id'), 'Deals')
    order_id = deal.get_key_value('orderID')
    if(so != None):
        so_products = so.get_key_value('Product_Details')
        so_prod_dict = {}
        for prod in so_products:
            key = str(prod.get_key_value('product').get_key_value('id'))+'_'+str(prod.get_key_value('net_total')/prod.get_key_value('quantity'))#Потому что прайса после скидки нет в данных
            so_prod_dict[key] = {'info':prod, 'quantity': int(prod.get_key_value('quantity'))}
        
        isSurcharge = False
        updating_payment_id = 0
        max_number = 0
        amount = so.get_key_value('Grand_Total')
        paidAmount = 0.0
        #Тут пробегаемся по сгенерированным оплатам и откидываем те, по которым уже были созданы.
        payments = json.loads(body.get('payments'))
        for p in payments:
            if(p.get('PaymentType') != None and p.get('PaymentType') != default_payment_type):
                if('-' in p.get('TinkoffOrderID')):
                    number = int(p.get('TinkoffOrderID').split('-')[-1])
                    if(number > max_number):
                        max_number = number
                if(p.get('State') == 'Оплачено'):
                    paidAmount += p.get('Amount')
                pp = json.loads(p.get('ProductsList'))#payment_products
                if(~isSurcharge):
                    for prod in pp:
                        key = str(prod.get('id'))+'_'+str(prod.get('price'))
                        if((key in so_prod_dict) and (so_prod_dict[key]['quantity']) >= prod.get('quantity')):
                            so_prod_dict[key]['quantity'] -= prod.get('quantity')
                        else:
                            isSurcharge = True
                amount -= p.get('Amount')
            else:
                #Запомнить первый ID для изменения, остальных после него вообще не должно быть, просто на всякий кинуть еррор
                if(updating_payment_id == 0):
                    updating_payment_id = int(p.get('id'))
                else:
                    raise Exception('Error. У сделки больше одной неотправленной оплаты id='+deal.get_id())
        # Собираем продукты, которые должны быть пробиты в заказах
        p_products = []
        if(amount<0):
            p_products.append(get_prod_for_payment(0, 'Возврат по заказу №'+order_id, 1, amount))
        elif(isSurcharge):
            p_products.append(get_prod_for_payment(0, 'Доплата по заказу №'+order_id, 1, amount))
        else:
            for k, v in so_prod_dict.items():
                if(v['quantity']>0 and v['info'].get_key_value('net_total') != 0):
                    prod_info = v['info']
                    p_products.append(get_prod_for_payment(prod_info.get_key_value('product').get_key_value('id'),
                            prod_info.get_key_value('product').get_key_value('name'),
                            v['quantity'],
                            prod_info.get_key_value('net_total')/prod_info.get_key_value('quantity')))
        
        d_r = ZCRMRecord()
        if(len(p_products)!=0):
            record = ZCRMRecord()
            record.add_key_value('ProductsList', json.dumps(p_products, ensure_ascii=False, default=str))
            record.add_key_value('Amount', round(amount,2))
            print('amount = ' + str(amount))
            if(updating_payment_id == 0):
                if('tOrderId' in body and body.get('tOrderId') != None):#Первое создание
                    t_order_id = body.get('tOrderId')
                else:
                    t_order_id = order_id+'-'+str(max_number+1)
                if('payment_type' in body and body.get('payment_type') != None):#Первое создание
                    record.add_key_value('PaymentType', Choice(body.get('payment_type')))
                else:
                    record.add_key_value('PaymentType', Choice(default_payment_type))
                record.add_key_value('TinkoffOrderID', t_order_id)
                record.add_key_value('Name', 'Оплата по заказу №'+order_id)
                record.add_key_value('State', Choice('Не оплачено'))
                deal_name = ZCRMRecord()
                deal_name.add_key_value('id', deal.get_id())
                record.add_key_value('Deal',deal_name)
            if(updating_payment_id == 0):
                create_record('Payments', record)
            else:
                update_record(updating_payment_id, 'Payments', record)
        elif(amount <= 0):#Нужно удалить все неоплаченные
            for p in payments:
                if(p.get('State') != 'Оплачено'):
                    delete_record(int(p.get('id')), 'Payments')
            result = deal.get_id()
            
        if(paidAmount == 0):
            d_state = 'Нет'
        elif(paidAmount != so.get_key_value('Grand_Total')):
            d_state = 'Частично'
        else:
            d_state = 'Полностью'
        if(paidAmount != deal.get_key_value('PaidAmount')):
            d_r.add_key_value('PaidAmount', paidAmount)
        if(deal.get_key_value('PaymentState').get_value() != d_state):
            d_r.add_key_value('PaymentState', Choice(d_state))
        if(len(d_r.get_key_values()) != 0):
            update_record(deal.get_id(), 'Deals', d_r)
    else:
        raise Exception('so is emptry')


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
    return (isinstance(response_o, rec.APIException)) or (isinstance(response_o, rel.APIException)) 
    
    
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