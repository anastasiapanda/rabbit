import os
import json
import re
from set_payment_type_1.Item import Item
from enum import Enum

class Receipt():

    def __init__(self, email, phone):
        self.email = email
        self.phone = re.sub("\D", "", phone)
        self.email_company = os.environ.get('EMAIL_COMPANY','hello@ensoflowers.ru')
        self.taxation = Taxation.USN_INCOME_OUTCOME
        self.items = []
    
    def add_item(self, name, quantity, price, discount):
        item = Item(name, quantity, price, discount)
        if(item.amount > 0):
            self.items.append(item)
        return item.amount
    
    def tojson(self):
        return {
            'Email':self.email,
            'Phone':self.phone,
            'EmailCompany':self.email_company,
            'Taxation':self.taxation.value,
            'Items':self.items,
        }
        
class Taxation(Enum):
    OSN: str  = 'osn'
    USN_INCOME: str  = 'usn_income'
    USN_INCOME_OUTCOME: str  = 'usn_income_outcome'
    PATENT: str  = 'patent'
    ENVD: str  = 'envd'
    ESN: str  = 'esn'
    