from .base import AcquisitionBase
from ..util.general import get_quantiles
import numpy as np


def rho(X, domain):
    res = []
    for x, i in enumerate(X):
        a, b = domain[domain.keys()[i]]['domain']
        res.append([(x - a) / (b - a)])
    return np.array(res)


def df_rho(X, domain):
    res = []
    for x, i in enumerate(X):
        a, b = domain[domain.keys()[i]]['domain']
        res.append([1 / (b - a)])
    return np.array(res)


# Acquisition Unifor Random
class AcquisitionUR(AcquisitionBase):

    analytical_gradient_prediction = True

    def __init__(self, model, space, optimizer=None, cost_withGradients=None, exploration_weight=2, domain=None):
        super(AcquisitionUR, self).__init__(model, space, optimizer)
        self.optimizer = optimizer
        self.exploration_weight = exploration_weight if exploration_weight is not None else 2

        if cost_withGradients is not None:
            print('The set cost function is ignored! NEW acquisition does not make sense with cost.')
        self.domain = domain
        assert(domain is not None)

    def _compute_acq(self, x):
        m, s = self.model.predict(x)
        sigma_val = s
        if self.rho is not None:
            return sigma_val * self.rho(x)
        return sigma_val

    def _compute_acq_withGradients(self, x):
        m, s, dmdx, dsdx = self.model.predict_withGradients(x)
        sigma_val = s

        if self.rho is not None:
            df_a = dsdx
            return sigma_val * rho(x, self.domain), (df_a * rho(x, self.domain) + sigma_val * df_rho(x, self.domain))[0]
        else:
            df_a = dsdx
            df_acqu = self.exploration_weight * dsdx
            return sigma_val, df_acqu

