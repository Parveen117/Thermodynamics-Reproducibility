# T01D Fit Contract Note

The machine-readable fit contract remains byte-for-byte frozen in `T01D_FIT_CONTRACT.json` because its canonical SHA-256 is embedded in the final result certificate.

Its `input_manifest` field records manifest v1, the manifest current when the fit contract was frozen. After manifest v1 returned `INCONCLUSIVE_FIT_GEOMETRY` without computing any Pluecker residual, manifest v2 replaced two weak source slots. The numerical fit family, evaluation point, coordinate scales, bandwidths, uncertainty rule, geometry gates, and five-sigma decision threshold remained unchanged.

The manifest transition is documented in:

- `T01D_MANIFEST_REVISION_01.json`
- `archive/T01D_CANDIDATE_MANIFEST_V1_INCONCLUSIVE.json`
- `T01D_CANDIDATE_MANIFEST_V2.json`

The frozen fit-contract canonical SHA-256 used by the final result is:

```text
07530b5da5cfb6db8e9f863e31e37318e490669471ffb7fd742a0e2a51b2dcba
```
