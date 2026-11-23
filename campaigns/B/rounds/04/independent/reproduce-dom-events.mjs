import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,mkdtemp} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {resolve,join} from 'node:path';
import {tmpdir} from 'node:os';
import {createHash} from 'node:crypto';
const require=createRequire(import.meta.url);
const jsdomPath=process.env.B_DOM_JSDOM_PATH||'jsdom';
const {JSDOM,VirtualConsole}=require(jsdomPath);
const root=resolve(process.env.B_REPO_ROOT||process.cwd());
const modulePath=resolve(process.argv[2]||join(root,'modules/interaction-ux-flow/examples/batch-flow.mjs'));
const htmlPath=resolve(process.argv[3]||join(root,'modules/interaction-ux-flow/examples/batch-flow.html'));
const out=process.env.B_CRITIC_OUTPUT_DIR?resolve(process.env.B_CRITIC_OUTPUT_DIR):await mkdtemp(join(tmpdir(),'b-r04-dom-'));
await mkdir(out,{recursive:true});
const factories=await import(pathToFileURL(modulePath).href);
const html=await readFile(htmlPath,'utf8');
const script=html.match(/<script type="module">([\s\S]*?)<\/script>/)?.[1];
const importLine="import {createBatchFlow} from './batch-flow.mjs';";
assert.equal(script.split(importLine).length,2);
const normal=x=>JSON.parse(JSON.stringify(x));
const hash=b=>createHash('sha256').update(b).digest('hex');
const labels={ready:'未送信',pending:'処理中',unknown:'結果未確認',succeeded:'成功',failed:'未適用',blocked:'前提未成立・未実行',cancelled:'取消済み'};
const results=[];
const caseFilter=process.env.B_CRITIC_CASE_IDS?new Set(process.env.B_CRITIC_CASE_IDS.split(',').filter(Boolean)):null;
async function page(){
 const errors=[],events=[],observations=[];const vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
 const dom=new JSDOM(html,{url:'https://fixture.invalid/batch-flow.html',runScripts:'outside-only',virtualConsole:vc});
 dom.window.__factories=factories;
 dom.window.eval(script.replace(importLine,'const {createBatchFlow}=window.__factories;'));
 const w=dom.window,$=id=>w.document.getElementById(id);
 const flush=()=>new Promise(r=>setImmediate(r));
 const click=async id=>{events.push({type:'click',id,disabled:$(id).disabled});$(id).click();await flush();};
 const change=async(id,value)=>{if($(id).type==='checkbox')$(id).checked=value;else $(id).value=value;$(id).dispatchEvent(new w.Event('change',{bubbles:true}));events.push({type:'change',id,value});await flush();};
 const snapshot=(step)=>{
  const s=normal({step,flow:w.batchDemo.getFlow().view(),calls:w.batchDemo.getCalls(),effects:w.batchDemo.getEffects(),server:w.batchDemo.getServer(),dom:{scope:$('scope').textContent,summary:$('summary').textContent,rows:[...$('items').children].map(tr=>({id:tr.dataset.itemId,cells:[...tr.children].map(td=>td.textContent)})),buttons:Object.fromEntries(['start','retry','reconcile','cancel'].map(id=>[id,{disabled:$(id).disabled,text:$(id).textContent}])),scenarioDisabled:$('scenario').disabled,references:JSON.parse($('references').textContent),service:JSON.parse($('service').textContent),cancelNote:$('cancel-note').textContent}});
  assert.equal(s.dom.summary,s.flow.message);assert.match(s.dom.scope,new RegExp(`対象は${s.flow.total}件`));
  assert.deepEqual(s.dom.service.effects,s.effects);assert.deepEqual(s.dom.service.server,s.server);
  assert.deepEqual(s.dom.rows.map(x=>x.id),s.flow.rows.map(x=>x.id));
  for(const r of s.flow.rows){assert.equal(s.dom.rows.find(x=>x.id===r.id).cells[1],labels[r.status]);assert.equal(s.dom.references.find(x=>x.itemId===r.id).requestId,r.requestId);}
  assert.equal(s.dom.buttons.retry.disabled,!s.flow.canRetryIds.length);assert.equal(s.dom.buttons.reconcile.disabled,!s.flow.canReconcileIds.length);assert.equal(s.dom.buttons.cancel.disabled,!s.flow.canCancelIds.length);
  observations.push(s);return s;
 };
 return {dom,w,$,errors,events,observations,click,change,snapshot};
}
const submits=s=>s.calls.filter(x=>x.method==='submit');
const lookups=s=>s.calls.filter(x=>x.method==='lookup');
const cancels=s=>s.calls.filter(x=>x.method==='cancel');
const rows=s=>Object.fromEntries(s.flow.rows.map(x=>[x.id,x]));
async function trial(id,kind,fn){if(caseFilter&&!caseFilter.has(id))return;const p=await page();try{await fn(p);assert.deepEqual(p.errors,[]);results.push({id,kind,pass:true,events:p.events,observations:p.observations});}catch(e){results.push({id,kind,pass:false,error:e.message,stack:e.stack,events:p.events,observations:p.observations,runtimeErrors:p.errors});}finally{p.dom.window.close();}}
await trial('DOM01-MIXED-RECOVERY','representative',async p=>{
 p.snapshot('ready');await p.click('start');let s=p.snapshot('mixed');assert.deepEqual(s.effects,{a:1,b:0,c:1});assert.deepEqual(s.flow.rows.map(x=>x.status),['succeeded','failed','unknown']);assert.equal(s.flow.allSucceeded,false);assert.deepEqual(s.flow.canRetryIds,[]);const originalC=rows(s).c.requestId;
 await p.click('retry');assert.equal(submits(p.snapshot('disabled-retry')).length,1);
 await p.click('advance');s=p.snapshot('minimum-delay-met');assert.deepEqual(s.flow.canRetryIds,['b']);assert.equal(submits(s).length,1);assert.deepEqual(s.effects,{a:1,b:0,c:1});
 await p.click('retry');s=p.snapshot('only-b-retried');assert.deepEqual(submits(s)[1].items.map(x=>x.itemId),['b']);assert.deepEqual(s.effects,{a:1,b:1,c:1});assert.equal(s.flow.allSucceeded,false);
 await p.click('reconcile');s=p.snapshot('complete');assert.equal(s.flow.allSucceeded,true);assert.deepEqual(lookups(s),[{method:'lookup',itemId:'c',requestId:originalC}]);assert.equal(submits(s).length,2);assert.deepEqual(s.effects,{a:1,b:1,c:1});assert.match(s.dom.summary,/3件すべての変更成功/);
});
await trial('DOM02-ACCEPTED-NO-RESULTS','representative',async p=>{
 await p.change('scenario','accepted');await p.click('start');let s=p.snapshot('accepted-only');assert.equal(s.flow.finished,false);assert.equal(s.flow.counts.unknown,3);assert.deepEqual(s.effects,{a:0,b:0,c:0});const refs=s.flow.rows.map(x=>({method:'lookup',itemId:x.id,requestId:x.requestId}));
 await p.click('finish');s=p.snapshot('server-completed-but-unobserved');assert.equal(s.flow.allSucceeded,false);assert.deepEqual(s.effects,{a:1,b:1,c:1});
 await p.click('reconcile');s=p.snapshot('observed-complete');assert.equal(s.flow.allSucceeded,true);assert.deepEqual(lookups(s),refs);assert.equal(submits(s).length,1);assert.deepEqual(s.effects,{a:1,b:1,c:1});
});
await trial('DOM03-LOST-RESPONSE-LOOKUP-CANCEL','representative',async p=>{
 await p.change('scenario','lost');await p.click('start');let s=p.snapshot('lost-after-one-effect');assert.equal(s.flow.counts.unknown,3);assert.deepEqual(s.effects,{a:1,b:0,c:0});const originalRefs=s.flow.rows.map(x=>({method:'lookup',itemId:x.id,requestId:x.requestId}));
 await p.click('start');await p.click('retry');assert.equal(submits(p.snapshot('no-replay')).length,1);
 await p.click('reconcile');s=p.snapshot('lookup-original-operations');assert.deepEqual(lookups(s),originalRefs);assert.deepEqual(s.flow.rows.map(x=>x.status),['succeeded','pending','pending']);
 await p.click('cancel');s=p.snapshot('cancellation-receipts');assert.deepEqual(cancels(s).map(x=>x.itemId),['b','c']);assert.equal(s.flow.counts.cancelled,0);assert.equal(s.flow.counts.pending,2);assert.equal(s.flow.finished,false);
 await p.click('reconcile');s=p.snapshot('terminal-mixed');assert.equal(s.flow.finished,true);assert.equal(s.flow.allSucceeded,false);assert.equal(s.flow.counts.succeeded,1);assert.equal(s.flow.counts.cancelled,2);assert.deepEqual(s.effects,{a:1,b:0,c:0});assert.match(s.dom.summary,/結果がそろいました/);assert.equal(submits(s).length,1);
});
await trial('DOM04-DEPENDENCY-RECOVERY','representative',async p=>{
 await p.change('scenario','dependency');await p.click('start');let s=p.snapshot('blocked');assert.deepEqual(s.flow.canRetryIds,['a']);assert.equal(rows(s).b.status,'blocked');assert.deepEqual(s.effects,{a:0,b:0,c:1});
 await p.click('retry');s=p.snapshot('predecessor-only');assert.deepEqual(submits(s)[1].items.map(x=>x.itemId),['a']);assert.deepEqual(s.effects,{a:1,b:0,c:1});assert.deepEqual(s.flow.canRetryIds,['b']);assert.equal(rows(s).b.status,'blocked');
 await p.click('retry');s=p.snapshot('dependent-explicit-retry');assert.deepEqual(submits(s)[2].items.map(x=>x.itemId),['b']);assert.equal(s.flow.allSucceeded,true);assert.deepEqual(s.effects,{a:1,b:1,c:1});
});
await trial('DOM05-CANCEL-ALREADY-APPLIED-UNKNOWN','representative',async p=>{
 await p.click('start');let s=p.snapshot('applied-unknown');const c=rows(s).c.requestId;
 await p.click('cancel');s=p.snapshot('receipt-does-not-undo');assert.deepEqual(cancels(s),[{method:'cancel',itemId:'c',requestId:c}]);assert.equal(rows(s).c.status,'unknown');assert.equal(rows(s).a.status,'succeeded');assert.equal(s.flow.counts.cancelled,0);assert.deepEqual(s.effects,{a:1,b:0,c:1});assert.match(s.dom.rows.find(x=>x.id==='c').cells[2],/受付確認・元結果は別途確認/);
 await p.click('reconcile');s=p.snapshot('original-success-confirmed');assert.equal(rows(s).c.status,'succeeded');assert.equal(s.flow.counts.cancelled,0);assert.deepEqual(s.effects,{a:1,b:0,c:1});assert.equal(submits(s).length,1);
});
await trial('DOM06-FAILED-WITHOUT-UNAPPLIED','representative',async p=>{
 await p.change('scenario','ambiguous');await p.click('start');let s=p.snapshot('error-with-applied-effect');assert.equal(rows(s).c.status,'unknown');assert.deepEqual(s.flow.canRetryIds,[]);assert.deepEqual(s.effects,{a:1,b:1,c:1});assert.equal(s.flow.allSucceeded,false);
 await p.click('retry');await p.click('reconcile');s=p.snapshot('original-success-reconciled');assert.equal(s.flow.allSucceeded,true);assert.equal(submits(s).length,1);assert.deepEqual(s.effects,{a:1,b:1,c:1});
});
await trial('DOM07-EMPTY-SELECTION','representative',async p=>{
 await p.change('scenario','empty');p.snapshot('empty');for(const id of ['start','retry','reconcile','cancel','finish'])await p.click(id);const s=p.snapshot('no-operation');assert.equal(s.flow.total,0);assert.equal(s.flow.allSucceeded,false);assert.equal(s.flow.finished,false);assert.deepEqual(s.calls,[]);assert.deepEqual(s.effects,{a:0,b:0,c:0});assert.match(s.dom.summary,/選択されていません/);
});
await trial('EDOM01-LOOKUP-EXPIRED-IS-NOT-UNAPPLIED','exploratory',async p=>{
 await p.click('start');await p.change('expire',true);await p.click('reconcile');let s=p.snapshot('record-unavailable');assert.equal(rows(s).c.status,'unknown');assert.equal(rows(s).a.status,'succeeded');assert.deepEqual(s.flow.canRetryIds,[]);assert.equal(submits(s).length,1);
 await p.change('expire',false);await p.click('reconcile');s=p.snapshot('original-lookup-recovered');assert.equal(rows(s).c.status,'succeeded');assert.deepEqual(s.effects,{a:1,b:0,c:1});assert.equal(submits(s).length,1);
});
await trial('EDOM02-SUCCESS-AFTER-CANCEL-HAS-TERMINAL-COPY','exploratory',async p=>{
 await p.click('start');await p.click('cancel');await p.click('reconcile');const s=p.snapshot('success-already-confirmed');
 assert.equal(rows(s).c.status,'succeeded');assert.equal(s.flow.canReconcileIds.includes('c'),false);assert.deepEqual(s.effects,{a:1,b:0,c:1});
 assert.equal(s.dom.rows.find(x=>x.id==='c').cells[2].includes('元結果は別途確認'),false,'A confirmed successful original operation must not retain a prompt to separately check its already-known result.');
});
await trial('EDOM03-CANCELLED-HAS-TERMINAL-COPY','exploratory',async p=>{
 await p.change('scenario','lost');await p.click('start');await p.click('reconcile');await p.click('cancel');await p.click('reconcile');const s=p.snapshot('cancellation-already-confirmed');
 assert.equal(s.flow.finished,true);assert.equal(rows(s).b.status,'cancelled');assert.deepEqual(s.flow.canReconcileIds,[]);assert.deepEqual(s.effects,{a:1,b:0,c:0});
 assert.equal(s.dom.rows.find(x=>x.id==='b').cells[2].includes('元結果は別途確認'),false,'A confirmed cancelled original operation must not retain a prompt to separately check its already-known result.');
});
const report={runtime:{node:process.version,jsdom:require(`${jsdomPath}/package.json`).version},method:'Actual candidate HTML click/change handlers in jsdom; only the single ESM import is replaced by the exact imported candidate factory. No browser rendering, visual, AT, authorization, persistence, SDK, or human evaluation.',case_filter:caseFilter?[...caseFilter]:null,hashes:{module:hash(await readFile(modulePath)),html:hash(html)},counts:Object.fromEntries(['representative','exploratory'].map(kind=>[kind,{total:results.filter(x=>x.kind===kind).length,passed:results.filter(x=>x.kind===kind&&x.pass).length}])),results};
await writeFile(join(out,'dom-events.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({outputDir:out,counts:report.counts,failures:results.filter(x=>!x.pass).map(({id,error})=>({id,error}))}));process.exitCode=results.some(x=>!x.pass)?1:0;
