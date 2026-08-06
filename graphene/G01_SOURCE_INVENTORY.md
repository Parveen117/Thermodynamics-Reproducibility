# G01 Graphene Online-Data Inventory

## Scope

This inventory asks whether public online sources can support a four-channel Pluecker experiment on a frozen two-control graphene state chart.

The preferred chart is

\[
(T_e,n),
\]

with electronic temperature and carrier density as controls.

A paper being online is not sufficient. A source must also provide usable coordinate coverage, units, uncertainty, material identity, and enough numerical information to reconstruct local gradients without inventing points from a theory curve.

## Current source map

### Electronic heat capacity

**Aamir et al. (2021), DOI 10.1021/acs.nanolett.1c01553**

- Direct graphene electronic calorimetry.
- Reports electronic heat capacities below `1e-19 J/K`.
- Supporting information is publicly available as `nl1c01553_si_001.pdf`.
- Public machine-readable two-dimensional tables have not been verified.
- Role: primary `C_e(T_e,n)` acquisition candidate.

### Quantum capacitance / compressibility

**Xia et al. (2009), DOI 10.1038/nnano.2009.177**

- Direct graphene quantum-capacitance measurement.
- Publicly visible coverage is mainly gate potential or carrier density.
- A temperature-resolved two-dimensional surface has not yet been verified.

**Droescher et al. (2010), arXiv:1001.4690**

- Independent quantum-capacitance and density-of-states source.
- Also appears primarily one-dimensional in density unless additional sweeps are recovered.

The missing temperature dimension remains the main bottleneck for the fourth channel.

### Electronic thermal diffusivity

**Block et al. (2021), DOI 10.1038/s41565-021-00957-6**

- hBN-encapsulated monolayer graphene.
- Explicitly studies response versus electronic temperature and carrier density.
- Strongest chart-matched diffusivity source.
- Underlying data are available from the corresponding author on reasonable request.
- Role: author-data request or reproducible digitization with a declared extraction covariance.

### Electrical and electronic thermal conductivity

**Majumdar et al. (2025), DOI 10.1038/s41567-025-02972-z**

- Studies charge and heat transport in ultraclean graphene near the Dirac point.
- Provides electrical conductivity and electronic thermal conductivity within one compatible device programme.
- NIMS Materials Data Repository record `6f293ba2-7f08-417f-a717-a8421b2624b7` hosts the accepted manuscript and supplementary information.
- Public machine-readable numerical tables have not yet been verified.
- Role: highest-priority same-device two-channel acquisition route.

A same-device pair is scientifically valuable for calibration and covariance modelling. It is not automatically independent evidence for all six Pluecker brackets.

### Alternative electronic thermal conductivity

**Yigen (2015), Concordia University thesis**

- Suspended graphene transistors.
- Reports electronic thermal conductivity versus electron temperature and carrier density.
- Public thesis PDF exists, but machine-readable tables are not yet verified.
- Mixing suspended devices with encapsulated-device data requires an explicit sample-compatibility model.

### Lattice thermal expansion

**Yoon et al. (2011), DOI 10.1021/nl201488g**

- Raman-derived thermal expansion for substrate-supported graphene.
- Valuable as a warning about substrate strain and lattice/electronic temperature separation.
- Excluded from the current electronic `(T_e,n)` channel set.

## ThermoML result

ThermoML searches for graphene are dominated by graphene oxide, reduced graphene oxide, composites, aerogels, and phase-change hybrids. These records do not form a pristine monolayer four-surface archive.

Status:

```text
ThermoML pristine graphene route                 INSUFFICIENT
same-device conductivity pair                    AVAILABLE FOR ACQUISITION
heat-capacity surface                            PDF/SI AVAILABLE
thermal-diffusivity surface                      AUTHOR DATA OR DIGITIZATION
quantum-capacitance temperature surface          UNRESOLVED
four-channel machine-readable contract           NOT MET
```

## Acquisition rules

1. Freeze the material class and state chart before digitization.
2. Hash every downloaded source and record its licence or access terms.
3. Preserve reported values separately from digitized values.
4. Attach axis-calibration and point-extraction uncertainty to every digitized datum.
5. Do not use a model-generated curve as experimental raw data.
6. Do not compute a graphene Pluecker residual before four compatible two-dimensional response surfaces pass the coverage gate.
7. Same-device channels must carry their shared covariance rather than being labelled independent by convenience.
