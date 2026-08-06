# G02 Ideal Dirac-Graphene Control

## Purpose

`G02_DIRAC_GRAPHENE_CONTROL` is a deterministic common-model control for the graphene campaign.

It verifies that four smooth electronic response channels generated on one explicit two-dimensional state chart produce a rank-two skew bracket matrix and a numerically flat Pluecker residual.

It does **not** provide experimental confirmation or a sigma significance.

## State chart

The frozen dimensionless coordinates are

\[
\theta = T/T_0,
\qquad
m = \mu/(k_B T_0),
\qquad
\eta = m/\theta.
\]

The numerical contract is restricted to

\[
|\eta| \le 8.
\]

This is a thermodynamic/electronic state chart. It is not inferred from graphene being spatially two-dimensional.

## Four channels

Overall positive dimensional prefactors are removed, leaving four nondimensional response functions:

1. net Dirac carrier density;
2. total electronic energy density;
3. electronic entropy density;
4. quantum-compressibility response.

The carrier and energy channels are evaluated from fixed Fermi-Dirac quadrature. Entropy is computed from the two-dimensional massless-Dirac relation `p = u/2`, and compressibility is the chemical-potential derivative of net density.

## Independent control gates

The control must satisfy all of the following:

- charge density is odd under `m -> -m`;
- energy, entropy, and compressibility are even under `m -> -m`;
- the neutrality-point values agree with their closed forms;
- the four-channel skew response matrix has negligible rank tail;
- the normalized Pluecker residual remains below the frozen numerical tolerance.

## Numerical contract

- quadrature: 256-node Gauss-Legendre;
- integration domain: `[0, 60]`;
- chart derivative: central finite difference;
- relative derivative step: `1e-4`;
- control points: five states spanning electron, neutrality, and hole sectors;
- maximum normalized Pluecker residual gate: `1e-14`;
- maximum rank-tail ratio gate: `1e-12`;
- neutrality and parity error gates: `1e-10`.

## Claim boundary

Allowed conclusion:

> The ideal common-model graphene response system is numerically Pluecker-flat on the frozen two-variable chart.

Forbidden conclusions:

- graphene has experimentally confirmed the theorem;
- the control has an experimental sigma value;
- graphene passes because it is spatially two-dimensional;
- the control replaces the need for independently sourced channel measurements.

## Experimental bridge

The 2025 paper *Universality in quantum critical flow of charge and heat in ultraclean graphene* (`10.1038/s41567-025-02972-z`) is a particularly valuable acquisition target because it combines electrical and electronic thermal conductivity in high-quality graphene devices near the Dirac point. NIMS MDR hosts the accepted manuscript and supplementary PDF. These remain two compatible measured channels, not yet a complete four-channel Pluecker experiment.
