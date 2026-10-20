# Interview walkthrough: Explainable Data Anomaly Detection

## 60-second explanation

“This is an independent portfolio project connecting my data stewardship experience with hands-on Python analysis. The question is: whether an anomaly model improves on understandable rules? I used synthetic data so the work is reproducible and shareable. On 600 synthetic held-out rows (48 injected anomalies), Isolation Forest precision = 0.64, recall = 0.6667, F1 = 0.6531. Rules precision/recall = 1.0/1.0 on these obvious injected cases. Hybrid recall = 1.0, precision = 0.7273. These are toy-data results, not fraud-detection performance. I would validate the assumptions and outputs with a business owner before applying the method to real data.”

## Demonstrate it in five minutes

1. Show the business question and data dictionary in the README.
2. Open `report.html`; use the filter and explain the denominator or model threshold.
3. Trace one row through the executable Python code into the CSV/JSON output.
4. Run the tests and explain one edge case that could change the conclusion.
5. Discuss a limitation below and propose a measured next experiment.

## Architecture and tradeoffs

Generate independent training, calibration, and test sets using seeds 11, 22, and 33. Fit 200 Isolation Forest trees on 1,200 normal training rows. Calibrate the review threshold at the 98th percentile of negative score_samples on 400 normal calibration rows; do not use test labels for selection. Inject labeled anomalies into 8% of 600 held-out test rows. Labels never enter the feature matrix.

Compare model flags with fixed business-rule flags and their union. Report precision, recall, F1, confusion matrices (row=true, column=prediction, labels [normal, anomaly]), and average precision. Explanations use the largest absolute robust z score relative to training median/MAD, not a causal or model-specific attribution. Drift diagnostics are absolute standardized mean shifts, not statistical significance tests.

## What I would change for production

Add source contracts, versioned datasets, access control, approved retention, source-to-report lineage, observed business SLAs, independent review, and monitoring for changing inputs. Current implementation stays local and has no enterprise deployment. SQL examples in analytics projects can be adapted to a governed Snowflake/dbt pipeline; they are not deployed Snowflake integrations.

## Strong questions to be ready for

- How did you prevent bad keys or missing values from changing the result?
- What is the denominator of each published metric?
- Which design choice is policy rather than an empirical finding?
- Which result would make you choose a simpler approach?
- What did you verify locally, and what remains untested?

## Honest resume wording after reviewing the code

“Implemented and evaluated an independent explainable data anomaly detection project using Python, reproducible synthetic data, automated validation, and an interactive results report.”

## Limits

Rules match this simple anomaly generator very well; that is why they outperform the model. Add subtle multivariate anomalies, real review labels, multiple seeds, time-ordered splits, and cost-sensitive threshold selection before drawing broader conclusions. Normal-only training/calibration is an educational assumption. Data is synthetic operational telemetry, not real banking transactions. No autonomous enforcement or production integration is implemented.
