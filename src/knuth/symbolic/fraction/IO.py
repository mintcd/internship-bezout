from collections import OrderedDict
from fractions import Fraction
import json
import os

OUTPUT_DIR = "outputs/symbolic_cdfs"
CACHE_LIMIT = 64

# --- Global Caches ---
_cdf_cache = OrderedDict()



# --- I/O and Cache Management ---
def _poly_to_terms(poly):
    """Convert poly dict -> list of [u_power, v_power, numer, denom]."""
    out = []
    for (up, vp), coeff in sorted(poly.items()):
        out.append([up, vp, coeff.numerator, coeff.denominator])
    return out

def _is_exact_one(poly):
    return len(poly) == 1 and poly.get((0, 0), None) == Fraction(1)

def read_cdf(n):
    """Read structured-term CDF from file, caching the result in memory."""
    if n in _cdf_cache:
        _cdf_cache.move_to_end(n)
        return _cdf_cache[n]

    path = os.path.join(OUTPUT_DIR, f"cdf_{n}.txt")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing CDF for n={n}; cannot compute higher targets.")

    cdf = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            terms = json.loads(line)
            poly = {}
            for t in terms:
                up, vp, numer, denom = t
                coeff = Fraction(int(numer), int(denom))
                if coeff != 0:
                    poly[(int(up), int(vp))] = coeff
            cdf.append(poly)

    # Ensure termination bounds
    if len(cdf) == 0 or not _is_exact_one(cdf[-1]):
        cdf = list(cdf)
        if len(cdf) == 0:
            cdf = [ { (0,0): Fraction(1) } ]
        else:
            cdf[-1] = { (0,0): Fraction(1) }

    _cdf_cache[n] = cdf
    _cdf_cache.move_to_end(n)
    
    while len(_cdf_cache) > CACHE_LIMIT:
        _cdf_cache.popitem(last=False)

    return cdf

def write_cdf(n, cdf):
    """Write structured-term CDF to file and update the memory cache."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"cdf_{n}.txt")
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        for poly in cdf:
            terms = _poly_to_terms(poly)
            f.write(json.dumps(terms, separators=(",", ":")) + "\n")
    os.replace(tmp, path)

    _cdf_cache[n] = cdf
    _cdf_cache.move_to_end(n)

def get_cdf_poly(n, k):
    arr = read_cdf(n)
    if k >= len(arr):
        return arr[-1]
    return arr[k]