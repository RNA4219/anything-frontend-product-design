// Focused regression probe: a terminal operation fact is not current authority.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=resolve(process.env.B_REPO_ROOT||process.cwd());
const output=resolve(process.env.B_CRITIC_OUTPUT_DIR||'artifacts/critic-r03');await mkdir(output,{recursive:true});
const modulePath=resolve(process.argv[2]||`${root}/modules/interaction-ux-flow/examples/resume-and-conflict.mjs`);
const {createResumableEdit}=await import(pathToFileURL(modulePath));
const session={accountId:'A',authenticated:true,canRead:true,canWrite:true};
const resource={etag:'old',values:{title:'Original'}};
const saved={ownerId:'A',resourceId:'doc-1',lastKnown:resource,draft:{title:'Private draft'},operation:null};
let releaseUpdate,releaseLookup,loads=0,lookups=0,updates=0;
const api={load:async()=>{loads++;return structuredClone(resource);},lookup:async()=>{lookups++;return await new Promise(r=>releaseLookup=r);},update:async()=>{updates++;return await new Promise(r=>releaseUpdate=r);}};
const f=createResumableEdit(api,{session,saved,nextId:()=> 'operation-1'}),trace=[];
let pass=true,error=null;
try{
 await f.resume();f.review();const update=f.commit(),lookup=f.resume();
 releaseUpdate({status:'succeeded',operationResult:{etag:'written',values:{title:'Private draft'}}});await update;
 trace.push({afterSuccess:f.view(),loads,lookups,updates});
 releaseLookup({status:'auth_required'});await lookup;
 trace.push({afterCurrentAuthRequired:f.view(),loads,lookups,updates});
 assert.equal(f.view().phase,'reauthenticate','A correlated success must not suppress a current auth_required signal.');
 assert.equal(f.view().draft,null);assert.equal(f.view().operationId,null);assert.equal(f.view().operationResult,null);assert.equal(loads,1,'No private current-resource read is allowed after the current auth-required response.');
 f.setSession(session);await f.resume();trace.push({afterReauth:f.view(),loads,lookups,updates});
 assert.equal(f.view().operationOutcome,'succeeded','Reauthentication must restore the retained operation fact without a new write.');assert.equal(updates,1);assert.equal(lookups,1);
}catch(e){pass=false;error=e.message;}
const report={id:'RC04-KNOWN-SUCCESS-DOES-NOT-GRANT-CURRENT-AUTHORITY',scope:'Direct regression risk of the terminal-priority change; not a frozen criterion.',modulePath,moduleSha256:createHash('sha256').update(await readFile(modulePath)).digest('hex'),pass,error,trace};
await writeFile(resolve(output,'authority-recheck.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({id:report.id,pass,error,moduleSha256:report.moduleSha256}));process.exitCode=pass?0:1;
