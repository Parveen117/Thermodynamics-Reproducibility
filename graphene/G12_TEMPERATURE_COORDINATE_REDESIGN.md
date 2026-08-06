# G12 Temperature-Coordinate Redesign

## Why G12 is necessary

The earlier graphene acquisition stages exposed three different objects that were all casually written as temperature:

1. equilibrium sample temperature in the Majumdar transport workbooks;
2. electronic temperature in the Aamir small-signal calorimetry experiment;
3. transient peak electronic temperature in the Block pump-probe experiment, with the lattice fixed near 300 K.

These variables cannot be merged merely because they share the letter `T`.

The Pluecker experiment requires four response channels on one smooth two-dimensional state sector. It does not authorize brackets assembled across different thermodynamic or nonequilibrium protocols.

## Typed sectors

### Primary sector: `EQ_HIGH_TN`

Coordinates:

\[
(T_{\mathrm{eq}},n),
\qquad 110\ \mathrm{K}\leq T_{\mathrm{eq}}\leq260\ \mathrm{K}.
\]

Current machine-readable channels:

1. electrical conductance `G`;
2. electronic thermal conductance `K_e`;
3. quantum-critical conductivity `Sigma_Q`.

This sector is selected because it is two-dimensional, directly represented by the official source-data workbooks, and regular at the Dirac point.

It is still missing a fourth directly measured response channel with uncertainty and independent provenance.

### Low-temperature equilibrium fallback: `EQ_LOW_TN`

The low-temperature sector contains candidate information from the Lorenz-ratio and heat-capacity experiments. It remains separate because the presently verified density-resolved heat-capacity support and Lorenz-ratio support share only one exact temperature at 100 K.

A single common temperature cannot provide a stable local temperature derivative.

### Transient hot-electron sector: `TRANSIENT_HOT_TE_N`

Coordinates:

\[
(T_e^{\mathrm{peak}},n),
\]

with lattice temperature fixed near 300 K and optical-power, pump-probe-delay, focus-width and instrument-response metadata frozen as part of the protocol.

This is a legitimate two-coordinate experimental sector only after its hidden protocol variables are fixed. It is not the same sector as equilibrium transport.

The Block diffusivity experiment therefore remains a separate companion campaign rather than a replacement channel in `EQ_HIGH_TN`.

## Why `T/T_F` is not the bridge

For ideal monolayer graphene,

\[
T_F\propto\sqrt{|n|}.
\]

Therefore `T/T_F` is undefined at the Dirac point `n = 0`. It may be used as a local reparameterization inside one already-typed sector away from neutrality, but it cannot serve as a global chart joining equilibrium and transient experiments.

A dimensionless coordinate does not erase the physical difference between an equilibrated sample and a photoexcited electronic distribution.

## Honest mixed-temperature description

A mixed equilibrium/transient programme is naturally described by

\[
(T_e,T_l,n),
\]

a three-dimensional manifold. That description is physically cleaner, but the current Pluecker theorem is frozen for a two-dimensional chart.

Reducing this three-dimensional space to two coordinates requires a proved closure relation or a genuinely common fixed-temperature slice. Neither is presently available.

## Frozen decision

```text
EQ_HIGH_TN                         SELECT PRIMARY
EQ_LOW_TN                          KEEP AS FALLBACK SECTOR
TRANSIENT_HOT_TE_N                 SEPARATE COMPANION CAMPAIGN
T_OVER_TF_N                        REJECT AS GLOBAL CHART
TE_TL_N                            HONEST BUT THREE-DIMENSIONAL
```

Current status:

```text
PASS_SECTORIZED_TEMPERATURE_REDESIGN
fourth channel ready               false
fit allowed                        false
experimental Pluecker significance false
```

## Next stage

`G13_EQ_HIGH_FOURTH_CHANNEL_SEARCH`

The next search is restricted to directly measured equilibrium graphene response surfaces on approximately 110-260 K and overlapping carrier density. Candidate sources must provide uncertainty, device metadata and provenance independent enough to support the six-bracket covariance contract.
