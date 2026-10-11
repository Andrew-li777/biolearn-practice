# 独立干净目录矩阵复现验收报告

结论：PASS。报告生成 UTC：2026-10-10T23:47:57.147379+00:00。

实际输出目录：`/home/a/projects/biolearn-practice/results/reproduction/acceptance-20261010T234118Z`。工作目录：`/home/a/projects/biolearn-practice`。
按 README 的新 output_root 运行完整 Snakemake 矩阵工作流及其验证命令。开始时四个分析子目录均不存在；未复制历史 results 充当输出。源码、工作流与输入在项目根目录使用，各分析规则在本目录的 `.attempts/` 实际执行，通过内部验收后发布。此项验收验证本机锁定环境中的干净输出复现，没有重装环境或声称跨机器复现。

## 复用项与环境

- 复用 `/home/a/miniforge3/envs/biolearn-r`、`biolearn-py`、`biolearn-workflow`；三者本次 Conda explicit URL/build 清单与项目锁文件完全一致。未安装、更新或覆盖系统环境。
- 复用 `environment/validation-venv`，其基础解释器为 biolearn-py、Python 3.11.17；完整本次 pip 清单见 [validation-venv-freeze.txt](evidence/validation-venv-freeze.txt)。
- 复用 `data/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz` 和 `filtered_gene_bc_matrices/hg19/{matrix.mtx,genes.tsv,barcodes.tsv}`。归档 SHA-256 为 `847d6ebd9a1ec9a768f2be7e40ca42cbfe75ebeb6d76a4c24167041699dc28b5`。归档与解压内容匹配由本次 prepare/内部验收核对。
- airway 输入从锁定 R 包 airway 实际导出，输入计数与样本表在 `bulk/airway_counts.csv`、`bulk/airway_coldata.csv`；没有复用历史分析矩阵输出。
- 补充诊断复用 Scanpy 随包提供的 PBMC68k reduced 独立参考；实际路径和 SHA 见 [reference-reuse.json](evidence/reference-reuse.json)。没有复用已有 doublet 或映射结果。
- 源码、README、方法文档和工作流从当前项目读取；实际运行脚本快照、脚本 SHA、参数及各阶段命令由四个路线的 `run-provenance.json`、`scripts/`、`logs/` 保存。

证据：[干净开始](evidence/clean-start.json)、[输入与锁文件 SHA](evidence/reuse-input-hashes.json)、[环境锁核对](evidence/environment-checks.json)。完整环境清单在 `evidence/*.actual-explicit.txt`、`*.actual-packages.json` 及各路线的 `environment/`。

| 环境 | 核心包 | 本次 Conda 记录版本 | build |
|---|---|---|---|
| biolearn-r | bioconductor-airway | 1.26.0 | r44hdfd78af_0 |
| biolearn-r | bioconductor-deseq2 | 1.46.0 | r44he5774e6_1 |
| biolearn-r | bioconductor-edger | 4.4.0 | r44h3df3fcb_0 |
| biolearn-r | python | 3.15.0 | h6e52b48_100_cp315 |
| biolearn-r | r-base | 4.4.3 | h502d0c9_11 |
| biolearn-r | r-seurat | 5.5.1 | r44h3697838_0 |
| biolearn-py | pydeseq2 | 0.5.4 | pyhdfd78af_0 |
| biolearn-py | python | 3.11.17 | h5f976f7_1_cpython |
| biolearn-py | scanpy | 1.11.5 | pyhd8ed1ab_0 |
| biolearn-workflow | python | 3.11.17 | h5f976f7_1_cpython |
| biolearn-workflow | snakemake-minimal | 9.13.4 | pyhdfd78af_1 |

## 数据、参数和实际关键统计

bulk 统一设计 `~ cell + dex`，比较 trt vs untrt，FDR<0.1。DESeq2/PyDESeq2 预过滤为至少 3 个样本 count>=10；edgeR 使用 filterByExpr、robust QL F 检验。输入为 63,677 基因×8 样本。参数依照方法和既定流程，没有为匹配参考数字调参。

| 方法 | 实际预过滤基因 | 显著基因 | 上调 | 下调 |
|---|---:|---:|---:|---:|
| deseq2 | 16596 | 4916 | 2618 | 2298 |
| edger | 16860 | 6550 | 3302 | 3248 |
| pydeseq2 | 16596 | 4685 | 2502 | 2183 |

三种方法共同显著基因：4611。DESeq2/PyDESeq2 显著集合 Jaccard：0.935685483871。

来源：[analysis_summary.csv](bulk/analysis_summary.csv)、[comparisons.csv](bulk/comparisons.csv)、[overlap_all_three.csv](bulk/overlap_all_three.csv)。完整结果表与显著子集经独立回读核对 FDR 选择。

PBMC 输入 2,700 细胞×32,738 基因，gene min.cells=3；严格 QC 为 200<检测基因数<2500、线粒体比例<5%。两路线保留 2,638 细胞×13,714 基因。Seurat：LogNormalize 10000、vst 2000 HVG、PC1:10、k20 SNN、Louvain resolution=.5；Scanpy：总量归一化 10000、seurat dispersion HVG、回归 total_counts/MT%、40 PC、k10 fuzzy graph、Leiden resolution=1。随机种子42，计算线程2，工作流 cores4、mem_mb14000。完整方法见路线 `method.txt`；诊断变体保持独立，没有改主结果。

| 路线 | 原始细胞 | QC后细胞 | 实际簇数 |
|---|---:|---:|---:|
| seurat | 2700 | 2638 | 9 |
| scanpy | 2700 | 2638 | 9 |

按条形码共有 2638 个细胞。独立重算 ARI=0.627931073463、NMI(arithmetic)=0.754504783439。

来源：[analysis_summary.csv](pbmc3k/analysis_summary.csv)、[comparison_metrics.json](pbmc3k/comparison_metrics.json)、[独立检查](verification/checks.json)、[RDS回读](verification/rds_readback.json)。

补充诊断：Scrublet flag 36/2700（主QC内34，未据此删细胞）；独立缩减参考 holdout accuracy=0.842857142857、macro-F1=0.834772492008。这些诊断不构成细胞类型实验真值。来源：[validation_summary.json](pbmc_validation/validation_summary.json)。

## 命令与退出状态

以下命令均从项目根目录执行。记录器为 `python3 /home/a/projects/biolearn-practice/results/reproduction/acceptance-20261010T234118Z/evidence/run_logged.py <label> <命令>`；原始 argv、起止 UTC、工作目录、退出码和日志路径见 [commands.jsonl](evidence/commands.jsonl)。

| 命令记录 | 退出状态 | 执行日志 |
|---|---:|---|
| environment | 0 | [environment.log](evidence/environment.log) |
| nfcore-readonly | 0 | [nfcore-readonly.log](evidence/nfcore-readonly.log) |
| readme-verification | 0 | [readme-verification.log](evidence/readme-verification.log) |
| independent-readback | 0 | [independent-readback.log](evidence/independent-readback.log) |
| matrix-initial | 0 | [matrix-initial.log](evidence/matrix-initial.log) |
| all-products-initial | 0 | [all-products-initial.log](evidence/all-products-initial.log) |
| rebuild-dry-run | 0 | [rebuild-dry-run.log](evidence/rebuild-dry-run.log) |
| matrix-rebuild | 0 | [matrix-rebuild.log](evidence/matrix-rebuild.log) |
| rebuild-proof | 0 | [rebuild-proof.log](evidence/rebuild-proof.log) |
| final-dry-run | 0 | [final-dry-run.log](evidence/final-dry-run.log) |
| readme-verification-final | 0 | [readme-verification-final.log](evidence/readme-verification-final.log) |
| preservation | 0 | [preservation.log](evidence/preservation.log) |
| all-products-final | 0 | [all-products-final.log](evidence/all-products-final.log) |
| independent-readback-final | 0 | [independent-readback-final.log](evidence/independent-readback-final.log) |

`environment`：

```bash
python3 results/reproduction/acceptance-20261010T234118Z/evidence/environment_check.py
```

`nfcore-readonly`：

```bash
/home/a/miniforge3/bin/conda run --no-capture-output -n biolearn-py python results/reproduction/acceptance-20261010T234118Z/evidence/check_nfcore.py
```

`readme-verification`：

```bash
/home/a/miniforge3/bin/conda run --no-capture-output -n biolearn-py python scripts/verify_reproduction.py results/reproduction/acceptance-20261010T234118Z
```

`independent-readback`：

```bash
/home/a/miniforge3/bin/conda run --no-capture-output -n biolearn-py python scripts/verify_followup.py results/reproduction/acceptance-20261010T234118Z
```

`matrix-initial`：

```bash
/home/a/miniforge3/bin/conda run --no-capture-output -n biolearn-workflow snakemake --cores 4 --resources mem_mb=14000 --config output_root=results/reproduction/acceptance-20261010T234118Z
```

`all-products-initial`：

```bash
/home/a/miniforge3/bin/conda run --no-capture-output -n biolearn-py python results/reproduction/acceptance-20261010T234118Z/evidence/check_all_products.py
```

`rebuild-dry-run`：

```bash
/home/a/miniforge3/bin/conda run --no-capture-output -n biolearn-workflow snakemake --dry-run --cores 4 --resources mem_mb=14000 --config output_root=results/reproduction/acceptance-20261010T234118Z
```

`matrix-rebuild`：

```bash
/home/a/miniforge3/bin/conda run --no-capture-output -n biolearn-workflow snakemake --cores 4 --resources mem_mb=14000 --config output_root=results/reproduction/acceptance-20261010T234118Z
```

`rebuild-proof`：

```bash
/home/a/miniforge3/bin/conda run --no-capture-output -n biolearn-py python results/reproduction/acceptance-20261010T234118Z/evidence/check_rebuild.py
```

`final-dry-run`：

```bash
/home/a/miniforge3/bin/conda run --no-capture-output -n biolearn-workflow snakemake --dry-run --cores 4 --resources mem_mb=14000 --config output_root=results/reproduction/acceptance-20261010T234118Z
```

`readme-verification-final`：

```bash
/home/a/miniforge3/bin/conda run --no-capture-output -n biolearn-py python scripts/verify_reproduction.py results/reproduction/acceptance-20261010T234118Z
```

`preservation`：

```bash
python3 results/reproduction/acceptance-20261010T234118Z/evidence/check_preservation.py
```

`all-products-final`：

```bash
/home/a/miniforge3/bin/conda run --no-capture-output -n biolearn-py python results/reproduction/acceptance-20261010T234118Z/evidence/check_all_products.py
```

`independent-readback-final`：

```bash
/home/a/miniforge3/bin/conda run --no-capture-output -n biolearn-py python scripts/verify_followup.py results/reproduction/acceptance-20261010T234118Z
```

矩阵两条主路线的各 R/Python 分析、注释、报告进程均 exit0；补充诊断路线各阶段也均 exit0。四条路线 `run-provenance.json` 保存精确命令和各阶段状态，缺图重跑的原 bulk 留在本次目录 `history/`，初次 attempt 留在 `.attempts/`。

## 回读、统计一致性与缺图重建

- 初次 README 对照 16/16，独立检查 158/158；最终对照 16/16，独立检查 158/158。关键表按 rtol=1e-8、atol=1e-10 与历史实测比较；条形码/QC/聚类及 ARI/NMI 亦核对一致。
- 最终 217/217 个声明产物存在、非空且可读取；连同附加文件 232/232 全部可读取。CSV/JSON/YAML解析、PNG完整解码、5个H5AD实际打开、3个RDS以R readRDS打开、Matrix Market图矩阵读取；全部四个发布 manifest 校验通过。证据：[全部文件回读](evidence/all-products-readback.json)、[对象回读](verification/objects_readback.json)、[RDS回读](verification/rds_readback.json)。
- 补充诊断内部独立验收18/18与4个图变体检查通过，见 `pbmc_validation/verification/checks.json` 与 `pbmc_graph/verification.json`。
- 将本次新生成 `bulk/pca.png` 移至 [保留的原图](evidence/moved/pca.png)，确认源路径不存在；没有删除原图。移走操作、时间与原图SHA见 [rebuild-before.json](evidence/rebuild-before.json)。
- 缺图 dry-run 明确列出 bulk_matrix；实际再次运行工作流 exit0，产生新的 bulk attempt，成功重建并解码 PCA 图片。该规则重跑完整 bulk 分析；PBMC 与补充诊断没有重跑。
- 原图与重建图 SHA-256 完全一致：`041bf3aeb9392171130834b9319e85310fd12732b0d08562d24be5f851b84ca9`。5张主要bulk统计/结果表字节一致；其余三路线157文件的SHA均未变化。证据：[重建证明](evidence/rebuild-proof.json)、[重跑日志](evidence/matrix-rebuild.log)。
- 最终 Snakemake dry-run exit0且显示 `Nothing to be done`，全部目标齐备。证据：[final-dry-run.log](evidence/final-dry-run.log)。
- 开始前记录的历史 results 文件 7790 个全部保持SHA一致；复用的11个输入/锁文件也未变化。证据：[保护检查](evidence/preservation-check.json)、[历史基线清单](evidence/historical-results-before.json)。

## nf-core 官方小型测试的独立状态

本轮没有重新执行 nf-core 流程；本轮状态为**既有成功测试的只读复核 PASS**，不能写为本次矩阵干净目录重新完成官方流程。既有独立测试目录为 `results/nfcore/rnaseq-3.27.0-attempt-2/`，固定rnaseq3.27.0/commit `a1fcdddd3b826fe46eb46f0479f2ff8a7815af05`、Nextflow25.10.4、Java21、test,docker。
本次实际读取完成状态与exit-code、trace及234个task .exitcode，均成功；1053个官方输出重新计算SHA并与原manifest匹配，MultiQC HTML可读取。历史独立验收报告267/267通过，仅作为历史证据引用。
本次命令及退出0见上表 nfcore-readonly；复核细节见 [nfcore-status.json](evidence/nfcore-status.json)，原验收/对象/文档证据位于 `results/nfcore/rnaseq-3.27.0-attempt-2/verification/`。官方测试是独立小型数据集，airway 原始FASTQ完整流程未验证。

## 边界与后续

本轮无未解决阻塞。日志中保留 PyDESeq2 自由度警告、稀疏矩阵中心化提示以及零表达 marker 的统计警告；其结果/允许NA/数值范围由独立检查核验，没有隐去日志或改变验收阈值。方法间结果差异按实际记录，不把相同簇数当作生物学正确性。跨主机新环境复现与蛋白实验验证仍未执行。后续输入/脚本变化按Snakemake依赖重跑；未推送GitHub、未修改系统代理、未删除历史资料。
