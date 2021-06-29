from feature_extraction.hist_market_worker import HistMarketDataWorker
from datetime import timedelta
from datetime import datetime


class LoanOptionsMaker():
    def __init__(self):
        self.hmdw = HistMarketDataWorker().load()
        return

    def Make(self, original_options, ir_curve=None, hz_curve=None):
        optionsDict = original_options.copy()
        opDate = datetime.today()

        optionsDict['irOptions_curve'] = {}
        self.__make_ir(optionsDict['irOptions_curve'], opDate, ir_curve)

        optionsDict['hzOptions_curve'] = {}
        self.__make_hz(optionsDict['hzOptions_curve'], opDate, hz_curve)
        return optionsDict

    def __make_ir(self, root, opDate, curve=None):
        root['values'] = self.hmdw.get_sample() if curve is None else curve
        root['dates'] = self.__transform_date(self.hmdw.get_deltas(), opDate)

    def __make_hz(self, root, opDate, curve=None):
        root['values'] = [1.0, 1.0] if curve is None else curve
        root['dates'] = self.__transform_date([10, 365], opDate)

    @staticmethod
    def __transform_date(deltas, opDate):
        return [opDate + timedelta(days=delta) for delta in deltas]
