# airway bulk 分析方法与参考代码修正

本阶段已在本机实际执行，入口 `bash scripts/run_bulk.sh`；结果位于 `results/bulk/latest-run.txt` 指定目录。统计验收来自该目录的 `acceptance.md` 和 `acceptance_checks.csv`，不从参考数字构造结果。

## 固定分析方案

输入是已安装 airway 1.26.0 中的原始整数计数，不下载 SRA、不比对、不做 TPM/FPKM 转换。每个供体对应 trt 和 untrt 各一个样本，设计 `~ cell + dex`，untrt 为参照，全部工具比较 trt vs untrt。显著性统一为 padj < 0.1，不另加 LFC 阈值。

| 项目 | DESeq2 | edgeR | PyDESeq2 |
| --- | --- | --- | --- |
| 预过滤 | 至少 3 个样本 count >= 10 | filterByExpr，使用完整 design；min.count=10、min.total.count=15、large.n=10、min.prop=0.7 | 同 DESeq2 |
| 归一化 | median-of-ratios | TMM，预过滤后重新计算 library size | median-of-ratios |
| 拟合 | parametric dispersion trend + MAP；betaPrior=FALSE | estimateDisp / glmQLFit 均 robust=TRUE；edgeR 4.4 的 legacy=FALSE 默认 QL 方法 | Python parametric dispersion / MAP 实现 |
| 检验 | two-sided Wald，lfcThreshold=0 | quasi-likelihood F；poisson.bound 默认 TRUE | two-sided Wald，lfc_null=0 |
| 多重检验 | BH；independentFiltering=TRUE，alpha=0.1 | 所有预过滤基因上 BH | BH；independent_filter=True，alpha=0.1 |
| 离群值 | results 默认 Cook cutoff，替换所需最少重复数为 7 | robust dispersion / QL moderation，无 DESeq2 式 Cook 过滤 | cooks_filter=True、refit_cooks=True，min_replicates=7 |
| 用于比较的 LFC | 未收缩 MLE | glmFit 默认 prior.count=0.125，存在轻度 prior-count 收缩 | 未收缩 MLE |

edgeR 的 filterByExpr 根据设计矩阵的 leverage 计算所需样本数量，不能把它简化成“至少 3 个样本原始计数 >=10”。三套原始过滤布尔表均保留，以便解释测试基因全集的不同。原文 edgeR robust=FALSE 默认示例改为 robust=TRUE 是本项目明确的方法选择，不是对原示例语法报错的修复。

本次预先选定的过滤规则沿用参考指南的 DESeq2/PyDESeq2 规则和 edgeR 常用 filterByExpr；它们没有因本次显著基因数量改变。归一化、检验及软件实现的差异同样不为匹配参考结果而调整。

## 核实及修正

- 核对已安装包的函数签名与源码，并查阅官方 DESeq2 vignette、edgeR 手册、PyDESeq2 0.5.4 文档。当前 R 库使用 DESeq2 1.46.0、edgeR 4.4.0；网络 release 文档不代替已安装版本的接口核对。
- PyDESeq2 `DeseqStats` 默认 alpha=0.05。实际脚本显式使用 **alpha=0.1**；该值同时影响独立过滤，不能只把最终 CSV 的比较阈值改成 0.1。参考指南已修正此处代码。
- R 将 dex 参照设置在建模前；Python 使用有序类别明确 untrt/trt，并显式 contrast。按样本 ID 对齐 metadata，检查原始计数整数性、样本配对和设计矩阵满秩。
- edgeR 明确加载 SummarizedExperiment（指南独立 R 示例调用 assay/colData 所需），独立示例创建输出目录。本项目 edgeR 脚本直接读取主脚本导出的统一输入，消除数据来源差异。
- `lfcShrink(..., res=res, type='apeglm')` 保留主检验结果的 alpha 和独立过滤；MA 颜色明确 alpha=0.1。收缩 LFC 单独导出，主差异表和跨方法比较不使用该收缩值。
- 火山图显著性颜色仅用 FDR<0.1，与差异表一致；对 raw p=0 做数值保护；缺失 symbol 用基因 ID。热图标签同时显示 symbol 和 ENSEMBL ID，避免重名。
- 样本距离图使用 VST 欧氏距离本身做聚类，保存矩阵；PCA 保存坐标和解释方差；热图保存 Top30 选基因表与 VST 矩阵。
- 对比程序按 gene ID 对齐，禁止静默删除重复 gene ID。报告所有原生显著集上的双向重合率及 Jaccard，另外记录共同可检验子集指标；明确 LFC 相关性和方向一致性的分母。
- 原参考验收脚本中的固定数字和经验区间没有作为本阶段通过/失败标准。新报告校验实际输入、设计、过滤、结果范围、显著性标记、图形可读性和程序退出码，并将参考 Top 基因和数量作为独立诊断。

两份参考文档已加入本机实测状态及脚本入口，详细指南的上述关键代码已修正。其余单细胞、nf-core、Docker、Snakefile 与学习任务没有因此自动标记为本机通过。

## 产物和复现

运行入口为 `scripts/run_bulk.sh`，每次创建时间戳目录，保留已有资料。依次执行三个分析脚本、环境版本导出和实际输出验收，任一步失败则停止。`scripts/05_bulk_manifest.py` 在日志完成后写入所有产物与脚本副本的 SHA-256。首次实测分步骤启动三个脚本，全部使用相同参数和目录；该入口封装相同命令，已做 shell 语法检查。

每个结果 CSV 包含 gene、symbol、log2FC、pvalue、padj、significant，并保留工具提供的统计量。`*_significant.csv` 是从主表按 padj<0.1 生成的派生表。比较表 `comparisons.csv` 给出 Spearman、Pearson、双向重合率、Jaccard 和方向一致性；三对完整对齐表与共同显著基因 ID 均保留。

R sessionInfo 和全部 R 包版本、Python distribution 元数据、解释器版本及 API 签名、两个 Conda 环境的全部依赖/build/频道/explicit 锁文件都保存在实际运行目录。未安装或更新软件，也没有运行 Docker、Nextflow 或 nf-core。

官方资料：[DESeq2 分析 vignette](https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html)、[edgeR 手册](https://bioconductor.org/packages/release/bioc/manuals/edgeR/man/edgeR.pdf)、[edgeR QL workflow](https://www.bioconductor.org/packages/release/workflows/vignettes/RnaSeqGeneEdgeRQL/inst/doc/edgeRQL.html)、[PyDESeq2 0.5.4 DeseqStats](https://pydeseq2.readthedocs.io/en/v0.5.4/api/docstrings/pydeseq2.ds.DeseqStats.html)。实际输出结论以本机版本和日志为准。
