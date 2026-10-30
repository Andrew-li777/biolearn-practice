#!/usr/bin/env python3
"""Read back official-test products, task exits and complete run evidence."""
from pathlib import Path
import sys,json,hashlib,zipfile,gzip,subprocess,datetime
import pandas as pd
import numpy as np
p=Path(sys.argv[1]);out=p/'verification';out.mkdir(exist_ok=True);checks=[]
def check(n,ok,d):checks.append({'check':n,'pass':bool(ok),'detail':d})
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
check('workflow exit zero',int((p/'exit-code.txt').read_text())==0,(p/'exit-code.txt').read_text().strip())
expected='a1fcdddd3b826fe46eb46f0479f2ff8a7815af05'
check('fixed pipeline commit',(p/'pipeline-commit.txt').read_text().strip()==expected,expected)
trace=pd.read_csv(p/'execution-trace.tsv',sep='\t',dtype=str,keep_default_na=False)
last=trace.drop_duplicates('name',keep='last')
check('all final tasks completed',len(trace)>0 and last.status.isin(['COMPLETED','CACHED']).all() and last.exit.isin(['0','-']).all(),{'rows':len(trace),'statuses':trace.status.value_counts().to_dict()})
tasklogs=[]
for _,r in trace.iterrows():
    prefix,suffix=r['hash'].split('/')
    candidates=list((p/'work'/prefix).glob(suffix+'*'))
    if len(candidates)!=1:
        check('task '+r['hash']+' local work',False,[str(x) for x in candidates]);continue
    work=candidates[0]
    ec=(work/'.exitcode').read_text().strip() if (work/'.exitcode').is_file() else None
    check('task '+r['hash']+' actual exit matches trace',ec==r['exit'],{'task':r['name'],'exit':ec})
    for name in ['.command.sh','.command.run','.command.out','.command.err','.command.log']:
        f=work/name
        if f.is_file():
            text=f.read_text(errors='replace')
            tasklogs.append({'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f),'error_warning_lines':[line for line in text.splitlines() if any(s in line.lower() for s in ['error','warn','exception','fatal'])]})
console=(p/'console.log').read_text(errors='replace');detail=(p/'nextflow.log').read_text(errors='replace')
check('workflow success log','Pipeline completed successfully' in console or 'Execution complete' in console,console[-1800:])
logsummary={'console_sha256':sha(p/'console.log'),'nextflow_sha256':sha(p/'nextflow.log'),'console_warning_lines':[l for l in console.splitlines() if 'WARN' in l],'detailed_error_lines':[l for l in detail.splitlines() if ' ERROR ' in l]}
check('no unhandled Nextflow errors',not logsummary['detailed_error_lines'],logsummary['detailed_error_lines'])
params_files=list((p/'output/pipeline_info').glob('params_*.json'))
check('one parameter snapshot',len(params_files)==1,[str(x) for x in params_files])
params=json.loads(params_files[0].read_text())
check('official test input and algorithms','626c8fab639062eade4b10747e919341cbf9b41a/samplesheet/v3.10/samplesheet_test.csv' in params['input'] and params['aligner']=='star_salmon' and params['pseudo_aligner']=='salmon',{'input':params['input'],'aligner':params['aligner'],'pseudo_aligner':params['pseudo_aligner']})
samplesheets=list((p/'work').glob('stage-*/*/*/samplesheet_test.csv'))
sheet=pd.read_csv(samplesheets[0]) if len(samplesheets)==1 else pd.DataFrame()
check('actual samplesheet lanes uniquely identified',len(sheet)==7 and sheet['sample'].nunique()==5 and not sheet.duplicated(['sample','fastq_1','fastq_2']).any() and sheet.groupby('sample').strandedness.nunique().eq(1).all(),{'rows':len(sheet),'sample_ids':sheet['sample'].tolist() if len(sheet) else [],'note':'Repeated sample IDs are official lane merging, not duplicate result columns.'})
reports=list((p/'output').rglob('*multiqc_report.html'))
check('MultiQC nonempty readable',len(reports)>=1 and all(f.stat().st_size>10000 and '<html' in f.read_text(errors='replace').lower() for f in reports),[str(x) for x in reports])
mqdata=list((p/'output').rglob('multiqc_data.json'))
check('MultiQC data JSON readable',bool(mqdata) and all(isinstance(json.loads(f.read_text()),dict) for f in mqdata),[str(x) for x in mqdata])
rawzip=list((p/'output/fastqc/raw').glob('*.zip'));trimzip=list((p/'output/fastqc/trim').glob('*.zip'))
check('raw and trimmed FastQC eight read files',len(rawzip)==8 and len(trimzip)==8,{'raw':len(rawzip),'trimmed':len(trimzip)})
for f in rawzip+trimzip:
    with zipfile.ZipFile(f) as z:
        good=z.testzip() is None and any(n.endswith('/fastqc_data.txt') for n in z.namelist())
    check(str(f.relative_to(p))+' readable ZIP',good,f.stat().st_size)
matrices=list((p/'output').rglob('*merged*gene_counts.tsv'))
check('both quantification branches merged gene matrices',len(matrices)>=2,[str(f) for f in matrices])
matrixstats=[]
expected_samples={'RAP1_IAA_30M_REP1','RAP1_UNINDUCED_REP1','RAP1_UNINDUCED_REP2','WT_REP1','WT_REP2'}
for f in matrices:
    df=pd.read_csv(f,sep='\t')
    samplecols=[c for c in df if c in expected_samples]
    values=df[samplecols].to_numpy()
    identifiers=df.iloc[:,0].astype(str)
    check(str(f.relative_to(p))+' sample IDs/gene IDs/count ranges',len(df)>0 and identifiers.is_unique and len(samplecols)==5 and set(samplecols)==expected_samples and np.isfinite(values).all() and (values>=0).all(),{'genes':len(df),'samples':samplecols,'min':float(values.min()) if values.size else None,'max':float(values.max()) if values.size else None})
    matrixstats.append({'path':str(f),'genes':len(df),'columns':list(df),'sample_columns':samplecols,'NA':df.isna().sum().loc[lambda x:x>0].to_dict()})
bams=list((p/'output/star_salmon').glob('*.bam'))
check('five final alignment BAMs',len(bams)==5,[str(f) for f in bams])
if bams:
    project=Path.cwd().resolve()
    cmd=['/usr/bin/docker','run','--rm','-v',str(project)+':'+str(project)+':ro',
         'community.wave.seqera.io/library/htslib_samtools:1.24--d697cfb9dce007cd',
         'samtools','quickcheck','-v']+[str(f.resolve()) for f in bams]
    result=subprocess.run(cmd,capture_output=True,text=True)
    (out/'bam-quickcheck.log').write_text(json.dumps(cmd)+'\n'+result.stdout+result.stderr+'\nExit code: '+str(result.returncode)+'\n')
    check('BAMs actual samtools quickcheck',result.returncode==0,{'exit_code':result.returncode,'evidence':str(out/'bam-quickcheck.log')})
# Input downloads and published outputs are hashed from this attempt, not inferred
# from remote reference numbers. A zero-size optional file is inventoried explicitly.
files=[]
for f in (p/'output').rglob('*'):
    if f.is_file():files.append({'path':str(f.relative_to(p)),'bytes':f.stat().st_size,'sha256':sha(f)})
downloads=[]
for f in (p/'work').glob('stage-*/*/*/*'):
    if f.is_file():
        if f.suffix=='.gz':
            with gzip.open(f,'rb') as stream:
                while stream.read(1024*1024):pass
        downloads.append({'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f)})
check('actual staged downloads readable',bool(downloads),{'files':len(downloads)})
summary={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pass':all(x['pass'] for x in checks),'passed':sum(x['pass'] for x in checks),'total':len(checks),'scope':'Official nf-core/rnaseq3.27.0 test; NOT airway original FASTQ reproduction.','trace_rows':len(trace),'trace_status_counts':trace.status.value_counts().to_dict(),'outputs':len(files),'download_files':len(downloads),'matrices':matrixstats}
for name,data in [('checks.json',checks),('summary.json',summary),('full_task_logs.json',tasklogs),('engine_log_summary.json',logsummary),('output_manifest.json',files),('download_manifest.json',downloads)]:
    (out/name).write_text(json.dumps(data,indent=2,default=str)+'\n')
print(json.dumps(summary,indent=2))
for x in checks:
    if not x['pass']:print('FAIL',x)
sys.exit(0 if summary['pass'] else 1)
