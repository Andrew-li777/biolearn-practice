#!/usr/bin/env python
from pathlib import Path
import sys,json,inspect,importlib.metadata as md
import numpy as np
import pandas as pd
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats
outdir=Path(sys.argv[1]) if len(sys.argv)>1 else Path('results/bulk')
counts=pd.read_csv(outdir/'airway_counts.csv',index_col=0).T
meta=pd.read_csv(outdir/'airway_coldata.csv',index_col=0).loc[counts.index,['cell','dex']]
assert counts.index.equals(meta.index) and not counts.columns.duplicated().any()
assert not meta.isna().any().any()
assert (counts.to_numpy()>=0).all() and np.equal(counts,counts.round()).all().all()
meta['cell']=pd.Categorical(meta.cell,categories=sorted(meta.cell.unique()))
meta['dex']=pd.Categorical(meta.dex,categories=['untrt','trt'])
keep=(counts>=10).sum(axis=0)>=3
pd.DataFrame({'gene':counts.columns,'keep':keep.to_numpy()}).to_csv(outdir/'pydeseq2_filter.csv',index=False)
counts=counts.loc[:,keep].astype('int64')
print(f'INPUT: {len(meta)} samples; PRE_FILTER: {counts.shape[1]} genes',flush=True)
dds=DeseqDataSet(counts=counts,metadata=meta,design='~ cell + dex',fit_type='parametric',size_factors_fit_type='ratio',refit_cooks=True,min_replicates=7,n_cpus=2)
design=dds.obsm['design_matrix']
assert np.linalg.matrix_rank(design)==design.shape[1]
design.to_csv(outdir/'python_design_matrix.csv')
dds.deseq2()
stats=DeseqStats(dds,contrast=['dex','trt','untrt'],alpha=0.1,cooks_filter=True,independent_filter=True,n_cpus=2)
stats.summary()
r=stats.results_df.rename(columns={'log2FoldChange':'log2FC'}).copy()
r.index.name='gene'
annotation=pd.read_csv(outdir/'gene_annotation.csv').set_index('gene')
r.insert(0,'symbol',annotation.symbol.reindex(r.index))
r['significant']=r.padj.notna() & (r.padj<0.1)
r.reset_index().to_csv(outdir/'pydeseq2_results.csv',index=False,na_rep='NA')
pd.DataFrame({'sample':dds.obs_names,'size_factor':dds.obs['size_factors'].to_numpy()}).to_csv(outdir/'pydeseq2_size_factors.csv',index=False)
(outdir/'pydeseq2_method.txt').write_text('\n'.join(['method=PyDESeq2','design=~ cell + dex','contrast=[dex, trt, untrt]','alpha=0.1','prefilter=at least 3 samples with count >= 10 (same as DESeq2)','normalization=median-of-ratios; size_factors_fit_type=ratio','fit_type=parametric; actual='+str(dds.uns.get('disp_function_type','see log')),'test=two-sided Wald; lfc_null=0','p_adjust=BH with independent_filter=True at alpha=0.1','cooks_filter=True; refit_cooks=True; min_replicates=7','comparison_LFC=unshrunk MLE','implementation=Python; numerical fitting, bounds and independent filtering may differ from R','n_cpus=2'])+'\n')
versions={d.metadata['Name']:d.version for d in md.distributions() if d.metadata['Name']}
(outdir/'python_distribution_versions.json').write_text(json.dumps(versions,indent=2,sort_keys=True)+'\n')
(outdir/'python_runtime.txt').write_text(sys.version+'\n'+sys.executable+'\nDeseqDataSet: '+str(inspect.signature(DeseqDataSet))+'\nDeseqStats: '+str(inspect.signature(DeseqStats))+'\n')
print(f'SIGNIFICANT: {r.significant.sum()} UP: {(r.significant & (r.log2FC>0)).sum()} DOWN: {(r.significant & (r.log2FC<0)).sum()}',flush=True)
print('PASS PyDESeq2 analysis',flush=True)
