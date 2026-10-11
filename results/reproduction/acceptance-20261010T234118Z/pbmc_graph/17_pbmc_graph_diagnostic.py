#!/usr/bin/env python3
from pathlib import Path
import sys,json,hashlib,shutil,datetime
import scanpy as sc
import pandas as pd
import numpy as np
from scipy.io import mmread
from sklearn.metrics import adjusted_rand_score,normalized_mutual_info_score
primary=Path(sys.argv[1]);out=Path(sys.argv[2])
a=sc.read_h5ad(primary/'scanpy/analysis.h5ad')
barcodes=pd.read_csv(out/'seurat_snn_barcodes.csv').barcode
assert np.array_equal(barcodes,a.obs_names)
g=mmread(out/'seurat_snn.mtx').tocsr()
assert g.shape==(a.n_obs,a.n_obs) and np.isfinite(g.data).all() and (g.data>=0).all()
seurat=pd.read_csv(primary/'seurat/clusters.csv',index_col='barcode').cluster.astype(str).loc[a.obs_names]
baseline=a.obs.cluster.astype(str)
graphs={'seurat_snn':g,'scanpy_fuzzy':a.obsp['connectivities']}
stats=[];rows=[]
for name,graph in graphs.items():
 stats.append({'graph':name,'cells':graph.shape[0],'nonzero_entries':graph.nnz,'weight_min':graph.data.min(),'weight_max':graph.data.max(),'mean_nonzero_degree':float(np.diff(graph.indptr).mean())})
 for res in [.5,1.]:
  sc.tl.leiden(a,adjacency=graph,resolution=res,flavor='igraph',n_iterations=2,directed=False,random_state=42,key_added='diagnostic')
  labels=a.obs.diagnostic.astype(str)
  variant=name+'_leiden_res_'+str(res)
  labels.to_csv(out/(variant+'_clusters.csv'),index_label='barcode')
  rows.append({'variant':variant,'graph':name,'algorithm':'Leiden igraph','resolution':res,'cells':len(labels),'clusters':labels.nunique(),'ARI_vs_seurat':adjusted_rand_score(seurat,labels),'NMI_vs_seurat':normalized_mutual_info_score(seurat,labels),'ARI_vs_scanpy':adjusted_rand_score(baseline,labels),'NMI_vs_scanpy':normalized_mutual_info_score(baseline,labels)})
pd.DataFrame(stats).to_csv(out/'graph_statistics.csv',index=False)
pd.DataFrame(rows).to_csv(out/'graph_resolution_experiments.csv',index=False)
sb=g.copy();sb.setdiag(0);sb.eliminate_zeros();sb.data=np.ones(sb.nnz)
fb=graphs['scanpy_fuzzy'].copy();fb.setdiag(0);fb.eliminate_zeros();fb.data=np.ones(fb.nnz)
intersection=sb.multiply(fb).nnz;union=(sb+fb).nnz
meta={'completed':True,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'primary':str(primary.resolve()),'seed':42,'graph_edge_Jaccard':intersection/union,'shared_directed_edges':intersection,'union_directed_edges':union,'interpretation':'Fixed Leiden implementation, seed and resolution compare saved Seurat SNN vs Scanpy fuzzy graphs. Upstream PCA/HVG/regression/k remain graph-specific; graph effect is bundled, not an isolated graph-construction formula effect. Primary outputs unchanged.','inputs':{str(primary/f):hashlib.sha256((primary/f).read_bytes()).hexdigest() for f in ['seurat/analysis.rds','seurat/clusters.csv','scanpy/analysis.h5ad']}}
for script in ['17_pbmc_graph_diagnostic.R','17_pbmc_graph_diagnostic.py']:shutil.copy2(Path('scripts')/script,out/script)
(out/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
manifest={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file()}
(out/'sha256-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(pd.DataFrame(rows).to_string(index=False));print(json.dumps(meta,indent=2))
