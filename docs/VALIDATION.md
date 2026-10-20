# Validation

Executed in Python 3.12 in the portfolio build workspace. Dependency versions are recorded in requirements.txt.

- `monitor.py` completed and wrote the checked-in sample outputs.
- Unit tests passed: 3.
- Sample result: On 600 synthetic held-out rows (48 injected anomalies), Isolation Forest precision = 0.64, recall = 0.6667, F1 = 0.6531. Rules precision/recall = 1.0/1.0 on these obvious injected cases. Hybrid recall = 1.0, precision = 0.7273. These are toy-data results, not fraud-detection performance.
- Static HTML report includes filters and uses the same saved sample data.
- Browser interaction and Windows commands were not executed in this workspace.
- GitHub Actions has been configured; its remote run is not claimed here.

This validates the sample computation, not external source accuracy or production readiness.
