# airway bulk 差异表达

输入是 airway 包现成计数矩阵，8 个样本，设计 `~ cell + dex`、trt 对 untrt、FDR<0.1。历史干净验收目录 `results/reproduction/acceptance-20261010T234118Z/bulk/` 的汇总表记录 DESeq2 4916、edgeR 6550、PyDESeq2 4685 个显著基因。方法和过滤差异见 [方法说明](docs/bulk-methods.md)。不是原始 FASTQ 流程。

## 环境与执行

在子项目根目录执行。先将 Miniforge 的 `bin` 加入 PATH，或在 Snakemake 命令中使用 `--config conda=/实际路径/bin/conda`。根据 `environment/` 中的 explicit 锁文件恢复或验证 `biolearn-r`、`biolearn-py`、`biolearn-workflow` 三个隔离环境，Linux 平台依赖与构建版本应与锁文件一致。

```bash
conda create -n biolearn-r --file environment/biolearn-r.linux-64.explicit.txt
conda create -n biolearn-py --file environment/biolearn-py.linux-64.explicit.txt
conda create -n biolearn-workflow --file environment/biolearn-workflow.linux-64.explicit.txt
```

新运行使用新的输出目录，避免重写历史结果：

```bash
conda run --no-capture-output -n biolearn-workflow snakemake --cores 4 --resources mem_mb=14000 --config output_root=results/my-new-run
```

结果中的历史路径来自之前的运行记录；跨主机环境重建尚未验证。

## 拆分后本机验证

本次拆分后的新运行 `results/new-run/bulk/acceptance.md` 于 2026-10-30 PASS 39/39；各方法显著基因数分别为 4916、6550、4685。`run.log` 和 `final-dry-run.log` 记录执行与最终依赖检查。
