# HQA HAL Loopback Boundary Contract V0

## Purpose

This report records a reported mock cryostat loopback transaction and defines the clean-lane boundary around it.

The important result is not that HQA can touch hardware. The important result is that HQA can treat a loopback ACK as transport evidence while refusing to promote it into real actuator authority.

## Reported Transaction

- Source class: `adjacent_lane_reported_mock_cryostat_transaction`
- Execution mode: `reported_loopback_replay_no_socket`
- Clean-lane network calls: `0`
- Hardware authority: `False`
- Real actuator authority: `False`

| Field | Value |
|---|---|
| Host | `127.0.0.1` |
| Port | `5000` |
| Server class | `MockCryostatHandler` |
| Controller mode reported | `physical` |
| Command | `SET:CRYO:PUMP:Q00 ON` |
| ACK | `ACK_OK: PUMPS_ENGAGED` |
| Clean-lane mode | `MOCK_LOOPBACK_ACK_ONLY` |
| Decision | `ACCEPT_AS_MOCK_TRANSPORT_EVIDENCE` |
| Transaction hash | `6a31b17e5f64d0868b280cf250c20dddb348f426bce6a3f8195c1522518665fd` |

## Allowed Interpretation

- The controller can serialize a cryostat command string.
- A mock loopback server can receive the command and return an ACK.
- The controller can update internal state after receiving the ACK.

## Disallowed Interpretation

- The system has validated real cryostat hardware control.
- The system may dispatch to non-loopback endpoints.
- A network ACK can override the HAL safety governor.
- Mock physical mode grants real actuator authority.

## Boundary

This clean-lane replay does not open sockets, submit network traffic, activate hardware, or grant physical HAL authority.
