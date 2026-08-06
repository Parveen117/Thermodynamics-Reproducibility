# G00 Graphene Statistic Audit

## Status

`REJECT_30_SIGMA_PLUCKER_CONFLATION`

A graphene significance above 30 sigma is reported in the earlier preprint **Multiscale Violation of Onsager Reciprocity: Thermomechanical Proof, Atomic Evidence, and Graphene Predictions**, Research Square DOI `10.21203/rs.3.rs-9055273/v2`. That claim concerns temperature-cycle Raman hysteresis loop area, not a Pluecker residual.

The two statistics must not be interchanged.

## Raman hysteresis statistic

For a heating-cooling Raman cycle, a natural significance statistic is

\[
z_H = \frac{|A_{\mathrm{loop}}|}{\sigma_A}.
\]

Under this convention, `z_H > 30` means the measured loop area is strongly inconsistent with zero under the declared loop-area uncertainty model. It can support reproducible hysteresis or curvature evidence, subject to return-class, drift, rate, substrate, and calibration audits.

It does **not** mean that a Pluecker identity has been confirmed at 30 sigma.

## Pluecker statistic

This repository defines the independent-bracket statistic

\[
z_P = \frac{|P(B)|}{\sigma_P},
\qquad
P(B)=B_{12}B_{34}-B_{13}B_{24}+B_{14}B_{23}.
\]

Under this convention:

- `z_P <= 5` means the frozen measurement contract is not rejected;
- `z_P > 5` means `FALSIFIED_MEASUREMENT_CONTRACT`;
- `z_P = 30` would be a thirty-sigma rejection.

A statement that the Pluecker residual is thirty times smaller than its uncertainty would correspond to

\[
z_P \approx \frac{1}{30} \approx 0.033,
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
- contact geometry and device mobility;
- heating and cooling rates for hysteresis experiments.

These are not explanations to introduce after inspection. They are part of the observation contract before a residual or loop significance is evaluated.

## Correct claim language

Allowed language is:

> The earlier graphene Raman campaign reports a greater-than-30-sigma nonzero hysteresis-loop result under its own statistic. The G01 campaign is a separate Pluecker test. No graphene Pluecker significance has yet been computed.

Forbidden language includes:

- `graphene confirms the Pluecker theorem at 30 sigma`;
- `a 30-sigma Pluecker score means the residual is below noise`;
- `graphene has no hidden variables`;
- `spatially 2D implies a two-dimensional thermodynamic state manifold`;
- `NIST-level pristine graphene data are centralized in ThermoML`.
