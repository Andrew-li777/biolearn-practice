# README 同步维护

根 README 与四个子项目 README 的 `BEGIN VERIFIED RESULTS` / `END VERIFIED RESULTS` 区块由 `scripts/sync_readmes.py` 维护。人工编辑区块之外的目标、输入、运行步骤和局限；区块内修改会在下次生成时被替换。

唯一展示数据源为受版本控制的 `docs/results-summary.json`，保存实际读取的结果表、验证日期、运行来源路径及 SHA-256。图片位于各子项目 `docs/figures/`，根 README 和子项目引用同一文件。表格由实际 CSV/JSON 回读生成，不根据参考文档填数。

```bash
# 普通生成：只需仓库内摘要和展示图
python3 scripts/sync_readmes.py
# 只读检查：生成区块是否过期、图片校验值、两级 README 本地链接
python3 scripts/sync_readmes.py --check
# 明确刷新：需要本机已经验收的完整运行产物
python3 scripts/sync_readmes.py --refresh
```

当前刷新来源固定为 2026-10-30 的 bulk/PBMC3k `results/new-run`、nf-core `results/nfcore/new-attempt` 和蛋白组 `results/final`。脚本先检查其验收状态，再保存快照。换用新的科学运行时，必须同时更新脚本中的来源和验证日期，并核实方法说明、阈值与解释仍适用；普通检查不证明科学结果重新运行过。

本地运行路径用代码样式显示，不生成 GitHub 无法访问的报告链接。正常生成和检查不读取这些路径，也不需要 R、Conda 或第三方 Python 包。`--refresh` 会重新读取完整产物并复制展示图，不执行分析、不改变统计参数。

GitHub Actions 在 push / pull request 时执行 `--check`。失败时按提示修复链接、恢复正确展示图，或重新生成过期区块；不要手动改校验值掩盖图片来源变化。旧展示图继续保留，当前区块使用带运行日期的副本。

2026-10-31 同步仅更新文档与图片；根 docs 中旧方法文档和 shared/history 本地历史资料继续保留，维护入口为子项目 README。
