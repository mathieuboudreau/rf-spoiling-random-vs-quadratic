"""Shared Plotly styling: fixed colors per scheme, recessive axes."""

import plotly.graph_objects as go

# Categorical slots (validated reference palette, light mode), fixed per scheme.
COLORS = {
    "quadratic": "#2a78d6",  # blue
    "random": "#eb6834",  # orange
    "none": "#1baf7a",  # aqua
    "ernst": "#0b0b0b",  # neutral ink, dashed
}
LABELS = {
    "quadratic": "Quadratic (φ₀ = 117°)",
    "random": "Random phase",
    "none": "Gradient spoiling only",
    "ernst": "Ideal (Ernst equation)",
}
INK = "#52514e"
GRID = "#e6e5e1"
# Diverging blue <-> neutral <-> red for difference maps.
DIVERGING = [[0.0, "#1c5cab"], [0.25, "#6da7ec"], [0.5, "#f0efec"],
             [0.75, "#ee8a88"], [1.0, "#b52c2c"]]


def style(fig, height=420):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=60, r=20, t=100, b=50),
        font=dict(family="Inter, Helvetica, Arial, sans-serif", size=13, color="#0b0b0b"),
        hoverlabel=dict(font_size=12),
        legend=dict(orientation="h", yref="container", y=0.99, yanchor="top", xanchor="left", x=0),
        paper_bgcolor="#fcfcfb",
        plot_bgcolor="#fcfcfb",
    )
    if fig.layout.sliders:
        fig.update_layout(margin=dict(b=130))
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=INK, ticks="outside")
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=INK, ticks="outside")
    return fig


def line(x, y, scheme, name=None, **kw):
    dash = "dash" if scheme == "ernst" else None
    return go.Scatter(x=x, y=y, mode="lines", name=name or LABELS[scheme],
                      line=dict(color=COLORS[scheme], width=2, dash=dash), **kw)


def visibility_slider(fig, groups, labels, prefix, active=0):
    """Slider that shows one trace group at a time.

    groups: list of lists of trace indices; traces not in any group stay visible.
    """
    n = len(fig.data)
    grouped = {i for g in groups for i in g}
    steps = []
    for g, lab in zip(groups, labels):
        vis = [(i in g) or (i not in grouped) for i in range(n)]
        steps.append(dict(method="update", args=[{"visible": vis}], label=lab))
    for i in range(n):
        fig.data[i].visible = (i in groups[active]) or (i not in grouped)
    fig.update_layout(margin=dict(b=130), sliders=[dict(active=active, steps=steps, pad=dict(t=60),
                                    currentvalue=dict(prefix=prefix))])
    return fig
