#!/usr/bin/env python
from pathlib import Path
import sys,json,random,importlib.metadata as md
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
import igraph as ig
from scipy import sparse
out=Path(sys.argv[1]);input=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
seed=42
np.random.seed(seed)
a=sc.read_10x_mtx(input,var_names='gene_symbols',cache=False)
a.var_names_make_unique()
assert not a.obs_names.duplicated().any() and not a.var.gene_ids.duplicated().any()
assert (a.X.data>=0).all() and np.equal(a.X.data,a.X.data.round()).all()
a.var['mt']=a.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(a,qc_vars=['mt'],percent_top=None,log1p=False,inplace=True)
a.obs.to_csv(out/'qc_raw.csv',index_label='barcode')
raw=a.copy()
raw.X=raw.X.astype(np.int32)
raw.write_h5ad(out/'raw_counts.h5ad',compression='gzip')
# Gene filtering before the final QC calculation matches the Seurat creation order.
sc.pp.filter_cells(a,min_genes=200)
sc.pp.filter_genes(a,min_cells=3)
sc.pp.calculate_qc_metrics(a,qc_vars=['mt'],percent_top=None,log1p=False,inplace=True)
a.obs['keep']=(a.obs.n_genes_by_counts>200)&(a.obs.n_genes_by_counts<2500)&(a.obs.pct_counts_mt<5)
a.obs['fail_low_genes']=a.obs.n_genes_by_counts<=200
a.obs['fail_high_genes']=a.obs.n_genes_by_counts>=2500
a.obs['fail_mt']=a.obs.pct_counts_mt>=5
a.obs.to_csv(out/'qc_before.csv',index_label='barcode')
fig,axes=plt.subplots(1,3,figsize=(11,4))
for ax,key in zip(axes,['n_genes_by_counts','total_counts','pct_counts_mt']):
    groups=[a.obs.loc[a.obs.keep==k,key].to_numpy() for k in [False,True]]
    ax.violinplot(groups,showmedians=True);ax.set_xticks([1,2],['Fail','Pass']);ax.set_title(key)
fig.suptitle('Scanpy QC before cell filtering');fig.tight_layout();fig.savefig(out/'qc_violin.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(7,5));g=ax.scatter(a.obs.total_counts,a.obs.n_genes_by_counts,c=a.obs.pct_counts_mt,s=4,cmap='viridis');fig.colorbar(g,ax=ax,label='MT %');ax.axhline(200,linestyle='--');ax.axhline(2500,linestyle='--');ax.set(xlabel='Total UMI',ylabel='Detected genes',title='Scanpy QC');fig.tight_layout();fig.savefig(out/'qc_scatter.png',dpi=160);plt.close(fig)
a=a[a.obs.keep].copy()
a.obs.to_csv(out/'qc_after.csv',index_label='barcode')
a.layers['counts']=a.X.copy().astype(np.int32)
sc.pp.normalize_total(a,target_sum=1e4)
sc.pp.log1p(a)
# Full-gene X/raw remain log-normalized for marker tests and dotplots.
a.raw=a.copy()
sc.pp.highly_variable_genes(a,flavor='seurat',min_mean=.0125,max_mean=3,min_disp=.5)
a.var[['gene_ids','highly_variable','means','dispersions','dispersions_norm']].to_csv(out/'feature_statistics.csv',index_label='gene')
pd.DataFrame({'gene':a.var_names[a.var.highly_variable]}).to_csv(out/'highly_variable_genes.csv',index=False)
work=a[:,a.var.highly_variable].copy()
sc.pp.regress_out(work,['total_counts','pct_counts_mt'],n_jobs=2)
sc.pp.scale(work,max_value=10)
sc.pp.pca(work,n_comps=50,svd_solver='arpack',random_state=seed)
sc.pp.neighbors(work,n_neighbors=10,n_pcs=40,metric='euclidean',random_state=seed)
sc.tl.leiden(work,resolution=1,flavor='igraph',n_iterations=2,directed=False,random_state=seed,key_added='cluster')
sc.tl.umap(work,min_dist=.5,spread=1,random_state=seed)
a.obsm['X_pca']=work.obsm['X_pca'].copy();a.obsm['X_umap']=work.obsm['X_umap'].copy()
a.obsp['connectivities']=work.obsp['connectivities'].copy();a.obsp['distances']=work.obsp['distances'].copy()
a.uns['neighbors']=work.uns['neighbors'].copy();a.uns['umap']=work.uns['umap'].copy()
a.uns['pca_variance_ratio']=work.uns['pca']['variance_ratio'].copy()
a.uns['pca_hvg_gene_ids']=work.var.gene_ids.to_numpy().astype(str)
a.uns['pca_hvg_loadings']=work.varm['PCs'].copy()
a.obs['cluster']=work.obs['cluster'].copy()
a.uns['cluster']=work.uns['cluster'].copy()
a.obs[['cluster']].to_csv(out/'clusters.csv',index_label='barcode')
pd.DataFrame(a.obsm['X_umap'],index=a.obs_names,columns=['UMAP1','UMAP2']).to_csv(out/'umap_coordinates.csv',index_label='barcode')
sc.pl.umap(a,color='cluster',legend_loc='on data',show=False,title='Scanpy Leiden: resolution 1, 40 PCs')
plt.savefig(out/'umap_clusters.png',dpi=160,bbox_inches='tight');plt.close('all')
sc.tl.rank_genes_groups(a,groupby='cluster',reference='rest',method='wilcoxon',use_raw=True,corr_method='benjamini-hochberg',tie_correct=True,pts=True,n_genes=a.n_vars)
markers=sc.get.rank_genes_groups_df(a,group=None).rename(columns={'group':'cluster','names':'gene'})
markers.to_csv(out/'markers_all_tested.csv',index=False)
pos=markers[(markers.logfoldchanges>.25)&(markers.pvals_adj<.05)].copy()
pos.to_csv(out/'markers_positive.csv',index=False)
panel=['CD3D','CD3E','IL7R','CCR7','S100A4','CD8A','CD8B','CCL5','NKG7','GNLY','PRF1','MS4A1','CD79A','CD14','LYZ','S100A8','FCGR3A','MS4A7','LST1','FCER1A','CST3','PPBP','PF4']
panel=[g for g in panel if g in a.var_names]
dot=sc.pl.dotplot(a,panel,groupby='cluster',use_raw=True,standard_scale='var',show=False,return_fig=True)
dot.savefig(out/'marker_dotplot.png',dpi=160);plt.close('all')
dot.dot_color_df.to_csv(out/'marker_dotplot_color.csv')
dot.dot_size_df.to_csv(out/'marker_dotplot_fraction.csv')
profiles=[]
for cl in a.obs.cluster.cat.categories:
    ix=(a.obs.cluster==cl).to_numpy();ids=a.var_names.get_indexer(panel)
    val=a.X[ix,:][:,ids];ct=a.layers['counts'][ix,:][:,ids]
    expressed=np.asarray((ct>0).sum(axis=0)).ravel().astype(np.int64)
    profiles.append(pd.DataFrame({'cluster':str(cl),'gene':panel,'mean_log1p':np.asarray(val.mean(axis=0)).ravel(),'pct_expressing':expressed/int(ix.sum())*100,'n_cells':int(ix.sum()),'expressing_cell_count':expressed}))
pd.concat(profiles).to_csv(out/'canonical_marker_profiles.csv',index=False)
# Controlled variants keep baseline labels unchanged and do not seek target cluster counts.
experiment_rows=[]
def save_variant(name,obj,key):
    pd.DataFrame({'barcode':obj.obs_names,'cluster':obj.obs[key].astype(str).to_numpy()}).to_csv(out/f'experiment_{name}.csv',index=False)
    experiment_rows.append({'variant':name,'n_clusters':obj.obs[key].nunique()})
sc.tl.leiden(work,resolution=.5,flavor='igraph',n_iterations=2,directed=False,random_state=seed,key_added='resolution_05')
save_variant('resolution_05',work,'resolution_05')
sc.tl.leiden(work,resolution=1,flavor='igraph',n_iterations=2,directed=False,random_state=7,key_added='seed_7')
save_variant('seed_7',work,'seed_7')
# Algorithm change on identical graph and resolution; graph conversion mirrors Scanpy.
from scanpy._utils import get_igraph_from_adjacency
g=get_igraph_from_adjacency(work.obsp['connectivities'],directed=False)
ig.set_random_number_generator(random.Random(seed))
louvain=g.community_multilevel(weights='weight',resolution=1)
work.obs['louvain_same_graph']=pd.Categorical([str(x) for x in louvain.membership])
save_variant('louvain_same_graph',work,'louvain_same_graph')
pc10=work.copy()
sc.pp.neighbors(pc10,n_neighbors=10,n_pcs=10,metric='euclidean',random_state=seed)
sc.tl.leiden(pc10,resolution=1,flavor='igraph',n_iterations=2,directed=False,random_state=seed,key_added='pc10')
save_variant('pc10',pc10,'pc10')
noregress=a[:,a.var.highly_variable].copy()
sc.pp.scale(noregress,max_value=10)
sc.pp.pca(noregress,n_comps=50,svd_solver='arpack',random_state=seed)
sc.pp.neighbors(noregress,n_neighbors=10,n_pcs=40,metric='euclidean',random_state=seed)
sc.tl.leiden(noregress,resolution=1,flavor='igraph',n_iterations=2,directed=False,random_state=seed,key_added='no_regression')
save_variant('no_regression',noregress,'no_regression')
pd.DataFrame(experiment_rows).to_csv(out/'experiment_variants.csv',index=False)
a.uns['analysis_parameters']={'seed':seed,'qc_min_genes_strict':200,'qc_max_genes_strict':2500,'qc_max_mt_pct_strict':5,'gene_min_cells':3,'normalization_target_sum':10000,'hvg_flavor':'seurat dispersion-based','regress_out':'total_counts,pct_counts_mt','scale_max':10,'pca_computed':50,'n_pcs_used':40,'n_neighbors':10,'resolution':1.0,'algorithm':'Leiden igraph','leiden_iterations':2,'umap_min_dist':.5,'umap_spread':1.0}
a.write_h5ad(out/'analysis.h5ad',compression='gzip')
loaded=sc.read_h5ad(out/'analysis.h5ad');raw_loaded=sc.read_h5ad(out/'raw_counts.h5ad')
assert loaded.obs_names.equals(a.obs_names) and (loaded.layers['counts']!=a.layers['counts']).nnz==0
assert (raw_loaded.X!=raw.X).nnz==0 and np.isfinite(loaded.obsm['X_umap']).all()
subset=raw_loaded[loaded.obs_names,loaded.var_names]
assert (subset.X!=loaded.layers['counts']).nnz==0
(out/'object_validation.txt').write_text('PASS raw H5AD reopened; counts equal input\nPASS analysis H5AD reopened; counts layer equals input subset; UMAP finite\nPASS no duplicate source or postQC barcodes\n')
(out/'method.txt').write_text('\n'.join(['QC=gene min.cells=3; init min.genes=200; then strict 200<n_genes<2500, pct_counts_mt<5','normalization=total=10000, log1p; full-gene X/raw hold log-normalized expression','counts=integer sparse layers[counts]; raw_counts.h5ad X is integer source matrix','HVG=seurat dispersion flavor min_mean=.0125,max_mean=3,min_disp=.5 (not Seurat vst)','regression=total_counts,pct_counts_mt on HVGs','scaling=HVG mean-center/unit variance,max_value=10','PCA=arpack 50 computed,40 used; seed=42','neighbors=10 euclidean, UMAP fuzzy graph; seed=42','clustering=Leiden igraph resolution=1,n_iterations=2,directed=False,seed=42','UMAP=min_dist=.5,spread=1,seed=42','markers=Wilcoxon tie_correct=True, one cluster vs rest; full-gene raw log-normalized; BH per cluster; no min.pct/logFC prefilter; positive subset logFC>.25,padj<.05','experiments=resolution .5; seed7; Louvain on same graph/resolution; PCs10; no regression; one change each'])+'\n')
(out/'python_runtime.txt').write_text(sys.version+'\n'+sys.executable+'\n')
(out/'python_distribution_versions.json').write_text(json.dumps({d.metadata['Name']:d.version for d in md.distributions() if d.metadata['Name']},indent=2,sort_keys=True)+'\n')
print(f'INPUT {raw.n_obs} cells x {raw.n_vars} genes; POSTQC {a.n_obs} cells x {a.n_vars} genes; HVGs {a.var.highly_variable.sum()}; CLUSTERS {a.obs.cluster.nunique()}',flush=True)
print('PASS Scanpy analysis, markers, plots, H5AD and controlled variants',flush=True)
