# Linux 环境审计

检查时间：2026-10-10 19:36 UTC。项目：`/home/a/projects/biolearn-practice`。当前用户：`a`（UID 1000）。

本次仅检查并写入本报告，没有安装软件、创建分析环境、下载数据、运行分析或修改系统配置。已读取本地参考材料，重点核对环境、airway、Seurat、Scanpy 与对比脚本；这些材料不纳入公开仓库。

参考文档中的勾选项和“已测试”描述不作为本机已完成的证据；以下均为本次检查结果。

## 1. 结论

本机资源满足参考文档对 airway 与 PBMC3k 小数据分析的建议，但分析软件尚未就绪。Python 3 和 Git 可运行；未发现 R、Conda、Mamba 或 Micromamba；当前 Python 没有 pip 或目标分析包。依赖源和 PBMC3k 数据地址经现有代理的 HTTPS HEAD 请求全部成功。未测试不经代理的直连，也未验证软件安装、完整下载或实际分析。

## 2. 系统与资源

| 项目 | 实测结果 | 判断 |
| --- | --- | --- |
| 发行版 | Ubuntu 24.04.5 LTS，Noble Numbat，x86_64 | Linux 环境可用 |
| 内核 | 6.8.0-139-generic | 来自 `uname -a` |
| 虚拟化 | VMware，full virtualization | `lscpu` 报告 |
| CPU | 4 个在线逻辑 CPU；Intel Core i5-11400H @ 2.70GHz；虚拟拓扑 2 插槽 × 2 核 × 1 线程 | 适合小数据分析；虚拟拓扑不代表宿主物理资源 |
| 内存 | 总计约 15 GiB（约 16 GB 级）；可用约 14 GiB | 达到参考文档建议的 16 GB 级配置；实际峰值未测试 |
| Swap | 4 GiB，当前使用 0 | 可用 |
| 项目所在根文件系统 | ext4；`df -hT` 总计 48 GiB，已用 7.7 GiB，可用 38 GiB，使用率 17% | 超过文档建议保留的 20 GB |
| 根文件系统 inode | 3,211,264 个，总使用率 3% | 充足 |
| 虚拟磁盘 | `/dev/sda` 100 GiB；根逻辑卷 49 GiB，另有 2 GiB boot 分区 | 100 GiB 不是项目当前可用空间；未检查 LVM 可扩容量 |
| 宿主共享挂载 | `/mnt/hgfs`，vmhgfs-fuse，约 290 GiB 可用 | 项目不在此挂载；未验证共享盘写入与分析兼容性 |

资源数字为检查时快照，`lsblk` 与 `df` 分别反映块设备大小和文件系统容量，显示值略有差异。

## 3. 软件存在性与 PATH

| 软件或入口 | 结果 | 分类与证据 |
| --- | --- | --- |
| Python 3 | `/usr/bin/python3`，3.12.3，可执行 | 已安装、已加入 PATH |
| `python` | PATH 中无此命令，常见目录也未找到入口 | 命令入口缺失；不能据此说 Python 未安装，应使用已有 `python3` |
| Git | `/usr/bin/git`，2.43.0，可执行 | 已安装、已加入 PATH；dpkg 版本 `1:2.43.0-1ubuntu7.3` |
| R / Rscript | PATH 无入口；未找到常见安装；`/usr/lib/R`、`/usr/share/R` 不存在；dpkg 无 `r-base` / `r-base-core` | 在检查范围内未安装；没有发现“已安装但未加入 PATH”的证据 |
| Conda | PATH 无入口；常见安装扫描无候选；dpkg 无记录 | 在检查范围内未安装；dpkg 无记录本身不足以排除用户安装 |
| Mamba / Micromamba | PATH 无入口，常见安装扫描无候选；dpkg 无 mamba 记录 | 在检查范围内未安装 |
| curl | `/usr/bin/curl`，8.5.0 | 可运行，HTTPS 检查成功 |
| wget / tar | `/usr/bin/wget`、`/usr/bin/tar` | PATH 中存在；未运行下载或解压 |
| Java / Nextflow / Docker / Snakemake | PATH 均无入口 | 仅确认当前 PATH 不可用，未对这些附加工具做完整安装扫描；不属于两个计数矩阵分析的核心依赖 |

安装扫描范围：`/home/a`、`/opt`、`/usr/local`，递归至相对路径六层，排除 `.git`、`node_modules`、缓存、Codex 和插件目录；另检查 R 标准目录。扫描未报告权限错误，没有发现 PATH 之外的目标可执行文件。未扫描其他用户家目录或全部文件系统，因此“未安装”限定于以上证据范围。

当前 PATH 包含 `/usr/local/bin`、`/usr/bin`、`/bin`、`/snap/bin`、Node/Codex 相关路径，没有常见 Conda 环境的 bin 路径。检查的是当前登录 shell 的运行环境，没有修改 shell 初始化文件。

### Python 包与环境能力

在 `/usr/bin/python3` 下通过 `importlib.util.find_spec` 检查，以下模块均未发现：`pip`、`numpy`、`scipy`、`pandas`、`matplotlib`、`sklearn`、`scanpy`、`anndata`、`igraph`、`leidenalg`、`pydeseq2`、`h5py`、`statsmodels`、`umap`。这是当前解释器的包可见性检查，未运行这些包的导入或分析。

`venv` 标准库模块存在，但 `python3 -m ensurepip --version` 报 `No module named ensurepip`；dpkg 显示 `python3-venv` 未安装、`python3-pip` 无记录。因此不能把“venv 模块存在”当作能够创建带 pip 的环境的证明。本次未创建 venv。

R 本身不可用，无法检查其包库；不能将 R 包记为“已验证未安装”，应记为“未检查，运行时缺失”。参考文档选择 Python 3.11，本机是 3.12.3；两者不同，但本次未做包版本解析，不能据此判定 3.12 不兼容。

## 4. 权限与错误分类

- 当前用户属于 `sudo` 组，但没有执行 sudo，也未验证提权能力。
- `/home/a` 与项目 `docs/` 的读、写、目录搜索权限检查均通过；报告实际写入作为项目写权限的证据。
- `/opt`、`/usr/local/bin` 可读、可搜索，当前用户不可写；系统级安装需要额外权限，用户目录安装另行决定。
- 首次沙箱命令在启动前失败：`bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`。这是沙箱创建网络命名空间时的权限问题，不是软件未安装、目标网站失败或 VM 没有网络。后续检查在获得授权后于沙箱外执行。

| 分类 | 判断标准 | 本次结果 |
| --- | --- | --- |
| 软件未安装 | PATH 缺失，并结合安装目录与包数据库 | R、Conda/Mamba 在检查范围内未发现 |
| 未加入 PATH | 在其他位置找到可执行软件，但 `command -v` 失败 | 本次未发现此类实例；`python` 缺失是入口名称问题 |
| 权限不足 | 明确的 EACCES / EPERM 或目录权限证据 | 沙箱启动失败；系统软件目录当前用户不可写 |
| 网络失败 | DNS 错误、连接超时、TLS 错误、HTTP 拒绝等实际证据 | 已测目标没有失败；直连与完整下载未测试 |

## 5. 代理与网络

网卡 `ens33` 为 UP，IPv4 `192.168.17.128/24`；默认网关 `192.168.17.2`。DNS 使用 systemd-resolved stub `127.0.0.53`，上游 DNS 为 `192.168.17.2`，搜索域 `localdomain`。

`HTTP_PROXY` / `http_proxy` 与 `HTTPS_PROXY` / `https_proxy` 都指向 `http://192.168.17.1:12049`，未包含用户名或密码。`NO_PROXY` / `no_proxy` 为 `localhost,127.0.0.1,::1`。Git 的 `http.proxy` 和 `https.proxy` 配置查询无值（退出码 1 表示未设置该键）；Git 实际传输尚未测试。

对每个目标独立进行了系统 DNS 查询和 `curl -I -L` 检查。连接超时 5 秒、总超时 18 秒，保留正常 TLS 校验，不使用 `-k`，没有绕过代理或下载数据正文。

| 目标 | 请求地址 | DNS | curl 退出码 / 最终 HTTP | TLS 校验 | 时间 |
| --- | --- | --- | --- | --- | --- |
| GitHub / Miniforge 发布入口 | https://github.com/conda-forge/miniforge/releases/latest | 成功 | 0 / 200 | 通过 | 1.92 s |
| conda-forge linux-64 索引 | https://conda.anaconda.org/conda-forge/linux-64/repodata.json | 成功 | 0 / 200 | 通过 | 0.91 s |
| bioconda linux-64 索引 | https://conda.anaconda.org/bioconda/linux-64/repodata.json | 成功 | 0 / 200 | 通过 | 0.93 s |
| Bioconductor | https://bioconductor.org/packages/release/bioc/ | 成功 | 0 / 200 | 通过 | 1.18 s |
| CRAN | https://cloud.r-project.org/ | 成功 | 0 / 200 | 通过 | 1.07 s |
| PyPI / Scanpy | https://pypi.org/simple/scanpy/ | 成功 | 0 / 200 | 通过 | 0.97 s |
| PBMC3k 数据文件 | https://cf.10xgenomics.com/samples/cell/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz | 成功 | 0 / 200 | 通过 | 1.09 s |

所有 curl 请求的远端连接 IP 为代理 `192.168.17.1`，`ssl_verify_result=0`。HTTP 200 是连通性证据，不保证后续全部包、GitHub release 二进制资产、镜像仓库或大文件下载成功。参考文档提到的另一沙箱 pip 403 不代表本机现状；本次没有执行 pip 安装，不能断言安装一定成功。

## 6. airway 与 PBMC3k 的最小依赖

以下从两份本地参考文档的流程和代码提取，是后续准备清单，不是本机已安装清单，也不是经过求解器验证的版本锁文件。各顶层包还需要其正常传递依赖；无需把传递依赖全部手工列成安装项。

| 任务 | 最小运行时与顶层依赖 | 输入 / 补充 |
| --- | --- | --- |
| airway 核心 DESeq2 分析 | R、`airway`、`DESeq2`，及其传递依赖（含 `SummarizedExperiment`） | airway 包内置原始计数与样本信息；设计 `~ cell + dex`；无需下载 SRA reads |
| 原样运行指南 `01_bulk_deseq2.R` 并输出全部图表与 symbol | 上述核心 + `apeglm`、`AnnotationDbi`、`org.Hs.eg.db`、`ggplot2`、`ggrepel`、`pheatmap` | 收缩、注释、火山图与热图依赖；不是仅进行 DESeq2 检验的最低要求 |
| airway 的 edgeR 交叉验证 | R、`airway`、`edgeR`，及访问 assay / colData 所需传递依赖 | 使用同一计数与 metadata |
| airway 的 PyDESeq2 交叉验证 | Python、`pydeseq2`、`pandas`，及其传递依赖 | 需要先导出的 counts 和 coldata CSV；Python 路线自身不要求 R，但指南的导出步骤使用 R |
| PBMC3k 的 Seurat 核心路线 | R、`Seurat` 及传递依赖 | 10x 的 `matrix.mtx`、`genes.tsv`、`barcodes.tsv`；用于 QC、归一化、PCA、聚类、UMAP 与 markers |
| 原样运行指南 `04_sc_seurat.R` | R、`Seurat`、`dplyr`、`ggplot2` 及传递依赖 | 直接加载后两包并使用管道、汇总与保存图形；不需要整个 tidyverse |
| PBMC3k 的 Scanpy 路线 | Python、`scanpy`、`igraph` 及其传递依赖 | 指南使用 `flavor="igraph"` 的 Leiden；所需科学计算栈包括 anndata、numpy、scipy、pandas、matplotlib、scikit-learn、h5py、umap-learn 等传递依赖 |
| Scanpy 的另一 Leiden 实现 | 上述 + `leidenalg` | 使用 `flavor="leidenalg"` 时需要；指南 igraph 路线不应把它当作无条件最小依赖 |
| bulk / 聚类对比和验收脚本 | Python、`pandas`、`numpy`、`scipy`、`scikit-learn` | Spearman 相关需要 scipy；ARI/NMI 使用 scikit-learn |
| 数据获取与记录 | `curl` 或 `wget`、`tar`/gzip、Git | 下载和解压 PBMC3k；Git 用于版本记录，不是统计计算运行时依赖 |

若目标是完整复现指南的 R 与 Python 两条路线，合并后的直接依赖清单为：

- R：`airway`、`DESeq2`、`edgeR`、`apeglm`、`AnnotationDbi`、`org.Hs.eg.db`、`ggplot2`、`ggrepel`、`pheatmap`、`Seurat`、`dplyr`。
- Python：`pydeseq2`、`scanpy`、`igraph`、`pandas`、`numpy`、`scipy`、`scikit-learn`；绘图和 AnnData 等由正常依赖解析安装。若换用 leidenalg 后端再加入 `leidenalg`。
- 环境管理：Conda/Mamba 可用于隔离 R/Python 环境，但不是数据分析本身必需的运行时。参考文档建议分开建 R 与 Python 环境，尚未执行。

`clusterProfiler`（可选 GO 富集）、整个 `tidyverse`、JupyterLab、Snakemake、Docker、Java、Nextflow、FastQC、STAR、Salmon 均不属于 airway 已有计数矩阵和 PBMC3k 已过滤矩阵分析的最小依赖。若另外执行 nf-core/rnaseq 测试，才需要额外准备 Nextflow、匹配的 Java、容器运行时及相应权限、镜像与测试数据网络；本次未运行该流程。

版本选择应在后续安装时根据实际可解析的组合固定，记录 R/Python 版本、sessionInfo 和包版本；本次没有核验参考文档里的版本号与当前软件仓库兼容性。

## 7. 检查方法与边界

主要证据命令：`cat /etc/os-release`、`uname -a`、`lscpu`、`free -h`、`df -hT`、`df -i`、`lsblk`、`id`、`command -v`、`dpkg-query`、Python `shutil.which` / `os.walk` / `os.access` / `importlib.util.find_spec`、`ip -brief address`、`ip route`、`resolvectl status`、`git config --get http.proxy` / `https.proxy`。

网络请求形式（本次仅 HEAD）：

```bash
curl -I -L -sS --connect-timeout 5 --max-time 18 \
  -o /dev/null \
  -w 'http=%{http_code} remote=%{remote_ip} tls_verify=%{ssl_verify_result} seconds=%{time_total}' \
  <目标 HTTPS URL>
```

包检查限于当前系统 Python；不证明所有用户、所有未激活环境均无这些包。没有修改 PATH、代理、DNS、用户组、分区或包配置，没有运行文档中的安装命令。
