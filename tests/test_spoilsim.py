import numpy as np

from spoilsim.bloch import ernst, rf_phases, simulate
from spoilsim.imaging import synthesize_image
from spoilsim.phantom import make_phantom

T1, T2, TR = 1000.0, 80.0, 10.0


def test_quadratic_phase_schedule():
    phi = rf_phases("quadratic", 5, phi0_deg=117.0)
    expected = np.deg2rad(117.0) * np.array([0, 1, 3, 6, 10])
    np.testing.assert_allclose(phi, expected)


def test_random_schedule_is_seeded():
    a = rf_phases("random", 50, seed=3)
    b = rf_phases("random", 50, seed=3)
    c = rf_phases("random", 50, seed=4)
    np.testing.assert_allclose(a, b)
    assert not np.allclose(a, c)


def test_ideal_spoiling_matches_ernst():
    # Tiny T2: transverse magnetization dies within one TR -> perfect spoiling.
    s = simulate(np.zeros(400), 15.0, T1, 1e-3, TR)
    np.testing.assert_allclose(abs(s[-1]), ernst(15.0, T1, TR), rtol=1e-3)


def test_quadratic_reaches_steady_state_near_ernst():
    s = simulate(rf_phases("quadratic", 600), 15.0, T1, T2, TR)
    tail = s[-100:]
    assert np.std(abs(tail)) / np.mean(abs(tail)) < 1e-3
    np.testing.assert_allclose(np.mean(abs(tail)), ernst(15.0, T1, TR), rtol=0.1)


def test_random_never_settles():
    s = simulate(rf_phases("random", 600, seed=0), 15.0, T1, T2, TR)
    tail = s[-100:]
    assert np.std(abs(tail)) / np.mean(abs(tail)) > 0.02


def test_constant_signal_reconstructs_phantom():
    ph = make_phantom(64)
    signals = {name: np.full(64, 1.0 + 0j) for name in ph.tissues}
    img = synthesize_image(ph, signals)
    truth = sum(ph.masks[name] for name in ph.tissues)
    np.testing.assert_allclose(abs(img), truth, atol=1e-10)
