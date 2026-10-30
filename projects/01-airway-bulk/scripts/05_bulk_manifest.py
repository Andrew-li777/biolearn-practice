#!/usr/bin/env python
from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1])
manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and p.name!='sha256-manifest.json'}
(root/'sha256-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'Saved SHA-256 for {len(manifest)} files')
