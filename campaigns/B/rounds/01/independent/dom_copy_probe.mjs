import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const require=createRequire(import.meta.url);
const {JSDOM}=require(process.env.B_DOM_JSDOM_PATH || 'jsdom');
const ROOT=process.cwd();
const OUT=process.argv[2] || '/tmp/session-b-dom';await mkdir(OUT,{recursive:true});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const results=[];
async function run(arm,scenario){
 const dir=`${ROOT}/campaigns/B/rounds/01/artifacts/${arm}`;
 const html=await readFile(`${dir}/index.html`,'utf8');
 const hashesBefore={};for(const name of ['flow.mjs','index.html','mock-service.mjs',...(arm==='candidate'?['app.mjs']:[])])hashesBefore[name]=createHash('sha256').update(await readFile(`${dir}/${name}`)).digest('hex');
 const flowModule=await import(pathToFileURL(`${dir}/flow.mjs`));
 const mockModule=await import(pathToFileURL(`${dir}/mock-service.mjs`));
 const moduleText=arm==='baseline'?html.match(/<script type="module">([\s\S]*?)<\/script>/)[1]:await readFile(`${dir}/app.mjs`,'utf8');
 const dom=new JSDOM(html,{url:`http://critic.local/${arm}/${scenario}/`,runScripts:'outside-only'});
 const w=dom.window;const errors=[],apiEvents=[];let flow,service;
 w.addEventListener('error',e=>errors.push(e.message));
 w.createFlow=(...a)=>(flow=flowModule.createFlow(...a));
 w.createMockService=(...a)=>{
  service=mockModule.createMockService(...a);const target=service.api??service;
  for(const method of ['submit','lookup','cancel']){const original=target[method];target[method]=async(...args)=>{
   apiEvents.push({method,stage:'start',at:Date.now(),args,mockStoredState:arm==='candidate'?JSON.parse(w.localStorage.getItem('booking-change-mock-v1')||'null'):null});
   try{const result=await original(...args);apiEvents.push({method,stage:'returned',at:Date.now(),result});return result;}
   catch(e){apiEvents.push({method,stage:'threw',at:Date.now(),error:e.message});throw e;}
  };}return service;
 };
 w.INITIAL_DATE=mockModule.INITIAL_DATE;w.SCENARIOS=mockModule.SCENARIOS;
 w.eval(moduleText.replace(/^\s*import\s+.*?;\s*$/gm,''));
 const d=w.document;const $=id=>d.getElementById(id);
 const sequence=[];
 function visibleText(el){
  if(!el||el.closest('[hidden]')||['SCRIPT','STYLE','NOSCRIPT'].includes(el.tagName))return '';
  return [...el.childNodes].map(n=>n.nodeType===3?n.textContent:n.nodeType===1?visibleText(n):'').join(' ').replace(/\s+/g,' ').trim();
 }
 function snap(stage,extra={}){
  const state=flow.view();
  const ids=arm==='baseline'?['status-title','status-message','confirmed-date','from-label','from-date','target-date','request-id']:['phase-label','status-message','current-date','draft-date','known-note','operation-id','finished-detail'];
  sequence.push({stage,state,fields:Object.fromEntries(ids.map(id=>[id,$(id)?.textContent??null])),bookingLabel:d.querySelector(arm==='baseline'?'.booking-label':'.columns .label')?.textContent,badge:d.querySelector('.badge')?.textContent,visibleText:visibleText(d.querySelector('main')),...extra});
 }
 function click(id){const e=$(id);if(!e)throw Error('missing '+id);if(e.disabled||e.closest('[hidden]'))throw Error('nonoperable '+id);e.click();}
 const selector=$(arm==='baseline'?'scenario-select':'scenario');
 selector.value=scenario==='race'?(arm==='baseline'?'cancellation_race':'race'):scenario;
 selector.dispatchEvent(new w.Event('change',{bubbles:true}));
 snap('initial');
 const radio=d.querySelector('input[value="2026-12-10T14:00"]');radio.checked=true;radio.dispatchEvent(new w.Event('change',{bubbles:true}));
 click('review-button');snap('review');
 click('confirm-button');snap('submit_in_flight');await sleep(600);snap('submit_settled');
 if(scenario==='lost'){
  click('check-button');await sleep(450);snap('early_check');
  await sleep(1850);
  const backend=arm==='baseline'?await service.api.lookup(flow.view().operationId):service.inspect();
  snap('backend_completed_before_ui_check',{backendObservation:backend});
  click('check-button');await sleep(450);snap('checked_success');
 } else if(scenario==='normal'){
  await sleep(2200);snap('before_success_check');click('check-button');await sleep(450);snap('checked_success');
 } else if(scenario==='cancellation'||scenario==='race'){
  click('cancel-button');snap('cancel_in_flight');await sleep(450);snap('cancel_acknowledged');
  await sleep(1700);click('check-button');await sleep(450);snap(scenario==='race'?'race_checked_success':'checked_cancellation');
 } else if(scenario==='rejected'){snap('known_rejection');}
 const hashes={};for(const name of ['flow.mjs','index.html','mock-service.mjs',...(arm==='candidate'?['app.mjs']:[])])hashes[name]=createHash('sha256').update(await readFile(`${dir}/${name}`)).digest('hex');
 const record={arm,scenario,method:'Actual click/change events in jsdom 26.1.0; actual controller and mock imports injected into original module body; no source edits.',sequence,errors,hashes,hashesBefore,filesStable:JSON.stringify(hashesBefore)===JSON.stringify(hashes),apiEvents};
 results.push(record);await writeFile(`${OUT}/dom-${arm}-${scenario}.json`,JSON.stringify(record,null,2)+'\n');
 service.dispose?.();dom.window.close();
 return {arm,scenario,phases:sequence.map(x=>[x.stage,x.state.phase]),errors};
}
const jobs=[];for(const arm of ['baseline','candidate'])for(const scenario of ['lost','normal','cancellation','race','rejected'])jobs.push(run(arm,scenario));
console.log(JSON.stringify(await Promise.allSettled(jobs),null,2));
await writeFile(`${OUT}/dom-copy-results.json`,JSON.stringify({method:'Exploratory DOM examination, not additions to frozen scoring suite',results,limitations:['No real browser layout, screenshots, accessibility tree, or user comprehension study.','Node imports use actual host timers and local mock service; no production backend.','Scenario selection and real input/click handlers are exercised; ES module imports are injected because jsdom does not execute module scripts natively.']},null,2)+'\n');
