# 本机验证记录（2026-10-30 UTC）

输入：DEP 1.28.0 UbiLength 源包，SHA-256 `c870e066e73386632ad541c2c93e27f051dfebdcd53a7b99a6202086a9413300`。导出时核对安装包对象与下载源包对象完全一致。原始 3,006 蛋白组、12 样本；排除反向库后 2,975、污染物后 2,941、仅位点鉴定后 2,907、完整组过滤后 1,898。以上来自实际 filter_counts.csv。

环境：独立 `proteomics-analysis`，R 4.4.3、DEP 1.28.0、limma 3.62.1、vsn 3.74.0、imputeLCMD 2.1。完整环境锁在 environment；运行版本表及 sessionInfo 在结果目录。准备期间另克隆了 `proteomics-r`，但没有用于正式分析，保留未删除。原有环境和系统 R/Python 未修改。

参数：Ctrl 参照，Ubi1/Ubi4/Ubi6 各自比较；seed=42、MinProb q=0.01、BH FDR<0.05、|log2FC|>=1、两线程。主结果 `results/final/`。

| 比较 | FDR 显著 | 同时满足效应阈值 | 不插补可检验 | 单侧全缺失 |
|---|---:|---:|---:|---:|
| Ubi1 vs Ctrl | 128 | 104 | 1486 | 353 |
| Ubi4 vs Ctrl | 395 | 242 | 1348 | 475 |
| Ubi6 vs Ctrl | 393 | 261 | 1352 | 493 |

共同可检验集合上，主分析与不插补分析显著集合 Jaccard 分别为 0.100、0.917、0.769；Ubi1 对缺失值处理尤其敏感，不能将主路线作为独立生物学真值。完整比较见 sensitivity_summary.csv。

已通过：小矩阵的样本错配、重复 ID/样本、零转换、过滤边界、效应方向和缺失组检查；实际 RDS 与所有 CSV 回读；样本顺序、插补未改写观测值、BH 独立重算、效应方向和敏感性排除检查；11 张 PNG 解码。PCA 已目视检查。

固定种子复跑：`results/validated` 与 `results/final` 的标准化/插补矩阵、3 组主差异表、3 组敏感性表和两个汇总表共 10 项字节一致，证据 `results/reproducibility.json`。这不保证跨平台或升级软件后位级一致。

失败记录保留：`results/demo` 与 `results/run-01` 的日志记录最初缺少 DEP name/ID 元数据；`results/run-02-workflow.log` 记录 Python 报告依赖 PIL 缺失。已补元数据，图片改用现有 R png 包解码，Python 报告仅依赖标准库；不影响最终统计方法。

新机器安装、其他数据接入、无显著结果的完整端到端运行未验证。无显著集合的空表和 NA Jaccard 分支已实现，但本数据未触发。

缺图恢复通过：移走 pca.png 并保留到 results/pca-before-recovery.png 后，工作流重新生成主分析及报告；恢复图片字节一致。最终 dry-run 无待运行任务，记录 results/final-dry-run.log。产物 SHA-256 清单逐项复核通过。
