# 方法与解释边界

来源：Bioconductor 3.20 DEP 1.28.0 的 UbiLength 和 UbiLength_ExpDesign，官方教程 https://bioconductor.org/packages/3.20/bioc/vignettes/DEP/inst/doc/DEP.html 。原始研究：Zhang, Smits, van Tilburg 等，2017，An interaction landscape of ubiquitin signaling，doi:10.1016/j.molcel.2017.01.004。源包 Artistic-2.0；下载地址与 SHA-256 固定于 scripts/download.py。

保留蛋白组，禁止按基因名合并。依次排除 Reverse、Potential.contaminant、Only.identified.by.site 为 + 的条目。LFQ 零值置 NA，至少一个组全部重复定量才保留。原始矩阵、过滤标记和每步计数独立保存。

DEP normalize_vsn 输入 log2 强度，内部还原线性强度并做 VSN，不能再对输出取 log2。主路线 MinProb q=0.01，seed=42，其余使用记录版本的默认值。每个处理组与 Ctrl 单独拟合 limma 组别模型，eBayes 默认参数；报告处理组减 Ctrl。此处直接调用 limma 并采用逐比较 BH 校正，不使用 DEP test_diff 的 fdrtool q 值。FDR<0.05 与同时 |log2FC|>=1 分开报告，后者为效应筛选，不是区间零假设检验。不同比较间未联合校正。

敏感性分析采用同一 VSN 矩阵且不插补；每个比较两组各至少两个观测值，至少两个可检验蛋白才进行经验贝叶斯拟合。不可检验条目保留原因。只在共同可检验集合计算 Spearman、方向一致率及 FDR 显著集合 Jaccard；空并集记 NA。由于可检验集合和经验贝叶斯先验不同，差异不能单独归因于插补。

MinProb 的低信号缺失假设不能从数据完全证实。单侧全缺失蛋白的效应强烈依赖插补；其原始观测数在 sensitivity 表中可查。PCA、热图用插补矩阵，相关性用非插补 VSN 的成对完整观测。热图为各比较 FDR 排名前 30 蛋白，不代表全部显著。没有富集功能注释或独立实验验证。

matrix_x 为线性 LFQ；matrix_n 为 VSN；matrix_im 为插补 VSN。样本 QC、correlation、pca 及每个比较 heatmap CSV 是图源数据，火山图直接使用 main.csv。缺失条目不计为真实零丰度。
