#!/usr/bin/env python3
"""Refresh verified local evidence explicitly; render/check README snapshots offline."""
import argparse
import csv
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'docs/results-summary.json'
START, END = '<!-- BEGIN VERIFIED RESULTS -->', '<!-- END VERIFIED RESULTS -->'
PROJECTS = ['01-airway-bulk', '02-pbmc3k-single-cell', '03-nfcore-rnaseq-test', '04-proteomics-matrix']

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def refresh():
    entries = []
    for name in PROJECTS:
        base = ROOT / 'projects' / name
        sources = []
        def read(rel, kind='csv'):
            p = base / rel
            sources.append({'path': str(p.relative_to(ROOT)), 'sha256': digest(p)})
            return json.loads(p.read_text()) if kind == 'json' else list(csv.DictReader(p.open()))
        def figure(rel, title):
            p = base / rel
            dest = base / 'docs/figures' / ('verified-20261030-' + rel.replace('/', '-'))
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(p.read_bytes())
            return {'path': str(dest.relative_to(ROOT)), 'source': str(p.relative_to(ROOT)), 'sha256': digest(p), 'caption': title}
        figures = []
        if name.startswith('01'):
            data = read('results/new-run/bulk/analysis_summary.csv')
            checks = read('results/new-run/bulk/acceptance_checks.csv')
            assert all(r['status'] == 'PASS' for r in checks)
            headers = ['方法', '输入基因', '预过滤基因', 'FDR < 0.1 显著基因']
            rows = [[r[k] for k in ['method','input_genes','prefilter_genes','significant_fdr_0.1']] for r in data]
            title = 'airway bulk 差异表达'
            note = '8 个样本；设计 ~ cell + dex，trt 对 untrt。显著性不叠加效应阈值；不同方法的过滤和统计模型不同。仅分析现成计数矩阵。'
            status = f'结构与运行验收 {len(checks)}/{len(checks)} PASS。'
            figures = [figure('results/new-run/bulk/pca.png','airway：VST PCA'), figure('results/new-run/bulk/volcano.png','airway：DESeq2 火山图，颜色依据 FDR < 0.1')]
        elif name.startswith('02'):
            data = read('results/new-run/pbmc3k/analysis_summary.csv')
            met = read('results/new-run/pbmc3k/comparison_metrics.json','json')
            checks = read('results/new-run/pbmc3k/acceptance_checks.csv')
            assert all(r['status'] == 'PASS' for r in checks)
            headers = ['路线', '原始细胞', 'QC 保留细胞', '簇数']
            rows = [[r[k] for k in ['route','raw_cells','QC_pass_cells','clusters']] for r in data]
            title = 'PBMC3k 单细胞分析'
            note = f"已过滤 UMI 矩阵；共有细胞 {met['shared']}，ARI={met['ARI']:.6f}，NMI={met['NMI_arithmetic']:.6f}。细胞类型为 marker 支持的推定注释；簇数不是验收目标，两侧 UMAP 坐标不能逐点比较。"
            status = f'结构与运行验收 {len(checks)}/{len(checks)} PASS。'
            figures = [figure(f'results/new-run/pbmc3k/{r}/umap_cell_types.png',f'PBMC3k：{r} 推定细胞类型 UMAP') for r in ['seurat','scanpy']]
        elif name.startswith('03'):
            data = read('results/nfcore/new-attempt/verification/summary.json','json')
            completion = read('results/nfcore/new-attempt/completion-status.json','json')
            assert data['pass'] and completion['completed'] and completion['exit_code'] == 0
            title = 'nf-core/rnaseq 官方小型测试'
            headers = ['版本', '退出码', '完成任务 / 总任务', '独立验收通过 / 总项']
            rows = [[completion['version'],completion['exit_code'],f"{data['trace_status_counts']['COMPLETED']}/{data['trace_rows']}",f"{data['passed']}/{data['total']}"]]
            note = 'test,docker 官方小型测试；不是 airway 原始 FASTQ 的完整复现。任务与验收统计用于展示流程结果。'
            status = '运行及独立验收 PASS；版本提交 ' + completion['commit'] + '。'
        else:
            data = read('results/final/summary.csv')
            read('results/final/filter_counts.csv')
            sens = read('results/final/sensitivity_summary.csv')
            acceptance = read('results/final/acceptance.json','json')
            assert acceptance['status'] == 'PASS'
            headers = ['比较', '检验蛋白组', 'BH FDR < 0.05', '同时绝对 log2FC ≥ 1', '不插补可检验']
            rows = [[r[k] for k in ['contrast','tested','fdr_significant','effect_significant','sensitivity_testable']] for r in data]
            title = 'UbiLength 蛋白组差异富集'
            jaccard = '、'.join(f"{float(r['jaccard']):.3f}" for r in sens)
            note = f'12 个样本；DEP 1.28.0，VSN、MinProb q=0.01、seed=42、limma，逐比较 BH 校正。正效应表示处理组相对 Ctrl 富集。共同可检验集合的主路线/不插补显著集合 Jaccard 依次为 {jaccard}；Ubi1 对缺失值处理尤其敏感。属于蛋白互作富集，不代表全细胞蛋白表达变化。'
            status = '实际产物验收 PASS；固定种子复跑及缺图恢复已验证。'
            figures = [figure('results/final/pca.png','UbiLength：VSN + MinProb 后 PCA'), figure('results/final/Ubi4_vs_Ctrl_volcano.png','Ubi4 vs Ctrl：差异富集火山图'), figure('results/final/Ubi4_vs_Ctrl_heatmap.png','Ubi4 vs Ctrl：插补后排名前 30 蛋白热图，不代表全部显著')]
        entries.append(dict(project=name,title=title,verified_date='2026-10-30',headers=headers,rows=rows,note=note,status=status,sources=sources,figures=figures))
    SNAPSHOT.write_text(json.dumps({'schema_version':1,'entries':entries},ensure_ascii=False,indent=2)+'\n')

def table(headers, rows):
    def row(values):
        return '| ' + ' | '.join(str(v).replace('|', '\\|') for v in values) + ' |'
    return '\n'.join([row(headers),row(['---']*len(headers))]+[row(r) for r in rows])

def render(entry, target, overview):
    lines = []
    if overview:
        rel = os.path.relpath(ROOT/'projects'/entry['project']/'README.md',target.parent)
        lines += [f"### [{entry['title']}]({rel})",'']
    lines += [f"本机验证日期：{entry['verified_date']}。{entry['status']}",'',table(entry['headers'],entry['rows']),'',entry['note'],'']
    lines += ['结果来源（本地运行产物，未随 Git 发布）：','']
    for source in entry['sources']:
        lines += ['- `'+os.path.relpath(ROOT/source['path'],target.parent)+'`']
    lines += ['','图表与来源校验值保存在受版本控制的结果摘要中。','']
    if not overview:
        lines += ['## 结果展示','']
    for fig in entry['figures'][:2 if overview else 3]:
        rel = os.path.relpath(ROOT/fig['path'],target.parent)
        lines += [f"![{fig['caption']}]({rel})",'',fig['caption'],'']
    if not entry['figures'] and not overview:
        lines += ['本项目以上方任务完成与验收统计表展示流程结果；完整 MultiQC 为本地产物。','']
    return '\n'.join(lines).rstrip()

def sync(check=False):
    data = json.loads(SNAPSHOT.read_text())
    assert [e['project'] for e in data['entries']] == PROJECTS
    for e in data['entries']:
        for f in e['figures']:
            p = ROOT/f['path']
            if not p.is_file() or digest(p) != f['sha256']:
                raise ValueError(f"图片缺失或校验失败：{p}")
    targets = [(ROOT/'README.md',data['entries'],True)]+[(ROOT/'projects'/e['project']/'README.md',[e],False) for e in data['entries']]
    errors = []
    for p, entries, overview in targets:
        text = p.read_text()
        if text.count(START)!=1 or text.count(END)!=1:
            raise ValueError(f'生成区块标记缺失或重复：{p}')
        begin, rest = text.split(START)
        old, end = rest.split(END)
        replacement = '\n\n'+'\n\n'.join(render(e,p,overview) for e in entries)+'\n\n'
        updated = begin+START+replacement+END+end
        if updated != text:
            if check: errors.append(str(p.relative_to(ROOT))+': 生成区块过期')
            else: p.write_text(updated)
        # Check local Markdown navigation and images, ignoring examples in code fences.
        prose = re.sub(r'```.*?```','',updated,flags=re.S)
        for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',prose):
            if re.match(r'\w+://|#',link): continue
            if not (p.parent/link.split('#')[0]).exists(): errors.append(f'{p.name}: 链接缺失 {link}')
    if errors: raise ValueError('\n'.join(errors))
    print('PASS: 5 README, generated sections, image SHA-256 and local links')

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--check',action='store_true',help='Read-only; needs only versioned snapshot and images')
    group.add_argument('--refresh',action='store_true',help='Read verified local run outputs, copy figures, refresh snapshot and render')
    args=parser.parse_args()
    if args.refresh: refresh()
    sync(args.check)
