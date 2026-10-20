import unittest
import numpy as np
from monitor import sample,validate,benchmark

class MonitorTests(unittest.TestCase):
    def test_invalid_values(self):
        df=sample(4,1);df.loc[0,'error_rate']=1.1
        with self.assertRaises(ValueError):validate(df)
        df=sample(4,1);df.loc[0,'latency_ms']=np.nan
        with self.assertRaises(ValueError):validate(df)
    def test_labels_never_features(self):
        df=sample(20,1,.1)
        self.assertNotIn('injected_anomaly',validate(df).columns)
        self.assertEqual(df.injected_anomaly.sum(),2)
    def test_benchmark_counts(self):
        rows,s=benchmark()
        self.assertEqual(sum(sum(x) for x in s['model']['confusion_matrix']),s['test_rows'])
        self.assertEqual(len(s['flagged_rows']),int(rows.review_flag.sum()))
        self.assertTrue((rows.review_flag>=rows.model_flag).all())
if __name__=='__main__':unittest.main()
