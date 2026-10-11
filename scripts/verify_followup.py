#!/usr/bin/env python3
"""Independent read-back checks; reports live outside immutable result manifests."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, datetime
import numpy as np
import pandas as pd
import scanpy as sc
from PIL import Image
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);args=ap.parse_args()
root=args.root;out=root/'verification';out.mkdir(exist_ok=True)
checks=[];inventory=[];images=[];logs=[]
def check(name,ok,detail):
    checks.append({'check':name,'pass':bool(ok),'detail':detail})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for route,old in [('bulk',Path('results/bulk/run-20261010T195642Z')),
                  ('pbmc3k',Path('results/pbmc3k/run-20261010T200432Z'))]:
    p=root/route
    manifest=json.loads((p/'sha256-manifest.json').read_text())
    bad=[f for f,h in manifest.items() if not(p/f).is_file() or sha(p/f)!=h]
    check(route+' manifest',not bad,{'files':len(manifest),'bad':bad})
    prov=json.loads((p/'run-provenance.json').read_text())
    check(route+' completed attempt',prov['completed'] and all(x['exit_code']==0 for x in prov['stages']),prov)
    for stage in prov['stages']:
        candidates=[Path(t) for t in stage['command'] if str(t).startswith('scripts/') and Path(t).suffix in ['.R','.py']]
        check(route+' '+stage['stage']+' script SHA', bool(candidates) and all(sha(p/'scripts'/f.name)==stage['script_sha256'] for f in candidates),stage['script_sha256'])
    for csv in p.rglob('*.csv'):
        df=pd.read_csv(csv)
        nums=df.select_dtypes(include='number')
        inf=int(np.isinf(nums.to_numpy()).sum())
        inventory.append({'path':str(csv),'rows':len(df),'columns':list(df),'NA':df.isna().sum().loc[lambda x:x>0].to_dict(),'infinite':inf})
        check(str(csv.relative_to(root))+' readable/finite',csv.stat().st_size>0 and inf==0,{'rows':len(df),'infinite':inf})
    for png in p.rglob('*.png'):
        with Image.open(png) as im: im.load();size=im.size
        same=(old/png.relative_to(p)).is_file() and sha(png)==sha(old/png.relative_to(p))
        images.append({'path':str(png),'size':size,'same_as_visually_verified':same})
        check(str(png.relative_to(root))+' decoded and prior visual match',same,{'size':size})
    for log in (p/'logs').glob('*.log'):
        text=log.read_text(errors='replace')
        logs.append({'path':str(log),'bytes':log.stat().st_size,'sha256':sha(log),'lines':len(text.splitlines()),
          'error_lines':[x for x in text.splitlines() if any(t in x.lower() for t in ['traceback','error','exception'])],
          'warning_lines':[x for x in text.splitlines() if 'warn' in x.lower()]})
        check(str(log.relative_to(root))+' exit evidence','Exit code: 0' in text or 'Exitcode: 0' in text,text[-200:])

b=root/'bulk';meta=pd.read_csv(b/'airway_coldata.csv',index_col=0);counts=pd.read_csv(b/'airway_counts.csv',index_col=0)
check('airway8 unique aligned',len(meta)==8 and counts.shape==(63677,8) and counts.index.is_unique and counts.columns.is_unique and list(counts.columns)==list(meta.index),str(counts.shape))
check('airway counts integers',np.isfinite(counts.to_numpy()).all() and (counts.to_numpy()>=0).all() and np.equal(counts,counts.round()).all().all(),'raw counts')
for method in ['deseq2','edger','pydeseq2']:
    df=pd.read_csv(b/(method+'_results.csv'))
    idcol='gene_id' if 'gene_id' in df else df.columns[0]
    pcol='padj'
    check(method+' unique gene IDs',df[idcol].is_unique,{'rows':len(df)})
    check(method+' valid adjusted probabilities',df[pcol].notna().all() and df[pcol].between(0,1).all(),{'min':float(df[pcol].min()),'max':float(df[pcol].max())})
    sig=pd.read_csv(b/(method+'_significant.csv'))
    check(method+' FDR .1 selection',set(sig[idcol])==set(df.loc[df[pcol]<.1,idcol]),{'significant':len(sig)})

p=root/'pbmc3k';raw=sc.read_h5ad(p/'scanpy/raw_counts.h5ad');a=sc.read_h5ad(p/'scanpy/analysis_annotated.h5ad')
object_rows=[]
for f in (p/'scanpy').glob('*.h5ad'):
    z=sc.read_h5ad(f)
    object_rows.append({'file':str(f),'cells':z.n_obs,'genes':z.n_vars,'clusters':int(z.obs.cluster.nunique()) if 'cluster' in z.obs else None})
    check(f.name+' object unique IDs',z.obs_names.is_unique and z.var_names.is_unique,str(z.shape))
source=sc.read_10x_mtx('data/pbmc3k/filtered_gene_bc_matrices/hg19',var_names='gene_symbols',cache=False);source.var_names_make_unique()
check('raw H5AD matches same 10x source',raw.shape==source.shape and raw.obs_names.equals(source.obs_names) and raw.var.gene_ids.equals(source.var.gene_ids) and (raw.X!=source.X).nnz==0,str(raw.shape))
expected=raw[a.obs_names,a.var_names].X
check('QC counts exact raw subset',(a.layers['counts']!=expected).nnz==0,str(a.shape))
labels={}
for route in ['seurat','scanpy']:
    df=pd.read_csv(p/route/'clusters.csv',index_col='barcode').astype(str)
    labels[route]=df.cluster
    check(route+' barcode alignment',df.index.is_unique and df.index.equals(a.obs_names),{'cells':len(df),'clusters':df.cluster.nunique()})
    if route=='scanpy':check('H5AD clusters equal CSV',df.cluster.equals(a.obs.cluster.astype(str).rename('cluster')),'all barcodes')
shared=labels['seurat'].index.intersection(labels['scanpy'].index)
metrics=json.loads((p/'comparison_metrics.json').read_text())
actual={'shared':len(shared),'ARI':adjusted_rand_score(labels['seurat'].loc[shared],labels['scanpy'].loc[shared]),'NMI_arithmetic':normalized_mutual_info_score(labels['seurat'].loc[shared],labels['scanpy'].loc[shared])}
check('recomputed ARI/NMI',all(np.isclose(actual[k],metrics[k],rtol=1e-12) for k in actual),actual)
profiles=pd.read_csv(p/'scanpy/canonical_marker_profiles.csv')
check('integer expression counts',np.equal(profiles.expressing_cell_count,profiles.expressing_cell_count.round()).all() and (profiles.expressing_cell_count>=0).all() and (profiles.expressing_cell_count<=profiles.n_cells).all(),{'rows':len(profiles)})
check('expression percentages exact integer ratio',np.allclose(profiles.pct_expressing,profiles.expressing_cell_count/profiles.n_cells*100,rtol=1e-12,atol=1e-12),'0..100%')
ev=pd.read_csv(p/'annotation_evidence.csv');missing=ev.positive_marker_padj.isna()
check('allowed marker NA exactly three non-significant',missing.sum()==3 and missing.equals(ev.positive_marker_log2FC.isna()) and (~ev.loc[missing,'passes_positive_marker_filter'].astype(bool)).all(),ev.loc[missing,['route','cluster','gene']].to_dict('records'))
fs=pd.read_csv(p/'scanpy/feature_statistics.csv',index_col=0)
bad=fs.loc[fs.dispersions.isna()|fs.dispersions_norm.isna()]
check('allowed zero-expression CDC6 dispersion NA',list(bad.index)==['CDC6'] and not bool(bad.highly_variable.iloc[0]) and a.layers['counts'][:,a.var_names=='CDC6'].sum()==0,bad.index.tolist())

rscript='''suppressPackageStartupMessages(library(Seurat))
suppressPackageStartupMessages(library(jsonlite))
args<-commandArgs(TRUE);p<-args[1];out<-args[2];rows<-list()
for(name in c("raw_counts","analysis","analysis_annotated")){
 x<-readRDS(file.path(p,"seurat",paste0(name,".rds")))
 ct<-if(name=="raw_counts")x$counts else LayerData(x,assay="RNA",layer="counts")
 stopifnot(!anyDuplicated(colnames(ct)),!anyDuplicated(rownames(ct)),all(is.finite(ct@x)),all(ct@x>=0),all(ct@x==round(ct@x)))
 ncl<-if(name=="raw_counts")NA_integer_ else length(unique(x$cluster))
 if(name!="raw_counts"){
  d<-read.csv(file.path(p,"seurat","clusters.csv"),row.names=1,check.names=FALSE)
  stopifnot(identical(rownames(d),colnames(x)),identical(as.character(d$cluster),as.character(x$cluster)))
 }
 rows[[name]]<-list(cells=ncol(ct),genes=nrow(ct),clusters=ncl)
}
write_json(rows,out,auto_unbox=TRUE,pretty=TRUE)
'''
(out/'read_rds.R').write_text(rscript)
cmd=['/home/a/miniforge3/bin/conda','run','--no-capture-output','-n','biolearn-r','Rscript',str(out/'read_rds.R'),str(p),str(out/'rds_readback.json')]
proc=subprocess.run(cmd,capture_output=True,text=True)
(out/'rds_readback.log').write_text(proc.stdout+proc.stderr)
check('RDS actual independent readback',proc.returncode==0,{'exit_code':proc.returncode,'evidence':str(out/'rds_readback.json')})
check('166 declared files nonempty',all((root/route/f).is_file() and (root/route/f).stat().st_size>0 for route,files in json.loads(Path('workflow/outputs.json').read_text()).items() for f in files),'69 bulk +97 PBMC')
(out/'objects_readback.json').write_text(json.dumps(object_rows,indent=2)+'\n')
(out/'csv_inventory.json').write_text(json.dumps(inventory,indent=2,default=str)+'\n')
(out/'images.json').write_text(json.dumps(images,indent=2)+'\n')
(out/'full_logs.json').write_text(json.dumps(logs,indent=2)+'\n')
(out/'checks.json').write_text(json.dumps(checks,indent=2,default=str)+'\n')
print(f'Passed {sum(x["pass"] for x in checks)}/{len(checks)} checks')
for x in checks:
    if not x['pass']:print('FAIL',x)
sys.exit(0 if all(x['pass'] for x in checks) else 1)
