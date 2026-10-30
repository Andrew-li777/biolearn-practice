#!/usr/bin/env python
"""Validate real outputs and generate pairwise comparisons and acceptance report."""
from pathlib import Path
import sys,json,itertools,hashlib,datetime
import numpy as np
import pandas as pd
from scipy.stats import spearmanr,pearsonr
from PIL import Image
outdir=Path(sys.argv[1]) if len(sys.argv)>1 else Path('results/bulk')
alpha=0.1
checks=[]
def check(name,condition,detail):
    checks.append({'check':name,'status':'PASS' if condition else 'FAIL','detail':str(detail)})
frames={}
summary=[]
counts=pd.read_csv(outdir/'airway_counts.csv',index_col=0)
meta=pd.read_csv(outdir/'airway_coldata.csv',index_col=0)
check('input sample alignment',list(counts.columns)==list(meta.index),f'{counts.shape[0]} genes x {counts.shape[1]} samples')
check('raw nonnegative integer counts',np.isfinite(counts.to_numpy()).all() and (counts>=0).all().all() and (counts==counts.round()).all().all(),'raw counts; no TPM/FPKM')
pairs=pd.crosstab(meta.cell,meta.dex)
pairs.to_csv(outdir/'sample_pairing.csv')
check('paired donor design',set(pairs.columns)=={'trt','untrt'} and (pairs==1).all().all(),pairs.to_dict())
for filename in ['r_design_matrix.csv','python_design_matrix.csv']:
    design=pd.read_csv(outdir/filename,index_col=0)
    check(f'full-rank design {filename}',np.linalg.matrix_rank(design)==design.shape[1] and list(design.index)==list(meta.index),f'{design.shape[0]} x {design.shape[1]}')
for name in ['deseq2','edger','pydeseq2']:
    f=pd.read_csv(outdir/f'{name}_results.csv').set_index('gene')
    check(f'{name} unique genes',f.index.is_unique and f.index.isin(counts.index).all(),len(f))
    check(f'{name} schema',{'log2FC','pvalue','padj','symbol','significant'}<=set(f.columns),list(f.columns))
    for column in ['pvalue','padj']:
        x=f[column].dropna()
        check(f'{name} {column} validity',np.isfinite(x).all() and x.between(0,1).all() and len(x)>0,f'{len(x)} valid; {f[column].isna().sum()} missing')
    check(f'{name} finite LFC',np.isfinite(f.log2FC).all(),len(f))
    sig=f.padj.notna() & (f.padj<alpha)
    check(f'{name} significance derived from padj',np.array_equal(sig.to_numpy(),f.significant.to_numpy()),f'FDR < {alpha}; no LFC threshold')
    filt=pd.read_csv(outdir/f'{name}_filter.csv').set_index('gene')['keep']
    check(f'{name} prefilter matches table',set(f.index)==set(filt.index[filt]) and list(filt.index)==list(counts.index),int(filt.sum()))
    if name in ['deseq2','pydeseq2']:
        expected=(counts>=10).sum(axis=1)>=3
        check(f'{name} prescribed prefilter',np.array_equal(filt.to_numpy(),expected.to_numpy()),'at least 3 samples with count >= 10')
    summary.append({'method':name,'input_genes':counts.shape[0],'prefilter_genes':len(f),'valid_pvalues':int(f.pvalue.notna().sum()),'valid_padj':int(f.padj.notna().sum()),'pvalue_missing':int(f.pvalue.isna().sum()),'padj_missing':int(f.padj.isna().sum()),'significant_fdr_0.1':int(sig.sum()),'up':int((sig & (f.log2FC>0)).sum()),'down':int((sig & (f.log2FC<0)).sum())})
    f.reset_index().loc[sig.to_numpy()].to_csv(outdir/f'{name}_significant.csv',index=False,na_rep='NA')
    frames[name]=f
summary=pd.DataFrame(summary)
summary.to_csv(outdir/'analysis_summary.csv',index=False)
check('DESeq2 / PyDESeq2 identical prefilter',set(frames['deseq2'].index)==set(frames['pydeseq2'].index),len(frames['deseq2']))
shr=pd.read_csv(outdir/'deseq2_apeglm.csv').set_index('gene')
main=frames['deseq2']
check('apeglm preserves testing results',shr.index.equals(main.index) and np.allclose(shr.pvalue,main.pvalue,equal_nan=True) and np.allclose(shr.padj,main.padj,equal_nan=True),'unshrunk testing and shrunk plotting kept separate')
rows=[]
for a,b in itertools.combinations(frames,2):
    fa,fb=frames[a],frames[b]
    sa=set(fa.index[fa.padj<alpha]); sb=set(fb.index[fb.padj<alpha])
    inter=sa&sb; union=sa|sb
    shared=fa.index.intersection(fb.index)
    x=fa.loc[shared,'log2FC'];y=fb.loc[shared,'log2FC']
    finite=np.isfinite(x)&np.isfinite(y)
    nonzero=finite & (x!=0) & (y!=0)
    hits=sorted(inter)
    hx=fa.loc[hits,'log2FC'];hy=fb.loc[hits,'log2FC']
    hvalid=np.isfinite(hx)&np.isfinite(hy)&(hx!=0)&(hy!=0)
    valid_padj=fa.loc[shared,'padj'].notna()&fb.loc[shared,'padj'].notna()
    common_tested=set(shared[valid_padj])
    csa=sa&common_tested;csb=sb&common_tested
    cinter=csa&csb;cunion=csa|csb
    row={'method_a':a,'method_b':b,'n_sig_a':len(sa),'n_sig_b':len(sb),'n_overlap':len(inter),'n_union':len(union),'overlap_fraction_a':len(inter)/len(sa) if sa else np.nan,'overlap_fraction_b':len(inter)/len(sb) if sb else np.nan,'jaccard':len(inter)/len(union) if union else np.nan,'prefilter_shared_genes':len(shared),'finite_lfc_pairs':int(finite.sum()),'spearman_log2FC_shared':float(spearmanr(x[finite],y[finite]).statistic),'pearson_log2FC_shared':float(pearsonr(x[finite],y[finite]).statistic),'direction_shared_n':int(nonzero.sum()),'direction_agreement_shared':float((np.sign(x[nonzero])==np.sign(y[nonzero])).mean()),'direction_overlap_n':int(hvalid.sum()),'direction_agreement_overlap':float((np.sign(hx[hvalid])==np.sign(hy[hvalid])).mean()) if hvalid.any() else np.nan,'both_valid_padj_genes':len(common_tested),'jaccard_both_valid_padj':len(cinter)/len(cunion) if cunion else np.nan}
    rows.append(row)
    aligned=pd.DataFrame({'gene':shared,'log2FC_a':x.to_numpy(),'log2FC_b':y.to_numpy(),'padj_a':fa.loc[shared,'padj'].to_numpy(),'padj_b':fb.loc[shared,'padj'].to_numpy()})
    aligned.to_csv(outdir/f'comparison_{a}_vs_{b}.csv',index=False,na_rep='NA')
    pd.DataFrame({'gene':sorted(inter)}).to_csv(outdir/f'overlap_{a}_vs_{b}.csv',index=False)
comparisons=pd.DataFrame(rows)
comparisons.to_csv(outdir/'comparisons.csv',index=False)
sets=[set(f.index[f.padj<alpha]) for f in frames.values()]
all_shared=set.intersection(*sets)
pd.DataFrame({'gene':sorted(all_shared)}).to_csv(outdir/'overlap_all_three.csv',index=False)
for filename in ['pca.png','sample_distance.png','ma_plot.png','ma_unshrunk.png','volcano.png','top30_heatmap.png']:
    with Image.open(outdir/filename) as im:
        im.verify()
    check(f'figure {filename}',(outdir/filename).stat().st_size>1000,'PNG decoded successfully')
distance=pd.read_csv(outdir/'sample_distance.csv',index_col=0)
check('sample distances',list(distance.index)==list(meta.index) and list(distance.columns)==list(meta.index) and np.allclose(distance,distance.T) and np.allclose(np.diag(distance),0),'symmetric, aligned, zero diagonal')
heat=pd.read_csv(outdir/'top30_vst_expression.csv',index_col=0)
check('heatmap source',len(heat)==30 and np.isfinite(heat).all().all() and list(heat.columns)==list(meta.index),'top30 VST matrix saved')
statuses=pd.read_csv(outdir/'logs/exit-status.tsv',sep='\t',header=None,names=['stage','exit'])
check('all analysis stages exited zero',{'deseq2','edger','pydeseq2'}<=set(statuses.stage) and (statuses.exit==0).all(),statuses.to_dict('records'))
top=main.sort_values('pvalue').head(20)
reference={'MAOA','DUSP1','SAMHD1','SPARCL1','SERPINA3','GPX3'}
hits=sorted(set(top.symbol.dropna())&reference)
diag={'reference_sig_count':4381,'actual_deseq2_sig_count':int(summary.loc[summary.method=='deseq2','significant_fdr_0.1'].iloc[0]),'actual_minus_reference':int(summary.loc[summary.method=='deseq2','significant_fdr_0.1'].iloc[0])-4381,'top20_reference_hits':hits,'policy':'diagnostic only; no pass/fail threshold and no parameter tuning'}
(outdir/'reference_diagnostics.json').write_text(json.dumps(diag,indent=2,ensure_ascii=False)+'\n')
pd.DataFrame(checks).to_csv(outdir/'acceptance_checks.csv',index=False)
def table(df,columns=None):
    if columns:df=df[columns]
    lines=['| '+' | '.join(df.columns)+' |','| '+' | '.join(['---']*len(df.columns))+' |']
    for _,row in df.iterrows():
        def fmt(v):
            if isinstance(v,(float,np.floating)):return f'{v:.6f}' if np.isfinite(v) else 'NA'
            return str(v).replace('|','/')
        lines.append('| '+' | '.join(fmt(v) for v in row)+' |')
    return '\n'.join(lines)
failed=[c for c in checks if c['status']=='FAIL']
report=['# airway bulk RNA-seq 实测验收报告','',f"生成时间：{datetime.datetime.now(datetime.timezone.utc).isoformat()}。本报告由 `scripts/04_bulk_report.py` 读取本目录的实际 CSV、图片和退出码生成。",'',f"状态：{'PASS' if not failed else 'FAIL'}；{len(checks)-len(failed)}/{len(checks)} 项结构和运行验收通过。参考数字不参与通过/失败判定。",'','## 实际结果','',table(summary),'',f'三套方法共同显著基因：{len(all_shared)}；基因列表见 `overlap_all_three.csv`。','','## 成对比较','',table(comparisons,['method_a','method_b','n_overlap','overlap_fraction_a','overlap_fraction_b','jaccard','prefilter_shared_genes','spearman_log2FC_shared','pearson_log2FC_shared','direction_agreement_overlap']),'','显著性统一定义为非缺失 padj < 0.1，不叠加 |log2FC| 阈值。重合率分别为交集/各方法显著集大小；Jaccard 为交集/并集，采用各方法完整显著集，未把另一方法预过滤掉的基因静默丢弃。相关性取两方法预过滤基因交集中的有限 log2FC，不使用 apeglm 收缩值；edgeR 默认 prior.count=0.125 带轻度收缩。方向一致性取共同显著基因中有限且两边非零的 log2FC，分母见 comparisons.csv；该文件另含共有基因方向一致性和两边 padj 有效的子集 Jaccard，后者沿用各方法原有 padj，不重新做 BH。','','## 过滤与方法','', '| 方法 | 预过滤 | 归一化 | 检验 / 多重校正 |','| --- | --- | --- | --- |','| DESeq2 | 至少 3 样本 count >= 10 | median-of-ratios | ~ cell + dex，trt vs untrt；Wald，parametric dispersion，Cook 默认过滤，BH + independent filtering(alpha=0.1) |','| PyDESeq2 | 同 DESeq2 | median-of-ratios | 相同设计和对比；Python Wald 实现，parametric fit，Cook 过滤，BH + independent filtering(alpha=0.1) |','| edgeR | filterByExpr(design)，参数见 edger_method.txt | TMM；过滤后重算库大小 | 相同设计，dextrt；robust dispersion / QL fit，QL F 检验；BH over prefiltered genes，无 DESeq2-style independent filtering |','', '三个 *_filter.csv 记录每个输入基因是否保留；方法、实际拟合类型、缺失 pvalue/padj 和库归一化信息分别见 *_method.txt、analysis_summary.csv、deseq2_results_metadata.txt 及 *_normalization/size_factors.csv。由于过滤、归一化、离散度估计、检验和独立过滤不同，显著基因数量和边缘基因可能不同；结果差异本身不是失败。','','## 图与源数据','', '- `pca.png`：design-aware VST，默认 top 500 变异基因 PCA；坐标和解释方差见 pca_scores.csv / pca_variance.csv。','- `sample_distance.png`：全部预过滤基因 VST 的样本欧氏距离，直接按该距离聚类；源矩阵 sample_distance.csv。','- `ma_plot.png`：apeglm 收缩 LFC，显著性保留主结果 alpha=0.1；另有 ma_unshrunk.png。','- `volcano.png`：未收缩 log2FC vs -log10(raw p)，颜色仅依据 padj<0.1；p=0 下限保护。','- `top30_heatmap.png`：padj 最小的 30 基因，VST 后按行 z-score；同时显示 symbol 与 ENSEMBL ID，避免重复 symbol；源数据 top30_vst_expression.csv / top30_heatmap_genes.csv。','','## 参考数字诊断','',f"DESeq2 实际显著数为 {diag['actual_deseq2_sig_count']}；与参考材料中的 4,381 相差 {diag['actual_minus_reference']}。原始 airway 计数、预过滤、软件版本与参考工作流的量化及过滤不同，不能直接逐位比较。没有为匹配参考数字改变参数。",'',f"实际 raw-p Top20 命中参考基因 {len(hits)}/6：{', '.join(hits) or '无'}。这是诊断，不作为验收门槛。完整 Top20 见 deseq2_top20.csv。",'','## 软件、日志与复现','', 'R 运行时及包版本：sessionInfo_deseq2.txt、sessionInfo_edger.txt、r_installed_packages.csv；Python：python_runtime.txt、python_distribution_versions.json；两环境全部 Conda 依赖和 build 见 environment/。每一步完整日志和退出码见 logs/。脚本副本和 SHA-256 manifest 记录本次实际执行代码与产物。','','从仓库根目录运行 `bash scripts/run_bulk.sh`，创建新的时间戳目录，保留已有结果。`results/bulk/latest-run.txt` 指向最近一次完整运行；脚本失败会停止，不生成伪成功报告。','','## 验收明细','',table(pd.DataFrame(checks)),'','本阶段处理已有计数矩阵，不含原始 reads 比对、GO 富集或 nf-core 测试。']
(outdir/'acceptance.md').write_text('\n'.join(report)+'\n')
print(summary.to_string(index=False))
print(comparisons.to_string(index=False))
print(f"ACCEPTANCE {'PASS' if not failed else 'FAIL'}: {len(checks)-len(failed)}/{len(checks)} checks; report={outdir/'acceptance.md'}")
if failed:raise SystemExit(1)
