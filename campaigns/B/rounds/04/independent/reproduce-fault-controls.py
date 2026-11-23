"""Selected defect-detection controls; no baseline or efficacy estimate."""
from pathlib import Path
import os, tempfile, json, subprocess, hashlib

root=Path(os.environ.get('B_REPO_ROOT',os.getcwd())).resolve()
out=Path(os.environ['B_CRITIC_OUTPUT_DIR']).resolve() if 'B_CRITIC_OUTPUT_DIR' in os.environ else Path(tempfile.mkdtemp(prefix='b-r04-controls-'))
out=out/'fault-controls';out.mkdir(parents=True,exist_ok=True)
candidate=root/'modules/interaction-ux-flow/examples/batch-flow.mjs'
source=candidate.read_text()
fixed=root/'modules/interaction-ux-flow/tests/test_batch_flow.mjs'
extra=root/'modules/interaction-ux-flow/tests/test_batch_boundaries.mjs'
controls=[
 {'id':'N01-IGNORE-MINIMUM-DELAY','purpose':'Premature retry must be detected.',
  'edits':[("(row.nextRetryAt===null||(Number.isFinite(row.nextRetryAt)&&now()>=row.nextRetryAt))",'true')],
  'suite':fixed,'expected_failure':'B05'},
 {'id':'N02-ASSIGN-RESULTS-BY-ARRIVAL-POSITION','purpose':'Wrong item/result assignment must be detected.',
  'edits':[("const matches=replies.filter(x=>x?.itemId===ref.itemId&&x?.requestId===ref.requestId);","const arrived=replies[prepared.indexOf(ref)];const matches=arrived?[{...arrived,itemId:ref.itemId,requestId:ref.requestId}]:[];")],
  'suite':fixed,'expected_failure':'B03'},
 {'id':'N03-CANCEL-RECEIPT-AS-TERMINAL','purpose':'A cancellation receipt must not fabricate a terminal cancellation.',
  'edits':[("if(row.requestId===ref.requestId)row.cancelState=receipt?.accepted===true?'accepted':'unconfirmed';","if(row.requestId===ref.requestId){row.cancelState=receipt?.accepted===true?'accepted':'unconfirmed';if(receipt?.accepted===true)row.status='cancelled';}")],
  'suite':fixed,'expected_failure':'B11'},
 {'id':'N04-LET-LATE-PENDING-ERASE-TERMINAL','purpose':'Supplement A02 must detect loss of same-attempt terminal evidence.',
  'edits':[("if(!terminal(attempt.status)){Object.assign(attempt,copy(next));}","Object.assign(attempt,copy(next));"),("if(terminal(row.status))return;",'')],
  'suite':extra,'expected_failure':'A02'},
]
summary=[]
for c in controls:
 mutant=source
 for before,after in c['edits']:
  if mutant.count(before)!=1:raise RuntimeError(f"{c['id']}: exact edit target not unique")
  mutant=mutant.replace(before,after,1)
 path=out/(c['id']+'.mjs');path.write_text(mutant)
 p=subprocess.run(['node',str(c['suite']),str(path)],cwd=root,text=True,capture_output=True)
 try: observed=json.loads(p.stdout)
 except json.JSONDecodeError:observed=None
 failed=[x['id'] for x in observed['results'] if not x['pass']] if observed else []
 detected=bool(observed and p.returncode==1 and c['expected_failure'] in failed)
 report={'id':c['id'],'purpose':c['purpose'],'suite':str(c['suite'].relative_to(root)),'expected_failure':c['expected_failure'],'mutant_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'detected':detected,'exit_code':p.returncode,'failed_cases':failed,'result':observed,'stderr':p.stderr,'edits':[{'before':a,'after':b} for a,b in c['edits']]}
 (out/(c['id']+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 summary.append({k:report[k] for k in ['id','purpose','suite','expected_failure','detected','exit_code','failed_cases','mutant_sha256']})
report={'kind':'Four selected fault controls only; not exhaustive mutation testing, a generated baseline, or a general quality/UX effect score. Faults live in temporary copies; candidate and frozen tests are unchanged.','total':len(summary),'detected':sum(x['detected'] for x in summary),'controls':summary}
(out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'output_dir':str(out),**report},ensure_ascii=False))
raise SystemExit(0 if all(x['detected'] for x in summary) else 1)
