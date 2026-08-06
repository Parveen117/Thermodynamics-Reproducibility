# Thermodynamics Reproducibility

Empirical and computational falsification tests for thermodynamic claims in the Recognition Kernel Framework and the paper **Geometric Completion of Thermodynamic Response**.

## First campaign

`T01_PLUCKER_INDEPENDENT_BRACKETS`

The paper proves that four smooth response channels on a two-dimensional equilibrium chart generate a skew response-bracket matrix

\[
B_{ab}=\{f_a,f_b\},
\]

with

\[
P(B)=B_{12}B_{34}-B_{13}B_{24}+B_{14}B_{23}=0.
\]

### Audit distinction

If all six entries are constructed from one shared pair of estimated gradient vectors,

\[
B=uv^T-vu^T,
\]

then `P(B)=0` is an algebraic identity. That calculation is useful as an implementation and equation-of-state consistency control, but it cannot by itself falsify the two-dimensional thermodynamic hypothesis.

The actual falsification campaign therefore requires the six pairwise bracket channels to be estimated independently, with disjoint or explicitly modelled provenance and a declared covariance matrix. The measured six-vector is then tested against the decomposable rank-two constraint.

## Campaign ladder

1. `T01A_COMMON_GRADIENT_CONTROL`
   - Verify the exact algebra and numerical implementation.
   - Demonstrate that common-gradient reconstruction is necessarily Pluecker-flat.

2. `T01B_INDEPENDENT_BRACKET_SYNTHETIC`
   - Inject controlled cross-channel inconsistency.
   - Verify that the statistical detector rejects beyond the declared uncertainty.

3. `T01C_IAPWS95_CONTROL`
   - Use IAPWS-95 water properties as a smooth two-variable equation-of-state control.
   - This is a numerical consistency test, not independent experimental falsification.

4. `T01D_THERMOML_EXPERIMENTAL`
   - Build independently sourced response channels from NIST ThermoML records.
   - Preserve source, method, units, constraints, and uncertainty for every datum.

## Allowed outcomes

- `PASS_CONTROL`
- `FAIL_CONTROL`
- `NOT_FALSIFIED`
- `FALSIFIED_MEASUREMENT_CONTRACT`
- `INCONCLUSIVE_DATA_COVERAGE`
- `INCONCLUSIVE_UNCERTAINTY_MODEL`

No failed result may be renamed as curvature, hidden memory, or a new constitutive law after inspection. The observation contract is frozen before the residual is evaluated.

## Reproduce

```bash
python -m pip install -e ".[test]"
python -m pytest
python scripts/run_t01_synthetic_audit.py
python scripts/run_t01_iapws95_control.py
```

The generated certificates must match:

- `results/T01_SYNTHETIC_AUDIT.json`
- `results/T01C_IAPWS95_CONTROL.json`

## Source hierarchy

- IAPWS R6-95(2018), the official IAPWS-95 formulation for ordinary water.
- NIST ThermoML Archive, an XML-based IUPAC representation of experimental thermophysical and thermochemical data.
- Recognition Kernel Framework thermodynamic theorem archive.

## Current result

```text
T01A common-gradient algebra                     PASS_CONTROL
T01B small independent inconsistency             NOT_FALSIFIED
T01B large independent inconsistency             FALSIFIED_MEASUREMENT_CONTRACT (11.28 sigma)
T01C IAPWS-95 water control                      PASS_CONTROL
T01D ThermoML independent experimental test      NEXT DATA CAMPAIGN
```

IAPWS-95 control range:

```text
states tested                                    5
T range                                          285 K to 350 K
P range                                          0.1 MPa to 10 MPa
maximum flat-closure error                       2.220446049250313e-16
maximum sound-bulk relative error                1.9050453295659672e-16
maximum normalized Pluecker residual             3.533498065462128e-17
```

The validation suite contains thirteen passing test cases. GitHub Actions reproduces both certificates on Python 3.11 and 3.12.
