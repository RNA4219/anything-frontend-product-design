import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,mkdtemp} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {tmpdir} from 'node:os';
import {createHash} from 'node:crypto';
const root=resolve(process.env.B_REPO_ROOT||process.cwd());
const modulePath=resolve(process.argv[2]||join(root,'modules/interaction-ux-flow/examples/batch-flow.mjs'));
const out=process.env.B_CRITIC_OUTPUT_DIR?resolve(process.env.B_CRITIC_OUTPUT_DIR):await mkdtemp(join(tmpdir(),'b-r04-edge-'));
await mkdir(out,{recursive:true});
const {createBatchFlow}=await import(pathToFileURL(modulePath).href);
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};};
const results=[];
const row=(f,id='a')=>f.view().rows.find(x=>x.id===id);
async function test(id,fn){const observations=[];try{await fn((step,data)=>observations.push({step,...structuredClone(data)}));results.push({id,pass:true,observations});}catch(e){results.push({id,pass:false,error:e.message,stack:e.stack,observations});}}
await test('E01-LATE-CANCEL-RECEIPT-AFTER-SUCCESS',async record=>{
 let n=0,effects=0,original;const gate=deferred(),calls=[];
 const api={submit:async({items:[r]})=>{original=r;calls.push({method:'submit',...r});return {accepted:true,results:[{...r,status:'pending'}]};},lookup:async r=>{calls.push({method:'lookup',...r});effects++;return {...r,status:'succeeded'};},cancel:async r=>{calls.push({method:'cancel',...r});return gate.promise;}};
 const f=createBatchFlow(api,{items:[{id:'a'}],nextRequestId:()=>`e1-${++n}`});await f.start();const pendingCancel=f.requestCancel(['a']);assert.equal(row(f).cancelState,'requesting');
 await f.reconcile(['a']);record('success-before-cancel-receipt',{view:f.view(),effects,calls});assert.equal(row(f).status,'succeeded');
 gate.resolve({accepted:true});await pendingCancel;assert.equal(row(f).status,'succeeded');assert.equal(f.view().counts.cancelled,0);assert.equal(f.view().allSucceeded,true);assert.deepEqual(f.view().canCancelIds,[]);assert.deepEqual(f.view().canReconcileIds,[]);assert.equal(effects,1);assert.equal(row(f).requestId,original.requestId);record('late-receipt-preserves-success',{view:f.view(),effects,calls});
});
await test('E02-WRONG-ITEM-OR-ATTEMPT-CANNOT-CONFIRM',async record=>{
 let n=0,correct=false;const effects={a:0,b:0},calls=[];
 const api={submit:async({items})=>{calls.push({method:'submit',items:structuredClone(items)});for(const x of items)effects[x.itemId]++;return {accepted:true,results:[{...items[0],itemId:'foreign',status:'succeeded'},{...items[1],requestId:'wrong-attempt',status:'succeeded'}]};},lookup:async r=>{calls.push({method:'lookup',...r});return correct?{...r,status:'succeeded'}:{...r,itemId:r.itemId==='a'?'b':'a',status:'succeeded'};}};
 const f=createBatchFlow(api,{items:[{id:'a'},{id:'b'}],nextRequestId:()=>`e2-${++n}`});await f.start();assert.equal(f.view().counts.unknown,2);await f.retry(['a','b','foreign']);await f.reconcile(['a','b']);assert.equal(f.view().counts.unknown,2);assert.equal(calls.filter(x=>x.method==='submit').length,1);record('wrong-correlations-remain-unresolved',{view:f.view(),effects,calls});
 correct=true;await f.reconcile(['a','b']);assert.equal(f.view().allSucceeded,true);assert.deepEqual(effects,{a:1,b:1});assert.equal(calls.filter(x=>x.method==='submit').length,1);record('correct-original-refs-resolve',{view:f.view(),effects,calls});
});
await test('E03-FAILED-BLOCKED-WITHOUT-NONAPPLICATION-EVIDENCE',async record=>{
 let n=0;const calls=[],effects={a:0,b:0};
 const api={submit:async({items:[a,b]})=>{calls.push({method:'submit',items:[a,b]});effects.a++;effects.b++;return {accepted:true,results:[{...a,status:'failed',retryable:true},{...b,status:'blocked',retryable:true,unapplied:false}]};},lookup:async r=>{calls.push({method:'lookup',...r});return {...r,status:'succeeded'};}};
 const f=createBatchFlow(api,{items:[{id:'a'},{id:'b'}],nextRequestId:()=>`e3-${++n}`});await f.start();assert.equal(f.view().counts.unknown,2);assert.deepEqual(f.view().canRetryIds,[]);await f.retry(['a','b']);assert.equal(calls.filter(x=>x.method==='submit').length,1);record('not-authoritatively-unapplied',{view:f.view(),effects,calls});await f.reconcile(['a','b']);assert.equal(f.view().allSucceeded,true);assert.deepEqual(effects,{a:1,b:1});record('known-outcome',{view:f.view(),effects,calls});
});
await test('E04-EXPLICIT-SUBSET-AND-RENEWED-MINIMUM-DELAY',async record=>{
 let n=0,time=10;const calls=[],effects={a:0,b:0},attempts={a:0,b:0};
 const api={submit:async({items})=>{calls.push({method:'submit',items:structuredClone(items)});return {accepted:true,results:items.map(r=>{attempts[r.itemId]++;if(attempts[r.itemId]===1)return {...r,status:'failed',unapplied:true,retryable:true,nextRetryAt:20};if(r.itemId==='b'&&attempts.b===2)return {...r,status:'failed',unapplied:true,retryable:true,nextRetryAt:40};effects[r.itemId]++;return {...r,status:'succeeded'};})};}};
 const f=createBatchFlow(api,{items:[{id:'a'},{id:'b'}],nextRequestId:()=>`e4-${++n}`,now:()=>time});await f.start();time=20;assert.deepEqual(f.view().canRetryIds,['a','b']);await f.retry(['b']);assert.deepEqual(calls[1].items.map(x=>x.itemId),['b']);assert.deepEqual(effects,{a:0,b:0});assert.equal(row(f,'b').status,'failed');assert.equal(row(f,'b').nextRetryAt,40);record('retry-can-fail-again',{view:f.view(),effects,calls});
 time=39;await f.retry(['b']);assert.equal(calls.length,2);time=40;assert.equal(calls.length,2);await f.retry(['b']);assert.deepEqual(effects,{a:0,b:1});assert.equal(f.view().allSucceeded,false);assert.deepEqual(f.view().canRetryIds,['a']);await f.retry(['a','b']);assert.deepEqual(calls.at(-1).items.map(x=>x.itemId),['a']);assert.deepEqual(effects,{a:1,b:1});assert.equal(f.view().allSucceeded,true);record('explicit-eligible-completion',{view:f.view(),effects,calls});
});
const report={kind:'Independent exploratory probes, not additions to original 13 or pre-candidate supplemental 3.',runtime:process.version,module_sha256:createHash('sha256').update(await readFile(modulePath)).digest('hex'),total:results.length,passed:results.filter(x=>x.pass).length,results};
await writeFile(join(out,'edge-probes.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({outputDir:out,total:report.total,passed:report.passed,failures:results.filter(x=>!x.pass).map(({id,error})=>({id,error}))}));process.exitCode=results.some(x=>!x.pass)?1:0;
