import tempfile
import unittest
from pathlib import Path
import pandas as pd
from export_datasets import export
from monitor import sample, benchmark, FEATURES

class ExportTests(unittest.TestCase):
    def test_exported_inputs_reproduce_benchmark(self):
        with tempfile.TemporaryDirectory() as folder:
            result=export(folder)
            self.assertEqual(sum(s['rows'] for s in result['splits']),2200)
            for spec in result['splits']:
                data=pd.read_csv(Path(folder)/'data'/spec['file'])
                expected=sample(spec['rows'],spec['seed'],.08 if spec['file']=='test.csv' else 0)
                pd.testing.assert_frame_equal(data,expected)
            ranked,_=benchmark()
            pd.testing.assert_frame_equal(pd.read_csv(Path(folder)/'data/test.csv'),ranked[FEATURES+['injected_anomaly']])
