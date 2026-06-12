import numpy as np
from monte_carlo import sample_from_empirical

def T(X, u,v, alpha):
    # Sample independent pairs
    X1 = sample_from_empirical(X)
    X2 = sample_from_empirical(X)
    
    # Sample U, I and J
    U = np.random.uniform(0, 1, size=len(X))
    R = np.random.uniform(0, 1, size=len(X))
    
    I = (R < u).astype(np.float64)
    J = ((R >= u) & (R < u + v)).astype(np.float64)
    
    # Apply the operator T_alpha
    term1 = (U**alpha) * X1
    term2 = ((1 - U)**alpha) * X2
    
    T_X = I * (term1 + term2) + J * np.maximum(term1, term2)

    return T_X

def T_independent(X, u, v, alpha):
    # Sample independent pairs
    X1 = sample_from_empirical(X)
    X2 = sample_from_empirical(X)
    
    # Sample U
    U1 = np.random.uniform(0, 1, size=len(X))
    U2 = np.random.uniform(0, 1, size=len(X))
    
    # Apply the operator T_alpha
    term1 = (U1**alpha) * X1
    term2 = ((1 - U2)**alpha) * X2
    
    T_X = term1 + term2

    return T_X


def S(X, u, v, alpha):
    TX = T(X, u, v, alpha)
    return TX/np.mean(TX)

def T_for_positive(Z, u, v, alpha):
    """
    Applies the transformation operator for the conditional random variable Z.
    Requires an external `sample_from_empirical(X)` function, which can be defined as:
    return np.random.choice(X, size=len(X), replace=True)
    """
    w = 1.0 / (u + v)
    
    # Validate parameters to ensure valid branch probabilities
    if not (1.0 <= w <= 2.0):
        raise ValueError(f"Parameters u+v must be in [0.5, 1]. Current w={w}")
        
    N = len(Z)
    
    # Sample independent elements
    Z1 = sample_from_empirical(Z)
    Z2 = sample_from_empirical(Z)
    
    # Sample U and branch selector R
    U = np.random.uniform(0, 1, size=N)
    R = np.random.uniform(0, 1, size=N)
    
    # Calculate branch probabilities
    p_sum = u * (2 - w)
    p_max = v * (2 - w)
    # The remainder is naturally 2 * (1 - 1/w)
    
    # Create branch indicators using the inverse transform method for discrete mixtures
    I_sum = (R < p_sum).astype(np.float64)
    I_max = ((R >= p_sum) & (R < p_sum + p_max)).astype(np.float64)
    I_single = (R >= p_sum + p_max).astype(np.float64)
    
    # Compute the components
    term1 = (U**alpha) * Z1
    term2 = ((1 - U)**alpha) * Z2
    
    # Apply the operator based on the chosen branch
    T_Z = (
        I_sum * (term1 + term2) + 
        I_max * np.maximum(term1, term2) + 
        I_single * term1
    )

    return T_Z