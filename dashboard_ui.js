const $=id=>document.getElementById(id), core=AnomalyCore;
const pct=x=>(x*100).toFixed(2)+'%', num=x=>Number(x).toLocaleString('en-US',{maximumFractionDigits:4});
const names={daily_volume:'Daily volume',error_rate:'Error rate',latency_ms:'Latency (ms)',missing_rate:'Missing rate'};
const value=(k,v)=>k.includes('rate')?pct(v):num(v);
function cell(tr,text){const td=document.createElement('td');td.textContent=text;tr.append(td);return td;}
function inspect(row){
  $('detail-title').textContent=row.row_id+' • '+core.outcome(row,$('method').value);
  $('detail-intro').textContent='Score '+num(row.anomaly_score)+' vs threshold '+num(DATA.summary.threshold)+'. Model: '+(row.model_flag?'flagged':'not flagged')+'. Rules: '+(row.rule_flag?'flagged':'not flagged')+'. Injected label: '+row.injected_anomaly+'.';
  $('detail-body').replaceChildren();
  Object.keys(names).forEach(k=>{const base=DATA.baseline[k],z=Math.abs(row[k]-base.median)/(1.4826*base.mad);const tr=document.createElement('tr');[names[k],value(k,row[k]),value(k,base.median),value(k,base.p05)+' – '+value(k,base.p95),num(z)].forEach(x=>cell(tr,x));$('detail-body').append(tr);});
  const rules=core.rules(row);$('detail-rules').textContent='Rules triggered: '+(rules.join('; ')||'none')+'. Largest descriptive deviation: '+names[row.top_deviation]+'.';
}
function render(){
  const method=$('method').value,m=core.metrics(DATA.rows,method);
  $('cm').textContent='True positives '+m.TP+' • False positives '+m.FP+' • False negatives '+m.FN+' • True negatives '+m.TN;
  $('formula').textContent='Precision = '+m.TP+' / '+m.alerts+' = '+pct(m.precision)+'. Recall = '+m.TP+' / '+(m.TP+m.FN)+' = '+pct(m.recall)+'. Alert volume = '+m.alerts+' / 600 ('+pct(m.alerts/600)+'). Metrics always use the full test set.';
  const rows=core.filter(DATA.rows,{method,outcome:$('outcome').value,feature:$('feature').value,query:$('search').value});
  $('count').textContent=rows.length+' of 600 test records match. Sorted by model anomaly score.';
  $('queue').replaceChildren();
  rows.forEach(r=>{const tr=document.createElement('tr'),td=cell(tr,'');const b=document.createElement('button');b.type='button';b.textContent=r.row_id;b.addEventListener('click',()=>{inspect(r);$('detail').scrollIntoView({behavior:'smooth',block:'start'});});td.append(b);[core.outcome(r,method),r.injected_anomaly,num(r.anomaly_score),r.model_flag,r.rule_flag,value('daily_volume',r.daily_volume),value('error_rate',r.error_rate),value('latency_ms',r.latency_ms),value('missing_rate',r.missing_rate),names[r.top_deviation]].forEach(x=>cell(tr,x));$('queue').append(tr);});
  if(rows.length)inspect(rows[0]);else{$('detail-title').textContent='No matching records';$('detail-intro').textContent='Change the filters to inspect a record.';$('detail-body').replaceChildren();$('detail-rules').textContent='';}
}
['method','outcome','feature'].forEach(id=>$(id).addEventListener('change',render));$('search').addEventListener('input',render);
$('reset').addEventListener('click',()=>{$('method').value='model';$('outcome').value='';$('feature').value='';$('search').value='';render();});
$('download').addEventListener('click',()=>{const keys=Object.keys(DATA.rows[0]),csv=[keys.join(','),...DATA.rows.map(r=>keys.map(k=>r[k]).join(','))].join('\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));const a=document.createElement('a');a.href=url;a.download='synthetic-anomaly-test-scored.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
render();
