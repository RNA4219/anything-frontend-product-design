// Portable copy of independent DOM harness; parent changed only environment paths.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
const require=createRequire(import.meta.url);
const {JSDOM,VirtualConsole}=require(process.env.B_DOM_JSDOM_PATH||'jsdom');
const modulePath=resolve(process.argv[2]||'modules/interaction-ux-flow/examples/task-flows.mjs');
const htmlPath=resolve(process.argv[3]||'modules/interaction-ux-flow/examples/repair-and-undo.html');
const outputPath=resolve(process.argv[4]||'/tmp/session-b-round02-dom.json');
const factories=await import(pathToFileURL(modulePath));
const html=await readFile(htmlPath,'utf8');
const originalScript=html.match(/<script type="module">([\s\S]*?)<\/script>/)[1];
const expectedImport="import {createApplication,createReversal} from './task-flows.mjs';";
assert.equal(originalScript.split(expectedImport).length,2);
const normalize=x=>JSON.parse(JSON.stringify(x));
const sourceHash=createHash('sha256').update(await readFile(modulePath)).digest('hex');
const htmlHash=createHash('sha256').update(html).digest('hex');
const results=[],exploratory=[];
async function page(){
 const errors=[];const console=new VirtualConsole();console.on('jsdomError',e=>errors.push(e.message));
 const dom=new JSDOM(html,{url:'https://fixture.invalid/repair-and-undo.html',runScripts:'outside-only',virtualConsole:console});
 dom.window.__factories=factories;dom.window.eval(originalScript.replace(expectedImport,'const {createApplication,createReversal}=window.__factories;'));
 const w=dom.window,$=id=>w.document.getElementById(id);
 const flush=()=>new Promise(r=>setImmediate(r));
 const change=async(id,value)=>{$(id).value=value;$(id).dispatchEvent(new w.Event('change',{bubbles:true}));await flush();};
 const click=async id=>{$(id).click();await flush();};
 const snapshot=()=>normalize({app:w.taskDemo.application.view(),undo:w.taskDemo.getReversal().view(),item:w.taskDemo.getItem(),appCalls:w.taskDemo.appCalls,restoreCalls:w.taskDemo.getRestoreCalls(),dom:{addressHidden:$('address-row').hidden,reviewHidden:$('review-panel').hidden,answers:$('answers').textContent,errors:$('errors').textContent,appMessage:$('app-message').textContent,appResult:$('app-result').textContent,undoMessage:$('undo-message').textContent,undoDisabled:$('undo').disabled,checkHidden:$('undo-check').hidden,undoNext:$('undo-next').textContent,scope:$('undo-scope').textContent,residual:$('undo-residual').textContent,fixtureState:$('fixture-state').textContent}});
 return {dom,w,$,errors,change,click,snapshot};
}
async function trial(id,fn){const p=await page();try{const observations=await fn(p);assert.deepEqual(p.errors,[]);results.push({id,pass:true,observations});}catch(e){results.push({id,pass:false,error:e.stack,snapshot:p.snapshot()});}finally{p.dom.window.close();}}
await trial('DOM-REPAIR',async p=>{
 const initial=p.snapshot().app.draft;
 await p.click('review');assert.equal(p.$('review-panel').hidden,false);assert.equal(p.w.taskDemo.appCalls.length,0);
 await p.click('submit');let s=p.snapshot();assert.equal(s.app.phase,'editing');assert.deepEqual(s.app.draft,initial);assert.deepEqual(Object.keys(s.app.errors),['email']);assert.ok(p.$('errors').querySelector('a[href="#email"]'));
 const rejected=s;await p.change('app-mode','normal');await p.change('email','new@example.test');await p.click('review');s=p.snapshot();assert.equal(s.app.phase,'review');assert.match(s.dom.answers,/new@example.test/);assert.equal(s.app.draft.address,initial.address);
 await p.click('change-email');assert.equal(p.w.document.activeElement.id,'email');assert.equal(p.w.taskDemo.appCalls.length,1);await p.click('review');await p.click('submit');s=p.snapshot();assert.equal(s.app.phase,'submitted');assert.equal(s.appCalls.length,2);assert.equal(s.appCalls[1].answers.email,'new@example.test');assert.match(s.dom.appResult,/demo-/);return {rejected,completed:s};
});
await trial('DOM-DELIVERY',async p=>{
 await p.change('app-mode','normal');await p.change('delivery','pickup');assert.equal(p.$('address-row').hidden,true);await p.click('review');let s=p.snapshot();assert.equal(Object.hasOwn(s.app.effective,'address'),false);assert.equal(s.app.draft.address,'1 Example Street');await p.click('submit');s=p.snapshot();assert.equal(s.app.phase,'submitted');assert.equal(Object.hasOwn(s.appCalls[0].answers,'address'),false);return s;
});
await trial('DOM-LOST-REPLY',async p=>{
 await p.change('app-mode','lost');await p.click('review');await p.click('submit');let s=p.snapshot();assert.equal(s.app.phase,'unknown');const id=s.app.operationId;assert.equal(s.app.canCheck,true);await p.click('app-check');s=p.snapshot();assert.equal(s.app.phase,'submitted');assert.equal(s.app.operationId,id);assert.equal(s.appCalls.length,1);return s;
});
await trial('DOM-COMPENSATION-FAILED',async p=>{
 await p.change('undo-mode','async-failed');await p.click('undo');let s=p.snapshot();assert.equal(s.undo.phase,'pending');assert.equal(s.item.archived,true);assert.equal(s.dom.checkHidden,false);const pending=s;await p.click('undo-check');s=p.snapshot();assert.equal(s.undo.phase,'failed');assert.equal(s.item.archived,true);assert.match(s.dom.undoNext,new RegExp(s.undo.operationId));assert.equal(s.restoreCalls.length,1);return {pending,failed:s};
});
await trial('DOM-COMPENSATION-SUCCESS',async p=>{
 await p.change('undo-mode','async-success');await p.click('undo');assert.equal(p.snapshot().undo.phase,'pending');await p.click('undo-check');const s=p.snapshot();assert.equal(s.undo.phase,'restored');assert.equal(s.item.archived,false);assert.match(s.dom.scope,/アーカイブ状態/);assert.match(s.dom.residual,/通知は取り消されません/);return s;
});
await trial('DOM-EXPIRED',async p=>{
 await p.change('undo-mode','expired');assert.equal(p.$('undo').disabled,true);await p.click('undo');const s=p.snapshot();assert.equal(s.undo.phase,'expired');assert.equal(s.item.archived,true);assert.equal(s.restoreCalls.length,0);assert.match(s.dom.undoMessage,/期限/);return s;
});
await trial('DOM-CONFLICT',async p=>{
 await p.change('undo-mode','conflict');await p.click('undo');const s=p.snapshot();assert.equal(s.undo.phase,'conflict');assert.equal(s.item.archived,true);assert.equal(s.item.revision,2);assert.equal(s.restoreCalls[0].expectedRevision,1);assert.match(s.dom.undoMessage,/上書きしていません/);return s;
});
await trial('DOM-LOCAL-UNDO',async p=>{
 let confirms=0;p.w.confirm=()=>{confirms++;return true;};await p.click('undo');const s=p.snapshot();assert.equal(s.undo.phase,'restored');assert.equal(s.item.archived,false);assert.equal(s.restoreCalls.length,1);assert.equal(confirms,0);return {...s,confirmCalls:confirms};
});
// Not added to the fixed 16-case score: dependency-error removal found by the independent critic.
const p=await page();
try{
 await p.change('app-mode','normal');await p.change('address','');await p.click('review');const invalidShipping=p.snapshot();
 assert.equal(invalidShipping.app.phase,'editing');assert.ok(invalidShipping.app.errors.address);
 await p.change('delivery','pickup');await p.click('review');const afterBranchChange=p.snapshot();
 const pass=afterBranchChange.app.phase==='review' && !Object.hasOwn(afterBranchChange.app.errors,'address');
 exploratory.push({id:'E01-INACTIVE-ERROR',expected:'Pickup has no address requirement; the old address error must not block review.',pass,invalidShipping,afterBranchChange});
}finally{p.dom.window.close();}
const report={runtime:{node:process.version,jsdom:require('/workspace/scratch/e05a84d14c1b/testing-C/node_modules/jsdom/package.json').version},method:'Real HTML event listeners in jsdom; the one ESM import is replaced by factories imported from the exact candidate module. No browser, layout, AT, keyboard-human, server, or human study.',modulePath,htmlPath,sourceHash,htmlHash,representative:{total:results.length,passed:results.filter(x=>x.pass).length,results},exploratory};
await writeFile(outputPath,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({representative:{total:results.length,passed:results.filter(x=>x.pass).length},exploratory:exploratory.map(({id,pass})=>({id,pass})),sourceHash,htmlHash}));
process.exitCode=results.some(x=>!x.pass)||exploratory.some(x=>!x.pass)?1:0;
