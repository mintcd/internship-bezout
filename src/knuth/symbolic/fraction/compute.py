from knuth.symbolic.fraction.polynomial import *
from knuth.symbolic.fraction.IO import *

OUTPUT_DIR = "outputs/symbolic_cdfs"

def compute_Yn_symbolic(n_target):
    """Compute CDF directly using the cumulative recurrence."""
    if n_target < 0:
        raise ValueError("n_target must be non-negative")

    # Base cases
    if n_target in (0, 1):
        one = { (0, 0): Fraction(1) }
        write_cdf(n_target, [one])
        return [one]

    n = n_target - 1
    max_k = n_target // 2 
    
    # Precompute convolution sums: C_k = sum_{i=0}^{n-1} sum_{j=0}^{k} q_{i,j} q_{n-1-i, k-j}
    C = {-2: poly_zero(), -1: poly_zero()}
    for k in range(max_k):
        c_k = poly_zero()
        for i in range(n):
            for j in range(k + 1):
                q1 = get_cdf_poly(i, j)
                q2 = get_cdf_poly(n - 1 - i, k - j)
                if q1 and q2:
                    c_k = poly_add(c_k, poly_mul(q1, q2))
        C[k] = c_k

    cdf_n = []
    
    # Constant term (1-u-v) universally applied to all m values
    term_const = { (0,0): Fraction(1), (1,0): Fraction(-1), (0,1): Fraction(-1) }

    for m in range(max_k + 1):
        # Compute V_m = sum_{i=0}^{n-1} q_{i,m} q_{n-1-i,m}
        V_m = poly_zero()
        for i in range(n):
            q1 = get_cdf_poly(i, m)
            q2 = get_cdf_poly(n - 1 - i, m)
            if q1 and q2:
                V_m = poly_add(V_m, poly_mul(q1, q2))
        
        # Shift dimensions for u and v variables using the direct CDF derivation
        term_u = poly_shift_u(poly_sub(C[m-1], C[m-2]))
        term_v = poly_shift_v(V_m)
        
        # Combine, scale by 1/n, and add the constant offset
        q_m = poly_add(term_u, term_v)
        q_m = poly_scale(q_m, Fraction(1, n))
        q_m = poly_add(q_m, term_const)
        
        cdf_n.append(q_m)

    write_cdf(n_target, cdf_n)
    return cdf_n

if __name__ == "__main__":
    for target in range(20, 100):
        compute_Yn_symbolic(target)
        if target % 10 == 0:
            print(f"Computed CDF for n={target}")