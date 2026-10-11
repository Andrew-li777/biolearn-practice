from pathlib import Path
import json,hashlib,sys
import pandas as pd
import anndata as ad
from PIL import Image
from scipy.io import mmread
import yaml
root=Path(__file__).parent.parent;out=root/'evidence';rows=[];checks=[]
contracts={**json.loads(Path('workflow/outputs.json').read_text()),**json.loads(Path('workflow/diagnostic-outputs.json').read_text())}
rds=json.loads((root/'verification/rds_readback.json').read_text())
for route,files in contracts.items():
 all_names=sorted(set(files)|{str(p.relative_to(root/route)) for p in (root/route).rglob('*') if p.is_file()})
 for name in all_names:
  p=root/route/name;r=dict(path=str(p),declared=name in files)
  try:
   assert p.is_file() and p.stat().st_size>0
   r['bytes']=p.stat().st_size;r['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
   if p.suffix=='.csv':
    d=pd.read_csv(p);r.update(reader='pandas CSV',rows=len(d),columns=len(d.columns))
   elif p.suffix=='.json':json.loads(p.read_text());r['reader']='JSON'
   elif p.suffix=='.png':
    with Image.open(p) as im:im.load();r.update(reader='Pillow full decode',size=im.size)
   elif p.suffix=='.h5ad':
    a=ad.read_h5ad(p);r.update(reader='AnnData full read',shape=a.shape)
   elif p.suffix=='.rds':
    assert p.stem in rds;r.update(reader='R readRDS independent verification',object=rds[p.stem])
   elif p.suffix=='.mtx':m=mmread(p);r.update(reader='scipy Matrix Market',shape=m.shape,nnz=m.nnz)
   elif p.suffix in ['.yaml','.yml']:yaml.safe_load(p.read_text());r['reader']='YAML'
   else:p.read_text();r['reader']='UTF-8 text'
   r['readable']=True
  except Exception as ex:r.update(readable=False,error=str(ex))
  rows.append(r)
for route in contracts:
 p=root/route;manifest=json.loads((p/'sha256-manifest.json').read_text());bad=[f for f,h in manifest.items() if not(p/f).is_file() or hashlib.sha256((p/f).read_bytes()).hexdigest()!=h]
 checks.append(dict(check=route+' manifest',pass_=not bad,files=len(manifest),bad=bad))
 prov=json.loads((p/'run-provenance.json').read_text());checks.append(dict(check=route+' complete/zero stages',pass_=prov['completed'] and all(s['exit_code']==0 for s in prov['stages']),provenance=str(p/'run-provenance.json')))
record=dict(declared_total=sum(r['declared'] for r in rows),total_files=len(rows),readable=sum(r['readable'] for r in rows),inventory=rows,checks=checks,pass_=all(r['readable'] for r in rows) and all(c['pass_'] for c in checks))
(out/'all-products-readback.json').write_text(json.dumps(record,indent=2)+'\n');print('Declared/readable',record['declared_total'],record['readable']);print('Checks',checks);sys.exit(0 if record['pass_'] else 1)
