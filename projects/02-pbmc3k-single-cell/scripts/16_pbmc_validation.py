#!/usr/bin/env python3
"""Supplementary diagnostics; never remove cells or change primary annotations."""
from pathlib import Path
import argparse, datetime, hashlib, json, shutil, subprocess, sys
import numpy as np
import pandas as pd
import scanpy as sc
from scipy import sparse
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, adjusted_rand_score, normalized_mutual_info_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p = argparse.ArgumentParser()
p.add_argument('primary', type=Path)
p.add_argument('output', type=Path)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
out = a.output
shutil.copy2(__file__, out / Path(__file__).name)
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
meta = {'started_utc': start, 'primary': str(a.primary.resolve()), 'seed': 42,
        'scope': 'Diagnostics only; primary cells, counts, clustering and labels unchanged.',
        'completed': False, 'inputs': {}}
def record(path):
    path = Path(path)
    meta['inputs'][str(path.resolve())] = hashlib.sha256(path.read_bytes()).hexdigest()
    return path
for f in ['scanpy/raw_counts.h5ad', 'scanpy/analysis_annotated.h5ad',
          'seurat/clusters.csv', 'seurat/cell_labels.csv', 'scanpy/cell_labels.csv',
          'seurat/highly_variable_genes.csv']:
    record(a.primary / f)
(out/'provenance.json').write_text(json.dumps(meta, indent=2)+'\n')
raw = sc.read_h5ad(a.primary/'scanpy/raw_counts.h5ad')
query = sc.read_h5ad(a.primary/'scanpy/analysis_annotated.h5ad')
assert raw.n_obs == 2700 and query.n_obs == 2638
assert raw.obs_names.is_unique and raw.var_names.is_unique
assert np.isfinite(raw.X.data).all() and (raw.X.data >= 0).all()
print('Scrublet: raw filtered-UMI input', raw.shape, flush=True)
# Scanpy defaults: expected rate .05; automatic threshold. These are assumptions,
# not a measured doublet frequency, and are not used to alter primary QC.
sc.pp.scrublet(raw, expected_doublet_rate=.05, sim_doublet_ratio=2,
              n_prin_comps=30, random_state=42, verbose=True)
doublets = raw.obs[['doublet_score', 'predicted_doublet']].copy()
doublets['retained_primary_qc'] = doublets.index.isin(query.obs_names)
doublets.to_csv(out/'doublet_scores.csv', index_label='barcode')
doublet_meta = dict(raw.uns['scrublet'])
def serial(x):
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, np.generic): return x.item()
    raise TypeError(type(x).__name__)
(out/'scrublet_parameters.json').write_text(json.dumps(doublet_meta, default=serial, indent=2)+'\n')
raw.write_h5ad(out/'raw_with_doublet_diagnostics.h5ad', compression='gzip')

# This independent reference is shipped with Scanpy, not PBMC3k labels.
ref_path = Path(sc.__file__).parent/'datasets/10x_pbmc68k_reduced.h5ad'
record(ref_path)
ref = sc.datasets.pbmc68k_reduced()
ref.obs.to_csv(out/'reference_observations.csv', index_label='barcode')
ref_map = {
 'CD14+ Monocyte': 'Monocytes', 'Dendritic': 'Dendritic cells',
 'CD19+ B': 'B cells', 'CD56+ NK': 'NK cells',
 'CD4+/CD25 T Reg': 'CD4 T', 'CD4+/CD45RO+ Memory': 'CD4 T',
 'CD4+/CD45RA+/CD25- Naive T': 'CD4 T',
 'CD8+ Cytotoxic T': 'CD8 T', 'CD8+/CD45RA+ Naive Cytotoxic': 'CD8 T',
 'CD34+': 'CD34+ (not a primary PBMC3k class)'}
assert set(ref.obs.bulk_labels.astype(str)) <= set(ref_map)
y = ref.obs.bulk_labels.astype(str).map(ref_map)
genes = ref.raw.var_names.intersection(query.raw.var_names, sort=False)
pd.Series(genes, name='gene').to_csv(out/'reference_common_genes.csv', index=False)
def dense(x): return x.toarray() if sparse.issparse(x) else np.asarray(x)
xref = dense(ref.raw[:, genes].X)
xquery = dense(query.raw[:, genes].X)
assert np.isfinite(xref).all() and np.isfinite(xquery).all()
def classifier():
    return make_pipeline(StandardScaler(), PCA(n_components=30, random_state=42),
                         KNeighborsClassifier(n_neighbors=15, weights='distance'))
train, test = train_test_split(np.arange(ref.n_obs), test_size=.3,
                              stratify=y, random_state=42)
model = classifier().fit(xref[train], y.iloc[train])
holdout_pred = model.predict(xref[test])
holdout = pd.DataFrame({'true_label': y.iloc[test].to_numpy(), 'prediction': holdout_pred},
                       index=ref.obs_names[test])
holdout.to_csv(out/'reference_holdout_predictions.csv', index_label='barcode')
pd.crosstab(holdout.true_label, holdout.prediction).to_csv(out/'reference_holdout_crosstab.csv')
model = classifier().fit(xref, y)
prob = model.predict_proba(xquery)
prediction = model.classes_[prob.argmax(axis=1)]
mapping = pd.DataFrame({'reference_prediction': prediction, 'confidence': prob.max(axis=1)},
                       index=query.obs_names)
mapping['low_confidence'] = mapping.confidence < .5
mapping.to_csv(out/'reference_predictions.csv', index_label='barcode')
pd.DataFrame(prob, index=query.obs_names, columns=model.classes_).to_csv(
    out/'reference_probabilities.csv', index_label='barcode')
metrics = {'raw_cells': raw.n_obs, 'primary_cells': query.n_obs,
 'predicted_doublets_raw': int(doublets.predicted_doublet.sum()),
 'predicted_doublets_primary': int(doublets.loc[query.obs_names].predicted_doublet.sum()),
 'scrublet_threshold': float(doublet_meta['threshold']),
 'reference_cells': ref.n_obs, 'reference_genes': ref.n_vars, 'common_genes': len(genes),
 'holdout_cells': len(test), 'holdout_accuracy': accuracy_score(y.iloc[test], holdout_pred),
 'holdout_macro_f1': f1_score(y.iloc[test], holdout_pred, average='macro'),
 'low_confidence_query_cells': int(mapping.low_confidence.sum()),
 'method': 'Reference-only z scaling and PCA30, distance-weighted kNN15; seed42; stratified30% holdout.',
 'limitations': ['Independent PBMC68k donor A reduced reference; not PBMC3k ground truth.',
 'Only common reference genes; reference has no platelets or FCGR3A-specific monocytes.',
 'Monocyte subtypes pooled; CD4 subtypes pooled. Confidence is a kNN vote, not calibrated probability.',
 'Scrublet rate .05 is an assumed default; automatic flags are diagnostic, no cells removed.',
 'Protein measurements absent. No claim of experimental cell-type accuracy.']}
for route in ['seurat', 'scanpy']:
    labels = pd.read_csv(a.primary/route/'cell_labels.csv', index_col='barcode')
    merged = labels.join(mapping).join(doublets.loc[query.obs_names])
    coarse = merged.broad_type.replace({'CD14 monocytes':'Monocytes', 'FCGR3A monocytes':'Monocytes'})
    represented = coarse.isin(model.classes_)
    merged['coarse_marker_label'] = coarse
    merged['reference_class_available'] = represented
    merged['reference_agrees'] = (coarse == merged.reference_prediction) & represented
    merged.to_csv(out/(route+'_diagnostic_labels.csv'), index_label='barcode')
    cross = pd.crosstab(coarse, merged.reference_prediction)
    cross.to_csv(out/(route+'_reference_crosstab.csv'))
    pd.crosstab(merged.cluster, merged.predicted_doublet).to_csv(out/(route+'_doublets_by_cluster.csv'))
    metrics[route] = {'represented_cells': int(represented.sum()),
      'unrepresented_cells': int((~represented).sum()),
      'reference_agreement_represented': float((coarse[represented] == merged.reference_prediction[represented]).mean())}
    fig, ax = plt.subplots(figsize=(11,6))
    im = ax.imshow(cross, cmap='Blues', aspect='auto')
    ax.set_xticks(range(cross.shape[1]), cross.columns, rotation=45, ha='right')
    ax.set_yticks(range(cross.shape[0]), cross.index)
    for i in range(cross.shape[0]):
        for j in range(cross.shape[1]): ax.text(j,i,str(cross.iloc[i,j]),ha='center',va='center',fontsize=8)
    ax.set(xlabel='Independent reference prediction', ylabel='Coarse putative marker label',
           title=f'{route}: PBMC68k reference mapping (not ground truth)')
    fig.colorbar(im, ax=ax); fig.tight_layout(); fig.savefig(out/(route+'_reference_crosstab.png'),dpi=150); plt.close(fig)
query.obs = query.obs.join(mapping).join(doublets.loc[query.obs_names])
query.write_h5ad(out/'analysis_with_diagnostics.h5ad', compression='gzip')
fig, axes = plt.subplots(1,2,figsize=(12,5))
umap = query.obsm['X_umap']
im = axes[0].scatter(*umap.T,c=query.obs.doublet_score,s=4)
fig.colorbar(im,ax=axes[0],label='Scrublet score')
axes[1].scatter(*umap.T,c=query.obs.predicted_doublet.astype(int),s=4,cmap='coolwarm')
for ax in axes: ax.set(xlabel='UMAP1',ylabel='UMAP2')
axes[0].set_title('Original Scanpy UMAP: doublet score')
axes[1].set_title('Automatic flags; primary cells retained')
fig.tight_layout(); fig.savefig(out/'doublet_umap.png',dpi=150); plt.close(fig)

# Additional one-factor experiments use fixed primary settings, not tuned targets.
seurat = pd.read_csv(a.primary/'seurat/clusters.csv', index_col='barcode').cluster.astype(str).loc[query.obs_names]
baseline = query.obs.cluster.astype(str)
experiments=[]
for name in ['neighbors20', 'exact_neighbors10', 'seurat_hvg']:
    work = query.copy()
    if name == 'seurat_hvg':
        hvgs = pd.read_csv(a.primary/'seurat/highly_variable_genes.csv').gene
        work = work[:, work.var_names.isin(hvgs)].copy()
        sc.pp.regress_out(work, ['total_counts','pct_counts_mt'], n_jobs=2)
        sc.pp.scale(work, max_value=10)
        sc.pp.pca(work,n_comps=50,svd_solver='arpack',random_state=42)
    kwargs = {'n_neighbors':20 if name=='neighbors20' else 10, 'n_pcs':40, 'random_state':42}
    if name == 'exact_neighbors10': kwargs['transformer']='sklearn'
    sc.pp.neighbors(work, **kwargs)
    sc.tl.leiden(work,resolution=1,flavor='igraph',n_iterations=2,directed=False,random_state=42,key_added='experiment')
    labels=work.obs.experiment.astype(str)
    labels.to_csv(out/(name+'_clusters.csv'),index_label='barcode')
    experiments.append({'experiment':name,'cells':len(labels),'clusters':labels.nunique(),
      'ARI_vs_primary_scanpy':adjusted_rand_score(baseline,labels),
      'NMI_vs_primary_scanpy':normalized_mutual_info_score(baseline,labels),
      'ARI_vs_seurat':adjusted_rand_score(seurat,labels),
      'NMI_vs_seurat':normalized_mutual_info_score(seurat,labels)})
    print('Experiment', experiments[-1], flush=True)
pd.DataFrame(experiments).to_csv(out/'additional_controlled_experiments.csv',index=False)
(out/'validation_summary.json').write_text(json.dumps(metrics,indent=2)+'\n')
subprocess.run([sys.executable,'-m','pip','freeze'],stdout=(out/'python-freeze.txt').open('w'),check=True)
meta.update(completed=True, ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(out/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
manifest={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file()}
(out/'sha256-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(metrics,indent=2),flush=True)
