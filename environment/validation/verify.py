import importlib
import importlib.metadata as md
import json
from pathlib import Path
modules = {'scanpy':'scanpy','pydeseq2':'pydeseq2','igraph':'igraph','leidenalg':'leidenalg','numpy':'numpy','scipy':'scipy','pandas':'pandas','sklearn':'scikit-learn','matplotlib':'matplotlib','seaborn':'seaborn','anndata':'anndata','h5py':'h5py','statsmodels':'statsmodels','umap':'umap-learn','skmisc':'scikit-misc'}
versions = {}
for module, dist in modules.items():
    importlib.import_module(module)
    versions[dist] = md.version(dist)
    print(f'PASS import: {module} {versions[dist]}', flush=True)
Path('environment/validation/python-versions.json').write_text(json.dumps(versions,indent=2)+'\n')
import scanpy as sc
import numpy as np
import matplotlib
matplotlib.use('Agg')
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
from scipy.stats import spearmanr
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats
rng = np.random.default_rng(42)
a = sc.AnnData(rng.poisson(3, (100, 50)).astype(np.float32))
sc.pp.normalize_total(a)
sc.pp.log1p(a)
sc.pp.pca(a, n_comps=10)
sc.pp.neighbors(a, n_neighbors=10, n_pcs=10)
sc.tl.leiden(a, flavor='igraph', n_iterations=2, directed=False, key_added='igraph')
sc.tl.leiden(a, flavor='leidenalg', key_added='leidenalg')
sc.tl.umap(a)
sc.tl.rank_genes_groups(a, 'igraph', method='wilcoxon')
assert np.isfinite(a.obsm['X_umap']).all()
assert adjusted_rand_score(a.obs.igraph, a.obs.igraph)==1
assert normalized_mutual_info_score(a.obs.igraph, a.obs.igraph)==1
assert spearmanr([1,2,3],[1,2,3]).statistic==1
sc.pl.umap(a, color='igraph', show=False)
import matplotlib.pyplot as plt
plt.savefig('environment/validation/python-plot.png')
a.write_h5ad('environment/validation/synthetic-smoke.h5ad')
print('PASS Scanpy PCA/neighbors/Leiden (both backends)/UMAP/markers/plot/H5AD and comparison metrics',flush=True)
import pandas as pd
counts = pd.DataFrame(rng.negative_binomial(10, .5, (8, 100)), index=[f's{i}' for i in range(8)])
meta = pd.DataFrame({'condition':['control']*4+['treated']*4}, index=counts.index)
dds = DeseqDataSet(counts=counts, metadata=meta, design='~condition', n_cpus=2)
dds.deseq2()
stats = DeseqStats(dds, contrast=['condition','treated','control'], n_cpus=2)
stats.summary()
assert stats.results_df.pvalue.notna().any()
print('PASS PyDESeq2 fit and statistical test',flush=True)
import sys
print('Python:', sys.version)
print('Executable:', sys.executable)
