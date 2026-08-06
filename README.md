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

The transport-source campaign is separate from the earlier graphene Raman heating-cooling hysteresis statistic. The Raman experiment uses nonzero loop-area significance. This campaign asks whether four response channels can support an independent Pluecker test on one frozen two-control chart.

### G01–G07: sources, model control and topology

- `G01`: freezes chart and significance semantics.
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

### G09–G11: replacement audits

Replacement priority initially selected:

1. Aamir 2021 electronic heat capacity `C_e`;
2. Block 2021 electronic thermal diffusivity `D_e`.

G10 found that density-resolved heat-capacity measurements stop at 100 K. A fixed-density curve reaches approximately 195 K but cannot supply local derivatives in both temperature and carrier density.

G11 found that Block uses transient peak electronic temperature at fixed lattice temperature, whereas the base channels use equilibrium sample temperature. The complete published `D(T_F,T_e)` surfaces are calculations, not public measured response tables.

```text
G10  INCONCLUSIVE_TWO_DIMENSIONAL_COMMON_DOMAIN
G11  INCONCLUSIVE_STATE_VARIABLE_ALIGNMENT_AND_MEASURED_SURFACE
```

### G12: typed temperature-sector redesign

The campaign no longer uses an informal universal temperature coordinate. It freezes a sector atlas:

```text
EQ_HIGH_TN                         SELECT PRIMARY
EQ_LOW_TN                          KEEP AS FALLBACK SECTOR
TRANSIENT_HOT_TE_N                 SEPARATE COMPANION CAMPAIGN
T_OVER_TF_N                        REJECT AS GLOBAL CHART
TE_TL_N                            HONEST BUT THREE-DIMENSIONAL
```

The selected primary chart is

\[
(T_{\mathrm{eq}},n),\qquad 110\ \mathrm{K}\le T_{\mathrm{eq}}\le260\ \mathrm{K},
\]

with three machine-readable responses:

\[
G(T,n),\qquad K_e(T,n),\qquad \Sigma_Q(T,n).
\]

`T/T_F` is rejected as a global chart because `T_F=0` at the Dirac point and because dimensionless scaling does not erase equilibrium-versus-transient protocol differences.

```text
status  PASS_SECTORIZED_TEMPERATURE_REDESIGN
```

### G13: equilibrium fourth-channel search

The strongest acquisition target is the equilibrium Seebeck coefficient

\[
S(T,n)=-\frac{\Delta V}{\Delta T}.
\]

Primary target:

- Wang and Shi 2011, DOI `10.1103/PhysRevB.83.113403`;
- directly measured equilibrium thermoelectric response;
- broad temperature and carrier-density coverage reported;
- public machine-readable arrays, exact target-window support and covariance not verified.

Secondary target:

- Zuev, Chang and Kim 2009, DOI `10.1103/PhysRevLett.102.096807`;
- clearly verified density sweeps inside 110–260 K occur at 150 and 200 K only;
- fails the frozen minimum-three-temperature gate.

Quantum capacitance lacks a verified target-window `T-n` surface. Hall-derived density duplicates a chart coordinate. Equilibrium Raman lacks a verified machine-readable `T-n` surface. Transient photo-thermoelectric and spin responses fail the G12 sector contract.

```text
status                    INCONCLUSIVE_EQ_HIGH_FOURTH_CHANNEL_ACQUISITION
selected candidate        SEEBECK_WANG_SHI_2011
secondary candidate       SEEBECK_ZUEV_KIM_2009
fit-ready candidates      0
fourth channel ready      false
fit allowed               false
Pluecker significance     not computed
```

## Current scientific boundary

The valid primary sector and three existing response channels are frozen, but no fourth equilibrium response surface has passed all acquisition gates. The next stage is:

`G14_SEEBECK_AUTHOR_DATA_AND_DIGITIZATION_CONTRACT`

G14 requires pointwise Seebeck data, exact temperature support, gate-to-density calibration, thermovoltage and temperature-gradient information, and statistical plus shared systematic covariance. Digitization cannot manufacture a missing temperature curve.

## Reproduce

```bash
python -m pip install -e ".[test]"
python -m pytest
python scripts/run_g10_ce_coverage_audit.py
python scripts/run_g11_de_coverage_audit.py
python scripts/run_g12_temperature_coordinate_redesign.py
python scripts/run_g13_eq_high_fourth_channel_search.py
```

`NOT_FALSIFIED` does not prove that the Recognition framework is uniquely selected by nature. It means a frozen measurement contract did not reject the stated constraint. No graphene experimental Pluecker significance may be announced until chart semantics, source independence, uncertainty and a common two-dimensional domain are all frozen and reproduced.
