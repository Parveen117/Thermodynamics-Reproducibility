# G01 Graphene Online-Source Inventory

## Objective

Determine whether online experimental data support a non-tautological four-channel Pluecker test for graphene.

## ThermoML finding

A repository-wide search of the pinned ThermoML mirror for `graphene` returns records dominated by:

- graphene or graphene-oxide aerogels;
- composite phase-change materials;
- graphene oxide and reduced graphene oxide;
- nanofluids and hybrid materials.

These records are not a centralized archive of pristine single-layer graphene response surfaces. ThermoML is therefore not the direct graphene analogue of the pure-water campaign.

## Scientifically coherent chart

The strongest initial graphene chart is

\[
(T_e,n),
\]

where:

- `T_e` is electronic temperature;
- `n` is carrier density.

This chart is preferable to `(T, P)` because graphene electronic responses are commonly tuned by heating and electrostatic gating, while a conventional hydrostatic-pressure chart is not well represented by open graphene measurements.

## Candidate four-channel set

1. Electronic heat capacity, `C_e(T_e,n)`
2. Quantum capacitance or inverse electronic compressibility, `C_q(T_e,n)` or `dmu/dn`
3. Electrical conductivity, `sigma(T_e,n)`
4. Electronic thermal diffusivity or conductivity, `D_e(T_e,n)` or `kappa_e(T_e,n)`

All channels must refer to compatible monolayer graphene devices and the same declared chart. Lattice heat capacity, lattice thermal expansion, and electronic responses must not be mixed without a physical identification of their state variables.

## Primary-source map

### Electronic heat capacity

- Mohammed Ali Aamir et al., *Ultrasensitive Calorimetric Measurements of the Electronic Heat Capacity of Graphene*, Nano Letters 21, 5330-5337 (2021), DOI `10.1021/acs.nanolett.1c01553`.
- Role: direct electronic heat-capacity measurement with electronic-temperature and carrier-density dependence.
- Availability: article and free supporting information are online; a raw machine-readable two-dimensional table has not yet been verified.

### Quantum capacitance / compressibility

- Jilin Xia et al., *Measurement of the quantum capacitance of graphene*, Nature Nanotechnology 4, 505-509 (2009), DOI `10.1038/nnano.2009.177`.
- S. Droescher et al., *Quantum capacitance and density of states of graphene*, arXiv `1001.4690` and related publication.
- Role: direct capacitance response versus gate-controlled carrier density.
- Limitation: much of the readily accessible evidence is one-dimensional in density rather than a full `(T_e,n)` surface.

### Electronic thermal transport

- Alexander Block et al., *Observation of giant and tunable thermal diffusivity of a Dirac fluid at room temperature*, Nature Nanotechnology 16, 1195-1200 (2021), DOI `10.1038/s41565-021-00957-6`.
- Role: thermal diffusivity controlled by electronic temperature and carrier density.
- Limitation: the paper states that supporting data are available from the corresponding author on reasonable request rather than providing a directly downloadable raw-data table.

- Serap Yigen, *Electronic Thermal Conductivity Measurements in Graphene*, doctoral thesis, Concordia University (2015).
- Role: electronic thermal conductivity versus electron temperature and carrier density.
- Limitation: numerical data appear primarily in figures and thesis analysis; machine-readable source tables require verification.

### Electrical conductivity

- Experimental graphene transport literature contains conductivity as a function of carrier density and temperature, but source compatibility depends strongly on suspension, encapsulation, disorder, and contact geometry.
- A theoretical surface or a digitized literature figure can be used only as a control or exploratory pilot, not as independent experimental falsification.

### Thermal expansion warning

- Duhee Yoon et al., *Negative Thermal Expansion Coefficient of Graphene Measured by Raman Spectroscopy*, Nano Letters 11, 3227-3231 (2011), DOI `10.1021/nl201488g`.
- Later measurements report substantial substrate, contamination, strain, and out-of-plane-coupling effects, including disagreement over sign and temperature dependence.
- Thermal expansion is therefore evidence against the claim that graphene has no hidden variables. It is not yet a suitable fourth channel for the electronic `(T_e,n)` chart.

## Data gates

Before a Pluecker residual may be computed, the campaign requires:

- four response surfaces on one declared two-control chart;
- compatible monolayer graphene class;
- numerical tables or reproducibly extracted values;
- uncertainties or a defensible covariance model;
- at least two-dimensional local support around the evaluation point;
- no silent substitution of theoretical curves for experimental surfaces;
- explicit treatment of shared samples, methods, and nuisance parameters.

## Current verdict

`ONLINE_DATA_EXIST_BUT_FOUR_CHANNEL_CONTRACT_NOT_YET_ASSEMBLED`

Graphene data are available online, but the claimed thirty-sigma result does not presently exist as a verified repository result. The next step is a source-data acquisition campaign on the `(T_e,n)` chart, beginning with heat capacity and electronic thermal transport.
