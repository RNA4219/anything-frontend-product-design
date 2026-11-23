// Supplemental risks identified by the analyst before candidate implementation.
// These three criteria are separate from the original 13-case frozen suite.
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
const {createBatchFlow}=await import(pathToFileURL(resolve(process.argv[2]||'modules/interaction-ux-flow/examples/batch-flow.mjs')).href);
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};};
const rows=f=>Object.fromEntries(f.view().rows.map(x=>[x.id,x]));
const results=[];async function test(id,name,fn){try{await fn();results.push({id,name,pass:true});}catch(e){results.push({id,name,pass:false,error:e.message});}}
await test('A01','Concurrent retry of one eligible item produces one new attempt',async()=>{
 const pending=deferred();let seq=0,effects=0;const calls=[];let retryRequest;
 const api={submit:async({items})=>{calls.push(structuredClone(items));const x=items[0];if(calls.length===1)return {accepted:true,results:[{...x,status:'failed',unapplied:true,retryable:true}]};retryRequest=x;return pending.promise;}};
 const f=createBatchFlow(api,{items:[{id:'a',label:'A'}],nextRequestId:()=>`r-${++seq}`,now:()=>0});await f.start();
 const first=f.retry(['a']),second=f.retry(['a']);assert.equal(calls.length,2);effects++;pending.resolve({accepted:true,results:[{...retryRequest,status:'succeeded'}]});await Promise.all([first,second]);assert.equal(effects,1);assert.equal(rows(f).a.status,'succeeded');
});
await test('A02','Late pending cannot replace a terminal outcome or a newer attempt',async()=>{
 for(const startNewAttempt of [false,true]){
  const delayed=deferred();let seq=0,lookups=0,writes=0,effects=0,original;
  const api={submit:async({items:[x]})=>{writes++;if(writes===1){original=x;return {accepted:true,results:[{...x,status:'pending'}]};}effects++;return {accepted:true,results:[{...x,status:'succeeded'}]};},lookup:async x=>{lookups++;return lookups===1?delayed.promise:{...x,status:'failed',unapplied:true,retryable:true};}};
  const f=createBatchFlow(api,{items:[{id:'a',label:'A'}],nextRequestId:()=>`r-${++seq}`,now:()=>0});await f.start();const old=f.reconcile(['a']);await f.reconcile(['a']);assert.equal(rows(f).a.status,'failed');
  if(startNewAttempt)await f.retry(['a']);const accepted=structuredClone(rows(f).a);delayed.resolve({...original,status:'pending'});await old;assert.equal(rows(f).a.status,accepted.status);assert.equal(rows(f).a.requestId,accepted.requestId);assert.equal(effects,startNewAttempt?1:0);assert.equal(writes,startNewAttempt?2:1);
 }
});
await test('A03','Caller or view mutation cannot alter selected scope or internal state',async()=>{
 const selected=[{id:'a',label:'A',dependsOn:[]}];let seq=0;const calls=[];const api={submit:async({items})=>{calls.push(structuredClone(items));return {accepted:true,results:items.map(x=>({...x,status:'succeeded'}))};}};
 const f=createBatchFlow(api,{items:selected,nextRequestId:()=>`r-${++seq}`,now:()=>0});selected[0].id='foreign';selected.push({id:'b',label:'B'});const view=f.view();view.rows[0].id='tampered';view.rows[0].status='succeeded';view.canRetryIds.push('foreign');view.counts.succeeded=99;
 assert.equal(f.view().total,1);assert.equal(rows(f).a.status,'ready');await f.start();assert.deepEqual(calls[0].map(x=>x.itemId),['a']);assert.equal(f.view().counts.succeeded,1);assert.equal(f.view().rows.length,1);
});
console.log(JSON.stringify({suite:'B-R04-pre-candidate-supplement',total:results.length,passed:results.filter(x=>x.pass).length,results},null,2));process.exitCode=results.some(x=>!x.pass)?1:0;
