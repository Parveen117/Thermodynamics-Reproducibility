# Thermodynamics Reproducibility

Empirical and computational falsification tests for thermodynamic claims in the Recognition Kernel Framework and the paper **Geometric Completion of Thermodynamic Response**.

## T01 water campaign

`T01_PLUCKER_INDEPENDENT_BRACKETS`

For four smooth nondimensional response channels on a two-dimensional equilibrium chart, the paper proves that the six pairwise area brackets obey

\[
P(B)=B_{12}B_{34}-B_{13}B_{24}+B_{14}B_{23}=0.
\]

If all six entries are constructed from one shared pair of estimated gradient vectors,

\[
B=uv^T-vu^T,
\]

then `P(B)=0` is an algebraic identity. That calculation is an implementation control, not a falsification test. The empirical campaign therefore estimates the six bracket channels from disjoint publication slots with a declared covariance model.

### Completed ladder

1. `T01A_COMMON_GRADIENT_CONTROL`: `PASS_CONTROL`.
2. `T01B_INDEPENDENT_BRACKET_SYNTHETIC`: the detector rejects a large injected inconsistency at 11.28 sigma.
3. `T01C_IAPWS95_CONTROL`: `PASS_CONTROL` over five stable liquid-water states.
4. `T01D_THERMOML_EXPERIMENTAL`: `NOT_FALSIFIED` using twelve distinct ThermoML publications.

### T01D primary result

```text
state                                T = 318.15 K, P = 12.5 MPa
Pluecker residual                   -1.8654273205408826e-06
standard error                       8.08728994960218e-06
z score                              0.23066161002829436
rejection threshold                  5.0
status                               NOT_FALSIFIED
```

A deterministic 200,000-draw bootstrap gives `z = 0.22892698956261887` and contains zero in its 95%, 99%, and 99.9% intervals.

The result is recorded in:

- `results/T01D_FINAL_CERTIFICATE.json`
- `results/T01D_RESULT.md`

## G01 graphene campaign

`G01_GRAPHENE_FEASIBILITY`

The graphene campaign begins with a claim audit rather than an inherited significance number.

### Frozen corrections

- The repository defines `z = abs(residual) / standard_error`.
- A result of `30 sigma` would be a thirty-sigma rejection, not overwhelming confirmation.
- A residual thirty times smaller than its uncertainty would have `z approximately 0.033`.
- The theorem concerns a two-dimensional state or control chart, not the spatial dimension of the material.
- Monolayer graphene has important nuisance variables including substrate, encapsulation, carrier density, strain, disorder, contamination, and electronic versus lattice temperature.

### Candidate chart and channels

The strongest initial chart is `(T_e, n)`, electronic temperature and carrier density, with candidate channels:

1. electronic heat capacity `C_e`;
2. quantum capacitance or inverse compressibility;
3. electrical conductivity;
4. electronic thermal diffusivity or thermal conductivity.

ThermoML graphene hits are dominated by composites, graphene oxide, and aerogels rather than pristine monolayer graphene response surfaces. Online experimental graphene data exist, but a compatible four-channel machine-readable contract has not yet been assembled.

Current status:

```text
G00 claimed 30-sigma interpretation               REJECTED
G01 ThermoML pristine-graphene route               INSUFFICIENT
G01 online primary-source inventory                IN PROGRESS
G01 graphene Pluecker significance                 NOT YET COMPUTED
```

See:

- `graphene/G00_CLAIM_AUDIT.md`
- `graphene/G01_SOURCE_INVENTORY.md`
- `protocols/G01_GRAPHENE_FEASIBILITY.json`

## Reproduce

```bash
python -m pip install -e ".[test]"
python -m pytest
python scripts/run_t01_synthetic_audit.py
python scripts/run_t01_iapws95_control.py
```

The ThermoML workflows download the pinned NIST archive, verify its SHA-256, extract the frozen source slots, reproduce the independent water test, and run the bootstrap audit.

## Claim boundary

`NOT_FALSIFIED` does not prove that the Recognition framework is uniquely selected by nature. It means a frozen measurement contract did not reject the Pluecker constraint. No graphene result may be announced until its own chart, sources, covariance model, and residual are frozen and reproduced.
