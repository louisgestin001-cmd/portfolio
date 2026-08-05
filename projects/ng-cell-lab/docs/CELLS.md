# Cell cards

## NG-StateMin-U1

### Law

\[
s_t=y_t=\min(x_t-s_{t-1},-x_t).
\]

### Structure

- one scalar state per hidden coordinate;
- no learned internal coefficient;
- one subtraction, one negation, and one minimum;
- piecewise temporal derivative in \(\{-1,0\}\).

### Verified behavior

On its memory branch, a fixed negative preactivation gives

\[
s_t=x-s_{t-1},\qquad s_{t+1}=s_{t-1},
\]

which is an exact period-two involution. This avoids gradient attenuation on that branch, but makes readout phase-sensitive.

### Classification

Specialized oscillatory memory, not a general recurrent replacement.

---

## NG-ShiftCompare-Mul

### Law

\[
c=1.231609\sin(1)+0.029583,
\]

\[
a_t=1.164214(x_t-c)-0.074532,
\]

\[
q_t=0.646213s_{t-1}-0.110654,
\]

\[
b_t=1.291792\tanh(q_t-x_t)-0.070705,
\]

\[
s_t=y_t=\operatorname{clip}\left(0.907561a_tb_t-0.145458,-20,20\right).
\]

The clamp value was implicit in the candidate description; the original benchmark used \([-20,20]\), exposed as a constructor parameter in the package.

### Temporal Jacobian

\[
\frac{\partial s_t}{\partial s_{t-1}}
=
0.907561\,a_t\,1.291792\,0.646213\,
\operatorname{sech}^2(q_t-x_t).
\]

It can locally exceed one, but products typically vanish on irregular sequences. For common normalized preactivations, the derivative is often negative, encouraging phase alternation.

### Classification

Expressive multiplicative comparator with a strong period-two attractor.

---

## NG-EnergyMax-1

### Law

\[
e_t=\frac1d\sum_j|x_{t,j}|,
\]

\[
y_t=0.922865\max(s_{t-1},0.839798e_tx_t),
\qquad s_t=x_t.
\]

The maximum is coordinatewise.

### Exact memory horizon

Because \(s_t=x_t\),

\[
\frac{\partial s_t}{\partial s_{t-1}}=0.
\]

The final output depends on the current and immediately previous input only. No optimizer can turn this standalone law into longer state memory.

### Scaling

For positive scale \(\lambda\), the energy branch grows as \(\lambda^2\). A clamp or normalization is therefore required at large amplitudes.

### Classification

Global-energy-modulated two-frame operator.

---

## NG-EnergyMax-2

### Law

\[
e_t=\frac1d\sum_j|x_{t,j}|,
\qquad g_t=\frac{e_t}{1+e_t},
\]

\[
u_t=0.839798g_tx_t,
\]

\[
s_t=\operatorname{ChooseMaxAbs}(\rho s_{t-1},u_t),
\qquad y_t=0.922865s_t.
\]

`ChooseMaxAbs` preserves the sign of whichever argument has larger absolute magnitude. The package default is \(\rho=0.999\).

### Temporal derivative

Away from equality surfaces,

\[
\frac{\partial s_t}{\partial s_{t-1}}
\in\{\rho,0\}.
\]

It cannot explode when \(\rho\le1\). The memory half-life is

\[
T_{1/2}=\frac{\log(1/2)}{\log\rho}.
\]

For \(\rho=0.999\), this is about 693 steps.

### Classification

Sparse event and extremum memory. Strong on delayed sparse signals, weak on ordered dense streams.

---

## NG-LagMean-1

### Law

\[
\bar x_t=\frac1d\sum_jx_{t,j},
\]

\[
s_t=\operatorname{clip}(0.5\bar x_t+0.011376,-32,32),
\]

\[
y_{t,i}=\operatorname{clip}
\left(
\operatorname{clip}(s_{t-1}x_{t,i},-32,32)-0.097814,
-32,32
\right).
\]

### Information rank

Away from clipping,

\[
\frac{\partial y_{t,i}}{\partial x_{t-1,j}}=\frac{x_{t,i}}{2d}.
\]

Every column is identical, so the cross-time Jacobian has rank at most one. Only the mean direction is transmitted.

### LayerNorm interaction

A centered LayerNorm makes \(\bar x_t\approx0\), hence

\[
s_t\approx0.011376.
\]

The collective state becomes nearly constant unless it is computed before centering or replaced by a non-centered statistic.

### Classification

Fast, rank-one delayed multiplicative modulator.
