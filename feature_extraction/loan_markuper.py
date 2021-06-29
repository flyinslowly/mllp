import requests
import json
import numpy as np
import os
from datetime import datetime


class LoanMarkuper:
    def MarkupLoan(self, loan_dict):
        result = 0
        curve = loan_dict['options']['irOptions']['curve']
        for payment in loan_dict['loan']['paymentsSchedule']:
            if payment['paymentType'] != 'notionalRepayment':
                continue
            result += payment['expectedAmount'] * self.find_discont_factor(curve, payment['paymentDate'])
        return result

    def MarkupLoanLP(self, loan_dict):
        r = requests.post('http://loanpricing-01.vm.esrt.cloud.sbrf.ru:9010/api/fv', json=loan_dict)

        return r.json()['vanilla']

    def find_discont_factor(self, curve, date):
        maturityDate = datetime.strptime(date, "%Y-%m-%d")

        prev_date = datetime.strptime(curve['date'], "%Y-%m-%d")
        prev_point = 1.0
        for point in curve['points']:
            cur_date = datetime.strptime(point['date'], "%Y-%m-%d")
            cur_point = point['value']
            if prev_date <= maturityDate <= cur_date:
                return prev_point - (maturityDate - prev_date) / (cur_date - prev_date) * (prev_point - cur_point)
            prev_date = cur_date
            prev_point = cur_point
        return prev_point