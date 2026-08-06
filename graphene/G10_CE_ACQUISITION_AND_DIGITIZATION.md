# G10 Electronic Heat-Capacity Acquisition and Coverage Audit

## Objective

Test whether the measured electronic heat capacity from Aamir et al. can replace the missing fourth response channel in the frozen graphene chart `(T_e, n)`.

The source is:

- DOI `10.1021/acs.nanolett.1c01553`;
- author preprint `arXiv:2007.14280`;
- supporting file `nl1c01553_si_001.pdf`;
- frozen SHA-256 `f3665ddf503d23400452d10366a39e783ab58ceabe5c80b04a03f2c375c7ef05`.

## Measurement identity

The experiment determines

\[
C_e=G_{th}\tau_e,
\qquad
c=C_e/A.
\]

Therefore, digitizing only the final heat-capacity curve is insufficient for a full uncertainty audit. The preferred acquisition is the measured `G_th`, `tau_e`, calibration, normalization, and covariance data from which `C_e` was produced.

## Published measured coverage

### Density-resolved measurements

The paper reports `G_th(n)`, `tau_e(n)`, and `c(n)` at:

```text
15.5 K
60.0 K
100.0 K
```

These are the measured two-control candidates.

### Temperature-resolved measurement

The measured `c(T_e)` curve extends approximately from 15 K to 195 K, but it is evaluated at one fixed density:

```text
n = -0.38 x 10^12 cm^-2
```

It contributes temperature support but not local density support.

## Common-domain decision

The current three-channel transport base requires temperatures from 110 K to 260 K.

The density-resolved heat-capacity curves stop at 100 K:

\[
\{15.5,60,100\}\cap[110,260]=\varnothing.
\]

The fixed-density temperature curve overlaps continuously on `[110,195] K`, but one density cannot define a two-dimensional response surface. Consequently:

```text
status                          INCONCLUSIVE_TWO_DIMENSIONAL_COMMON_DOMAIN
heat-capacity replacement       NOT READY
four-channel fit                FORBIDDEN
Pluecker significance           NOT COMPUTED
```

## Figure typing

- `Fig_3A`: measured `G_th(n)` input.
- `Fig_3B`: measured `tau_e(n)` input.
- `Fig_4A`: measured `c(T_e)` at fixed density.
- `Fig_4B`: measured `c(n)` at three temperatures.
- `Fig_S18`: measured extended cross-check for the main device.
- `Fig_S20`: second-device exploratory estimate; excluded because `tau_e` is not normalized.
- `Fig_S22`: numerical theory surface; excluded from experimental evidence.

## Required author data

The highest-priority request is:

1. numerical `G_th(T_e,n)`, `tau_e(T_e,n)`, and `c(T_e,n)` arrays;
2. pointwise uncertainty components;
3. covariance between `G_th` and `tau_e`, or fit-level outputs sufficient to reconstruct it;
4. gate-voltage to density calibration and uncertainty;
5. contact-resistance calibration and uncertainty;
6. ground-state `tau_e` normalization corrections;
7. device area and device/sweep identifiers;
8. any additional density sweeps between 110 K and 195 K.

## Digitization rule

Digitization may proceed only after the source hash is verified. Every extracted point must retain figure, panel, curve, axis calibration, pixel uncertainty, reported measurement uncertainty, and measured-versus-theory classification.

Digitization cannot manufacture the missing temperature-density support. Without additional density sweeps above 100 K, the result remains inconclusive even if every plotted point is recovered perfectly.

## Next stage

`G11_DE_BLOCK_COVERAGE_AND_AUTHOR_DATA_AUDIT`

The Block et al. electronic thermal-diffusivity source is now the fallback replacement candidate.
