from pathlib import Path
import subprocess,json,sys,hashlib
out=Path(__file__).parent;rows=[]
for env in ['biolearn-r','biolearn-py','biolearn-workflow']:
 cmd=['/home/a/miniforge3/bin/conda','list','-n',env,'--explicit'];p=subprocess.run(cmd,capture_output=True,text=True);(out/(env+'.actual-explicit.txt')).write_text(p.stdout)
 q=subprocess.run(['/home/a/miniforge3/bin/conda','list','-n',env,'--json'],capture_output=True,text=True);(out/(env+'.actual-packages.json')).write_text(q.stdout)
 urls=lambda s:sorted(x for x in s.splitlines() if x.startswith(('https://','http://','file://')))
 lock=Path('environment')/(env+'.linux-64.explicit.txt')
 rows.append(dict(environment=env,prefix='/home/a/miniforge3/envs/'+env,explicit_exit=p.returncode,packages_exit=q.returncode,exact_lock_match=urls(p.stdout)==urls(lock.read_text())))
q=subprocess.run(['environment/validation-venv/bin/python','-m','pip','freeze'],capture_output=True,text=True);(out/'validation-venv-freeze.txt').write_text(q.stdout)
ref=Path('/home/a/miniforge3/envs/biolearn-py/lib/python3.11/site-packages/scanpy/datasets/10x_pbmc68k_reduced.h5ad')
(out/'reference-reuse.json').write_text(json.dumps({'path':str(ref),'sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'reuse':'Scanpy bundled reduced PBMC68k reference'},indent=2))
(out/'environment-checks.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2));sys.exit(0 if all(r['exact_lock_match'] and r['explicit_exit']==r['packages_exit']==0 for r in rows) and q.returncode==0 else 1)
