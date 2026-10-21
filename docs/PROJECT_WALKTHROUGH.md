# Explainable Data Anomaly Detection — project walkthrough

## What is this project about?

This is a reproducible monitoring experiment: identify unusual processing observations, compare a machine-learning detector with simple thresholds, and give a human reviewer useful context for investigation. It connects data quality and governance work with an introductory unsupervised machine-learning workflow.

A processing issue could appear as a volume spike, higher error rate, longer response time, or more missing data. An unusual observation is a reason to investigate, not proof that a record is incorrect or fraudulent. The demonstration does not automatically correct, remove, or block data.

**Goal:** determine whether Isolation Forest adds value beyond fixed rules, measured by detection quality and review workload on a held-out test set.

**Conclusion:** rules outperform the model on this deliberately simple synthetic dataset. The practical lesson is to establish a baseline and evaluate added complexity rather than assume machine learning is always better.

## Dataset source and granularity

There is no downloaded public dataset, real bank feed, employer dataset, or customer information. `monitor.py`, function `sample()`, generates independent observations with NumPy's `default_rng`. One row is an illustrative processing-period monitoring observation. No timestamp, source-system identity, entity ID, or genuine business history is included. `daily_volume` is a continuous numeric count proxy, not an integer transaction count.

The exact static inputs are checked in under [`data/`](../data), along with `manifest.json`. Each input has **four numeric features plus one evaluation label**:

| Field | Meaning | Normal generator | Injected anomaly |
|---|---|---|---|
| daily_volume | Simulated processing volume per period | Normal(1000,100), clipped at 1 | Original value × Uniform(2,3) |
| error_rate | Error proportion, 0–1 | Beta(2,100), expected mean 2/102 ≈ 1.96% | Uniform(0.2,0.5) |
| latency_ms | Simulated response time in milliseconds | Normal(200,25), clipped at 1 | Original value + Uniform(180,350) |
| missing_rate | Missing-value proportion, 0–1 | Beta(1,150), expected mean 1/151 ≈ 0.66% | Uniform(0.2,0.5) |
| injected_anomaly | Known synthetic evaluation label | 0 | 1 for a deliberately modified row |

Normal-generator parameters are assumptions chosen for an educational example, not measured industry benchmarks. Rates are stored as proportions: 0.2258 means 22.58%. `row_id` is a sequential test ID added after scoring; it is not a model feature.

| Split | Rows | Seed | Injected anomalies | Purpose |
|---|---:|---:|---:|---|
| train.csv | 1,200 | 11 | 0 | Fit model and derive baseline statistics |
| calibration.csv | 400 | 22 | 0 | Choose score threshold without test labels |
| test.csv | 600 | 33 | 48 | Evaluate on independent held-out examples |
| Total | 2,200 | — | 48 | Three distinct roles |

The test generator selects 48 distinct row positions at random (600 × 8%). Iterating over the selected positions, it rotates through the four features, so exactly 12 anomalies modify each feature. Only one feature is changed per selected row. The remaining 552 rows retain the normal generator's values. These independent random splits do not emulate temporal dependence or seasonality. Normal-only training/calibration is a simplifying assumption.

## Platforms and analytical sequence

Everything runs locally without a paid API or cloud service:

| Component | Tool and purpose |
|---|---|
| Generation | Python / NumPy |
| Validation and transformations | pandas |
| Model and evaluation | scikit-learn IsolationForest and metrics |
| Storage | Static CSV and JSON files; no database |
| Report | Standalone HTML and vanilla JavaScript |
| Hosting | Public portfolio displays a stored results snapshot |

The project does not use Snowflake, Tableau, a vector database, or an LLM. Python computes the model outputs; the browser filters those outputs and computes outcome counts. The deployed page is interactive but is not a live ingestion or inference service.

1. Generate input splits. Validate that all four required features are present, numeric, finite, and nonempty; volume/latency must be nonnegative and both rates within [0,1].
2. Fit `IsolationForest(n_estimators=200, random_state=42, contamination='auto')` on 1,200 training rows. Labels are excluded. No scaler is used; Isolation Forest uses random feature splits rather than Euclidean distance. Its default sample-size setting is retained. Different feature scaling and distributions still warrant testing on a new application.
3. Calculate `-model.score_samples()` on 400 calibration rows. The negative sign means higher scores indicate more unusual behavior. These scores are not anomaly probabilities.
4. Set the threshold to the calibration 98th percentile: **0.5600185939566462**. Flag test records with score ≥ threshold. The custom threshold is used instead of `model.predict()`. `contamination='auto'` does not mean the implementation assumes 8% anomalies when setting this threshold.
5. Apply four independent fixed rules: volume > 1600, errors > 0.10, latency > 350 ms, or missingness > 0.10. These are demonstration thresholds, not regulatory requirements. Any breach produces `rule_flag = 1`.
6. Set `review_flag = model_flag OR rule_flag`. This union is the hybrid detector, not a separate fitted model.
7. Compare each method to the injected labels. Export scores, flags, descriptive explanations, confusion matrices, precision, recall, F1, average precision, and feature mean-shift diagnostics.

## Results and where the numbers come from

Counts below reconcile to the same 600 test rows. TP means an injected anomaly was flagged; FP means a normal-generator row was flagged; FN means an injected anomaly was missed; TN means a normal-generator row was not flagged.

| Detector | TP | FP | FN | TN | Total alerts | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Isolation Forest | 32 | 18 | 16 | 534 | 50 | 64.00% | 66.67% | 0.6531 |
| Fixed rules | 48 | 0 | 0 | 552 | 48 | 100% | 100% | 1.0000 |
| Hybrid | 48 | 18 | 0 | 534 | 66 | 72.73% | 100% | 0.8421 |

- Model precision = TP/(TP+FP) = 32/50 = **64%**. Of every 50 model alerts, 18 are false alarms in this test.
- Model recall = TP/(TP+FN) = 32/48 = **66.67%**. The model misses 16 of the deliberately modified records.
- Model F1 = 2TP/(2TP+FP+FN) = 64/98 = **0.6531**.
- Hybrid precision = 48/66 = **72.73%**; hybrid recall = 48/48 = **100%**.
- Review workload: rules 48/600 = **8%**; model 50/600 = **8.33%**; hybrid 66/600 = **11%**. The hybrid adds 18 false alarms compared with rules alone.
- Calibration false-positive rate = 8/400 = **2%**; test model false-positive rate = 18/552 = **3.26%**. A percentile calibration target does not guarantee an identical rate on fresh observations.
- Model average precision = **0.7468**, calculated by `average_precision_score` over ranked test scores. It summarizes precision weighted by recall increments across score thresholds, not precision at this particular threshold.

`outputs/evaluation.json` stores confusion matrices as `[[TN,FP],[FN,TP]]`, with true classes as rows, predicted classes as columns, and class order `[0,1]`.

## What does “explainable” mean here?

For each feature, calculate absolute robust z:

`abs(record value − training median) / (1.4826 × training MAD)`

MAD is the median absolute deviation from the training median. The code guards zero MAD with 1e-9. `top_deviation` names the feature with the largest absolute robust z; `robust_z` stores that maximum. The record inspector additionally shows the training 5th–95th percentile interval.

For example, **TEST0536** has error_rate ≈ 6.56%, a model score ≈ 0.6465 above the 0.5600 threshold, and no rule breach. Its label is 0, so it is a model false positive even though its error rate is unusual. **TEST0396** has volume ≈ 2751.10 and score ≈ 0.5509: the volume rule flags it, but the model misses it. Inspect those IDs in the report.

These diagnostics help a reviewer form hypotheses. They do **not** explain the model's internal decision, identify causality, or use SHAP. A feature's largest deviation need not be the cause of its model score. Potential follow-ups include checking duplicate loads, validation errors, missing source fields, or processing delays; the dataset cannot verify those root causes.

Mean-shift diagnostics use `abs(test mean − training mean) / training population std`: volume 0.3432, error rate 0.3972, latency 0.1809, missing rate 1.1183. Missing rate shifts the most on this measure. These are descriptive values affected by injected anomalies, not significance tests or evidence of actual production drift.

## Conclusion, value, and limitations

The rules match the deliberately obvious anomaly generator extremely well and are the best detector in this single test. The model neither improves recall nor reduces false alarms relative to those rules. This is a useful analytical conclusion: model complexity must earn its cost.

The portfolio demonstrates clean separation of training/calibration/testing, leakage avoidance, model-versus-rule evaluation, reconciliation of metrics to counts, and a human review interface. It is relevant to data quality and stewardship because it connects monitoring signals with prioritization and investigation.

It does not prove production readiness, real banking performance, fraud detection, financial savings, or a particular employer outcome. Limits include one seed per split, independent synthetic observations, simplistic one-feature anomalies, known normal training data, no temporal validation, and no operating-cost study. Perfect rules performance is limited to this generator and sample.

Next experiments: subtle multivariate anomalies that remain below individual thresholds; multiple seeds and uncertainty intervals; real adjudicated labels; temporal splits and seasonality; threshold selection on a validation set using reviewer capacity and error costs; production input contracts and monitored retraining. These are proposed extensions, not implemented capabilities.

## Reproduce and refresh the report

After installing `requirements.txt`:

```shell
python export_datasets.py
python monitor.py
python build_report.py
python -m unittest discover -s tests -v
node --test tests/dashboard.test.cjs
```

Open `report.html`. Run these commands from the repository root. `monitor.py` regenerates scored CSV/JSON; `build_report.py` refreshes the report from those outputs. Rebuilding locally does not automatically republish the portfolio. Browser downloads contain all 600 scored rows, irrespective of active filters.

## Interview explanation

“I built a synthetic pipeline-monitoring benchmark to compare Isolation Forest with simple rules. I used four operational measures and separated training, threshold calibration, and testing to avoid leakage. The model found 32 of 48 injected anomalies and raised 18 false alarms. Rules performed better because the injected cases were obvious. I built a record explorer showing false positives, missed anomalies, and deviations from the training baseline. My main conclusion was to validate a simple baseline first and use human review rather than treat model alerts as confirmed errors.”

Independent learning work developed with AI assistance. Explain the implementation and limitations accurately; do not describe synthetic results as employment achievements.
