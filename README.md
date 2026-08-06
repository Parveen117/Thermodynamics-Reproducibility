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

## G01 graphene feasibility

`G01_GRAPHENE_FEASIBILITY`

The graphene campaign begins by separating two different significance statistics.

### Raman hysteresis versus Pluecker residual

The earlier preprint **Multiscale Violation of Onsager Reciprocity**, Research Square DOI `10.21203/rs.3.rs-9055273/v2`, reports Raman heating-cooling hysteresis loop areas above 30 sigma under a loop-area statistic. That is evidence for a nonzero loop under its own calibration and uncertainty contract.

The G01 campaign is different. It uses

\[
z_P=\frac{|P(B)|}{\sigma_P}.
\]

For this statistic:

- `z_P <= 5` means `NOT_FALSIFIED`;
- `z_P > 5` means `FALSIFIED_MEASUREMENT_CONTRACT`;
- `z_P = 30` would be a thirty-sigma Pluecker rejection;
- a residual thirty times smaller than uncertainty would give `z_P approximately 0.033`.

The repository therefore rejects only the **conflation** of the two statistics, not the earlier Raman-loop result.

### State-manifold correction

The theorem concerns a two-dimensional state or control chart, not the spatial dimension of the material. Monolayer graphene also has important nuisance variables including substrate, encapsulation, carrier density, strain, disorder, contamination, contact geometry, and electronic versus lattice temperature.

### Candidate chart and channels

The strongest initial chart is `(T_e, n)`, electronic temperature and carrier density, with candidate channels:

1. electronic heat capacity `C_e`;
2. quantum capacitance or inverse compressibility;
3. electrical conductivity;
4. electronic thermal diffusivity or thermal conductivity.

ThermoML graphene hits are dominated by composites, graphene oxide, and aerogels rather than pristine monolayer graphene response surfaces. Online experimental graphene data exist, but a compatible four-channel machine-readable contract has not yet been assembled.

Current status:

```text
G00 Raman / Pluecker statistic distinction        FROZEN
G01 ThermoML pristine-graphene route               INSUFFICIENT
G01 online primary-source ledger                   PASS_FEASIBILITY_LEDGER
G01 four machine-readable response surfaces        NOT YET ASSEMBLED
G01 graphene Pluecker significance                 NOT YET COMPUTED
```

See:

- `graphene/G00_CLAIM_AUDIT.md`
- `graphene/G01_SOURCE_INVENTORY.md`
- `graphene/G01_SOURCE_LEDGER.json`
- `protocols/G01_GRAPHENE_FEASIBILITY.json`
- `results/G01_FEASIBILITY_AUDIT.json`

## G02 ideal Dirac-graphene control

`G02_DIRAC_GRAPHENE_CONTROL`

The ideal graphene control uses the explicit two-variable state chart

\[
\theta=T/T_0,
\qquad
m=\mu/(k_B T_0),
\]

with four dimensionless channels:

1. net Dirac carrier density;
2. total electronic energy density;
3. electronic entropy density;
4. quantum-compressibility response.

The model checks neutrality-point closed forms, electron-hole parity, the rank-two skew-matrix tail, and the Pluecker residual at five states spanning electron, neutrality, and hole sectors.

Cross-version result:

```text
status                                      PASS_CONTROL
maximum normalized Pluecker residual        9.623875392445127e-18
maximum skew rank-tail ratio                1.137913056238364e-16
maximum neutrality formula error            9.464077248116687e-15
maximum electron-hole parity error          0.0
Python versions                             3.11 and 3.12
experimental sigma significance             NONE
```

This is a common-model numerical control, not experimental confirmation. Its job is to calibrate the graphene pipeline before literature-derived surfaces are allowed to vote.

See:

- `graphene/G02_DIRAC_CONTROL.md`
- `src/thermo_recognition/graphene_dirac.py`
- `scripts/run_g02_dirac_graphene_control.py`
- `tests/test_graphene_dirac.py`
- `results/G02_DIRAC_GRAPHENE_CONTROL.json`

## G03 experimental bridge

`G03_GRAPHENE_EXPERIMENTAL_BRIDGE`

The strongest newly identified bridge is the 2025 Nature Physics study **Universality in quantum critical flow of charge and heat in ultraclean graphene**, which combines measured electrical and electronic thermal conductivity in high-quality devices near the Dirac point. NIMS MDR hosts the accepted manuscript and supplementary PDF.

That source improves same-device coverage to two channels. It does not yet create a four-channel independent Pluecker experiment.

Current gate:

```text
same-device electrical + thermal conductivity      AVAILABLE FOR ACQUISITION
heat-capacity candidate                             AVAILABLE AS PDF/SI
thermal-diffusivity candidate                       RAW DATA ON REQUEST / DIGITIZE
quantum-capacitance temperature surface             UNRESOLVED
four compatible experimental surfaces              NOT MET
experimental graphene Pluecker residual             FORBIDDEN UNTIL GATE PASSES
```

See `protocols/G03_GRAPHENE_EXPERIMENTAL_BRIDGE.json`.

## Reproduce

```bash
python -m pip install -e ".[test]"
python -m pytest
python scripts/validate_g01_source_ledger.py
python scripts/run_g02_dirac_graphene_control.py
python scripts/run_t01_synthetic_audit.py
python scripts/run_t01_iapws95_control.py
```

The ThermoML workflows download the pinned NIST archive, verify its SHA-256, extract the frozen source slots, reproduce the independent water test, and run the bootstrap audit. The graphene workflows verify significance semantics, source acquisition, ideal Dirac thermodynamics, and the common-model Pluecker control on Python 3.11 and 3.12.

## Claim boundary

`NOT_FALSIFIED` does not prove that the Recognition framework is uniquely selected by nature. It means a frozen measurement contract did not reject the Pluecker constraint. No graphene experimental Pluecker result may be announced until its own chart, sources, covariance model, and residual are frozen and reproduced.
