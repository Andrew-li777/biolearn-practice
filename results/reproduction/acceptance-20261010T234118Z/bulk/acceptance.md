# airway bulk RNA-seq 实测验收报告

生成时间：2026-10-10T23:46:47.069921+00:00。本报告由 `scripts/04_bulk_report.py` 读取本目录的实际 CSV、图片和退出码生成。

状态：PASS；39/39 项结构和运行验收通过。参考数字不参与通过/失败判定。

## 实际结果

| method | input_genes | prefilter_genes | valid_pvalues | valid_padj | pvalue_missing | padj_missing | significant_fdr_0.1 | up | down |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deseq2 | 63677 | 16596 | 16596 | 16596 | 0 | 0 | 4916 | 2618 | 2298 |
| edger | 63677 | 16860 | 16860 | 16860 | 0 | 0 | 6550 | 3302 | 3248 |
| pydeseq2 | 63677 | 16596 | 16596 | 16596 | 0 | 0 | 4685 | 2502 | 2183 |

三套方法共同显著基因：4611；基因列表见 `overlap_all_three.csv`。

## 成对比较

| method_a | method_b | n_overlap | overlap_fraction_a | overlap_fraction_b | jaccard | prefilter_shared_genes | spearman_log2FC_shared | pearson_log2FC_shared | direction_agreement_overlap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deseq2 | edger | 4879 | 0.992474 | 0.744885 | 0.740701 | 16493 | 0.996428 | 0.996643 | 1.000000 |
| deseq2 | pydeseq2 | 4641 | 0.944060 | 0.990608 | 0.935685 | 16596 | 0.999994 | 0.999986 | 1.000000 |
| edger | pydeseq2 | 4635 | 0.707634 | 0.989328 | 0.702273 | 16493 | 0.996532 | 0.996871 | 1.000000 |

显著性统一定义为非缺失 padj < 0.1，不叠加 |log2FC| 阈值。重合率分别为交集/各方法显著集大小；Jaccard 为交集/并集，采用各方法完整显著集，未把另一方法预过滤掉的基因静默丢弃。相关性取两方法预过滤基因交集中的有限 log2FC，不使用 apeglm 收缩值；edgeR 默认 prior.count=0.125 带轻度收缩。方向一致性取共同显著基因中有限且两边非零的 log2FC，分母见 comparisons.csv；该文件另含共有基因方向一致性和两边 padj 有效的子集 Jaccard，后者沿用各方法原有 padj，不重新做 BH。

## 过滤与方法

| 方法 | 预过滤 | 归一化 | 检验 / 多重校正 |
| --- | --- | --- | --- |
| DESeq2 | 至少 3 样本 count >= 10 | median-of-ratios | ~ cell + dex，trt vs untrt；Wald，parametric dispersion，Cook 默认过滤，BH + independent filtering(alpha=0.1) |
| PyDESeq2 | 同 DESeq2 | median-of-ratios | 相同设计和对比；Python Wald 实现，parametric fit，Cook 过滤，BH + independent filtering(alpha=0.1) |
| edgeR | filterByExpr(design)，参数见 edger_method.txt | TMM；过滤后重算库大小 | 相同设计，dextrt；robust dispersion / QL fit，QL F 检验；BH over prefiltered genes，无 DESeq2-style independent filtering |

三个 *_filter.csv 记录每个输入基因是否保留；方法、实际拟合类型、缺失 pvalue/padj 和库归一化信息分别见 *_method.txt、analysis_summary.csv、deseq2_results_metadata.txt 及 *_normalization/size_factors.csv。由于过滤、归一化、离散度估计、检验和独立过滤不同，显著基因数量和边缘基因可能不同；结果差异本身不是失败。

## 图与源数据

- `pca.png`：design-aware VST，默认 top 500 变异基因 PCA；坐标和解释方差见 pca_scores.csv / pca_variance.csv。
- `sample_distance.png`：全部预过滤基因 VST 的样本欧氏距离，直接按该距离聚类；源矩阵 sample_distance.csv。
- `ma_plot.png`：apeglm 收缩 LFC，显著性保留主结果 alpha=0.1；另有 ma_unshrunk.png。
- `volcano.png`：未收缩 log2FC vs -log10(raw p)，颜色仅依据 padj<0.1；p=0 下限保护。
- `top30_heatmap.png`：padj 最小的 30 基因，VST 后按行 z-score；同时显示 symbol 与 ENSEMBL ID，避免重复 symbol；源数据 top30_vst_expression.csv / top30_heatmap_genes.csv。

## 参考数字诊断

DESeq2 实际显著数为 4916；与参考材料中的 4,381 相差 535。原始 airway 计数、预过滤、软件版本与参考工作流的量化及过滤不同，不能直接逐位比较。没有为匹配参考数字改变参数。

实际 raw-p Top20 命中参考基因 5/6：DUSP1, GPX3, MAOA, SAMHD1, SPARCL1。这是诊断，不作为验收门槛。完整 Top20 见 deseq2_top20.csv。

## 软件、日志与复现

R 运行时及包版本：sessionInfo_deseq2.txt、sessionInfo_edger.txt、r_installed_packages.csv；Python：python_runtime.txt、python_distribution_versions.json；两环境全部 Conda 依赖和 build 见 environment/。每一步完整日志和退出码见 logs/。脚本副本和 SHA-256 manifest 记录本次实际执行代码与产物。

从仓库根目录运行 `bash scripts/run_bulk.sh`，创建新的时间戳目录，保留已有结果。`results/bulk/latest-run.txt` 指向最近一次完整运行；脚本失败会停止，不生成伪成功报告。

## 验收明细

| check | status | detail |
| --- | --- | --- |
| input sample alignment | PASS | 63677 genes x 8 samples |
| raw nonnegative integer counts | PASS | raw counts; no TPM/FPKM |
| paired donor design | PASS | {'trt': {'N052611': 1, 'N061011': 1, 'N080611': 1, 'N61311': 1}, 'untrt': {'N052611': 1, 'N061011': 1, 'N080611': 1, 'N61311': 1}} |
| full-rank design r_design_matrix.csv | PASS | 8 x 5 |
| full-rank design python_design_matrix.csv | PASS | 8 x 5 |
| deseq2 unique genes | PASS | 16596 |
| deseq2 schema | PASS | ['symbol', 'baseMean', 'log2FC', 'lfcSE', 'stat', 'pvalue', 'padj', 'significant'] |
| deseq2 pvalue validity | PASS | 16596 valid; 0 missing |
| deseq2 padj validity | PASS | 16596 valid; 0 missing |
| deseq2 finite LFC | PASS | 16596 |
| deseq2 significance derived from padj | PASS | FDR < 0.1; no LFC threshold |
| deseq2 prefilter matches table | PASS | 16596 |
| deseq2 prescribed prefilter | PASS | at least 3 samples with count >= 10 |
| edger unique genes | PASS | 16860 |
| edger schema | PASS | ['symbol', 'log2FC', 'logCPM', 'F', 'pvalue', 'padj', 'significant'] |
| edger pvalue validity | PASS | 16860 valid; 0 missing |
| edger padj validity | PASS | 16860 valid; 0 missing |
| edger finite LFC | PASS | 16860 |
| edger significance derived from padj | PASS | FDR < 0.1; no LFC threshold |
| edger prefilter matches table | PASS | 16860 |
| pydeseq2 unique genes | PASS | 16596 |
| pydeseq2 schema | PASS | ['symbol', 'baseMean', 'log2FC', 'lfcSE', 'stat', 'pvalue', 'padj', 'significant'] |
| pydeseq2 pvalue validity | PASS | 16596 valid; 0 missing |
| pydeseq2 padj validity | PASS | 16596 valid; 0 missing |
| pydeseq2 finite LFC | PASS | 16596 |
| pydeseq2 significance derived from padj | PASS | FDR < 0.1; no LFC threshold |
| pydeseq2 prefilter matches table | PASS | 16596 |
| pydeseq2 prescribed prefilter | PASS | at least 3 samples with count >= 10 |
| DESeq2 / PyDESeq2 identical prefilter | PASS | 16596 |
| apeglm preserves testing results | PASS | unshrunk testing and shrunk plotting kept separate |
| figure pca.png | PASS | PNG decoded successfully |
| figure sample_distance.png | PASS | PNG decoded successfully |
| figure ma_plot.png | PASS | PNG decoded successfully |
| figure ma_unshrunk.png | PASS | PNG decoded successfully |
| figure volcano.png | PASS | PNG decoded successfully |
| figure top30_heatmap.png | PASS | PNG decoded successfully |
| sample distances | PASS | symmetric, aligned, zero diagonal |
| heatmap source | PASS | top30 VST matrix saved |
| all analysis stages exited zero | PASS | [{'stage': 'deseq2', 'exit': 0}, {'stage': 'edger', 'exit': 0}, {'stage': 'pydeseq2', 'exit': 0}] |

本阶段处理已有计数矩阵，不含原始 reads 比对、GO 富集或 nf-core 测试。
