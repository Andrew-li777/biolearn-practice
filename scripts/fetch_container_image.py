#!/usr/bin/env python3
"""Fetch exact public image references via the existing client network into Docker."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess

p = argparse.ArgumentParser()
p.add_argument('image')
p.add_argument('--out', default='environment/nfcore/image-imports-20261010')
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
out = Path(a.out)
if not out.is_absolute():
    out = root / out
out.mkdir(parents=True, exist_ok=True)
key = hashlib.sha256(a.image.encode()).hexdigest()[:20]
prefix = Path('/home/a/miniforge3/envs/biolearn-container')
env = os.environ.copy()
env['CONTAINERS_REGISTRIES_CONF'] = str(root/'environment/nfcore/registries-v2.conf')
skopeo = [str(prefix/'bin/skopeo'), '--command-timeout', '20m', '--override-os', 'linux', '--override-arch', 'amd64']
def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
with (out/(key+'.lock')).open('w') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    record = out/(key+'.json')
    check = subprocess.run(['/usr/bin/docker', 'image', 'inspect', a.image], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if check.returncode == 0 and record.exists():
        saved = json.loads(record.read_text())
        if json.loads(check.stdout)[0]['Id'] == saved.get('docker_image_id') and saved.get('completed'):
            raise SystemExit(0)
    state = {'image': a.image, 'started_utc': utc(), 'source': 'docker://'+a.image, 'transport': 'skopeo -> docker-daemon; existing client proxy inherited; no system proxy changes', 'completed': False}
    record.write_text(json.dumps(state, indent=2)+'\n')
    with (out/(key+'.log')).open('a') as log:
        cmd = skopeo+['copy', '--retry-times', '2', 'docker://'+a.image, 'docker-daemon:'+a.image]
        log.write('Started '+utc()+'\n'+'Command '+json.dumps(cmd)+'\n');log.flush()
        code = subprocess.run(cmd, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
        state.update(exit_code=code, ended_utc=utc())
        if code == 0:
            inspect = subprocess.run(skopeo+['inspect', 'docker://'+a.image], env=env, stdout=subprocess.PIPE, stderr=log)
            code = inspect.returncode
            if code == 0:
                source = json.loads(inspect.stdout)
                local = json.loads(subprocess.check_output(['/usr/bin/docker', 'image', 'inspect', a.image]))[0]
                state.update(source_digest=source['Digest'], architecture=source['Architecture'], docker_image_id=local['Id'], docker_size=local['Size'], docker_layers=local['RootFS']['Layers'], completed=True)
                (out/(key+'.source-inspect.json')).write_bytes(inspect.stdout)
        state['exit_code'] = code
        record.write_text(json.dumps(state, indent=2)+'\n')
        if code:
            print('Image import failed; full log: '+str(out/(key+'.log')))
            raise SystemExit(code)
        print('Imported '+a.image+' source_digest='+state['source_digest'], flush=True)
