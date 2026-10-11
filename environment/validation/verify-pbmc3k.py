import matplotlib
matplotlib.use('Agg')
import scanpy as sc
import numpy as np
import matplotlib.pyplot as plt
x = sc.read_10x_mtx('data/pbmc3k/filtered_gene_bc_matrices/hg19', var_names='gene_symbols', cache=False)
x.var_names_make_unique()
assert x.shape == (2700,32738), x.shape
sc.pp.filter_cells(x, min_genes=200)
sc.pp.filter_genes(x, min_cells=3)
x.var['mt'] = x.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(x, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)
x = x[(x.obs.n_genes_by_counts<2500) & (x.obs.pct_counts_mt<5)].copy()
sc.pp.normalize_total(x, target_sum=1e4)
sc.pp.log1p(x)
sc.pp.highly_variable_genes(x, n_top_genes=2000)
x = x[:,x.var.highly_variable].copy()
sc.pp.scale(x,max_value=10)
sc.pp.pca(x, n_comps=30)
sc.pp.neighbors(x,n_neighbors=10,n_pcs=10)
sc.tl.leiden(x,resolution=.5,flavor='igraph',n_iterations=2,directed=False,random_state=42)
sc.tl.umap(x, random_state=42)
assert np.isfinite(x.obsm['X_umap']).all()
sc.pl.umap(x,color='leiden',show=False)
plt.savefig('environment/validation/pbmc3k-scanpy.png')
print(f'PASS PBMC3k Scanpy: input=2700 x 32738; QC cells={x.n_obs}; clusters={x.obs.leiden.nunique()}')
sc.logging.print_versions()
