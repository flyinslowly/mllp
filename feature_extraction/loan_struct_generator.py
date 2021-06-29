import numpy as np
import json
from datetime import datetime


class LoanStructGenerator(object):
    def __init__(self, maxLoanSum, maxNumPayments, beginDate, endDate):
        self.maxLoanSum = maxLoanSum
        self.maxNumPayments = maxNumPayments
        self.beginDate = beginDate
        self.endDate = endDate

        self.loanInfo = {}


    def GenerateLoanStruct(self, path_to_save):
        # generateLoan
        self.loanInfo['operationDate'] = datetime.today()
        self.loanInfo['dateBegin'] = self.__date_from_uniform(self.beginDate, self.endDate)  # дата начала
        self.loanInfo['maturityDate'] = self.__date_from_uniform(self.loanInfo['dateBegin'], self.endDate)  # дата конца
        self.loanInfo['loanSum'] = int(np.random.uniform(0, self.maxLoanSum))  # сумма кредита
        self.loanInfo['numPayments'] = int(np.random.uniform(0, self.maxNumPayments))  # количество выплат
        self.loanInfo['payments'] = self.__generatePayments(self.loanInfo['numPayments']) # генератор самих выплат

        return self.loanInfo

    def __generatePayments(self, numPayments):
        dictsList = []

        # снятие основной суммы кредита
        dictsList.append({
            'paymentType': "draw",
            'paymentDate': self.loanInfo['dateBegin'],
            'expectedAmount': self.loanInfo['loanSum'],
            'actualAmount': self.loanInfo['loanSum']
        })

        remainingSumToSample = self.loanInfo['loanSum']
        lastSampledDay = self.loanInfo['dateBegin']
        for i in range(numPayments):
            sampledDay = self.__date_from_uniform(lastSampledDay, self.loanInfo['maturityDate'])
            lastSampledDay = sampledDay

            sampledSum = np.random.uniform(0, remainingSumToSample)
            remainingSumToSample -= sampledSum

            dictsList.append({
                'paymentType': "notionalRepayment",
                'paymentDate': sampledDay,
                'expectedAmount': sampledSum,
                'actualAmount': sampledSum
            })

        # полное погашение кредита до конца в последний день
        dictsList.append({
            'paymentType': "notionalRepayment",
            'paymentDate': self.loanInfo['maturityDate'],
            'expectedAmount': remainingSumToSample,
            'actualAmount': remainingSumToSample
        })

        # ToDo:: у нас типа actual = expected, на самом деле значение actual зависит от того в будущем ли этот поток.
        return dictsList

    @staticmethod
    def __date_from_uniform(date1, date2):
        return datetime.utcfromtimestamp(np.random.uniform(date1.timestamp(), date2.timestamp()))
