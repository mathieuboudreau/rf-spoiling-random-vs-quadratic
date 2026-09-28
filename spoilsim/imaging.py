"""Build SPGR images: one phase-encode (ky) line per TR, linear ordering."""

import numpy as np

from .bloch import rf_phases, simulate


def _fft2c(img):
    return np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(img)))


def _ifft2c(k):
    return np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(k)))


def synthesize_image(phantom, signals):
    """Complex image when tissue ``t`` contributes ``signals[t][i]`` to ky line i.

    ``signals[t]`` has one complex value per ky line (acquisition order =
    row order, from -ky_max to +ky_max). Signal is constant along a line
    (readout), so each line of each tissue's k-space is simply scaled.
    """
    k = np.zeros((phantom.n, phantom.n), dtype=complex)
    for name in phantom.tissues:
        k += signals[name][:, None] * _fft2c(phantom.masks[name])
    return _ifft2c(k)


def tissue_signals(phantom, scheme, alpha_deg, TR, n_dummy=100, phi0_deg=117.0,
                   seed=None, n_iso=None):
    """Per-tissue complex signal for each acquired ky line (after dummy TRs).

    scheme "ideal" = perfect spoiling (transverse magnetization destroyed every
    TR), including the same approach-to-steady-state as the real schemes.
    """
    ideal = scheme == "ideal"
    phases = rf_phases("none" if ideal else scheme, n_dummy + phantom.n,
                       phi0_deg=phi0_deg, seed=seed)
    out = {}
    for name, (T1, T2, PD) in phantom.tissues.items():
        s = simulate(phases, alpha_deg, T1, 1e-6 if ideal else T2, TR,
                     n_iso=1 if ideal else n_iso, M0=PD)
        out[name] = s[n_dummy:]
    return out
