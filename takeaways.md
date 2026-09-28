---
title: Takeaways
---

## Answer to the student

| | Quadratic $\phi_n = \phi_0\,n(n+1)/2$ | Random $\phi_n$ |
|---|---|---|
| Destroys coherent transverse magnetization? | Mostly (depends on $\phi_0$) | Yes, on average |
| Reaches a steady state? | **Yes.** Exactly the same signal every TR | **No.** Fluctuates every TR |
| Bias against Ernst | Small, deterministic, $T_2$-dependent, correctable | None on average |
| TR-to-TR variation | Zero | Large (grows with $T_2$/TR and flip angle) |
| Image artifacts | None in steady state (contrast bias only) | Ghosting / noise-like streaks along phase-encode |
| Helped by more dummy scans? | Yes, until steady state | No |
| Reproducible between scans? | Yes | Only if the seed is fixed |

The quadratic formula isn't just *one way* to scramble phases. It is built
so that each TR is a **shifted copy of the previous one** across the voxel's
dephasing distribution. That symmetry is what produces a steady state. A
random sequence scrambles phases just as well, but it has no such symmetry, so
the signal never settles, and in imaging, an unsettled signal means corrupted
k-space.

## Discussion questions for class

1. On the [φ₀ plot](steady-state.md), why is $\phi_0 = 0$ identical to
   gradient-only spoiling? What about a *linear* phase schedule,
   $\phi_n = n\phi_0$? *(Hint: a constant $\Delta\phi$ is just a relabelling of
   the isochromats.)*
2. The random scheme is unbiased on average. Suggest an acquisition where that
   would actually be an advantage. *(Hint: think about what happens if you
   average many repetitions, or acquire a non-imaging, single-voxel signal
   over many TRs.)*
3. Why does the random scheme's TR-to-TR variation grow with $T_2$ and flip
   angle?
4. The quadratic scheme's residual bias depends on $T_2$. How would that affect
   variable-flip-angle $T_1$ mapping, and how could you correct for it?
5. In the image, why are the artifacts spread along the phase-encode direction
   only, and not the readout direction?

## Reproducing and extending

The simulation code is in `spoilsim/` (≈150 lines of NumPy) and is tested in
`tests/`. To rebuild the book:

```bash
pip install -r requirements.txt
pytest -q
myst build --html --execute     # static site in _build/html
myst start --execute            # live preview
```

Things to try: change TR or the tissue parameters in `spoilsim/phantom.py`,
add a centric phase-encode ordering in `spoilsim/imaging.py` (the transient
then lands in the centre of k-space), or compare $\phi_0 = 50^\circ$ with
$117^\circ$.

## References

- Zur Y, Wood ML, Neuringer LJ. Spoiling of transverse magnetization in
  steady-state sequences. *Magn Reson Med.* 1991;21(2):251–263.
- Preibisch C, Deichmann R. Influence of RF spoiling on the stability and
  accuracy of T1 mapping based on spoiled FLASH with varying flip angles.
  *Magn Reson Med.* 2009;61(1):125–135.
