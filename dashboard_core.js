(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.AnomalyCore=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
  function flag(row,method){return Number(row[method+'_flag']);}
  function outcome(row,method){return row.injected_anomaly?(flag(row,method)?'TP':'FN'):(flag(row,method)?'FP':'TN');}
  function metrics(rows,method){const m={TP:0,FP:0,FN:0,TN:0};rows.forEach(r=>m[outcome(r,method)]++);m.alerts=m.TP+m.FP;m.precision=m.alerts?m.TP/m.alerts:0;m.recall=m.TP+m.FN?m.TP/(m.TP+m.FN):0;return m;}
  function filter(rows,{method='model',outcome:choice='',feature='',query=''}={}){return rows.filter(r=>(!choice||outcome(r,method)===choice)&&(!feature||r.top_deviation===feature)&&(!query||r.row_id.toLowerCase().includes(query.toLowerCase()))).sort((a,b)=>b.anomaly_score-a.anomaly_score);}
  function rules(row){return [['Volume > 1,600',row.daily_volume>1600],['Error rate > 10%',row.error_rate>.1],['Latency > 350 ms',row.latency_ms>350],['Missing rate > 10%',row.missing_rate>.1]].filter(x=>x[1]).map(x=>x[0]);}
  return {flag,outcome,metrics,filter,rules};
});
