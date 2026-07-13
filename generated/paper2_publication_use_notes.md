# Paper 2 Dynamic Behavior Bridge

This bridge maps the earlier dynamic-analysis concepts onto the current 15-app evidence package without claiming that the original published RDI tables were regenerated.

## Current Dynamic Coverage

- Total dynamic runs scanned by the runtime audit: 363.
- Stats-eligible runs: 209.
- Local PCAP-available runs: 217.
- Apps with stats-eligible runs: 15.
- Apps with interactive comparison: 12.
- Apps inference-ready: 7.

## Safe Wording

- Use: baseline-relative runtime behavior.
- Use: baseline-relative traffic-shape evidence based on PCAP-derived traffic-shape and TLS-fingerprint features.
- Use: static exposure and runtime behavior are complementary evidence layers.
- Avoid: original RDI-table regeneration claims, payload inspection, malware labeling, causal attribution, or static posture predicting runtime deviation.

## Highest-Signal Metric Shifts

| Metric | Apps | +Delta | p<=0.05 | Large | |Cliff| |
| --- | --- | --- | --- | --- | --- |
| packets_per_second | 9 | 9 | 8 | 9 | 0.929 |
| pcap_bytes | 9 | 9 | 8 | 9 | 0.9 |
| unique_ja3_count | 9 | 9 | 4 | 8 | 0.667 |
| unique_ja4_count | 9 | 8 | 4 | 8 | 0.704 |
