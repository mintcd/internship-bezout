"""Utility helpers for notebooks and console output.

Provides `latex_print` which renders HTML-styled output when running
inside a Jupyter environment, and falls back to ANSI-colored console
output otherwise.

This module is lightweight and safe to import from notebooks.
"""
from typing import Optional
try:
    from IPython.display import display, HTML
    _HAVE_IPY = True
except Exception:
    _HAVE_IPY = False

import html as _html
import re as _re

def latex_print(text: object,
                 color: Optional[str] = None,
                 bgcolor: Optional[str] = None,
                 bold: bool = False,
                 italic: bool = False,
                 monospace: bool = False) -> None:
    """Print styled text.

    - In Jupyter: uses HTML/CSS for styling via `IPython.display.HTML`.
    - In a terminal: uses a minimal ANSI fallback for color/bold.

    Parameters
    ----------
    text: object
        Text (or object) to display. Converted with `str()`.
    color, bgcolor: Optional[str]
        CSS color names or hex values (e.g. 'red' or '#ff0000').
    bold, italic, monospace: bool
        Additional style flags.
    """
    s = str(text)
    if _HAVE_IPY:
        styles = []
        if color:
            styles.append(f"color: {color}")
        if bgcolor:
            styles.append(f"background-color: {bgcolor}")
        if bold:
            styles.append("font-weight: bold")
        if italic:
            styles.append("font-style: italic")
        if monospace:
            styles.append("font-family: monospace")
        style_str = "; ".join(styles)
        # If no explicit styling requested, prefer rendering as LaTeX
        # to match `display(Math(latex(...)))` when possible.
        if not (color or bgcolor or bold or italic or monospace):
            try:
                from IPython.display import Math
                from IPython import get_ipython

                def _safe_display_latex(latex_candidate: object) -> bool:
                    """Safely display LaTeX via `Math` if small; otherwise show
                    a preformatted HTML fallback. Returns True if something was
                    displayed.
                    """
                    try:
                        s = str(latex_candidate)
                    except Exception:
                        return False
                    candidate = s.strip()
                    # Strip surrounding dollar delimiters if present
                    if (candidate.startswith('$$') and candidate.endswith('$$')) or (
                            candidate.startswith('$') and candidate.endswith('$')):
                        if candidate.startswith('$$') and candidate.endswith('$$'):
                            candidate = candidate[2:-2].strip()
                        else:
                            candidate = candidate[1:-1].strip()

                    # Heuristic guards to avoid frontend LaTeX expansion issues
                    MAX_LATEX_LEN = 2000
                    MAX_BRACE_COUNT = 1000
                    if len(candidate) == 0:
                        return False
                    if len(candidate) <= MAX_LATEX_LEN and candidate.count('{') <= MAX_BRACE_COUNT:
                        try:
                            display(Math(candidate))
                            return True
                        except Exception:
                            # If display(Math) raises synchronously, fallthrough
                            pass

                    # Fall back to preformatted HTML to avoid frontend LaTeX parsing
                    safe_html = "<pre style='white-space:pre-wrap; font-family:monospace;'>" + _html.escape(candidate) + "</pre>"
                    try:
                        display(HTML(safe_html))
                        return True
                    except Exception:
                        return False

                ip = get_ipython()
                latex_func = None
                if ip is not None:
                    user_ns = getattr(ip, 'user_ns', {})
                    latex_func = user_ns.get('latex')

                # Try sympy.latex as a fallback if the user doesn't have
                # a notebook-level `latex` function available.
                if not callable(latex_func):
                    try:
                        from sympy import latex as _sympy_latex

                        latex_func = _sympy_latex
                    except Exception:
                        latex_func = None

                if callable(latex_func):
                    try:
                        latex_str = latex_func(text)
                        if _safe_display_latex(latex_str):
                            return
                    except Exception:
                        # If latex conversion fails, fall through to HTML
                        pass

                # If object provides a rich LaTeX repr, obtain it and render
                # it safely (avoid delegating raw rendering to the frontend).
                repr_latex = getattr(text, '_repr_latex_', None)
                if callable(repr_latex):
                    try:
                        latex_repr = repr_latex()
                        if _safe_display_latex(latex_repr):
                            return
                        # If repr returned nothing usable, show the object safely
                        display(HTML(_html.escape(str(text))))
                        return
                    except Exception:
                        pass

                # Heuristic: map trailing digit suffixes on variable names to
                # LaTeX subscripts (e.g. 'y1' -> 'y_{1}'). This helps when the
                # kernel's latex() isn't available and sympy.latex doesn't
                # format trailing digits as subscripts.
                try:
                    ss = str(text)
                    latex_guess = _re.sub(r'(?<![_\\])\b([A-Za-z]+)(\d+)\b',
                                          lambda m: f"{m.group(1)}_{{{m.group(2)}}}",
                                          ss)
                    if latex_guess != ss:
                        if _safe_display_latex(latex_guess):
                            return
                except Exception:
                    pass
            except Exception:
                # Any import/get_ipython errors -> fall back to HTML below
                pass

        safe = _html.escape(s)
        html = f"<div style=\"{style_str}\">{safe}</div>" if style_str else safe
        display(HTML(html))
        return

    # Terminal fallback: minimal ANSI support
    COLORS = {
        'black': '30', 'red': '31', 'green': '32', 'yellow': '33',
        'blue': '34', 'magenta': '35', 'cyan': '36', 'white': '37'
    }
    codes = []
    if bold:
        codes.append('1')
    if color and color in COLORS:
        codes.append(COLORS[color])
    prefix = '\x1b[' + ';'.join(codes) + 'm' if codes else ''
    suffix = '\x1b[0m' if codes else ''
    print(prefix + s + suffix)

__all__ = ['latex_print']

def report_memory(obj):
  try:
    bytes_alloc = obj.nbytes
  except Exception:
      import sys
      bytes_alloc = sys.getsizeof(obj)
  def _format_bytes(n):
      for unit in ['B','KB','MB','GB','TB']:
          if n < 1024.0:
              return f"{n:.2f}{unit}"
          n /= 1024.0
      return f"{n:.2f}PB"
  print(f"Allocated memory for 'history': {_format_bytes(bytes_alloc)} ({bytes_alloc} bytes)")