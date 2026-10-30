#!/usr/bin/env python3
from pathlib import Path
import sys,json,hashlib
import scanpy as sc
import pandas as pd
import numpy as np
from PIL import Image
from sklearn.metrics import accuracy_score,f1_score,adjusted_rand_score,normalized_mutual_info_score
p=Path(sys.argv[1]);primary=Path(sys.argv[2]);out=p/'verification';out.mkdir(exist_ok=True)
checks=[]
def check(n,v,d):checks.append({'check':n,'pass':bool(v),'detail':d})
manifest=json.loads((p/'sha256-manifest.json').read_text())
bad=[f for f,h in manifest.items() if not(p/f).is_file() or hashlib.sha256((p/f).read_bytes()).hexdigest()!=h]
check('manifest',not bad,{'files':len(manifest),'bad':bad})
meta=json.loads((p/'provenance.json').read_text())
changed=[f for f,h in meta['inputs'].items() if hashlib.sha256(Path(f).read_bytes()).hexdigest()!=h]
check('complete with unchanged inputs',meta['completed'] and not changed,changed)
s=json.loads((p/'validation_summary.json').read_text())
doublets=pd.read_csv(p/'doublet_scores.csv',index_col='barcode');mapping=pd.read_csv(p/'reference_predictions.csv',index_col='barcode')
check('2700 unique finite doublet scores',len(doublets)==2700 and doublets.index.is_unique and doublets.doublet_score.notna().all() and doublets.doublet_score.between(0,1).all(),{'flags':int(doublets.predicted_doublet.sum()),'range':[doublets.doublet_score.min(),doublets.doublet_score.max()]})
check('automatic flags agree threshold',np.array_equal(doublets.predicted_doublet,doublets.doublet_score>s['scrublet_threshold']),'default expected rate.05; automatic threshold')
base=sc.read_h5ad(primary/'scanpy/analysis_annotated.h5ad');z=sc.read_h5ad(p/'analysis_with_diagnostics.h5ad')
raw=sc.read_h5ad(p/'raw_with_doublet_diagnostics.h5ad')
check('diagnostic H5ADs actual readback',raw.shape==(2700,32738) and z.shape==base.shape and z.obs_names.equals(base.obs_names) and z.var_names.equals(base.var_names),'raw2700×32738; analysis2638×13714')
check('primary counts clusters UMAP unchanged',(z.layers['counts']!=base.layers['counts']).nnz==0 and np.array_equal(z.obsm['X_umap'],base.obsm['X_umap']) and z.obs.cluster.equals(base.obs.cluster),'no diagnostic removal or main re-clustering')
check('mapping unique aligned finite',mapping.index.is_unique and mapping.index.equals(base.obs_names) and mapping.confidence.notna().all() and mapping.confidence.between(0,1).all(),{'cells':len(mapping),'low_confidence':int(mapping.low_confidence.sum())})
prob=pd.read_csv(p/'reference_probabilities.csv',index_col='barcode')
check('reference probability rows and predictions',prob.index.equals(mapping.index) and np.allclose(prob.sum(axis=1),1) and np.array_equal(prob.idxmax(axis=1),mapping.reference_prediction),'distance weighted votes, not calibrated probabilities')
hold=pd.read_csv(p/'reference_holdout_predictions.csv',index_col='barcode')
check('holdout metrics recomputed',np.isclose(accuracy_score(hold.true_label,hold.prediction),s['holdout_accuracy']) and np.isclose(f1_score(hold.true_label,hold.prediction,average='macro'),s['holdout_macro_f1']),{'accuracy':s['holdout_accuracy'],'macro_f1':s['holdout_macro_f1']})
labels={}
for route in ['seurat','scanpy']:
    d=pd.read_csv(p/(route+'_diagnostic_labels.csv'),index_col='barcode')
    labels[route]=d
    represented=d.reference_class_available
    agreement=(d.coarse_marker_label[represented]==d.reference_prediction[represented]).mean()
    check(route+' reference count/agreement',int(represented.sum())==s[route]['represented_cells'] and np.isclose(agreement,s[route]['reference_agreement_represented']),s[route])
    c=pd.read_csv(p/(route+'_reference_crosstab.csv'),index_col=0)
    expected=pd.crosstab(d.coarse_marker_label,d.reference_prediction)
    check(route+' plot table exact',c.equals(expected.rename_axis(index=c.index.name,columns=c.columns.name)) and c.to_numpy().sum()==2638,'each plotted count matches barcode table')
    c=pd.read_csv(p/(route+'_doublets_by_cluster.csv'),index_col=0)
    check(route+' doublet cluster totals',c.to_numpy().sum()==2638 and c['True'].sum()==34,'34 primary QC cells flagged')
for png in p.glob('*.png'):
    with Image.open(png) as im:im.load();shape=im.size
    check(png.name+' decoded',True,shape)
kept=base.obs_names[~doublets.loc[base.obs_names,'predicted_doublet'].to_numpy()]
conditional={'description':'Existing primary cluster labels restricted to unflagged barcodes; no reclustering.',
 'cells':len(kept),'ARI':adjusted_rand_score(labels['seurat'].loc[kept,'cluster'],labels['scanpy'].loc[kept,'cluster']),
 'NMI_arithmetic':normalized_mutual_info_score(labels['seurat'].loc[kept,'cluster'],labels['scanpy'].loc[kept,'cluster']),
 'broad_type_agreement':float((labels['seurat'].loc[kept,'broad_type']==labels['scanpy'].loc[kept,'broad_type']).mean())}
(out/'conditional_comparison.json').write_text(json.dumps(conditional,indent=2)+'\n')
ref=sc.datasets.pbmc68k_reduced()
panel=['CD3D','CD3E','IL7R','CCR7','S100A4','CD8A','CD8B','CCL5','NKG7','GNLY','PRF1','MS4A1','CD79A','CD14','LYZ','S100A8','FCGR3A','MS4A7','LST1','FCER1A','CST3','PPBP','PF4']
pd.DataFrame({'gene':panel,'reference_available':[g in ref.raw.var_names for g in panel],'primary_available':[g in base.raw.var_names for g in panel]}).to_csv(out/'reference_marker_coverage.csv',index=False)
(out/'checks.json').write_text(json.dumps(checks,indent=2,default=str)+'\n')
print('Passed',sum(x['pass'] for x in checks),'/',len(checks));print(json.dumps(conditional,indent=2))
for x in checks:
    if not x['pass']:print('FAIL',x)
sys.exit(0 if all(x['pass'] for x in checks) else 1)
