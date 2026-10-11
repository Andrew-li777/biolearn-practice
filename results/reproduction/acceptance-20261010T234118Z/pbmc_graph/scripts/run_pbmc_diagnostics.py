#!/usr/bin/env python3
from pathlib import Path
import argparse,subprocess,json,hashlib,datetime,shutil,os
p=argparse.ArgumentParser();p.add_argument('route',choices=['pbmc_validation','pbmc_graph']);p.add_argument('primary');p.add_argument('out');p.add_argument('--python',required=True);p.add_argument('--conda',default='/home/a/miniforge3/bin/conda');a=p.parse_args()
published=Path(a.out);stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');out=published.parent/'.attempts'/(published.name+'-'+stamp)
out.parent.mkdir(parents=True,exist_ok=True)
primary=Path(a.primary)
if a.route=='pbmc_validation':
 commands=[[a.python,'scripts/16_pbmc_validation.py',str(primary),str(out)],
           [a.python,'scripts/verify_pbmc_validation.py',str(out),str(primary)]]
else:
 commands=[[a.conda,'run','--no-capture-output','-n','biolearn-r','Rscript','scripts/17_pbmc_graph_diagnostic.R',str(primary/'seurat/analysis.rds'),str(out)],
           [a.python,'scripts/17_pbmc_graph_diagnostic.py',str(primary),str(out)],
           [a.python,'scripts/verify_pbmc_graph.py',str(out),str(primary)]]
record={'route':a.route,'primary':str(primary.resolve()),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'completed':False,'commands':commands,'stages':[]}
log_path=out.parent/(out.name+'.execution.log')
os.environ.update({x:'2' for x in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMBA_NUM_THREADS']})
with log_path.open('w') as log:
 for cmd in commands:
  step={'command':cmd,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  log.write('Started UTC: '+step['started_utc']+'\nCommand: '+json.dumps(cmd)+'\n');log.flush()
  code=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT).returncode
  step.update(exit_code=code,ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());record['stages'].append(step)
  log.write('Ended UTC: '+step['ended_utc']+'\nExit code: '+str(code)+'\n');log.flush()
  (out.parent/(out.name+'.provenance.json')).write_text(json.dumps(record,indent=2)+'\n')
  if code:
   if out.exists():(out/'run-provenance.json').write_text(json.dumps(record,indent=2)+'\n')
   raise SystemExit(code)
(out/'logs').mkdir(exist_ok=True);shutil.copy2(log_path,out/'logs/execution.log')
(out/'scripts').mkdir(exist_ok=True);shutil.copy2(__file__,out/'scripts/run_pbmc_diagnostics.py')
(out/'run-provenance.json').write_text(json.dumps(record,indent=2)+'\n')
contract=json.loads(Path('workflow/diagnostic-outputs.json').read_text())[a.route]
missing=[f for f in contract if not(out/f).is_file() or (out/f).stat().st_size==0]
assert not missing,missing
record.update(completed=True,ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(out/'run-provenance.json').write_text(json.dumps(record,indent=2)+'\n')
manifest={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file() and f.name!='sha256-manifest.json'}
(out/'sha256-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
staged=published.parent/'.publish-staging'/out.name;staged.parent.mkdir(exist_ok=True);shutil.copytree(out,staged)
if published.exists():
 history=published.parent/'history';history.mkdir(exist_ok=True);published.rename(history/(published.name+'-'+stamp))
staged.rename(published)
print('Published successful diagnostics: '+str(published),flush=True)
