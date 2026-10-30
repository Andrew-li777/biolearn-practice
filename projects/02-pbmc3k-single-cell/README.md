# PBMC3k 单细胞分析

输入 `data/pbmc3k/` 是已过滤 UMI 数据；归档 SHA-256 为 `847d6ebd9a1ec9a768f2be7e40ca42cbfe75ebeb6d76a4c24167041699dc28b5`。历史干净验收目录 `results/reproduction/acceptance-20261010T234118Z/` 中两路线均保留 2638/2700 细胞、各 9 簇，ARI 0.627931，NMI 0.754505。细胞类型是 marker 支持的推定注释，非实验真值；见 [方法说明](docs/pbmc3k-methods.md)。

## 输入准备

如数据尚未保存到本地，从 10x 获取并校验后解压：

```bash
mkdir -p data/pbmc3k
curl -fL https://cf.10xgenomics.com/samples/cell/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz -o data/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz
echo '847d6ebd9a1ec9a768f2be7e40ca42cbfe75ebeb6d76a4c24167041699dc28b5  data/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz' | sha256sum -c -
tar -xzf data/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz -C data/pbmc3k
```

## 环境与执行

在子项目根目录执行。先将 Miniforge 的 `bin` 加入 PATH，或在 Snakemake 命令中使用 `--config conda=/实际路径/bin/conda`。根据 `environment/` 中的 explicit 锁文件恢复或验证 `biolearn-r`、`biolearn-py`、`biolearn-workflow` 三个隔离环境，Linux 平台依赖与构建版本应与锁文件一致。

```bash
conda create -n biolearn-r --file environment/biolearn-r.linux-64.explicit.txt
conda create -n biolearn-py --file environment/biolearn-py.linux-64.explicit.txt
conda create -n biolearn-workflow --file environment/biolearn-workflow.linux-64.explicit.txt
```

PBMC 诊断使用本子项目独立 venv：

```bash
conda run -n biolearn-py python -m venv --system-site-packages environment/validation-venv
environment/validation-venv/bin/python -m pip install -r environment/validation-extra-requirements.txt
```

新运行使用新的输出目录，避免重写历史结果：

```bash
conda run --no-capture-output -n biolearn-workflow snakemake --cores 4 --resources mem_mb=14000 --config output_root=results/my-new-run
```

结果中的历史路径来自之前的运行记录；跨主机环境重建尚未验证。

## 拆分后本机验证

本次拆分后的新运行 `results/new-run/pbmc3k/acceptance.md` 于 2026-10-30 PASS 83/83；诊断 18/18、图变体 4/4 通过。RDS/H5AD 回读记录见 `rds-readback.log` 和 `object-readback.log`；最终 dry-run 无待执行任务。

迁移后的本机补充验证：新建的本地 validation-venv 成功执行 PBMC 诊断，18/18 项通过；输出 `results/migration-check/pbmc_validation/`，记录 `migration-diagnostic.log`。这是既有主分析结果上的诊断重跑。
