#!/usr/bin/env python
"""Apply a reviewed, evidence-based cluster annotation plan to real outputs."""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scanpy as sc
out=Path(sys.argv[1]);plan=json.loads(Path(sys.argv[2]).read_text())
assert json.loads((out/'data_source.json').read_text())['archive_sha256']==plan['reviewed_archive_sha256']
annotations=[];evidence=[]
for route in ['seurat','scanpy']:
    folder=out/route
    labels=pd.read_csv(folder/'clusters.csv',dtype={'barcode':str,'cluster':str})
    assert not labels.barcode.duplicated().any()
    observed=set(labels.cluster)
    assert observed==set(plan[route]),f'{route} cluster labels changed; annotation plan requires review, no automatic recycling'
    profiles=pd.read_csv(folder/'canonical_marker_profiles.csv',dtype={'cluster':str})
    markers=pd.read_csv(folder/'markers_positive.csv',dtype={'cluster':str})
    fc_col='avg_log2FC' if route=='seurat' else 'logfoldchanges'
    padj_col='p_val_adj' if route=='seurat' else 'pvals_adj'
    for cluster,item in plan[route].items():
        subset=markers[markers.cluster==cluster].sort_values([padj_col,fc_col],ascending=[True,False])
        top=list(subset.gene.head(10))
        chosen=item['markers']
        prof=profiles[(profiles.cluster==cluster)&profiles.gene.isin(chosen)].copy()
        assert set(prof.gene)==set(chosen),f'missing annotation evidence: {route}/{cluster}'
        sig_markers=[]
        for gene in chosen:
            row=prof[prof.gene==gene].iloc[0]
            mr=subset[subset.gene==gene]
            if len(mr):sig_markers.append(gene)
            evidence.append({'route':route,'cluster':cluster,'cell_type':item['cell_type'],'gene':gene,'mean_log1p':float(row.mean_log1p),'pct_expressing':float(row.pct_expressing),'positive_marker_log2FC':float(mr.iloc[0][fc_col]) if len(mr) else np.nan,'positive_marker_padj':float(mr.iloc[0][padj_col]) if len(mr) else np.nan,'passes_positive_marker_filter':bool(len(mr))})
        assert len(sig_markers)>=2,f'annotation signature no longer supported: {route}/{cluster}; review required'
        annotations.append({'route':route,'cluster':cluster,'cell_type':item['cell_type'],'broad_type':item['broad_type'],'n_cells':int((labels.cluster==cluster).sum()),'confidence':item['confidence'],'supporting_genes':';'.join(chosen),'significant_supporting_genes':';'.join(sig_markers),'top10_positive_markers':';'.join(top),'rationale':item['rationale'],'limitations':item['limitations'],'source':'https://satijalab.org/seurat/articles/pbmc3k_tutorial','status':'putative marker-based annotation, reviewed against this run'})
    annotation=pd.DataFrame([r for r in annotations if r['route']==route])
    annotation.to_csv(folder/'cell_type_annotation.csv',index=False)
    cmap=annotation.set_index('cluster').cell_type
    labels['cell_type']=labels.cluster.map(cmap)
    labels['broad_type']=labels.cluster.map(annotation.set_index('cluster').broad_type)
    assert labels.cell_type.notna().all()
    labels.to_csv(folder/'cell_labels.csv',index=False)
    if route=='scanpy':
        a=sc.read_h5ad(folder/'analysis.h5ad')
        indexed=labels.set_index('barcode').loc[a.obs_names]
        assert (indexed.cluster.to_numpy()==a.obs.cluster.astype(str).to_numpy()).all()
        a.obs['cell_type']=pd.Categorical(indexed.cell_type)
        a.obs['broad_type']=pd.Categorical(indexed.broad_type)
        sc.pl.umap(a,color='cell_type',legend_loc='right margin',show=False,title='Scanpy: putative marker-based cell types')
        plt.savefig(folder/'umap_cell_types.png',dpi=160,bbox_inches='tight');plt.close('all')
        panel=['CD3D','IL7R','CCR7','S100A4','CD8A','CD8B','CCL5','NKG7','GNLY','MS4A1','CD79A','CD14','LYZ','S100A8','FCGR3A','MS4A7','FCER1A','CST3','PPBP','PF4']
        panel=[g for g in panel if g in a.var_names]
        dot=sc.pl.dotplot(a,panel,groupby='cell_type',use_raw=True,standard_scale='var',show=False,return_fig=True)
        dot.savefig(folder/'marker_dotplot_cell_types.png',dpi=160);plt.close('all')
        a.uns['annotation_note']='Putative canonical-marker annotation; not independently validated. See cell_type_annotation.csv and annotation_evidence.csv.'
        a.write_h5ad(folder/'analysis_annotated.h5ad',compression='gzip')
        loaded=sc.read_h5ad(folder/'analysis_annotated.h5ad')
        assert loaded.obs.cell_type.astype(str).equals(a.obs.cell_type.astype(str))
        assert (loaded.layers['counts']!=a.layers['counts']).nnz==0
pd.DataFrame(annotations).to_csv(out/'cell_type_annotations.csv',index=False)
pd.DataFrame(evidence).to_csv(out/'annotation_evidence.csv',index=False,na_rep='NA')
print(f'PASS reviewed annotations for {len(annotations)} clusters; {len(evidence)} gene/cluster evidence rows')
