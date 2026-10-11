from pathlib import Path
import hashlib,json,sys,datetime
out=Path(__file__).parent;before=json.loads((out/'historical-results-before.json').read_text());reuse=json.loads((out/'reuse-input-hashes.json').read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
bad=[n for n,h in before.items() if not Path(n).is_file() or sha(Path(n))!=h]
inputs=[n for n,h in reuse.items() if not Path(n).is_file() or sha(Path(n))!=h]
record=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),historical_files=len(before),changed_or_missing=bad,reused_files=len(reuse),reused_changed_or_missing=inputs,pass_=not bad and not inputs)
(out/'preservation-check.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));sys.exit(0 if record['pass_'] else 1)
