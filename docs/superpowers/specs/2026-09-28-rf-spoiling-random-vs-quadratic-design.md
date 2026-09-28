# RF spoiling: quadratic vs random phase — interactive MyST book

## Goal
Answer a student's in-class question: *"Why use the quadratic phase increment
φₙ = φ₀·n(n+1)/2 instead of a random number generator?"* with an interactive
MyST book (static HTML, Plotly figures) usable offline in class.

## Core message
Random RF phases do destroy coherent transverse magnetization *on average*, but
the magnetization never reaches a steady state: the demodulated signal
fluctuates TR-to-TR. In an image, one k-space line per TR, those fluctuations
modulate k-space and appear as ghosting / structured noise, and they differ
from scan to scan (seed). Quadratic phase cycling produces a true, reproducible
steady state (constant signal after the transient), which for φ₀ ≈ 117° is
close to the ideal Ernst signal.

## Decisions (user delegated: "I'll leave it to you")
- Interactivity: precomputed Plotly figures with sliders/dropdowns; fully
  static HTML (`myst build --html --execute`). No live kernel.
- Audience: grad students who know Bloch equations and k-space.
- Physics: isochromat Bloch simulation, N isochromats uniformly dephased over
  2π per TR by the spoiler gradient; instantaneous RF about axis at phase φₙ;
  relaxation + precession over TR; signal read right after RF (TE→0),
  demodulated by the receiver phase φₙ.
- Schemes compared: quadratic (φ₀ = 117° default), random uniform phases
  (several seeds), gradient spoiling only (φ = 0), ideal (Ernst equation).
- Image: in-house ellipse phantom (no scikit-image), a few tissues with T1/T2,
  128×128, linear phase-encode ordering, one ky line per TR after dummy scans;
  image per scheme = Σ_tissues s_t(line) · FFT(mask_t).

## Structure
- `spoilsim/` Python package: `bloch.py` (phase schedules, simulator, Ernst),
  `phantom.py` (tissue masks + parameters), `imaging.py` (k-space synthesis),
  `style.py` (colors/plot defaults).
- `tests/` pytest: Ernst limit reached with ideal spoiling, quadratic reaches
  steady state, random does not, image recon of constant signal = phantom.
- Book pages: `index.md` (question + short answer), `theory.md`,
  `few-spins.md`, `steady-state.md`, `image.md`, `takeaways.md`.

## Colors
Categorical slots from the dataviz reference palette: quadratic = blue,
random = orange, gradient-only = aqua; Ernst = dashed neutral ink. Images in
grayscale; difference maps diverging blue↔red with neutral midpoint.
