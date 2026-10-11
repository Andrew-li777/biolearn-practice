#!/usr/bin/env python3
"""Run verified matrix stages; capture failure logs and full environment provenance."""
from pathlib import Path
import argparse,os,subprocess,shutil,datetime,json
p=argparse.ArgumentParser();p.add_argument('route',choices=['bulk','pbmc3k']);p.add_argument('out');p.add_argument('--conda',default='/home/a/miniforge3/bin/conda');a=p.parse_args()
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
for sub in ['logs','environment','scripts']: (out/sub).mkdir(exist_ok=True)
os.environ.update({x:'2' for x in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMBA_NUM_THREADS']})
if a.route=='bulk':
 stages=[('deseq2','biolearn-r','Rscript','01_bulk_deseq2.R',[]),('edger','biolearn-r','Rscript','02_bulk_edger.R',[]),('pydeseq2','biolearn-py','python','03_bulk_pydeseq2.py',[])]
 report='04_bulk_report.py';method='bulk-methods.md'
else:
 inp='data/pbmc3k/filtered_gene_bc_matrices/hg19'
 stages=[('prepare','biolearn-py','python','10_pbmc_prepare.py',[]),('seurat','biolearn-r','Rscript','11_pbmc_seurat.R',[inp]),('scanpy','biolearn-py','python','12_pbmc_scanpy.py',[inp]),('annotation_python','biolearn-py','python','13_pbmc_annotate.py',['scripts/pbmc_annotation_plan.json']),('annotation_r','biolearn-r','Rscript','14_pbmc_annotate_seurat.R',[])]
 report='15_pbmc_report.py';method='pbmc3k-methods.md'
for f in [s[3] for s in stages]+[report,'05_bulk_manifest.py']:
 shutil.copy2(Path('scripts')/f,out/'scripts'/f)
if a.route=='pbmc3k':shutil.copy2('scripts/pbmc_annotation_plan.json',out/'scripts/pbmc_annotation_plan.json')
shutil.copy2(Path('docs')/method,out/method)
with (out/'logs/exit-status.tsv').open('w') as status:
 def run(stage,env,exe,script,extra):
  target=out/stage if stage in ['seurat','scanpy'] else out
  cmd=[a.conda,'run','--no-capture-output','-n',env,exe,'scripts/'+script,str(target)]+extra
  with (out/'logs'/f'{stage}.log').open('w') as log:
   log.write('Started UTC: '+datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n');log.flush()
   code=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT).returncode
  status.write(f'{stage}\t{code}\n');status.flush()
  print(f'{stage}: exit={code}',flush=True)
  if code:raise SystemExit(code)
 for s in stages:run(*s)
 for env in ['biolearn-r','biolearn-py']:
  for suffix,args in [('packages.json',['list','--json']),('linux-64.explicit.txt',['list','--explicit']),('resolved.yml',['env','export'])]:
   with (out/'environment'/f'{env}.{suffix}').open('w') as f:subprocess.run([a.conda]+args+['-n',env],stdout=f,check=True)
 run('report','biolearn-py','python',report,[])
subprocess.run([a.conda,'run','--no-capture-output','-n','biolearn-py','python','scripts/05_bulk_manifest.py',str(out)],check=True)
contract=json.loads(Path('workflow/outputs.json').read_text())[a.route]
missing=[f for f in contract if not (out/f).is_file()]
assert not missing,missing
