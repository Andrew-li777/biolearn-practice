import sys,subprocess,json,datetime,pathlib,shlex
out=pathlib.Path(__file__).parent
label=sys.argv[1];cmd=sys.argv[2:]
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (out/(label+'.log')).open('w') as f:
 f.write('Command: '+shlex.join(cmd)+'\nStarted UTC: '+start+'\n');f.flush()
 code=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT).returncode
 end=datetime.datetime.now(datetime.timezone.utc).isoformat();f.write(f'\nEnded UTC: {end}\nExit code: {code}\n')
with (out/'commands.jsonl').open('a') as f:f.write(json.dumps(dict(label=label,command=cmd,cwd=str(pathlib.Path.cwd()),started_utc=start,ended_utc=end,exit_code=code,log=str(out/(label+'.log'))))+'\n')
print(label,'exit=',code,flush=True);sys.exit(code)
