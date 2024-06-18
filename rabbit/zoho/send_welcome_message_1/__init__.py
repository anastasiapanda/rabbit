import json
import zcrmsdk.src.com.zoho.crm.api.related_records as rel
from zcrmsdk.src.com.zoho.crm.api.record import Record as ZCRMRecord
import zcrmsdk.src.com.zoho.crm.api.record as rec
from zcrmsdk.src.com.zoho.crm.api.util import Choice, StreamWrapper

#/app
def generate(body):
    print('body: ', body)
    deal = get_record(body.get('id'), 'Deals')
    is_error_not_2 = False
    errors = deal.get_key_value('errors') if deal.get_key_value('errors') else ''
    #Проверка на просрочку
    expired_products = ''
    expired_count = 0
    closing_date = deal.get_key_value('Closing_Date')
    for k in json.loads(deal.get_key_value('TechGoods').replace(',\n}','\n}')):
        prod = get_record(k,'Products')
        category = prod.get_key_value("Product_Category");
        print(type(prod.get_key_value("valid_until_date")))
        print(type(closing_date))
        if(prod.get_key_value("valid_until_date") is not None and prod.get_key_value("valid_until_date") < closing_date):
            expired_products += prod.get_key_value("Product_Name") + "\n";
            expired_count += 1
            errors += 'Error_3:Просрочка '+prod.get_key_value("Product_Name")+'\n'
            is_error_not_2 = True
    
    welcome_text = ''
    welcome_text += 'Здравствуйте '+deal.get_key_value('Contact_Name').get_key_value('name')+', ваш заказ №'+str(deal.get_key_value('orderID'))+' принят в работу.\n'
    welcome_text += 'Доставка ' + str(deal.get_key_value('Closing_Date')) + ' ' + deal.get_key_value('deliveryTime') +'.\n'

    products = deal.get_key_value('Goods')

    delivery = products.split('\n')[-1]
    if('Самовывоз'.lower() in delivery.lower()):
        d_type = 0
    elif('интервале'.lower() in delivery.lower()):
        d_type = 1
    elif('за мкад'.lower() in delivery.lower()):
        d_type = 2
        errors += 'Error_2:Стоимость за МКАД\n'
    else:
        d_type = -1#error

    welcome_text += products + '\n'

    welcome_text += 'Итого: ' + str(deal.get_key_value('Amount')) + '\n'

    if(deal.get_key_value('deliveryAddress') is not None):
        welcome_text += 'Адрес: '+ deal.get_key_value('deliveryAddress') + '\n'
    if(deal.get_key_value('addInfo') is not None):
        welcome_text += 'Доп. инфо: '+ deal.get_key_value('addInfo') + '\n'
    if(deal.get_key_value('receiverPhone') is not None):
        welcome_text += 'Имя и телефон получателя: '
        if(deal.get_key_value('receiverName') is not None):
            welcome_text += deal.get_key_value('receiverName') + ' '
        welcome_text += deal.get_key_value('receiverPhone') + '\n'
    if(deal.get_key_value('approve') is not None):
        if(deal.get_key_value('approve').get_value() == 'Согласовать'):
            welcome_text += 'Согласовать с получателем дату и время\n'
        elif(deal.get_key_value('approve').get_value() == 'Согласовать + сюрприз'):
            welcome_text += 'Согласовать с получателем дату и время, но сохранить сюрприз\n'
        else:
            welcome_text += 'Не звонить получателю\n'
    if(deal.get_key_value('is_call_before_leaving') is not None and deal.get_key_value('is_call_before_leaving') == True):
        welcome_text += 'Позвонить перед выездом\n'

    if(expired_products != ''):
        if(expired_count == 1):
            welcome_text += '\nСледующий продукт не будет доступен в указанную вами дату:\n'
        else:
            welcome_text += '\nСледующие продукты не будут доступны в указанную вами дату:\n'
        welcome_text += expired_products

    for_us = deal.get_key_value("ForUs")
    if('error_4' in errors.lower()):
        welcome_text += 'Вы заказали букет через предзаказ, хотя букет уже был на сайте, нам нужно подсчитать букеты.\n'
        is_error_not_2 = True
    if(is_error_not_2 and d_type == 2):
        welcome_text += '\nМы придумаем решения для проблем выше, рассчитаем стоимость доставки и вернёмся к вам :)\n'
    elif(d_type == 2):
        welcome_text += '\nМы рассчитаем стоимость доставки и вернёмся к вам :)\n'
    elif(is_error_not_2):
        welcome_text += '\nМы придумаем решения для проблем выше и вернёмся к вам :)\n'
    else:
        welcome_text += '\nВсё верно?\n'
    welcome_text += '\nОбращаем ваше внимание, что все позиции на сайте полностью соответствуют фото и мы не высылаем его на подтверждение. Если вам всё же нужно фото именно вашего букета, то напишите нам :)\n'
    if(d_type == 0):
        welcome_text += '\nПозвоните, пожалуйста, за 5-10 минут, чтобы мы успели подготовить заказ и Вам не пришлось ждать :)\nАдрес: Нижняя Красносельская улица, 35с7. https://yandex.ru/maps/-/CCUFESQgcB'
        #welcome_text += 'Инструкция, как нас найти:\nhttps://yandex.ru/maps/-/CCUAiUVsSB\nДверь с цифрой 3\nНа всякий случай текстом)\nБольшая Татарская 35с7-9\nВход в серую арку напротив Магнита (между ТВЦ и Лавкой Братьев Караваевых), если Вы на автомобиле, то позвоните нам заранее и мы закажем пропуск. После охраны направо, увидите длинное красное здание, дойдите до него и поверните налево. Пройдя вдоль здания мимо" + " школы рисования и главного входа, увидите справа сквозной проход (арку) через само здание. Можете позвонить нам, как пройдете в него. Вдали увидите серую железную дверь с цифрой 3. Мы на третьем, серая дверь, на этаже можно позвонить на телефон или в звоночек'
    welcome_text += '\nПодписывайтесь на нас в телеграм :) https://t.me/ensoflowerslive'
    if(errors != ''):
        updatedDeal = ZCRMRecord()
        updatedDeal.add_key_value('errors', errors)
    else:
        updatedDeal = ZCRMRecord()
        updatedDeal.add_key_value('Stage', Choice('Подтверждается'))
    update_record(int(body.get('id')), 'Deals', updatedDeal)
    result = {'phone':deal.get_key_value('Contact_Phone'),
            'message':welcome_text}
    return result


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