import numpy as np
import scipy.stats as ss

from .base import ExperimentDesign
from ..core.task.variables import BanditVariable, DiscreteVariable, CategoricalVariable


class RandomDesign(ExperimentDesign):
    """
    Random experiment design.
    Random values for all variables within the given bounds.
    """
    def __init__(self, space):
        super(RandomDesign, self).__init__(space)

    def get_samples(self, init_points_count):
        if self.space.has_constraints():
            return self.get_samples_with_constraints(init_points_count)
        else:
            return self.get_samples_without_constraints(init_points_count)

    def get_samples_with_constraints(self, init_points_count):
        """
        Draw random samples and only save those that satisfy constraints
        Finish when required number of samples is generated
        """
        samples = np.empty((0, self.space.dimensionality))

        while samples.shape[0] < init_points_count:
            domain_samples = self.get_samples_without_constraints(init_points_count)
            valid_indices = (self.space.indicator_constraints(domain_samples) == 1).flatten()
            if sum(valid_indices) > 0:
                valid_samples = domain_samples[valid_indices,:]
                samples = np.vstack((samples,valid_samples))

        return samples[0:init_points_count,:]

    def fill_noncontinous_variables(self, samples):
        """
        Fill sample values to non-continuous variables in place
        """
        init_points_count = samples.shape[0]
        for (idx, var) in enumerate(self.space.space_expanded):
            if isinstance(var, DiscreteVariable) or isinstance(var, CategoricalVariable) :
                sample_var = np.atleast_2d(np.random.choice(var.domain, init_points_count))
                samples[:,idx] = sample_var.flatten()

            # sample in the case of bandit variables
            elif isinstance(var, BanditVariable):
                # Bandit variable is represented by a several adjacent columns in the samples array
                idx_samples = np.random.randint(var.domain.shape[0], size=init_points_count)
                bandit_idx = np.arange(idx, idx + var.domain.shape[1])
                samples[:, bandit_idx] = var.domain[idx_samples,:]

    def get_samples_without_constraints(self, init_points_count):
        samples = np.empty((init_points_count, self.space.dimensionality))

        self.fill_noncontinous_variables(samples)

        if self.space.has_continuous():
            X_design = samples_multidimensional_normal(self.space.get_continuous_bounds(), init_points_count)
            samples[:, self.space.get_continuous_dims()] = X_design
        return samples

def samples_multidimensional_uniform(bounds, points_count):
    """
    Generates a multidimensional grid uniformly distributed.
    :param bounds: tuple defining the box constraints.
    :points_count: number of data points to generate.
    """
    dim = len(bounds)
    Z_rand = np.zeros(shape=(points_count, dim))
    for k in range(0,dim):
        Z_rand[:,k] = np.random.uniform(low=bounds[k][0], high=bounds[k][1], size=points_count)
    print('shape: ', Z_rand.shape)
    return Z_rand

def samples_multidimensional_normal(bounds, points_count, probability_function = ss.multivariate_normal(mean = np.array([ 0.99979098,  0.99853687,  0.99374547,  0.98132326,  0.96271213,
        0.92622281,  0.85831136,  0.67986163,  0.45735066,  0.45146176]), cov = np.array([[  1.68364856e-11,   1.17855399e-10,   4.84730408e-10,
          1.43678159e-09,   2.75599180e-09,   5.31215103e-09,
          1.00413010e-08,   2.14812457e-08,   2.90042984e-08,
          2.92104868e-08],
       [  1.17855399e-10,   8.24987793e-10,   3.39311286e-09,
          1.00574711e-08,   1.92919426e-08,   3.71850572e-08,
          7.02891071e-08,   1.50368720e-07,   2.03030089e-07,
          2.04473407e-07],
       [  4.84730408e-10,   3.39311286e-09,   1.46573849e-08,
          4.23008916e-08,   7.81069061e-08,   1.42614838e-07,
          2.57516001e-07,   5.75501836e-07,   8.67940396e-07,
          8.75678783e-07],
       [  1.43678159e-09,   1.00574711e-08,   4.23008916e-08,
          1.41398817e-07,   3.08534936e-07,   6.61392309e-07,
          1.24699012e-06,   2.08307409e-06,   1.92202021e-06,
          1.91585845e-06],
       [  2.75599180e-09,   1.92919426e-08,   7.81069061e-08,
          3.08534936e-07,   8.09740663e-07,   2.00397555e-06,
          4.02922430e-06,   5.74073739e-06,   2.27176849e-06,
          2.17662032e-06],
       [  5.31215103e-09,   3.71850572e-08,   1.42614838e-07,
          6.61392309e-07,   2.00397555e-06,   5.48848130e-06,
          1.15746225e-05,   1.57202932e-05,   2.04704497e-06,
          1.68889717e-06],
       [  1.00413010e-08,   7.02891071e-08,   2.57516001e-07,
          1.24699012e-06,   4.02922430e-06,   1.15746225e-05,
          2.61555887e-05,   3.67662826e-05,   4.83129870e-06,
          4.04191198e-06],
       [  2.14812457e-08,   1.50368720e-07,   5.75501836e-07,
          2.08307409e-06,   5.74073739e-06,   1.57202932e-05,
          3.67662826e-05,   6.51964809e-05,   3.43450711e-05,
          3.37702763e-05],
       [  2.90042984e-08,   2.03030089e-07,   8.67940396e-07,
          1.92202021e-06,   2.27176849e-06,   2.04704497e-06,
          4.83129870e-06,   3.43450711e-05,   9.04633467e-05,
          9.21043033e-05],
       [  2.92104868e-08,   2.04473407e-07,   8.75678783e-07,
          1.91585845e-06,   2.17662032e-06,   1.68889717e-06,
          4.04191198e-06,   3.37702763e-05,   9.21043033e-05,
          9.38436916e-05]]), allow_singular=True)):
    dim = len(bounds)
    first_arr = probability_function.rvs(points_count)
    N_rand = np.zeros(shape=(points_count, dim))

    for k in range(0, dim):
        N_rand[:, k] = np.clip(first_arr[:, k], bounds[k][0], bounds[k][1])

    return N_rand