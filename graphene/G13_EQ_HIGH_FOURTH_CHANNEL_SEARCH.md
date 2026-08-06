# G13 equilibrium high-temperature fourth-channel search

## Scope

G12 selected the equilibrium sector

\[
(T_{\mathrm{eq}},n),\qquad 110\ \mathrm{K}\le T_{\mathrm{eq}}\le260\ \mathrm{K},
\]

with three existing machine-readable responses:

\[
G(T,n),\qquad K_e(T,n),\qquad \Sigma_Q(T,n).
\]

G13 searches for one additional directly measured equilibrium response surface. It does not calculate a Pluecker residual.

## Frozen qualification gates

A candidate must provide:

1. equilibrium sample temperature, not transient peak electronic temperature;
2. a directly measured response rather than a theory or reconstructed curve;
3. carrier-density-resolved data;
4. at least three distinct temperatures inside 110-260 K;
5. at least five distinct densities at each accepted temperature;
6. machine-readable numerical values before fitting;
7. pointwise uncertainty or fit-level data sufficient to reconstruct covariance;
8. no temperature or density extrapolation;
9. no algebraic reconstruction from the existing G, K_e or Sigma_Q channels.

## Selected acquisition target: equilibrium Seebeck coefficient

The strongest candidate is the equilibrium Seebeck coefficient

\[
S(T,n)=-\frac{\Delta V}{\Delta T}.
\]

It is a directly measured thermoelectric response and is conceptually distinct from conductance, thermal conductance and the quantum-critical conductivity parameter.

### Primary source target

Deqi Wang and Jing Shi, *Effect of charged impurities on the thermoelectric power of graphene near the Dirac point*, Phys. Rev. B 83, 113403 (2011), DOI `10.1103/PhysRevB.83.113403`, arXiv `1101.4676`.

The article reports thermoelectric power and electrical conductivity over a wide temperature range and carrier-density control. However, G13 does not treat this description as a numerical surface. Public machine-readable S(T,n) arrays, exact target-window temperature support and pointwise covariance have not been verified.

Decision: `SELECT_PRIMARY_ACQUISITION_TARGET`.

### Secondary source target

Yuri M. Zuev, Willy Chang and Philip Kim, *Thermoelectric and Magnetothermoelectric Transport Measurements of Graphene*, Phys. Rev. Lett. 102, 096807 (2009), DOI `10.1103/PhysRevLett.102.096807`, arXiv `0812.1393`.

The primary manuscript directly reports equilibrium thermoelectric-power sweeps versus gate voltage. Clearly identified full density sweeps occur at 10, 40, 80, 150 and 300 K in Fig. 1, and at 15, 40 and 200 K in Fig. 2. Only 150 and 200 K lie inside the selected 110-260 K window. This fails the frozen three-temperature gate.

Decision: `SECONDARY_AUTHOR_DATA_TARGET`.

## Rejected alternatives

### Quantum capacitance

The Xia et al. quantum-capacitance measurement is directly density or gate resolved, but a three-temperature equilibrium surface inside 110-260 K has not been verified. It remains one-dimensional for this campaign.

### Hall coefficient or inferred carrier density

Carrier density is already a chart coordinate. Hall-derived density would duplicate the coordinate calibration rather than supply an independent response channel.

### Equilibrium Raman peak position or linewidth

Temperature-resolved Raman data exist, but a machine-readable equilibrium T-n surface with uncertainty has not been verified. The separate heating-cooling hysteresis experiment is not silently reused as this equilibrium channel.

### Photo-thermoelectric, hot-carrier or thermally generated spin responses

These use transient electronic temperature, bilayer or magnetic graphene, or another material sector. G12 forbids cross-sector brackets.

## Required author-data package

G14 should request:

- measured Seebeck coefficient versus gate voltage or carrier density at every equilibrium temperature;
- exact temperature list and thermometer calibration;
- raw or fit-level thermovoltage and temperature-gradient data;
- gate-voltage to density calibration and uncertainty;
- pointwise statistical uncertainty and shared systematic covariance;
- device IDs, sweep direction, contact geometry and annealing state.

Digitization may be used only after figure identity, axis calibration, point extraction uncertainty and covariance assumptions are frozen. It cannot manufacture a third target-window temperature curve that is absent from the source.

## Current result

```text
status                    INCONCLUSIVE_EQ_HIGH_FOURTH_CHANNEL_ACQUISITION
selected candidate        SEEBECK_WANG_SHI_2011
secondary candidate       SEEBECK_ZUEV_KIM_2009
fit-ready candidates      0
fourth channel ready      false
fit allowed               false
Pluecker significance     not computed
```

Next stage: `G14_SEEBECK_AUTHOR_DATA_AND_DIGITIZATION_CONTRACT`.
