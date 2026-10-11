# 项目进度

更新日期：2026-10-10 UTC。最新干净目录验收详见 [acceptance-report.md](../results/reproduction/acceptance-20261010T234118Z/acceptance-report.md)，此前核验见 [verification-report.md](verification-report.md)；所有历史产物保留。

## GitHub 首次发布（2026-10-11 UTC）

- 已按可复现发布边界整理 `.gitignore`：提交代码、文档、环境锁/版本清单、最终验收结果与关键图表；本机原始资料和既有完整产物均未删除。
- 不进入普通 Git 的内容包括下载数据与安装器、隔离环境本体、RDS/H5AD、BAM/CRAM、FASTQ、Snakemake/Nextflow 缓存、nf-core work/官方大输出、过时或失败尝试、重复历史运行目录及事务暂存目录。这些文件仍保留在虚拟机本地。
- 提交前候选集实测约64.8 MB、1488文件，最大单文件约13.2 MB；未发现密钥文件或典型GitHub/AWS令牌。生成HTML中的通用credential/password文字命中已按报告产物处理，不是检出的访问令牌。
- GitHub OAuth账号为`Andrew-li777`；已创建public仓库：`https://github.com/Andrew-li777/biolearn-practice`。首次提交及push状态以本节后续Git记录为准。
- 此次Git发布不等于跨主机新环境复现；被排除的大对象及完整历史结果仍应通过虚拟机共享目录、SFTP或rsync另行归档。

## 本次用户要求的独立干净目录验收（2026-10-10 UTC）

- **PASS**：依 README 在新目录 `results/reproduction/acceptance-20261010T234118Z/` 实际执行完整 Snakemake 工作流，初次与缺图重跑均退出 0。开始时没有分析子目录，未复制旧 results 作为运行输出。完整[验收报告](../results/reproduction/acceptance-20261010T234118Z/acceptance-report.md)记录命令、退出状态、实际统计、数据/参数/环境及证据路径。
- 明确复用三个 Conda 隔离环境（本次 actual explicit 与锁文件完全一致）、validation-venv、已下载 PBMC3k 归档和解压数据、airway 固定 R 包与 Scanpy 随包缩减参考；复用路径/SHA/实际版本见验收报告与 `evidence/`。未安装或覆盖系统环境。
- 初次及重建后 README 对照16/16、独立回读158/158；217声明产物全部存在、非空、可读取，连同附加文件232/232通过回读与四路线manifest核对。3个RDS/5个H5AD实际打开；补充诊断18/18及4个图变体通过。
- 本次实际结果：DESeq2/edgeR/PyDESeq2显著4916/6550/4685，共同显著4611；Seurat/Scanpy均2638细胞、13714基因、9簇；ARI=.6279310735、NMI=.7545047834。关键结果与历史实测一致，未为参考数字调参。
- 将本次 `bulk/pca.png` 移至 `evidence/moved/pca.png`，确认源路径缺失后重跑。bulk新attempt成功重建图片，SHA与移走原图完全一致；五张关键bulk统计表与其余三路线157文件未变。最终dry-run显示Nothing to be done。证据 `evidence/rebuild-proof.json`、`matrix-rebuild.log`、`final-dry-run.log`。
- 历史results共7790文件及11复用输入/锁文件SHA全部未变；没有覆盖历史已验证结果。证据 `evidence/preservation-check.json` 与 `historical-results-before.json`。原图、初次attempt及本次旧bulk均保留。
- nf-core **单独只读复核PASS，本轮没有重新运行官方流程**：既有attempt-2实际exit0、234任务exit0；1053官方输出重新核对SHA、MultiQC可读，历史独立验收267/267作为历史证据。复核命令exit0与状态见 `evidence/nfcore-status.json`。不能将其写成本次干净目录运行成功，也不代表airway原始FASTQ复现。
- 本轮无未解决阻塞。后续输入/源码变化按工作流依赖重跑；跨主机新环境与蛋白实验验证仍未执行。未推送GitHub、未改系统代理、未删除已有资料。

## 本轮已完成的修复与实际运行

- 容器预检PASS：Docker29.1.3可用，独立Skopeo1.24.1通过已有客户端网络导入精确官方镜像；容器DNS/HTTPS HTTP200。未修改系统代理。证据`environment/nfcore/container-check-ready-20261010/`及`image-imports-20261010/`。
- 主矩阵已在`results/reproduction/followup-20261010/`完整重跑：bulk39/39、PBMC83/83；DESeq2/edgeR/PyDESeq2显著4916/6550/4685；Seurat/Scanpy2638细胞、各9簇；ARI=.6279310735、NMI=.7545047834。主参数和输入未调整。
- 统一Scanpy整数expressing_cell_count字段，增加比例/唯一键/允许NA契约；runner独立attempt、日志命令/时间/脚本SHA/退出、验收后发布。旧结果完整保存。
- 独立扩大核验158/158；三RDS、三H5AD实际回读，原count逐元素对齐；19主图与此前视觉核验版本字节一致。新旧主要数值比较16/16。证据`results/reproduction/followup-20261010/verification/`。
- doublet及独立参考NOT RUN项已执行：`pbmc_validation/`18/18独立验收；Scrublet原2700细胞flag36，主QC内34（未删除）；PBMC68k独立参考700×765/共有764，holdoutaccuracy=.8428571429，macro-F1=.8347724920；映射一致率Seurat.8125714286、Scanpy.8049523810。缺CD14/MS4A7/PPBP/PF4及platelet类、单核/DC混淆，保留WARN/putative。
- 补做k20、精确邻居、Seurat HVG、实际SNN/fuzzy固定Leiden图诊断，均保存全barcode labels与重算ARI/NMI；主9/9不变。图边Jaccard=.05539603424；固定Leiden res.5时SNN9/fuzzy6，res1时11/9。没有为8簇参考调参。
- 新诊断接入Snakemake的PBMC下游，新增51声明产物，总217。最终诊断日志3/3完成；217文件全部非空，metadata217/incomplete0/输入hash变化0，最终dry-run无任务。日志`logs/snakemake-diagnostics-20261010.log`、`snakemake-all-final-dry-run.log`。
- 编排首轮venv软链接解析到基础Python导致缺skimage；第二轮图manifest与可变执行记录冲突；均修复并实际重跑。失败attempt和first/second日志保留。验收器首次raw RDS类型误判和SHA参数误判也已修复并保留首次失败证据；当前主验收完整PASS。
- 失败隔离实测exit1，测试fixture已发布75文件哈希全部不变。历史4目录372个manifest文件均匹配。未删除数据或资料、未推送GitHub。
- 环境版本元数据WARN已调查：Conda/模块/distribution差异实物记录于`environment/followup-20261010/version-provenance.json`，保留原环境，不手改已安装元数据。

## 官方流程已完成与实际验收

`results/nfcore/rnaseq-3.27.0-attempt-2/`固定commit a1fcdddd3b826fe46eb46f0479f2ff8a7815af05、test,docker、Nextflow25.10.4/Java21。22:50:05Z至23:23:46Z，exit0、234/234任务COMPLETED；独立验收267/267。5样本、gene125/transcript126，两定量分支读取；5BAM quickcheck成功，8序列化文件回读，1053输出/19下载文件及1170完整任务日志有清单。128PDF/132页可渲染，MultiQC71section/55图、5标签、页面错误0；主要PCA/distance图表一致。证据`verification/summary.json`、`objects-readback.json`、`documents/`、`full_task_logs.json`。阶段PASS；最终1053官方输出SHA全部保持，文档更新后Snakemake再次dry-run无任务。证据`verification/final_preservation_and_presentation.json`及`logs/snakemake-final-after-docs-20261010.log`。官方小型测试不等于airway FASTQ复现。

原MultiQC RGB兼容警告已定位；保留官方结果，使用project adapter只重绘展示。`presentation-corrected-4/`36原始模块/14综合统计与官方完全一致，颜色错误0、88PDF读取、HTML回读PASS。前三次失败/不完整展示尝试及完整日志保留，只有第4次有效。命令/digest/输入SHA/adapter在派生目录`REPRODUCE.md`和`verification/`。其余分类Library types、Top500上限标题、弃用警告已有解释。新增文档验证依赖全部隔离，不覆盖系统或原分析环境。

## 证据边界与下一步

1. 官方test及展示补充已经完成PASS；当前授权范围的可修复FAIL和有输入的NOT RUN均已处理。后续输入/脚本变化应按依赖重跑，额外大运行前复核可用磁盘（约5.7GiB）。
2. WARN保持方法解释：bulk参考+535无参考原流程可归因；PyDESeq2 df3警告准确触发；PBMC方法差异及缩减参考映射约80%不是类型准确率。
3. 无额外蛋白测量或第二主机位置，蛋白验证NOT RUN、实验准确性与跨主机新环境复现UNVERIFIED；最小动作是提供可对齐的实验数据或授权主机。现有数据可支持的doublet、计算参考和图诊断已完成。

## 先前阶段记录：Snakemake 干净复现通过；官方流程首次尝试失败

- 已实际安装独立 `biolearn-workflow`：Snakemake 9.13.4、Nextflow 25.10.4、OpenJDK 21.0.10；环境锁文件与安装日志在 `environment/`。没有覆盖系统 R/Python 或修改代理。
- 虚拟机初检：4 核、约 14 GiB 可用内存、32 GiB 可用盘；固定 rnaseq 3.27.0 要求 Nextflow≥25.10.4，兼容性已验证。核实记录在 `docs/nfcore-test.md`、`environment/nfcore/`。
- 已建立 `Snakefile`、`workflow/config.yaml`、`workflow/outputs.json`、`workflow/run_matrix.py`，显式跟踪所有矩阵产物。中文 `README.md` 提供复现命令、实测结果和局限。
- 干净输出 `results/reproduction/clean-20261010` 实际完成全部矩阵阶段；bulk 39/39、PBMC3k 78/78 验收通过。新旧主要结果表、QC、条形码聚类、ARI/NMI 与 SHA 清单核实通过 16/16；报告 `reproduction-acceptance.md`、日志 `logs/snakemake-clean.log`。
- 已只删除新输出的 bulk/pca.png，Snakemake 自动重跑 bulk 规则并生成图片，SHA-256 与删除前一致；PBMC 规则没有重跑。证据 `logs/rebuild-proof/evidence.json`，执行日志 `logs/snakemake-rebuild.log`。重建后仍为 16/16；最终 dry-run 显示无需执行。
- 官方测试仓库固定提交 `a1fcdddd3b826fe46eb46f0479f2ff8a7815af05`；实际尝试在 `results/nfcore/rnaseq-3.27.0-attempt-1` 已结束：流程退出 1，首个 GUNZIP_GTF 任务因 `docker: command not found` 退出 127；完成状态 false、MultiQC 未生成。21 个官方数据 URL 实际 HTTP 200，主机容器仓库 HTTP 401 认证挑战可达。
- 阻塞：无 Docker/其他容器引擎，普通用户 namespace 被限制，sudo 需要交互认证。已经请用户在虚拟机终端安装并启动 Docker；容器拉取、容器内网络、官方测试完成与 MultiQC 均不得记为通过。
- 下一步：容器引擎可用后验证 `docker info`、镜像拉取/运行/网络，再执行 `scripts/run_nfcore_test.sh`，读取退出码、完成状态和 MultiQC 验收。官方小型测试不是 airway 原始 FASTQ 的完整复现。
- 未推送 GitHub，未删除旧分析资料，未下载完整人类参考基因组。

## PBMC3k 两条路线（上一阶段已完成）

实际产物目录：`results/pbmc3k/run-20261010T200432Z`。验收报告：[acceptance.md](../results/pbmc3k/run-20261010T200432Z/acceptance.md)，**78/78 项通过**；全部主分析、注释、修复和最终报告阶段成功。

| 路线 | 原始细胞数 | QC 后细胞数 | 实际簇数 |
| --- | --- | --- | --- |
| seurat | 2700 | 2638 | 9 |
| scanpy | 2700 | 2638 | 9 |

条形码精确对齐：共有 2638，Seurat独有 0，Scanpy独有 0；源数据和结果表未发现重复条形码。ARI=0.627931，NMI(arithmetic)=0.754505。9/8个簇仅作参考，不作为验收输入；没有为匹配其调整主参数。

实际产物：

- 来源与完整性：`results/pbmc3k/run-20261010T200432Z/data_source.json`；复用同一10x归档，SHA-256为 `847d6ebd9a1ec9a768f2be7e40ca42cbfe75ebeb6d76a4c24167041699dc28b5`，解压文件逐字节核对。
- QC：两路线 `qc_raw.csv`、`qc_before.csv`、`qc_after.csv`、QC violin/scatter；总体 `qc_statistics.csv`、`analysis_summary.csv`、跨工具QC差异表。
- 对象：`results/pbmc3k/run-20261010T200432Z/seurat/raw_counts.rds`、`analysis.rds`、`analysis_annotated.rds`；`results/pbmc3k/run-20261010T200432Z/scanpy/raw_counts.h5ad`、`analysis.h5ad`、`analysis_annotated.h5ad`。重新打开验证，整数counts与源数据子集一致。
- marker与注释：各路线 `markers_all_tested.csv`、`markers_positive.csv`、`top10_markers.csv`、`marker_dotplot.png`；全局 `cell_type_annotations.csv`、`annotation_evidence.csv`，另有注释后UMAP与点图。
- 比较：`barcode_alignment.csv`、共有/独有数量JSON、两边独有细胞清单、`cluster_crosstab.csv/.png`、按行比例和细胞类型列联表。
- 版本及复现：各路线 method.txt、运行时版本、全量环境锁文件、日志、执行脚本与注释计划、SHA-256 manifest。入口 `bash scripts/run_pbmc3k.sh`。

实测单因素实验：

| 路线/变体 | 变体簇数 | 与该路线基线 ARI |
| --- | --- | --- |
| scanpy / louvain_same_graph | 8 | 0.636202 |
| scanpy / no_regression | 8 | 0.610619 |
| scanpy / pc10 | 14 | 0.495671 |
| scanpy / resolution_05 | 6 | 0.618129 |
| scanpy / seed_7 | 8 | 0.704651 |
| seurat / resolution_1 | 11 | 0.790078 |

这些实验验证分辨率、随机种子、同图算法、PC数和回归对本流程的影响。HVG集、SNN/fuzzy图、邻居算法与k差异的完整因果贡献尚未逐一分解；明确区分实测与推测，见 [pbmc3k-methods.md](pbmc3k-methods.md) 和 controlled_experiments.csv。

可修复问题：初次验收发现一个表达比例浮点累计误差超过100%，已用整数表达细胞数重算；Seurat点图透明底已改成白底。失败报告、初版脚本、图片和修复日志均保留。没有放宽阈值、删除资料或修改聚类来通过验收。

该阶段无阻塞。注释仍为 marker支持的推定标签，T亚型/小DC/platelet-like明确限制；未做doublet检测或独立参考验证。nf-core/rnaseq官方测试仍是后续独立任务，本轮未安装Docker/Nextflow、更新软件、修改代理或推送GitHub。

下一步：整理项目总README与结果对照、复现说明；若开展nf-core测试，作为独立任务核查运行条件。

## airway bulk（已完成）

实际运行目录：`results/bulk/run-20261010T195642Z`。验收报告：[acceptance.md](../results/bulk/run-20261010T195642Z/acceptance.md)，39/39 项通过；三个分析和报告进程退出码均为 0。

| 方法 | 实际预过滤基因 | 实际 FDR<0.1 显著数 | 上调 | 下调 |
| --- | --- | --- | --- | --- |
| deseq2 | 16596 | 4916 | 2618 | 2298 |
| edger | 16860 | 6550 | 3302 | 3248 |
| pydeseq2 | 16596 | 4685 | 2502 | 2183 |

设计统一 `~ cell + dex`，比较 trt vs untrt，alpha=0.1。DESeq2/PyDESeq2 使用至少 3 样本 count>=10；edgeR 使用 filterByExpr 与 robust QL F 检验，明确保留方法差异。参数未因参考数字调整。

| 比较 | Jaccard | Spearman log2FC | 共同显著基因方向一致率 |
| --- | --- | --- | --- |
| deseq2 vs edger | 0.740701 | 0.996428 | 100.00% |
| deseq2 vs pydeseq2 | 0.935685 | 0.999994 | 100.00% |
| edger vs pydeseq2 | 0.702273 | 0.996532 | 100.00% |

实际产物：

- 三套完整差异表：`results/bulk/run-20261010T195642Z/{deseq2,edger,pydeseq2}_results.csv`；显著子集另存为 `*_significant.csv`。
- 主分析图：`results/bulk/run-20261010T195642Z/pca.png`、`sample_distance.png`、`ma_plot.png`、`ma_unshrunk.png`、`volcano.png`、`top30_heatmap.png`，各图源数据已保存。
- 比较：`results/bulk/run-20261010T195642Z/comparisons.csv`、三对完整对齐表、成对及三套共同显著基因列表。
- 版本及记录：`results/bulk/run-20261010T195642Z/sessionInfo_*.txt`、`r_installed_packages.csv`、`python_runtime.txt`、`python_distribution_versions.json`、`environment/`、`logs/`、`scripts/` 和 `sha256-manifest.json`。
- 方法与文档修正：[bulk-methods.md](bulk-methods.md)；详细指南修正 PyDESeq2 alpha、样本对齐、apeglm 结果沿用、MA alpha、火山图口径与数值保护、热图标签、edgeR 示例依赖及 robust 方法选择。
- 可重复入口：`bash scripts/run_bulk.sh`，保留旧结果并新建时间戳目录；shell 语法与 Python 编译检查通过。

bulk 无阻塞。PBMC3k 的完整分析现已完成，见文首记录；nf-core 官方测试仍为后续独立任务。没有安装新软件、修改代理、删除资料或推送 GitHub。

以下保留环境准备阶段的历史记录，其当时未完成的 bulk / PBMC3k 项已由上面的实测更新。

## 当前范围

1. airway 现成计数矩阵：DESeq2、edgeR、PyDESeq2。
2. PBMC3k 已过滤 UMI 矩阵：Seurat、Scanpy。
3. nf-core/rnaseq 官方测试：后续独立任务，本轮不安装 Docker/Nextflow。

## 环境准备阶段完成（历史）

| 完成项 | 实际产物 / 证据 |
| --- | --- |
| 重新检查 Linux 系统、资源、路径、版本、现有环境 | `docs/environment-audit.md`；`environment/audit/host-network.json` |
| 复用兼容的 R 环境，不安装或更新 | `/home/a/miniforge3/envs/biolearn-r`：R 4.4.3；DESeq2 1.46.0、edgeR 4.4.0、airway 1.26.0、Seurat 5.5.1 |
| 复用兼容的 Python 环境，不安装或更新 | `/home/a/miniforge3/envs/biolearn-py`：Python 3.11.17；Scanpy 1.11.5、PyDESeq2 0.5.4 |
| 实际重新 library()/import 核心包，未发现核心包加载失败 | `environment/audit/r-load.log`、`python-load.log`；执行进程均退出 0，日志内逐包 PASS/MISSING 分类 |
| 记录完整直接和传递依赖版本、build、频道和精确下载地址 | `environment/audit/biolearn-r.packages.json`、`biolearn-py.packages.json`、两份 `.resolved.yml` 和 `.linux-64.explicit.txt`；R 包库另见 `r-installed-packages.csv` |
| 七个网络地址重新连通性检查成功 | GitHub、conda-forge、bioconda、CRAN、Bioconductor、PyPI、PBMC3k：本次 HEAD 全部 HTTP 200、TLS verify 0；`host-network.json` |
| 建立项目约定；保留原有审计资料 | `AGENTS.md`；旧审计备份 `environment/audit/environment-audit.previous.md` |

系统 Python 仍为 `/usr/bin/python3` 3.12.3。R、Conda/Mamba 未加入当前 PATH，但通过已有绝对路径可运行；这不是软件缺失。

## 已有产物（此前安装验收，本轮未重新运行分析）

- 安装报告：`docs/environment-installation.md`；安装日志：`environment/logs/install-*.log`。
- airway 的 DESeq2 size factor 和 edgeR dispersion smoke test：`environment/logs/verify-r.log`。
- PyDESeq2 合成数据拟合和统计检验、Scanpy 合成数据测试：`environment/logs/verify-python.log`。
- PBMC3k 数据和 SHA-256：`data/pbmc3k/`、`environment/validation/pbmc3k-sha256.txt`。
- PBMC3k Seurat/Scanpy smoke test：`environment/logs/verify-pbmc3k-r.log`、`verify-pbmc3k-python.log`；图：`environment/validation/pbmc3k-seurat.pdf`、`pbmc3k-scanpy.png`。

这些此前 smoke test 不能替代完整项目验收；当前完整三套 airway 差异表与交叉比较已完成，见上面的 bulk 阶段记录。真实 PBMC3k markers、细胞类型注释及跨工具 ARI/NMI 也已完成，见文首实测记录。前轮 smoke test 参数记录在 `environment/validation/verify-pbmc3k.{R,py}`，与参考文档全流程参数不同；不能据此声称完整复现。后续验收必须读取实际结果文件，不手工传入参考数字，不为匹配数字调参。

## 阻塞与待核实

- 当前环境准备无阻塞，核心分析包可用。
- 缺少 clusterProfiler、整个 tidyverse 和 Snakemake；前两者可选，Snakemake 属后续流程化，不阻塞当前范围，不补装。
- Docker、Java、Nextflow 在检查范围内未发现；Docker 引擎未核实。仅影响后续 nf-core 独立任务，不阻塞矩阵分析。
- scikit-misc 的 Python distribution 元数据为 0.0.0，而 Conda 包版本为 0.5.3；两类证据均记录，导入成功。
- HEAD 连通不能替代完整软件下载、Git clone 和完整数据下载验证。本轮不安装、不更新、不新增数据下载。

## 环境准备时的下一步（历史，bulk / PBMC3k 已完成）

1. 把参考代码整理为项目脚本，检查参数与当前版本 API，记录预过滤、设计公式、参照水平和随机种子。
2. 对 airway 运行完整 DESeq2、edgeR、PyDESeq2；保存计数、样本信息、差异表与图，按实际结果计算重合率、方向一致率和相关性。
3. 对 PBMC3k 固定并记录各路线参数，保存 QC 指标、簇标签、markers、UMAP 和注释依据；从结果文件读取数字并比较共有条形码的 ARI/NMI。
4. 后续另行处理 nf-core/rnaseq 官方测试的运行条件与验证，不在当前任务中安装 Docker/Nextflow。

以上保留环境准备时的计划；bulk 项现已完成，当前下一步以文首记录为准。

## 使用现有环境

从项目根目录执行，无需修改 shell 初始化文件：

```bash
/home/a/miniforge3/bin/conda run -n biolearn-r Rscript your_script.R
/home/a/miniforge3/bin/conda run -n biolearn-py python your_script.py
```

重新执行仅加载检查（不会安装软件）：

```bash
/home/a/miniforge3/bin/conda run --no-capture-output -n biolearn-r Rscript environment/audit/check-r.R
/home/a/miniforge3/bin/conda run --no-capture-output -n biolearn-py python environment/audit/check-python.py
```

不自动推送 GitHub，不修改代理，不删除已有资料。
