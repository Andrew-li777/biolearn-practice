#!/usr/bin/env python3
from pathlib import Path
import sys,json,hashlib
import pandas as pd
import numpy as np
from scipy.io import mmread
import scanpy as sc
from sklearn.metrics import adjusted_rand_score,normalized_mutual_info_score
p=Path(sys.argv[1]);primary=Path(sys.argv[2])
m=json.loads((p/'sha256-manifest.json').read_text())
bad=[f for f,h in m.items() if hashlib.sha256((p/f).read_bytes()).hexdigest()!=h]
meta=json.loads((p/'provenance.json').read_text())
changed=[f for f,h in meta['inputs'].items() if hashlib.sha256(Path(f).read_bytes()).hexdigest()!=h]
a=sc.read_h5ad(primary/'scanpy/analysis.h5ad')
s=pd.read_csv(primary/'seurat/clusters.csv',index_col='barcode').cluster.astype(str)
rows=pd.read_csv(p/'graph_resolution_experiments.csv');checks=[]
for _,r in rows.iterrows():
 l=pd.read_csv(p/(r.variant+'_clusters.csv'),index_col='barcode').diagnostic.astype(str)
 ok=l.index.is_unique and np.array_equal(l.index,a.obs_names) and l.nunique()==r.clusters and np.isclose(adjusted_rand_score(s,l),r.ARI_vs_seurat) and np.isclose(normalized_mutual_info_score(s,l),r.NMI_vs_seurat) and np.isclose(adjusted_rand_score(a.obs.cluster.astype(str),l),r.ARI_vs_scanpy)
 checks.append({'variant':r.variant,'pass':bool(ok),'clusters':int(r.clusters)})
g=mmread(p/'seurat_snn.mtx').tocsr();sym=(g-g.T).nnz==0
summary={'manifest_files':len(m),'hash_mismatch':bad,'changed_inputs':changed,'symmetric_seurat_graph':sym,'variants':checks,'pass':not bad and not changed and sym and all(x['pass'] for x in checks),'graph_edge_Jaccard':meta['graph_edge_Jaccard']}
(p/'verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2));sys.exit(0 if summary['pass'] else 1)
