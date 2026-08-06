# G03 Experimental Graphene Acquisition Plan

## Objective

Convert online graphene literature into auditable numerical response surfaces without computing a Pluecker residual prematurely.

The frozen target chart is

\[
(T_e,n),
\]

with electronic temperature and carrier density as the two controls.

## Acquisition priority

### Priority 1: Same-device charge and heat transport

Source: Majumdar et al. (2025), DOI `10.1038/s41567-025-02972-z`.

Target channels:

- electrical conductivity;
- electronic thermal conductivity.

Repository record: NIMS MDR `6f293ba2-7f08-417f-a717-a8421b2624b7`.

Required audit:

1. Pin accepted-manuscript and supplementary-file hashes.
2. Identify every figure or table containing temperature and density dependence.
3. Record device identifier, geometry, mobility, contacts, magnetic field, and temperature definition.
4. Determine whether numerical tables exist inside the supplement.
5. If digitization is necessary, freeze axis calibration and extraction covariance before fitting.
6. Treat the two channels as sharing device-level covariance.

### Priority 2: Electronic heat capacity

Source: Aamir et al. (2021), DOI `10.1021/acs.nanolett.1c01553`.

Target channel: electronic heat capacity.

Required audit:

1. Pin `nl1c01553_si_001.pdf` and its hash.
2. Separate measured heat capacity from device-background subtraction and theoretical comparison curves.
3. Recover electronic-temperature and carrier-density coordinates.
4. Preserve reported uncertainty and calibration terms.
5. Reject any plot that cannot support local two-dimensional gradients.

### Priority 3: Electronic thermal diffusivity

Source: Block et al. (2021), DOI `10.1038/s41565-021-00957-6`.

Target channel: electronic thermal diffusivity.

Required audit:

1. Request the underlying data from the corresponding author where possible.
2. Keep author-supplied values distinct from digitized values.
3. Record hydrodynamic versus diffusive regime labels.
4. Do not merge regimes into one smooth surface unless a frozen physical model justifies it.

### Priority 4: Quantum capacitance or replacement channel

Current capacitance sources provide strong density dependence but lack a verified temperature-density surface.

Allowed resolutions:

- find temperature-resolved quantum-capacitance measurements on compatible monolayer graphene;
- obtain author data with explicit temperature sweeps;
- replace quantum capacitance with another independently measured response channel that has full `(T_e,n)` support.

A one-dimensional density curve may be used as an anchor or model check, but not as a two-dimensional experimental surface.

## Digitization contract

Every digitized dataset must include:

- source DOI and file hash;
- figure, panel, and curve identifier;
- pixel-to-axis calibration points;
- axis scale and units;
- extracted coordinates and values;
- point-extraction uncertainty;
- axis-calibration uncertainty;
- curve-overlap or ambiguity flags;
- digitizer version and deterministic settings;
- an untouched image crop for independent verification.

Digitization uncertainty must enter the covariance model. It may not be quietly omitted because the curve looked crisp on a large monitor.

## Gate before residual

The experimental residual remains forbidden until all of the following are true:

```text
four response channels                           READY
local support in both T_e and n                  READY
compatible material and device classes          READY
reported or reconstructed covariance             READY
source and digitization manifests frozen         READY
pairwise independence/shared covariance typed    READY
```

Until then, the allowed result is `INCONCLUSIVE_DATA_COVERAGE` or a narrower acquisition status.
