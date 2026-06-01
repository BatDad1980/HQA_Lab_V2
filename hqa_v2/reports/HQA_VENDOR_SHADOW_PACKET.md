# HQA Vendor Shadow Packet Report

## Purpose

This report records generation of the sample vendor shadow-mode interface packet.

## Output

- Packet directory: `X:\HQA_LAB_V1\hqa_v2\outputs\vendor_shadow_packet_v1`
- JSON payloads: `5`
- Manifest: `MANIFEST_SHA256.txt`
- README: `README.md`

## Files

| File | SHA-256 |
|---|---|
| `01_topology_snapshot.json` | `737d038260c491eff35eec47e6a5e10a16399d1201e00a4c202565c0297d7d86` |
| `02_syndrome_record.json` | `3bb5bbe5395f72bec619f9995ca590df53c86da54423cde81c12a11d9a0faa7b` |
| `03_quarantine_decision.json` | `7a4799228a53382564318ef4bc5070278c9f64e519168982bbb3a9b499359530` |
| `04_reroute_proposal.json` | `7149a56508e63792e9a4499a894b02b9e4cf6caa7d71fbf4b93db85da9ac75d3` |
| `05_hal_manifest.json` | `a26bebcbdc41bd6f6a96c7149f2f8e38251724d492a90d4566bce138b1bcdd9d` |
| `MANIFEST_SHA256.txt` | `d954f5f21fe305a3349423274858c1859b6707fe44f81a8d1d09c5e92063d126` |
| `README.md` | `66cc868e46d8a5fba0918716ec5ca531e58deaade3727def2e9a2afa39e68f0b` |

## Boundary

The packet contains example shadow-mode payloads only. It does not validate physical quantum hardware, submit live jobs, or grant HQA hardware control authority.
