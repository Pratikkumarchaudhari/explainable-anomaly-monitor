const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const core=require('../dashboard_core.js');
const html=fs.readFileSync(path.join(__dirname,'../report.html'),'utf8');
const data=JSON.parse(html.match(/const DATA=(.*?);<\/script>/s)[1]);
test('all detector confusion counts reconcile to Python output',()=>{
  assert.equal(data.rows.length,600);
  for(const [method,key] of [['model','model'],['rule','rules'],['review','hybrid']]){
    const m=core.metrics(data.rows,method),cm=data.summary[key].confusion_matrix;
    assert.deepEqual([[m.TN,m.FP],[m.FN,m.TP]],cm);
    assert.equal(m.TP+m.FP+m.FN+m.TN,600);
  }
});
test('filters expose model misses, false alarms and correct hybrid union',()=>{
  assert.equal(core.filter(data.rows,{method:'model',outcome:'FN'}).length,16);
  assert.equal(core.filter(data.rows,{method:'model',outcome:'FP'}).length,18);
  assert.equal(core.filter(data.rows,{method:'review',outcome:'FN'}).length,0);
  assert.equal(core.filter(data.rows,{query:'test0536'})[0].row_id,'TEST0536');
  assert.equal(core.filter(data.rows,{query:'unknown'}).length,0);
});
test('rule explanations use the exact Python thresholds',()=>{
  for(const r of data.rows)assert.equal(Number(core.rules(r).length>0),r.rule_flag);
  assert.equal(core.rules({daily_volume:1600,error_rate:.1,latency_ms:350,missing_rate:.1}).length,0);
});
