from pathlib import Path
import json,hashlib,sys,datetime
import pandas as pd
out=Path(__file__).parent;p=Path('results/nfcore/rnaseq-3.27.0-attempt-2');checks=[]
def check(n,ok,d):checks.append(dict(check=n,pass_=bool(ok),detail=d))
s=json.loads((p/'completion-status.json').read_text());v=json.loads((p/'verification/summary.json').read_text())
check('recorded completion and actual exit',s['completed'] and s['exit_code']==int((p/'exit-code.txt').read_text())==0,s)
trace=pd.read_csv(p/'execution-trace.tsv',sep='\t',dtype=str,keep_default_na=False);last=trace.drop_duplicates('name',keep='last');bad=[]
for _,r in trace.iterrows():
 pre,suf=r['hash'].split('/');paths=list((p/'work'/pre).glob(suf+'*'))
 if len(paths)!=1 or not(paths[0]/'.exitcode').is_file() or (paths[0]/'.exitcode').read_text().strip()!=r['exit']:bad.append(r['hash'])
check('trace and task exitcode files',not bad and last.status.eq('COMPLETED').all() and last.exit.eq('0').all(),dict(rows=len(trace),bad=bad))
manifest=json.loads((p/'verification/output_manifest.json').read_text());bad=[]
for r in manifest:
 f=p/r['path']
 if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=r['sha256']:bad.append(r['path'])
check('official outputs match recorded manifest',not bad,dict(files=len(manifest),bad=bad))
check('prior independent acceptance report',v['pass'] and v['passed']==v['total'],dict(passed=v['passed'],total=v['total'],evidence=str(p/'verification/summary.json')))
reports=[Path(x) for x in s['multiqc_reports']];check('MultiQC HTML readable',bool(reports) and all('<html' in f.read_text().lower() for f in reports),[str(x) for x in reports])
record=dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Read-only recheck of existing official small test; no nf-core rerun in this matrix validation; not airway FASTQ.',checks=checks,passed=all(x['pass_'] for x in checks),prior_evidence=str(p/'verification'))
(out/'nfcore-status.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));sys.exit(0 if record['passed'] else 1)
