# T01 Measurement Contract

## Target

Test whether six independently estimated pairwise response brackets are compatible with a decomposable two-form on a smooth two-dimensional equilibrium chart.

For pair order

```text
(12, 13, 14, 23, 24, 34)
```

the frozen target equation is

\[
P(B)=B_{12}B_{34}-B_{13}B_{24}+B_{14}B_{23}=0.
\]

## Critical distinction

A matrix reconstructed from one shared pair of gradient vectors,

\[
B=uv^T-vu^T,
\]

satisfies the target equation identically. Such a calculation is labelled `T01A_COMMON_GRADIENT_CONTROL`; it tests implementation and equation-of-state consistency only.

The empirical test, `T01D_THERMOML_EXPERIMENTAL`, must estimate the six pair channels independently. Acceptable designs include:

1. disjoint source publications for different pairs;
2. disjoint experimental methods with covariance retained;
3. held-out pairwise fits whose shared nuisance parameters are included in the full six-channel covariance;
4. direct cyclic or area-response measurements for each pair.

Reusing one fitted four-channel gradient model to produce all six entries is forbidden for the falsification verdict.

## Frozen state chart

Initial control chart:

```text
material: ordinary water
coordinates: temperature T and pressure P
phase: stable single-phase liquid
excluded: saturation line, critical neighbourhood, spinodal/metastable region
```

The experimental chart and numerical region must be recorded before residual evaluation.

## Channel requirements

Every response channel must record:

- physical definition;
- units;
- reference scale used for nondimensionalization;
- constraint held fixed;
- source publication and table;
- experimental method;
- state coordinates;
- reported and propagated uncertainty;
- transformations and interpolation method.

No channel substitution is allowed after seeing the result.

## Statistical decision

Let `b` be the six-channel estimate and `Sigma` its covariance. The first-order residual variance is

\[
\operatorname{Var}P\approx \nabla P(b)^T\Sigma\nabla P(b).
\]

The initial conservative rejection gate is

\[
|P(b)|/\sigma_P>5.
\]

A five-sigma crossing yields `FALSIFIED_MEASUREMENT_CONTRACT`, meaning at least one frozen assumption failed. It does not identify the failed assumption without further controlled experiments.

## Required controls

- exact common-gradient algebra;
- synthetic nondecomposable injection;
- scale and sign invariance checks;
- covariance positive-semidefinite audit;
- bootstrap comparison before a real-data claim;
- state-domain sensitivity and leave-one-source-out analysis.

## Data-source boundary

IAPWS-95 is a smooth equation-of-state control, not independent experimental evidence. NIST states that ThermoML records experimental data and detailed metadata but that the archived values are not critically evaluated. The repository must preserve that distinction.
