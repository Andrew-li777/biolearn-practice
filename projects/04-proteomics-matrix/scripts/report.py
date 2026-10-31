import csv, hashlib, html, json, sys
from pathlib import Path

root=Path(sys.argv[1])
def rows(name):
    with (root/name).open() as f: return list(csv.DictReader(f))
def table(name):
    rr=rows(name)
    if not rr: return '<p>No rows</p>'
    return '<table border="1"><tr>'+''.join('<th>'+html.escape(k)+'</th>' for k in rr[0])+'</tr>'+''.join('<tr>'+''.join('<td>'+html.escape(v)+'</td>' for v in r.values())+'</tr>' for r in rr)+'</table>'
checks=(root/'validation.log').read_text().splitlines()
assert checks and all(line.startswith('PASS:') for line in checks)
summary=rows('summary.csv')
assert len(summary)==3
for r in summary:
    name=r['contrast']; m=rows(name+'_main.csv'); ss=rows(name+'_significant.csv')
    assert len(m)==int(r['tested']) and len(ss)==int(r['effect_significant'])
    assert len({z['protein_id'] for z in m})==len(m)
    assert all(0<=float(z['padj'])<=1 and 0<=float(z['pvalue'])<=1 for z in m)
    checks.append(name+': row counts, IDs and probabilities PASS')
for p in root.glob('*.png'):
    assert p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    checks.append(p.name+': PNG signature PASS')
parts=['<meta charset="utf-8"><title>UbiLength differential enrichment</title><h1>UbiLength 差异富集分析</h1>',
'<p>蛋白互作富集实验；不代表全细胞蛋白丰度变化。单位为蛋白组，未按基因合并。主分析采用 VSN、MinProb 和 limma，逐比较 BH 校正。正效应表示处理组相对 Ctrl 富集。</p>',
'<p>MinProb 假定缺失信号偏低，并不能证明缺失机制。敏感性分析不插补，仅比较两组各至少两个观测值的蛋白。单侧缺失信号依赖插补，不作为独立验证。热图展示排名前 30 蛋白，未必全部显著。</p>']
for name in ['filter_counts.csv','sample_qc.csv','summary.csv','sensitivity_summary.csv']:
    parts.extend(['<h2>'+name+'</h2>',table(name)])
for p in sorted(root.glob('*.png')): parts.append(f'<h2>{p.stem}</h2><img width="750" src="{p.name}">')
(root/'report.html').write_text('\n'.join(parts))
(root/'acceptance.json').write_text(json.dumps({'status':'PASS','checks':checks},indent=2))
files=list(root.glob('*'))+[Path('data/DEP_1.28.0.tar.gz'),Path('data/matrix.csv'),Path('data/samples.csv')]+list(Path('scripts').glob('*'))+list(Path('environment').glob('*.txt'))+[Path('Snakefile'),Path('workflow/config.yaml')]
manifest={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file() and p.name!='sha256.json'}
(root/'sha256.json').write_text(json.dumps(manifest,indent=2))
