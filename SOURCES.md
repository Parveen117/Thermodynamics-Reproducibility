# Authoritative Sources

## IAPWS-95 control source

International Association for the Properties of Water and Steam, **R6-95(2018): Revised Release on the IAPWS Formulation 1995 for the Thermodynamic Properties of Ordinary Water Substance for General and Scientific Use**.

- Official release page: https://www.iapws.org/relguide/IAPWS-95.html
- Official document: https://iapws.org/documents/release/IAPWS-95
- Role in this repository: smooth equation-of-state and derivative-pipeline control.
- Claim boundary: IAPWS-95 is internally generated from one Helmholtz formulation and is not an independent six-channel experimental falsification dataset.

## NIST ThermoML experimental source

National Institute of Standards and Technology, Thermodynamics Research Center, **ThermoML Archive**.

- Archive page: https://www.nist.gov/mml/acmd/trc/thermoml/thermoml-archive
- Standard description: https://www.nist.gov/mml/acmd/trc/thermoml
- Dataset DOI: 10.18434/mds2-2422
- Pinned snapshot: `ThermoML.v2020-09-30.tgz`
- Pinned snapshot SHA-256: `231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2`
- Snapshot coverage: ThermoML entries published through calendar year 2019.
- Role in this repository: provenance-rich experimental property records, including methods, constraints, and uncertainty descriptions where supplied.
- Claim boundary: NIST states that ThermoML values and metadata are checked for completeness and representation accuracy but are not critically evaluated. Every real-data verdict therefore preserves source sensitivity and uncertainty-model boundaries.

## Recognition sources

- Paper: *Geometric Completion of Thermodynamic Response: From the T-V-S-P Compass to Recognition Kernels, Cut-Flow Jets, and Action-Lifted Spacetime Field Equations*, rigorous revision draft dated 4 August 2026.
- Framework repository: `Parveen117/Recognition-Kernel-Framework`.
- Relevant theorem capsules:
  - `theorum/thermodynamics/01_response_tetrad_and_flat_closure.md`
  - `theorum/thermodynamics/03_canonical_response_cost_barrier.md`
  - `theorum/thermodynamics/05_onsager_compass_and_constitutive_no_go.md`
  - `theorum/thermodynamics/06_onsager_hodge_no_leakage.md`
  - `theorum/thermodynamics/10_thermodynamic_cut_square_response_decomposition.md`

## Citation discipline

Downloaded records retain original bibliographic identifiers and the ThermoML citation requested by NIST. Raw source files remain immutable; transformations, manifests, revisions, and content hashes are recorded separately.
