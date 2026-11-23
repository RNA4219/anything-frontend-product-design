import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
const require=createRequire(import.meta.url);
const jsdomPath=process.env.B_DOM_JSDOM_PATH||'jsdom';
const {JSDOM,VirtualConsole}=require(jsdomPath);
const base=resolve(process.env.B_REPO_ROOT||process.cwd());
const modulePath=resolve(process.argv[2]||`${base}/modules/interaction-ux-flow/examples/resume-and-conflict.mjs`);
const htmlPath=resolve(process.argv[3]||`${base}/modules/interaction-ux-flow/examples/resume-and-conflict.html`);
const outputDir=resolve(process.env.B_CRITIC_OUTPUT_DIR||'artifacts/critic-r03');
await mkdir(outputDir,{recursive:true});
const outputPath=resolve(process.argv[4]||`${outputDir}/dom-events.json`);
const factories=await import(pathToFileURL(modulePath));
const html=await readFile(htmlPath,'utf8');
const originalScript=html.match(/<script type="module">([\s\S]*?)<\/script>/)[1];
const expectedImport="import {createResumableEdit} from './resume-and-conflict.mjs';";
assert.equal(originalScript.split(expectedImport).length,2);
const normal=x=>JSON.parse(JSON.stringify(x));
const hashes={module:createHash('sha256').update(await readFile(modulePath)).digest('hex'),html:createHash('sha256').update(html).digest('hex')};
const representative=[],exploratory=[];
async function page(){
 const errors=[],events=[];const vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
 const dom=new JSDOM(html,{url:'https://fixture.invalid/resume-and-conflict.html',runScripts:'outside-only',virtualConsole:vc});
 dom.window.__factories=factories;
 dom.window.eval(originalScript.replace(expectedImport,'const {createResumableEdit}=window.__factories;'));
 const w=dom.window,$=id=>w.document.getElementById(id);
 const flush=()=>new Promise(r=>setImmediate(r));
 const change=async(id,value)=>{const el=$(id);if(el.type==='checkbox')el.checked=value;else el.value=value;el.dispatchEvent(new w.Event('change',{bubbles:true}));events.push({type:'change',id,value});await flush();};
 const click=async id=>{events.push({type:'click',id,disabled:$(id).disabled});$(id).click();await flush();};
 const snapshot=()=>normal({flow:w.resumeDemo.getFlow().view(),server:w.resumeDemo.getServer(),calls:w.resumeDemo.apiCalls,effects:w.resumeDemo.getEffects(),dom:{workHidden:$('work').hidden,fixtureHidden:$('fixture').hidden,status:$('status').textContent,title:$('title').value,titleDisabled:$('title').disabled,reauthHidden:$('reauth').hidden,resumeDisabled:$('resume').disabled,reviewDisabled:$('review').disabled,reviewHidden:$('review-panel').hidden,reviewText:$('review-text').textContent,commitDisabled:$('commit').disabled,saved:$('saved-value').textContent,observed:$('observed-value').textContent,readError:$('read-error').textContent,operation:$('operation-result').textContent,reference:$('operation-reference').textContent,recovery:$('recovery').textContent,workText:$('work').textContent,effects:$('effects').textContent}});
 return {dom,w,$,errors,events,change,click,snapshot};
}
async function trial(collection,id,fn){const p=await page();try{const observations=await fn(p);assert.deepEqual(p.errors,[]);collection.push({id,pass:true,events:p.events,observations});}catch(e){collection.push({id,pass:false,error:e.message,events:p.events,observations:p.snapshot(),runtimeErrors:p.errors});}finally{p.dom.window.close();}}
await trial(representative,'DOM01-UNSENT',async p=>{
 await p.click('resume');const s=p.snapshot();assert.equal(s.flow.phase,'editing');assert.equal(s.flow.draft.title,'My draft title');assert.equal(s.flow.observedResource.values.title,'Original title');assert.match(s.dom.status,/未送信/);assert.equal(s.calls.filter(x=>x.method==='update').length,0);return s;
});
await trial(representative,'DOM02-ACCOUNT-MISMATCH',async p=>{
 await p.change('lose-reply',true);await p.click('resume');await p.click('review');await p.click('commit');assert.equal(p.snapshot().flow.phase,'unknown');const before=p.snapshot();await p.change('session','B');await p.click('resume');const s=p.snapshot();assert.equal(s.calls.length,before.calls.length);assert.equal(s.flow.phase,'different_account');assert.equal(s.dom.workHidden,true);assert.equal(s.dom.fixtureHidden,true);assert.equal(s.dom.title,'');assert.equal(s.flow.draft,null);assert.equal(s.flow.operationId,null);assert.equal(s.dom.reference,'');assert.equal(s.dom.operation,'');assert.equal(s.dom.workText.includes('My draft title'),false);assert.equal(s.dom.workText.includes('Original title'),false);return {before,after:s};
});
await trial(representative,'DOM03-EXPIRED-REAUTH',async p=>{
 await p.change('lose-reply',true);await p.click('resume');await p.click('review');await p.click('commit');const operationId=p.snapshot().flow.operationId;const calls=p.snapshot().calls.length;await p.change('session','expired');assert.equal(p.snapshot().flow.phase,'reauthenticate');assert.equal(p.snapshot().dom.workHidden,true);assert.equal(p.snapshot().dom.reauthHidden,false);assert.equal(p.snapshot().calls.length,calls);await p.click('reauth');const s=p.snapshot();assert.equal(s.flow.phase,'completed');assert.equal(s.flow.operationId,operationId);assert.equal(s.calls.filter(x=>x.method==='lookup').at(-1).operationId,operationId);assert.equal(s.effects,1);return s;
});
await trial(representative,'DOM04-READONLY',async p=>{
 await p.change('session','expired');await p.change('session','readonly');await p.click('resume');await p.click('review');await p.click('commit');const s=p.snapshot();assert.equal(s.flow.phase,'readonly');assert.equal(s.dom.titleDisabled,true);assert.equal(s.dom.reviewDisabled,true);assert.equal(s.calls.filter(x=>x.method==='update').length,0);assert.equal(s.effects,0);assert.match(s.dom.status,/閲覧のみ/);return s;
});
await trial(representative,'DOM05-CONFLICT-NEW-REVIEW',async p=>{
 await p.click('resume');await p.change('title','I choose this title');await p.click('review');await p.click('external-change');await p.click('commit');const conflict=p.snapshot();assert.equal(conflict.flow.phase,'conflict');assert.equal(conflict.flow.draft.title,'I choose this title');assert.equal(conflict.server.values.title,'Other editor title');assert.equal(conflict.effects,0);assert.equal(conflict.dom.reviewHidden,true);assert.match(conflict.dom.status,/比較して確認し直し/);assert.match(conflict.dom.observed,/Other editor title/);await p.click('commit');assert.equal(p.snapshot().calls.filter(x=>x.method==='update').length,1);await p.click('review');assert.match(p.snapshot().dom.reviewText,/Other editor title/);await p.click('commit');const s=p.snapshot();assert.equal(s.effects,1);assert.equal(s.server.values.title,'I choose this title');assert.equal(s.calls.filter(x=>x.method==='update').at(-1).ifMatch,conflict.server.etag);return {conflict,confirmed:s};
});
await trial(representative,'DOM06-LOST-REPLY-REOPEN',async p=>{
 await p.change('lose-reply',true);await p.click('resume');await p.click('review');await p.click('commit');const before=p.snapshot();assert.equal(before.flow.phase,'unknown');assert.equal(before.effects,1);await p.click('reopen');const s=p.snapshot();assert.equal(s.flow.phase,'completed');assert.equal(s.flow.operationId,before.flow.operationId);assert.equal(s.calls.filter(x=>x.method==='update').length,1);assert.equal(s.calls.filter(x=>x.method==='lookup').at(-1).operationId,before.flow.operationId);assert.equal(s.effects,1);return {before,after:s};
});
await trial(representative,'DOM07-SUCCESS-CURRENT-READ-FAILS',async p=>{
 await p.click('resume');await p.click('review');await p.change('read-fails',true);await p.click('commit');let s=p.snapshot();assert.equal(s.flow.phase,'completed');assert.equal(s.flow.operationOutcome,'succeeded');assert.equal(s.flow.observedResource,null);assert.match(s.dom.operation,/My draft title/);assert.match(s.dom.readError,/照合できません/);const before=s;await p.click('reopen');s=p.snapshot();assert.equal(s.flow.phase,'completed');assert.equal(s.effects,1);assert.equal(s.flow.observedResource,null);assert.match(s.dom.operation,/My draft title/);return {before,after:s};
});
await trial(representative,'DOM08-OPERATION-AND-CURRENT-DIFFER',async p=>{
 await p.click('resume');await p.click('review');await p.click('commit');await p.click('external-change');await p.click('reopen');const s=p.snapshot();assert.equal(s.flow.phase,'completed');assert.equal(s.flow.operationResult.values.title,'My draft title');assert.equal(s.flow.observedResource.values.title,'Other editor title');assert.match(s.dom.operation,/My draft title/);assert.match(s.dom.observed,/Other editor title/);assert.equal(s.effects,1);return s;
});
// Exploratory checks are not additions to the frozen 13-case score.
await trial(exploratory,'E01-CONFIRMED-SUCCESS-REOPEN-EXPIRED',async p=>{
 await p.click('resume');await p.click('review');await p.click('commit');assert.equal(p.snapshot().flow.operationOutcome,'succeeded');await p.change('record-expires',true);await p.click('reopen');const s=p.snapshot();assert.equal(s.flow.operationOutcome,'succeeded','A known correlated success must survive this same-page snapshot reopen, even when lookup record expires.');assert.equal(s.flow.phase,'completed');assert.equal(s.effects,1);return s;
});
await trial(exploratory,'E02-SENT-INPUT-NOT-LABELLED-UNSENT',async p=>{
 await p.click('resume');await p.click('review');await p.click('commit');const s=p.snapshot();assert.equal(s.flow.phase,'completed');assert.equal(s.dom.workText.includes('下書きは未送信の入力です。'),false,'After confirming the submitted title succeeded, its displayed input must not be described unconditionally as unsent.');return s;
});
const report={runtime:{node:process.version,jsdom:require(`${jsdomPath}/package.json`).version},method:'Actual candidate HTML click/change listeners executed in jsdom. Only the single ESM import was replaced with the exact imported candidate factory. No real browser, visual, AT, or human evidence.',modulePath,htmlPath,hashes,representative:{total:representative.length,passed:representative.filter(x=>x.pass).length,results:representative},exploratory:{total:exploratory.length,passed:exploratory.filter(x=>x.pass).length,results:exploratory}};
await writeFile(outputPath,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({representative:{total:representative.length,passed:report.representative.passed},exploratory:exploratory.map(({id,pass,error})=>({id,pass,error})),hashes}));
process.exitCode=representative.some(x=>!x.pass)||exploratory.some(x=>!x.pass)?1:0;
