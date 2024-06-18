import json
import requests
from set_payment_type_1.Init_Request import Init_Request

def create(body):
    init = Init_Request(body.get('orderID'), body.get('email'), body.get('phone'))
    products = json.loads(body.get('productsList'))
    discount = 0
    for prod in products:
        if(prod.get('price') < 0.0):
            discount-= int(prod.get('price') * prod.get('quantity') *100)
    for prod in products:
        price = prod.get('price')
        if(price > 0.0):
            discount = -init.add_item(prod.get('name'), prod.get('quantity'), price, discount)
    if(init.amount <= 0):
        raise Exception('Amount <= 0')
    headers = {'Content-type': 'application/json',  # Определение типа данных
           'Accept': 'text/plain',
           'Content-Encoding': 'utf-8'}
    data = json.dumps(init, indent=4, cls=CustomEncoder)
    resp = requests.post('https://securepay.tinkoff.ru/v2/Init/', data=data, headers=headers)
    return resp.json()
    
class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if "tojson" in dir(o):
            return o.tojson()
        return json.JSONEncoder.default(self, o)

