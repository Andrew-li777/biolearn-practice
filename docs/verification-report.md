# 项目当前完成状态核验

更新：2026-10-10 UTC。本报告依据当前脚本、实际产物、对象回读、完整日志、执行记录和环境文件；没有用参考数字或 README 声明代替运行证据。最初只读核验完整保存于 [verification-report-20261010-readonly.md](verification-report-20261010-readonly.md)。历史结果和失败资料均保留。

PASS＝完整执行及产物证据；WARN＝已执行但有方法/参考差异或解释局限；FAIL＝失败、缺失或不一致；NOT RUN＝未执行；UNVERIFIED＝证据不足。阶段总体包含重要局限，执行子项单独标记。

## 当前阶段

| 阶段 | 状态 | 实测证据及最小后续动作 |
|---|---|---|
| 1 环境准备 | WARN；加载和容器预检 PASS | R/Python原分析环境保持；Docker29.1.3和客户端导入可用；Snakemake/scikit-misc版本元数据差异已记录，按Conda build和实际模块文件报告，不手改元数据 |
| 2 airway bulk | WARN；完整重跑和核验 PASS | 三方法39/39验收；DESeq2/edgeR/PyDESeq2显著4916/6550/4685；参考4381缺少同输入原流程证据，保留差异；df=3触发PyDESeq2先验警告 |
| 3 PBMC3k | WARN；主分析、注释、比较 PASS | 两路线2638细胞/9簇，83/83验收；doublet和独立参考已经实际执行；参考约80%一致，注释仍为推定 |
| 4 nf-core/rnaseq官方测试 | PASS；官方报告展示警告已调查 | attempt-2退出0，234/234任务COMPLETED，267/267核验；8序列化文件、5BAM、128PDF/132页及MultiQC回读成功；独立修正展示报告与原科学数据一致 |
| 5 Snakemake/干净输出 | PASS；跨主机证据另记UNVERIFIED | 主矩阵16/16比较、158/158扩大核验；补充诊断3/3完成，217文件全部非空、metadata217/incomplete0/输入变化0；最终dry-run无任务 |

当前主要有效目录：`results/reproduction/followup-20261010/`，下分`bulk`、`pbmc3k`、`pbmc_validation`、`pbmc_graph`。nf-core独立目录：`results/nfcore/rnaseq-3.27.0-attempt-2/`。旧`run-*`、`clean-20261010`及首轮官方失败仅作历史证据，不与新目录拼接交付。

## 1. 环境及网络

已验证主要版本：R4.4.3、DESeq2 1.46.0、edgeR4.4.0、Seurat5.5.1、airway1.26.0、apeglm1.28.0、Matrix1.7.6；Python3.11.17、PyDESeq2 .5.4、Scanpy1.11.5、AnnData.12.19、NumPy2.4.6、pandas2.3.3、SciPy1.17.1、igraph1.0.0、leidenalg.12.0。主分析实际运行加载这些包；独立对象验收另行加载Seurat/Scanpy。全量版本及锁文件在各主目录`environment/`和各路线session/runtime记录。

- `environment/followup-20261010/version-provenance.json`：Snakemake CLI及模块9.13.4，Conda`snakemake-minimal`9.13.4/pyhdfd78af_1，distribution=0.0.0；scikit-misc Conda0.5.3/py311h9340a49_0，模块和distribution0.0.0，生成的版本文件有实物证据。这是元数据不一致WARN；实际使用和完整环境build已记录。
- Docker daemon可用；当前会话使用`sg docker`取得已配置的组权限，不需再次安装系统引擎。
- daemon直接pull失败：`Head https://registry-1.docker.io/v2/library/alpine/manifests/3.20: dial tcp 192.133.77.189:443: connect: connection refused`。完整错误：`environment/nfcore/container-check-20261010T2244/pull.log`。
- 修复使用独立`biolearn-container` Skopeo1.24.1，继承已有客户端代理，将官方精确镜像参考导入Docker；没有修改系统代理。项目v2 registry配置解决客户端附带v1格式不兼容。入口`scripts/fetch_container_image.py`和`scripts/container-client/docker`；锁文件`environment/biolearn-container.*`，安装日志`environment/logs/install-container-client-20261010.log`。
- `environment/nfcore/container-check-ready-20261010/status.txt`=PASS：Alpine实际运行、DNS正常；curl8.10.1容器访问官方samplesheet HTTP200/1335B。原BusyBox wget HTTP503、主机200和容器curl200证据保留在`container-check-client-20261010/`；修复预检使用curl，不再将wget探针失败当网络整体失败。
- 每镜像源digest、Docker image ID/层、开始结束、退出和复制日志在`environment/nfcore/image-imports-20261010/`。它们是Skopeo源摘要和daemon导入证据，不能冒充daemon直接pull成功。
- doublet自动阈值所需scikit-image原环境缺失。独立克隆因`SSLRECORD_LAYER_FAILURE`失败，离线克隆因缺包缓存失败；完整日志`environment/logs/create-validation-clone-20261010.log`及`create-validation-clone-offline-20261010.log`。采用`environment/validation-venv`继承已验证Python，只安装额外依赖；原R/Python环境未改变。额外固定版本见`environment/validation-extra-requirements.txt`，完整freeze见诊断产物。

## 2. airway bulk实际重跑

目录`bulk/`以下均指当前主目录。8样本、63677基因，4个cell供体各一对trt/untrt；设计`~ cell + dex`，untrt参照，trt vs untrt，两侧检验、FDR<0.1，不加LFC筛选。`airway_coldata.csv`、`airway_counts.csv`、两设计矩阵、配对表和各method.txt保存实际方案。设计8×5、rank5、残差df3；所有样本/基因ID唯一并对齐。

| 方法 | 过滤 | 测试基因 | 显著 | 上调/下调 |
|---|---|---:|---:|---:|
| DESeq2 | 至少3样本count≥10 |16596|4916|2618/2298|
| edgeR | 完整design的filterByExpr；min.count10/min.total15/large.n10/min.prop.7 |16860|6550|3302/3248|
| PyDESeq2 | 同DESeq2 |16596|4685|2502/2183|

DESeq2/PyDESeq2 median-of-ratios、parametric/MAP、Wald、BH+independent filtering alpha=.1、Cook选项；edgeR TMM、robust dispersion及robust QL、BH。比较使用未收缩主LFC，apeglm只用于独立图表。过滤全集不同，不把edgeR简化为原始count≥10的同一布尔规则。

新运行三个主阶段、报告全部退出0，39/39验收。主结果p/padj缺失均0，概率0..1、LFC及统计量有限；symbol缺失2391/2473/2391是未注释基因，允许且保留gene ID。显著CSV按主表FDR<.1逐gene重核对，无异常NA/Inf。

| 方法对 | overlap | Jaccard | overlap方向一致 |
|---|---:|---:|---:|
| DESeq2/edgeR |4879|.740701381509033|1.0|
| DESeq2/PyDESeq2 |4641|.9356854838709677|1.0|
| edgeR/PyDESeq2 |4635|.7022727272727273|1.0|

三工具共同显著4611；新旧主要结果数值一致。`reference_diagnostics.json`区分参考4381与实测4916，差+535。本轮重复得到相同4916；参考缺少完整同输入/同版本运行产物，不能宣称已确定535的唯一原因。最小动作是补齐参考原流程证据后才能做严格归因；本项目无需调参去匹配它。

PyDESeq2警告文字称残差df“less than3”，实际源码`dds.py`的条件为`(num_samples-num_vars)<=3`。8−5=3确实触发，非样本丢失或设计不满秩；与小样本离散度先验估计局限一致，保留WARN。不能通过删除cell配对项消除警告。

证据：`bulk/analysis_summary.csv`、`comparisons.csv`、`*_results.csv`、`*_filter.csv`、`*_method.txt`、`run-provenance.json`、`logs/*.log`；扩大核验`verification/checks.json`和`csv_inventory.json`。

## 3. PBMC3k、注释与比较

同一10x归档SHA256=`847d6ebd9a1ec9a768f2be7e40ca42cbfe75ebeb6d76a4c24167041699dc28b5`；两路线原始32738基因×2700细胞。95重复gene symbols已唯一化；gene IDs和barcodes唯一。新H5AD counts实际逐元素等于解压矩阵；QC后counts等于同一原始矩阵子集。

两路线先gene min.cells3及cell初始化200，再严格`200<genes<2500, MT<5%`，最终2638细胞、13714基因；拒绝62（高gene5、MT57、低gene0）。原始/QC前/QC后表保留，不将原始32738基因范围与预过滤后QC指标混用。

| 路线 | HVG | 回归 | PCs用于邻居 | 图/聚类 | 实测簇 |
|---|---|---|---|---|---:|
| Seurat |vst2000|无|1:10|Annoy k20/SNN；Louvain res.5/seed42|9|
| Scanpy |dispersion1838|counts、MT|40|k10 fuzzy；Leiden res1/n_iterations2/seed42|9|

83/83主验收，新加整数表达细胞数、比例关系、唯一证据键和允许NA检查。三个RDS实际readRDS（raw是list，不是Seurat）；三个H5AD实际读取。原始2700×32738，两个分析/注释对象2638×13714、9簇；对象簇标签与CSV全barcode对齐，UMAP有限且同表。

共有2638、独有0/0；ARI=.6279310734626542、NMI arithmetic=.7545047834392827，重新从barcodes算得。broad putative类型一致率=.9499620924943138是工具间一致率，不能叫准确率。HVG共同1462、Jaccard=.615319865。marker返回Seurat6964/positive2187；Scanpy123426/positive10924。

18簇注释、62行marker证据；9种putative标签均有实际正向显著canonical marker支持。Seurat/Scanpy cells分别：naive-likeCD4 705/656、memory-likeCD4 472/497、B344/341、CD8 274/307、CD14mono481/463、FCGR3Amono162/171、NK155/152、DC-like32/38、platelet-like13/13。保留like/putative及边界局限。

允许NA：正向marker统计3行（Seurat簇2/S100A4、簇5/LYZ，Scanpy簇0/S100A4）同时LFC/padj缺失且passes=False；它们有表达但没有正向显著检验证据。Scanpy CDC6离散度2字段各1 NA，该基因QC后总count0、HVG=False。其他主要数值无异常Inf；不使用全表dropna隐藏问题。

### doublet和独立参考：执行PASS，可靠性WARN

诊断入口`scripts/16_pbmc_validation.py`，当前结果位于`pbmc_validation/`；此前独立运行保留在`results/pbmc3k-validation/run-20261010T2310/`。所有诊断都使用当前主counts/labels，不删除细胞或改写主注释。

Scrublet以原始2700×32738 filtered-UMI输入，固定seed42、expected_doublet_rate=.05（默认假设，非实测真值）、simulation ratio2、PCA30、自动阈值；模拟5400，阈值=.246042051581765。原始flag36，主QC内flag34；疑似分布见每路线`*_doublets_by_cluster.csv`。检测比例不是实验doublet率，不能把36改成期望5%的135。

独立Scanpy附带PBMC68k donorA缩减参考，实际700细胞765基因，共有764；源文件SHA保存在provenance。只在reference拟合标准化/PCA30，distance-weighted kNN15，seed42；30%分层holdout210细胞，accuracy=.8428571428571429、macro-F1=.8347724920084263。类型别名事先按broad类合并CD4/CD8及monocytes，未按查询注释调参。

两路线各2625细胞有对应参考类别；platelet-like13无对应类。Seurat一致率=.8125714285714286，Scanpy=.804952380952381；29低票置信细胞（max vote<.5）。reference缺CD14/MS4A7/PPBP/PF4，类别组成偏DC、无FCGR3A特异类；Seurat643单核中230被参考预测DC，Scanpy634中224。此为明显方法/参考局限WARN，不拿预测当独立真值，不宣称生物学准确性已证明。

18/18独立检查涵盖诊断H5AD、counts/UMAP/簇完全保留、阈值flag、票和为1、留出指标重算、参考混淆表和图片。排除34flag但仅限制已有标签的2604细胞，ARI=.6263521113108851、NMI=.7589438432351208、broad一致率=.9519969278033794；这是条件比较，没有重聚类。

### 跨工具差异调查

原有控制实验已重跑，Scanpy同图Louvain/无回归/PC10/res.5/seed7分别8/8/14/6/8簇，Seuratres1=11簇。新增固定参数实验：

| 仅改变项 | 簇 | ARI对主Scanpy | ARI对Seurat |
|---|---:|---:|---:|
| Scanpy k10→20 |8|.6800459384311236|.6526309855272934|
| 精确sklearn邻居k10 |9|1.0|.6279310734626542|
| 换Seurat HVG，保留其余Scanpy方案 |8|.6543864823856812|.6605166878037708|

实际Seurat SNN导出2638×2638，194492存储项；Scanpy fuzzy41952存储项（包含显式零，不把存储项数当有效边数）。去对角/显式零后的边Jaccard=.05539603423989598。固定同一Leiden/seed42/迭代2，res.5时SNN9簇/fuzzy6簇，res1时11/9簇；SNN res.5对原Seurat ARI=.9610335706019486。4变体metrics实际从CSV回算通过。

结论限于实测：HVG、k、回归、PC、resolution、seed、聚类器及上游形成的图都可影响簇数。精确邻居替换本例没有影响。图替换打包了原有HVG/PCA/k等差异，不能宣称单独识别图公式因果效应，也不能声称所有交互已穷尽。主9/9和所有主参数保留；不把实验中8簇选作“匹配参考”的新主结果。

## 4. nf-core官方test

固定rnaseq3.27.0、提交`a1fcdddd3b826fe46eb46f0479f2ff8a7815af05`、Nextflow25.10.4、Java21.0.10。只运行固定仓库官方`test,docker`、默认star_salmon及pseudo_salmon；CPU≤4/任务内存≤12GB/time4h/队列2。已删除schema不接受的max_* params；原配置在attempt-1保留。

attempt-1退出1，两任务FAILED127，成功0、MultiQC0；根因Docker缺失，历史资料保留。attempt-2从2026-10-10T22:50:05Z执行至23:23:46Z，退出0，完整trace234/234为COMPLETED，各work退出均成功，没有未处理Nextflow ERROR。`completion-status.json`=completed:true。完整读取1170个任务日志，清单/哈希和warning/error行保存在`verification/full_task_logs.json`、`engine_log_summary.json`；独立验收`verification/summary.json`和`checks.json`为267/267。

实际samplesheet7条lane记录、5个样本，两个样本各两lane，复合键(sample,fastq1,fastq2)唯一、链方向一致，合法合并并非重复样本错误。两分支gene counts各125基因×5样本，transcript126×5；gene IDs/sample IDs唯一对齐，计数有限非负，无NA。5个最终BAM quickcheck均退出0，FastQC ZIP和实际19个下载文件均读取；输出manifest含1053文件。4个空文件是未执行的可选Picard模块的MultiQC直方图占位，记录于核验清单，不是缺失的必需定量结果。

8个RData/RDS文件共8对象实际回读：两DESeqDataSet125×5，counts/vst有效；四SummarizedExperiment gene125或transcript126×5；两个正值有限size factor对象。证据`verification/objects-readback.json`、`objects-readback.log`及`bam-quickcheck.log`。初次验收器对data.frame assay直接is.finite报错，已转换numeric matrix后重新回读；首次失败日志保留，不将其误判为流程失败。

原始128PDF/132页全部实际渲染，主要DESeq2 PCA及distance图逐张打开；PCA5个样本标签/坐标与表一致，salmon PC1/PC2=51%/22%，star_salmon=52%/22%；distance5×5对称、对角0、有限。官方“Top500”是ntop=500上限，本测试实际125基因，所以与all-genes图一致；标题不表示实测500基因。`verification/documents/pdf_readback.json`及`plot_table_alignment.json`保存实际证据。原MultiQC浏览器回读71section/55图、5样本标签、页面错误0，见`verification/documents/html_readback.json`。

日志非致命WARN已区分：官方优先GTF/重新导出transcript FASTA，GFP补充transcript-to-gene映射，Java/native-access、locale/fontcache、TrimGalore/R绘图弃用；Salmon Library types为ISR等分类值，MultiQC数值violin的NaN/Inf提示不表示计数矩阵含异常。原MultiQC1.35将裸RGB字符串55,126,184等交给spectra.html，93次转换警告并回退黑色，属于展示兼容问题。

已单独修复展示：`scripts/multiqc_compat/sitecustomize.py`只将裸RGB转换为等值rgb(...)，复用精确MultiQC镜像及原task输入，不修改官方结果/分析参数。有效派生目录`presentation-corrected-4/`：36个raw-data模块和14组general-statistics与官方JSON完全相等，颜色转换错误0、模块失败0、图导出失败0；88PDF/88页可渲染，HTML71section/55图、5样本、页面错误0，overview实际打开。命令、源digest、130输入文件哈希、执行adapter、完整日志与比较在该目录`REPRODUCE.md`及`verification/`。前三个展示尝试分别输出父目录缺失、未激活容器PATH导致导出失败、旧生成报告被重新扫描导致custom_content解析失败；全部保留，只使用fresh输入的第4次有效报告。dupRadar配置dash/label的2类兼容WARN仍保留，未调整数据。

用于报告读取的隔离`environment/document-validation-venv`锁定PyMuPDF1.28.2、Playwright1.63.0/Chromium153.0.8010.12；浏览器缺共享库以独立`biolearn-doclib`补充，子进程LD_LIBRARY_PATH，无系统覆盖。锁和完整安装日志在`environment/document-validation-requirements.txt`、`environment/biolearn-doclib.*`及`environment/logs/`。当前磁盘约5.7GiB可用；大规模额外运行前应再评估容量，已有资料不删除。

此测试输入不是airway FASTQ；airway原始FASTQ全流程当前范围外，NOT RUN。实验蛋白验证也是NOT RUN（没有数据），不能用计算参考映射代替。

## 5. Snakemake、运行归属和产物

`workflow/config.yaml`当前输出root=`results/reproduction/followup-20261010`。主契约`workflow/outputs.json`：69 bulk+97PBMC=166；新增`workflow/diagnostic-outputs.json`：34validation+17graph=51，总217。Snakefile明确PBMC→诊断依赖；`scripts/16/17`及核验器变更会重跑相应诊断，不复用失效结果。

主runner每次新建`.attempts/`，阶段记录命令、脚本SHA、起止、exit；全部报告成功和契约完整后发布，保留历史目录。主矩阵此次完整3/3成功，日志`logs/snakemake-followup-20261010.log`；`reproduction_checks.json`16/16；扩大核验`verification/checks.json`158/158。当前主要有效manifest bulk74/pbmc105文件全部匹配，main39+50CSV可读、6+13PNG可解码。

失败隔离实测`results/reproduction/failure-isolation-20261010/evidence.json`：复制成功bulk为测试fixture，conda命令故意设/bin/false，exit1，已发布75文件全部哈希保持；failed attempt completed=false。没有删除任何原始数据或已有资料。

诊断最终运行`logs/snakemake-diagnostics-20261010.log`3/3成功；完整metadata217、incomplete0、输入hash变化0，`logs/snakemake-all-final-dry-run.log`无待执行。4目录manifest74/105/33/16均匹配，所有217声明产物非空；25个诊断CSV可读且无Inf，3个新增实验ARI/NMI重新计算一致。`verification/final_contract_and_diagnostics.json`、`snakemake_metadata.json`、`preserved_history.json`保存实测；历史4目录manifest共372文件均未改变。

新诊断采用独立attempt及预先copy staging后rename发布；任何阶段失败均保存完整执行日志且不发布。初轮venv软链接被resolve到基础Python，报`ValueError: threshold is None and thus scrublet requires skimage, but skimage is not installed.`；保留venv路径后重跑。随后图阶段manifest包含了正在更新的run-provenance而校验失败；将可变执行记录置于attempt旁，最后再入稳定manifest，修复后重新运行全部受影响诊断。失败资料见`.attempts/`、`logs/snakemake-diagnostics-first-20261010.log`及`...second...log`；主矩阵始终有效。

首次扩大验收器误将raw RDS list当Seurat、误把annotation-plan参数也当脚本比较SHA，导致156/158；已修正验收器、重新实际回读，最终158/158，保留`checks-first.json`、`rds_readback-first.log`。这两项是验收器错误，不是主分析失败。

主要19图实际与此前逐张视觉核验版本SHA相同，标签、样本/簇/marker列表、VST/UMAP及dotplot表一致。新3诊断图已经逐张打开：参考表逐格重算一致，doublet UMAP使用主坐标、score和flags（蓝=未flag，红=flag）。不以HTML存在或图片可打开单独判分析成功。

所有现存新阶段日志全文读取、warning/error行及SHA清单在`verification/full_logs.json`及诊断日志。历史65日志全文清单和19图逐图证据在最初只读快照。nf-core完整任务日志清单已保存在独立目录`verification/full_task_logs.json`；未处理错误必须以最终退出、trace及当前产物判断，不能忽略失败。

## 剩余证据边界及按依赖的下一步

1. 容器→官方test→完整回读→展示兼容修复及数值一致核验，均已完成PASS，无遗留可修复FAIL。官方原报告及所有失败尝试保留；最终重新核对官方1053输出文件SHA全部未变，证据`results/nfcore/rnaseq-3.27.0-attempt-2/verification/final_preservation_and_presentation.json`。文档更新后再次dry-run无任务：`logs/snakemake-final-after-docs-20261010.log`。
2. 诊断编排修复→全图运行→217产物/manifest/输入元数据/dry-run已完成PASS。若后续输入或方法变化，按Snakemake依赖自动重跑受影响路线及比较。
3. 现有数据可支持的注释诊断已运行。实验类型准确性仍UNVERIFIED、蛋白验证NOT RUN：缺蛋白/其他实验真值数据，最小解决动作是提供可对齐的测量数据；计算映射不能补出实验数据。
4. 独立第二主机/全新环境复现UNVERIFIED：仅有本机固定环境的干净输出证据，无第二主机位置。最小动作是在另一授权主机恢复锁环境再执行工作流并比较；本轮已保存环境锁、额外依赖、输入哈希和执行命令。
5. 若要解释bulk参考差值的唯一原因，先取得参考原始运行输入/完整参数/版本/结果，再做同输入对照。无需为当前实测调整阈值、设计或聚类。

未推送GitHub，未修改系统代理，未删除原始数据或历史资料。
