# RF spoiling: why not just use random phases?

An interactive MyST book (Plotly figures) comparing quadratic RF phase cycling,
φₙ = φ₀·n(n+1)/2, with random RF phases in spoiled gradient echo (SPGR),
from a few isochromats up to a full image.

```bash
pip install -r requirements.txt
pytest -q                      # simulator tests
myst start --execute           # live preview at http://localhost:3000
myst build --html --execute    # static site in _build/html (works offline)
```

- `spoilsim/`: isochromat Bloch simulator, phantom, k-space synthesis, plot style
- `*.md`: book pages (`index`, `theory`, `few-spins`, `steady-state`, `image`, `takeaways`)
