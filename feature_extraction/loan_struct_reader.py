import numpy as np
import json
from datetime import datetime


class LoanStructReader():
    def Read(self, path, returnOptions=False):
        with open(path, 'rb') as json_file:
            self.json = json.load(json_file)
        self.loanInfo = {}

        self.__read_loanSummary()
        self.__read_paymentsSchedule()
        self.__read_factPayments()
        self.__read_prepaymentPenalties()
        self.__read_interestSchema()
        self.__read_interestPayments()

        if not returnOptions:
            return self.loanInfo

        self.options = {}
        self.__read_options()
        return self.loanInfo, self.options

    def __read_loanSummary(self):
        self.loanInfo['operationDate'] = datetime.today() # strtodate(self.json['loan']['loanSummary']['operationDate'])
        self.loanInfo['dateBegin'] = strtodate(self.json['loan']['loanSummary']['dateBegin'])
        self.loanInfo['maturityDate'] = strtodate(self.json['loan']['loanSummary']['maturityDate'])

    def __read_paymentsSchedule(self):
        self.loanInfo['paymentsSchedule'] = []
        for i in range(len(self.json['loan']['paymentsSchedule'])):
            self.loanInfo['paymentsSchedule'].append({
                'paymentType': self.json['loan']['paymentsSchedule'][i]['paymentType'],
                'paymentDate': strtodate(self.json['loan']['paymentsSchedule'][i]['paymentDate']),
                'expectedAmount': self.json['loan']['paymentsSchedule'][i]['expectedAmount'],
                'actualAmount': self.json['loan']['paymentsSchedule'][i]['actualAmount'],
            })
        return

    def __read_factPayments(self):
        # делается автоматически из self.loanInfo['paymentsSchedule']
        return

    def __read_prepaymentPenalties(self):
        self.loanInfo['prepaymentPenalties'] = []
        for i in range(len(self.json['loan']['prepaymentPenalties'])):
            self.loanInfo['prepaymentPenalties'].append({
                'startDate': strtodate(self.json['loan']['prepaymentPenalties'][i]['startDate']),
                'type': self.json['loan']['prepaymentPenalties'][i]['type'],
                'value': self.json['loan']['prepaymentPenalties'][i]['value']
            })
        return

    def __read_interestPayments(self):
        self.loanInfo['interestPayments'] = []
        for i in range(len(self.json['loan']['interestPayments'])):
            self.loanInfo['interestPayments'].append({
                'startDate': strtodate(self.json['loan']['interestPayments'][i]['startDate']),
                'endDate': strtodate(self.json['loan']['interestPayments'][i]['endDate']),
                'paymentDate': strtodate(self.json['loan']['interestPayments'][i]['paymentDate']),
                'paymentType': self.json['loan']['interestPayments'][i]['paymentType'],
                'accrualType': self.json['loan']['interestPayments'][i]['accrualType'],
                'accrualBase': self.json['loan']['interestPayments'][i]['accrualBase'],
                'actualAmount': self.json['loan']['interestPayments'][i]['actualAmount'],
                'executionStatus': self.json['loan']['interestPayments'][i]['executionStatus']
            })
            if 'schemaId' in self.json['loan']['interestPayments'][i].keys():
                self.loanInfo['interestPayments']['schemaId'] = self.json['loan']['interestPayments'][i]['schemaId']
        return

    def __read_interestSchema(self):
        self.loanInfo['interestSchema'] = []
        for i in range(len(self.json['loan']['interestSchema'])):
            if self.json['loan']['interestSchema'][i]['type'] == 'fixed':
                self.loanInfo['interestSchema'].append({
                    'inclusiveBeginDate': strtodate(self.json['loan']['interestSchema'][i]['inclusiveBeginDate']),
                    'bankYear': self.json['loan']['interestSchema'][i]['bankYear'],
                    'bankMonth': self.json['loan']['interestSchema'][i]['bankMonth'],
                    'type': self.json['loan']['interestSchema'][i]['type'],
                    'fixedSchema': self.json['loan']['interestSchema'][i]['fixedSchema']
                })
                if 'schemaId' in self.json['loan']['interestSchema'][i].keys():
                    self.loanInfo['interestSchema'][-1]['schemaId'] = self.json['loan']['interestSchema'][i]['schemaId']
        return

    def __read_options(self):
        self.options['algorithm'] = self.json['options']["algorithm"]
        self.options['lgd'] = self.json['options']['lgd']
        self.options['operationDate'] = datetime.today() #strtodate(self.json['options']['asOfDate'])
        self.options['deltaTInDays'] = self.json['options']['deltaTInDays']
        self.options['irOptions_alpha'] = self.json['options']['irOptions']['alpha']
        self.options['irOptions_sigma'] = self.json['options']['irOptions']['sigma']
        self.options['hzOptions_alpha'] = self.json['options']['hzOptions']['alpha']
        self.options['hzOptions_sigma'] = self.json['options']['hzOptions']['sigma']
        self.options['irOptions_curve'] = self.__read_points('irOptions')
        self.options['hzOptions_curve'] = self.__read_points('hzOptions')

    def __read_points(self, root):
        points = self.json['options'][root]['curve']['points']
        res = []
        for point in points:
            res.append(point['value'])
        return np.array(res)


def strtodate(date):
    return datetime.strptime(date, '%Y-%m-%d')
