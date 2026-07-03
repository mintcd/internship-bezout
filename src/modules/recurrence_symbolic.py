from sage.all import *

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
