import subprocess,shutil,os,json,datetime,pathlib,concurrent.futures
out={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tools':{},'network':[]}
def run(args,timeout=30):
 try:
  p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
  return {'exit':p.returncode,'output':(p.stdout+p.stderr).strip()}
 except subprocess.TimeoutExpired:return {'exit':None,'output':'TIMEOUT'}
for name,args in {'R':['--version'],'Rscript':['--version'],'python':['--version'],'python3':['--version'],'conda':['--version'],'mamba':['--version'],'git':['--version'],'docker':['--version'],'java':['-version'],'nextflow':['-version'],'snakemake':['--version']}.items():
 path=shutil.which(name)
 candidates=[path] if path else []
 for p in [f'/home/a/miniforge3/bin/{name}',f'/home/a/miniforge3/envs/biolearn-r/bin/{name}',f'/home/a/miniforge3/envs/biolearn-py/bin/{name}',f'/home/a/.local/bin/{name}',f'/usr/local/bin/{name}']:
  if os.path.isfile(p) and os.access(p,os.X_OK) and p not in candidates:candidates.append(p)
 out['tools'][name]={'PATH':path,'candidates':[{'path':p,**run([p]+args)} for p in candidates]}
if out['tools']['docker']['candidates']:
 out['docker_engine']=run([out['tools']['docker']['candidates'][0]['path'],'info','--format','{{json .ServerVersion}}'])
else:out['docker_engine']={'status':'UNVERIFIED','reason':'Docker CLI not found'}
urls=[('GitHub','https://github.com/conda-forge/miniforge/releases/latest'),('conda-forge','https://conda.anaconda.org/conda-forge/linux-64/repodata.json'),('bioconda','https://conda.anaconda.org/bioconda/linux-64/repodata.json'),('CRAN','https://cloud.r-project.org/'),('Bioconductor','https://bioconductor.org/packages/release/bioc/'),('PyPI','https://pypi.org/simple/scanpy/'),('PBMC3k','https://cf.10xgenomics.com/samples/cell/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz')]
def check(item):
 name,url=item
 p=subprocess.run(['curl','-I','-L','-sS','--connect-timeout','5','--max-time','20','-o','/dev/null','-w','%{http_code}\t%{ssl_verify_result}\t%{time_total}',url],capture_output=True,text=True)
 # Do not save stderr, proxy configuration, headers or authenticated URLs.
 return {'name':name,'url':url,'exit':p.returncode,'metrics':p.stdout.strip(),'status':'PASS' if p.returncode==0 and p.stdout.startswith(('200','204','206')) else 'NETWORK_FAILED'}
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:out['network']=list(pool.map(check,urls))
out['proxy_variables_present']=[k for k in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','NO_PROXY','http_proxy','https_proxy','all_proxy','no_proxy'] if k in os.environ]
out['system']={key:run(args) for key,args in {'os':['cat','/etc/os-release'],'user':['id'],'cpu':['lscpu'],'memory':['free','-b'],'disk':['df','-hT','/home/a'],'kernel':['uname','-a']}.items()}
out['conda_envs']=run(['/home/a/miniforge3/bin/conda','env','list','--json'])
pathlib.Path('environment/audit/host-network.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'tools':out['tools'],'network':out['network']},ensure_ascii=False,indent=2))
