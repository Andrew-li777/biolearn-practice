#!/usr/bin/env python3
from pathlib import Path
import pandas as pd,json,hashlib,sys
root=Path(sys.argv[1]);records=[]
def check(name,ok,detail):
 records.append({'check':name,'pass':bool(ok),'detail':detail})
for route,original in [('bulk','results/bulk/run-20261010T195642Z'),('pbmc3k','results/pbmc3k/run-20261010T200432Z')]:
 p=root/route;old=Path(original)
 checks=pd.read_csv(p/'acceptance_checks.csv')
 check(route+' acceptance',checks['status'].eq('PASS').all(),str(len(checks)))
 manifest=json.loads((p/'sha256-manifest.json').read_text())
 bad=[f for f,h in manifest.items() if not (p/f).exists() or hashlib.sha256((p/f).read_bytes()).hexdigest()!=h]
 check(route+' manifest',not bad,str(bad))
 if route=='bulk':
  for f in ['analysis_summary.csv','comparisons.csv','overlap_all_three.csv','deseq2_results.csv','edger_results.csv','pydeseq2_results.csv']:
   a=pd.read_csv(p/f);b=pd.read_csv(old/f)
   try:pd.testing.assert_frame_equal(a,b,check_exact=False,rtol=1e-8,atol=1e-10);ok=True
   except AssertionError:ok=False
   check(route+' '+f,ok,'compared with prior verified run; rtol=1e-8 atol=1e-10')
 else:
  for route2 in ['seurat','scanpy']:
   for f in ['clusters.csv','qc_after.csv']:
    a=pd.read_csv(p/route2/f);b=pd.read_csv(old/route2/f)
    try:pd.testing.assert_frame_equal(a,b,check_exact=False,rtol=1e-8,atol=1e-10);ok=True
    except AssertionError:ok=False
    check(route+'/'+route2+'/'+f,ok,'compared by saved barcode rows and values')
  a=json.loads((p/'comparison_metrics.json').read_text());b=json.loads((old/'comparison_metrics.json').read_text())
  check(route+' comparison_metrics',a==b,json.dumps(a))
check('all declared outputs',all((root/k/f).is_file() for k,v in json.loads(Path('workflow/outputs.json').read_text()).items() for f in v),'explicit file contract')
(root/'reproduction_checks.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
lines=['# Snakemake 干净输出复现验收','',f'实际目录：`{root}`','',f'通过 {sum(x["pass"] for x in records)}/{len(records)} 项。','', '| 项目 | 结果 |','|---|---|']+[f'| {x["check"]} | {"PASS" if x["pass"] else "FAIL"} |' for x in records]
(root/'reproduction-acceptance.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines));sys.exit(0 if all(x['pass'] for x in records) else 1)
