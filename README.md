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

### Completed water ladder

1. `T01A_COMMON_GRADIENT_CONTROL`: `PASS_CONTROL`.
2. `T01B_INDEPENDENT_BRACKET_SYNTHETIC`: detector rejects a large injected inconsistency at 11.28 sigma.
3. `T01C_IAPWS95_CONTROL`: `PASS_CONTROL` over five stable liquid-water states.
4. `T01D_THERMOML_EXPERIMENTAL`: `NOT_FALSIFIED` using twelve distinct ThermoML publications.

```text
state                                T = 318.15 K, P = 12.5 MPa
Pluecker residual                   -1.8654273205408826e-06
standard error                       8.08728994960218e-06
z score                              0.23066161002829436
rejection threshold                  5.0
status                               NOT_FALSIFIED
```

## Graphene response campaign

The transport-source campaign is separate from the earlier graphene Raman heating-cooling hysteresis statistic. The Raman experiment uses nonzero loop area significance. This campaign asks whether four response channels can support an independent Pluecker test on one frozen two-control chart.

### G01–G07: sources, model control and topology

- `G01`: freezes the chart and significance semantics.
- `G02`: ideal massless-Dirac common-model control, `PASS_CONTROL`.
- `G03`: identifies the first experimental bridge.
- `G04`: pins four official PDFs without redistributing them.
- `G05`: discovers and pins nine official Nature Physics XLSX workbooks.
- `G06`: maps compact source-data labels.
- `G07`: freezes numerical layouts for 22 high-priority sheets.

### G08: first four-channel attempt

Candidate channels:

1. electrical conductance `G(T,n)`;
2. electronic thermal conductance `K_e(T,n)`;
3. quantum-critical conductivity `Sigma_Q(T,n)`;
4. measured Lorenz ratio `L/L0(T,n)`.

The common temperature domain is empty:

```text
K_e temperature range        110-260 K
measured L/L0 range           40-100 K
status                        INCONCLUSIVE_COMMON_DOMAIN
```

No extrapolation is permitted.

### G09: replacement ranking

Replacement priority:

1. Aamir 2021 electronic heat capacity `C_e`;
2. Block 2021 electronic thermal diffusivity `D_e`.

Circular same-source reconstructions and theory-derived substitutes are rejected.

### G10: electronic heat-capacity coverage

Measured density-resolved `C_e(n)` support occurs at 15.5, 60 and 100 K. The current base channels begin at 110 K. A measured `C_e(T_e)` curve extends to approximately 195 K but only at one fixed density.

```text
status                     INCONCLUSIVE_TWO_DIMENSIONAL_COMMON_DOMAIN
density-resolved overlap   EMPTY
fixed-density overlap      110-195 K
replacement ready          false
```

A one-density temperature curve cannot supply local derivatives in both `T` and `n`.

### G11: thermal-diffusivity state-variable audit

Block 2021 measures spatiotemporal thermoelectric current and fitted spatial widths at fixed lattice temperature `T_l = 300 K`. Its control variable is a transient peak electron temperature inferred from optical power.

The base channels instead use equilibrium sample temperature. These are different physical coordinates:

```text
equilibrium sample temperature     != transient peak electron temperature
```

The complete published `D(T_F,T_e)` surfaces are Boltzmann calculations, while the measured objects are `Delta I_TE` maps and width-based diffusivity estimates.

```text
status              INCONCLUSIVE_STATE_VARIABLE_ALIGNMENT_AND_MEASURED_SURFACE
replacement ready   false
fit allowed         false
```

Raw maps, fit covariance, power-to-temperature calibration, density calibration, focus-width uncertainty and instrument-response covariance are required from the authors before any stronger use.

## Current scientific boundary

The campaign has not produced an experimental graphene Pluecker score. It has instead identified three independent blockers:

1. empty common temperature support in the first four-channel set;
2. insufficient two-dimensional heat-capacity coverage in the replacement set;
3. incompatible meanings of temperature in the thermal-diffusivity replacement.

The next stage is `G12_TEMPERATURE_COORDINATE_REDESIGN`.

## Reproduce

```bash
python -m pip install -e ".[test]"
python -m pytest
python scripts/run_g10_ce_coverage_audit.py
python scripts/run_g11_de_coverage_audit.py
```

`NOT_FALSIFIED` does not prove that the Recognition framework is uniquely selected by nature. It means a frozen measurement contract did not reject the stated constraint. No graphene experimental Pluecker significance may be announced until chart semantics, source independence, uncertainty and a common two-dimensional domain are all frozen and reproduced.
