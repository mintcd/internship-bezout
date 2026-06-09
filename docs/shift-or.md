# Alternative Shift-Or

Let $P$ be the pattern and $T$ be the text. Let $\ell_{R}, \ell_{T}, \ell_{P}$ be the length of the register, the text and the pattern, respectively (decreasing).

1. Build mask for each character $c$ in the alphabet
    $$M[c][i] := \begin{cases} 0, &\text{ if } P[i-\ell_P] = c \text{ or } P[i-\ell_P] \text{ is undefined},\\ 1, &\text{ otherwise. } \end{cases}
     $$

2. Initiate the state $S$ such that
  $$S[i] = \begin{cases}1, & \text{ if } \ell_R - \ell_P < i < \ell_R - \ell_T,\\ 0, &\text{ otherwise }\end{cases}.$$

  $S[i] = 1$ means either there has been at least $1$ mismatch between $S[\ell_R - i-\ell_P+1\cdots \ell_R - i]$ and $P$, or the cannot be a match ending at $\ell_R - i$.

3. For $k$ from $0$ to $\ell_T-1$
    &nbsp;&nbsp; $c := T[\ell_T-1-k]$
    &nbsp;&nbsp; $S = S \,|\, M[c] \ll k$

  If $S[k] = 0$, report $\ell_R - k-\ell_P$ as the beginning of a match.
   
