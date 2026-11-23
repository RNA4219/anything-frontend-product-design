import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
const base=resolve(process.env.B_REPO_ROOT||process.cwd());
const modulePath=resolve(process.argv[2]||`${base}/modules/interaction-ux-flow/examples/resume-and-conflict.mjs`);
const outputDir=resolve(process.env.B_CRITIC_OUTPUT_DIR||'artifacts/critic-r03');
await mkdir(outputDir,{recursive:true});
const outputPath=resolve(process.argv[3]||`${outputDir}/edge-probes.json`);
const {createResumableEdit}=await import(pathToFileURL(modulePath));
const cp=x=>structuredClone(x),session=(id='A',canRead=true,canWrite=true)=>({accountId:id,authenticated:true,canRead,canWrite});
const old={etag:'z-old',values:{title:'Original'}},success={status:'succeeded',operationResult:{etag:'b-written',values:{title:'My draft'}}};
const saved=()=>({ownerId:'A',resourceId:'doc-1',lastKnown:cp(old),draft:{title:'My draft'},operation:null});
const results=[];
async function trial(id,fn){const trace=[];try{await fn(trace);results.push({id,pass:true,trace});}catch(e){results.push({id,pass:false,error:e.message,trace});}}
await trial('X01-SAME-ACCOUNT-ABA-OLD-READ',async trace=>{
 let release,n=0;const api={load:async()=>++n===1?await new Promise(r=>release=r):{etag:'a-new',values:{title:'New observation'}},lookup:async()=>({status:'pending'}),update:async()=>{throw Error('unexpected');}};
 const f=createResumableEdit(api,{session:session(),saved:saved(),nextId:()=> 'op'});const p=f.resume();f.setSession(session('B'));f.setSession(session());await f.resume();release(cp(old));await p;trace.push(f.view());assert.equal(f.view().observedResource.values.title,'New observation');
});
await trial('X02-OLD-VIEW-SUCCESS-RETAINED-FOR-OWNER',async trace=>{
 let release,lookups=0;const api={load:async()=>cp(success.operationResult),lookup:async()=>{lookups++;return {status:'expired'};},update:async()=>await new Promise(r=>release=r)};
 const f=createResumableEdit(api,{session:session(),saved:saved(),nextId:()=> 'op'});await f.resume();f.review();const p=f.commit();f.setSession(session('B'));release(cp(success));await p;trace.push({atB:f.view()});assert.equal(f.view().draft,null);f.setSession(session());await f.resume();trace.push({atA:f.view(),lookups});assert.equal(f.view().phase,'completed');assert.equal(lookups,0);
});
await trial('X03-TERMINAL-SUCCESS-VS-INFLIGHT-STALE-PENDING',async trace=>{
 let releaseUpdate,releaseLookup;const api={load:async()=>cp(success.operationResult),lookup:async()=>await new Promise(r=>releaseLookup=r),update:async()=>await new Promise(r=>releaseUpdate=r)};
 const f=createResumableEdit(api,{session:session(),saved:saved(),nextId:()=> 'op'});await f.resume();f.review();const update=f.commit();const lookup=f.resume();releaseUpdate(cp(success));await update;trace.push({afterConfirmedSuccessArrives:f.view()});releaseLookup({status:'pending'});await lookup;trace.push({afterOlderPendingArrives:f.view()});assert.equal(f.view().operationOutcome,'succeeded','A stale pending response must not override a correlated terminal success already received by the controller.');assert.equal(f.view().phase,'completed');
});
await trial('X04-NO-ACCESS-NO-QUERY',async trace=>{
 const calls=[];const api={load:async x=>{calls.push(['load',x]);return cp(old);},lookup:async x=>{calls.push(['lookup',x]);return {status:'pending'};},update:async x=>{calls.push(['update',x]);return cp(success);}};
 const f=createResumableEdit(api,{session:session('A',false,true),saved:saved(),nextId:()=> 'op'});await f.resume();f.review();await f.commit();trace.push({view:f.view(),calls});assert.equal(f.view().phase,'no_access');assert.equal(f.view().draft,null);assert.equal(calls.length,0);
});
await trial('X05-DIFFERENT-TARGET-NO-QUERY',async trace=>{
 const calls=[];const api={load:async x=>{calls.push(x);return cp(old);},lookup:async x=>{calls.push(x);return {status:'pending'};},update:async x=>{calls.push(x);return cp(success);}};
 const f=createResumableEdit(api,{session:session(),saved:saved(),targetResourceId:'doc-2',nextId:()=> 'op'});await f.resume();trace.push({view:f.view(),calls});assert.equal(f.view().phase,'different_task');assert.equal(calls.length,0);assert.equal(f.view().draft,null);
});
await trial('X06-CHANGE-AFTER-REVIEW-INVALIDATES-COMMIT',async trace=>{
 let writes=0;const api={load:async()=>cp(old),lookup:async()=>({status:'pending'}),update:async()=>{writes++;return cp(success);}};
 const f=createResumableEdit(api,{session:session(),saved:saved(),nextId:()=> 'op'});await f.resume();f.review();f.edit('title','Different decision');await f.commit();trace.push({view:f.view(),writes});assert.equal(writes,0);assert.equal(f.view().canCommit,false);
});
const report={suite:'Independent R03 exploratory probes; not frozen criteria',modulePath,moduleSha256:createHash('sha256').update(await readFile(modulePath)).digest('hex'),total:results.length,passed:results.filter(x=>x.pass).length,results,limits:['No production server/auth/storage/security or browser verification.','Pending/success race uses two correctly correlated operation replies delivered out of order; no mutated candidate.']};await writeFile(outputPath,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({total:results.length,passed:report.passed,failures:results.filter(x=>!x.pass).map(({id,error})=>({id,error}))}));process.exitCode=results.some(x=>!x.pass)?1:0;
