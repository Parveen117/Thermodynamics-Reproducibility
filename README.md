# Thermodynamics Reproducibility

Empirical and computational falsification tests for thermodynamic claims in the Recognition Kernel Framework and the paper **Geometric Completion of Thermodynamic Response**.

## First campaign

`T01_PLUCKER_INDEPENDENT_BRACKETS`

For four smooth nondimensional response channels on a two-dimensional equilibrium chart, the paper proves that the six pairwise area brackets obey

\[
P(B)=B_{12}B_{34}-B_{13}B_{24}+B_{14}B_{23}=0.
\]

### Audit distinction

If all six entries are constructed from one shared pair of estimated gradient vectors,

\[
B=uv^T-vu^T,
\]

then `P(B)=0` is an algebraic identity. That calculation is an implementation control, not a falsification test.

The empirical campaign therefore estimates the six bracket channels from disjoint publication slots with a declared covariance model.

## Completed campaign ladder

1. `T01A_COMMON_GRADIENT_CONTROL`
   - exact algebra and numerical implementation;
   - result: `PASS_CONTROL`.

2. `T01B_INDEPENDENT_BRACKET_SYNTHETIC`
   - small inconsistency: `NOT_FALSIFIED`;
   - large inconsistency: `FALSIFIED_MEASUREMENT_CONTRACT` at 11.28 sigma.

3. `T01C_IAPWS95_CONTROL`
   - five stable liquid-water states;
   - result: `PASS_CONTROL`.

4. `T01D_THERMOML_EXPERIMENTAL`
   - pinned NIST ThermoML archive;
   - twelve distinct publications for twelve source slots;
   - density, sound speed, isobaric heat capacity, and viscosity;
   - result: `NOT_FALSIFIED`.

## T01D primary result

Frozen state:

```text
T = 318.15 K
P = 12.5 MPa
```

Primary delta-method result:

```text
Pluecker residual                  -1.8654273205408826e-06
standard error                      8.08728994960218e-06
z score                             0.23066161002829436
rejection threshold                 5.0
status                              NOT_FALSIFIED
```

Deterministic 200,000-draw bootstrap:

```text
bootstrap standard error            8.14856878214715e-06
bootstrap / delta SE ratio           1.0075771776363704
bootstrap z score                    0.22892698956261887
zero inside 95%, 99%, 99.9% ranges  yes
status                              NOT_FALSIFIED
```

The result is recorded in:

- `results/T01D_FINAL_CERTIFICATE.json`
- `results/T01D_RESULT.md`

## Narrow-tetrad boundary

The pinned ThermoML archive did not provide enough independent two-dimensional surfaces for the strict caloric-mechanical tetrad. That route is recorded as `INCONCLUSIVE_DATA_COVERAGE`.

The completed experiment instead tests the paper's broader theorem for any four smooth nondimensional response channels. The channel substitution was made from the archive inventory before fitting or residual evaluation.

## Manifest history

Manifest v1 failed two fit-geometry gates and produced no bracket residual. The two weak source slots were replaced using only point topology and uncertainty availability. Manifest v1 remains archived, the revision is recorded, and the fit family, state, bandwidths, gates, uncertainty rule, and five-sigma threshold were unchanged in v2.

## IAPWS-95 control

```text
states tested                         5
T range                               285 K to 350 K
P range                               0.1 MPa to 10 MPa
maximum flat-closure error            2.220446049250313e-16
maximum sound-bulk relative error     1.9050453295659672e-16
maximum normalized Pluecker residual  3.533498065462128e-17
```

## Reproduce

```bash
python -m pip install -e ".[test]"
python -m pytest
python scripts/run_t01_synthetic_audit.py
python scripts/run_t01_iapws95_control.py
```

The ThermoML workflows download the pinned NIST archive, verify its SHA-256, extract the frozen source slots, reproduce the independent test, and run the bootstrap audit.

## Claim boundary

`NOT_FALSIFIED` does not prove that the Recognition framework is uniquely selected by nature. It means the frozen independent measurement contract did not reject the Pluecker constraint. Stronger work should repeat the campaign across alternative state points, bandwidths, and unused source ensembles without redefining this completed primary result.
