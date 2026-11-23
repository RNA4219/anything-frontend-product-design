#!/usr/bin/env python3
"""Same-model separate-task critic probes. No parent test imports. Defaults never overwrite evidence."""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
CHECK = ROOT / 'modules/ui-engineering-design-system/checks/tokens.py'
spec = importlib.util.spec_from_file_location('candidate_tokens', CHECK)
tokens = importlib.util.module_from_spec(spec); spec.loader.exec_module(tokens)

def leaf(value=1, kind='number'):
    return {'$type': kind, '$value': value}

def cfg(base=None, roles=None, themes=None):
    return {'format':'C-token-subset/1','prefix':'sensor','default_theme':'day',
            'base': base if base is not None else {'reading': leaf()},
            'roles': roles if roles is not None else {'reading':'number'},
            'themes': themes if themes is not None else {'day':{}}}

def deep(depth, terminal):
    for _ in range(depth): terminal={'g':terminal}
    return terminal

rows=[]

def add_build(name, c, expected='PASS_SUPPORTED_SCOPE', code=None, kind=None, verify=None):
    row={'id':name,'interface':'build','expected_status':expected,'expected_code':code,'expected_kind':kind}
    try:
        result=tokens.build(c)
        row['status']=result['status']; row['diagnostics']=result['diagnostics']
        row['css_present']=result['css'] is not None
        row['theme_names']=list(result['themes'])
        good = result['status']==expected
        if expected != 'PASS_SUPPORTED_SCOPE':
            good &= result['css'] is None and result['themes']=={}
        if code: good &= any(d.get('code')==code for d in result['diagnostics'])
        if kind: good &= any(d.get('kind')==kind for d in result['diagnostics'])
        if verify: good &= bool(verify(result))
        row['ok']=bool(good)
    except Exception as exc:
        row.update(status='UNCAUGHT_EXCEPTION',exception=type(exc).__name__,message=str(exc),ok=False)
    rows.append(row)

# Unused research boundaries and independent normal controls.
add_build('number-control',cfg(),verify=lambda r:'--sensor-reading: 1;' in r['css'])
for value in [True,False,float('inf'),float('-inf'),float('nan')]:
    add_build('number-'+str(value),cfg({'reading':leaf(value)}),'FAIL','NUMBER_VALUE','INVALID')
for kind,unit in [('dimension','px'),('duration','s')]:
    add_build(kind+'-negative',cfg({'reading':leaf({'value':-1,'unit':unit},kind)},{'reading':kind}),verify=lambda r:'-1'+unit+';' in r['css'])
    add_build(kind+'-boolean',cfg({'reading':leaf({'value':True,'unit':unit},kind)},{'reading':kind}),'FAIL','MEASURE_VALUE','INVALID')
    add_build(kind+'-infinite',cfg({'reading':leaf({'value':float('inf'),'unit':unit},kind)},{'reading':kind}),'FAIL','MEASURE_VALUE','INVALID')
    add_build(kind+'-zero',cfg({'reading':leaf({'value':-0.0,'unit':unit},kind)},{'reading':kind}),verify=lambda r:': 0'+unit+';' in r['css'])
color={'colorSpace':'srgb','components':[0.25,0.5,0.75]}
add_build('color-control',cfg({'reading':leaf(color,'color')},{'reading':'color'}),verify=lambda r:'color(srgb 0.25 0.5 0.75 / 1)' in r['css'])
for change,code,kind in [({'components':['none',0,1]},'COLOR_NONE','UNSUPPORTED'),({'colorSpace':'display-p3'},'COLOR_SPACE','UNSUPPORTED'),({'components':[True,0,1]},'COLOR_RANGE','INVALID'),({'components':[0,0,1.0001]},'COLOR_RANGE','INVALID'),({'alpha':True},'COLOR_ALPHA','INVALID'),({'alpha':-0.01},'COLOR_ALPHA','INVALID'),({'hex':'#0008'},'COLOR_HEX','INVALID'),({'hex':'#000000FF'},'COLOR_HEX','INVALID')]:
    value=dict(color,**change)
    add_build('color-'+code+'-'+str(change),cfg({'reading':leaf(value,'color')},{'reading':'color'}),'FAIL',code,kind)
base={'source':leaf({'value':1,'unit':'s'},'duration'),'g':{'$type':'dimension','reading':{'$value':'{source}'}}}
add_build('parent-alias-conflict',cfg(base,{'g.reading':'duration'}),'FAIL','AMBIGUOUS_ALIAS_TYPE','CONTRACT')
base['g']['reading']['$type']='duration'
add_build('parent-conflict-explicit-resolution',cfg(base,{'g.reading':'duration'}),verify=lambda r:r['themes']['day']['roles']['g.reading']['type']=='duration')
for name,extra in [('root',{'$root':leaf()}),('ref',{'$ref':'#/reading/$value'}),('extends',{'$extends':'{reading}'}),('extensions',{'$extensions':{'vendor':{}}}),('deprecated',{'$deprecated':True}),('schema',{'$schema':'https://example.test/schema'})]:
    c=cfg(); c['base']['other']=extra
    add_build('unsupported-'+name,c,'FAIL','NODE_CONSTRUCT','UNSUPPORTED')
c=cfg(); c['base']['$description']='root note'; c['base']['reading']['$description']='token note'; c['base']['empty']={}
add_build('descriptions-empty-group-control',c)
c=cfg(); c['base']['reading']['$description']=False
add_build('metadata-wrong-type',c,'FAIL','DESCRIPTION_SHAPE','INVALID')
c=cfg(); c['unknown_schema_version']=1
add_build('unknown-wrapper-schema',c,'FAIL','CONFIG_FIELDS','UNSUPPORTED')
for name in ['x; color:red','日本語','x\nbody','x[bad]']:
    add_build('token-name-'+repr(name),cfg({name:leaf()},{'reading':'number'}),'FAIL','NAME_SUBSET','UNSUPPORTED')
add_build('case-distinct',cfg({'A':leaf(1),'a':leaf(2)},{'A':'number','a':'number'},{'day':{},'Day':{}}),verify=lambda r:'--sensor-A: 1;' in r['css'] and '--sensor-a: 2;' in r['css'] and '[data-theme="Day"]' in r['css'])
for field in ['prefix','theme']:
    c=cfg()
    if field=='prefix': c['prefix']='sensor;body'
    else: c['themes']['day"] { body']= {}
    add_build('injection-'+field,c,'FAIL','PREFIX' if field=='prefix' else 'THEME_ID','CONTRACT')
add_build('three-segment-collision',cfg({'a-b':{'c':leaf()},'a':{'b-c':leaf()}},{'a-b.c':'number'}),'FAIL','CSS_NAME_COLLISION','CONTRACT')
add_build('empty-group-token-conflict',cfg({'reading':leaf(),'empty':{}},themes={'day':{},'night':{'empty':leaf(2)}}),'FAIL','MERGE_KIND','CONTRACT')
add_build('token-empty-group-conflict',cfg(themes={'day':{},'night':{'reading':{}}}),'FAIL','MERGE_KIND','CONTRACT')
add_build('inherited-role-control',cfg(themes={'day':{},'night':{}}),verify=lambda r:len(r['themes'])==2 and r['themes']['night']['roles']['reading']['value']==1)
add_build('late-theme-required-type-change',cfg(themes={'day':{},'zbad':{'reading':leaf({'value':1,'unit':'s'},'duration')}}),'FAIL','ROLE_TYPE','CONTRACT')
add_build('missing-required-role',cfg(roles={'absent':'number'}),'FAIL','ROLE_MISSING','CONTRACT')
add_build('partial-measure-patch',cfg({'reading':leaf({'value':8,'unit':'px'},'dimension')},{'reading':'dimension'},{'day':{},'night':{'reading':{'$value':{'value':4},'$type':'dimension'}}}),'FAIL','MEASURE_SHAPE','INVALID')
add_build('unused-broken-token',cfg({'reading':leaf(),'unused':{'$value':'{absent}'}}),'FAIL','REFERENCE_MISSING','INVALID')
add_build('group-target',cfg({'reading':{'$value':'{g}'},'g':{'n':leaf()}}),'FAIL','REFERENCE_MISSING','INVALID')
add_build('self-cycle',cfg({'reading':{'$value':'{reading}'}}),'FAIL','REFERENCE_CYCLE','INVALID')
add_build('property-brace-reference',cfg({'reading':{'$value':'{source.$value.value}'},'source':leaf({'value':8,'unit':'px'},'dimension')}),'FAIL','ALIAS_SYNTAX','INVALID')
for d in [31,32,1200]:
    base={'reading':leaf(),'deep':deep(d,{'last':leaf()})}
    expected='PASS_SUPPORTED_SCOPE' if d==31-1 else 'FAIL'
    # Path includes deep and last, so 31 nested g groups exceeds declared 32 path depth.
    add_build('group-depth-'+str(d),cfg(base),'FAIL','GROUP_DEPTH','LIMIT')
add_build('group-depth-positive',cfg({'reading':leaf(),'deep':deep(29,{'last':leaf()})}))
for count in [256,257]:
    base={f'n{i:04d}':({'$value':'{n%04d}'%(i+1)} if i<count-1 else leaf(3)) for i in range(count)}
    add_build('alias-node-count-'+str(count),cfg(base,{'n0000':'number'}),'PASS_SUPPORTED_SCOPE' if count==256 else 'FAIL',None if count==256 else 'ALIAS_DEPTH',None if count==256 else 'LIMIT')
for count in [10000,10001]:
    base={f'n{i:05d}':leaf(i) for i in range(count)}
    add_build('token-count-'+str(count),cfg(base,{'n00000':'number'}),'PASS_SUPPORTED_SCOPE' if count==10000 else 'FAIL',None if count==10000 else 'TOKEN_COUNT',None if count==10000 else 'LIMIT')
add_build('deep-malformed-value',cfg({'reading':leaf(deep(1200,1))}),'FAIL')
add_build('large-integer-serializer',cfg({'reading':leaf(10**5000)}),'FAIL')
add_build('transfer-industrial-console',cfg({'metric':leaf(1.25),'motion':{'$type':'duration','settle':{'$value':{'value':0.15,'unit':'s'}}},'grid':leaf({'value':0.5,'unit':'rem'},'dimension')},{'metric':'number','motion.settle':'duration','grid':'dimension'}),verify=lambda r:'--sensor-grid: 0.5rem;' in r['css'] and len(r['themes']['day']['roles'])==3)

# CLI probes: existing output must survive every input or output failure.
with tempfile.TemporaryDirectory() as temp:
    directory=Path(temp); source=directory/'input.json'; target=directory/'output.css'
    cli_cases=[
      ('syntax-invalid',b'{',2),
      ('duplicate-key',b'{"a":1,"a":2}',2),
      ('non-json-constant',b'{"n":NaN}',2),
      ('invalid-utf8',b'\xff\xfe\xff',2),
      ('oversized-json-integer',('{"n":'+'9'*5001+'}').encode(),2),
      ('deep-json',('['*1200+'0'+']'*1200).encode(),2),
      ('overflow-float',json.dumps(cfg()).replace('"$value": 1','"$value": 1e999').encode(),1),
      ('late-theme-failure',json.dumps(cfg(themes={'day':{},'zbad':{'reading':leaf(True)}})).encode(),1),
      ('normal-success',json.dumps(cfg()).encode(),0),
    ]
    for name,content,returncode in cli_cases:
        source.write_bytes(content); target.write_text('PREVIOUS VALID CSS\n')
        result=subprocess.run([sys.executable,str(CHECK),str(source),'--css',str(target)],capture_output=True,text=True)
        try: report=json.loads(result.stdout)
        except Exception: report=None
        ok=result.returncode==returncode and isinstance(report,dict)
        if returncode: ok &= target.read_text()=='PREVIOUS VALID CSS\n' and report is not None and report.get('css') is None and report.get('status')!='PASS_SUPPORTED_SCOPE'
        else: ok &= target.read_text()==report['css']
        rows.append({'id':'cli-'+name,'interface':'cli','expected_returncode':returncode,'returncode':result.returncode,'report':report,'stderr_tail':result.stderr[-1800:],'preserved_previous':target.read_text()=='PREVIOUS VALID CSS\n','ok':bool(ok)})
    source.write_text(json.dumps(cfg()))
    result=subprocess.run([sys.executable,str(CHECK),str(source),'--css',str(directory/'absent'/'out.css')],capture_output=True,text=True)
    try: report=json.loads(result.stdout)
    except Exception: report=None
    rows.append({'id':'cli-output-io-failure','interface':'cli','returncode':result.returncode,'report':report,'ok':result.returncode==2 and report is not None and report['status']=='ERROR_INPUT_OR_OUTPUT' and report['css'] is None})

parser=argparse.ArgumentParser();parser.add_argument('--out',default=str(Path(__file__).with_name('initial-results.json')));args=parser.parse_args()
result={'reviewer':'same-model separate-task independent critic','hidden_holdout':False,'cost':'unknown','candidate_sha256':hashlib.sha256(CHECK.read_bytes()).hexdigest(),'probe_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'total':len(rows),'passed':sum(r['ok'] for r in rows),'failed':sum(not r['ok'] for r in rows),'results':rows}
with open(args.out,'x') as stream: json.dump(result,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
print(json.dumps({'total':result['total'],'passed':result['passed'],'failed':result['failed'],'failures':[r for r in rows if not r['ok']]},ensure_ascii=False,indent=2))
