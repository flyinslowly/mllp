from .base import AcquisitionBase
from ..util.general import get_quantiles
import numpy as np

class AcquisitionNEW(AcquisitionBase):

    analytical_gradient_prediction = True

    def __init__(self, model, space, optimizer=None, cost_withGradients=None, exploration_weight=2, rho_func = None):
        self.optimizer = optimizer
        self.rho_func = rho_func
        super(AcquisitionNEW, self).__init__(model, space, optimizer)
        if exploration_weight is None:
            self.exploration_weight = 2
        else:
            self.exploration_weight = exploration_weight

        if cost_withGradients is not None:
            print('The set cost function is ignored! NEW acquisition does not make sense with cost.')  

    def _compute_acq(self, x):
        #print('rho_foo: ', self.rho_func)
        #print(self.model.predict())
        m, s = self.model.predict(x)
        sigma_val = s#self.exploration_weight * s
        #f_acqu = -m + self.exploration_weight * s
        #f_acqu = m + self.exploration_weight * s
        if self.rho_func is not None:
            #print('rho_foo: ', sigma_val * self.rho_func(x))
            return sigma_val * self.rho_func(x)
        else:
            return sigma_val

    def _compute_acq_withGradients(self, x):
        m, s, dmdx, dsdx = self.model.predict_withGradients(x)
        sigma_val = s#self.exploration_weight * s
        #f_acqu = -m + self.exploration_weight * s
        #f_acqu = m + self.exploration_weight * s
        #print('gradients: ', dmdx, dsdx)

        if self.rho_func is not None:
            # f'(x)=(f(x_0)+f(x))/h
            # foo(x)= a(b,x)*\rho(x)
            # foo'(x)=a'(b,x)\rho(x)+a(b,x)\rho'(x)

            #df_a = -dsdx
            df_a = dsdx#self.exploration_weight * dsdx
            #df_a = -dmdx + self.exploration_weight * dsdx
            #df_a = dmdx + self.exploration_weight * dsdx
            h = 1e-8
            #df_rho = [-1*(self.rho_func(x+h)-self.rho_func(x))/h]
            #print(self.rho_func(x_k+h),)
            df_rho_upper = np.array([(np.array(self.rho_func(x_k+h))-np.array(self.rho_func(x_k)))/h for x_k in [x]])
            df_rho_lower = np.array([(np.array(self.rho_func(x_k))-np.array(self.rho_func(x_k-h)))/h for x_k in [x]])
            df_rho = (df_rho_upper+df_rho_lower)/2
            #print('f_acqu', f_acqu * self.rho_func(x))
            #print('df_acqu', df_a*self.rho_func(x)+f_acqu*df_rho)
            return sigma_val * self.rho_func(x), (df_a*self.rho_func(x)+sigma_val*df_rho)[0]#[df_a*self.rho_func(x)+f_acqu*df_rho_k for df_rho_k in df_rho]
        else:
            df_a = dsdx
            df_acqu = self.exploration_weight * dsdx
            #print('f_acqu_1', f_acqu * self.rho_func(x))
            #print('df_acqu_1', df_acqu)
            return sigma_val * self.rho_func(x), df_acqu

