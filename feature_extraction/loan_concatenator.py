import json


def datetostr(date):
    return date.strftime('%Y-%m-%d')

class LoanConcatenator(object):
    def __init__(self, loanStruct, loanOptions, loanMarketdata):
        self.__loanStruct = loanStruct
        self.__loanOptions = loanOptions
        self.__loanMarketdata = loanMarketdata

    def Parse(self):
        loanDict = {'loan': {}, 'options': {}, 'marketContainer': {}}

        # loan
        self.__parse_loanSummary(loanDict['loan'])
        self.__parse_paymentsSchedule(loanDict['loan'])
        self.__parse_factPayments(loanDict['loan'])
        self.__parse_prepaymentPenalties(loanDict['loan'])
        self.__parse_interestPayments(loanDict['loan'])
        self.__parse_interestSchema(loanDict['loan'])

        # options
        self.__parse_options(loanDict['options'])

        # marketContainer
        self.__parse_marketContainer(loanDict['marketContainer'])

        return loanDict

    @staticmethod
    def Save(loanDict, path):
        with open(path, 'w',) as file:
            json.dump(loanDict, file, indent=4)

        return

###################################################################################################
# LOAN

    def __parse_loanSummary(self, root):
        """
        "loanSummary": {
            "tradeId": "TEST-1",
            "operationDate": "2020-11-30",
            "dateBegin": "2014-07-31",
            "maturityDate": "2024-07-31"
        }
        """
        root['loanSummary'] = {}
        loanSum = root['loanSummary']
        loanSum['tradeId'] = "TEST"
        loanSum['operationDate'] = datetostr(self.__loanStruct['operationDate'])
        loanSum['dateBegin'] = datetostr(self.__loanStruct['dateBegin'])
        loanSum['maturityDate'] = datetostr(self.__loanStruct['maturityDate'])
        return

    def __parse_paymentsSchedule(self, root):
        """
        "paymentsSchedule": [
            {
                "paymentDate": "2014-07-31",
                "expectedAmount": 100000000,
                "actualAmount": 100000000,
                "paymentType": "draw",
                "executionStatus": "executed"
            }
        ]
        """
        root['paymentsSchedule'] = []
        loanPS = root['paymentsSchedule']
        for i in range(len(self.__loanStruct['paymentsSchedule'])):
            loanPS.append({
                'paymentDate': datetostr(self.__loanStruct['paymentsSchedule'][i]['paymentDate']),
                'expectedAmount': self.__loanStruct['paymentsSchedule'][i]['expectedAmount'],
                'actualAmount': self.__loanStruct['paymentsSchedule'][i]['actualAmount'],
                'paymentType': self.__loanStruct['paymentsSchedule'][i]['paymentType'],
                'executionStatus': self.__checkExecuted(self.__loanStruct['paymentsSchedule'][i]['paymentDate'])
            })
        return

    def __parse_factPayments(self, root):
        """
        "factPayments": [
            {
                "paymentDate": "2014-07-31",
                "actualAmount": 100000000,
                "paymentType": "draw"
            }
        ]
        """
        root['factPayments'] = []
        loanFP = root['factPayments']
        for i in range(len(self.__loanStruct['paymentsSchedule'])):
            if root['paymentsSchedule'][i]['executionStatus'] == 'executed':
                loanFP.append({
                    'paymentDate': root['paymentsSchedule'][i]['paymentDate'], # v root уже строка
                    'actualAmount': root['paymentsSchedule'][i]['actualAmount'],
                    'paymentType': root['paymentsSchedule'][i]['paymentType']
                })
        return

    def __parse_prepaymentPenalties(self, root):
        """
        [
            {
                "startDate": "2014-07-31",
                "type": "процент_от_суммы_досрочно_возвращаемого_долга",
                "value": 0
            }
        ]
        """
        root['prepaymentPenalties'] = []
        loanPP = root['prepaymentPenalties']

        for i in range(len(self.__loanStruct['prepaymentPenalties'])):
            loanPP.append({
                'startDate': datetostr(self.__loanStruct['prepaymentPenalties'][i]['startDate']),
                'type': self.__loanStruct['prepaymentPenalties'][i]['type'],
                'value': self.__loanStruct['prepaymentPenalties'][i]['value']
            })
        return

    def __parse_interestPayments(self, root):
        """
        [
            {
                "paymentDate": "2021-01-29",
                "paymentType": "interestPayment",
                "accrualType": "simple",
                "accrualBase": "notionalAndCapitalized",
                "actualAmount": 0,
                "startDate": "2020-10-31",
                "endDate": "2021-01-29",
                "executionStatus": "notExecuted"
            }
        ]
        """
        root['interestPayments'] = []
        loanIP = root['interestPayments']

        for i in range(len(self.__loanStruct['interestPayments'])):
            payment = {}
            for key in self.__loanStruct['interestPayments'][i].keys():
                payment[key] = self.__loanStruct['interestPayments'][i][key]
                if key.find('Date') != -1:
                    payment[key] = datetostr(self.__loanStruct['interestPayments'][i][key])
            loanIP.append(payment)

        return

    def __parse_interestSchema(self, root):
        """
        [
            {
                "inclusiveBeginDate": "2018-04-28",
                "bankYear": "ACT",
                "bankMonth": "ACT",
                "type": "fixed",
                "fixedSchema": 0.03472
            },
            {
                "inclusiveBeginDate": "2020-10-31",
                "bankYear": "360",
                "bankMonth": "ACT",
                "type": "floating",
                "floatingSchema": {
                    "baseIndex": "EURIBOR3M",
                    "spreadValue": {
                        "summand": 0.038
                    }
                }
            }
        ]
        """
        root['interestSchema'] = []
        loanIS = root['interestSchema']
        for i in range(len(self.__loanStruct['interestSchema'])):
            loanIS.append({
                "inclusiveBeginDate": datetostr(self.__loanStruct['interestSchema'][i]['inclusiveBeginDate']),
                "bankYear": self.__loanStruct['interestSchema'][i]['bankYear'],
                "bankMonth": self.__loanStruct['interestSchema'][i]['bankMonth'],
                "type": self.__loanStruct['interestSchema'][i]['type'],
                "fixedSchema": self.__loanStruct['interestSchema'][i]['fixedSchema']
            })
        return

###################################################################################################
# OPTIONS

    def __parse_options(self, root):
        root['algorithm'] = self.__loanOptions['algorithm']
        root['lgd'] = self.__loanOptions['lgd']
        root['asOfDate'] = datetostr(self.__loanOptions['operationDate'])
        root['deltaTInDays'] = self.__loanOptions['deltaTInDays']
        root['irOptions'] = {}
        root['irOptions']['alpha'] = self.__loanOptions['irOptions_alpha']
        root['irOptions']['sigma'] = self.__loanOptions['irOptions_sigma']
        root['irOptions']['curve'] = {}
        root['irOptions']['curve']['date'] = datetostr(self.__loanOptions['operationDate'])
        root['irOptions']['curve']['points'] = []
        assert(len(self.__loanOptions['irOptions_curve']['values']) == len(self.__loanOptions['irOptions_curve']['dates']))
        for i in range(len(self.__loanOptions['irOptions_curve']['values'])):
            root['irOptions']['curve']['points'].append({
                'date': datetostr(self.__loanOptions['irOptions_curve']['dates'][i]),
                'value': self.__loanOptions['irOptions_curve']['values'][i]
            })

        root['hzOptions'] = {}
        root['hzOptions']['alpha'] = self.__loanOptions['hzOptions_alpha']
        root['hzOptions']['sigma'] = self.__loanOptions['hzOptions_sigma']
        root['hzOptions']['curve'] = {}
        root['hzOptions']['curve']['date'] = datetostr(self.__loanOptions['operationDate'])
        root['hzOptions']['curve']['points'] = []
        assert(len(self.__loanOptions['hzOptions_curve']['values']) == len(self.__loanOptions['hzOptions_curve']['dates']))
        for i in range(len(self.__loanOptions['hzOptions_curve']['values'])):
            root['hzOptions']['curve']['points'].append({
                'date': datetostr(self.__loanOptions['hzOptions_curve']['dates'][i]),
                'value': self.__loanOptions['hzOptions_curve']['values'][i]
            })

###################################################################################################
# MARKET CONTAINER

    def __parse_marketContainer(self, root):
        root = {}
        if 'historicalIndexes' in self.__loanMarketdata.keys():
            root['historicalIndexValues'] = []
            for i in range(len(self.__loanMarketdata['historicalIndexes'])):
                root['historicalIndexValue'] = {
                    'baseIndex': self.__loanMarketdata['historicalIndexes']['indexes'][i],
                    'date': datetostr(self.__loanMarketdata['historicalIndexes']['dates'][i]),
                    'value': self.__loanMarketdata['historicalIndexes']['values'][i]
                    # ToDo :: 'sources' = []
                }
        if 'forecastCurves' in self.__loanMarketdata.keys():
            root['forecastCurves'] = []
            for i in range(len(self.__loanMarketdata['forecastCurves'])):
                curDictCurve = {}
                curDictCurve['baseIndex'] = self.__loanMarketdata['forecastCurves'][i]['baseIndex']
                curDictCurve['tenor'] = self.__loanMarketdata['forecastCurves'][i]['tenor']
                curDictCurve['date'] = datetostr(self.__loanMarketdata['forecastCurves'][i]['date'])
                curDictCurve['points'] = []
                for j in range(len(self.__loanMarketdata['forecastCurves'][i]['dates'])):
                    curDictCurve['points'].append({
                        'date': datetostr(self.__loanMarketdata['forecastCurves'][i]['dates'][j]),
                        'value': self.__loanMarketdata['forecastCurves'][i]['values'][j]
                    })
                root['forecastCurves'].append(curDictCurve)

###################################################################################################

    def __checkExecuted(self, date):
        return "executed" if date < self.__loanStruct['operationDate'] else "notExecuted"

