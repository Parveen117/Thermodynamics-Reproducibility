# Final PR Summary

## Primary experimental result

`T01D_THERMOML_EXPERIMENTAL` completed with status:

```text
NOT_FALSIFIED
```

At `T = 318.15 K` and `P = 12.5 MPa`, the independently reconstructed Pluecker residual was `-1.8654273205408826e-06` with standard error `8.08728994960218e-06`, giving `0.23066161002829436 sigma` against a frozen rejection threshold of `5 sigma`.

A deterministic 200,000-draw bootstrap gave standard error `8.14856878214715e-06` and score `0.22892698956261887 sigma`; zero remained inside the 95%, 99%, and 99.9% bootstrap intervals.

## Independence contract

- twelve source slots;
- twelve unique ThermoML publications;
- no publication reused across bracket slots;
- no common four-channel surface used to manufacture all six brackets.

## Audit boundaries

- The strict caloric-mechanical tetrad was `INCONCLUSIVE_DATA_COVERAGE` in the pinned archive.
- The completed test uses the paper's broader any-four-channel theorem with density, sound speed, isobaric heat capacity, and viscosity.
- Manifest v1 was inconclusive before any residual was computed. Manifest v2 replaced two weak source slots using only pre-residual fit geometry while preserving the frozen fit contract.
- `NOT_FALSIFIED` is not proof of unique physical selection.

See `results/T01D_FINAL_CERTIFICATE.json` and `results/T01D_RESULT.md`.
