from feature_extraction.hist_market_worker import *

from datetime import datetime
import time
import numpy as np
import os
import pickle

PROJECT_PATH = os.path.dirname(os.getcwd())

# gen = loan_struct_generator.LoanGenerator(10000, 1, datetime(2020, 1, 1), datetime(2022, 1, 1))
# gen.GenerateAndSaveLoan(os.path.join(PROJECT_PATH + r"\json_augmented", 'test.json'))

# hmdw = HistMarketDataWorker(DEFAULT_CURVES_PATH, DEFAULT_CURVE_NAME)
# print(hmdw.get_sample())
# hmdw.save()

# np.random.seed(int(time.time()))
# h = HistMarketDataWorker().load()
# print(h.get_sample())
# print(h.get_sample())

# print(gen_crv)

from feature_extraction.loan_struct_reader import LoanStructReader
json_example_path = os.path.join(PROJECT_PATH, r"json_real", r"sample_10.json")
struct, original_options = LoanStructReader().Read(json_example_path, returnOptions=True)

from feature_extraction.loan_options_maker import LoanOptionsMaker
options = LoanOptionsMaker().Make(original_options)
print(options['irOptions_curve']['values'])

from feature_extraction.loan_concatenator import LoanConcatenator
from feature_extraction.loan_markuper import LoanMarkuper

markuper = LoanMarkuper()
optionsMaker = LoanOptionsMaker()

js = LoanConcatenator(struct, options, {}).Parse()
LoanConcatenator.Save(js, os.path.join(PROJECT_PATH, r"json_real", 'opt_etalon.json'))
print(markuper.MarkupLoan(js))


exit(0)

markupdict = {}
for i in range(0, 2000):
    options = optionsMaker.Make(original_options)

    js = LoanConcatenator(struct, options, {}).Parse()
    name = "sample_{}.json".format(i)
    LoanConcatenator.Save(js, os.path.join(PROJECT_PATH, r"json_augmented", name))
    markupdict[name] = markuper.MarkupLoan(js)

with open(os.path.join(PROJECT_PATH, r"json_augmented", "markupdict0-2000.pckl"), 'wb') as f:
    pickle.dump(markupdict, f)

