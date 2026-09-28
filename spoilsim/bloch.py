"""Isochromat Bloch simulation of a spoiled gradient-echo (SPGR) sequence.

Model
-----
A voxel is represented by ``n_iso`` isochromats. The spoiler gradient gives
isochromat k an extra precession angle ``2*pi*k/n_iso`` every TR, i.e. exactly
one full cycle of dephasing across the voxel per TR.

Each TR:
  1. instantaneous RF pulse of flip angle alpha about an axis in the xy-plane
     at angle phi_n (the RF phase),
  2. the signal is read immediately (TE -> 0) and demodulated by the receiver,
     whose phase follows the RF phase: s_n = mean(Mxy) * exp(-i phi_n),
  3. T1/T2 relaxation and gradient-induced precession over one TR.
"""

import numpy as np


def rf_phases(scheme, n_tr, phi0_deg=117.0, seed=None):
    """RF phase (radians) for each of ``n_tr`` excitations.

    scheme: "quadratic" -> phi_n = phi0 * n(n+1)/2
            "random"    -> phi_n ~ Uniform[0, 2pi), independent every TR
            "none"      -> phi_n = 0 (gradient spoiling only)
    """
    n = np.arange(n_tr)
    if scheme == "quadratic":
        return np.deg2rad(phi0_deg) * n * (n + 1) / 2
    if scheme == "random":
        return np.random.default_rng(seed).uniform(0, 2 * np.pi, n_tr)
    if scheme == "none":
        return np.zeros(n_tr)
    raise ValueError(f"unknown scheme {scheme!r}")


def ernst(alpha_deg, T1, TR, M0=1.0):
    """Ideal spoiled-GRE signal (perfect spoiling of transverse magnetization)."""
    a = np.deg2rad(alpha_deg)
    E1 = np.exp(-TR / T1)
    return M0 * np.sin(a) * (1 - E1) / (1 - E1 * np.cos(a))


def default_n_iso(T2, TR):
    """Enough isochromats that the discrete dephasing pattern (periodic in
    n_iso TRs) cannot produce a spurious echo: E2**n_iso < 1e-4."""
    return int(max(100, np.ceil(9.3 * T2 / TR)))


def simulate(phases, alpha_deg, T1, T2, TR, n_iso=None, M0=1.0, return_iso=False):
    """Run the SPGR sequence for the given RF phase schedule.

    Returns the complex demodulated voxel signal for every TR (length
    ``len(phases)``). With ``return_iso=True`` also returns the demodulated
    transverse magnetization of every isochromat, shape (n_tr, n_iso).
    """
    if n_iso is None:
        n_iso = default_n_iso(T2, TR)
    a = np.deg2rad(alpha_deg)
    ca, sa = np.cos(a), np.sin(a)
    E1, E2 = np.exp(-TR / T1), np.exp(-TR / T2)
    precess = E2 * np.exp(1j * 2 * np.pi * np.arange(n_iso) / n_iso)

    mxy = np.zeros(n_iso, dtype=complex)
    mz = np.full(n_iso, M0, dtype=float)
    signal = np.empty(len(phases), dtype=complex)
    iso = np.empty((len(phases), n_iso), dtype=complex) if return_iso else None

    for n, phi in enumerate(phases):
        # RF: go to the frame where the RF axis is x, rotate about x, come back.
        rot = np.exp(-1j * phi)
        m = mxy * rot
        mx, my = m.real, m.imag
        my_new = my * ca + mz * sa
        mz = -my * sa + mz * ca
        m = mx + 1j * my_new  # demodulated (receiver frame) magnetization
        signal[n] = m.mean()
        if return_iso:
            iso[n] = m
        mxy = m / rot
        # Free precession + relaxation over one TR.
        mxy = mxy * precess
        mz = M0 + (mz - M0) * E1
    return (signal, iso) if return_iso else signal
