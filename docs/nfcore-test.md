# nf-core/rnaseq 官方测试：资源与运行核实

本任务是官方 `test` profile 的小型流程测试，**不是 airway 原始 FASTQ 的完整复现**。矩阵分析与流程测试分别验收。

## 当前更新（2026-10-10）

Docker29.1.3已安装并启动，`sg docker`可访问。直接daemon pull网络连接被拒绝；使用独立Skopeo1.24.1和项目客户端wrapper经既有代理导入精确镜像，未修改系统代理。`environment/nfcore/container-check-ready-20261010/status.txt`=PASS，容器DNS和curl HTTPS HTTP200/1335B。完整镜像源digest及复制日志在`environment/nfcore/image-imports-20261010/`。

`results/nfcore/rnaseq-3.27.0-attempt-2/`已完成PASS：退出0，234/234任务COMPLETED，独立267/267核验；5样本、125基因/126转录本，5BAM、8序列化文件、128PDF/132页实际读取，MultiQC71section/55图且页面错误0。移除schema无效的max_* params，保留process.resourceLimits和并发2。原报告RGB兼容WARN已用单独`presentation-corrected-4/`修复展示，36数据模块/14综合统计完全一致。详见该attempt的`verification/`和[核验报告](verification-report.md)。下方缺Docker描述均为首轮历史记录。

运行须使用新attempt目录，脚本拒绝覆盖已有尝试：

```bash
sg docker -c 'PATH="$PWD/scripts/container-client:$PATH" bash scripts/run_nfcore_test.sh results/nfcore/new-attempt'
```

最终验收除了退出0和递归查找MultiQC，还检查完整trace/work退出、两分支合并计数、样本/基因唯一、FastQC ZIP、MultiQC数据及原始下载清单，入口`scripts/verify_nfcore.py`。当前核验以[verification-report.md](verification-report.md)为准。

## 首轮历史记录

## 已核实

- VMware 虚拟机，Ubuntu 24.04.5，普通用户 a，4 个逻辑 CPU。
- 运行前约 14 GiB 可用内存，根盘约 32 GiB 可用空间；总内存约 15 GiB，交换分区 4 GiB。
- 用户隔离环境 `biolearn-workflow`：OpenJDK 21.0.10、Nextflow 25.10.4、Snakemake 9.13.4。Java/Nextflow 实际执行版本日志在 `environment/nfcore/`。
- 固定 rnaseq 3.27.0，提交 `a1fcdddd3b826fe46eb46f0479f2ff8a7815af05`。标签配置实际要求 Nextflow `!>=25.10.4`；环境满足该要求。
- 使用固定标签中的官方测试数据及分析参数，仅限制 CPU≤4、单任务内存≤12 GB、并发任务≤2。
- 主机访问 quay.io 和 Docker Registry 均得到 HTTP 401 认证挑战：网络端点可达，但这不证明容器拉取或容器内部网络已通过。
- 本机初检没有 Docker/Podman/Apptainer；`unshare -Ur true` 失败，系统 `apparmor_restrict_unprivileged_userns=1`。`sudo -n true` 失败，不能无交互安装系统服务。

## 实际运行结果

已实际启动固定版本的官方 `test,docker` 测试，目录 `results/nfcore/rnaseq-3.27.0-attempt-1`。流程退出码为 **1**；首个 `GUNZIP_GTF` 任务退出码 **127**，明确报 `.command.run: docker: command not found`。`completion-status.json` 保存 `completed=false` 和 `blocked_container_runtime_missing`；**没有生成 MultiQC**，不能记为测试成功。Nextflow 控制台、详细日志、执行 trace/report/timeline 已保存。

21 个官方测试输入地址均实际返回 HTTP 200；检查文件 `environment/nfcore/test-url-checks.json`。Java HTTPS 小型连接探针返回 HTTP 200。`scripts/check_container.sh` 当前退出 127，记录 `FAIL`；Docker 安装后该脚本会依次验证引擎、镜像拉取、运行、DNS 和 HTTPS，并保存镜像 digest。它仅继承现有客户端代理变量，不写代理配置。

## 首轮阻塞（历史，已解除）

容器引擎缺失；已请求用户在虚拟机终端安装、启动 Docker 并授权 a 用户。密码不应发送到对话。没有修改代理、系统 Python/R 或下载完整人类参考基因组。

## 复跑

```bash
scripts/run_nfcore_test.sh results/nfcore/rnaseq-3.27.0-test
```

安装 Docker 后，如果当前终端尚未取得 docker 组，可在新组会话执行：

```bash
sg docker -c 'scripts/check_container.sh environment/nfcore/container-check-ready'
sg docker -c 'scripts/run_nfcore_test.sh results/nfcore/rnaseq-3.27.0-test'
```

脚本核对提交，记录 `console.log`、`nextflow.log`、退出码和 `completion-status.json`；成功运行后保存 execution report/trace/timeline 和 `output/multiqc/multiqc_report.html`。退出码与 MultiQC 必须同时满足条件才记为完成。

依据：[固定版本文档](https://nf-co.re/rnaseq/3.27.0)、[固定版本配置](https://github.com/nf-core/rnaseq/blob/3.27.0/nextflow.config)、[Nextflow Java 支持范围](https://docs.seqera.io/nextflow/install)。
