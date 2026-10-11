# RNA-seq 与 PBMC3k 实际复现项目

本项目已验证 airway **现成计数矩阵**的 DESeq2、edgeR、PyDESeq2，以及同一 PBMC3k 已过滤 UMI 数据的 Seurat、Scanpy 分析。`docs/` 的学习文档是参考材料；验收数字读取实际产物，不为匹配参考数字调参。

nf-core/rnaseq 官方小型测试单独运行和验收，不能描述为 airway 原始 FASTQ 的完整复现。

## 复现矩阵分析

当前 Linux 环境使用用户目录 Miniforge，系统 R/Python 未被覆盖。完整依赖固定在 `environment/*.linux-64.explicit.txt`；相应 resolved YAML 和包版本 JSON 提供可读记录。新机器需先在用户目录安装 Miniforge，再恢复环境：

```bash
conda create -n biolearn-r --file environment/biolearn-r.linux-64.explicit.txt
conda create -n biolearn-py --file environment/biolearn-py.linux-64.explicit.txt
conda create -n biolearn-workflow --file environment/biolearn-workflow.linux-64.explicit.txt
```

新增doublet和参考诊断使用独立venv继承已验证Python，不改主环境：

```bash
conda run -n biolearn-py python -m venv --system-site-packages environment/validation-venv
environment/validation-venv/bin/python -m pip install -r environment/validation-extra-requirements.txt
```

工作目录须为项目根目录。若 Miniforge 路径不同，用 `--config conda=/实际路径/bin/conda`；验证解释器可用 `validation_python=/实际venv/bin/python` 配置。同名已有环境先按环境审计验证兼容性；不要覆盖系统环境。

输入 airway 来自固定 R 包；PBMC3k 下载来源和 SHA-256 记录在各轮 `pbmc3k/data_source.json`。若本地缺少 PBMC 数据：

```bash
mkdir -p data/pbmc3k
curl -fL https://cf.10xgenomics.com/samples/cell/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz -o data/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz
echo '847d6ebd9a1ec9a768f2be7e40ca42cbfe75ebeb6d76a4c24167041699dc28b5  data/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz' | sha256sum -c -
tar -xzf data/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz -C data/pbmc3k
```

使用一个新的输出目录运行完整矩阵工作流：

```bash
conda run --no-capture-output -n biolearn-workflow snakemake --cores 4 --resources mem_mb=14000 --config output_root=results/reproduction/my-run
conda run --no-capture-output -n biolearn-py python scripts/verify_reproduction.py results/reproduction/my-run
```

`Snakefile` 显式跟踪主矩阵166产物及`workflow/diagnostic-outputs.json`中51个补充诊断产物（共217）。PBMC变化会触发依赖它的doublet、参考映射、图诊断。运行使用独立attempt，验收成功后发布，失败及旧资料保留。两条矩阵规则内部按已验证阶段顺序执行；缺失一张图会重跑对应路线的完整矩阵分析。这种粒度较粗，能保证依赖一致，但不会只重绘一张图。随机种子固定为 42；并行线程为 2。参数与方法差异见 [bulk 方法](docs/bulk-methods.md) 和 [PBMC3k 方法](docs/pbmc3k-methods.md)。

## 实际结果对照

以下数字已在新目录`results/reproduction/followup-20261010/`完整重跑；原历史目录保留。当前核验见[verification-report.md](docs/verification-report.md)。

| 分析 | 实际输入/过滤 | 实际结果 |
|---|---|---|
| DESeq2 | 63,677 基因、8 样本；预过滤 16,596 | FDR<0.1：4,916 |
| edgeR | 同一输入；filterByExpr 16,860 | FDR<0.1：6,550 |
| PyDESeq2 | 同一输入；预过滤 16,596 | FDR<0.1：4,685 |
| Seurat | 2,700 → 2,638 细胞，13,714 基因 | 9 簇、2,000 HVG |
| Scanpy | 同一输入；同样保留 2,638 细胞 | 9 簇、1,838 HVG |

三种 bulk 方法共同显著基因 4,611；DESeq2/PyDESeq2 的显著集合 Jaccard 为 0.935685。单细胞按条形码共有 2,638 个细胞，两侧独有均为 0；ARI=0.627931、NMI=0.754505。簇数不是验收目标，注释也不是独立生物学真值。完整对照、方向一致性、列联表及各项检查在各输出目录的 `acceptance.md` 和 CSV/JSON 中。

新干净目录已完成：bulk39/39、PBMC3k83/83；对照验收16/16、扩大核验158/158、补充诊断18/18及4图变体通过。217产物/输入元数据核验及最终dry-run通过。历史干净运行曾做缺图重建：删除新生成的 `bulk/pca.png` 后自动重建，SHA-256 与原图一致；最终 dry-run 无待执行任务。证据见 `logs/rebuild-proof/evidence.json`、`logs/snakemake-rebuild.log`。

## nf-core/rnaseq 独立测试

固定版本 rnaseq 3.27.0，提交 `a1fcdddd3b826fe46eb46f0479f2ff8a7815af05`，Nextflow 25.10.4，Java 21。仓库位于 `workflow/nfcore-rnaseq-3.27.0`；新机器可用 `git clone --depth 1 --branch 3.27.0 https://github.com/nf-core/rnaseq.git workflow/nfcore-rnaseq-3.27.0` 获取，运行脚本会核对提交。

```bash
sg docker -c 'PATH="$PWD/scripts/container-client:$PATH" bash scripts/check_container.sh environment/nfcore/new-container-check'
sg docker -c 'PATH="$PWD/scripts/container-client:$PATH" bash scripts/run_nfcore_test.sh results/nfcore/new-attempt'
```

历史attempt-1退出1（Docker缺失），完整保留。Docker现已可用，容器DNS/HTTPS预检PASS；attempt-2已经退出0，234/234任务成功，267/267独立核验通过；8序列化文件、5BAM、128PDF/132页和MultiQC实际回读。RGB展示兼容修复单独保存在`presentation-corrected-4/`，科学数据与官方报告完全一致。最新状态见[核验报告](docs/verification-report.md)。

该命令需要可用的 Docker 引擎；运行前执行 `scripts/check_container.sh` 验证容器拉取、运行和网络。实际完成状态读取 `completion-status.json`，不能根据脚本存在、开始启动或参考文档勾选判定成功。资源、网络与阻塞记录见 [官方测试记录](docs/nfcore-test.md)。

## 局限与进度

- bulk 输入已是计数矩阵，未验证原始 reads 的质控、比对和计数。
- PBMC输入已过滤，不含空液滴。Scrublet已诊断36/2700疑似doublet（主QC内34）；未据此删除细胞。独立缩减参考映射约80%–81%一致，缺少部分关键marker/platelet参考类，marker注释仍为推定，实验真值未取得。
- 两条单细胞路线的 HVG、回归、PCA、邻居图和聚类实现不同；控制实验能证明部分参数敏感性，不能将全部差异归因于一个因素。
- 同版本环境内数值复现可以核对；跨平台、软件版本或线程库变化不能承诺所有图像字节及数值完全相同。固定的簇注释计划需核对数据校验和、簇标签及 marker 支持；变化时会停止要求重新审阅。
- 完整人类参考基因组不在项目范围；不自动推送 GitHub，不更改系统代理，不删除旧分析资料。

持续记录见 [docs/progress.md](docs/progress.md)。
