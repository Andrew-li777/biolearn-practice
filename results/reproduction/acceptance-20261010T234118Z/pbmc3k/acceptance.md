# PBMC3k Seurat / Scanpy 实测验收

生成：2026-10-10T23:44:17.347933+00:00；`scripts/15_pbmc_report.py` 从实际 CSV、对象、图片与运行退出码生成。

**PASS：83/83 项验收通过。** 不以细胞数或 9/8 簇数作为通过门槛。

## 数据与校验

同一输入目录 `data/pbmc3k/filtered_gene_bc_matrices/hg19`；[10x PBMC3k 数据源](https://cf.10xgenomics.com/samples/cell/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz)。复用既有下载，不重新下载或修改数据。归档 SHA-256：`847d6ebd9a1ec9a768f2be7e40ca42cbfe75ebeb6d76a4c24167041699dc28b5`。

三个解压文件逐字节与归档成员一致，文件级 SHA-256 见 data_source.json。校验和用于本项目完整性记录，不是官方签名。原始 counts 是 10x 已过滤 UMI 矩阵，并非未过滤液滴矩阵。

## QC 与实际统计

| route | raw_cells | before_final_QC_cells | QC_pass_cells | rejected_cells | fail_low_genes | fail_high_genes | fail_mt | clusters | marker_rows_returned | positive_marker_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| seurat | 2700 | 2700 | 2638 | 62 | 0 | 5 | 57 | 9 | 6964 | 2187 |
| scanpy | 2700 | 2700 | 2638 | 62 | 0 | 5 | 57 | 9 | 123426 | 10924 |

| route | stage | cells | median_genes | median_UMI | median_mt_pct | max_genes | max_mt_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| seurat | raw | 2700 | 817.000000 | 2197.000000 | 2.029639 | 3422 | 22.569028 |
| seurat | before_final_qc | 2700 | 816.000000 | 2196.000000 | 2.030801 | 3400 | 22.569028 |
| seurat | after_final_qc | 2638 | 819.000000 | 2213.000000 | 2.010702 | 2413 | 4.993835 |
| scanpy | raw | 2700 | 817.000000 | 2197.000000 | 2.029639 | 3422 | 22.569027 |
| scanpy | before_final_qc | 2700 | 816.000000 | 2196.000000 | 2.030800 | 3400 | 22.569027 |
| scanpy | after_final_qc | 2638 | 819.000000 | 2213.000000 | 2.010702 | 2413 | 4.993835 |

先作基因至少 3 个细胞检出的预过滤、初始化至少 200 检出基因细胞，然后在过滤后的基因上计算 QC；两条路线均使用严格 200 < 检出基因数 < 2500、MT% < 5。原始全基因 QC 和过滤前/后逐细胞表同时保留。低基因、高基因和 MT 不通过数允许重叠，不能直接相加。跨工具 QC 指标差见 qc_cross_tool_differences.csv。

## 预处理与参数

| 项目 | Seurat | Scanpy |
| --- | --- | --- |
| 归一化 | LogNormalize，10000，log1p | normalize_total=10000，log1p |
| HVG | vst，2000 个 | seurat dispersion flavor，mean [.0125,3]、min_disp=.5，1838 个 |
| 回归/缩放 | 无回归；HVG mean-center/unit variance，scale.max=10 | HVG 回归 total_counts/MT%；mean-center/unit variance，max_value=10 |
| PCA/图 | 50 PCs 计算，前10；Annoy Euclidean k20，SNN prune=1/15 | ARPACK 50 PCs，前40；Euclidean k10，UMAP fuzzy graph |
| 聚类 | Louvain algorithm1，resolution=.5，n.start10/n.iter10 | Leiden igraph，resolution1，n_iterations2，directed=False |
| UMAP | uwot cosine，30邻居，min_dist=.3 | umap-learn，min_dist=.5，spread1，使用已有邻居图 |
| 种子 | 42（PCA、聚类、UMAP） | 42（PCA、图、聚类、UMAP） |

这里 Scanpy flavor="seurat" 是 dispersion 方法，不等同于 Seurat 的 vst。按 gene ID 对齐的 HVG overlap 见 hvg_overlap.json。每条路线完整参数见 method.txt，运行版本见 sessionInfo.txt / python_runtime.txt 与 environment/ 的全量依赖。

## Marker 与注释

Seurat 在 RNA log-normalized data 上对每簇 vs rest 运行 Wilcoxon，min.pct=.25、logfc.threshold=.25，Bonferroni 校正；Scanpy 在完整基因的 log-normalized raw 上运行 Wilcoxon、tie_correct=True，BH 每簇校正，无同样的前置 min.pct/logFC 筛选。两种表的检验全集和校正不同，不直接比较显著 marker 数量。markers_all_tested.csv 保留各实现返回的检验，Seurat return.thresh=1 仍排除 p=1 的行；markers_positive.csv 是各路线的正向筛选表。

| route | cluster | cell_type | n_cells | confidence | supporting_genes |
| --- | --- | --- | --- | --- | --- |
| seurat | 0 | Naive-like CD4 T | 705 | moderate | CD3D;CD3E;IL7R;CCR7 |
| seurat | 1 | CD14+ monocytes | 481 | high marker support | CD14;LYZ;S100A8;LST1 |
| seurat | 2 | Memory-like CD4 T | 472 | moderate | CD3D;CD3E;IL7R;S100A4 |
| seurat | 3 | B cells | 344 | high marker support | MS4A1;CD79A |
| seurat | 4 | Cytotoxic CD8 T | 274 | moderate-high marker support | CD3D;CD3E;CD8A;CD8B;CCL5;NKG7 |
| seurat | 5 | FCGR3A+ monocytes | 162 | high marker support | FCGR3A;MS4A7;LST1;LYZ |
| seurat | 6 | NK cells | 155 | high broad-type marker support | GNLY;NKG7;PRF1 |
| seurat | 7 | Dendritic-like cells | 32 | moderate | FCER1A;CST3 |
| seurat | 8 | Platelet-like cells | 13 | strong markers, small cluster | PPBP;PF4 |
| scanpy | 0 | Memory-like CD4 T | 497 | moderate | CD3D;CD3E;IL7R;S100A4 |
| scanpy | 1 | Naive-like CD4 T | 656 | moderate | CD3D;CD3E;IL7R;CCR7 |
| scanpy | 2 | B cells | 341 | high marker support | MS4A1;CD79A |
| scanpy | 3 | FCGR3A+ monocytes | 171 | high marker support | FCGR3A;MS4A7;LST1;LYZ |
| scanpy | 4 | CD14+ monocytes | 463 | high marker support | CD14;LYZ;S100A8;LST1 |
| scanpy | 5 | NK cells | 152 | high broad-type marker support | GNLY;NKG7;PRF1 |
| scanpy | 6 | Cytotoxic CD8 T | 307 | moderate-high marker support | CD3D;CD3E;CD8A;CD8B;CCL5;NKG7 |
| scanpy | 7 | Dendritic-like cells | 38 | moderate | FCER1A;CST3 |
| scanpy | 8 | Platelet-like cells | 13 | strong markers, small cluster | PPBP;PF4 |

注释是本次表达和差异 marker 支持的推定标签，不是独立真值。逐簇依据、限制、Top10 及每个证据基因的表达比例、均值、正向 marker logFC/padj 见 cell_type_annotations.csv / annotation_evidence.csv。T 亚型仅标为 naive-like/memory-like；小 DC 簇与 platelet-like 簇需谨慎；未做 doublet 检测、参考映射或蛋白验证。没有从教程簇编号复制标签。

## 条形码对齐与一致性

| n_a | n_b | shared | only_a | only_b | clusters_a | clusters_b | ARI | NMI_arithmetic | broad_type_agreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2638.000000 | 2638.000000 | 2638.000000 | 0.000000 | 0.000000 | 9.000000 | 9.000000 | 0.627931 | 0.754505 | 0.949962 |

源数据和两条路线的簇表、注释表均先检查重复条形码；发现重复会失败，不通过 drop_duplicates 静默修正。本次按完整 barcode 精确对齐，保留 -1 后缀；只有一个同源数据批次，无需去掉后缀。共有细胞才参与 ARI/NMI；NMI average_method="arithmetic"。ARI 可为负，不预设 0–1 的错误下界。唯一细胞清单保留，即使是空表。

| seurat_cluster | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 198 | 490 | 0 | 0 | 0 | 0 | 17 | 0 | 0 |
| 1 | 1 | 0 | 0 | 19 | 455 | 0 | 0 | 6 | 0 |
| 2 | 283 | 155 | 0 | 0 | 0 | 0 | 34 | 0 | 0 |
| 3 | 1 | 3 | 340 | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | 14 | 6 | 0 | 1 | 0 | 8 | 245 | 0 | 0 |
| 5 | 0 | 2 | 1 | 151 | 8 | 0 | 0 | 0 | 0 |
| 6 | 0 | 0 | 0 | 0 | 0 | 144 | 11 | 0 | 0 |
| 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 32 | 0 |
| 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 13 |

完整列联表、按行比例、注释类型列联表、barcode_alignment.csv 和热图 cluster_crosstab.png 均保存。broad_type_agreement 仅是两个推定注释之间的一致性，不是注释准确率。

## 实验验证与推测分开

| route | variant | variant_clusters | ARI_vs_route_baseline | NMI_vs_route_baseline | ARI_vs_other_route_baseline |
| --- | --- | --- | --- | --- | --- |
| scanpy | louvain_same_graph | 8 | 0.636202 | 0.794551 | 0.621528 |
| scanpy | no_regression | 8 | 0.610619 | 0.745941 | 0.665121 |
| scanpy | pc10 | 14 | 0.495671 | 0.688884 | 0.509700 |
| scanpy | resolution_05 | 6 | 0.618129 | 0.802185 | 0.603260 |
| scanpy | seed_7 | 8 | 0.704651 | 0.874445 | 0.662048 |
| seurat | resolution_1 | 11 | 0.790078 | 0.884486 | 0.533246 |

以上都是实际运行的单因素变体，改动定义见 controlled_experiments.csv。resolution/seed/optimizer 在同一图上比较；PC数和回归改动重建后续图。它们验证了各因素在本流程上的影响，不是对跨工具差异的完整因果分解。主结果保持原始参数，不选择最接近参考簇数的变体。

已验证：两条路线读入相同 counts，QC 数值与细胞集合直接比较；共有细胞的划分差异由列联表量化。HVG 集合确实不同，但“改变 HVG 方法造成多少 ARI 差异”尚未单独做方法替换实验。Seurat SNN 与 Scanpy fuzzy graph、邻居算法和邻居数的差异、PCA 数值实现等是其余待检验原因。UMAP 在聚类后计算，外观差异不会造成上游簇标签变化，更不能证明细胞类型。

参考教程中的 Seurat9/Scanpy8 仅用于诊断。实际簇数见 analysis_summary.csv，未用其作为验收阈值或调参目标。

## 可修复问题与处理

初次验收发现一个 Scanpy canonical-marker 表达比例因浮点 mean 的累计误差略高于100%。已从 counts 的非零整数数量/簇细胞数重算所有比例，保留失败报告和修复日志，没有放宽验收范围。Seurat 点图透明背景造成黑底显示问题，已从保存对象重绘为白底；初版图片和执行脚本保留。Scanpy tied Wilcoxon 的除零警告、回归和稀疏缩放的性能/密集化警告均保留在日志，导出 marker scores/pvalues/logFC 有限；Seurat 缺少可选 presto 使用现有实现完成检验，未补装。

## 对象、日志与复现

- Seurat 原始 counts：seurat/raw_counts.rds（含原始 ENSEMBL ID、symbols、barcodes）；分析对象 analysis.rds；含推定注释的对象 analysis_annotated.rds。
- Scanpy 原始 counts：scanpy/raw_counts.h5ad，X 为原始整数；分析和注释对象 analysis.h5ad / analysis_annotated.h5ad，layers["counts"] 保留整数，X/raw 为全基因 log-normalized 表达，PCA/图/UMAP 保留在对象中。
- 各路线 QC、UMAP、marker 点图以及各源数据表保存在对应子目录。注释后的 UMAP/点图另存。
- 运行日志、退出码、脚本副本、注释计划、版本和 SHA-256 manifest 均在本目录。对象均重新打开验证，整数 counts 与原始输入子集一致。

入口：`bash scripts/run_pbmc3k.sh`，使用已有隔离环境和数据，新建结果目录，避免覆盖已有结果。`results/pbmc3k/latest-run.txt` 指向成功运行。若未来聚类标签或注释证据变化，注释计划需要重新审阅，脚本会停止而非套用旧标签。

## 验收明细

| check | status | detail |
| --- | --- | --- |
| no duplicate source barcodes | PASS | 2700 source cells |
| raw H5AD counts equal source matrix | PASS | (2700, 32738) |
| raw H5AD source barcodes preserved | PASS | exact IDs, preserve -1 suffix |
| integer raw counts | PASS | not normalized counts |
| unique barcodes: seurat/clusters.csv | PASS | 0 |
| unique barcodes: seurat/cell_labels.csv | PASS | 0 |
| seurat annotations cover observed clusters | PASS | 9 |
| seurat cell annotations align | PASS | 2638 |
| seurat QC mask matches fixed thresholds | PASS | strict 200 < genes < 2500 and MT % < 5 |
| seurat postQC membership from real QC mask | PASS | 2638 |
| seurat source membership | PASS | 2638 |
| seurat marker table covers clusters | PASS | 6964 |
| seurat unique cluster/gene marker rows | PASS | 6964 |
| seurat valid marker probabilities | PASS | finite in [0,1] |
| seurat marker finite logFC | PASS | 6964 |
| seurat positive marker filter | PASS | 2187 |
| seurat UMAP aligned and finite | PASS | (2638, 2) |
| seurat raw and analysis object reopened | PASS | PASS raw RDS reopened and equals source counts
PASS analysis RDS reopened; counts equal source subset; UMAP finite
PASS no duplicate source or postQC barcodes |
| seurat object raw_counts.rds | PASS | 5428255 |
| seurat object analysis.rds | PASS | 19683436 |
| seurat object analysis_annotated.rds | PASS | 19688646 |
| seurat figure qc_violin.png | PASS | decoded PNG |
| seurat figure qc_scatter.png | PASS | decoded PNG |
| seurat figure umap_clusters.png | PASS | decoded PNG |
| seurat figure umap_cell_types.png | PASS | decoded PNG |
| seurat figure marker_dotplot.png | PASS | decoded PNG |
| seurat figure marker_dotplot_cell_types.png | PASS | decoded PNG |
| unique barcodes: scanpy/clusters.csv | PASS | 0 |
| unique barcodes: scanpy/cell_labels.csv | PASS | 0 |
| scanpy annotations cover observed clusters | PASS | 9 |
| scanpy cell annotations align | PASS | 2638 |
| scanpy QC mask matches fixed thresholds | PASS | strict 200 < genes < 2500 and MT % < 5 |
| scanpy postQC membership from real QC mask | PASS | 2638 |
| scanpy source membership | PASS | 2638 |
| scanpy marker table covers clusters | PASS | 123426 |
| scanpy unique cluster/gene marker rows | PASS | 123426 |
| scanpy valid marker probabilities | PASS | finite in [0,1] |
| scanpy marker finite logFC | PASS | 123426 |
| scanpy positive marker filter | PASS | 10924 |
| scanpy UMAP aligned and finite | PASS | (2638, 2) |
| scanpy raw and analysis object reopened | PASS | PASS raw H5AD reopened; counts equal input
PASS analysis H5AD reopened; counts layer equals input subset; UMAP finite
PASS no duplicate source or postQC barcodes |
| scanpy object raw_counts.h5ad | PASS | 7550181 |
| scanpy object analysis.h5ad | PASS | 26499254 |
| scanpy object analysis_annotated.h5ad | PASS | 26522279 |
| scanpy figure qc_violin.png | PASS | decoded PNG |
| scanpy figure qc_scatter.png | PASS | decoded PNG |
| scanpy figure umap_clusters.png | PASS | decoded PNG |
| scanpy figure umap_cell_types.png | PASS | decoded PNG |
| scanpy figure marker_dotplot.png | PASS | decoded PNG |
| scanpy figure marker_dotplot_cell_types.png | PASS | decoded PNG |
| unique barcodes: seurat/cell_labels.csv | PASS | 0 |
| unique barcodes: scanpy/cell_labels.csv | PASS | 0 |
| contingency conserves shared cells | PASS | 2638 |
| metric bounds | PASS | {'n_a': 2638, 'n_b': 2638, 'shared': 2638, 'only_a': 0, 'only_b': 0, 'clusters_a': 9, 'clusters_b': 9, 'ARI': 0.6279310734626542, 'NMI_arithmetic': 0.7545047834392827, 'broad_type_agreement': 0.9499620924943138} |
| two routes QC metrics equal on matched cells | PASS | max differences={'genes_difference': 0.0, 'UMI_difference': 0.0, 'MT_pct_difference': 1.6486485989730681e-06} |
| analysis.h5ad labels match exported table | PASS | (2638, 13714) |
| analysis.h5ad count layer equals raw source subset | PASS | integer counts preserved |
| analysis.h5ad marker expression is log-normalized | PASS | full-gene X and raw; not scaled residuals |
| analysis_annotated.h5ad labels match exported table | PASS | (2638, 13714) |
| analysis_annotated.h5ad count layer equals raw source subset | PASS | integer counts preserved |
| analysis_annotated.h5ad marker expression is log-normalized | PASS | full-gene X and raw; not scaled residuals |
| annotated H5AD cell types match table | PASS | 2638 |
| annotated RDS validated | PASS | R process reopened annotated object and checked labels/counts |
| unique barcodes: scanpy/experiment_louvain_same_graph.csv | PASS | 0 |
| experiment same cell universe louvain_same_graph | PASS | 2638 |
| unique barcodes: scanpy/experiment_no_regression.csv | PASS | 0 |
| experiment same cell universe no_regression | PASS | 2638 |
| unique barcodes: scanpy/experiment_pc10.csv | PASS | 0 |
| experiment same cell universe pc10 | PASS | 2638 |
| unique barcodes: scanpy/experiment_resolution_05.csv | PASS | 0 |
| experiment same cell universe resolution_05 | PASS | 2638 |
| unique barcodes: scanpy/experiment_seed_7.csv | PASS | 0 |
| experiment same cell universe seed_7 | PASS | 2638 |
| unique barcodes: seurat/experiment_resolution_1.csv | PASS | 0 |
| Seurat resolution experiment same cells | PASS | 2638 |
| annotations have recorded expression evidence | PASS | 62 |
| Scanpy expression count schema | PASS | ['cluster', 'gene', 'mean_log1p', 'pct_expressing', 'n_cells', 'expressing_cell_count'] |
| Scanpy expression counts integer and bounded | PASS | 207 |
| Scanpy expression proportions from integer counts | PASS | 207 |
| annotation evidence unique full key | PASS | 62 |
| annotation evidence missing tests explicitly unsupported | PASS | 3 |
| annotation signature supported | PASS | at least two positive canonical markers per cluster; reviewed source annotations |
| analysis and annotation processes exit zero | PASS | [{'stage': 'prepare', 'exit': 0}, {'stage': 'seurat', 'exit': 0}, {'stage': 'scanpy', 'exit': 0}, {'stage': 'annotation_python', 'exit': 0}, {'stage': 'annotation_r', 'exit': 0}] |

这是单个 PBMC 样本的探索性聚类和注释，不涉及多供体差异推断、批次整合或 nf-core。
