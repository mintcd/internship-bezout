from knuth.symbolic.fraction.IO import read_cdf, get_cdf_poly
from fractions import Fraction


def _eval_poly(poly, u, v):
  """Evaluate a structured polynomial (dict) at (u, v) and return Fraction."""
  if not poly:
    return Fraction(0)
  out = Fraction(0)
  for (up, vp), coeff in poly.items():
    out += coeff * (u ** up) * (v ** vp)
  return out


def compute_expectation(n, u=Fraction(1, 2), v=Fraction(1, 2)):
  """Compute E[Y_n] using

  e_n = floor(n/2) - sum_{m=0}^{floor(n/2)} q_m,

  where q_m = P(Y_n <= m) is stored symbolically in the CDF (polynomials
  in `u` and `v`). Returns an exact `Fraction`.
  """
  half = n // 2
  total = Fraction(0)
  for m in range(half + 1):
    q_poly = get_cdf_poly(n, m)
    total += _eval_poly(q_poly, u, v)
  return Fraction(half) - total
  