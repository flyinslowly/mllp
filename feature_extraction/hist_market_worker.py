import json
import os
import numpy as np
import scipy.stats as sps
from datetime import datetime
import pickle


DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(os.getcwd()), r"model\md_hist.pckl")
DEFAULT_CURVES_PATH = os.path.join(os.path.dirname(os.getcwd()), r"rate_curves")
DEFAULT_CURVE_NAME = r"RUB__RUONIA_OIS"


class HistMarketDataWorker():
    def __init__(self, curves_path=None, curve_name=None):
        self.__deltas = [1, 7, 30, 3 * 30, 6 * 30, 12 * 30, 2 * 12 * 30, 5 * 12 * 30, 10 * 12 * 30, 20 * 12 * 30]
        if curves_path is not None:
            self.__curve_name = curve_name
            self.__curves_path = curves_path
            self.__curves = self.__read_historical_md_canonical()
            self.__calibrate(self.__curves)

    def __read_historical_md_canonical(self):
        pt_array = []
        for date in os.listdir(self.__curves_path):
            with open(os.path.join(self.__curves_path, date, self.__curve_name + '.json'), 'rb') as file:
                curve_json = json.load(file)
                points = self.__parse_curve(curve_json)

                if self.__deltas[-1] > points[-1][1]:
                    points.append((points[-1][0], self.__deltas[-1]))

                canonical_curve_vals = []
                for dlt in self.__deltas:
                    for point_id in range(len(points) - 1):
                        l_day, r_day = points[point_id][1], points[point_id + 1][1]
                        if l_day < dlt <= r_day:
                            l_val, r_val = points[point_id][0], points[point_id + 1][0]
                            canonical_curve_vals.append(l_val + (dlt - l_day) / (r_day - l_day) * (r_val - l_val))

                canonic_points = list(zip(canonical_curve_vals, self.__deltas))

                pt_array.append(canonical_curve_vals)

        return pt_array

    @staticmethod
    def __parse_curve(curve):
        op_date = datetime(*list(map(int, curve['date'].split('-'))))
        vals, deltas = [1.0], [0]
        for point in curve['points']:
            cur_date = datetime(*list(map(int, point['date'].split('-'))))
            cur_val = point['value']['value']

            vals.append(cur_val)
            deltas.append(int((cur_date - op_date).days))
        return list(zip(vals, deltas))

    def __calibrate(self, curves):
        curves = np.array(curves)

        mu, cov = np.mean(curves, axis=0), #np.cov(curves, rowvar=False)*1e5
        self.__f = sps.multivariate_normal(mean=mu, cov=cov, allow_singular=True)
        return

    def get_func(self):
        return self.__f

    def get_deltas(self):
        return self.__deltas

    def get_sample(self):
        return self.__f.rvs()

    def get_train_curves(self):
        return self.__curves

    def rho_normal(self, X):
        # [10]
        # [N x 10]
        # assert self.__f.dim == len(X) and type(X).__name__ == 'ndarray'
        res = []
        for x in X:
            res.append([self.__f.pdf(x)])
        return np.array(res)

    def save(self, path=DEFAULT_MODEL_PATH):
        with open(path, 'wb') as file:
            pickle.dump(self, file)

    def load(self, path=DEFAULT_MODEL_PATH):
        with open(path, 'rb') as file:
            return pickle.load(file)
