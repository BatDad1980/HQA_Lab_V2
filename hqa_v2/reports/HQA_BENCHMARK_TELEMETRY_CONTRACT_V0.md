# HQA Benchmark Telemetry Contract V0

## Purpose

This report defines the clean boundary for CLI benchmark and telemetry-server expansion work.

Telemetry may observe, record, and hash. Telemetry may not authorize or actuate.

## Commands

| Command | Allowed | Forbidden |
|---|---|---|
| `run-telemetry` | start local read-only telemetry service, emit bounded status records | store credentials, dispatch commands, call HAL, submit provider jobs |
| `benchmark-qec` | run local repetition-code benchmark, write markdown report, write hashed telemetry records | claim production QEC, touch live backend, authorize intervention |

## Benchmark Fixture Records

| Benchmark | Distance | Rounds | Shots | Logical Failure Proxy | Hash Prefix |
|---|---:|---:|---:|---:|---|
| `QEC-REP-D3` | `3` | `3` | `4096` | `0.0875` | `b6a0baeff964` |
| `QEC-REP-D5` | `5` | `5` | `4096` | `0.0312` | `bf2dca11b56b` |
| `QEC-REP-D7` | `7` | `7` | `4096` | `0.0109` | `557c7f39ed94` |

## Permission Boundary

- Observe: `True`
- Record: `True`
- Hash: `True`
- Authorize: `False`
- Actuate: `False`
- Store credentials: `False`
- Remote command dispatch: `False`
- HAL authority: `False`

## Boundary

Benchmark Telemetry Contract V0 allows local observation, recording, hashing, and report writing only. It does not authorize hardware action, store credentials, expose remote command dispatch, submit provider jobs, or grant HAL authority.
