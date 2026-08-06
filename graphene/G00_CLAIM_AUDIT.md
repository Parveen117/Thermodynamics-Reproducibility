# G00 Graphene Claim Audit

## Status

`REJECT_UNSUPPORTED_30_SIGMA_NARRATIVE`

The proposed statement that graphene gives a 30-sigma confirmation is not currently supported by a reproducible dataset or certificate in this repository.

## Significance convention

This repository defines

\[
z = \frac{|P(B)|}{\sigma_P}.
\]

Under that convention:

- `z < 5` means the frozen measurement contract is not rejected;
- `z > 5` means `FALSIFIED_MEASUREMENT_CONTRACT`;
- `z = 30` would be a thirty-sigma rejection, not a residual thirty times smaller than its uncertainty.

A statement that the residual is thirty times smaller than its uncertainty would correspond to

\[
z \approx \frac{1}{30} \approx 0.033,
\]

not `30 sigma`.

## Which two dimensions matter

The Pluecker theorem concerns a two-dimensional **state or control manifold** on which four scalar response channels are defined. It does not identify the spatial dimension of the specimen with the dimension of the thermodynamic chart.

Therefore:

- monolayer graphene being spatially two-dimensional does not force the theorem to pass;
- bulk water being spatially three-dimensional does not weaken a test performed on a two-variable chart such as `(T, P)`;
- the chart, controls, constraints, and hidden state variables must be declared independently of material geometry.

## Graphene is not hidden-variable-free

Any graphene campaign must freeze or model at least:

- monolayer versus bilayer or multilayer structure;
- substrate or suspension;
- encapsulation material;
- carrier density and charge inhomogeneity;
- electronic and lattice temperatures;
- strain and rippling;
- defects, contamination, and disorder;
- magnetic field and displacement field;
- contact geometry and device mobility.

These are not excuses to use after inspection. They are part of the observation contract before a residual is evaluated.

## Correct claim language

Until a pinned dataset and frozen protocol produce a certificate, allowed language is:

> Graphene is a promising candidate for a stringent two-control response test because several electronic responses can be tuned by carrier temperature and carrier density. No graphene significance level has yet been established by this repository.

Forbidden language includes:

- `graphene confirms the theorem at 30 sigma`;
- `graphene has no hidden variables`;
- `spatially 2D implies a two-dimensional thermodynamic state manifold`;
- `NIST-level graphene data are already centralized in ThermoML`.
