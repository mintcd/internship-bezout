from decimal import Decimal
import numpy as np

from operators import T
from solver import mean_preserving_alpha

def extract_digits(alpha):
    # Formats to string cleanly to avoid floating point representation bugs
    decimal = Decimal(str(alpha))
    _, d_digits, _ = decimal.as_tuple()
    return list(d_digits)

def digits_to_float(digits_list):
    str_val = "0." + "".join(map(str, digits_list))
    return float(str_val)

def find_next_digit(u, v, alpha0=0.5, num_particles=100000, max_iter=1000):
 
    base_digits = extract_digits(alpha0)
    X_init = np.ones(num_particles)
    
    for i in range(1, 10):
    
        current_digits = base_digits + [i]
        alpha = digits_to_float(current_digits)
        
        X = np.copy(X_init)
        global_min_mean = np.mean(X_init)
        current_mean = global_min_mean
        
        for j in range(max_iter):
            X = T(X, u, v, alpha)
            current_mean = np.mean(X)
            
            if current_mean < global_min_mean:
              global_min_mean = current_mean

            if current_mean > global_min_mean * 1.20:
              print(f"alpha = {alpha}. Upcrossing confirmed. Valley was {global_min_mean}, currently at {current_mean}.")
              break
                
        if current_mean > global_min_mean * 1.20:
           continue
        
        print(f"alpha = {alpha}. No upcrossing confirmed after {max_iter} iterations.")

        current_digits = base_digits + [i-1]
        alpha = digits_to_float(current_digits) 
        
        return alpha
                
    raise ValueError("No suitable alpha found that causes the mean to increase.")

def find_alpha_mean_preserving(u, v, num_particles=1000000, num_iters=20):
  X = np.ones(num_particles)
  op = lambda x, a: T(x, u, v, a)

  for i in range(num_iters):
    alpha = mean_preserving_alpha(X, op, bracket=[1e-10, 1.0])
    X = T(X, u, v, alpha)
    print(f"Find alpha iteration {i+1}/{num_iters}: alpha = {alpha}")
  return alpha