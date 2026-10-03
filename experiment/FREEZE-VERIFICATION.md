# Freeze verification

The freeze files are preserved as issued. A freeze records the source and design at a specific point; later amendments are listed separately rather than silently changing the original hashes.

## R7 source-access sample

`FREEZE-R7-source-access.txt` records the initial collector hash `071f7e0e60768ed6bc7600f780c48fbfcf6eaf4494d2fa4e4d6b2ec46b7bbf29`. The subsequent `AMENDMENT-R7-power-target.md` explicitly supersedes that collector hash with `02511c96e161b0a4e7ab2063915f8a951764512ba586f75d2d5a9602bb7584b6`, which matches the released `r7_source_access.py`. The original frozen collector source is not present in the available repository history, so the initial source snapshot cannot be independently reconstructed from this release. The amended source hash is verifiable.

The R7 freeze's `harness.py` hash, `8624610c7e7579daee0b25b4c6be61f807e313c6c00e5488678c12bd713960dd`, matches the released file.

## Balanced and equivalence samples

The balanced and equivalence freeze files both record `harness.py` hash `78b5b8579d0fcd9d669e3a5601e1d5ec7e834f35947ce5e5652d84097033fad5`. That exact historical version is preserved byte-for-byte at
`experiment/frozen/harness-balanced-equivalence.py`; verify it with:

```sh
shasum -a 256 experiment/frozen/harness-balanced-equivalence.py
```

The current harness was subsequently extended for R7 and has a different hash. Its release hash, along with the amended R7 collector hash, is listed in `RELEASE-CODE-CHECKSUMS.txt`. Verify current files with `shasum -a 256 -c experiment/RELEASE-CODE-CHECKSUMS.txt`.
