from pathlib import Path
import json,hashlib,sys,datetime
from PIL import Image
out=Path(__file__).parent;root=out.parent;before=json.loads((out/'rebuild-before.json').read_text());p=Path(before['source']);held=Path(before['held']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with Image.open(p) as im:im.load();size=im.size
prov=json.loads((root/'bulk/run-provenance.json').read_text());cmds=[json.loads(s) for s in (out/'commands.jsonl').read_text().splitlines()];rebuild=next(r for r in cmds if r['label']=='matrix-rebuild')
unchanged=all(Path(n).is_file() and sha(Path(n))==h for n,h in before['unchanged_other_routes'].items());tables={n:sha(root/'bulk'/n)==h for n,h in before['bulk_statistics_before'].items()}
record=dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),image=str(p),image_decoded=size,moved_original_preserved=held.is_file() and sha(held)==before['original_sha256'],source_absent_before_rerun=before['confirmed_source_absent'],rerun_exit=rebuild['exit_code'],new_attempt=prov['attempt_directory']!=before['original_bulk_provenance']['attempt_directory'],bulk_completed=prov['completed'] and all(s['exit_code']==0 for s in prov['stages']),original_sha256=before['original_sha256'],rebuilt_sha256=sha(p),image_bytes_identical=sha(p)==before['original_sha256'],other_routes_files_checked=len(before['unchanged_other_routes']),other_routes_unchanged=unchanged,bulk_statistics_identical=tables,rerun_log=rebuild['log'])
record['pass_']=all([record['moved_original_preserved'],record['source_absent_before_rerun'],record['rerun_exit']==0,record['new_attempt'],record['bulk_completed'],record['image_bytes_identical'],unchanged,all(tables.values())])
(out/'rebuild-proof.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));sys.exit(0 if record['pass_'] else 1)
