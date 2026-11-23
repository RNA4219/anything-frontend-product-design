"""Reproduce four targeted fault controls against the immutable initial R03 candidate.

Run from the repository root, or set B_REPO_ROOT. Outputs go to B_CRITIC_OUTPUT_DIR.
No original research texts, connected services, or private paths are required.
"""
from pathlib import Path
import os,json,hashlib,subprocess
root=Path(os.environ.get('B_REPO_ROOT',Path.cwd())).resolve()
out=Path(os.environ.get('B_CRITIC_OUTPUT_DIR',root/'artifacts/critic-r03')).resolve()/'negative-controls'
out.mkdir(parents=True,exist_ok=True)
source=root/'campaigns/B/rounds/03/artifacts/initial/resume-and-conflict.mjs'
test=root/'modules/interaction-ux-flow/tests/test_resume_conflict.mjs'
candidate=source.read_text()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
mutations=[
 ('N01-REMOVE-ACCOUNT-GUARD',"if(activeSession.accountId!==record.ownerId)return 'different_account';",'// intentionally removed account guard',['R03','R09']),
 ('N02-IGNORE-REQUEST-EPOCH','const current=e=>e===epoch&&!guard();','const current=e=>!guard();',['R08']),
 ('N03-OPERATION-RESULT-OVERWRITES-CURRENT','await readCurrent(e);return;','await readCurrent(e);observedResource=copy(operationResult);return;',['R11','R12']),
 ('N04-READ-ERROR-ERASES-SUCCESS',"observedResource=null;resourceReadError='現在の資源状態を照合できません。確認済みの操作結果とは別の問題です。';","observedResource=null;operationOutcome=null;operationResult=null;phase='unknown';resourceReadError='現在の資源状態を照合できません。';",['R12'])
]
results=[]
for mid,old,new,targets in mutations:
 assert candidate.count(old)==1,(mid,'anchor drift')
 mutant=out/f'{mid}.mjs';mutant.write_text(candidate.replace(old,new))
 report=out/f'{mid}.json'
 run=subprocess.run(['node',str(test),str(mutant),str(report)],cwd=root,text=True,capture_output=True)
 (out/f'{mid}.log').write_text(run.stdout+run.stderr)
 result=json.loads(report.read_text());failed=[x['id'] for x in result['results'] if not x['pass']]
 results.append({'id':mid,'base_sha256':sha(source),'mutant_sha256':sha(mutant),'target_cases':targets,'failed_cases':failed,'detected':all(x in failed for x in targets),'returncode':run.returncode})
summary={'scope':'Four purpose-built fault controls; not causal efficacy evidence','candidate':'immutable initial snapshot','total':len(results),'detected':sum(x['detected'] for x in results),'results':results}
(out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
raise SystemExit(0 if summary['detected']==summary['total'] else 1)
