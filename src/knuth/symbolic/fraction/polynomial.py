# --- Polynomial Math Helpers ---

from fractions import Fraction

def poly_zero():
    """Return the zero polynomial."""
    return {}

def poly_clean(p):
    """Remove zero-coefficient terms from the polynomial dict."""
    return {k: v for k, v in p.items() if v != 0}

def poly_add(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, Fraction(0)) + v
        if out[k] == 0:
            del out[k]
    return out

def poly_sub(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, Fraction(0)) - v
        if out[k] == 0:
            del out[k]
    return out

def poly_scale(a, scalar):
    if scalar == 0:
        return {}
    return {k: (v * scalar) for k, v in a.items()}

def poly_mul(a, b):
    if not a or not b:
        return {}
    out = {}
    for (u1, v1), c1 in a.items():
        for (u2, v2), c2 in b.items():
            key = (u1 + u2, v1 + v2)
            out[key] = out.get(key, Fraction(0)) + (c1 * c2)
    return poly_clean(out)

def poly_shift_u(a, shift=1):
    """Change u^n to u^(n+shift) for all terms."""
    if not a:
        return {}
    return { (u+shift, v): c for (u, v), c in a.items() }

def poly_shift_v(a, shift=1):
    """Change v^n to v^(n+shift) for all terms."""
    if not a:
        return {}
    return { (u, v+shift): c for (u, v), c in a.items() }
