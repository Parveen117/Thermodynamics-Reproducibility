# T01D Independent ThermoML Pluecker Test

## Verdict

```text
NOT_FALSIFIED
```

At the frozen liquid-water state

```text
T = 318.15 K
P = 12.5 MPa
```

the independently reconstructed six-channel Pluecker residual was

\[
P(B)=-1.8654273205408826\times 10^{-6},
\]

with delta-method standard error

\[
\sigma_P=8.08728994960218\times10^{-6}.
\]

Therefore

\[
\frac{|P(B)|}{\sigma_P}=0.23066161002829436,
\]

well below the frozen rejection threshold of five standard deviations.

## Channels

The tested nondimensional response channels were:

1. mass density;
2. speed of sound;
3. molar heat capacity at constant pressure;
4. viscosity.

The six pairwise brackets were estimated from twelve distinct ThermoML publications. No publication was reused in another source slot, and no single four-channel fitted surface was used to manufacture all six brackets.

## Why these channels were used

The pinned ThermoML archive did not contain enough independent two-dimensional surfaces to test the narrower caloric-mechanical tetrad directly. That narrow test is therefore recorded as `INCONCLUSIVE_DATA_COVERAGE`, not silently replaced.

The paper's proved geometric theorem applies to any four smooth nondimensional response channels on a two-dimensional equilibrium chart. Density, sound speed, isobaric heat capacity, and viscosity supplied the strongest independently replicated liquid-water candidate set in the archive.

## Bootstrap audit

A deterministic parametric bootstrap with 200,000 gradient draws gave

```text
bootstrap standard error              8.14856878214715e-06
bootstrap / delta standard-error ratio 1.0075771776363704
bootstrap z score                     0.22892698956261887
```

Zero lay inside the bootstrap 95%, 99%, and 99.9% residual intervals. The primary verdict is therefore not an artifact of the first-order delta approximation.

## Manifest revision discipline

Manifest v1 was inconclusive because two source slots failed the fit-geometry gates. The Pluecker residual was not computed. Two unused sources with stronger point topology were selected using only pre-residual diagnostics, and the original evaluation point, fit family, bandwidths, uncertainty rule, gates, and five-sigma threshold were retained unchanged in manifest v2.

## Scientific interpretation

The result means that this frozen conjunction of:

- liquid-water two-dimensional chart;
- four declared response channels;
- twelve-source provenance assignment;
- nondimensionalization;
- weighted quadratic fit contract;
- reported uncertainty interpretation;
- and Pluecker rank-two constraint

was not rejected by the selected online experimental records.

It does not prove that the Recognition framework is uniquely selected by nature. It does establish that the theorem survived a non-tautological test in which the six brackets were independently reconstructed rather than generated from one common pair of gradients.

## Remaining robustness work

A stronger publication-grade campaign should repeat the analysis across multiple state points, bandwidths, and alternative independent source assignments. Those tests assess stability of the `NOT_FALSIFIED` verdict; they are not allowed to redefine the completed primary result.
