from enum import Enum
import json

class Item():
    def __init__(self, name, quantity, price, discount):
        self.quantity = int(quantity)
        self.price = int(float(price)*100)
        self.amount = self.quantity*self.price
        if(self.amount > discount):
            if(discount !=0):
                self.amount -= discount
                self.price = self.amount / self.quantity
            self.name = name
            self.paymentMethod = Payment_Method.FULL_PAYMENT
            self.paymentObject = Payment_Object.COMMODITY
            self.tax = 'none'
        else:
            self.amount -= discount#<0
    
    def tojson(self):
        return {
            'Name':self.name,
            'Quantity':self.quantity,
            'Price':self.price,
            'Amount':self.amount,
            'PaymentMethod':json.dumps(self.paymentMethod.value),
            'PaymentObject':json.dumps(self.paymentObject.value),
            'Tax':self.tax,
        }
class Payment_Method(Enum):
    FULL_PAYMENT = 'full_payment'
    FULL_PREPAYMENT = 'full_prepayment'
    PREPAYMENT = 'prepayment'
    ADVANCE = 'advance'
    PARTIAL_PAYMENT = 'partial_payment'
    CREDIT = 'credit'
    CREDIT_PAYMENT = 'credit_payment'
    
    
class Payment_Object(Enum):
    COMMODITY = 'commodity'
    EXCISE = 'excise'
    JOB = 'job'
    SERVICE = 'service'
    GAMBLING_BET = 'gambling_bet'
    GAMBLING_PRIZE = 'gambling_prize'
    LOTTERY = 'lottery'
    LOTTERY_PRIZE = 'lottery_prize'
    INTELLECTUAL_ACTIVITY = 'intellectual_activity'
    PAYMENT = 'payment'
    AGENT_COMMISSION = 'agent_commission'
    COMPOSITE = 'composite'
    ANOTHER = 'another'
    