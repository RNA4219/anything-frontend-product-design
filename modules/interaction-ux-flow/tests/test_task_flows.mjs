// R02 behavioral cases frozen before implementation; pure fixture adapters.
import assert from 'node:assert/strict';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {readFile,writeFile} from 'node:fs/promises';
const modulePath=process.argv[2]||'modules/interaction-ux-flow/examples/task-flows.mjs';
const {createApplication,createReversal}=await import(pathToFileURL(resolve(modulePath)));
const cases=JSON.parse(await readFile('campaigns/B/rounds/02/cases.json','utf8')).cases;
const results=[];
const initial={name:'Aki',email:'old@example.test',delivery:'shipping',address:'1 Example Street'};
async function trial(id,run){try{await run();results.push({id,pass:true});}catch(e){results.push({id,pass:false,error:e.message});}}
function application({result={status:'succeeded',reference:'A-1'},throwReply=false,deferred=false}={}){
 const calls=[];let next=0,finish;const api={submit:async data=>{calls.push(structuredClone(data));if(throwReply)throw Error('lost');if(deferred)return await new Promise(r=>finish=r);return result;},lookup:async()=>({status:'succeeded',reference:'A-1'})};
 return {flow:createApplication(api,{initial,nextId:()=>`apply-${++next}`}),calls,finish:x=>finish(x)};
}
function reversal({result={status:'restored'},now=500,deadline=1000,actualRevision=3,kind='local',throwReply=false}={}){
 const state={id:'item-1',revision:actualRevision,archived:true};const calls=[];let time=now,seq=0;
 const api={restore:async data=>{calls.push(structuredClone(data));if(data.expectedRevision!==state.revision)return {status:'conflict'};if(throwReply)throw Error('lost');if(result.status==='restored'){state.archived=false;state.revision++;}return {...result,reference:data.requestId};},lookup:async()=>{state.archived=false;return {status:'restored'};}};
 const flow=createReversal(api,{kind,itemId:state.id,expectedRevision:3,validUntil:deadline,now:()=>time,nextId:()=>`undo-${++seq}`,scope:'archive flag',residualEffects:['notification remains'],recoveryAction:'Open the item history'});
 return {flow,state,calls,setTime:t=>time=t};
}
await trial('F01',async()=>{const x=application();x.flow.review();x.flow.change('email');assert.equal(x.calls.length,0);assert.equal(x.flow.view().draft.name,'Aki');});
await trial('F02',async()=>{const x=application({result:{status:'invalid',fieldErrors:{email:'Enter an address you can receive mail at'}}});x.flow.review();await x.flow.submit();const v=x.flow.view();assert.deepEqual(v.draft,initial);assert.deepEqual(Object.keys(v.errors),['email']);assert.ok(v.errors.email);assert.notEqual(v.phase,'submitted');x.flow.set('email','new@example.test');x.flow.review();assert.equal(x.flow.view().draft.address,initial.address);});
await trial('F03',async()=>{const x=application();x.flow.review();x.flow.change('email');x.flow.set('email','new@example.test');await x.flow.submit();assert.equal(x.calls.length,0);x.flow.review();await x.flow.submit();assert.equal(x.calls.length,1);assert.equal(x.calls[0].answers.email,'new@example.test');});
await trial('F04',async()=>{const x=application();x.flow.review();x.flow.change('delivery');x.flow.set('delivery','pickup');x.flow.review();await x.flow.submit();assert.equal(x.calls[0].answers.delivery,'pickup');assert.equal(Object.hasOwn(x.calls[0].answers,'address'),false);assert.equal(x.flow.view().draft.address,initial.address);});
await trial('F05',async()=>{const x=application({result:{status:'failed',message:'Service unavailable'}});x.flow.review();await x.flow.submit();assert.deepEqual(x.flow.view().errors,{});assert.ok(x.flow.view().formError);assert.deepEqual(x.flow.view().draft,initial);});
await trial('F06',async()=>{const x=application({throwReply:true});x.flow.review();await x.flow.submit();const id=x.flow.view().operationId;await x.flow.submit();assert.equal(x.calls.length,1);assert.equal(x.flow.view().phase,'unknown');assert.equal(x.flow.view().operationId,id);assert.deepEqual(x.flow.view().draft,initial);await x.flow.check();assert.equal(x.flow.view().phase,'submitted');assert.equal(x.calls.length,1);});
await trial('F07',async()=>{const x=application({deferred:true});x.flow.review();const a=x.flow.submit(),b=x.flow.submit();assert.equal(x.calls.length,1);x.finish({status:'succeeded',reference:'A-1'});await Promise.all([a,b]);assert.equal(x.flow.view().phase,'submitted');});
await trial('U01',async()=>{const x=reversal();await x.flow.undo();assert.equal(x.state.archived,false);assert.equal(x.calls.length,1);assert.equal(x.calls[0].itemId,'item-1');assert.equal(x.flow.view().phase,'restored');});
await trial('U02',async()=>{const x=reversal({now:1000});await x.flow.undo();assert.equal(x.calls.length,0);assert.equal(x.state.archived,true);assert.notEqual(x.flow.view().phase,'restored');assert.equal(x.flow.view().canUndo,false);});
await trial('U03',async()=>{const x=reversal({actualRevision:4});await x.flow.undo();assert.equal(x.calls[0].expectedRevision,3);assert.equal(x.state.revision,4);assert.equal(x.state.archived,true);assert.equal(x.flow.view().phase,'conflict');});
await trial('U04',async()=>{const x=reversal({kind:'compensation',result:{status:'pending'}});await x.flow.undo();assert.equal(x.state.archived,true);assert.equal(x.flow.view().phase,'pending');assert.equal(x.flow.view().canCheck,true);});
await trial('U05',async()=>{const x=reversal({kind:'compensation',result:{status:'failed',message:'Insufficient balance'}});await x.flow.undo();assert.equal(x.state.archived,true);assert.equal(x.flow.view().phase,'failed');assert.equal(x.flow.view().nextAction,'Open the item history');assert.ok(x.flow.view().operationId);});
await trial('U06',async()=>{const x=reversal({kind:'compensation'});await x.flow.undo();assert.equal(x.state.archived,false);assert.equal(x.flow.view().scope,'archive flag');assert.deepEqual(x.flow.view().residualEffects,['notification remains']);assert.equal(x.flow.view().phase,'restored');});
await trial('U07',async()=>{const x=reversal({kind:'compensation',throwReply:true});await x.flow.undo();assert.equal(x.flow.view().phase,'unknown');const id=x.flow.view().operationId;assert.ok(id);assert.equal(x.flow.view().canCheck,true);await x.flow.check();assert.equal(x.flow.view().phase,'restored');assert.equal(x.flow.view().operationId,id);});
await trial('U08',async()=>{const x=reversal({kind:'compensation',result:{status:'pending'}});await x.flow.undo();await x.flow.undo();assert.equal(x.calls.length,1);assert.equal(x.state.archived,true);});
await trial('U09',async()=>{const x=reversal({kind:'compensation',result:{status:'pending'}});await x.flow.undo();x.setTime(1500);assert.equal(x.flow.view().canUndo,false);assert.equal(x.flow.view().canCheck,true);await x.flow.check();assert.equal(x.flow.view().phase,'restored');});
const report={suite:'B-R02-task-flows-v1',module:modulePath,total:results.length,passed:results.filter(x=>x.pass).length,failed:results.filter(x=>!x.pass).length,results:results.map(x=>({...x,expected:cases.find(c=>c.id===x.id).expected})),limits:['Synthetic task/service fixture; no real service or human study.','Deliberate mutants are negative controls, not generated baseline arms.']};
if(process.argv[3])await writeFile(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({suite:report.suite,total:report.total,passed:report.passed,failed:report.failed,failures:report.results.filter(x=>!x.pass)}));process.exitCode=report.failed?1:0;
