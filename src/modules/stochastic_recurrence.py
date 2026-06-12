"""
Different ways to compute/simulate Yn
"""

from sage.all import *
import numpy as np
from numba import njit, objmode, prange

def compute_Yns_symbolic(N):
    """
    Compute symbolic PMFs, CDFs, and expected values for Y_n using Sage symbolic expressions.
    This is primarily for small N (less than 60) due to complexity of fractions.
    """
    
    u, v = var('u v')
    
    # Initialize ragged arrays (dynamically sized based on max possible value)
    pmfs = [[SR(0)] * ((i + 1) // 2 + 1) for i in range(N + 1)]
    cdfs = [[SR(1)] * ((i + 1) // 2 + 1) for i in range(N + 1)]
    
    # Base cases: Y_1 = 1, Y_2 = 0
    pmfs[1][1] = SR(1)
    pmfs[2][0] = SR(1)
    
    # Base CDFs
    cdfs[1][0] = SR(0)

    termination_prob = 1 - u - v

    for n_target in range(3, N + 1):
        n = n_target - 2
        target_len = (n_target + 1) // 2 + 1

        for k in range(target_len): 
            prob_k = SR(0)
            
            for i in range(1, n + 1):
                idx1 = i
                idx2 = n + 1 - i
                
                len1 = len(pmfs[idx1])
                len2 = len(pmfs[idx2])
                
                # Term I: Bounded discrete convolution
                c_prob = SR(0)
                
                # Ensure j is valid for pmfs[idx1] AND (k - j) is valid for pmfs[idx2]
                j_start = max(0, k - len2 + 1)
                j_end = min(k, len1 - 1)
                
                for j in range(j_start, j_end + 1):
                    c_prob += pmfs[idx1][j] * pmfs[idx2][k - j]
                        
                # Term J: Maximum of independent copies
                # Safe getter for ragged CDF arrays
                def get_cdf(arr, idx):
                    if idx < 0: return SR(0)
                    if idx >= len(arr): return arr[-1] # Beyond support, CDF is maxed
                    return arr[idx]
                
                cdfs1_k = get_cdf(cdfs[idx1], k)
                cdfs2_k = get_cdf(cdfs[idx2], k)
                cdfs1_k_minus_1 = get_cdf(cdfs[idx1], k - 1)
                cdfs2_k_minus_1 = get_cdf(cdfs[idx2], k - 1)
                
                m_prob = (cdfs1_k * cdfs2_k) - (cdfs1_k_minus_1 * cdfs2_k_minus_1)
                
                prob_k += u * c_prob + v * m_prob
                
            t_prob = SR(1) if k == 0 else SR(0)
            
            pmfs[n_target][k] = ((prob_k / n) + (termination_prob * t_prob)).expand()
            
        # CDF update over the dynamically truncated length
        current_cdf = SR(0)
        for k in range(target_len):
            current_cdf += pmfs[n_target][k]
            cdfs[n_target][k] = current_cdf.expand()

    # Expectation logic strictly iterates over available lengths
    expected_values = []
    for i in range(1, N + 1):
        expected_y = sum((k * pmfs[i][k] for k in range(len(pmfs[i]))), SR(0))
        expected_values.append(SR(expected_y).expand())

    # Ragged arrays inherently act as truncated versions already
    return pmfs, cdfs, expected_values

def compute_Yns_numerical(N, u, v, precision_bits=53, callback=None):
    """
    Computes numerical PMFs, CDFs, and expected values using arbitrary precision.
    """
    # Set up Sage's Arbitrary Precision Real Field
    R = RealField(precision_bits)
    
    u = R(u)
    v = R(v)
    termination_prob = R(1) - u - v
    
    # Helper to calculate exact required length for Y_i to avoid truncation bugs
    # Y_0 = 1, Y_1 = 0. Max value of Y_i <= i // 2 + 1
    # Therefore, array length should be (i // 2) + 2
    def get_len(i):
        return (i // 2) + 2

    # Initialize dynamically sized arrays
    pmfs = [[R(0)] * get_len(i) for i in range(N + 1)]
    cdfs = [[R(0)] * get_len(i) for i in range(N + 1)]
    
    # Base cases: Y_0 = 1, Y_1 = 0
    pmfs[0][1] = R(1)
    pmfs[1][0] = R(1)
    
    # Initialize CDFs for base cases
    cdfs[0][0] = R(0)
    cdfs[0][1] = R(1)
    
    cdfs[1][0] = R(1)
    cdfs[1][1] = R(1)
        
    for n_target in range(2, N + 1):
        
        if n_target % 100 == 0:
            print(f"Computing Y_{n_target}...")

        n = n_target - 1
        target_len = get_len(n_target)

        for k in range(target_len): 
            prob_k = R(0)
            
            for i in range(n):
                idx1 = i
                idx2 = n - 1 - i
                
                len1 = len(pmfs[idx1])
                len2 = len(pmfs[idx2])
                
                # Term I: Bounded discrete convolution
                c_prob = R(0)
                j_start = max(0, k - len2 + 1)
                j_end = min(k, len1 - 1)
                
                for j in range(j_start, j_end + 1):
                    c_prob += pmfs[idx1][j] * pmfs[idx2][k - j]
                        
                # Term J: Maximum of independent copies (Subtraction-Free)
                def get_val(arr, idx, is_cdf=False):
                    if idx < 0: 
                        return R(0)
                    if idx >= len(arr): 
                        return arr[-1] if is_cdf else R(0)
                    return arr[idx]
                
                if k == 0:
                    m_prob = pmfs[idx1][0] * pmfs[idx2][0]
                else:
                    pmf1_k = get_val(pmfs[idx1], k, False)
                    pmf2_k = get_val(pmfs[idx2], k, False)
                    cdf1_k_minus_1 = get_val(cdfs[idx1], k - 1, True)
                    cdf2_k = get_val(cdfs[idx2], k, True)
                    
                    # Subtraction-free logic handles out-of-bounds indices automatically via get_val
                    m_prob = (pmf1_k * cdf2_k + cdf1_k_minus_1 * pmf2_k)
                
                prob_k += u * c_prob + v * m_prob
                
            t_prob = R(1) if k == 0 else R(0)
            
            # Update PMF array
            pmfs[n_target][k] = (prob_k / n) + (termination_prob * t_prob)
            
        # Update the CDF array sequentially
        current_cdf = R(0)
        for k in range(target_len):
            current_cdf += pmfs[n_target][k]
            cdfs[n_target][k] = current_cdf

    # Compute expected values by directly iterating over available ragged lengths
    expected_values = []
    for i in range(0, N + 1):
        expected_y = sum(R(k) * pmfs[i][k] for k in range(len(pmfs[i])))
        expected_values.append(expected_y)

    # Truncation step removed: arrays are perfectly sized natively
    return pmfs, cdfs, expected_values

@njit(cache=True)
def compute_Yns_numba(N, u, v):
    """
    Computes numerical PMFs, CDFs, and expected values using Numba JIT.
    Precision is strictly standard double precision (float64, 53-bit mantissa).
    """
    # Calculate the maximum possible column length needed
    max_len = (N // 2) + 2
    
    # Initialize rectangular NumPy arrays with zeros
    pmfs = np.zeros((N + 1, max_len), dtype=np.float64)
    cdfs = np.zeros((N + 1, max_len), dtype=np.float64)
    
    termination_prob = 1.0 - u - v
    
    # Base cases: Y_0 = 1, Y_1 = 0
    pmfs[0, 1] = 1.0
    pmfs[1, 0] = 1.0
    
    # Initialize CDFs for base cases
    cdfs[0, 1:] = 1.0 # 0.0 at index 0, 1.0 everywhere else
    cdfs[1, :] = 1.0  # 1.0 everywhere
        
    for n_target in range(2, N + 1):

        if n_target % 100 == 0:
            with objmode():
                print(f"Processing n_target = {n_target} / {N}", flush=True)

        n = n_target - 1
        target_len = (n_target // 2) + 2

        for k in range(target_len): 
            prob_k = 0.0
            
            for i in range(n):
                idx1 = i
                idx2 = n - 1 - i
                
                len1 = (idx1 // 2) + 2
                len2 = (idx2 // 2) + 2
                
                # Term I: Bounded discrete convolution
                c_prob = 0.0
                j_start = max(0, k - len2 + 1)
                j_end = min(k, len1 - 1)
                
                for j in range(j_start, j_end + 1):
                    c_prob += pmfs[idx1, j] * pmfs[idx2, k - j]
                        
                # Term J: Subtraction-free maximum
                if k == 0:
                    m_prob = pmfs[idx1, 0] * pmfs[idx2, 0]
                else:
                    # Safe getters implemented via conditional logic 
                    # rather than function calls to maximize Numba inlining
                    pmf1_k = pmfs[idx1, k] if k < len1 else 0.0
                    pmf2_k = pmfs[idx2, k] if k < len2 else 0.0
                    
                    cdf1_k_minus_1 = cdfs[idx1, k - 1] if (k - 1) < len1 else cdfs[idx1, len1 - 1]
                    cdf2_k = cdfs[idx2, k] if k < len2 else cdfs[idx2, len2 - 1]
                    
                    m_prob = (pmf1_k * cdf2_k + cdf1_k_minus_1 * pmf2_k)
                
                prob_k += u * c_prob + v * m_prob
                
            t_prob = 1.0 if k == 0 else 0.0
            pmfs[n_target, k] = (prob_k / n) + (termination_prob * t_prob)
            
        # Update the CDF array sequentially
        current_cdf = 0.0
        for k in range(target_len):
            current_cdf += pmfs[n_target, k]
            cdfs[n_target, k] = current_cdf

    # Compute expected values
    expected_values = np.zeros(N + 1, dtype=np.float64)
    for i in range(N + 1):
        expected_y = 0.0
        current_len = (i // 2) + 2
        for k in range(current_len):
            expected_y += k * pmfs[i, k]
        expected_values[i] = expected_y

    return pmfs, cdfs, expected_values

def simulate_Yns_independent(N, u, v, num_particles, callback=None):
    """
        Simulates Y_n for n=1 to N using num_particles samples.
    """

    history = np.zeros((N + 1, num_particles), dtype=int)
    history[1, :] = 1 # Y_1 = 1
    
    for n_target in range(3, N + 1):
        n = n_target - 2

        # Uniform indices
        Un = np.random.randint(1, n+1, size=num_particles)
        idx1 = Un
        idx2 = n + 1 - Un
        
        # Sample independent copies Y^(1) and Y^(2) 
        p_idx1 = np.random.randint(0, num_particles, size=num_particles)
        p_idx2 = np.random.randint(0, num_particles, size=num_particles)
        
        y1 = history[idx1, p_idx1]
        y2 = history[idx2, p_idx2]
        
        # Determine the Bernoulli events I and J
        rand_vals = np.random.rand(num_particles)
        
        mask_I = rand_vals < u
        mask_J = (rand_vals >= u) & (rand_vals < u + v)
        
        # Apply the recurrence formula conditionally
        y_new = np.zeros(num_particles, dtype=int)
        y_new[mask_I] = y1[mask_I] + y2[mask_I]
        y_new[mask_J] = np.maximum(y1[mask_J], y2[mask_J])
        
        history[n_target] = y_new

        if n_target % 1000 == 0:
            print(f"Iteration {n_target}/{N} completed.")
    
    return history

def simulate_Yns(N, u, v, num_particles, callback=None):
    """
        Simulates Y_n for n=1 to N using num_particles samples.
    """

    history = np.zeros((N + 1, num_particles), dtype=int)
    history[1, :] = 1 # Y_1 = 1
    
    for n_target in range(3, N + 1):
        n = n_target - 2

        # Uniform indices
        idx1 = np.random.randint(1, n+1, size=num_particles)
        idx2 = np.random.randint(1, n+1, size=num_particles)
        
        # Sample independent copies Y^(1) and Y^(2) 
        p_idx1 = np.random.randint(0, num_particles, size=num_particles)
        p_idx2 = np.random.randint(0, num_particles, size=num_particles)
        
        y1 = history[idx1, p_idx1]
        y2 = history[idx2, p_idx2]
        
        # Determine the Bernoulli events I and J
        rand_vals = np.random.rand(num_particles)
        
        mask_I = rand_vals < u
        mask_J = (rand_vals >= u) & (rand_vals < u + v)
        
        # Apply the recurrence formula conditionally
        y_new = np.zeros(num_particles, dtype=int)
        y_new[mask_I] = y1[mask_I] + y2[mask_I]
        y_new[mask_J] = np.maximum(y1[mask_J], y2[mask_J])
        
        history[n_target] = y_new

        if n_target % 1000 == 0:
            print(f"Iteration {n_target}/{N} completed.")
    
    return history

@njit(parallel=True, cache=True)
def simulate_Yns_numba(N, u, v, num_particles):
    """
    Simulates Y_n using parallel multi-threading over particles.
    """
    # Explicitly define dtype to avoid 64-bit float fallback
    history = np.zeros((N + 1, num_particles), dtype=np.int32)
    history[1, :] = 1 # Y_1 = 1
    
    # Base cases: Y_1 = 1, Y_2 = 0 (history[0] remains unused/zero)
    for p in prange(num_particles):
        history[1, p] = 1
    
    for n_target in range(3, N + 1):
        n = n_target - 2

        # Parallelize strictly over the independent particles
        for p in prange(num_particles):
            
            # Sample U_n 
            Un = np.random.randint(1, n + 1)
            idx1 = Un
            idx2 = n + 1 - Un
            
            # Sample independent copies Y^(1) and Y^(2)
            p_idx1 = np.random.randint(0, num_particles)
            p_idx2 = np.random.randint(0, num_particles)
            
            y1 = history[idx1, p_idx1]
            y2 = history[idx2, p_idx2]
            
            # Determine the Bernoulli events using a single random draw
            rand_val = np.random.rand()
            
            if rand_val < u:
                history[n_target, p] = y1 + y2
            elif rand_val < u + v:
                history[n_target, p] = max(y1, y2)
            else:
                pass # history[n_target, p] remains 0 due to initialization

        if n_target % 1000 == 0:
            with objmode():
                print(f"Iteration {n_target}/{N} completed.", flush=True)
                
    return history