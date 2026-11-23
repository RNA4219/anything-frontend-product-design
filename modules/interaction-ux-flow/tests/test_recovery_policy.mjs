import assert from 'node:assert/strict';
import {decideRecovery} from '../examples/recovery-policy.mjs';
const results=[];
function test(name,fn){try{fn();results.push({name,pass:true});}catch(e){results.push({name,pass:false,error:e.message});}}
const safe={supported:true,requestId:'request-1',samePayload:true,scopeMatches:true,errorAllowsRetry:true,now:50,validUntil:100};
test('Complete replay contract permits same-intent replay',()=>assert.equal(decideRecovery({replay:safe}),'replay_same_intent'));
for(const [field,value] of [['requestId',''],['samePayload',false],['scopeMatches',false],['errorAllowsRetry',false],['supported',false],['validUntil',undefined]])
  test(`Missing or invalid ${field} requires reconciliation`,()=>assert.equal(decideRecovery({replay:{...safe,[field]:value}}),'reconcile'));
test('Expiry boundary is outside the verified replay window',()=>assert.equal(decideRecovery({replay:{...safe,now:100}}),'reconcile'));
test('No response or nonauthoritative not_found is not a final result',()=>assert.equal(decideRecovery({verifiedOutcome:'not_found'}),'reconcile'));
test('Verified outcome needs no extra request',()=>assert.equal(decideRecovery({verifiedOutcome:'succeeded'}),'show_verified_result'));
test('Proven nonexecution allows correction',()=>assert.equal(decideRecovery({verifiedUnapplied:true}),'repair_then_submit'));
test('Method semantics can permit retry without a custom key',()=>assert.equal(decideRecovery({methodSemanticsIdempotent:true,errorAllowsRetry:true}),'retry_by_contract'));
test('Repeated replies need not be byte-identical to preserve effects',()=>{
  let effects=0,observations=0;const seen=new Set();
  const submit=key=>{if(!seen.has(key)){effects++;seen.add(key);}return {effects,observation:++observations};};
  submit(safe.requestId);assert.equal(decideRecovery({replay:safe}),'replay_same_intent');submit(safe.requestId);assert.equal(effects,1);
});
test('Negative control: replaying a pruned key duplicates a side effect',()=>{
  let effects=0;let saved=false;
  const submit=()=>{if(!saved){effects++;saved=true;}};
  submit();saved=false; // explicit service expiry in this synthetic fixture
  assert.equal(decideRecovery({replay:{...safe,now:100}}),'reconcile');assert.equal(effects,1);
  submit();assert.equal(effects,2); // demonstrates why the expiry case is meaningful
});
console.log(JSON.stringify({suite:'B-recovery-policy-v1',total:results.length,passed:results.filter(x=>x.pass).length,results,
  limits:'Synthetic contract decision and service-side-effect counterexample; not a live API test.'},null,2));
process.exitCode=results.some(x=>!x.pass)?1:0;
