// Exploratory R02 regression cases added after independent E01 reproduction.
import assert from 'node:assert/strict';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {writeFile} from 'node:fs/promises';
const file=process.argv[2]||'modules/interaction-ux-flow/examples/task-flows.mjs';
const {createApplication}=await import(pathToFileURL(resolve(file)));
const results=[];
async function test(id,fn){try{await fn();results.push({id,pass:true});}catch(e){results.push({id,pass:false,error:e.message});}}
const make=()=>createApplication({submit:async()=>({status:'invalid',fieldErrors:{email:'Correct this email'}})},{initial:{name:'Aki',email:'bad@example.test',delivery:'shipping',address:''},nextId:()=> 'a-1'});
await test('E01-inactive-error',()=>{const f=make();assert.equal(f.review(),false);assert.ok(f.view().errors.address);f.set('delivery','pickup');assert.equal(f.review(),true);assert.equal(f.view().phase,'review');assert.equal(Object.hasOwn(f.view().errors,'address'),false);assert.equal(f.view().draft.address,'');});
await test('E02-reactivated-required-answer',()=>{const f=make();f.set('delivery','pickup');assert.equal(f.review(),true);f.change('delivery');f.set('delivery','shipping');assert.equal(f.review(),false);assert.ok(f.view().errors.address);});
await test('E03-unrelated-active-error-preserved',async()=>{const f=make();f.set('address','1 Example Street');f.review();await f.submit();assert.ok(f.view().errors.email);f.set('delivery','pickup');assert.equal(f.review(),false);assert.ok(f.view().errors.email);});
const report={suite:'B-R02-exploratory-branch-error-regressions',module:file,total:results.length,passed:results.filter(x=>x.pass).length,results,origin:'Independent critic found nonapplicable hidden address error blocking review; separate from frozen 16-case scoring.'};
if(process.argv[3])await writeFile(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));process.exitCode=report.passed===report.total?0:1;
