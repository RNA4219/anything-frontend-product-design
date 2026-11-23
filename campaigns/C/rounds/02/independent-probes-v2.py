#!/usr/bin/env python3
"""Revision 2 critic probes. Initial evidence and source remain immutable; explicit local resource policies are tested."""
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
    add_build('group-depth-'+str(d),cfg(base),'FAIL','JSON_DEPTH' if d==1200 else 'GROUP_DEPTH','LIMIT')
add_build('group-depth-positive',cfg({'reading':leaf(),'deep':deep(29,{'last':leaf()})}))
for count in [256,257]:
    base={f'n{i:04d}':({'$value':'{n%04d}'%(i+1)} if i<count-1 else leaf(3)) for i in range(count)}
    add_build('alias-node-count-'+str(count),cfg(base,{'n0000':'number'}),'PASS_SUPPORTED_SCOPE' if count==256 else 'FAIL',None if count==256 else 'ALIAS_DEPTH',None if count==256 else 'LIMIT')
for count in [10000,10001]:
    base={f'n{i:05d}':leaf(i) for i in range(count)}
    add_build('token-count-'+str(count),cfg(base,{'n00000':'number'}),'PASS_SUPPORTED_SCOPE' if count==10000 else 'FAIL',None if count==10000 else 'TOKEN_COUNT',None if count==10000 else 'LIMIT')
add_build('deep-malformed-value',cfg({'reading':leaf(deep(1200,1))}),'FAIL','JSON_DEPTH','LIMIT')
add_build('large-integer-serializer',cfg({'reading':leaf(10**5000)}),'FAIL','INTEGER_SIZE','LIMIT')
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
      ('deep-json',('['*1200+'0'+']'*1200).encode(),1),
      ('overflow-float',json.dumps(cfg()).replace('"$value": 1','"$value": 1e999').encode(),1),
      ('late-theme-failure',json.dumps(cfg(themes={'day':{},'zbad':{'reading':leaf(True)}})).encode(),1),
      ('normal-success',json.dumps(cfg()).encode(),0),
    ]
    for name,content,returncode in cli_cases:
        source.write_bytes(content); target.write_text('PREVIOUS VALID CSS\n')
        original_input=source.read_bytes()
        result=subprocess.run([sys.executable,str(CHECK),str(source),'--css',str(target)],capture_output=True,text=True)
        try: report=json.loads(result.stdout)
        except Exception: report=None
        ok=result.returncode==returncode and isinstance(report,dict) and source.read_bytes()==original_input and 'Traceback' not in result.stderr
        if returncode: ok &= target.read_text()=='PREVIOUS VALID CSS\n' and report is not None and report.get('css') is None and report.get('status')!='PASS_SUPPORTED_SCOPE'
        else: ok &= target.read_text()==report['css']
        rows.append({'id':'cli-'+name,'interface':'cli','expected_returncode':returncode,'returncode':result.returncode,'report':report,'stderr_tail':result.stderr[-1800:],'preserved_previous':target.read_text()=='PREVIOUS VALID CSS\n','input_unchanged':source.read_bytes()==original_input,'ok':bool(ok)})
    source.write_text(json.dumps(cfg()))
    result=subprocess.run([sys.executable,str(CHECK),str(source),'--css',str(directory/'absent'/'out.css')],capture_output=True,text=True)
    try: report=json.loads(result.stdout)
    except Exception: report=None
    rows.append({'id':'cli-output-io-failure','interface':'cli','returncode':result.returncode,'report':report,'ok':result.returncode==2 and report is not None and report['status']=='ERROR_INPUT_OR_OUTPUT' and report['css'] is None})


# The original 73 rows are kept, with only documented diagnostic precedence and
# the previously disclosed deep-JSON oracle correction. New exact boundaries follow.
original_case_count=len(rows)

def add_resource(name,value,expected_code=None):
    row={'id':name,'interface':'resources','expected_code':expected_code}
    try:
        tokens.resources(value)
        row.update(status='RESOURCE_ACCEPT',ok=expected_code is None)
    except tokens.TokenError as exc:
        d=exc.diagnostic
        row.update(status='RESOURCE_REJECT',diagnostics=[d],ok=d.get('kind')=='LIMIT' and d.get('code')==expected_code and bool(d.get('path')))
    except Exception as exc:
        row.update(status='UNCAUGHT_EXCEPTION',exception=type(exc).__name__,message=str(exc),ok=False)
    rows.append(row)

def add_resolve(name,value,expected_code=None):
    row={'id':name,'interface':'resolve','expected_code':expected_code}
    try:
        answer=tokens.resolve(value)
        row.update(status='RESOLVED',token_count=len(answer),ok=expected_code is None)
    except tokens.TokenError as exc:
        d=exc.diagnostic
        row.update(status='REJECTED',diagnostics=[d],ok=d.get('kind')=='LIMIT' and d.get('code')==expected_code and bool(d.get('path')))
    except Exception as exc:
        row.update(status='UNCAUGHT_EXCEPTION',exception=type(exc).__name__,message=str(exc),ok=False)
    rows.append(row)

def arrays(depth):
    value=0
    for _ in range(depth): value=[value]
    return value

def json_nodes(value):
    stack=[value]; total=0
    while stack:
        item=stack.pop();total+=1
        if isinstance(item,dict): stack.extend(item.values())
        elif isinstance(item,list): stack.extend(item)
    return total

for depth in [63,64,65]:
    add_resource('resource-json-depth-'+str(depth),arrays(depth),None if depth<=64 else 'JSON_DEPTH')
    # Root/base/token/$value is depth 3. Within resource limits this is still
    # invalid number shape, so the distinction INVALID vs LIMIT is essential.
    add_build('build-json-depth-'+str(depth),cfg({'reading':leaf(arrays(depth-3))}),'FAIL', 'NUMBER_VALUE' if depth<=64 else 'JSON_DEPTH','INVALID' if depth<=64 else 'LIMIT')
add_resolve('resolve-deep-1200',deep(1200,leaf()),'JSON_DEPTH')

for total in [249999,250000,250001]:
    add_resource('resource-json-nodes-'+str(total),[0]*(total-1),None if total<=250000 else 'JSON_NODES')

# At the exact global node boundary a supported document can still succeed:
# its padding consists of valid empty groups; role/token counts stay unchanged.
def wide_config(total):
    value=cfg()
    extra=total-json_nodes(value)
    value['base'].update({f'empty{i:06d}':{} for i in range(extra)})
    assert json_nodes(value)==total
    return value
for total in [250000,250001]:
    c=wide_config(total)
    add_build('build-json-nodes-'+str(total),c,'PASS_SUPPORTED_SCOPE' if total==250000 else 'FAIL',None if total==250000 else 'JSON_NODES',None if total==250000 else 'LIMIT')
del c

max_int=(1<<1024)-1
for sign in [1,-1]:
    for kind,unit in [('number',None),('dimension','px'),('duration','s')]:
        good=sign*max_int
        bad=sign*(1<<1024)
        value_good=good if unit is None else {'value':good,'unit':unit}
        value_bad=bad if unit is None else {'value':bad,'unit':unit}
        add_build('integer-1024-bits-'+kind+'-'+str(sign),cfg({'reading':leaf(value_good,kind)},{'reading':kind}),verify=lambda r,g=good,u=unit:(': '+str(g)+(u or '')+';') in r['css'])
        add_build('integer-1025-bits-'+kind+'-'+str(sign),cfg({'reading':leaf(value_bad,kind)},{'reading':kind}),'FAIL','INTEGER_SIZE','LIMIT')
    add_resolve('resolve-integer-1024-'+str(sign),{'reading':leaf(sign*max_int)})
    add_resolve('resolve-integer-1025-'+str(sign),{'reading':leaf(sign*(1<<1024))},'INTEGER_SIZE')
for value in [sys.float_info.max,-sys.float_info.max,5e-324,-5e-324,-0.0]:
    add_build('finite-float-'+repr(value),cfg({'reading':leaf(value)}),verify=lambda r,v=value:r['themes']['day']['roles']['reading']['value']==v and 'inf' not in r['css'] and 'nan' not in r['css'])

# Test the loader and file contract at integer, resource, malformed input and
# output boundaries. The caller's JSON bytes and previous CSS must both survive.
with tempfile.TemporaryDirectory() as temp:
    directory=Path(temp);source=directory/'input.json';target=directory/'output.css'
    def cli(name,raw,expected_returncode,expected_code=None,expected_kind=None):
        source.write_bytes(raw); target.write_bytes(b'PREVIOUS CSS: exact bytes\r\n')
        before=source.read_bytes();previous=target.read_bytes()
        command=[sys.executable,str(CHECK),str(source),'--css',str(target)]
        proc=subprocess.run(command,capture_output=True,text=True)
        try: report=json.loads(proc.stdout)
        except Exception: report=None
        good=proc.returncode==expected_returncode and report is not None and source.read_bytes()==before and 'Traceback' not in proc.stderr
        if report is not None:
            if expected_returncode:
                good &= report.get('status')!='PASS_SUPPORTED_SCOPE' and report.get('css') is None and target.read_bytes()==previous
            else:
                good &= report['status']=='PASS_SUPPORTED_SCOPE' and target.read_bytes()==report['css'].encode()
            if expected_code: good &= any(d.get('code')==expected_code for d in report['diagnostics'])
            if expected_kind: good &= any(d.get('kind')==expected_kind for d in report['diagnostics'])
        rows.append({'id':name,'interface':'cli','returncode':proc.returncode,'expected_returncode':expected_returncode,'expected_code':expected_code,'expected_kind':expected_kind,'report':report,'input_unchanged':source.read_bytes()==before,'previous_css_preserved':target.read_bytes()==previous,'stderr_tail':proc.stderr[-1600:],'ok':bool(good)})
    for sign in [1,-1]:
        cli('cli-integer-1024-'+str(sign),json.dumps(cfg({'reading':leaf(sign*max_int)})).encode(),0)
        cli('cli-integer-1025-'+str(sign),json.dumps(cfg({'reading':leaf(sign*(1<<1024))})).encode(),2,'INTEGER_SIZE','LIMIT')
        cli('cli-5001-digits-'+str(sign),('{"n":'+('-' if sign<0 else '')+'9'*5001+'}').encode(),2,'INTEGER_SIZE','LIMIT')
    for depth in [64,65]:
        cli('cli-json-depth-'+str(depth),json.dumps(cfg({'reading':leaf(arrays(depth-3))})).encode(),1,'NUMBER_VALUE' if depth==64 else 'JSON_DEPTH','INVALID' if depth==64 else 'LIMIT')
    for total in [250000,250001]:
        cli('cli-json-nodes-'+str(total),json.dumps(wide_config(total)).encode(),0 if total==250000 else 1,None if total==250000 else 'JSON_NODES',None if total==250000 else 'LIMIT')
    cli('cli-parser-recursion',('['*10000+'0'+']'*10000).encode(),2,'RecursionError','IO_OR_PARSE')
    cli('cli-non-json-positive-infinity',b'{"n":Infinity}',2,'JSON_NUMBER','INVALID')
    cli('cli-non-json-negative-infinity',b'{"n":-Infinity}',2,'JSON_NUMBER','INVALID')
    cli('cli-utf8-truncated',b'{"n":"\xe3\x81"}',2,'UnicodeDecodeError','IO_OR_PARSE')
    cli('cli-integer-leading-zero',b'{"n":01}',2,'JSONDecodeError','IO_OR_PARSE')
    cli('cli-missing-file-control',b'{"placeholder":1}',1,'CONFIG_SHAPE','CONTRACT')
    cli('cli-float-maximum',json.dumps(cfg({'reading':leaf(sys.float_info.max)})).encode(),0)
    cli('cli-float-minimum-subnormal',json.dumps(cfg({'reading':leaf(5e-324)})).encode(),0)

# Existing public fixture remains byte-for-byte deterministic and keeps visual scope.
example=ROOT/'modules/ui-engineering-design-system/examples/booking-tokens.json'
expected_css=(example.with_suffix('.css')).read_text()
add_build('booking-css-regression',json.loads(example.read_text()),verify=lambda r:r['css']==expected_css and r['dtcg_conformance']=='NOT_CLAIMED' and set(r['visual'].values())=={'NOT_TESTED'})

parser=argparse.ArgumentParser();parser.add_argument('--out',default=str(Path(__file__).with_name('recheck-results.json')));args=parser.parse_args()
result={'reviewer':'same-model separate-task independent critic','hidden_holdout':False,'cost':'unknown','candidate_sha256':hashlib.sha256(CHECK.read_bytes()).hexdigest(),'probe_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'original_cases':original_case_count,'additional_cases':len(rows)-original_case_count,'total':len(rows),'passed':sum(r['ok'] for r in rows),'failed':sum(not r['ok'] for r in rows),'results':rows}
with open(args.out,'x') as stream: json.dump(result,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
print(json.dumps({'total':result['total'],'passed':result['passed'],'failed':result['failed'],'failures':[r for r in rows if not r['ok']]},ensure_ascii=False,indent=2))
