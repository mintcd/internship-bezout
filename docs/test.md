$$|T_\alpha(Z) - T_\alpha(Z')| \le I \cdot \big( U^\alpha \Delta_1 + (1-U)^\alpha \Delta_2 \big) + J \cdot \begin{cases}
U^\alpha \Delta_1 & \text{if branch 1 is max} \
(1-U)^\alpha \Delta_2 & \text{if branch 2 is max}
\end{cases}$$

$z_{n+2} = \dfrac{2^u}{n}\sum\limits_{i=1}^n (z_iz_{n+1-i})^{u}(z_i + z_{n+1-i})^v, z_1=z_2=1$

$(n+2)^\beta \ge \max\limits_{1\le i\le n} [u(i^\alpha + (n+1-i)^\alpha) + v\max(i^\alpha, (n+1-i)^\alpha)]$

$x_{n+2} = 2+\max\limits_{1\le i\le n} (x_i + x_{n+1-i} + \max(x_i, x_{n+1-i})), x_1=x_2=0$

$z_{n+2} = \dfrac{2}{n}\sum\limits_{i=1}^n (uz_iz_{n+1-i}+vz_i) + 1-u-v, z_1=z_2=1$

$p_{n+2} = 1-u-v + \dfrac{v}{n}\sum\limits_{i=1}^n p_ip_{n+1-i}, p_1=p_2=1$

$p(n+2,m) = \dfrac{u}{n}\sum\limits_{i=1}^n\sum\limits_{j=0}^{m-1} p(i,j)p(n+1-j,m-1-j) + \dfrac{v}{n}\sum\limits_{i=1}^np(i,m)p(n+1-i,m), p(1,m) = p(2,m) = 1,\forall m$

$z_{n+1} = 1-u-v + \dfrac{v}{n}\sum\limits_{i=0}^{n-1} z_iz_{n-1-i}, \forall n\ge 1, \quad z_0=z_1=1$

$\mathbb{P}(\max(Y_i^{(1)}, Y_{n-1-i}^{(2)}) \le m) = p_{i,m}q_{n-1-i,m} + p_{n-1-i,m}q_{i,m} - p_{i,m}p_{n-1-i,m}$

$$\mathbb{P}(\max(X,Y) = c) = p_X F_Y(c) + p_Y F_X(c) - p_X p_Y$$


$$Y_{n+1} \stackrel{d}{=} I^{(n)}\left(Y_{U_n}^{(1)} + Y_{n-1-U_n}^{(2)}\right) + J^{(n)}\max\left(Y_{U_n}^{(1)}, Y_{n-1-U_n}^{(2)}\right), \forall n\ge 1, \quad Y_0=1, Y_1=0.$$

The variables $I$ and $J$ are Bernoulli with expectation $u$ and $v$ respectively, such that $I + J \le 1$. That means we can only either take the sum-plus-one term, or the max term, or zero. The variable $U_n$ is uniformly distributed on $\{0, \ldots, n-1\}$. Superscripts are for independent copies.

$\lfloor n/2\rfloor- \sum\limits_{m=0}^{\lfloor n/2\rfloor}q_m$


$\mathbb{E}[\max(Y_{U_n}^{(1)}, Y_{n-1-U_n}^{(2)})]=\dfrac{1}{n}\sum_{i=0}^{n-1}\mathbb{E}[\max(Y_{i}^{(1)}, Y_{n-1-i}^{(2)})]\ge \dfrac{1}{n}\sum_{i=0}^{n-1}\max(\mathbb{E}[Y_{i}^{(1)}], \mathbb{E}[Y_{n-1-i}^{(2)}])$


$$Y'_n= \dfrac{2u+v-1}{u}Y_n + 1$$

$$Y_{n+1}' \stackrel{d}{=} I^{(n)}\left(Y_{U_n}'^{(1)} + Y_{n-1-U_n}'^{(2)}\right) + J^{(n)}\max\left(Y_{U_n}'^{(1)}, Y_{n-1-U_n}'^{(2)}\right) + u(1-J^{(n)})-I^{(n)}(1-v), \forall n\ge 1, \quad Y'_0=Y'_1=1.$$

$$Y_{n+1}'' \stackrel{d}{=} I^{(n)}\left(Y_{U_n}''^{(1)} + Y_{n-1-U_n}''^{(2)}\right) + J^{(n)}\max\left(Y_{U_n}''^{(1)}, Y_{n-1-U_n}''^{(2)}\right), \forall n\ge 1, \quad Y''_0=Y''_1=1.$$


$X \stackrel{d}{=} I\left(U^{\alpha} X^{(1)} + \left(1-U\right)^{\alpha} X^{(2)}\right) + J\max\left(U^{\alpha} X^{(1)}, \left(1-U\right)^{\alpha} X^{(2)}\right), \quad X^{(1)}, X^{(2)} \stackrel{\text{iid}}{\sim} X$.

$I$ and $J$ are independent, mutually exclusive Bernoulli with expectation $u$ and $v$ respectively, such that $u > 1/2$. 