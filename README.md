# Explainable Data Anomaly Detection

An unsupervised model benchmark that separates training, threshold calibration, and held-out testing, compares simple rules, and produces a review queue with transparent deviation diagnostics.

**[Open the interactive demo](https://pratikkumar-data-ai-portfolio.woollydog11.chatgpt.site/demos/explainable-anomaly-monitor.html)** · [Portfolio](https://pratikkumar-data-ai-portfolio.woollydog11.chatgpt.site) · [LinkedIn](https://www.linkedin.com/in/pratikkumarchaudhari/)

## Business question

Does an unsupervised anomaly model add value beyond explicit rules, and how can a reviewer inspect its flags?

## Run locally — no paid APIs or cloud account

Requires Python 3.11 or 3.12. In Windows PowerShell:

```powershell
git clone https://github.com/Pratikkumarchaudhari/explainable-anomaly-monitor.git
cd explainable-anomaly-monitor
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe monitor.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
Start-Process report.html
```

On macOS/Linux use `python3 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.txt`, then `.venv/bin/python monitor.py`. Open `report.html` in your browser.

`report.html` is a checked-in snapshot with all 600 scored test records, detector/outcome filters, a training-baseline inspector, and a CSV download. Running `monitor.py` regenerates CSV/JSON outputs. Run `python build_report.py` afterward to refresh the HTML; local regeneration does not automatically republish the portfolio. No server, account, or API key is required. Normal internet and electricity use still apply.

## Reproduced sample findings

On 600 synthetic held-out rows (48 injected anomalies), Isolation Forest precision = 0.64, recall = 0.6667, F1 = 0.6531. Rules precision/recall = 1.0/1.0 on these obvious injected cases. Hybrid recall = 1.0, precision = 0.7273. These are toy-data results, not fraud-detection performance.

## How it works

Generate independent training, calibration, and test sets using seeds 11, 22, and 33. Fit 200 Isolation Forest trees on 1,200 normal training rows. Calibrate the review threshold at the 98th percentile of negative score_samples on 400 normal calibration rows; do not use test labels for selection. Inject labeled anomalies into 8% of 600 held-out test rows. Labels never enter the feature matrix.

Compare model flags with fixed business-rule flags and their union. Report precision, recall, F1, confusion matrices (row=true, column=prediction, labels [normal, anomaly]), and average precision. Explanations use the largest absolute robust z score relative to training median/MAD, not a causal or model-specific attribution. Drift diagnostics are absolute standardized mean shifts, not statistical significance tests.

## Repository guide

| Path | Purpose |
|---|---|
| `monitor.py` | Executable analysis pipeline |
| `outputs/` | Reproducible sample metrics and review outputs |
| `tests/` | Meaningful input, reconciliation, and behavior checks |
| `report.html` | Standalone interactive sample report |
| `docs/INTERVIEW_GUIDE.md` | Walkthrough, decisions, limitations, resume wording |
| `.github/workflows/checks.yml` | Dependency install, unit checks, and sample execution |

## Data dictionary

daily_volume: synthetic record count; error_rate and missing_rate: proportions [0,1]; latency_ms: synthetic service latency; injected_anomaly: evaluation-only label; anomaly_score: negative Isolation Forest score_samples (larger is more unusual); top_deviation/robust_z: descriptive training-relative diagnostics.

## Scope and limitations

Rules match this simple anomaly generator very well; that is why they outperform the model. Add subtle multivariate anomalies, real review labels, multiple seeds, time-ordered splits, and cost-sensitive threshold selection before drawing broader conclusions. Normal-only training/calibration is an educational assumption. Data is synthetic operational telemetry, not real banking transactions. No autonomous enforcement or production integration is implemented.

Independent portfolio work developed with AI assistance. Contains no employer records, internal procedures, credentials, or confidential material. Synthetic benchmark results must not be presented as employer outcomes. Review and understand the implementation before representing it in an interview. MIT license covers this original code and synthetic data; separately imported source data retains its own terms.


## Detailed project explanation and static datasets

Read [PROJECT_WALKTHROUGH.md](docs/PROJECT_WALKTHROUGH.md) for the purpose, source, field-level generator, split strategy, rules, calculations, worked examples, conclusion, and interview explanation. All **2,200 synthetic input rows** are available in [data/](data), with split seeds and provenance in [manifest.json](data/manifest.json).

To regenerate inputs and the interactive report after dependency setup:

```shell
python export_datasets.py
python monitor.py
python build_report.py
python -m unittest discover -s tests -v
node --test tests/dashboard.test.cjs
```

The Node test command requires Node.js and checks dashboard outcome counts and filtering against the stored Python results. It is not needed just to open the report. The deployed report is an interactive results snapshot, not a live production service.
