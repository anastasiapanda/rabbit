import os
import json
from hashlib import sha256
from set_payment_type_1.Receipt import Receipt

class Init_Request():
    def __init__(self, order_id, email, phone):
        self.amount = 0
        self.description = 'Оплата по заказу '+str(order_id)
        self.order_id = order_id
        self.terminal_key = os.environ.get('TERMINAL_KEY','1559724026236')
        self.receipt = Receipt(email, phone)
    
    def generate_token(self):
        password = os.environ.get('TERMINAL_PASS','a9y8l7mg37ihjwv4')
        token = str(int(self.amount))+ self.description + self.order_id + password + self.terminal_key
        self.token = sha256(token.encode('utf-8')).hexdigest()
        
    def add_item(self, name, quantity, price, discount):
        result = self.receipt.add_item(name, quantity, price, discount)
        if(result > 0):
            self.amount += result
            return 0;
        else:
            return result
    
    def tojson(self):
        self.generate_token()
        return {
            'Amount':self.amount,
            'Description':self.description,
            'OrderId':self.order_id,
            'TerminalKey':self.terminal_key,
            'Token': self.token,
            'Receipt':self.receipt,
        }