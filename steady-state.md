---
title: Steady state (or not)
kernelspec:
  name: python3
  display_name: Python 3
---

This page moves from pictures of spins to numbers: the signal magnitude over
time, the steady-state signal against flip angle, and the role of $\phi_0$. Two
tissues are compared:

- **white matter-like** ($T_1 = 830$ ms, $T_2 = 80$ ms), where $T_2$ is short
  and few echo pathways survive;
- **CSF-like** ($T_1 = 3700$ ms, $T_2 = 1500$ ms), where $T_2$ is long, many
  pathways survive, and spoiling is hard.

```{code-cell} python
:tags: [hide-input]
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from spoilsim.bloch import ernst, rf_phases, simulate
from spoilsim.style import COLORS, INK, LABELS, line, style, visibility_slider

TR = 10.0
SEED = 0
TISSUES = {"White matter (T1 830, T2 80 ms)": (830.0, 80.0),
           "CSF (T1 3700, T2 1500 ms)": (3700.0, 1500.0)}
SCHEMES = ["quadratic", "random", "none"]
```

## 1. Signal over time

The plot shows $|s_n|$ over the first 1000 TRs (10 s). Quadratic and gradient-only
spoiling both flatten out into a steady state, although gradient-only settles at the
wrong value. Random phases keep fluctuating around the Ernst line for as long
as you look. Zoom into the last few hundred TRs to see it clearly.

```{code-cell} python
:tags: [hide-input]
n_tr = 1000
flips = [5, 10, 15, 20, 30, 45, 60]
n = np.arange(n_tr)
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                    subplot_titles=list(TISSUES))
groups = []
for a in flips:
    g = []
    for row, (T1, T2) in enumerate(TISSUES.values(), start=1):
        for s in SCHEMES:
            sig = simulate(rf_phases(s, n_tr, seed=SEED), a, T1, T2, TR)
            fig.add_trace(line(n, np.abs(sig), s, legendgroup=s, showlegend=row == 1,
                               hovertemplate="TR %{x}<br>|s| = %{y:.4f}<extra>" + LABELS[s] + "</extra>"),
                          row=row, col=1)
            g.append(len(fig.data) - 1)
        fig.add_trace(line(n, np.full(n_tr, ernst(a, T1, TR)), "ernst", legendgroup="ernst",
                           showlegend=row == 1, hovertemplate="Ernst: %{y:.4f}<extra></extra>"),
                      row=row, col=1)
        g.append(len(fig.data) - 1)
    groups.append(g)
visibility_slider(fig, groups, [f"{a}°" for a in flips], "Flip angle α = ", active=3)
fig.update_xaxes(title_text="TR index n", row=2, col=1)
fig.update_yaxes(title_text="|s| (M₀ = 1)", rangemode="tozero")
style(fig, height=640)
```

:::{note} Things to try
- At **α = 5°**, all three schemes are close to each other. Small flip angles
  barely refocus anything.
- For **CSF at α ≥ 15°**, gradient-only spoiling is many times too bright,
  quadratic sits a bit above Ernst, and random swings by tens of percent from
  TR to TR.
:::

## 2. Signal against flip angle

This is the plot behind variable-flip-angle $T_1$ mapping. For each flip angle,
it shows the steady-state signal (quadratic, gradient-only) or the range the
random scheme wanders over (shaded band: 5th–95th percentile of $|s_n|$ over
500 TRs taken after 1000 TRs of preparation; solid line: its mean).

```{code-cell} python
:tags: [hide-input]
flips = np.arange(1, 91, 2)
n_prep, n_keep = 1000, 500
fig = make_subplots(rows=1, cols=2, subplot_titles=list(TISSUES), horizontal_spacing=0.1)
for col, (T1, T2) in enumerate(TISSUES.values(), start=1):
    res = {s: np.array([np.abs(simulate(rf_phases(s, n_prep + n_keep, seed=SEED), a, T1, T2, TR)[n_prep:])
                        for a in flips]) for s in SCHEMES}
    lo, hi = np.percentile(res["random"], [5, 95], axis=1)
    show = col == 1
    fig.add_trace(go.Scatter(x=np.r_[flips, flips[::-1]], y=np.r_[hi, lo[::-1]], fill="toself", mode="lines",
                             fillcolor="rgba(235,104,52,0.22)", line=dict(width=0), hoverinfo="skip",
                             name="Random: 5–95% range", legendgroup="band", showlegend=show), row=1, col=col)
    fig.add_trace(line(flips, res["random"].mean(1), "random", name="Random: mean", legendgroup="random",
                       showlegend=show, hovertemplate="α %{x}°<br>mean |s| %{y:.4f}<extra>Random</extra>"),
                  row=1, col=col)
    for s in ["quadratic", "none"]:
        fig.add_trace(line(flips, res[s][:, -1], s, legendgroup=s, showlegend=show,
                           hovertemplate="α %{x}°<br>|s| %{y:.4f}<extra>" + LABELS[s] + "</extra>"),
                      row=1, col=col)
    fig.add_trace(line(flips, ernst(flips, T1, TR), "ernst", legendgroup="ernst", showlegend=show,
                       hovertemplate="α %{x}°<br>%{y:.4f}<extra>Ernst</extra>"), row=1, col=col)
fig.update_xaxes(title_text="Flip angle α (°)")
fig.update_yaxes(title_text="Steady-state |s| (M₀ = 1)", rangemode="tozero", col=1)
fig.update_yaxes(range=[0, 0.06], col=2)
style(fig, height=480)
```

The CSF panel's y-axis is clipped so the Ernst curve stays readable. The
gradient-only curve keeps climbing off the top (double-click the panel to
autoscale). Note the difference between the orange line and the orange band.
The **mean** of the random scheme tracks Ernst best of all. But a single TR, and
therefore a single k-space line, can land anywhere in the band.

## 3. The knob: choosing $\phi_0$

The quadratic scheme has one free parameter. The plot shows its steady-state
signal *relative to Ernst* for every $\phi_0$ from 0° to 180° in 1° steps
($\phi_0 = 0$ is gradient-only spoiling). The shaded orange band is the random
scheme's 5–95% range for comparison.

- For **white matter** (short $T_2$), most $\phi_0$ values land within ~10% of
  Ernst, apart from sharp **resonances** near simple fractions of 360°
  (0°, 90°, 120°, 180°, …).
- For **CSF** (long $T_2$), the curve is dominated by resonances. Only a few
  values, including the commonly used **117°** and **50°**, come close to 1.
  Even there, moving $\phi_0$ by a degree or two changes the signal
  noticeably. Hover to check.

So the quadratic scheme is *stable* but its *bias* depends on $\phi_0$ and
$T_2$, which is why quantitative methods either calibrate for it or correct it
(Preibisch & Deichmann, 2009).

```{code-cell} python
:tags: [hide-input]
phi0s = np.arange(0, 181, 1.0)
flips = [10, 20, 30]
n_prep, n_keep = 1500, 300
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, subplot_titles=list(TISSUES))
groups = []
for a in flips:
    g = []
    for row, (T1, T2) in enumerate(TISSUES.values(), start=1):
        E = ernst(a, T1, TR)
        q = np.array([np.abs(simulate(rf_phases("quadratic", n_prep, phi0_deg=p), a, T1, T2, TR)[-50:]).mean()
                      for p in phi0s]) / E
        r = np.abs(simulate(rf_phases("random", n_prep + n_keep, seed=SEED), a, T1, T2, TR)[n_prep:]) / E
        lo, hi = np.percentile(r, [5, 95])
        fig.add_trace(go.Scatter(x=[0, 180, 180, 0], y=[lo, lo, hi, hi], fill="toself", mode="lines",
                                 fillcolor="rgba(235,104,52,0.22)", line=dict(width=0), hoverinfo="skip",
                                 name="Random: 5–95% range", legendgroup="band", showlegend=row == 1),
                      row=row, col=1)
        g.append(len(fig.data) - 1)
        fig.add_trace(line(phi0s, q, "quadratic", name="Quadratic, steady state", legendgroup="q",
                           showlegend=row == 1,
                           hovertemplate="φ₀ = %{x}°<br>S / S_Ernst = %{y:.3f}<extra></extra>"), row=row, col=1)
        g.append(len(fig.data) - 1)
    groups.append(g)
for row in (1, 2):
    fig.add_hline(y=1, line=dict(color=COLORS["ernst"], dash="dash", width=1.5), row=row, col=1)
    for p in (50, 117):
        fig.add_vline(x=p, line=dict(color=INK, dash="dot", width=1), row=row, col=1)
fig.add_annotation(x=50, y=1, yref="paper", text="50°", showarrow=False, yshift=8, font=dict(color=INK))
fig.add_annotation(x=117, y=1, yref="paper", text="117°", showarrow=False, yshift=8, font=dict(color=INK))
visibility_slider(fig, groups, [f"{a}°" for a in flips], "Flip angle α = ", active=2)
fig.update_yaxes(type="log", title_text="S / S_Ernst", tickvals=[0.5, 0.7, 1, 1.5, 2, 3, 5, 10, 20])
fig.update_xaxes(title_text="φ₀ (°)", row=2, col=1, dtick=15)
style(fig, height=640)
```

:::{important} What this page shows
The quadratic scheme trades a **small, deterministic, $T_2$-dependent bias**
for a **perfectly stable signal**. The random scheme has **no bias on
average** but **large TR-to-TR variation**. For a single-voxel measurement that
you could average over many TRs, random would be fine. An image is different:
every TR gets its own k-space line, as the [next page](image.md) shows.
:::
