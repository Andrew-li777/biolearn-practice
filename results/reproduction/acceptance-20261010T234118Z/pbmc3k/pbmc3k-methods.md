# PBMC3k 实际分析、注释与差异实验

本阶段使用已有隔离环境，实际完成 Seurat、Scanpy、marker 分析、基于 marker 的推定注释和条形码比较。入口为 `bash scripts/run_pbmc3k.sh`，结果目录由 `results/pbmc3k/latest-run.txt` 指定；具体数字和参数以该目录的 `acceptance.md`、CSV 和对象为准。

## 数据和对象

两条路线均读取 `data/pbmc3k/filtered_gene_bc_matrices/hg19/`，来自 [10x PBMC3k 已过滤 UMI 矩阵](https://cf.10xgenomics.com/samples/cell/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz)。复用本机既有下载，并逐字节核对三个解压文件与归档成员。校验和是本机完整性记录，没有称其为上游签名。

原始 counts 保存为 `seurat/raw_counts.rds`（counts、ENSEMBL ID、symbol、barcode）与 `scanpy/raw_counts.h5ad`（整数 X）；保留原始全基因计数。Seurat 使用原始 ID 到分析 symbol 的显式映射，Scanpy 保留 gene_ids 并使 symbol 唯一；跨工具 HVG 比较使用 gene ID，不依赖可能不同的 symbol 唯一化规则。

分析对象保存为 `seurat/analysis.rds` 和 `scanpy/analysis.h5ad`，含注释的版本另存为 `analysis_annotated.rds/.h5ad`。Seurat RNA counts layer 与 Scanpy counts layer 都保存 QC 后的原始整数计数。Scanpy 的全基因 X 和 raw 保存 log-normalized 表达，而缩放/回归后的 HVG 数据用于 PCA；完整 PCA、邻居图、UMAP、marker 统计和标签均保留。所有对象都重新打开验证，counts 与输入子集一致。

## QC 和方法

两条路线统一基因至少在3细胞检出的过滤和最终严格阈值：`200 < detected genes < 2500`、`mitochondrial UMI percent < 5`。统计在基因预过滤后重算，同时保存原始全基因 QC 指标。每个条形码的保留/排除布尔值、各阈值失败原因、过滤前后分布及中位数分别保存在 QC 表和图中；不将可能重叠的失败原因简单相加。

Seurat：LogNormalize scale.factor=10000；vst 2000 HVG；HVG 缩放且不回归协变量；计算50 PCs，使用前10；Annoy Euclidean k=20 构造 SNN，prune=1/15；Louvain algorithm=1，resolution=.5；UWOT cosine UMAP，n.neighbors=30、min.dist=.3。PCA、聚类与UMAP种子均为42。

Scanpy：normalize_total=10000 + log1p；`flavor='seurat'` 为 dispersion HVG，min_mean=.0125、max_mean=3、min_disp=.5，不是 Seurat vst；在 HVG 上回归 total_counts 和 pct_counts_mt，缩放截断10；ARPACK 计算50 PCs、使用前40；Euclidean k=10 邻居/fuzzy graph；Leiden igraph，resolution=1、n_iterations=2、directed=False；UMAP min_dist=.5、spread=1。PCA、图、Leiden和UMAP种子均为42。参数在看到结果前固定，不为匹配9/8簇调参。

## Marker 和注释

两条路线均在 log-normalized 表达上做 cluster-vs-rest Wilcoxon，而非 scaled residuals。Seurat 使用 min.pct=.25、logfc.threshold=.25，Bonferroni 校正；Scanpy 使用完整基因、tie_correct=True 和 BH 校正。两条路线的检验全集和校正方法不同，不能直接将显著 marker 行数当作一致性指标。

`markers_all_tested.csv` 保存工具返回的检验（Seurat return.thresh=1 的实现仍排除 p=1 行），`markers_positive.csv` 为各路线正向筛选。`top10_markers.csv` 与 canonical marker 点图供审閱。点图分别采用 Seurat 表达标准化色阶与 Scanpy 按基因 min-max 色阶，不能把两张点图颜色数值直接相减；表达均值/比例另存数值表。

注释计划 `scripts/pbmc_annotation_plan.json` 根据本次两个路线的实际 marker 表和 canonical marker profiles 审阅生成，不套用教程簇编号。每簇支持基因的均值、比例、差异统计、Top10、置信描述及限制均保存；注释重放要求源 SHA 匹配、簇集合匹配且每簇至少两个 canonical marker 通过正向筛选。未来版本或结果变化需要重新审阅，不自动套标签。

主要依据为 [Seurat 官方 PBMC3k 教程](https://satijalab.org/seurat/articles/pbmc3k_tutorial) 和 [Scanpy PBMC3k 教程](https://scanpy.readthedocs.io/en/stable/tutorials/basics/clustering-2017.html) 的 canonical markers，并用本次表达验证：CD3/IL7R/CCR7 或 S100A4 支持 T 亚型，CD8A/B 与 CD3/CCL5/NKG7 区分 cytotoxic T，MS4A1/CD79A 支持 B，CD14/LYZ/S100A8 与 FCGR3A/MS4A7/LST1 支持两类单核，GNLY/NKG7/PRF1 支持 NK，FCER1A/CST3 支持 DC-like，PPBP/PF4 支持 platelet-like。

这些是推定标签，marker 支持程度不是独立准确率。T 亚型采用 naive-like / memory-like；DC 小簇、platelet-like 小簇明确限制，不据此断言精细 DC 亚型或“巨核细胞”。没有做 doublet 排除、参考映射或蛋白验证；单供体的细胞级 marker 检验用于探索，不是跨供体生物学重复的差异表达推断。

## 差异：实际测量与推测

完整 barcode 保留 `-1`，先检测源数据、cluster表、注释表的重复，再精确取交集。禁止静默去重。报告共有/独有细胞及清单、ARI、算术平均方式 NMI、原始与按行比例列联表、类型列联表；类型一致性仅是两套推定注释的一致性。

本次基线两条路线都为9簇，仍有分区差异。列联表显示主要差异在 T 细胞：Seurat naive-like cluster0 分到 Scanpy naive-like cluster1 490细胞、memory-like cluster0 198细胞；Seurat memory-like cluster2 分到对应两簇155/283细胞，另有34细胞分到 cytotoxic T。多数 B、NK、DC-like 和 platelet-like 对应更集中。这是对实际列联表的描述；不能据此认定一方更准确。

实测单因素对照保存至 `controlled_experiments.csv`，主分析保持不变：

- Scanpy 同图同种子，仅 resolution 1→.5。
- Scanpy 同图同 resolution，仅聚类 seed 42→7。
- Scanpy 同图同 resolution/seed，仅 Leiden→igraph multilevel Louvain。
- Scanpy 同细胞/HVG和其余参数，仅邻居输入 PCs 40→10，重建邻居图。
- Scanpy 同细胞/HVG和其余参数，仅取消 total_counts/MT 回归，重算 PCA 和邻居图。
- Seurat 同 SNN/种子，仅 resolution .5→1。

这些实验验证各因素在本流程中的敏感性；它们不是跨工具全部差异的因果分解，算法不同也不能单独解释全部差异。原始 counts、QC 指标和细胞集合直接对齐验证；HVG集合不同得到实测，但未单独替换 HVG 方法测定其因果贡献。SNN vs fuzzy graph、邻居构造和 k 差异、PCA 实现属于其余待验证原因。UMAP 在聚类之后计算，外观差异不会造成上游簇标签变化，更不能作为注释真值。

## 修复与验收边界

初次报告严格检查发现 Scanpy 一个表达比例经 sparse mean 累计误差略高于100%；已从 counts 的整数表达细胞数/总细胞数重算207行 profile，并重新生成62条注释证据，没有放宽验收范围。保留第一次失败报告、日志和初版脚本。Seurat 点图的透明底影响黑色界面可读性，已从保存对象重绘为白底，初版图片保留。这些是数值呈现/图形修复，没有重跑或调整聚类以匹配簇数。

Scanpy Wilcoxon ties 的数值警告经检查输出 scores/pvalues/logFC 均为有限数；回归/稀疏缩放性能警告保留。Seurat 使用现有 Wilcoxon 实现，未因缺少可选 presto 而安装软件。实际验收从对象、CSV、图片与退出码读取，不硬编码2638或9/8。完整环境build/版本、所有日志及产物SHA记录位于本次输出目录。
