import pandas as pd
from datetime import datetime


class FeatureTransformer:
    def __init__(self):
        self.rows_list = []

    def AccumulateExtractFrom(self, loan_dict, loan_price):
        md_dict = self.__generate_historical_md()

        loan_summary = loan_dict['loan']['loanSummary']
        row_dict = {'label': loan_price,
                    'loanSum': loan_summary['notional'],
                    # 'loanLength': self.__datetime_days_diff(loan_summary['maturityDate'], loan_summary['operationDate']),
                    'loanExpDaysLeft': self.__datetime_days_diff(loan_summary['maturityDate'])}
        row_dict.update(md_dict)

        self.rows_list.append(row_dict)

    def BuildDataFrame(self):
        return pd.DataFrame(self.rows_list)

    @staticmethod
    def __datetime_days_diff(date_str: str, date_str_2: str = None):
        date_1 = datetime.strptime(date_str, '%Y-%m-%d')
        date_2 = datetime.today()
        if date_str_2 is not None:
            date_2 = datetime.strptime(date_str_2, '%Y-%m-%d')

        return abs((date_1 - date_2).days)

    @staticmethod
    def __generate_historical_md():
        pass
