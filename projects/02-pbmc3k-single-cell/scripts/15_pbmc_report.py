#!/usr/bin/env python
from pathlib import Path
import sys,json,datetime
import numpy as np
import pandas as pd
from scipy.io import mmread
from scipy import sparse
from sklearn.metrics import adjusted_rand_score,normalized_mutual_info_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import scanpy as sc
from PIL import Image
root=Path(sys.argv[1]);checks=[]
def check(name,ok,detail):checks.append({'check':name,'status':'PASS' if ok else 'FAIL','detail':str(detail)})
def read_labels(path):
    d=pd.read_csv(path,dtype={'barcode':str,'cluster':str})
    check(f'unique barcodes: {path.relative_to(root)}',not d.barcode.duplicated().any(),int(d.barcode.duplicated().sum()))
    if d.barcode.duplicated().any():raise ValueError(f'duplicate barcodes: {path}')
    assert not d[['barcode','cluster']].isna().any().any()
    return d.set_index('barcode')
def metrics(a,b):
    shared=a.index.intersection(b.index)
    assert len(shared)>0
    return {'n_a':len(a),'n_b':len(b),'shared':len(shared),'only_a':len(a.index.difference(b.index)),'only_b':len(b.index.difference(a.index)),'clusters_a':a.cluster.nunique(),'clusters_b':b.cluster.nunique(),'ARI':adjusted_rand_score(a.loc[shared,'cluster'],b.loc[shared,'cluster']),'NMI_arithmetic':normalized_mutual_info_score(a.loc[shared,'cluster'],b.loc[shared,'cluster'],average_method='arithmetic')}
source=json.loads((root/'data_source.json').read_text())
input=Path(source['input_directory'])
barcodes=pd.read_csv(input/'barcodes.tsv',header=None)[0].astype(str)
check('no duplicate source barcodes',not barcodes.duplicated().any(),f'{len(barcodes)} source cells')
raw=sc.read_h5ad(root/'scanpy/raw_counts.h5ad')
original=mmread(input/'matrix.mtx').T.tocsr()
check('raw H5AD counts equal source matrix',raw.shape==original.shape and (raw.X!=original).nnz==0,raw.shape)
check('raw H5AD source barcodes preserved',list(raw.obs_names)==list(barcodes),'exact IDs, preserve -1 suffix')
check('integer raw counts',np.equal(raw.X.data,raw.X.data.round()).all() and (raw.X.data>=0).all(),'not normalized counts')
labels={};qc_rows=[];summaries=[]
for route in ['seurat','scanpy']:
    folder=root/route
    d=read_labels(folder/'clusters.csv');labels[route]=d
    cell_labels=read_labels(folder/'cell_labels.csv')
    ann=pd.read_csv(folder/'cell_type_annotation.csv',dtype={'cluster':str})
    check(f'{route} annotations cover observed clusters',set(ann.cluster)==set(d.cluster) and not ann.cluster.duplicated().any(),len(ann))
    check(f'{route} cell annotations align',d.index.equals(cell_labels.index) and d.cluster.equals(cell_labels.cluster) and cell_labels.cell_type.notna().all(),len(cell_labels))
    q0=pd.read_csv(folder/'qc_raw.csv',index_col=0)
    q=pd.read_csv(folder/'qc_before.csv',index_col=0)
    after=pd.read_csv(folder/'qc_after.csv',index_col=0)
    keygenes='nFeature_RNA' if route=='seurat' else 'n_genes_by_counts'
    keyumi='nCount_RNA' if route=='seurat' else 'total_counts'
    keymt='percent.mt' if route=='seurat' else 'pct_counts_mt'
    expected=(q[keygenes]>200)&(q[keygenes]<2500)&(q[keymt]<5)
    check(f'{route} QC mask matches fixed thresholds',np.array_equal(expected,q.keep),'strict 200 < genes < 2500 and MT % < 5')
    check(f'{route} postQC membership from real QC mask',set(q.index[expected])==set(d.index)==set(after.index),len(d))
    check(f'{route} source membership',set(d.index)<=set(barcodes),len(d))
    for stage,df,g,u,m in [('raw',q0,'n_genes' if route=='seurat' else keygenes,'total_counts','pct_mt' if route=='seurat' else keymt),('before_final_qc',q,keygenes,keyumi,keymt),('after_final_qc',after,keygenes,keyumi,keymt)]:
        qc_rows.append({'route':route,'stage':stage,'cells':len(df),'median_genes':df[g].median(),'median_UMI':df[u].median(),'median_mt_pct':df[m].median(),'max_genes':df[g].max(),'max_mt_pct':df[m].max()})
    markers=pd.read_csv(folder/'markers_all_tested.csv',dtype={'cluster':str})
    pk='p_val' if route=='seurat' else 'pvals';ak='p_val_adj' if route=='seurat' else 'pvals_adj';fc='avg_log2FC' if route=='seurat' else 'logfoldchanges'
    check(f'{route} marker table covers clusters',set(markers.cluster)==set(d.cluster),len(markers))
    check(f'{route} unique cluster/gene marker rows',not markers.duplicated(['cluster','gene']).any(),len(markers))
    check(f'{route} valid marker probabilities',np.isfinite(markers[[pk,ak]]).all().all() and markers[pk].between(0,1).all() and markers[ak].between(0,1).all(),'finite in [0,1]')
    check(f'{route} marker finite logFC',np.isfinite(markers[fc]).all(),len(markers))
    positive=pd.read_csv(folder/'markers_positive.csv',dtype={'cluster':str})
    check(f'{route} positive marker filter',len(positive)>0 and (positive[ak]<.05).all() and (positive[fc]> (0 if route=='seurat' else .25)).all(),len(positive))
    top=positive.sort_values([ak,fc],ascending=[True,False]).groupby('cluster',sort=False).head(10)
    top.to_csv(folder/'top10_markers.csv',index=False)
    coordinates=pd.read_csv(folder/'umap_coordinates.csv',index_col=0)
    check(f'{route} UMAP aligned and finite',list(coordinates.index)==list(d.index) and np.isfinite(coordinates).all().all(),coordinates.shape)
    verification=(folder/'object_validation.txt').read_text()
    check(f'{route} raw and analysis object reopened',verification.count('PASS')==3,verification.strip())
    objects=['raw_counts.rds','analysis.rds','analysis_annotated.rds'] if route=='seurat' else ['raw_counts.h5ad','analysis.h5ad','analysis_annotated.h5ad']
    for filename in objects:check(f'{route} object {filename}',(folder/filename).stat().st_size>1000,(folder/filename).stat().st_size)
    for filename in ['qc_violin.png','qc_scatter.png','umap_clusters.png','umap_cell_types.png','marker_dotplot.png','marker_dotplot_cell_types.png']:
        with Image.open(folder/filename) as im:im.verify()
        check(f'{route} figure {filename}',(folder/filename).stat().st_size>1000,'decoded PNG')
    summaries.append({'route':route,'raw_cells':len(q0),'before_final_QC_cells':len(q),'QC_pass_cells':len(d),'rejected_cells':len(q)-len(d),'fail_low_genes':int((q[keygenes]<=200).sum()),'fail_high_genes':int((q[keygenes]>=2500).sum()),'fail_mt':int((q[keymt]>=5).sum()),'clusters':d.cluster.nunique(),'marker_rows_returned':len(markers),'positive_marker_rows':len(positive)})
summary=pd.DataFrame(summaries);summary.to_csv(root/'analysis_summary.csv',index=False)
pd.DataFrame(qc_rows).to_csv(root/'qc_statistics.csv',index=False)
a,b=labels['seurat'],labels['scanpy'];shared=a.index.intersection(b.index)
comparison=metrics(a,b)
(root/'comparison_metrics.json').write_text(json.dumps(comparison,indent=2)+'\n')
pd.DataFrame({'barcode':a.index.difference(b.index)}).to_csv(root/'seurat_only_cells.csv',index=False)
pd.DataFrame({'barcode':b.index.difference(a.index)}).to_csv(root/'scanpy_only_cells.csv',index=False)
joined=pd.DataFrame({'seurat_cluster':a.loc[shared,'cluster'],'scanpy_cluster':b.loc[shared,'cluster']},index=shared)
for route in ['seurat','scanpy']:
    cell=read_labels(root/route/'cell_labels.csv')
    joined[f'{route}_cell_type']=cell.loc[shared,'cell_type']
    joined[f'{route}_broad_type']=cell.loc[shared,'broad_type']
joined.to_csv(root/'barcode_alignment.csv',index_label='barcode')
cross=pd.crosstab(joined.seurat_cluster,joined.scanpy_cluster)
cross.to_csv(root/'cluster_crosstab.csv')
cross.div(cross.sum(axis=1),axis=0).to_csv(root/'cluster_crosstab_row_fraction.csv')
pd.crosstab(joined.seurat_cell_type,joined.scanpy_cell_type).to_csv(root/'cell_type_crosstab.csv')
comparison['broad_type_agreement']=float((joined.seurat_broad_type==joined.scanpy_broad_type).mean())
(root/'comparison_metrics.json').write_text(json.dumps(comparison,indent=2)+'\n')
fig,ax=plt.subplots(figsize=(10,7));sns.heatmap(cross,annot=True,fmt='d',cmap='Blues',ax=ax);ax.set(title='PBMC3k: shared-cell cluster contingency',xlabel='Scanpy cluster',ylabel='Seurat cluster');fig.tight_layout();fig.savefig(root/'cluster_crosstab.png',dpi=160);plt.close(fig)
check('contingency conserves shared cells',int(cross.to_numpy().sum())==len(shared),len(shared))
check('metric bounds',-1<=comparison['ARI']<=1 and 0<=comparison['NMI_arithmetic']<=1,comparison)
# Raw source totals agree; final QC metrics checked across tools on exact barcode IDs.
qs=pd.read_csv(root/'seurat/qc_before.csv',index_col=0)
qp=pd.read_csv(root/'scanpy/qc_before.csv',index_col=0).loc[qs.index]
qc_diff=pd.DataFrame({'barcode':qs.index,'genes_difference':qs.nFeature_RNA.to_numpy()-qp.n_genes_by_counts.to_numpy(),'UMI_difference':qs.nCount_RNA.to_numpy()-qp.total_counts.to_numpy(),'MT_pct_difference':qs['percent.mt'].to_numpy()-qp.pct_counts_mt.to_numpy()})
qc_diff.to_csv(root/'qc_cross_tool_differences.csv',index=False)
check('two routes QC metrics equal on matched cells',np.allclose(qc_diff.iloc[:,1:].to_numpy(),0,atol=1e-5),'max differences='+str(qc_diff.iloc[:,1:].abs().max().to_dict()))
# H5AD serialized annotations/counts validated against exported actual tables and raw input.
for filename in ['analysis.h5ad','analysis_annotated.h5ad']:
    obj=sc.read_h5ad(root/'scanpy'/filename)
    check(f'{filename} labels match exported table',obj.obs_names.equals(b.index) and list(obj.obs.cluster.astype(str))==list(b.cluster),obj.shape)
    check(f'{filename} count layer equals raw source subset',(obj.layers['counts']!=raw[obj.obs_names,obj.var_names].X).nnz==0,'integer counts preserved')
    check(f'{filename} marker expression is log-normalized',obj.X.min()>=0 and obj.raw is not None and (obj.raw.X!=obj.X).nnz==0,'full-gene X and raw; not scaled residuals')
    if filename=='analysis_annotated.h5ad':
        lab=pd.read_csv(root/'scanpy/cell_labels.csv',index_col=0)
        check('annotated H5AD cell types match table',list(obj.obs.cell_type.astype(str))==list(lab.loc[obj.obs_names,'cell_type']),len(obj.obs))
check('annotated RDS validated',(root/'seurat/annotation_object_validation.txt').read_text().count('PASS')==2,'R process reopened annotated object and checked labels/counts')
# Match HVGs by stable gene IDs instead of differing symbol uniquification.
sf=pd.read_csv(root/'seurat/feature_map.csv').set_index('analysis_gene')
shvg=pd.read_csv(root/'seurat/highly_variable_genes.csv').gene
pf=pd.read_csv(root/'scanpy/feature_statistics.csv',index_col=0)
sh=set(sf.loc[shvg,'gene_id']);ph=set(pf.loc[pf.highly_variable,'gene_ids'])
hvg={'seurat_hvgs':len(sh),'scanpy_hvgs':len(ph),'intersection':len(sh&ph),'jaccard':len(sh&ph)/len(sh|ph)}
(root/'hvg_overlap.json').write_text(json.dumps(hvg,indent=2)+'\n')
experiments=[]
variant_changes={'resolution_05':'only resolution: 1 -> 0.5; same graph/seed','seed_7':'only Leiden random_state: 42 -> 7; same graph/resolution','louvain_same_graph':'only clustering optimizer: Leiden -> igraph multilevel Louvain; same graph/resolution/seed','pc10':'only neighbors input PCs: 40 -> 10; graph rebuilt; same neighbor count/metric/seed','no_regression':'only remove total_counts/MT regression; same cells/HVGs/scaling/PCA dimension/neighbors/resolution/seed'}
for path in sorted((root/'scanpy').glob('experiment_*.csv')):
    if path.name=='experiment_variants.csv':continue
    variant=path.stem.removeprefix('experiment_')
    v=read_labels(path);base=metrics(b,v);crossmetric=metrics(a,v)
    check(f'experiment same cell universe {variant}',set(v.index)==set(b.index),len(v))
    experiments.append({'route':'scanpy','variant':variant,'changed':variant_changes[variant],'baseline_clusters':b.cluster.nunique(),'variant_clusters':v.cluster.nunique(),'ARI_vs_route_baseline':base['ARI'],'NMI_vs_route_baseline':base['NMI_arithmetic'],'ARI_vs_other_route_baseline':crossmetric['ARI'],'NMI_vs_other_route_baseline':crossmetric['NMI_arithmetic'],'evidence_status':'experimentally measured; does not uniquely explain entire between-route difference'})
v=read_labels(root/'seurat/experiment_resolution_1.csv');base=metrics(a,v);other=metrics(b,v)
check('Seurat resolution experiment same cells',set(v.index)==set(a.index),len(v))
experiments.append({'route':'seurat','variant':'resolution_1','changed':'only resolution: 0.5 -> 1; same SNN/seed','baseline_clusters':a.cluster.nunique(),'variant_clusters':v.cluster.nunique(),'ARI_vs_route_baseline':base['ARI'],'NMI_vs_route_baseline':base['NMI_arithmetic'],'ARI_vs_other_route_baseline':other['ARI'],'NMI_vs_other_route_baseline':other['NMI_arithmetic'],'evidence_status':'experimentally measured; does not uniquely explain entire between-route difference'})
ex=pd.DataFrame(experiments);ex.to_csv(root/'controlled_experiments.csv',index=False)
annotation=pd.read_csv(root/'cell_type_annotations.csv',dtype={'cluster':str})
evidence=pd.read_csv(root/'annotation_evidence.csv',dtype={'cluster':str})
check('annotations have recorded expression evidence',len(evidence)>0 and evidence.mean_log1p.notna().all() and evidence.pct_expressing.between(0,100).all(),len(evidence))
profile=pd.read_csv(root/'scanpy/canonical_marker_profiles.csv',dtype={'cluster':str})
check('Scanpy expression count schema','expressing_cell_count' in profile.columns,list(profile.columns))
if 'expressing_cell_count' in profile:
    numer=profile.expressing_cell_count
    check('Scanpy expression counts integer and bounded',np.isfinite(numer).all() and (numer==numer.round()).all() and (numer>=0).all() and (numer<=profile.n_cells).all(),len(profile))
    check('Scanpy expression proportions from integer counts',np.allclose(profile.pct_expressing,numer/profile.n_cells*100,rtol=1e-12,atol=1e-12),len(profile))
check('annotation evidence unique full key',not evidence.duplicated(['route','cluster','gene']).any(),len(evidence))
missing=evidence.positive_marker_padj.isna()
check('annotation evidence missing tests explicitly unsupported',np.array_equal(missing,evidence.positive_marker_log2FC.isna()) and (~evidence.loc[missing,'passes_positive_marker_filter']).all(),int(missing.sum()))
check('annotation signature supported',annotation.significant_supporting_genes.fillna('').str.split(';').apply(len).ge(2).all(),'at least two positive canonical markers per cluster; reviewed source annotations')
statuses=pd.read_csv(root/'logs/exit-status.tsv',sep='\t',header=None,names=['stage','exit'])
required={'prepare','seurat','scanpy','annotation_python','annotation_r'}
check('analysis and annotation processes exit zero',required<=set(statuses.stage) and (statuses[statuses.stage.isin(required)].groupby('stage').tail(1).exit==0).all(),statuses.to_dict('records'))
pd.DataFrame(checks).to_csv(root/'acceptance_checks.csv',index=False)
def table(df):
    result=['| '+' | '.join(df.columns)+' |','| '+' | '.join(['---']*len(df.columns))+' |']
    for _,r in df.iterrows():
        vals=[f'{x:.6f}' if isinstance(x,(float,np.floating)) else str(x).replace('|','/') for x in r]
        result.append('| '+' | '.join(vals)+' |')
    return '\n'.join(result)
failed=[x for x in checks if x['status']=='FAIL']
report=['# PBMC3k Seurat / Scanpy 实测验收','',f"生成：{datetime.datetime.now(datetime.timezone.utc).isoformat()}；`scripts/15_pbmc_report.py` 从实际 CSV、对象、图片与运行退出码生成。",'',f"**{'PASS' if not failed else 'FAIL'}：{len(checks)-len(failed)}/{len(checks)} 项验收通过。** 不以细胞数或 9/8 簇数作为通过门槛。",'','## 数据与校验','',f"同一输入目录 `{source['input_directory']}`；[10x PBMC3k 数据源]({source['source_url']})。复用既有下载，不重新下载或修改数据。归档 SHA-256：`{source['archive_sha256']}`。",'', '三个解压文件逐字节与归档成员一致，文件级 SHA-256 见 data_source.json。校验和用于本项目完整性记录，不是官方签名。原始 counts 是 10x 已过滤 UMI 矩阵，并非未过滤液滴矩阵。', '', '## QC 与实际统计','',table(summary),'',table(pd.DataFrame(qc_rows)),'', '先作基因至少 3 个细胞检出的预过滤、初始化至少 200 检出基因细胞，然后在过滤后的基因上计算 QC；两条路线均使用严格 200 < 检出基因数 < 2500、MT% < 5。原始全基因 QC 和过滤前/后逐细胞表同时保留。低基因、高基因和 MT 不通过数允许重叠，不能直接相加。跨工具 QC 指标差见 qc_cross_tool_differences.csv。','','## 预处理与参数','', '| 项目 | Seurat | Scanpy |','| --- | --- | --- |','| 归一化 | LogNormalize，10000，log1p | normalize_total=10000，log1p |',f"| HVG | vst，{hvg['seurat_hvgs']} 个 | seurat dispersion flavor，mean [.0125,3]、min_disp=.5，{hvg['scanpy_hvgs']} 个 |",'| 回归/缩放 | 无回归；HVG mean-center/unit variance，scale.max=10 | HVG 回归 total_counts/MT%；mean-center/unit variance，max_value=10 |','| PCA/图 | 50 PCs 计算，前10；Annoy Euclidean k20，SNN prune=1/15 | ARPACK 50 PCs，前40；Euclidean k10，UMAP fuzzy graph |','| 聚类 | Louvain algorithm1，resolution=.5，n.start10/n.iter10 | Leiden igraph，resolution1，n_iterations2，directed=False |','| UMAP | uwot cosine，30邻居，min_dist=.3 | umap-learn，min_dist=.5，spread1，使用已有邻居图 |','| 种子 | 42（PCA、聚类、UMAP） | 42（PCA、图、聚类、UMAP） |','', '这里 Scanpy flavor="seurat" 是 dispersion 方法，不等同于 Seurat 的 vst。按 gene ID 对齐的 HVG overlap 见 hvg_overlap.json。每条路线完整参数见 method.txt，运行版本见 sessionInfo.txt / python_runtime.txt 与 environment/ 的全量依赖。','','## Marker 与注释','', 'Seurat 在 RNA log-normalized data 上对每簇 vs rest 运行 Wilcoxon，min.pct=.25、logfc.threshold=.25，Bonferroni 校正；Scanpy 在完整基因的 log-normalized raw 上运行 Wilcoxon、tie_correct=True，BH 每簇校正，无同样的前置 min.pct/logFC 筛选。两种表的检验全集和校正不同，不直接比较显著 marker 数量。markers_all_tested.csv 保留各实现返回的检验，Seurat return.thresh=1 仍排除 p=1 的行；markers_positive.csv 是各路线的正向筛选表。', '',table(annotation[['route','cluster','cell_type','n_cells','confidence','supporting_genes']]),'', '注释是本次表达和差异 marker 支持的推定标签，不是独立真值。逐簇依据、限制、Top10 及每个证据基因的表达比例、均值、正向 marker logFC/padj 见 cell_type_annotations.csv / annotation_evidence.csv。T 亚型仅标为 naive-like/memory-like；小 DC 簇与 platelet-like 簇需谨慎；未做 doublet 检测、参考映射或蛋白验证。没有从教程簇编号复制标签。', '', '## 条形码对齐与一致性','',table(pd.DataFrame([comparison])),'', '源数据和两条路线的簇表、注释表均先检查重复条形码；发现重复会失败，不通过 drop_duplicates 静默修正。本次按完整 barcode 精确对齐，保留 -1 后缀；只有一个同源数据批次，无需去掉后缀。共有细胞才参与 ARI/NMI；NMI average_method="arithmetic"。ARI 可为负，不预设 0–1 的错误下界。唯一细胞清单保留，即使是空表。', '',table(cross.reset_index()),'', '完整列联表、按行比例、注释类型列联表、barcode_alignment.csv 和热图 cluster_crosstab.png 均保存。broad_type_agreement 仅是两个推定注释之间的一致性，不是注释准确率。', '', '## 实验验证与推测分开','',table(ex[['route','variant','variant_clusters','ARI_vs_route_baseline','NMI_vs_route_baseline','ARI_vs_other_route_baseline']]),'', '以上都是实际运行的单因素变体，改动定义见 controlled_experiments.csv。resolution/seed/optimizer 在同一图上比较；PC数和回归改动重建后续图。它们验证了各因素在本流程上的影响，不是对跨工具差异的完整因果分解。主结果保持原始参数，不选择最接近参考簇数的变体。', '', '已验证：两条路线读入相同 counts，QC 数值与细胞集合直接比较；共有细胞的划分差异由列联表量化。HVG 集合确实不同，但“改变 HVG 方法造成多少 ARI 差异”尚未单独做方法替换实验。Seurat SNN 与 Scanpy fuzzy graph、邻居算法和邻居数的差异、PCA 数值实现等是其余待检验原因。UMAP 在聚类后计算，外观差异不会造成上游簇标签变化，更不能证明细胞类型。', '', '参考教程中的 Seurat9/Scanpy8 仅用于诊断。实际簇数见 analysis_summary.csv，未用其作为验收阈值或调参目标。','','## 可修复问题与处理','', '初次验收发现一个 Scanpy canonical-marker 表达比例因浮点 mean 的累计误差略高于100%。已从 counts 的非零整数数量/簇细胞数重算所有比例，保留失败报告和修复日志，没有放宽验收范围。Seurat 点图透明背景造成黑底显示问题，已从保存对象重绘为白底；初版图片和执行脚本保留。Scanpy tied Wilcoxon 的除零警告、回归和稀疏缩放的性能/密集化警告均保留在日志，导出 marker scores/pvalues/logFC 有限；Seurat 缺少可选 presto 使用现有实现完成检验，未补装。', '', '## 对象、日志与复现','', '- Seurat 原始 counts：seurat/raw_counts.rds（含原始 ENSEMBL ID、symbols、barcodes）；分析对象 analysis.rds；含推定注释的对象 analysis_annotated.rds。','- Scanpy 原始 counts：scanpy/raw_counts.h5ad，X 为原始整数；分析和注释对象 analysis.h5ad / analysis_annotated.h5ad，layers["counts"] 保留整数，X/raw 为全基因 log-normalized 表达，PCA/图/UMAP 保留在对象中。','- 各路线 QC、UMAP、marker 点图以及各源数据表保存在对应子目录。注释后的 UMAP/点图另存。','- 运行日志、退出码、脚本副本、注释计划、版本和 SHA-256 manifest 均在本目录。对象均重新打开验证，整数 counts 与原始输入子集一致。','', '入口：`bash scripts/run_pbmc3k.sh`，使用已有隔离环境和数据，新建结果目录，避免覆盖已有结果。`results/pbmc3k/latest-run.txt` 指向成功运行。若未来聚类标签或注释证据变化，注释计划需要重新审阅，脚本会停止而非套用旧标签。','','## 验收明细','',table(pd.DataFrame(checks)),'','这是单个 PBMC 样本的探索性聚类和注释，不涉及多供体差异推断、批次整合或 nf-core。']
(root/'acceptance.md').write_text('\n'.join(report)+'\n')
print(summary.to_string(index=False));print(json.dumps(comparison,indent=2));print(ex.to_string(index=False));print(f"ACCEPTANCE {'PASS' if not failed else 'FAIL'} {len(checks)-len(failed)}/{len(checks)}")
if failed:raise SystemExit(1)
