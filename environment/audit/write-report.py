from pathlib import Path
import json
r=json.loads(Path('environment/audit/host-network.json').read_text())
mem=r['system']['memory']['output'].splitlines()[1].split()
s += [f'| 内存 | 总计 {int(mem[1])/2**30:.2f} GiB；检查时可用 {int(mem[6])/2**30:.2f} GiB |','| Swap | 4 GiB，当前使用 0 |','| 项目文件系统 | ext4；48 GiB 总量，14 GiB 已用，32 GiB 可用，31% 使用率 |','', '容量和内存是快照，不保证后续运行峰值；本次没有运行完整分析或构建参考基因组。', '', '## 3. 软件路径与版本','', '| 工具 | 当前 PATH | 已发现可执行路径 / 版本 | 分类 |','| --- | --- | --- | --- |']
for name,v in r['tools'].items():
 candidates='<br>'.join(f"`{c['path']}`：{c['output'].splitlines()[0]}（exit={c['exit']}）" for c in v['candidates']) or '未发现'
 status='可运行' if v['PATH'] else ('已安装，未在当前 PATH' if v['candidates'] else '缺失（检查范围内）')
 s.append(f"| {name} | {v['PATH'] or '无'} | {candidates} | {status} |")
s += ['', '补充扫描 `/home/a`、`/opt`、`/usr/local` 至六层，排除 Codex 插件与 node_modules，未发现 Docker、Java、Nextflow、Snakemake；扫描没有权限错误。结合常见入口和 dpkg 查询判断“检查范围内缺失”，没有扫描其他用户目录或全部文件系统。证据：`extra-tool-paths.txt`、`extra-tool-scan-errors.log`、`system-packages.log`，均位于 `environment/audit/`。', '', 'Docker CLI 未发现，因此引擎状态为**未核实**；没有执行 `docker info`、容器运行或拉取镜像。不能把 CLI 缺失直接等同于所有远端 Docker 服务不存在。', '', '## 4. 已有环境与实际包加载','', '| 环境 | 路径 | 用途及结果 |','| --- | --- | --- |','| base | `/home/a/miniforge3` | Python 3.14.7；检查的分析模块缺失，不作为分析环境 |','| biolearn-r | `/home/a/miniforge3/envs/biolearn-r` | R 4.4.3；R 核心包通过。环境附带 Python 3.15.0，仅为传递依赖，不用于项目 Python 分析 |','| biolearn-py | `/home/a/miniforge3/envs/biolearn-py` | Python 3.11.17；Python 核心包通过 |','| 系统 Python | `/usr/bin/python3` | 3.12.3；检查的分析模块均缺失，未覆盖或修改 |','', 'Conda 登记的环境只有 base 和上述两个隔离环境；不排除未登记或检查范围外的环境。', '', '### R 环境','', '| 包 | 状态 | 实际版本 |','| --- | --- | --- |']
for line in Path('environment/audit/r-load.log').read_text().splitlines():
 if line.startswith(('PASS\t','MISSING\t','LOAD_FAILED\t')):
  fields=[x.strip() for x in line.split('\t')]
  s.append(f"| {fields[1]} | {'library() 通过' if fields[0]=='PASS' else fields[0]} | {fields[2] if len(fields)>2 else '—'} |")
s += ['', '### Python 分析环境','', '| 模块 | 状态 | distribution 元数据版本 |','| --- | --- | --- |']
for line in Path('environment/audit/python-load.log').read_text().splitlines():
 if line.startswith(('PASS\t','MISSING\t','LOAD_FAILED\t')):
  fields=line.split('\t')
  s.append(f"| {fields[1]} | {'import 通过' if fields[0]=='PASS' else fields[0]} | {fields[2] if len(fields)>2 else '—'} |")
s += ['', '`skmisc` 的 distribution 元数据报告 0.0.0，Conda 实际包版本为 scikit-misc 0.5.3；两者分别记录，不把元数据当作仓库版本。`clusterProfiler` 是可选 GO 富集包；完整 tidyverse、Snakemake 不属于当前核心分析范围，不补装。JupyterLab 因环境依赖已存在，不是本次安装。', '', '加载使用已有环境的实际 Rscript/Python，通过 `conda run` 或绝对路径执行；没有只用 find_spec 判定通过。R 库路径为隔离环境内的 `lib/R/library`。完整 R 包版本和 Built 信息见 `environment/audit/r-installed-packages.csv`；运行时信息见 `r-load.log`。Python 解释器与导入记录见 `python-load.log`；系统、base、R 附带 Python 分别见对应 `*-python-load.log`。', '', '全量 Conda 依赖（含 build、channel、传递依赖）重新导出到 `environment/audit/biolearn-{r,py}.packages.json`、`.resolved.yml` 与 `.linux-64.explicit.txt`。这些是本次读取现有环境产生的快照。', '', '## 5. 网络连通性','', '继承当前代理环境，未修改设置，未输出代理值、密码或令牌。测试使用 `curl -I -L -sS --connect-timeout 5 --max-time 20`，正常 TLS 校验，只请求响应头；未下载软件或 PBMC3k 数据正文，未测试绕过代理的直连。', '', '| 目标 | HTTPS 请求地址 | curl exit | 最终 HTTP | TLS verify result | 用时（s） |','| --- | --- | --- | --- | --- | --- |']
for n in r['network']:
 metrics=n['metrics'].split('\t')
 s.append(f"| {n['name']} | {n['url']} | {n['exit']} | {' | '.join(metrics)} |")
s += ['', 'HTTP 200 表示这些地址本次 HEAD 连通；不保证每个实际包、Git clone、release 二进制资产、完整大文件下载或所有仓库子地址可用。Git 实际克隆、容器仓库与 nf-core 流程拉取未核实。网络原始结构化证据见 `environment/audit/host-network.json`，未保留可能含敏感信息的响应头和 curl 错误全文。', '', '## 6. 状态分类与边界','', '| 分类 | 判定 | 本次结果 |','| --- | --- | --- |','| 缺失 | 指定解释器中模块/包不存在，或工具在已说明扫描范围内未发现 | 可选 R 包、Snakemake；Docker/Java/Nextflow；系统与 base 的分析模块 |','| 已安装但未加入 PATH | 实际找到可执行文件并成功查询版本，当前 PATH 无入口 | R/Rscript、Conda/Mamba、各环境的 python |','| 加载失败 | 已发现包但实际 library()/import 报错 | 本次未发现核心包加载失败 |','| 网络失败 | 请求非零退出、超时、TLS 错误或 HTTP 失败 | 本次七个目标均未发生 |','| 未核实 | 没有执行对应验证，或证据不足 | Docker 引擎、远端 Docker 服务、完整下载/clone、完整三套 airway 分析及其差异表、真实单细胞注释/跨工具比较、nf-core 官方测试 |','', '本轮仅做环境准备与加载验收，没有重新运行此前的计算 smoke test。已有 `environment/logs/verify-*.log` 和图表属于前一轮安装验收，详见 `docs/environment-installation.md`，不能将其视为两份参考文档全部代码已验证。参考显著基因数、细胞数与簇数没有在本轮作为验收输入。', '', '审计脚本保存在 `environment/audit/check-host.py`、`check-r.R`、`check-python.py`；未安装、更新软件，未修改代理或系统运行时，未推送 GitHub，未删除已有资料。']
Path('docs/environment-audit.md').write_text('\n'.join(s)+'\n')
