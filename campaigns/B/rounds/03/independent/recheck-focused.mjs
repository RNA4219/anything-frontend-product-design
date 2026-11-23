import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
const root=resolve(process.env.B_REPO_ROOT||process.cwd());
const output=resolve(process.env.B_CRITIC_OUTPUT_DIR||'artifacts/critic-r03');await mkdir(output,{recursive:true});
const modulePath=resolve(root,'modules/interaction-ux-flow/examples/resume-and-conflict.mjs');
const htmlPath=resolve(root,'modules/interaction-ux-flow/examples/resume-and-conflict.html');
const {createResumableEdit}=await import(pathToFileURL(modulePath));
const results=[];async function test(id,fn){const trace=[];try{await fn(trace);results.push({id,pass:true,trace});}catch(e){results.push({id,pass:false,error:e.message,trace});}}
const copy=x=>structuredClone(x),session={accountId:'A',authenticated:true,canRead:true,canWrite:true};
const resource={etag:'original',values:{title:'Original'}};
const saved=()=>({ownerId:'A',resourceId:'doc-1',lastKnown:copy(resource),draft:{title:'Draft'},operation:null});
const success={status:'succeeded',operationResult:{etag:'written',values:{title:'Draft'}}};
await test('RC01-TERMINAL-SUCCESS-BEFORE-LOOKUP-REJECTION',async trace=>{
 let releaseUpdate,rejectLookup;
 const api={load:async()=>copy(resource),lookup:async()=>await new Promise((_,rej)=>rejectLookup=rej),update:async()=>await new Promise(r=>releaseUpdate=r)};
 const f=createResumableEdit(api,{session,saved:saved(),nextId:()=> 'operation-1'});
 await f.resume();f.review();const update=f.commit();const lookup=f.resume();releaseUpdate(copy(success));await update;
 trace.push({afterSuccess:f.view()});rejectLookup(Error('lookup transport failed'));await lookup;trace.push({afterLookupFailure:f.view()});
 assert.equal(f.view().operationOutcome,'succeeded','The same terminal-precedence fix must also cover lookup transport failure after the success has already arrived.');
 assert.equal(f.view().phase,'completed');
});
await test('RC02-RESTORED-EVIDENCE-BINDING',async trace=>{
 for(const mismatch of ['ownerId','resourceId','operationId']){
  const r=saved();r.operation={id:'op-1',baseEtag:resource.etag,changes:copy(r.draft)};
  r.confirmedOutcome={ownerId:'A',resourceId:'doc-1',operationId:'op-1',result:copy(success)};
  r.confirmedOutcome[mismatch]='different';let lookups=0;
  const api={load:async()=>copy(resource),lookup:async()=>{lookups++;return {status:'pending'};},update:async()=>{throw Error('unexpected');}};
  const f=createResumableEdit(api,{session,saved:r,nextId:()=> 'unused'});await f.resume();trace.push({mismatch,view:f.view(),lookups});
  assert.equal(f.view().phase,'pending');assert.equal(f.view().operationOutcome,null);assert.equal(lookups,1);
 }
});
await test('RC03-INPUT-COPY-ACROSS-SUBMISSION-STATES',async trace=>{
 const require=createRequire(import.meta.url),jsdomPath=process.env.B_DOM_JSDOM_PATH||'jsdom';const {JSDOM}=require(jsdomPath);
 const html=await readFile(htmlPath,'utf8'),script=html.match(/<script type="module">([\s\S]*?)<\/script>/)[1];
 const dom=new JSDOM(html,{url:'https://fixture.invalid/',runScripts:'outside-only'});const w=dom.window,$=id=>w.document.getElementById(id);
 w.__factory=createResumableEdit;w.eval(script.replace("import {createResumableEdit} from './resume-and-conflict.mjs';",'const createResumableEdit=window.__factory;'));
 const flush=()=>new Promise(r=>setImmediate(r));const click=async id=>{$(id).click();await flush();};
 try{
  await click('resume');trace.push({phase:w.resumeDemo.getFlow().view().phase,inputStatus:$('input-status').textContent});assert.match($('input-status').textContent,/復帰だけでは更新を実行していません/);
  $('lose-reply').checked=true;$('lose-reply').dispatchEvent(new w.Event('change',{bubbles:true}));await click('review');await click('commit');
  trace.push({phase:w.resumeDemo.getFlow().view().phase,inputStatus:$('input-status').textContent});assert.equal(w.resumeDemo.getFlow().view().phase,'unknown');assert.match($('input-status').textContent,/送信済み/);assert.equal($('input-status').textContent.includes('成功を確認'),false);
  await click('reopen');trace.push({phase:w.resumeDemo.getFlow().view().phase,inputStatus:$('input-status').textContent});assert.match($('input-status').textContent,/成功を確認/);assert.equal(w.resumeDemo.getEffects(),1);
  $('session').value='B';$('session').dispatchEvent(new w.Event('change',{bubbles:true}));await flush();trace.push({phase:w.resumeDemo.getFlow().view().phase,inputStatus:$('input-status').textContent});assert.equal($('input-status').textContent,'');assert.equal($('work').hidden,true);
 }finally{dom.window.close();}
});
const report={scope:'Focused recheck of known repairs plus their directly changed binding/error path. Separate from frozen criteria.',moduleSha256:createHash('sha256').update(await readFile(modulePath)).digest('hex'),htmlSha256:createHash('sha256').update(await readFile(htmlPath)).digest('hex'),total:results.length,passed:results.filter(x=>x.pass).length,results};
await writeFile(resolve(output,'focused-recheck.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({total:report.total,passed:report.passed,failures:results.filter(x=>!x.pass).map(({id,error})=>({id,error}))}));process.exitCode=results.some(x=>!x.pass)?1:0;
