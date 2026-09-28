---
title: A few spins
kernelspec:
  name: python3
  display_name: Python 3
---

This page follows a single voxel: the RF phase schedule, a subset of the
isochromats it contains, and their sum (the measured signal).

```{code-cell} python
:tags: [hide-input]
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from spoilsim.bloch import ernst, rf_phases, simulate
from spoilsim.style import COLORS, INK, LABELS, line, style, visibility_slider

TR = 10.0
SEED = 0
```

## 1. The phase schedules

The top panel shows the RF phase itself (mod 360°). Both schemes look like a
random scatter of points. Even the first difference $\Delta\phi_n = n\phi_0$
wraps around so often that it looks irregular. The hidden structure only shows
up in the **second difference**
$\Delta^2\phi_n = \Delta\phi_n - \Delta\phi_{n-1}$ (bottom). For the quadratic
scheme it is exactly $\phi_0 = 117^\circ$ every TR, a flat line. For the random
scheme it is just noise. That constant second difference is the symmetry the
[theory page](theory.md) uses.

```{code-cell} python
:tags: [hide-input]
n_show = 60
n = np.arange(n_show)
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                    subplot_titles=("RF phase φₙ (mod 360°)", "Second difference Δ²φₙ = Δφₙ − Δφₙ₋₁ (mod 360°)"))
for scheme in ["quadratic", "random"]:
    phi = np.rad2deg(rf_phases(scheme, n_show, seed=SEED))
    d2phi = np.mod(np.diff(phi, n=2, prepend=[0.0, 0.0]), 360)
    for row, y in [(1, np.mod(phi, 360)), (2, d2phi)]:
        fig.add_trace(go.Scatter(
            x=n, y=y, mode="lines+markers", name=LABELS[scheme], legendgroup=scheme,
            showlegend=row == 1, line=dict(color=COLORS[scheme], width=1),
            marker=dict(size=8, color=COLORS[scheme], line=dict(color="#fcfcfb", width=1)),
            hovertemplate="TR %{x}<br>%{y:.1f}°<extra>" + LABELS[scheme] + "</extra>"),
            row=row, col=1)
fig.update_yaxes(range=[0, 360], tickvals=[0, 90, 180, 270, 360], ticksuffix="°")
fig.update_xaxes(title_text="TR index n", row=2, col=1)
style(fig, height=520)
```

## 2. The isochromats inside one voxel

The voxel is modelled as a set of isochromats, each dephased by a different
amount by the spoiler gradient. Below, 15 of them are drawn as gray arrows (the faint line joins the tips of all 120) in
the receiver frame just after each RF pulse. The **colored arrow is the voxel
signal** (the average over *all* isochromats), magnified ×5 so it's visible.

The figure opens at TR 60, after most of the transient. Press ▶ or drag the slider (back to 0 to watch the transient; the first few TRs are clipped):

- **Quadratic:** after the first few dozen TRs, the faint closed curve traced by
  *all* isochromat tips stops changing. Every TR, each isochromat just slides
  along that curve to the position its neighbour 117° away had (the shift by
  $\phi_0$ from the previous page). The colored arrow, which is the average over
  the curve, stops moving.
- **Random:** the curve itself changes shape every TR, and the colored arrow
  keeps jumping around.

```{code-cell} python
:tags: [hide-input]
T1, T2, alpha = 1000.0, 100.0, 30.0
n_iso, n_tr, stride, gain = 120, 150, 8, 5.0  # 360/120 = 3°, so 117° = 39 slots exactly
sims = {s: simulate(rf_phases(s, n_tr, seed=SEED), alpha, T1, T2, TR,
                    n_iso=n_iso, return_iso=True) for s in ["quadratic", "random"]}

def arrows(z):
    x = np.column_stack([np.zeros_like(z.real), z.real, np.full(z.shape, np.nan)]).ravel()
    y = np.column_stack([np.zeros_like(z.imag), z.imag, np.full(z.shape, np.nan)]).ravel()
    return x, y

def traces(k):
    out = []
    for s in ["quadratic", "random"]:
        sig, iso = sims[s]
        ring = np.append(iso[k], iso[k, 0])
        out.append(go.Scatter(x=ring.real, y=ring.imag, mode="lines", line=dict(color="#c9c7c1", width=1),
                              hoverinfo="skip", showlegend=False))
        x, y = arrows(iso[k, ::stride])
        out.append(go.Scatter(x=x, y=y, mode="lines+markers", line=dict(color="#9a9893", width=1.5),
                              marker=dict(size=5, color="#9a9893"), hoverinfo="skip", showlegend=False))
        x, y = arrows(np.array([gain * sig[k]]))
        out.append(go.Scatter(x=x, y=y, mode="lines+markers", line=dict(color=COLORS[s], width=4),
                              marker=dict(size=9, color=COLORS[s]), showlegend=False,
                              hovertemplate=f"voxel signal ×{gain:g}<br>Re %{{x:.3f}}, Im %{{y:.3f}}<extra></extra>"))
    return out

fig = make_subplots(rows=1, cols=2, subplot_titles=(LABELS["quadratic"], LABELS["random"]),
                    horizontal_spacing=0.08)
k0 = 60  # open on a frame past the transient; drag back to 0 to see it
for i, tr in enumerate(traces(k0)):
    fig.add_trace(tr, row=1, col=1 + i // 3)
fig.frames = [go.Frame(data=traces(k), name=str(k), traces=list(range(6))) for k in range(n_tr)]
lim = 0.32  # early TRs (larger transverse magnetization) are clipped
fig.update_xaxes(range=[-lim, lim], title_text="Mx (receiver frame)")
fig.update_yaxes(range=[-lim, lim], scaleanchor="x", title_text="My")
fig.update_yaxes(scaleanchor="x2", row=1, col=2)
fig.update_layout(
    updatemenus=[dict(type="buttons", x=0, y=-0.18, xanchor="left", direction="left", buttons=[
        dict(label="▶ Play", method="animate",
             args=[None, dict(frame=dict(duration=120, redraw=False), fromcurrent=True, transition=dict(duration=0))]),
        dict(label="❚❚ Pause", method="animate",
             args=[[None], dict(mode="immediate", frame=dict(duration=0, redraw=False))])])],
    sliders=[dict(active=k0, x=0.18, len=0.82, y=-0.12, currentvalue=dict(prefix="TR n = ", xanchor="right"),
                  steps=[dict(label=str(k), method="animate",
                              args=[[str(k)], dict(mode="immediate", frame=dict(duration=0, redraw=False))])
                         for k in range(n_tr)])])
style(fig, height=520)
fig.update_layout(margin=dict(b=120))
```

## 3. The voxel signal in the complex plane

The next figure plots every TR's voxel signal $s_n$ as a point in the complex
plane (receiver frame), for the first 400 TRs. The black ✕ marks the ideal
Ernst value.

- **Quadratic** spirals in and **stops at one point**. That point is the steady
  state. It sits near the ✕ but not exactly on it.
- **Random** never converges. The points form a **cloud centred on the ✕**:
  correct on average, different every TR.

Use the slider to change the flip angle. Larger flip angles couple more echo
pathways, and the random cloud grows.

```{code-cell} python
:tags: [hide-input]
T1, T2, n_tr = 1000.0, 100.0, 400
flips = [5, 10, 15, 20, 30, 45, 60]
fig = make_subplots(rows=1, cols=2, subplot_titles=(LABELS["quadratic"], LABELS["random"]),
                    horizontal_spacing=0.1)
groups = []
for a in flips:
    g = []
    for col, s in enumerate(["quadratic", "random"], start=1):
        sig = simulate(rf_phases(s, n_tr, seed=SEED), a, T1, T2, TR)
        fig.add_trace(go.Scatter(
            x=sig.real, y=sig.imag, mode="lines+markers", showlegend=False,
            line=dict(color=COLORS[s], width=1), marker=dict(size=5, color=COLORS[s]),
            customdata=np.arange(n_tr),
            hovertemplate="TR %{customdata}<br>Re %{x:.4f}<br>Im %{y:.4f}<extra></extra>"), row=1, col=col)
        g.append(len(fig.data) - 1)
        fig.add_trace(go.Scatter(
            x=[0], y=[ernst(a, T1, TR)], mode="markers", showlegend=False,
            marker=dict(symbol="x-thin", size=11, line=dict(width=2, color=COLORS["ernst"])),
            hovertemplate="Ernst: %{y:.4f}<extra></extra>"), row=1, col=col)
        g.append(len(fig.data) - 1)
    groups.append(g)
visibility_slider(fig, groups, [f"{a}°" for a in flips], "Flip angle α = ", active=4)
fig.update_xaxes(title_text="Re s")
fig.update_yaxes(title_text="Im s")
style(fig, height=500)
```

:::{admonition} What the transient hides
:class: note
The first ~50 points of the quadratic curve (the spiral) are the approach to
steady state. They are not converging onto a single fixed isochromat pattern.
The pattern keeps shifting by $\phi_0$ every TR, but, as derived on the
[theory page](theory.md), its *average* stops changing.
:::
