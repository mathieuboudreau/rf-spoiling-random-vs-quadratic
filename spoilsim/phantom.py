"""Toy brain phantom built from Shepp-Logan-style ellipses, one mask per tissue."""

from dataclasses import dataclass

import numpy as np

# name: (T1 ms, T2 ms, proton density) -- rough 3 T values
TISSUES = {
    "fat": (380.0, 110.0, 0.9),
    "white matter": (830.0, 80.0, 0.7),
    "grey matter": (1330.0, 110.0, 0.8),
    "CSF": (3700.0, 1500.0, 1.0),
    "lesion": (1600.0, 250.0, 0.9),
}

# (tissue, x0, y0, a, b, angle_deg); later ellipses overwrite earlier ones
ELLIPSES = [
    ("fat", 0.0, 0.0, 0.69, 0.92, 0),
    ("grey matter", 0.0, -0.0184, 0.6624, 0.874, 0),
    ("white matter", 0.0, -0.0184, 0.60, 0.80, 0),
    ("CSF", 0.22, 0.0, 0.11, 0.31, -18),
    ("CSF", -0.22, 0.0, 0.16, 0.41, 18),
    ("grey matter", 0.0, 0.35, 0.21, 0.25, 0),
    ("lesion", 0.0, 0.1, 0.046, 0.046, 0),
    ("lesion", 0.0, -0.1, 0.046, 0.046, 0),
    ("lesion", -0.08, -0.605, 0.046, 0.023, 0),
    ("lesion", 0.06, -0.605, 0.023, 0.046, 0),
]


@dataclass
class Phantom:
    n: int
    tissues: dict  # name -> (T1, T2, PD)
    masks: dict  # name -> float array (n, n), 0/1


def make_phantom(n=128):
    y, x = np.mgrid[1:-1:n * 1j, -1:1:n * 1j]  # row 0 at the top (y = +1)
    label = np.full((n, n), "", dtype=object)
    for name, x0, y0, a, b, ang in ELLIPSES:
        t = np.deg2rad(ang)
        xr = (x - x0) * np.cos(t) + (y - y0) * np.sin(t)
        yr = -(x - x0) * np.sin(t) + (y - y0) * np.cos(t)
        label[(xr / a) ** 2 + (yr / b) ** 2 <= 1] = name
    masks = {name: (label == name).astype(float) for name in TISSUES}
    return Phantom(n=n, tissues=dict(TISSUES), masks=masks)
