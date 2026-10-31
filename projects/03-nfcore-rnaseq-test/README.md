# nf-core/rnaseq 官方小型测试

[返回项目总览](../../README.md)

## 分析目标

验证固定版本 nf-core/rnaseq 官方小型流程，从输入到结果回读；与 airway 矩阵分析独立。

## 输入

nf-core/rnaseq 3.27.0，提交 `a1fcdddd3b826fe46eb46f0479f2ff8a7815af05`，Nextflow 25.10.4、Java 21，使用 `test,docker` 官方测试配置。

## 环境与执行

在子项目根目录执行（需要 Docker 及 biolearn-workflow 环境）：

```bash
PATH="$PWD/scripts/container-client:$PATH" bash scripts/check_container.sh environment/nfcore/new-container-check
PATH="$PWD/scripts/container-client:$PATH" bash scripts/run_nfcore_test.sh results/nfcore/my-new-attempt
```

历史 work 中的绝对路径属于旧环境，不作为可移植缓存；新运行使用新的 work 目录。

新机器可从官方仓库获取固定版本：`git clone --depth 1 --branch 3.27.0 https://github.com/nf-core/rnaseq.git workflow/nfcore-rnaseq-3.27.0`，脚本会核验提交。将 conda 加入 PATH 或设置 `BIOLEARN_CONDA`；使用提供的 Docker wrapper 时需要 PATH 中有 skopeo，或设置 `BIOLEARN_CONTAINER_PREFIX` 指向其隔离环境。Nextflow、Java、Docker 和网络需要预先可用。

独立结果验收需 `biolearn-py` 环境（锁文件在 `environment/`）：

```bash
conda create -n biolearn-py --file environment/biolearn-py.linux-64.explicit.txt
conda run --no-capture-output -n biolearn-py python scripts/verify_nfcore.py results/nfcore/my-new-attempt
```

## 实际结果

<!-- BEGIN VERIFIED RESULTS -->

本机验证日期：2026-10-30。运行及独立验收 PASS；版本提交 a1fcdddd3b826fe46eb46f0479f2ff8a7815af05。

| 版本 | 退出码 | 完成任务 / 总任务 | 独立验收通过 / 总项 |
| --- | --- | --- | --- |
| 3.27.0 | 0 | 234/234 | 267/267 |

test,docker 官方小型测试；不是 airway 原始 FASTQ 的完整复现。任务与验收统计用于展示流程结果。

结果来源（本地运行产物，未随 Git 发布）：

- `results/nfcore/new-attempt/verification/summary.json`
- `results/nfcore/new-attempt/completion-status.json`

图表与来源校验值保存在受版本控制的结果摘要中。

## 结果展示

本项目以上方任务完成与验收统计表展示流程结果；完整 MultiQC 为本地产物。

<!-- END VERIFIED RESULTS -->

## 验收与局限

2026-10-30 的本地 `results/nfcore/new-attempt/` 已完成运行与独立验收，命令日志为 `run.log`、`verify.log`。更早的容器迁移预检仅验证容器条件，不代表完整流程；2026-10-31 本轮只改文档。

MultiQC 报告位于本地 `results/nfcore/new-attempt/output/multiqc/star_salmon/multiqc_report.html`，未随 Git 发布。此官方小型测试不是 airway 原始 FASTQ 的完整复现；跨主机重建尚未验证。

## 相关文档

[测试说明](docs/nfcore-test.md) · [全项目进度](../../docs/progress.md)
