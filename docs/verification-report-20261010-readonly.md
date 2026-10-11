# 项目当前完成状态核验

核验日期：2026-10-10 UTC，现场检查约 22:30–22:42。范围依据 `AGENTS.md` 和本轮用户要求。只读取代码、环境、对象、表格、图片和日志，并在内存中重算过滤掩码、汇总和比较指标；没有安装软件、修改分析脚本或重跑拟合、聚类、完整分析。唯一项目写入是本报告。`docs/progress.md` 保持原样，其中过时的阻塞描述在下文纠正。

**矩阵分析和既有 Snakemake 复现有完整成功证据；项目整体尚未完成，因为 nf-core 官方测试最后一次实际运行失败。** bulk 参考数差异、PyDESeq2 警告、Scanpy 簇数差异和注释局限应保留为 WARN，不能用参考数字覆盖实测。

## 判定和证据目录

PASS＝完整执行及可读取产物相互支持；WARN＝已经运行，但有参考差异或解释/证据局限；FAIL＝执行失败、必需产物缺失或不一致；NOT RUN＝未执行；UNVERIFIED＝缺少足够证据。主阶段采用包含重要问题的判定，子项单独列出。

以下路径均相对于项目根 `/home/a/projects/biolearn-practice`；简写只是为缩短表格，不表示多个目录可混用。

| 简写 | 实际路径 |
| --- | --- |
| B | `results/bulk/run-20261010T195642Z` |
| P | `results/pbmc3k/run-20261010T200432Z` |
| CB | `results/reproduction/clean-20261010/bulk` |
| CP | `results/reproduction/clean-20261010/pbmc3k` |
| N | `results/nfcore/rnaseq-3.27.0-attempt-1` |

读取了 `AGENTS.md`、`docs/progress.md`、方法/环境记录、`scripts/` 中分析/注释/验收/运行脚本、结果目录中的执行副本和初版副本，以及 `Snakefile`、`workflow/config.yaml`、`workflow/outputs.json`、`workflow/run_matrix.py`、nf-core 配置和固定仓库。判断没有依赖 README。对现存日志全文读取并扫描错误、警告、退出及完成记录；日志清单见附录。

| 阶段 | 总判定 | 本次核验结果 | 问题与最小后续动作 |
| --- | --- | --- | --- |
| 1 环境准备 | WARN | R/Python 核心包现场全部加载；三个隔离环境锁记录与当前 conda-meta 相符；工作流工具可执行 | Snakemake/scikit-misc 的 Python 元数据版本异常；Docker 本会话组权限未生效，但组会话可访问服务。记录双重版本证据，使用新组会话；无需重装分析环境 |
| 2 airway bulk | WARN | 三路线完整执行、39/39 历史验收；8 样本、设计/方向/阈值正确，产物独立核验通过 | DESeq2 4916 与参考 4381 不同；PyDESeq2 有离散度先验警告。补清方法解释，保留实测，无需为参考数调参 |
| 3 PBMC3k | WARN | Seurat、Scanpy、注释产物和比较均存在；两路线 2638 细胞、9 簇；78/78 最终历史验收 | Scanpy 9 簇偏离参考 8；注释为推定；初次失败后已修复，旧失败文件保留。明确当前有效版本和局限，无需重跑聚类 |
| 4 nf-core/rnaseq 官方测试 | FAIL | 退出 1；trace 两任务 FAILED/127；成功任务 0；MultiQC 缺失 | Docker 现已安装，历史缺失阻塞不再准确；镜像拉取/容器执行未验证。后续先做容器预检，再运行固定版本测试 |
| 5 Snakemake/干净输出复现 | PASS | 164 个声明输出完整；历史干净运行和缺图重建成功；当前元数据无 incomplete，所有记录输入哈希相符 | 辅助表一个额外字段未在干净路线保留，记 WARN；未来增强表结构契约及失败重试隔离 |

## 1. 环境准备

### 现场加载和版本：PASS

本轮用 `/home/a/miniforge3/bin/conda run --no-capture-output -n ...` 执行独立只读探针；没有直接执行会写出文件的 `environment/audit/check-r.R`。

| 环境/包 | 现场实际版本/结果 | 历史证据路径 |
| --- | --- | --- |
| biolearn-r / R | 4.4.3；实际 library 全部成功 | `environment/audit/r-load.log`；B/`sessionInfo_deseq2.txt`、`sessionInfo_edger.txt`；P/`seurat/sessionInfo.txt` |
| DESeq2 / edgeR / airway | 1.46.0 / 4.4.0 / 1.26.0 | 同上和 B/`r_installed_packages.csv` |
| Seurat / apeglm / Matrix | 5.5.1 / 1.28.0 / 1.7.6 | 同上和 P/`seurat/r_installed_packages.csv` |
| AnnotationDbi / org.Hs.eg.db | 1.68.0 / 3.20.0 | B/`sessionInfo_deseq2.txt` |
| ggplot2 / ggrepel / pheatmap / patchwork | 4.0.3 / 0.9.8 / 1.0.13 / 1.3.2；加载成功 | 同上，P/`seurat/sessionInfo.txt` |
| biolearn-py / Python | 3.11.17；15 个核心模块实际 import 成功 | `environment/audit/python-load.log`；B/`python_runtime.txt`、`python_distribution_versions.json`；P/`scanpy/` 同名记录 |
| PyDESeq2 / Scanpy / AnnData | 0.5.4 / 1.11.5 / 0.12.19 | 同上 |
| numpy / scipy / pandas / h5py | 2.4.6 / 1.17.1 / 2.3.3 / 3.16.0 | 同上 |
| scikit-learn / igraph / leidenalg | 1.9.1 / 1.0.0 / 0.12.0 | 同上 |
| matplotlib / seaborn / statsmodels / umap | 3.11.2 / 0.13.2 / 0.15.0 / 0.5.12 | 同上 |
| biolearn-workflow / Snakemake | CLI `snakemake --version`＝9.13.4；import 成功 | `environment/biolearn-workflow.packages.json`；`logs/snakemake-clean.log` |
| Nextflow / Java | 25.10.4 build 11173 / OpenJDK 21.0.10-internal；现场版本命令成功 | `environment/nfcore/nextflow-version.txt`、`java-version.txt` |

实际 conda-meta 与 `environment/{biolearn-r,biolearn-py,biolearn-workflow}.packages.json` 按包名、版本、build 比较：303/285/154 个包，差异 0、额外包 0。B/P/CB/CP 中保存的 R/Python 环境记录也与现有根目录记录一致。各 `.resolved.yml`、`.linux-64.explicit.txt` 可读非空。安装历史里曾有下载 404、shard 超时、包缓存锁警告，但后续安装日志收尾和现场加载证明分析环境现已可用，不能把历史尝试错误当成当前加载失败。

### 环境记录解释：WARN

`importlib.metadata.version('snakemake')` 返回 **0.0.0**，而 CLI 和 Conda 记录为 **9.13.4**；`skmisc` 导入版本 **0.0.0**，Conda 的 scikit-misc 记录为 **0.5.3**。这是版本来源冲突，不是导入失败。最小动作：环境报告并列保存 CLI/Conda/Python distribution 的值，后续定位打包元数据来源；本轮不更新软件。历史系统 Python 缺包、可选 clusterProfiler/tidyverse 缺失不阻塞上述现有隔离环境的分析范围。

### 容器当前状态：WARN，历史缺失描述已过时

本轮现场输出：

```text
docker --version: Docker version 29.1.3, build 29.1.3-0ubuntu3~24.04.2
docker info: exit 1, permission denied ... unix:///var/run/docker.sock
id: 当前进程 groups 不包含 docker
getent group docker: docker:x:104:a
socket: srw-rw---- root docker /var/run/docker.sock
systemctl is-active docker: active
sg docker -c 'docker info --format ...': exit 0
ServerVersion=29.1.3 Driver=overlayfs Containers=0 Images=0
sg docker -c 'docker image ls --digests': exit 0，镜像列表为空
```

Docker 已安装且服务活动，用户账户已加入组；当前进程尚未继承组权限。只读的新组会话能够连接 daemon。没有拉取或启动容器，因此镜像拉取、容器工具和容器内网络为 **UNVERIFIED**，完整容器预检的成功运行为 **NOT RUN**。最小动作是后续用新登录/新组会话检查；不应继续要求重装已经存在的 Docker。`docs/progress.md`、`docs/nfcore-test.md` 和 `environment/nfcore/container-check/status.txt` 记录的是较早状态。

## 2. airway bulk

### 数据、参数和三路线执行

证据：B 与 CB 的 `airway_counts.csv`、`airway_coldata.csv`、`r_design_matrix.csv`、`python_design_matrix.csv`、三个 `*_filter.csv`、`*_method.txt`、`*_results.csv`、`*_significant.csv`、`logs/{deseq2,edger,pydeseq2,report}.log`、`logs/exit-status.tsv`，及 `scripts/01_bulk_deseq2.R`、`02_bulk_edger.R`、`03_bulk_pydeseq2.py`。

本轮直接与加载的 airway 1.26.0 对象核对：计数矩阵 **63677 基因 × 8 样本**，完全一致；整数、非负、有限，样本/基因 ID 唯一。样本顺序与 metadata、两份设计矩阵一致；4 个 cell 各有 1 个 trt 和 1 个 untrt。两设计矩阵均为 **8×5、秩 5**，dex 列编码 trt=1。设计为 `~ cell + dex`，untrt 参照；三个工具均比较 **trt vs untrt**；显著性仅为 **非 NA padj < 0.1**，不另加 logFC 门槛。

| 路线 | 执行/产物 | 实际保留基因 | 显著 | 上调/下调 | 过滤、检验和问题 | 最小动作 |
| --- | --- | ---: | ---: | --- | --- | --- |
| DESeq2 | PASS；主分析/报告退出均 0 | 16596 | 4916 | 2618 / 2298 | ≥3 样本 count≥10；ratio normalization；parametric Wald；BH + independent filtering，alpha=.1；结果偏离参考，另记 WARN | 补充与参考差异解释，不调参 |
| edgeR | PASS；退出 0 | 16860 | 6550 | 3302 / 3248 | filterByExpr 完整设计，min.count=10、min.total.count=15、large.n=10、min.prop=.7；TMM；robust estimateDisp/glmQLFit、QL F；全保留集 BH | 无必需修复；保留方法差异 |
| PyDESeq2 | 执行/产物 PASS；方法警告 WARN | 16596 | 4685 | 2502 / 2183 | 同 DESeq2 预过滤；ratio、parametric Wald、BH + independent_filter；Cook 过滤/refit；日志有离散度先验 MAD 警告 | 明确警告及统计局限；不改设计以消警告 |

本轮从 counts 重算 DESeq2/PyDESeq2 掩码、用现有 edgeR 只重算 `filterByExpr`（没有拟合）均与保存掩码逐项相符。主表 gene 集等于各保留集；共同比较用未收缩 LFC，edgeR 的默认 prior.count 轻度收缩与 R/Python MLE 不同；apeglm 仅用于 MA 图，保存的 pvalue/padj 与主结果相同。

各主表字段完整：gene、symbol、log2FC、pvalue、padj、significant，DESeq2/PyDESeq2 另有 baseMean/lfcSE/stat，edgeR 有 logCPM/F。pvalue/padj 全部有限且在 [0,1]；**三个工具本次 pvalue/padj NA 均为 0**。DESeq2 元数据 `filterTheta=0`、alpha=.1，日志报告 outlier/low-count 排除均为 0；不是强行填补 NA。

symbol 缺失为 DESeq2/PyDESeq2 各 **2391**、edgeR **2473**，属于基因注释未映射，允许；gene ID 完整。数值没有 NaN/Inf。DESeq2/PyDESeq2 size factor 范围约 **0.668031–1.399993**；edgeR TMM 因子 **0.948343–1.056310**；库大小和离散度为正、有限。显著标记逐项等于 padj<.1；显著子集 ID/顺序/字段一致，数值在 rtol=1e-12、atol=1e-14 下相同。CSV 重写引起最大绝对差为 PyDESeq2 **3.64e-12**，R 表约 1e-24，属于序列化精度。

### 比较与参考差异：实测比较 PASS，参考差异 WARN

本轮从主结果重新计算，而非引用 `comparisons.csv` 的完成声明：

| 比较 | 共同显著基因 | Jaccard | 共有预过滤基因 Spearman LFC | 共同显著方向一致率 |
| --- | ---: | ---: | ---: | ---: |
| DESeq2 / edgeR | 4879 | 0.740701382 | 0.996427653 | 1.000000 |
| DESeq2 / PyDESeq2 | 4641 | 0.935685484 | 0.999993550 | 1.000000 |
| edgeR / PyDESeq2 | 4635 | 0.702272727 | 0.996531589 | 1.000000 |

三方法共同显著 **4611**。证据 B/CB 的 `comparisons.csv`、三个 `comparison_*.csv`、`overlap_*.csv`。参考诊断 `reference_diagnostics.json` 中的 4381 是参考，不是本轮实测；DESeq2 实际 4916，差 **+535**。raw-p Top20 命中参考六基因中的 DUSP1、GPX3、MAOA、SAMHD1、SPARCL1（5/6）。不能据此断言唯一差异原因；矩阵来源、过滤、模型与实现不同是已记录条件，尚无参考原流程的逐因素同输入对照。

PyDESeq2 日志警告：残差自由度小、log dispersion 的 MAD 先验估计可能不稳；本轮设计矩阵 n−rank＝**3**。本轮进一步只读检查 `/home/a/miniforge3/envs/biolearn-py/lib/python3.11/site-packages/pydeseq2/dds.py:859`：实际触发条件为 `(num_samples - num_vars) <= 3`，警告文案却写 less than 3。因此本次触发符合实现，不表示设计自由度核算错误；统计局限仍记 WARN。无需重跑或删去配对因子。

## 3. PBMC3k

### 输入及对象：PASS

证据：`data/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz`、`data/pbmc3k/filtered_gene_bc_matrices/hg19/{matrix.mtx,genes.tsv,barcodes.tsv}`，P/CP 的 `data_source.json`、两路线 `raw_counts.*`、`analysis.*`、`analysis_annotated.*`、QC/cluster/UMAP/annotation 表及运行日志。

本轮重新计算归档 SHA-256：`847d6ebd9a1ec9a768f2be7e40ca42cbfe75ebeb6d76a4c24167041699dc28b5`；三个解压文件与归档成员逐字节相同。原始矩阵 **32738 基因 × 2700 细胞**。两路线保存的原始 counts 与同一输入精确相同。条形码和稳定 gene ID 唯一；源 symbol 有 **95 个重复行**，symbol 不是唯一 ID，Seurat/Scanpy 分别作唯一化，跨工具 HVG 比较使用稳定 gene ID。

| 路线及目录 | 本轮实际 readRDS/read_h5ad | 原始细胞/基因 | 分析及注释对象细胞/基因 | 实际簇数 | 核验 |
| --- | --- | --- | --- | ---: | --- |
| P、CP / Seurat | raw_counts.rds、analysis.rds、analysis_annotated.rds 全部成功 | 2700 / 32738 | 2638 / 13714 | 9 | counts 等于源子集；cluster、UMAP、cell_type 与 CSV 一致 |
| P、CP / Scanpy | raw_counts.h5ad、analysis.h5ad、analysis_annotated.h5ad 全部成功 | 2700 / 32738 | 2638 / 13714 | 9 | integer counts layer 等于源子集；cluster、UMAP、cell_type 与 CSV 一致 |

对象及对应表的 obs/barcode、var/gene 标识唯一且对齐；UMAP 有限。Scanpy X/raw 保留相同的全基因非负 log-normalized 表达，counts 单独保留，没有用回归残差进行 marker 测试。Seurat 对象 `@commands` 现场检查：LogNormalize=10000、vst=2000、PCA=50、neighbors dims1:10/k20、FindClusters resolution=.5/algorithm1/seed42；Idents 与 baseline cluster 相同，resolution=1 实验没有覆盖主结果。Scanpy `uns['analysis_parameters']` 与脚本和 method.txt 一致。

### QC 和主参数：Seurat PASS；Scanpy 运行 PASS、参考簇数 WARN

`scripts/11_pbmc_seurat.R`、`12_pbmc_scanpy.py` 和 P/CP 的各 `method.txt`、`qc_raw.csv`、`qc_before.csv`、`qc_after.csv` 为依据。基因至少 3 个细胞检出、初始化至少 200 基因；最终使用过滤基因后的 QC，严格 **200<genes<2500、MT%<5**。本轮重算掩码与 keep 列、对象和 cluster 表细胞集合完全一致。

两路线 raw/before/post 为 **2700/2700/2638**；剔除 **62**，低基因失败 **0**、高基因失败 **5**、MT 失败 **57**（一般不能假定这些原因互斥）。两条路线同条形码 QC 基因数及 UMI 最大差 **0**，MT 百分比最大绝对差 **1.64865e-6**，为浮点精度；QC 后最大基因数 **2413**、MT% 最大约 **4.993835**，符合阈值。

| 方法项 | Seurat | Scanpy |
| --- | --- | --- |
| 归一化 | LogNormalize 10000 | normalize_total 10000 + log1p |
| HVG | vst，2000 | seurat dispersion flavor，1838；mean .0125–3，min_disp=.5 |
| 回归/缩放 | 无回归，HVG scale.max=10 | HVG 回归 total_counts、pct_counts_mt；max_value=10 |
| PCA/图 | 50 PCs，使用10；Annoy Euclidean k20，SNN prune=1/15 | 50 PCs，使用40；Euclidean k10，fuzzy graph |
| 聚类 | Louvain algorithm1，resolution=.5 | Leiden igraph，resolution=1，n_iterations=2 |
| UMAP | uwot cosine，30 neighbors，min_dist=.3 | 使用既有图，min_dist=.5，spread=1 |
| 主种子 | 42 | 42 |

HVG stable-ID 交集 **1462**，Jaccard **0.615319865**，见 `hvg_overlap.json`。Scanpy flavor='seurat' 不等于 Seurat vst；两路线并非所有算法/参数相同，簇划分不同可预期。参考 Seurat9/Scanpy8 仅诊断，本次实际 **9/9**；不能使用变体结果替换主分析来匹配参考。

### Marker、注释与数值：产物 PASS，生物学确定性 WARN

证据：P/CP 的两路线 `markers_all_tested.csv`、`markers_positive.csv`、`top10_markers.csv`、`canonical_marker_profiles.csv`、`cell_type_annotation.csv`、`cell_labels.csv`，全局 `cell_type_annotations.csv`、`annotation_evidence.csv` 和 `scripts/pbmc_annotation_plan.json`。

Seurat 在 RNA/data 用 Wilcoxon、min.pct=.25、logfc.threshold=.25，Bonferroni；返回 **6964** 行，正向 p_adj<.05 子集 **2187**。Scanpy 在 log-normalized raw 用 Wilcoxon、tie_correct=True、BH，未作同样 marker 前筛选；返回 **123426** 行，logFC>.25、p_adj<.05 子集 **10924**。不能将两个 marker 数量作为相同口径比较。本轮正向子集与按主表重新筛选完全相符；marker 的 cluster+gene 唯一，概率 [0,1]，LFC、score 等导出数值有限。

全局 **18 个簇注释、62 行证据**；正确唯一键是 route+cluster+gene，跨路线重复 cluster/gene 不构成异常。逐行证据与本路线 marker/profiles 相符，每簇至少两个正向显著 canonical markers。两路线 profiles 共各 **207** 行，pct_expressing 在 **0–100%**；Scanpy 从整数 counts 重算比例最大差 **1.42e-14**；Seurat 从对象重算比例最大差 **4.97e-14**、mean_log1p 最大差 **6.66e-15**。Seurat 保存点图比例同样一致。

| 推定类型 | 关键依据 | Seurat 簇/细胞数 | Scanpy 簇/细胞数 |
| --- | --- | --- | --- |
| Naive-like CD4 T | CD3D/CD3E、IL7R、CCR7 | 0 / 705 | 1 / 656 |
| Memory-like CD4 T | CD3D/CD3E、IL7R，结合 S100A4/CCR7 模式 | 2 / 472 | 0 / 497 |
| B cells | MS4A1、CD79A | 3 / 344 | 2 / 341 |
| Cytotoxic CD8 T | CD3D/E、CD8A/B、CCL5/NKG7 | 4 / 274 | 6 / 307 |
| CD14+ monocytes | CD14、LYZ、S100A8、LST1 | 1 / 481 | 4 / 463 |
| FCGR3A+ monocytes | FCGR3A、MS4A7、LST1，结合 LYZ | 5 / 162 | 3 / 171 |
| NK cells | GNLY、NKG7、PRF1，结合较低 CD3/CD8B | 6 / 155 | 5 / 152 |
| Dendritic-like cells | FCER1A、CST3 | 7 / 32 | 7 / 38 |
| Platelet-like cells | PPBP、PF4 | 8 / 13 | 8 / 13 |

这是本次 marker 支持的推定，不是独立真值。T 亚型、DC、小 platelet-like 簇和边界细胞有明确局限；doublet 检测、独立参考映射或蛋白验证为 **NOT RUN**，类型准确性为 **UNVERIFIED**。最小动作：保留 putative/like 名称和限制；若后续要求生物学确认，再另行确定参考验证范围。

允许的 NA 明细（P 与 CP 相同）：

- `annotation_evidence.csv` 中正向 marker LFC/padj 各 **3** 个 NA：Seurat 簇2/S100A4、簇5/LYZ、Scanpy 簇0/S100A4；这三行 `passes_positive_marker_filter=False`，表示有表达依据但未进入正向显著表，不能宣称它们显著。其他同簇基因仍满足至少两个显著支持。
- `scanpy/feature_statistics.csv` 的 **CDC6 / ENSG00000094804**，dispersions、dispersions_norm 各 **1** 个 NA；在 QC 后 counts 总和实际为 **0**、highly_variable=False。零表达基因的离散度未定义，允许保留；不作为 HVG。means 中约 1e-12 是实现数值保护，不是实测表达。
- Scanpy tied Wilcoxon 的 invalid-divide、稀疏中心化密集化/性能警告存在，但最后导出 markers 无非有限统计量；Seurat 可选 presto 提示没有造成未处理异常。当前主结果未发现其他异常 NaN/Inf。最小动作：把这些 NA 分类纳入未来验收，禁止全表简单 `dropna`。

### 跨工具比较：PASS；差异原因完整分解 UNVERIFIED

本轮按完整 barcode（保留 -1 后缀）从 `clusters.csv` 重新计算：共有 **2638**，Seurat/Scanpy 独有均 **0**；独有清单是可读、非空的仅表头 CSV（0 数据行合法）。ARI＝**0.6279310734626542**，NMI arithmetic＝**0.7545047834392827**。`barcode_alignment.csv`、9×9 `cluster_crosstab.csv`、按行比例和图一致，计数和＝2638。保存的 broad_type_agreement＝**0.9499620924943138**，只是两套推定标签一致率，不是准确率。

`controlled_experiments.csv` 和各 `experiment_*.csv` 有实际日志与产物：Scanpy 同图 Louvain/无回归/PC10/resolution .5/seed7 分别为 **8/8/14/6/8** 簇，Seurat resolution1 为 **11** 簇。主结果仍为9/9。HVG 替换、图类型、邻居算法和 k 的独立因果贡献没有完整验证；不能将所有跨工具差异归因于单一因素。最小动作：方法讨论区分已测单因素与待验证推测；不为当前验收扩展分析。

## 4. nf-core/rnaseq 官方测试

**FAIL：这是已经执行并失败，不是 NOT RUN。** 实际目录 N、版本 **3.27.0**、Git HEAD 和 `pipeline-commit.txt` 一致：`a1fcdddd3b826fe46eb46f0479f2ff8a7815af05`。官方 `test,docker`，输入为固定 test-datasets samplesheet，参数证据 N/`output/pipeline_info/params_2026-10-10_20-19-34.json`；默认 aligner 为 star_salmon，pseudo_aligner 为 salmon。该测试不能等同于 airway 原始 FASTQ 完整复现。

| 核验项 | 状态 | 实际证据/数值 | 最小动作 |
| --- | --- | --- | --- |
| 固定提交、profile 和运行参数 | PASS | N/`pipeline-commit.txt`、`nfcore-vm.config`、`console.log`、`nextflow.log`、params JSON；与本地仓库一致 | 保持固定版本和官方数据 |
| 流程执行 | FAIL | N/`exit-code.txt`＝1；`completion-status.json` completed=false；详细日志 succeededCount=0、failedCount=2 | 容器预检通过后用新尝试目录复跑 |
| 两个已提交任务 | FAIL | N/`execution-trace.tsv`：GUNZIP_GTF、GUNZIP_ADDITIONAL_FASTA 均 FAILED、127；两 work 子目录 `.exitcode`＝127，`.command.err` 为 docker: command not found | 记录历史根因，不用现有 Docker 状态改写失败记录 |
| 最终产物 | FAIL | MultiQC 0 个；output 仅3个 pipeline_info 文件（DAG、params、workflow versions）；无完整分析交付 | 检查退出0、trace任务和最终矩阵/质控产物，不能只看 HTML 文件存在 |
| 执行诊断 HTML | PASS（存在） | execution-report.html 2932311 B、execution-timeline.html 252216 B；均可读非空 | 它们是失败运行诊断，不是成功 MultiQC |
| 容器镜像及内部网络 | UNVERIFIED | 现场 daemon 可经 sg 访问，但 Images=0；历史 container-check/status 为 FAIL/127 | 后续运行既有容器检查，再启动官方测试 |
| 参数警告 | WARN | 控制台将 max_cpus=4、max_memory=12.GB、max_time=4.h 列为 invalid input values；配置另有 `process.resourceLimits` 和 queueSize=2 | 后续去除无效/多余 params 字段并核对资源限制；本轮不编辑 |

详细日志中的 InterruptedException/RejectedExecutionException 出现在失败取消及传输线程收尾阶段，没有后续成功结束证据；不能忽略而宣告完成。官方 profile 同时提供 GTF/GFF、transcript_fasta 引起的警告和首次 `-resume` 被忽略也保留，不等于此次容器错误根因。21 个 URL 的历史 HTTP 200 仅证明当时主机访问；本轮未联网重测，当前容器拉取和容器内 HTTPS 仍无证据。

airway FASTQ 全流程为当前范围之外，**NOT RUN**；bulk 的成功是现成计数矩阵分析成功。

## 5. Snakemake 与干净输出复现

### 执行和现存证据：PASS

证据：`Snakefile`、`workflow/config.yaml`、`workflow/outputs.json`、`workflow/run_matrix.py`；`logs/snakemake-clean.log`、`snakemake-rebuild.log`、`snakemake-final-dry-run.log`、`reproduction-verify*.log`；`.snakemake/log/` 和 `.snakemake/metadata/`；`results/reproduction/clean-20261010/reproduction_checks.json`、`reproduction-acceptance.md`、CB/CP 全部结果。

- 输出契约实际 **bulk 68 + PBMC 96＝164 文件**，全存在、非空。仅表头的独有细胞表是有效空集合；必需日志无空文件。
- 历史 clean log 由缺失输出触发两个矩阵规则，报告3/3步骤100%完成；CB/CP 的所有阶段最后退出为0。这里已有执行证据，本轮没有运行 Snakemake，也未删除输出触发复算。
- 元数据 **164 条**、incomplete **0**；所有记录的 input_checksums 现场重新核算，变化 **0**。最终 bulk rule 时间 **20:21:07–20:22:33 UTC**，PBMC **20:17:46–20:20:40 UTC**；与本目录各日志 Started UTC 相符。两者不必在相同时间开始，属于同一配置下有效输出集。
- 历史 bulk 缺 `pca.png` 触发的是整个 bulk_matrix 规则，而非单独画图；rebuild log 2/2步骤完成、四阶段退出0。`logs/rebuild-proof/evidence.json`、保存的 before 图和当前图 SHA 都为 `041bf3aeb9392171130834b9319e85310fd12732b0d08562d24be5f851b84ca9`；PBMC 未重跑。最终 dry-run 记录 Nothing to be done；本轮只读该日志。
- 历史 reproduction_checks 16/16。独立扩大 CSV 比较：bulk **39 表全部同值**；PBMC **50 表**中48表在 rtol=1e-8、atol=1e-10 下相同，另两表差异如下；主 counts/QC/簇/UMAP/注释/ARI/NMI 均同值。

### 复现差异及追踪局限：WARN

`P/scanpy/canonical_marker_profiles.csv` 有额外 `expressing_cell_count`，CP 对应表没有该列；共同字段（cluster/gene/mean/pct/n_cells）数值一致。原因与保存的整数比例修复脚本相符，干净主脚本直接算整数非零数量的比例，没有输出额外计数列。`acceptance_checks.csv` 的 detail 包含历史重试退出记录及不同序列化格式，因此不是逐字相同，但两者均78 PASS。最小动作：未来把期望辅助字段写入契约并统一输出；现阶段不得宣称所有文件/字段完全一致。无需为此重跑主聚类。

`workflow/run_matrix.py` 复用指定输出目录并覆盖日志，若未来在半途失败会留下部分输出；当前不存在这一失败状态，完整零退出、时间、哈希和对象一致性支持有效完成。最小未来改进是独立 attempt 目录、完成后发布指针，日志附开始/结束/命令/退出，而不是仅依赖验收 CSV。Snakemake 粗粒度规则能追踪声明产物，丢一图会重跑整条路线；没有安装环境的独立干净机器复现证据（**UNVERIFIED**），本次证明的是同机既有固定环境、干净输出目录复现。

## 产物完整性、运行归属与失败残留

本轮逐文件重算 SHA-256，与保存 manifest 比较：

| 目录 | manifest 覆盖文件数（不含 manifest 自身） | 哈希不符/缺失 | 未入 manifest 的当前文件 | CSV 可读数 | PNG 可解码数 |
| --- | ---: | ---: | ---: | ---: | ---: |
| B | 73 | 0 | 0 | 39 | 6 |
| P | 124 | 0 | 0 | 52（含失败归档2表） | 17（含旧图4张） |
| CB | 72 | 0 | 0 | 39 | 6 |
| CP | 103 | 0 | 0 | 50 | 13 |

这些哈希只能证明当前文件与本地清单相符，不是签名或绝对来源证明。结合输入精确匹配、环境记录、执行副本、零退出和对象/表一致性，支持本次有效运行归属。顶层保存脚本与当前对应脚本全部相同；P 的 `scripts/initial_execution/` 是修复前代码，应按历史版本解释。

P 原始 report.log 明确 **FAIL 77/78、exit1**，失败项为 annotation expression evidence；`report-attempt-1/` 保存失败验收。随后 `presentation_fix`、`percentage_fix`、`annotation_python` 和两次 report 均退出0，`report_retry.log`、`report_final.log` 都为 **PASS78/78**。比例修复207行、maximum=100；初版图在 `seurat/presentation_before/`。最终表、对象、图片和哈希现场均有效；历史失败已经处理，不能只看第一个 report.log 判整阶段FAIL，也不能把它藏掉。最小动作：阅读时以 final/retry及最后退出记录为当前有效版本；未来加入 attempt ID。

B 的日志和数值完整，无失败后旧结果冒充成功的证据。CB 的 bulk 日志为成功重建覆盖版本，原 clean 的引擎日志及部分 before 证据仍在；CP 为 clean 成功运行。N 则只有失败和部分 pipeline_info，不能作为成功分析产物使用。`logs/nfcore/config.log`、`container-check.log` 为0字节，不独立支持成功；不能从空日志推断正常。

## 主要图逐张核验

本轮对 B/P/CB/CP 全部 PNG 实际解码；对以下 **19 张当前主要图**逐张打开视觉检查。旧结果与 clean 对应19张图均逐字节相同，所以视觉结论也适用于 clean 图。历史4张修复前图可解码，但不作为当前有效展示。

| 路径（B/P 下；CB/CP 对应同名） | 状态 | 标签与数据依据/实测 |
| --- | --- | --- |
| B/pca.png | PASS | 8个SRR样本、trt/untrt与4供体图例匹配；PC1 47.5%、PC2 23.8%，表值 .4750319866/.2382651027 |
| B/sample_distance.png | PASS | 8样本标签及cell/dex匹配；源矩阵与VST重算欧氏距离一致、对称、对角0 |
| B/ma_plot.png | PASS | apeglm LFC、FDR<.1；测试列与主表相同；y轴截断±5的超界点用三角显示 |
| B/ma_unshrunk.png | PASS | unshrunk LFC、FDR<.1，区别于收缩图的标签明确 |
| B/volcano.png | PASS | trt/untrt、raw p纵轴和FDR颜色口径一致；标注SPARCL1/CACNB2/DUSP1/SAMHD1/MAOA/GPX3/STEAP2/NEXN/MT2A/ADAMTS1为主表raw-p Top10 |
| B/top30_heatmap.png | PASS | 30个symbol+ENSEMBL标签匹配padj/pvalue排序Top30；源值与VST一致，8样本注释正确 |
| P/seurat/qc_violin.png | PASS | Pass QC TRUE/FALSE及3指标，对应qc_before掩码和分布 |
| P/seurat/qc_scatter.png | PASS | UMI/genes/MT%，200/2500界线和keep图例，范围与QC表一致 |
| P/seurat/umap_clusters.png | PASS | 簇0–8；标题Louvain/.5/PC1:10，与对象和clusters表一致 |
| P/seurat/umap_cell_types.png | PASS | 9个推定类型标签，簇到类型映射与cell_labels一致 |
| P/seurat/marker_dotplot.png | PASS | 0–8簇、23基因面板，比例和保存DotPlot数据/对象一致；白底可读 |
| P/seurat/marker_dotplot_cell_types.png | PASS | 9类型、20基因，标注与annotation表一致；白底可读 |
| P/scanpy/qc_violin.png | PASS | Fail/Pass、gene/UMI/MT%，与qc_before和掩码一致 |
| P/scanpy/qc_scatter.png | PASS | UMI/genes/MT%，200/2500界线，范围与QC表一致 |
| P/scanpy/umap_clusters.png | PASS | 簇0–8；标题Leiden/1/40PC，与对象/表一致 |
| P/scanpy/umap_cell_types.png | PASS | 9推定类型，与对象cell_type和cell_labels一致 |
| P/scanpy/marker_dotplot.png | PASS | 0–8簇、23基因；fraction表范围0–1，图例以百分数呈现；颜色按基因缩放0–1 |
| P/scanpy/marker_dotplot_cell_types.png | PASS | 9类型、20基因，类型与annotation一致；空白边距不影响标签 |
| P/cluster_crosstab.png | PASS | 9×9列联值逐格与从共有barcodes重建表一致，总和2638 |

图片的标签/源表/绘图脚本/对象和哈希形成证据链；本轮没有重绘以逐像素逆推每个点。参考材料中的图、安装阶段 smoke 图和 nf-core 执行 HTML 不用于代替当前主要分析图验收。

## 按依赖关系的下一步（本轮不执行）

1. **先更正文档事实**：在后续允许写入时更新 progress/nfcore 文档，记录 Docker29.1.3 已安装、daemon active、sg会话可访问；保留旧失败原因。并记录 Snakemake metadata0.0.0/CLI9.13.4 和 scikit-misc 两类版本。
2. **容器预检 → 官方测试**：新组/登录会话已能只读访问服务；下一步按 `scripts/check_container.sh` 检查镜像拉取、运行、digest和内部DNS/HTTPS。通过后审阅 max_* 无效参数警告，再在新attempt目录执行固定3.27.0官方test。保留首轮失败资料。
3. **官方测试结束 → 完整验收**：读取退出码、完整Nextflow日志/trace，检查所有必需任务成功或合法缓存及MultiQC/主要输出非空可读；仅满足这些条件才更新为PASS。airway FASTQ完整复现仍不在这条依赖链中。
4. **矩阵报告完善可独立进行**：解释bulk +535差异和PyDESeq2警告，明确PBMC9/9参考差异与推定注释限制；不修改参数去迎合参考，不需要重新拟合/聚类。
5. **未来工作流增强**：统一canonical profile附加字段、显式schema契约和attempt/结束记录，保留NA白名单；这些属于后续修改。跨工具完整因果分解、doublet/独立参考确认及跨机器环境复现，仅在另行确定范围后开展。

本轮未修改 progress.md、脚本或既有分析产物；未安装、拉取镜像、启动容器、推送GitHub、改变代理或运行完整分析。

## 附录：全文读取的完整日志清单

以下统计来自本轮对现存文件全文读取，不是只读取tail。错误关键词数量只用于定位，不代替执行判定；历史失败、下游取消异常和已经修复的失败应结合正文解释。两份 .snakemake 原始日志与外层捕获日志分别列出。

日志共 **65** 个；扫描以核验时现存日志为准，不能恢复已覆盖的历史stdout。

| 实际路径 | 字节数 | 行数 | 错误关键词行 / 警告关键词行 | SHA-256 |
| --- | ---: | ---: | --- | --- |
| `.snakemake/log/2026-10-10T201745.905536.snakemake.log` | 47238 | 54 | 0 / 0 | `1ec3948b3bd31e5d793b55cf5ca8c095c4ade01df35f4154cfb125e21e31d1ca` |
| `.snakemake/log/2026-10-10T202107.190979.snakemake.log` | 21500 | 41 | 0 / 0 | `34d81c7cf63e0e59aff7dcd0b228b6a1042090804abfd04c83d8a6f3ab677f5a` |
| `environment/audit/base-python-load.log` | 400 | 19 | 0 / 0 | `a2d295b842fd0dadddac586a61e3dc4076054fa616fea184406c3d46f7bdba70` |
| `environment/audit/extra-tool-scan-errors.log` | 0 | 0 | 0 / 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `environment/audit/host-network-summary.log` | 4129 | 166 | 0 / 0 | `b323decb107c3eada8a2e6f27eaff28f3b7717622a927064f8a0c6134f598ade` |
| `environment/audit/python-load.log` | 448 | 19 | 0 / 0 | `f3f89b75eb392658fcee72cc24741a78b7c4de599a4bc41ed5a545df324b8fac` |
| `environment/audit/r-environment-python-load.log` | 416 | 19 | 0 / 0 | `be9fca56605e3e44a9fa42262ff04340afc8b435fd418f51927480b8c6f76591` |
| `environment/audit/r-load.log` | 5165 | 94 | 0 / 0 | `431a50556a503bfa65daa84dded2e38d05005714dbd2df38e7bd41a855723a5e` |
| `environment/audit/system-packages-query-errors.log` | 522 | 10 | 0 / 0 | `2037b61f01d60927630d23597a4ba06b9c3d6a8850da9c9f23f8697ebb62b2f4` |
| `environment/audit/system-packages.log` | 70 | 2 | 0 / 0 | `8284b6a3e25278ca99b30fbf02eaeb152b99f8f37edd03b74be23bd2114792a6` |
| `environment/audit/system-python-load.log` | 359 | 19 | 0 / 0 | `30493bf605ceb8324d9a7d7f186ab46193c49652d9203e45f34f4511d51d85f0` |
| `environment/logs/download-miniforge.log` | 3530 | 50 | 1 / 0 | `515b0c6959da7650849218647e05d00934e2d37906806469633c3f7dff0c2320` |
| `environment/logs/download-pbmc3k.log` | 554 | 8 | 0 / 0 | `3b278ff25063d7cbd7a947d0ffc00159436ba7a348824da07f7d20a4e6bb67f7` |
| `environment/logs/install-miniforge.log` | 25695 | 508 | 0 / 1 | `b88c0aa91c69b0999368dcda0cec5abb7e1553cc885f9ae86d05684d162e656d` |
| `environment/logs/install-python-shards-attempt.log` | 980 | 7 | 1 / 1 | `91e9b72f51b149e8365e7ffce1d2554f14ccd3f4c05430470ad59ae70d536998` |
| `environment/logs/install-python.log` | 41536 | 638 | 0 / 1 | `1dac2bfa225dcc1fc386a72585a30aa73173c0aa9749b787c459cdbabd7a13a9` |
| `environment/logs/install-r-shards-attempt.log` | 780 | 6 | 0 / 1 | `6488c6e3ccd9f52c5f00b4114bde53c2d62bd211072d5ce473c52324c18ee7a8` |
| `environment/logs/install-r.log` | 57219 | 903 | 2 / 6 | `74bced3848eaf6f0bb861592ee551c2a7b4cfe0f47018b8b4bd9bcede1cd66c3` |
| `environment/logs/install-workflow.log` | 24527 | 364 | 0 / 1 | `f44174fb5d73398918e945a17d9b48383b181338c623baa4f75d8963d5c4a760` |
| `environment/logs/miniforge-checksum.log` | 77 | 1 | 0 / 0 | `46416777b91852264da85be9a3da0b2a825abbc0f9b8cae69ba0687e0a09b241` |
| `environment/logs/verify-pbmc3k-python.log` | 249 | 3 | 0 / 1 | `880caca8ac57d70188d8a0864957839c500bc7bf5183a633b41859f33c8555b6` |
| `environment/logs/verify-pbmc3k-r.log` | 4212 | 76 | 0 / 2 | `d7fc1630363071ca86bd336e837e1927029f64478d8609ffe688d415c368be3c` |
| `environment/logs/verify-python.log` | 2230 | 60 | 0 / 1 | `d61b1a4cacb66e7adae4c22dca22774fa9d7bd87b195b4db36e28e8d66a0ba75` |
| `environment/logs/verify-r.log` | 10182 | 275 | 0 / 1 | `b2b830d9b47df35f37cd53f5febf4770a6d8d64747c9e84ec7612981d23d54db` |
| `logs/nfcore/attempt-1-status.log` | 351 | 11 | 0 / 0 | `4920c14dc3fcaa22f7409d555a96f7b1113d0f821671dbd62b13637487413698` |
| `logs/nfcore/clone.log` | 628 | 18 | 0 / 0 | `bbd6cf8a0c430d06394d061fb2172a4e8548803d5e3908cffb5d7faac886550f` |
| `logs/nfcore/config.log` | 0 | 0 | 0 / 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `logs/nfcore/container-check.log` | 0 | 0 | 0 / 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `logs/rebuild-proof/deseq2-before.log` | 1094 | 33 | 0 / 0 | `3b7ae56d86f3aebd4f693defb07c9d2c55766679c22747e92ad5ac8e6920907c` |
| `logs/reproduction-verify-after-rebuild.log` | 685 | 24 | 0 / 0 | `a1cf03b3a87e882059f3375d772c879e004ba44f49d7bae157e472f30b787d99` |
| `logs/reproduction-verify.log` | 685 | 24 | 0 / 0 | `a1cf03b3a87e882059f3375d772c879e004ba44f49d7bae157e472f30b787d99` |
| `logs/snakemake-clean.log` | 47465 | 69 | 0 / 0 | `424b1122116b9611ea4c6548c186b5b24a36fa4ce117894ae6ee3deabf8be3dc` |
| `logs/snakemake-final-dry-run.log` | 101 | 3 | 0 / 0 | `3c2aac91cbd010d56cc562fd1a6d15d54582648e4c414dfb5fbf3661d6d78c5c` |
| `logs/snakemake-rebuild.log` | 21590 | 48 | 0 / 0 | `8c860a561cfa26c9a871c217737f04c0ad86e90a8a47d27bd157109ed129cc27` |
| `results/bulk/run-20261010T195642Z/logs/deseq2.log` | 1048 | 32 | 0 / 0 | `ed65511a274c40ee6984a391d1e40305fbb4a5c07f9fba5de6e27c7ef925b886` |
| `results/bulk/run-20261010T195642Z/logs/edger.log` | 103 | 3 | 0 / 0 | `71d8122029158264dcf1da91c9722e11549b02d22f43a4c434c4c47fa4675e1b` |
| `results/bulk/run-20261010T195642Z/logs/pydeseq2.log` | 1772 | 44 | 0 / 1 | `61ad0baeb873851914f0d7e5a8188e0f1384ba6cc6dccc26261a4ca52dec542f` |
| `results/bulk/run-20261010T195642Z/logs/report.log` | 1958 | 9 | 0 / 0 | `e8ded4cef336911851b02aba69b455e2eab88236ba7d4a3037f1af1ca71b6b2a` |
| `results/nfcore/rnaseq-3.27.0-attempt-1/console.log` | 8193 | 144 | 7 / 8 | `a85acccd13da6a2973b57809402fced58e45abe5b41ec2f9a1e790dc2425a3a2` |
| `results/nfcore/rnaseq-3.27.0-attempt-1/nextflow.log` | 127593 | 852 | 28 / 8 | `7352d14268278682dc121fe36b6925710636153da7a249e4a7c7805b99793b45` |
| `results/nfcore/rnaseq-3.27.0-attempt-1/work/24/3eaa39d9123bce399e02e6536c6996/.command.log` | 50 | 1 | 0 / 0 | `0cbb911cdf9027426a37aaf4081a2d28a57070a9e635e2c92883d3abce2261cc` |
| `results/nfcore/rnaseq-3.27.0-attempt-1/work/f4/fce340914b5cb48c0e44d4ac767ade/.command.log` | 50 | 1 | 0 / 0 | `0cbb911cdf9027426a37aaf4081a2d28a57070a9e635e2c92883d3abce2261cc` |
| `results/pbmc3k/run-20261010T200432Z/logs/annotation_python.log` | 73 | 1 | 0 / 0 | `f508a6b0d3a92b1804d5f64918b66a2d7edc6f6c81796bcdb2015cf6fb21a1dc` |
| `results/pbmc3k/run-20261010T200432Z/logs/annotation_python_retry.log` | 73 | 1 | 0 / 0 | `f508a6b0d3a92b1804d5f64918b66a2d7edc6f6c81796bcdb2015cf6fb21a1dc` |
| `results/pbmc3k/run-20261010T200432Z/logs/annotation_r.log` | 39 | 1 | 0 / 0 | `de331fddb9d88a64bd505b61a26d7907b7c8512a3ca21cec68874729d1c8a176` |
| `results/pbmc3k/run-20261010T200432Z/logs/original-download.log` | 554 | 8 | 0 / 0 | `3b278ff25063d7cbd7a947d0ffc00159436ba7a348824da07f7d20a4e6bb67f7` |
| `results/pbmc3k/run-20261010T200432Z/logs/percentage_fix.log` | 82 | 1 | 0 / 0 | `96e6b2c37990c87ff50a5780aba36620e3196b5a331bfcf874aa4b8555ef575c` |
| `results/pbmc3k/run-20261010T200432Z/logs/prepare.log` | 110 | 1 | 0 / 0 | `c5bd183eec7ace0444ac2a02b7b0f323f1c8a752cc36e37c2ba36843543d0e93` |
| `results/pbmc3k/run-20261010T200432Z/logs/presentation_fix.log` | 85 | 1 | 0 / 0 | `d6c5414afe359335131e96e645747ab75697f6a0fae67e555d19d7e8aeee8e30` |
| `results/pbmc3k/run-20261010T200432Z/logs/report.log` | 3388 | 24 | 2 / 0 | `df72e06526ffaaf92fef518fd192cb9091b18def59d2fb5bb3f2e9b33c886f82` |
| `results/pbmc3k/run-20261010T200432Z/logs/report_final.log` | 3238 | 23 | 0 / 0 | `517752d39caa7007c989e95c47d909cbbbdc95925bf9fcc80a3932b7a34cd31e` |
| `results/pbmc3k/run-20261010T200432Z/logs/report_retry.log` | 3238 | 23 | 0 / 0 | `517752d39caa7007c989e95c47d909cbbbdc95925bf9fcc80a3932b7a34cd31e` |
| `results/pbmc3k/run-20261010T200432Z/logs/scanpy.log` | 2607 | 26 | 0 / 12 | `78b864e03cac188109a2f6760f7edacddcd55e5eec2bcf75848c427d33973026` |
| `results/pbmc3k/run-20261010T200432Z/logs/seurat.log` | 1079 | 23 | 0 / 1 | `465cf6493e3567a5598ba862b4108c174af6f455b370362cadaddbd0df54cecd` |
| `results/pbmc3k/run-20261010T200432Z/report-attempt-1/report.log` | 3388 | 24 | 2 / 0 | `df72e06526ffaaf92fef518fd192cb9091b18def59d2fb5bb3f2e9b33c886f82` |
| `results/reproduction/clean-20261010/bulk/logs/deseq2.log` | 1094 | 33 | 0 / 0 | `ae284608799ad4f8fa0de42aa506443e3adced052ad76fd5a5273a02d4e0c0c1` |
| `results/reproduction/clean-20261010/bulk/logs/edger.log` | 149 | 4 | 0 / 0 | `488a3f5c5b7c1f37de799f138bb75d1b70a0ca46d91b6e00735fc14ce09793fd` |
| `results/reproduction/clean-20261010/bulk/logs/pydeseq2.log` | 1818 | 45 | 0 / 1 | `66acfc596761199206ffc4b0053b8b65b8c4afda6b9d5ae562c114799ba13aa5` |
| `results/reproduction/clean-20261010/bulk/logs/report.log` | 2011 | 10 | 0 / 0 | `3acb25c594cf448187e57fc87813ddb0862bce7d1bc516dd141c7a7fdadaee78` |
| `results/reproduction/clean-20261010/pbmc3k/logs/annotation_python.log` | 119 | 2 | 0 / 0 | `8d482659576bcd3f059e79d68a678fd0778d81c932c5ac35cb4372c2ff58f507` |
| `results/reproduction/clean-20261010/pbmc3k/logs/annotation_r.log` | 85 | 2 | 0 / 0 | `cd4d489c9660edc60458ac730da3193f1f06c48205ed61052f09dded897a8332` |
| `results/reproduction/clean-20261010/pbmc3k/logs/prepare.log` | 156 | 2 | 0 / 0 | `f100f89c0ec10314a0ae443e338b4a1149b0015b498db44081d85ab78dbcbd89` |
| `results/reproduction/clean-20261010/pbmc3k/logs/report.log` | 3284 | 24 | 0 / 0 | `d9b2bf16090e4c624c42e254bdf1a49b6d3bcccd01eee3524000a701144b3242` |
| `results/reproduction/clean-20261010/pbmc3k/logs/scanpy.log` | 2057 | 23 | 0 / 10 | `7240580f44aeaebb33bd130e7974dceb63d4825a300712bbd2d34136b8834438` |
| `results/reproduction/clean-20261010/pbmc3k/logs/seurat.log` | 1125 | 24 | 0 / 1 | `f55eb0e8179f9d17c32520ecf3c720eb322d2d63af907e3561023ed041c5f051` |

本轮只读检查包括：逐文件SHA对照；P/CP共12个RDS/H5AD实际加载（每条路线3个对象、两个目录）；全部CSV解析与主键/数值扫描；19张主要图打开和新旧字节比较；源counts比对、过滤掩码、显著子集、marker证据及共有barcode ARI/NMI重算；当前包加载与Docker只读诊断。探针stdout中的实测数值已记入正文，未调用会覆盖历史验收或运行分析的脚本。

报告日志索引生成时间：2026-10-10T22:42:36.447093+00:00。
