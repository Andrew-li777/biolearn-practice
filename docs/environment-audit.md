# Linux 环境审计

检查时间：2026-10-10T19:53:03.747769+00:00。项目：`/home/a/projects/biolearn-practice`。

本次重新检查当前状态，未安装或更新软件。上次审计已保留在 `environment/audit/environment-audit.previous.md`。分析前已读取本地参考材料；这些材料不纳入公开仓库。

文档中的代码、勾选、版本与参考数字均是待核实参考，不作为本机证据。此前安装记录与本次新检查分开：以下包加载、路径和网络结论来自本次执行。

## 1. 当前结论

已有 `/home/a/miniforge3` 及独立 `biolearn-r` / `biolearn-py` 环境，核心包加载通过，可以复用。当前 shell 未激活这些环境，R、Conda/Mamba 不在 PATH，不应误判为未安装。Docker、Java、Nextflow、Snakemake 在本次范围内未发现。七个网络目标 HTTPS HEAD 均返回 200，TLS 校验通过。

## 2. 系统与资源

| 项目 | 实测结果 |
| --- | --- |
| 发行版 | Ubuntu 24.04.5 LTS，Noble，x86_64 |
| 用户 | a，UID/GID 1000；属于 sudo 组，但没有执行 sudo |
| CPU | 4 个在线逻辑 CPU，Intel Core i5-11400H @ 2.70GHz；VMware 虚拟机，虚拟拓扑不代表宿主物理资源 |
| 内存 | 总计 15.57 GiB；检查时可用 14.64 GiB |
| Swap | 4 GiB，当前使用 0 |
| 项目文件系统 | ext4；48 GiB 总量，14 GiB 已用，32 GiB 可用，31% 使用率 |

容量和内存是快照，不保证后续运行峰值；本次没有运行完整分析或构建参考基因组。

## 3. 软件路径与版本

| 工具 | 当前 PATH | 已发现可执行路径 / 版本 | 分类 |
| --- | --- | --- | --- |
| R | 无 | `/home/a/miniforge3/envs/biolearn-r/bin/R`：R version 4.4.3 (2025-02-28) -- "Trophy Case"（exit=0） | 已安装，未在当前 PATH |
| Rscript | 无 | `/home/a/miniforge3/envs/biolearn-r/bin/Rscript`：Rscript (R) version 4.4.3 (2025-02-28)（exit=0） | 已安装，未在当前 PATH |
| python | 无 | `/home/a/miniforge3/bin/python`：Python 3.14.7（exit=0）<br>`/home/a/miniforge3/envs/biolearn-r/bin/python`：Python 3.15.0（exit=0）<br>`/home/a/miniforge3/envs/biolearn-py/bin/python`：Python 3.11.17（exit=0） | 已安装，未在当前 PATH |
| python3 | /usr/bin/python3 | `/usr/bin/python3`：Python 3.12.3（exit=0）<br>`/home/a/miniforge3/bin/python3`：Python 3.14.7（exit=0）<br>`/home/a/miniforge3/envs/biolearn-r/bin/python3`：Python 3.15.0（exit=0）<br>`/home/a/miniforge3/envs/biolearn-py/bin/python3`：Python 3.11.17（exit=0） | 可运行 |
| conda | 无 | `/home/a/miniforge3/bin/conda`：conda 26.7.2（exit=0） | 已安装，未在当前 PATH |
| mamba | 无 | `/home/a/miniforge3/bin/mamba`：2.9.0（exit=0） | 已安装，未在当前 PATH |
| git | /usr/bin/git | `/usr/bin/git`：git version 2.43.0（exit=0） | 可运行 |
| docker | 无 | 未发现 | 缺失（检查范围内） |
| java | 无 | 未发现 | 缺失（检查范围内） |
| nextflow | 无 | 未发现 | 缺失（检查范围内） |
| snakemake | 无 | 未发现 | 缺失（检查范围内） |

补充扫描 `/home/a`、`/opt`、`/usr/local` 至六层，排除 Codex 插件与 node_modules，未发现 Docker、Java、Nextflow、Snakemake；扫描没有权限错误。结合常见入口和 dpkg 查询判断“检查范围内缺失”，没有扫描其他用户目录或全部文件系统。证据：`extra-tool-paths.txt`、`extra-tool-scan-errors.log`、`system-packages.log`，均位于 `environment/audit/`。

Docker CLI 未发现，因此引擎状态为**未核实**；没有执行 `docker info`、容器运行或拉取镜像。不能把 CLI 缺失直接等同于所有远端 Docker 服务不存在。

## 4. 已有环境与实际包加载

| 环境 | 路径 | 用途及结果 |
| --- | --- | --- |
| base | `/home/a/miniforge3` | Python 3.14.7；检查的分析模块缺失，不作为分析环境 |
| biolearn-r | `/home/a/miniforge3/envs/biolearn-r` | R 4.4.3；R 核心包通过。环境附带 Python 3.15.0，仅为传递依赖，不用于项目 Python 分析 |
| biolearn-py | `/home/a/miniforge3/envs/biolearn-py` | Python 3.11.17；Python 核心包通过 |
| 系统 Python | `/usr/bin/python3` | 3.12.3；检查的分析模块均缺失，未覆盖或修改 |

Conda 登记的环境只有 base 和上述两个隔离环境；不排除未登记或检查范围外的环境。

### R 环境

| 包 | 状态 | 实际版本 |
| --- | --- | --- |
| DESeq2 | library() 通过 | 1.46.0 |
| edgeR | library() 通过 | 4.4.0 |
| airway | library() 通过 | 1.26.0 |
| Seurat | library() 通过 | 5.5.1 |
| apeglm | library() 通过 | 1.28.0 |
| AnnotationDbi | library() 通过 | 1.68.0 |
| org.Hs.eg.db | library() 通过 | 3.20.0 |
| SummarizedExperiment | library() 通过 | 1.36.0 |
| ggplot2 | library() 通过 | 4.0.3 |
| ggrepel | library() 通过 | 0.9.8 |
| pheatmap | library() 通过 | 1.0.13 |
| dplyr | library() 通过 | 1.2.1 |
| clusterProfiler | MISSING | — |
| tidyverse | MISSING | — |

### Python 分析环境

| 模块 | 状态 | distribution 元数据版本 |
| --- | --- | --- |
| numpy | import 通过 | 2.4.6 |
| scipy | import 通过 | 1.17.1 |
| pandas | import 通过 | 2.3.3 |
| matplotlib | import 通过 | 3.11.2 |
| seaborn | import 通过 | 0.13.2 |
| sklearn | import 通过 | 1.9.1 |
| scanpy | import 通过 | 1.11.5 |
| anndata | import 通过 | 0.12.19 |
| igraph | import 通过 | 1.0.0 |
| leidenalg | import 通过 | 0.12.0 |
| pydeseq2 | import 通过 | 0.5.4 |
| h5py | import 通过 | 3.16.0 |
| statsmodels | import 通过 | 0.15.0 |
| umap | import 通过 | 0.5.12 |
| skmisc | import 通过 | 0.0.0 |
| snakemake | MISSING | — |
| jupyterlab | import 通过 | 4.6.4 |

`skmisc` 的 distribution 元数据报告 0.0.0，Conda 实际包版本为 scikit-misc 0.5.3；两者分别记录，不把元数据当作仓库版本。`clusterProfiler` 是可选 GO 富集包；完整 tidyverse、Snakemake 不属于当前核心分析范围，不补装。JupyterLab 因环境依赖已存在，不是本次安装。

加载使用已有环境的实际 Rscript/Python，通过 `conda run` 或绝对路径执行；没有只用 find_spec 判定通过。R 库路径为隔离环境内的 `lib/R/library`。完整 R 包版本和 Built 信息见 `environment/audit/r-installed-packages.csv`；运行时信息见 `r-load.log`。Python 解释器与导入记录见 `python-load.log`；系统、base、R 附带 Python 分别见对应 `*-python-load.log`。

全量 Conda 依赖（含 build、channel、传递依赖）重新导出到 `environment/audit/biolearn-{r,py}.packages.json`、`.resolved.yml` 与 `.linux-64.explicit.txt`。这些是本次读取现有环境产生的快照。

## 5. 网络连通性

继承当前代理环境，未修改设置，未输出代理值、密码或令牌。测试使用 `curl -I -L -sS --connect-timeout 5 --max-time 20`，正常 TLS 校验，只请求响应头；未下载软件或 PBMC3k 数据正文，未测试绕过代理的直连。

| 目标 | HTTPS 请求地址 | curl exit | 最终 HTTP | TLS verify result | 用时（s） |
| --- | --- | --- | --- | --- | --- |
| GitHub | https://github.com/conda-forge/miniforge/releases/latest | 0 | 200 | 0 | 1.924132 |
| conda-forge | https://conda.anaconda.org/conda-forge/linux-64/repodata.json | 0 | 200 | 0 | 1.055368 |
| bioconda | https://conda.anaconda.org/bioconda/linux-64/repodata.json | 0 | 200 | 0 | 1.027568 |
| CRAN | https://cloud.r-project.org/ | 0 | 200 | 0 | 1.244868 |
| Bioconductor | https://bioconductor.org/packages/release/bioc/ | 0 | 200 | 0 | 1.235890 |
| PyPI | https://pypi.org/simple/scanpy/ | 0 | 200 | 0 | 1.240141 |
| PBMC3k | https://cf.10xgenomics.com/samples/cell/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz | 0 | 200 | 0 | 1.049034 |

HTTP 200 表示这些地址本次 HEAD 连通；不保证每个实际包、Git clone、release 二进制资产、完整大文件下载或所有仓库子地址可用。Git 实际克隆、容器仓库与 nf-core 流程拉取未核实。网络原始结构化证据见 `environment/audit/host-network.json`，未保留可能含敏感信息的响应头和 curl 错误全文。

## 6. 状态分类与边界

| 分类 | 判定 | 本次结果 |
| --- | --- | --- |
| 缺失 | 指定解释器中模块/包不存在，或工具在已说明扫描范围内未发现 | 可选 R 包、Snakemake；Docker/Java/Nextflow；系统与 base 的分析模块 |
| 已安装但未加入 PATH | 实际找到可执行文件并成功查询版本，当前 PATH 无入口 | R/Rscript、Conda/Mamba、各环境的 python |
| 加载失败 | 已发现包但实际 library()/import 报错 | 本次未发现核心包加载失败 |
| 网络失败 | 请求非零退出、超时、TLS 错误或 HTTP 失败 | 本次七个目标均未发生 |
| 未核实 | 没有执行对应验证，或证据不足 | Docker 引擎、远端 Docker 服务、完整下载/clone、完整三套 airway 分析及其差异表、真实单细胞注释/跨工具比较、nf-core 官方测试 |

本轮仅做环境准备与加载验收，没有重新运行此前的计算 smoke test。已有 `environment/logs/verify-*.log` 和图表属于前一轮安装验收，详见 `docs/environment-installation.md`，不能将其视为两份参考文档全部代码已验证。参考显著基因数、细胞数与簇数没有在本轮作为验收输入。

审计脚本保存在 `environment/audit/check-host.py`、`check-r.R`、`check-python.py`；未安装、更新软件，未修改代理或系统运行时，未推送 GitHub，未删除已有资料。
