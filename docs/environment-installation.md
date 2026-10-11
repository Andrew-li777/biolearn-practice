# airway / PBMC3k 分析环境安装与验证

安装和验证日期：2026-10-10 UTC。项目：`/home/a/projects/biolearn-practice`。

## 实际结果

已在用户目录安装 Miniforge 26.7.2-0（Mamba 2.9.0），安装前校验官方发布资产 SHA-256。安装目录 `/home/a/miniforge3`，两个独立环境为：

| 环境 | 路径 | 主要实际版本 |
| --- | --- | --- |
| biolearn-r | `/home/a/miniforge3/envs/biolearn-r` | R 4.4.3、DESeq2 1.46.0、edgeR 4.4.0、airway 1.26.0、Seurat 5.5.1 |
| biolearn-py | `/home/a/miniforge3/envs/biolearn-py` | Python 3.11.17、Scanpy 1.11.5、PyDESeq2 0.5.4、igraph 1.0.0、leidenalg 0.12.0 |

使用 conda-forge 优先、bioconda 次之的严格频道优先级，未使用 defaults。R 的 Bioconductor 包对应 3.20 系列；R/Python 顶层版本范围先由求解器解析，再通过加载和实际计算验证。所有直接和传递依赖、精确 build 和下载地址均保存在环境导出及 explicit 清单中。

R 额外包实际版本：apeglm 1.28.0、AnnotationDbi 1.68.0、org.Hs.eg.db 3.20.0、ggplot2 4.0.3、ggrepel 0.9.8、pheatmap 1.0.13、dplyr 1.2.1。

Python 科学计算主要版本：NumPy 2.4.6、SciPy 1.17.1、pandas 2.3.3、scikit-learn 1.9.1、Matplotlib 3.11.2、seaborn 0.13.2、AnnData 0.12.19、h5py 3.16.0、statsmodels 0.15.0、umap-learn 0.5.12。`scikit-misc` 0.5.3（Conda 包版本）也已安装并成功导入；其 Python distribution 元数据报告 0.0.0，仓库实际版本应以 `biolearn-py.packages.json` / explicit 清单为准。

## 已完成验证

四个验证进程均退出 0，汇总见 [status.txt](../environment/validation/status.txt)。

- R：11 个目标包全部 `library()` 成功。airway 数据为 63,677 基因 × 8 样本；采用 `~ cell + dex`，成功构造 DESeq2 对象并估计 size factors；edgeR 完成归一化和 dispersion 估计。另完成 Seurat 对象创建、归一化及 ggplot2 PDF 绘图。
- Python：15 个模块全部 `import` 成功。合成小矩阵完成 Scanpy PCA、邻居图、igraph / leidenalg 两个 Leiden 后端、UMAP、Wilcoxon markers、绘图、H5AD 写入；比较依赖通过 ARI、NMI、Spearman 计算；PyDESeq2 完成小数据拟合与统计检验。
- 真实 PBMC3k：从 10x 下载过滤矩阵（2,700 细胞 × 32,738 基因），保存归档 SHA-256。Seurat 和 Scanpy 分别完成读取、质控、归一化、变异基因、PCA、邻居图、聚类、UMAP 和绘图。相同质控阈值下均保留 2,638 细胞，各得到 9 簇；簇数相同不代表两种实现的簇划分一致，本次没有进行真实 PBMC3k 的跨工具 ARI/NMI 比较。

这是安装验收和计算 smoke test；没有完成完整 airway DESeq2 拟合、apeglm 收缩、注释和研究级结果解释，也没有对真实 PBMC3k 进行 markers/细胞类型注释。上述相关包加载已通过。

非阻断警告：Seurat 自动替换基因名中的下划线、矩阵转稀疏格式及说明默认 R-native UWOT；Scanpy scale 的零中心化使稀疏矩阵变密集。全部验证成功，PBMC3k 的当前规模可处理。

## 保存的文件

- 原始顶层依赖：[r-analysis.yml](../environment/r-analysis.yml)、[python-analysis.yml](../environment/python-analysis.yml)。
- 实际解析环境：[biolearn-r.resolved.yml](../environment/biolearn-r.resolved.yml)、[biolearn-py.resolved.yml](../environment/biolearn-py.resolved.yml)。
- Linux x86_64 精确复现清单：[R explicit](../environment/biolearn-r.linux-64.explicit.txt)、[Python explicit](../environment/biolearn-py.linux-64.explicit.txt)。这些清单限定当前平台，Bioconductor 数据包的 post-link 仍可能需要访问其数据源。
- 全量包信息：`environment/biolearn-{r,py}.packages.json`；主要包运行时版本：`environment/validation/r-versions.csv`、`python-versions.json`。
- 安装日志：`environment/logs/download-miniforge.log`、`miniforge-checksum.log`、`install-miniforge.log`、`install-r.log`、`install-python.log`，并保留首次分片索引失败日志。
- 验证日志：[R](../environment/logs/verify-r.log)、[Python](../environment/logs/verify-python.log)、[Seurat PBMC3k](../environment/logs/verify-pbmc3k-r.log)、[Scanpy PBMC3k](../environment/logs/verify-pbmc3k-python.log)。R 日志包含 `sessionInfo()`。
- 验证代码：`environment/validation/verify.R`、`verify.py`、`verify-pbmc3k.R`、`verify-pbmc3k.py`；重复验收入口：`bash environment/verify-environments.sh`。
- 绘图：`environment/validation/r-plot.pdf`、`python-plot.png`、`pbmc3k-seurat.pdf`、`pbmc3k-scanpy.png`；合成矩阵：`synthetic-smoke.h5ad`。
- 下载数据：`data/pbmc3k/`（没有加入 Git）；Miniforge 安装器也通过 `.gitignore` 排除，日志、环境文件及验证结果仍保留。

## 错误排查与权限

1. 通用安装器的 `.sha256` 地址返回 HTTP 404。通过 GitHub 官方 release API 找到版本专属校验文件，实际比对通过：`281b0ac7d550802efc81af633225a5e6116d29ae72f3ab4eae7168c3931a4c05`。
2. Mamba 分片索引的 python_abi 请求超时。停止该次解析、保留日志，以单次命令环境变量 `MAMBA_USE_SHARDED_REPODATA=false` 切换到常规 repodata，两个环境均求解和安装成功。此设置已经写入重复安装脚本；`environment/condarc.yml` 是记录文件，没有覆盖全局配置。
3. 两个安装进程共享缓存产生锁等待，后续自行恢复，无需清理其他环境。

没有 sudo、sudo pip 或系统包安装；没有修改代理、DNS、shell 初始化文件或系统 Python。最终 `command -v python3` 仍为 `/usr/bin/python3`，版本仍为 3.12.3。未安装 Docker、Nextflow、完整人类参考基因组或其他大流程工具。PBMC3k 自带的 hg19 基因名标注不属于参考基因组下载。

最终 `/home/a/miniforge3` 含环境与缓存约 6.2 GiB，根文件系统剩余约 32 GiB。

## 使用已安装环境

不依赖 shell 自动初始化，可直接执行：

```bash
/home/a/miniforge3/bin/conda run -n biolearn-r Rscript your_script.R
/home/a/miniforge3/bin/conda run -n biolearn-py python your_script.py
```

交互激活：

```bash
source /home/a/miniforge3/etc/profile.d/conda.sh
conda activate biolearn-r  # 或 biolearn-py
```

后续在同一 Linux 平台重新创建精确环境：

```bash
/home/a/miniforge3/bin/conda create -n biolearn-r-reproduced --file environment/biolearn-r.linux-64.explicit.txt
/home/a/miniforge3/bin/conda create -n biolearn-py-reproduced --file environment/biolearn-py.linux-64.explicit.txt
```

来源：[Miniforge 官方发布](https://github.com/conda-forge/miniforge/releases/tag/26.7.2-0)、[Bioconda DESeq2 配方](https://bioconda.github.io/recipes/bioconductor-deseq2/README.html)、[Bioconda PyDESeq2 配方](https://bioconda.github.io/recipes/pydeseq2/README.html)、[conda-forge Seurat 配方](https://github.com/conda-forge/r-seurat-feedstock)、[conda-forge Scanpy 配方](https://github.com/conda-forge/scanpy-feedstock)。本报告的版本与验证结论来自本机实际安装和执行日志。
