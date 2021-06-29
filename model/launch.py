import os
import numpy as np
import GPyOpt
from feature_extraction.loan_struct_reader import LoanStructReader
from feature_extraction.loan_options_maker import LoanOptionsMaker
from feature_extraction.loan_concatenator import LoanConcatenator
from feature_extraction.loan_markuper import LoanMarkuper
from feature_extraction.hist_market_worker import HistMarketDataWorker


PROJECT_PATH = os.path.dirname(os.getcwd())
DOMAIN = [{'name': 'var_1', 'type': 'continuous', 'domain': (0, 1)},
          {'name': 'var_2', 'type': 'continuous', 'domain': (0, 1)},
          {'name': 'var_3', 'type': 'continuous', 'domain': (0, 1)},
          {'name': 'var_4', 'type': 'continuous', 'domain': (0, 1)},
          {'name': 'var_5', 'type': 'continuous', 'domain': (0, 1)},
          {'name': 'var_6', 'type': 'continuous', 'domain': (0, 1)},
          {'name': 'var_7', 'type': 'continuous', 'domain': (0, 1)},
          {'name': 'var_8', 'type': 'continuous', 'domain': (0, 1)},
          {'name': 'var_9', 'type': 'continuous', 'domain': (0, 1)},
          {'name': 'var_10', 'type': 'continuous', 'domain': (0, 1)}]

DOMAIN_1 = {'name': 'var_1', 'type': 'continuous', 'domain':(0, 1), 'dimensionality':10}


def f(X, json_example_path=os.path.join(PROJECT_PATH, r"json_real", r"sample_1.json")):
    "It should take 2-dimensional numpy arrays as input and return 2-dimensional outputs (one evaluation per row)"
    Y = []
    for x in X:
        struct, original_options = LoanStructReader().Read(json_example_path, returnOptions=True)
        options = LoanOptionsMaker().Make(original_options, ir_curve=x)

        loan = LoanConcatenator(struct, options, {}).Parse()
        Y.append([LoanMarkuper().MarkupLoan(loan)])
    return np.array(Y)

X_init = np.array(np.ones(HistMarketDataWorker().load().get_sample().shape).reshape(1, -1))
print(X_init.shape)
Y_init = f(X_init)
print(Y_init)


hmdw = HistMarketDataWorker().load()

bo = GPyOpt.methods.BayesianOptimization(f=f, domain=DOMAIN,
                                        initial_design_numdata = 1,
                                        X=X_init, Y=Y_init,
                                        acquisition_type='NEW',
                                        exact_feval = True,
                                        normalize_Y = False,
                                        optimize_restarts = 10,
                                        acquisition_weight = 2,
                                        de_duplication = True,
                                        rho_func = hmdw.rho_normal,
                                        exploration_weight=1000,
                                        with_noise=False)
bo.run_optimization(60)
print('evalluations_list: ', bo.get_evaluations())


X_test = []
for i in range(100):
    X_test.append(hmdw.get_sample())
X_test = np.array(X_test)

print('test_sample_values:')
predict = bo.model.predict(X_test)
print('\mu_values: ', predict[0])
print('\sigma_values: ', predict[1])
print('MAE: ', np.mean(predict[1] / predict[0]))
print('MAE_list: ', bo.error_list)