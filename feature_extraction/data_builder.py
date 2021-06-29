import os

from feature_extraction.loan_markuper import LoanMarkuper
from feature_extraction.loan_struct_generator import LoanStructGenerator
from feature_extraction.feature_transformer import FeatureTransformer


def build_data_frame(data_size):
    JSON_REAL_DIR = '../json_real_patterns'

    GENERATOR = LoanStructGenerator()
    MARKUPER = LoanMarkuper()
    TRANSFORMER = FeatureTransformer()  # накапливает в поле класса лист диктов с признаками

    for i in range(data_size):
        realJsons = os.listdir(JSON_REAL_DIR)
        realJsonName = realJsons[i % len(realJsons)]
        realJsonPath = os.path.join(JSON_REAL_DIR, realJsonName)

        augmentedLoan = GENERATOR.GenerateLoanStruct(realJsonPath)
        augmentedLoanLabel = MARKUPER.MarkupLoan(augmentedLoan)
        TRANSFORMER.AccumulateExtractFrom(augmentedLoan, augmentedLoanLabel)

    df = TRANSFORMER.BuildDataFrame()

    return df
