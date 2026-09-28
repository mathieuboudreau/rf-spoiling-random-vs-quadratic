---
title: Why not just use random phases?
short_title: The question
---

> *"If the goal of RF spoiling is just to scramble the phase of the transverse
> magnetization, why do we use this specific formula,*
> $\phi_n = \phi_0 \frac{n(n+1)}{2}$*, instead of a random number generator?"*
>
> — a student, in class

It's a good question, and the answer isn't obvious. A random phase *does*
scramble the transverse magnetization. On average it even does a slightly
better job than the quadratic scheme. What it does badly is let the sequence
reach a **steady state**.

:::{important} Short answer
- **Quadratic phase cycling** drives every voxel into a *true steady state*.
  After the transient, the signal is exactly the same every TR. It is close
  to (but not exactly) the ideal Ernst-equation signal, and the small bias is
  deterministic and reproducible.
- **Random phases** are *unbiased on average*, but the signal never settles.
  It changes in magnitude and phase from one TR to the next.
- In an image, one phase-encoding line is acquired per TR. Those random
  TR-to-TR fluctuations modulate k-space and appear as **ghosting and
  noise-like artifacts along the phase-encode direction**. More dummy scans
  don't remove them.
:::

## How to use this book

Each page builds on the previous one, from a handful of spins up to a full image.
All figures are interactive: hover for values, use the sliders to change the flip
angle, click legend entries to hide or show curves, and drag to zoom.

1. [](theory.md) covers the SPGR sequence, why gradient spoiling alone is not
   enough, and why the quadratic formula produces a steady state (and random
   phases don't).
2. [](few-spins.md) shows the RF phase schedules, a few isochromats in a voxel,
   and the voxel signal in the complex plane.
3. [](steady-state.md) compares signal over time, signal against flip angle,
   and the effect of the choice of $\phi_0$.
4. [](image.md) shows what each scheme does to a full image.
5. [](takeaways.md) summarizes the results and gives discussion questions for class.

:::{note} Simulation model
All results come from a small isochromat Bloch simulation (`spoilsim/`). A voxel
contains many isochromats, which the spoiler gradient dephases uniformly over
$2\pi$ each TR. RF pulses are instantaneous, the signal is read right after
each pulse ($\mathrm{TE}\to 0$), and the receiver phase follows the RF phase.
Unless stated otherwise, $\mathrm{TR} = 10$ ms.
:::
