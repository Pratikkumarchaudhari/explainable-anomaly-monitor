"""Held-out anomaly detection benchmark with transparent deviation explanations."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score,recall_score,f1_score,average_precision_score,confusion_matrix

ROOT=Path(__file__).resolve().parent
FEATURES=['daily_volume','error_rate','latency_ms','missing_rate']

def sample(n,seed,rate=0):
    rng=np.random.default_rng(seed)
    df=pd.DataFrame({'daily_volume':rng.normal(1000,100,n).clip(1),
        'error_rate':rng.beta(2,100,n),'latency_ms':rng.normal(200,25,n).clip(1),
        'missing_rate':rng.beta(1,150,n)})
    labels=np.zeros(n,dtype=int)
    k=int(n*rate)
    if k:
        selected=rng.choice(n,k,replace=False);labels[selected]=1
        for i,j in enumerate(selected):
            feature=FEATURES[i%4]
            if feature=='daily_volume':df.loc[j,feature]*=rng.uniform(2,3)
            elif feature=='latency_ms':df.loc[j,feature]+=rng.uniform(180,350)
            else:df.loc[j,feature]=rng.uniform(.2,.5)
    df['injected_anomaly']=labels
    return df

def validate(df):
    if set(FEATURES)-set(df.columns):raise ValueError('Missing monitoring features')
    x=df[FEATURES].astype(float)
    if x.empty or not np.isfinite(x.to_numpy()).all():raise ValueError('Empty/nonfinite features')
    if (x[['daily_volume','latency_ms']]<0).any().any():raise ValueError('Negative volume/latency')
    if ((x[['error_rate','missing_rate']]<0)|(x[['error_rate','missing_rate']]>1)).any().any():raise ValueError('Rates must lie in [0,1]')
    return x

def benchmark():
    train=sample(1200,11);calibration=sample(400,22);test=sample(600,33,.08)
    x=validate(train);cal=validate(calibration);xt=validate(test)
    model=IsolationForest(n_estimators=200,random_state=42,contamination='auto').fit(x)
    # Select a review threshold from normal calibration data, never test labels.
    threshold=float(np.quantile(-model.score_samples(cal),.98))
    scores=-model.score_samples(xt);pred=(scores>=threshold).astype(int)
    y=test.injected_anomaly.to_numpy()
    median=x.median();mad=(x-median).abs().median().replace(0,1e-9)
    deviation=(xt-median).abs().div(1.4826*mad)
    rules=((xt.error_rate>.10)|(xt.missing_rate>.10)|(xt.latency_ms>350)|(xt.daily_volume>1600)).astype(int).to_numpy()
    ranked=test.copy();ranked['anomaly_score']=scores;ranked['model_flag']=pred;ranked['rule_flag']=rules
    ranked['review_flag']=((pred+rules)>0).astype(int)
    ranked['top_deviation']=deviation.idxmax(axis=1)
    ranked['robust_z']=deviation.max(axis=1)
    ranked['row_id']=[f'TEST{i:04}' for i in range(len(test))]
    def metrics(p):return dict(precision=round(float(precision_score(y,p,zero_division=0)),4),
        recall=round(float(recall_score(y,p,zero_division=0)),4),f1=round(float(f1_score(y,p,zero_division=0)),4),
        confusion_matrix=confusion_matrix(y,p,labels=[0,1]).tolist())
    # Drift: standardized mean shift vs training. Diagnostic, not a hypothesis test.
    drift=((xt.mean()-x.mean()).abs()/x.std(ddof=0).replace(0,1e-9)).round(4).to_dict()
    result=dict(data_type='Synthetic injected-anomaly benchmark',train_rows=len(train),calibration_rows=len(calibration),
        test_rows=len(test),injected_anomalies=int(y.sum()),threshold=threshold,
        calibration_false_positive_rate=round(float((-model.score_samples(cal)>=threshold).mean()),4),
        model=metrics(pred),rules=metrics(rules),hybrid=metrics(ranked.review_flag.to_numpy()),
        average_precision=round(float(average_precision_score(y,scores)),4),
        drift_standardized_mean_shift=drift,
        flagged_rows=ranked[ranked.review_flag==1].sort_values('anomaly_score',ascending=False).round(4).to_dict('records'))
    return ranked,result

def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    ranked,result=benchmark();out=ROOT/'outputs';out.mkdir(exist_ok=True)
    ranked.to_csv(out/'scored_records.csv',index=False)
    (out/'evaluation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='flagged_rows'},indent=2))
if __name__=='__main__':main()
