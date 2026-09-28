---
title: A full image
kernelspec:
  name: python3
  display_name: Python 3
---

In a 2D Cartesian SPGR acquisition, **one phase-encoding line of k-space is
acquired per TR**. If the signal changes from TR to TR, each k-space line is
scaled by a different complex factor. That is a *modulation of k-space* along
$k_y$, and in the image it becomes blurring, ghosting, and noise-like streaks
along the **phase-encode direction** (vertical here).

The phantom is a Shepp–Logan-style head with five tissues. Each tissue is
simulated with its own $T_1$/$T_2$ and all tissues see the *same* RF phase
schedule (it's one scan). Lines are acquired in linear order from $-k_{y,\max}$ to
$+k_{y,\max}$ after a number of dummy TRs.

```{code-cell} python
:tags: [hide-input]
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from spoilsim.imaging import synthesize_image, tissue_signals
from spoilsim.phantom import make_phantom
from spoilsim.style import COLORS, DIVERGING, INK, LABELS, line, style, visibility_slider

TR = 10.0
N = 128
ph = make_phantom(N)
background = sum(ph.masks.values()) == 0
```

```{code-cell} python
:tags: [hide-input]
import pandas as pd  # only for a tidy table
pd.DataFrame([(k, *v) for k, v in ph.tissues.items()],
             columns=["tissue", "T1 (ms)", "T2 (ms)", "proton density"]).set_index("tissue")
```

## 1. What k-space "sees"

Each point is the signal (per tissue) that scales one $k_y$ line, acquired in
steady state (after 1000 dummy TRs). The quadratic scheme gives a **flat line**:
every $k_y$ is weighted equally, just like the ideal case, so the image is
clean. Only the overall tissue brightness can be slightly off, plus a constant
phase offset that doesn't show in a magnitude image. The random
scheme gives a **jagged, random weighting** in both magnitude and phase.

```{code-cell} python
:tags: [hide-input]
flips = [5, 15, 30, 60]
N_DUMMY = 1000
ky = np.arange(N) - N // 2
sigs = {a: {s: tissue_signals(ph, s, a, TR, n_dummy=N_DUMMY, seed=0)
            for s in ["ideal", "quadratic", "random"]} for a in flips}
show_tissues = ["white matter", "CSF"]
fig = make_subplots(rows=2, cols=2, shared_xaxes=True, vertical_spacing=0.1, horizontal_spacing=0.1,
                    subplot_titles=[f"{t}: |s|" for t in show_tissues] + [f"{t}: phase of s" for t in show_tissues])
names = {"ideal": "ernst", "quadratic": "quadratic", "random": "random"}
groups = []
for a in flips:
    g = []
    for col, t in enumerate(show_tissues, start=1):
        for s in ["random", "quadratic", "ideal"]:
            z = sigs[a][s][t]
            for row, y, unit in [(1, np.abs(z), ""), (2, np.rad2deg(np.angle(z)), "°")]:
                fig.add_trace(line(ky, y, names[s], name=LABELS[names[s]].replace("Ernst equation", "perfect spoiling"),
                                   legendgroup=s, showlegend=(row == 1 and col == 1),
                                   hovertemplate="ky %{x}<br>%{y:.4g}" + unit + "<extra>" + s + "</extra>"),
                              row=row, col=col)
                g.append(len(fig.data) - 1)
    groups.append(g)
visibility_slider(fig, groups, [f"{a}°" for a in flips], "Flip angle α = ", active=2)
fig.update_yaxes(rangemode="tozero", row=1)
fig.update_yaxes(title_text="|s|", row=1, col=1)
fig.update_yaxes(title_text="phase (°)", row=2, col=1)
fig.update_xaxes(title_text="k_y line (acquisition order)", row=2)
style(fig, height=620)
```

## 2. The images

- **Top row:** magnitude images, each on the same gray scale as the
  perfect-spoiling reference.
- **Bottom row:** difference from the perfect-spoiling reference, in % of the
  reference's maximum.

Two different random seeds are shown to make a second point: random spoiling is
**not reproducible** unless the seed is fixed, because each scan gets a
different artifact pattern.

Look at the **background** in the difference maps. The quadratic scheme's error
stays *inside* the tissues it affects (mostly CSF, the long-$T_2$ bias from the
previous page), so it's a contrast error. The random scheme's error is smeared
**vertically across the whole field of view**, background included. That is
ghosting.

```{code-cell} python
:tags: [hide-input]
cols = [("ideal", None, "Perfect spoiling"), ("quadratic", None, "Quadratic 117°"),
        ("random", 0, "Random, seed 0"), ("random", 1, "Random, seed 1")]
DMAX = 20  # % colour range of the difference maps
fig = make_subplots(rows=2, cols=4, horizontal_spacing=0.015, vertical_spacing=0.06,
                    subplot_titles=[c[2] for c in cols] + ["", "Quadratic − perfect", "Random (0) − perfect",
                                                           "Random (1) − perfect"])
groups, stats = [], {}
for a in flips:
    g = []
    ref = np.abs(synthesize_image(ph, sigs[a]["ideal"]))
    scale = ref.max()
    for c, (s, seed, title) in enumerate(cols, start=1):
        sig = sigs[a][s] if seed in (None, 0) else tissue_signals(ph, s, a, TR, n_dummy=N_DUMMY, seed=seed)
        img = np.abs(synthesize_image(ph, sig)) / scale
        fig.add_trace(go.Heatmap(z=img.astype(np.float32), colorscale="gray", zmin=0, zmax=1, showscale=False,
                                 hovertemplate="x %{x}, y %{y}<br>%{z:.3f}<extra>" + title + "</extra>"),
                      row=1, col=c)
        g.append(len(fig.data) - 1)
        if c > 1:
            d = 100 * (img - ref / scale)
            stats[(a, title)] = (np.sqrt(np.mean(d[background] ** 2)), np.sqrt(np.mean(d[~background] ** 2)))
            fig.add_trace(go.Heatmap(z=d.astype(np.float32), colorscale=DIVERGING, zmin=-DMAX, zmax=DMAX,
                                     showscale=(c == 4), colorbar=dict(title="%", len=0.45, y=0.22, thickness=12),
                                     hovertemplate="x %{x}, y %{y}<br>%{z:.1f}%<extra>" + title + "</extra>"),
                          row=2, col=c)
            g.append(len(fig.data) - 1)
    groups.append(g)
visibility_slider(fig, groups, [f"{a}°" for a in flips], "Flip angle α = ", active=2)
fig.update_xaxes(visible=False)
fig.update_yaxes(visible=False, autorange="reversed", scaleanchor="x", constrain="domain")
for i in range(2, 9):
    fig.update_yaxes(scaleanchor=f"x{i}", row=(i - 1) // 4 + 1, col=(i - 1) % 4 + 1)
style(fig, height=560)
fig.update_layout(margin=dict(l=10, r=10, t=40, b=20))
```

Here are the same results as numbers: root-mean-square difference from the
perfect-spoiling image, in % of its maximum, split into *background* (where
there should be nothing, so any error is a ghost) and *object*.

```{code-cell} python
:tags: [hide-input]
pd.DataFrame([(f"{a}°", t, bg, obj) for (a, t), (bg, obj) in stats.items()],
             columns=["flip angle", "scheme", "background RMS error (%)", "object RMS error (%)"]
             ).round(2).set_index(["flip angle", "scheme"])
```

## 3. Can you wait it out?

A natural follow-up: *"maybe random just needs more dummy scans?"* No. The
random scheme never reaches a steady state, so its ghosting stays roughly
constant. The quadratic scheme's ghosting (the transient of the long-$T_1$ CSF
modulating k-space) disappears once the steady state is reached. The plot
shows background (ghost) error against the number of dummy TRs at α = 30°. The
random scheme is shown as mean ± range over 5 seeds.

```{code-cell} python
:tags: [hide-input]
a = 30
dummies = [0, 25, 50, 100, 200, 300, 500, 750, 1000, 1500]
seeds = range(5)

def bg_err(n_dummy, s, seed=None):
    ref = np.abs(synthesize_image(ph, tissue_signals(ph, "ideal", a, TR, n_dummy=n_dummy)))
    img = np.abs(synthesize_image(ph, tissue_signals(ph, s, a, TR, n_dummy=n_dummy, seed=seed)))
    d = 100 * (img - ref) / ref.max()
    return np.sqrt(np.mean(d[background] ** 2))

q = [bg_err(d, "quadratic") for d in dummies]
r = np.array([[bg_err(d, "random", sd) for sd in seeds] for d in dummies])
fig = go.Figure()
fig.add_trace(go.Scatter(x=dummies + dummies[::-1], y=np.r_[r.max(1), r.min(1)[::-1]], fill="toself", mode="lines",
                         fillcolor="rgba(235,104,52,0.22)", line=dict(width=0), hoverinfo="skip",
                         name="Random: range over 5 seeds"))
fig.add_trace(go.Scatter(x=dummies, y=r.mean(1), mode="lines+markers", name="Random: mean over 5 seeds",
                         line=dict(color=COLORS["random"], width=2), marker=dict(size=8),
                         hovertemplate="%{x} dummies<br>%{y:.2f}%<extra></extra>"))
fig.add_trace(go.Scatter(x=dummies, y=q, mode="lines+markers", name=LABELS["quadratic"],
                         line=dict(color=COLORS["quadratic"], width=2), marker=dict(size=8),
                         hovertemplate="%{x} dummies<br>%{y:.2f}%<extra></extra>"))
fig.update_xaxes(title_text="Number of dummy TRs before the first k-space line (TR = 10 ms)")
fig.update_yaxes(title_text="Background RMS error (% of max)", rangemode="tozero")
style(fig, height=440)
```
