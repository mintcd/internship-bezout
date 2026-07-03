from scipy.optimize import root_scalar
import numpy as np

def mean_preserving_alpha(X, operator, bracket=[1e-9, 1.0]):
    def objective(alpha):
        TX = operator(X, alpha)
        return np.mean(TX) - np.mean(X)
    
    sol = root_scalar(objective, bracket=bracket, method='bisect', xtol=1e-20)
    return sol.root


def second_moment_preserving_alpha(X, operator, bracket=[1e-9, 1.0], num_iters=20):
    def objective(alpha):
        TX = operator(X, alpha)
        return np.mean(TX**2) - np.mean(X**2)
    
    sol = root_scalar(objective, bracket=bracket, method='bisect', xtol=1e-20)
    return sol.root