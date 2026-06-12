import numpy as np
from scipy.optimize import root_scalar
from operators import T, T_for_positive

def compute_alpha(u, v, X, num_samples=None):
    """
    Computes the unique alpha in (0, 1] such that f(alpha) = 1.
    
    Parameters:
    - u, v: Bernoulli expectations (scalars).
    - X: 1D numpy array representing the empirical distribution of X.
    - num_samples: Number of Monte Carlo iterations for the expectation.
    """

    if num_samples is None:
        num_samples = len(X)
    
    def objective(alpha):
        TX = T(X, u, v, alpha)
        return TX - np.mean(TX) 
        
    try:
        result = root_scalar(objective, bracket=[1e-9, 1.0], method='bisect')
        return result.root
    except ValueError as e:
        raise ValueError(f"Root not bracketed in (0, 1]. Ensure E[X]=1 and bounds hold for given u, v. Detail: {e}")




def find_mean_preserving_alpha(X, operator, bracket=[1e-9, 1.0], num_iters=20):
    def objective(alpha):
        TX = operator(X, alpha)
        return np.mean(TX) - np.mean(X)
    
    sol = root_scalar(objective, bracket=bracket, method='bisect', xtol=1e-20)
    return sol.root