// Frozen behavioral trials for generated controllers; Node built-ins only.
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {writeFile} from 'node:fs/promises';

const OLD='2026-12-08T14:00', NEW='2026-12-10T14:00', OTHER='2026-12-11T14:00';
const {createFlow}=await import(pathToFileURL(process.argv[2]).href);
const results=[];
function setup({submitResult={status:'succeeded',currentDate:NEW},lookupResult,
  submitError=false,lookupError=false,deferred=false,cancelError=false}={}) {
  const calls={submit:[],lookup:[],cancel:[]};let seq=0,resolve;
  let lookup=lookupResult??{status:'succeeded',currentDate:NEW};
  const api={
    async submit(x){calls.submit.push(structuredClone(x));if(submitError)throw Error('connection lost');
      if(deferred)return await new Promise(r=>{resolve=r;});return structuredClone(submitResult);},
    async lookup(id){calls.lookup.push(id);if(lookupError)throw Error('offline');return structuredClone(lookup);},
    async cancel(id){calls.cancel.push(id);if(cancelError)throw Error('connection lost');return {accepted:true};}
  };
  const flow=createFlow(api,{bookingId:'R-204',currentDate:OLD,nextId:()=>`intent-${++seq}`});
  return {flow,calls,setLookup:x=>{lookup=x},finish:x=>resolve(x)};
}
async function ready(x){await x.flow.choose(NEW);await x.flow.review();}
async function trial(id,title,fn){try{await fn();results.push({id,title,pass:true});}
  catch(e){results.push({id,title,pass:false,error:String(e.message)});}}

await trial('T01','Review has no side effect; acknowledged success updates confirmed data',async()=>{
  const x=setup();await ready(x);assert.equal(x.calls.submit.length,0);assert.equal(x.flow.view().currentDate,OLD);
  await x.flow.confirm();assert.equal(x.flow.view().currentDate,NEW);assert.equal(x.flow.view().phase,'succeeded');
});
await trial('T02','Known rejection preserves previous reservation and entered choice',async()=>{
  const x=setup({submitResult:{status:'failed',message:'slot taken'}});await ready(x);await x.flow.confirm();
  assert.equal(x.flow.view().currentDate,OLD);assert.equal(x.flow.view().draftDate,NEW);assert.equal(x.flow.view().phase,'failed');
  assert.ok(x.flow.view().message);await x.flow.choose(OTHER);await x.flow.review();assert.equal(x.flow.view().draftDate,OTHER);
});
await trial('T03','Lost response cannot authorize a second mutation',async()=>{
  const x=setup({submitError:true});await ready(x);await x.flow.confirm();assert.equal(x.flow.view().phase,'unknown');
  assert.equal(x.flow.view().canSubmit,false);assert.equal(x.flow.view().canCheck,true);
  await x.flow.confirm();assert.equal(x.calls.submit.length,1);assert.equal(x.flow.view().currentDate,OLD);
});
await trial('T04','Reconciliation confirms result without resubmitting',async()=>{
  const x=setup({submitError:true});await ready(x);await x.flow.confirm();await x.flow.check();
  assert.equal(x.flow.view().currentDate,NEW);assert.equal(x.flow.view().phase,'succeeded');assert.equal(x.calls.submit.length,1);
  assert.equal(x.calls.lookup[0],x.calls.submit[0].requestId);
});
await trial('T05','Pending lookup keeps the intended change unresolved',async()=>{
  const x=setup({submitError:true,lookupResult:{status:'pending',currentDate:OLD}});await ready(x);await x.flow.confirm();await x.flow.check();
  assert.equal(x.flow.view().currentDate,OLD);assert.equal(x.flow.view().canSubmit,false);assert.equal(x.flow.view().canCheck,true);
  assert.notEqual(x.flow.view().phase,'succeeded');
});
await trial('T06','Cancellation acknowledgement is not a cancelled operation',async()=>{
  const x=setup({submitResult:{status:'pending'}});await ready(x);await x.flow.confirm();await x.flow.cancel();
  assert.equal(x.calls.cancel.length,1);assert.notEqual(x.flow.view().phase,'cancelled');assert.notEqual(x.flow.view().phase,'succeeded');
  assert.equal(x.flow.view().canSubmit,false);assert.equal(x.flow.view().canCheck,true);
});
await trial('T07','Completion can win a cancellation race',async()=>{
  const x=setup({submitResult:{status:'pending'}});await ready(x);await x.flow.confirm();await x.flow.cancel();await x.flow.check();
  assert.equal(x.flow.view().phase,'succeeded');assert.equal(x.flow.view().currentDate,NEW);
});
await trial('T08','Confirmed cancellation preserves original and new intent gets new identity',async()=>{
  const x=setup({submitResult:{status:'pending'},lookupResult:{status:'cancelled',currentDate:OLD}});
  await ready(x);await x.flow.confirm();const first=x.calls.submit[0].requestId;await x.flow.cancel();await x.flow.check();
  assert.equal(x.flow.view().phase,'cancelled');assert.equal(x.flow.view().currentDate,OLD);
  await x.flow.choose(OTHER);await x.flow.review();await x.flow.confirm();assert.equal(x.calls.submit.length,2);
  assert.notEqual(x.calls.submit[1].requestId,first);assert.equal(x.calls.submit[1].targetDate,OTHER);
});
await trial('T09','Rapid duplicate activation creates one operation',async()=>{
  const x=setup({deferred:true});await ready(x);const a=x.flow.confirm();const b=x.flow.confirm();
  assert.equal(x.calls.submit.length,1);assert.equal(x.flow.view().currentDate,OLD);x.finish({status:'succeeded',currentDate:NEW});
  await Promise.all([a,b]);assert.equal(x.flow.view().currentDate,NEW);
});
await trial('T10','Reconciliation failure keeps recovery available and entered data intact',async()=>{
  const x=setup({submitError:true,lookupError:true});await ready(x);await x.flow.confirm();await x.flow.check();
  assert.equal(x.flow.view().phase,'unknown');assert.equal(x.flow.view().canSubmit,false);assert.equal(x.flow.view().canCheck,true);
  assert.equal(x.flow.view().draftDate,NEW);assert.ok(x.flow.view().message);
});
await trial('T11','Editing a reviewed choice requires reviewing the changed choice',async()=>{
  const x=setup();await ready(x);await x.flow.back();await x.flow.choose(OTHER);await x.flow.confirm();
  assert.equal(x.calls.submit.length,0);await x.flow.review();await x.flow.confirm();assert.equal(x.calls.submit[0].targetDate,OTHER);
});
await trial('T12','Non-authoritative lookup miss does not prove no side effect',async()=>{
  const x=setup({submitError:true,lookupResult:{status:'not_found'}});await ready(x);await x.flow.confirm();await x.flow.check();
  assert.equal(x.flow.view().canSubmit,false);assert.equal(x.flow.view().canCheck,true);
  assert.ok(!['succeeded','cancelled','failed'].includes(x.flow.view().phase));assert.equal(x.calls.submit.length,1);
});
const out={suite:'B-R01-flow-trials-v1',controller:process.argv[2],total:results.length,passed:results.filter(x=>x.pass).length,
  failed:results.filter(x=>!x.pass).length,results,limits:['Synthetic service adapter; no live backend or human participants','Tests observe controller and rendered prototype separately','A pass does not prove service implementation semantics']};
if(process.argv[3])await writeFile(process.argv[3],JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(out,null,2));process.exitCode=out.failed?1:0;
