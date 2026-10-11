from pathlib import Path
import sys,json,datetime
p=Path(sys.argv[1]);code=int((p/'exit-code.txt').read_text())
reports=list((p/'output').glob('multiqc/*multiqc_report.html'))
console=(p/'console.log').read_text(errors='replace')
status={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pipeline':'nf-core/rnaseq','version':'3.27.0','commit':(p/'pipeline-commit.txt').read_text().strip(),'profile':'test,docker','exit_code':code,'multiqc_reports':[str(f) for f in reports],'completed':code==0 and bool(reports),'scope':'Official small test dataset; NOT a reproduction of airway original FASTQ.'}
status['blocker']='Docker runtime missing' if 'docker: command not found' in console or 'docker: command not found' in console.lower() else None
status['state']='completed' if status['completed'] else ('blocked_container_runtime_missing' if status['blocker'] else 'failed_or_incomplete')
(p/'completion-status.json').write_text(json.dumps(status,indent=2)+'\n')
print(json.dumps(status,indent=2))
