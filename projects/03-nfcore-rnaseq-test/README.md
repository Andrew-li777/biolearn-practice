# nf-core/rnaseq 官方小型测试

历史测试 `results/nfcore/rnaseq-3.27.0-attempt-2/` 使用 nf-core/rnaseq 3.27.0、提交 `a1fcdddd3b826fe46eb46f0479f2ff8a7815af05`、Nextflow 25.10.4、Java 21、test,docker；历史验收 267/267，234 任务完成。官方测试不等于 airway FASTQ 复现。查看 [测试说明](docs/nfcore-test.md)。

在子项目根目录执行（需要 Docker 及 biolearn-workflow 环境）：

```bash
PATH="$PWD/scripts/container-client:$PATH" bash scripts/check_container.sh environment/nfcore/new-container-check
PATH="$PWD/scripts/container-client:$PATH" bash scripts/run_nfcore_test.sh results/nfcore/my-new-attempt
```

历史 work 中的绝对路径属于旧环境，不作为可移植缓存；新运行使用新的 work 目录。

## 拆分后本机验证

2026-10-30 新运行 `results/nfcore/new-attempt/` 退出 0，trace 234/234 COMPLETED；`verification/summary.json` 独立验收 267/267，MultiQC 与输出回读通过。命令日志为 `run.log` 和 `verify.log`。此运行仍为官方小型测试。

新机器可从官方仓库获取固定版本：`git clone --depth 1 --branch 3.27.0 https://github.com/nf-core/rnaseq.git workflow/nfcore-rnaseq-3.27.0`，脚本会核验提交。将 conda 加入 PATH 或设置 `BIOLEARN_CONDA`；使用提供的 Docker wrapper 时需要 PATH 中有 skopeo，或设置 `BIOLEARN_CONTAINER_PREFIX` 指向其隔离环境。Nextflow、Java、Docker 和网络需要预先可用。

独立结果验收需 `biolearn-py` 环境（锁文件在 `environment/`）：

```bash
conda create -n biolearn-py --file environment/biolearn-py.linux-64.explicit.txt
conda run --no-capture-output -n biolearn-py python scripts/verify_nfcore.py results/nfcore/my-new-attempt
```

迁移后容器预检通过，状态在 `environment/nfcore/migration-container-check/status.txt`。未为本次目录调整重新运行完整 nf-core 流程。
