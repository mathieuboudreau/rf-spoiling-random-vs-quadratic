---
title: Why the quadratic formula works
short_title: Theory
---

## The goal of spoiling

A spoiled gradient echo (SPGR / FLASH) sequence is meant to behave as if *all*
transverse magnetization disappeared before the next RF pulse. The steady-state
signal then follows the Ernst equation:

$$
S_\text{Ernst}(\alpha) = M_0 \sin\alpha \,\frac{1 - E_1}{1 - E_1\cos\alpha},
\qquad E_1 = e^{-\mathrm{TR}/T_1}.
$$ (ernst)

With $\mathrm{TR} \ll T_2$, the transverse magnetization has not decayed by the
next pulse, so something has to destroy it.

## Gradient spoiling alone is not enough

A spoiler gradient at the end of each TR dephases the voxel. The isochromat at
position $\theta\in[0,2\pi)$ picks up an extra phase $\theta$ every TR. The net
transverse magnetization at the end of the TR is then zero, but the individual
isochromats still carry their transverse components. Because the gradient is
**the same every TR**, later RF pulses **refocus** these components into echoes
(stimulated echoes and higher-order pathways) that land exactly at the next
readout. The steady state then depends on $T_2$ and is far from
{eq}`ernst`, as shown by the green curves on the next pages.

## RF spoiling: change the RF phase every TR

If the phase of each RF pulse is changed, and the receiver is demodulated with
the same phase, the refocused pathways add up with *different* phases and
cancel. The standard choice (Zur et al., 1991) is a **quadratic** phase
schedule:

$$
\phi_n = \phi_0\,\frac{n(n+1)}{2}
\quad\Longleftrightarrow\quad
\Delta\phi_n = \phi_n - \phi_{n-1} = n\,\phi_0 .
$$ (quad)

The phase *increment* grows linearly, so the second difference is a constant
$\phi_0$ (often $117^\circ$ or $50^\circ$).

## Why the quadratic schedule gives a steady state

Work in the receiver frame, demodulated by $\phi_n$ at TR $n$. Let
$\mathbf m_n(\theta)$ be the magnetization of isochromat $\theta$ just after
pulse $n$. Going from pulse $n$ to pulse $n+1$, the isochromat relaxes and
precesses by $\theta$. The frame then rotates by $-\Delta\phi_{n+1}$, and the RF
pulse (now always about $x$) is applied. The only thing that depends on $n$ is
the **effective precession angle**

$$
\theta_\text{eff} = \theta - \Delta\phi_{n+1} = \theta - (n+1)\,\phi_0 .
$$

Now relabel the isochromats and follow $\mathbf u_n(\vartheta) = \mathbf m_n(\vartheta + n\phi_0)$.
Substituting gives

$$
\mathbf u_{n+1}(\vartheta) = \mathcal F\!\left[\mathbf u_n(\vartheta + \phi_0);\ \vartheta\right],
$$

where $\mathcal F$ (relax, precess by $\vartheta$, rotate by $\alpha$) **does not
depend on $n$ at all**. Relaxation makes this map contractive, so
$\mathbf u_n \to \mathbf u^\star$, a fixed pattern. In the original labels,

$$
\mathbf m_n(\theta) = \mathbf u^\star(\theta - n\phi_0):
$$

the magnetization pattern across the voxel is the *same* every TR, just
**shifted by $\phi_0$ along the dephasing axis**. The voxel signal is the
average over $\theta\in[0,2\pi)$, and a shift doesn't change that average:

$$
s_n = \frac{1}{2\pi}\int_0^{2\pi} m_{xy,n}(\theta)\,d\theta = \text{constant}.
$$

That is a **true steady state**. The value of the constant depends on
$\phi_0$, $T_1$, $T_2$ and $\alpha$. For well-chosen $\phi_0$ it is close to
{eq}`ernst`, but not exactly equal to it, because some refocused pathways still
add up coherently.

## Why random phases do not

With random phases, $\Delta\phi_{n+1}$ is a new random number every TR. No
relabelling of isochromats makes the map independent of $n$, so there is no
fixed point, and the voxel signal is a **random variable at every TR**.

In the echo-pathway picture, each refocused pathway reaching the readout
carries a phase that is a sum of *several different random phases*. Averaged
over many TRs these contributions cancel, which is why random spoiling is
*unbiased*: the mean signal equals the Ernst signal. At any single TR, though,
they don't cancel, so the signal jitters around the Ernst value in magnitude
and phase. The longer $T_2$ is compared with $\mathrm{TR}$, the more pathways
survive and the larger the jitter.

:::{tip} It's not randomness itself that's the problem
A pseudo-random sequence with a fixed seed is perfectly reproducible from scan
to scan. The issue is the lack of structure *within* a scan. The quadratic
schedule has a hidden symmetry (the constant second difference) that turns
every TR into a shifted copy of the previous one. Any sequence without that
symmetry, whether random or not, fails to reach a steady state.
:::

The next page shows this with a handful of spins.
