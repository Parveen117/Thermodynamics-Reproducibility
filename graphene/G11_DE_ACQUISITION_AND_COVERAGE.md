# G11 Electronic Thermal-Diffusivity Acquisition and State-Variable Audit

## Objective

Test whether Block et al. (2021) can supply the fourth experimental response channel after the heat-capacity replacement failed its two-dimensional common-domain gate.

Source:

- DOI `10.1038/s41565-021-00957-6`;
- supplement `41565_2021_957_MOESM1_ESM.pdf`;
- frozen SHA-256 `b60cec3dcec1468d9885f00bfa53912f9259a755992c7f247234aca8bb6d3b0b`;
- 21 supplement pages;
- supporting data available from the corresponding author on reasonable request.

## What the experiment directly measures

The primary observable is the interacting thermoelectric current

\[
\Delta I_{TE}(\Delta x,\Delta t).
\]

The experiment extracts spatial spreading through either the second moment

\[
\langle \Delta x^2\rangle
\]

or Gaussian widths `sigma_x^2` and `sigma_y^2`.

The hydrodynamic diffusivity estimate is then constructed from the excess time-zero width:

\[
D=\frac{w_{min}-w_{focus}}{2\Delta t_{IRF}}.
\]

Thus, the public paper does not provide a direct dense measured table of `D(T_e,n)`. The measured objects are spatiotemporal maps and fitted widths, followed by a derived diffusivity estimate.

## State-variable distinction

The Majumdar base channels use an equilibrium sample-temperature coordinate spanning approximately 110–260 K.

Block et al. perform the optical experiment at fixed lattice temperature

\[
T_l=300\ \mathrm{K},
\]

while varying a transient peak electron temperature inferred from laser power:

\[
T_e=\sqrt{T_0^2+bP}.
\]

Carrier density is separately inferred from gate voltage through the hBN capacitance model.

Therefore:

```text
equilibrium sample temperature     != transient peak electron temperature
```

The two quantities cannot be merged merely because both are denoted by a temperature symbol.

## Figure typing

### Measured or experimentally fitted

- `Fig. 2e`: measured spatial spreading at three Fermi energies, compared with simulations using mobility-derived diffusivity.
- `Fig. 3e-f`: measured Gaussian widths versus optical power and gate voltage.
- `Supplementary Fig. 5`: full measured width dataset versus power and gate voltage.
- `Supplementary Fig. 9`: calibration connecting optical power to peak electron temperature.

### Calculated or model-dependent

- `Fig. 3g-h`: Boltzmann-calculated diffusivity surfaces.
- `Extended Data Fig. 1`: electrical mobility and corresponding calculated diffusivity, including extrapolation beyond part of the directly measured Fermi-energy range.

Calculated surfaces are excluded from the experimental response channel.

## Coverage verdict

The source has genuine two-control experimental variation in optical power and gate voltage. However, it does not currently pass the replacement gate because:

1. the candidate temperature coordinate is not aligned with the base chart;
2. the raw `Delta I_TE` maps and fit outputs are not publicly machine-readable;
3. no pointwise measured `D(T_e,n)` table with uncertainty is publicly verified;
4. the `P -> T_e` and gate-voltage-to-density calibration covariance is not frozen;
5. focus-width and instrument-response uncertainty must propagate into `D`;
6. the complete published diffusivity map is theoretical rather than measured.

Result:

```text
status                  INCONCLUSIVE_STATE_VARIABLE_ALIGNMENT_AND_MEASURED_SURFACE
replacement ready       false
four-channel fit        forbidden
Pluecker significance   not computed
```

## Required author data

The highest-priority request is for:

1. raw `Delta I_TE(Delta x,Delta t)` maps for every power and gate condition used in Figs. 2 and 3;
2. Gaussian and second-moment fit outputs with covariance;
3. the optical-power-to-peak-electron-temperature calibration parameter `b` and uncertainty;
4. gate-voltage-to-density calibration and uncertainty;
5. instrument-response time and covariance;
6. measured focus widths and covariance;
7. pointwise diffusivity estimates with labels distinguishing measured, mobility-derived, simulated, and Boltzmann-calculated values;
8. device, sweep, junction-polarity, and transport-regime identifiers.

## Consequence for the programme

The heat-capacity route failed because its density-resolved data stop below the base temperature range. The diffusivity route fails for a deeper reason: its temperature is a different physical coordinate.

The next stage must therefore audit or redesign the chart itself rather than searching indefinitely for a fourth observable while quietly changing what `T` means.

## Next stage

`G12_TEMPERATURE_COORDINATE_REDESIGN`
