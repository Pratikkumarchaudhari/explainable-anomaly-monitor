"""Rebuild the standalone report from current benchmark outputs; no server needed."""
import json
from pathlib import Path
import pandas as pd
from monitor import sample, FEATURES

ROOT=Path(__file__).resolve().parent

def build():
    summary=json.loads((ROOT/'outputs/evaluation.json').read_text())
    rows=pd.read_csv(ROOT/'outputs/scored_records.csv').to_dict('records')
    train=sample(1200,11)
    baseline={}
    for k in FEATURES:
        median=float(train[k].median())
        baseline[k]=dict(median=median,mad=float((train[k]-median).abs().median()),
                         p05=float(train[k].quantile(.05)),p95=float(train[k].quantile(.95)))
    template=(ROOT/'report_template.html').read_text()
    data=json.dumps(dict(summary=summary,rows=rows,baseline=baseline),allow_nan=False)
    html=template.replace('/*CORE*/',(ROOT/'dashboard_core.js').read_text()).replace('/*DATA*/','const DATA='+data+';').replace('/*UI*/',(ROOT/'dashboard_ui.js').read_text())
    (ROOT/'report.html').write_text(html)
    return html

if __name__=='__main__':
    build()
    print('Rebuilt report.html from 600 scored test records.')
