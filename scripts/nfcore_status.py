from pathlib import Path
import sys,json,datetime,csv,shutil
p=Path(sys.argv[1]);code=int((p/'exit-code.txt').read_text())
reports=[f for f in (p/'output').rglob('*multiqc_report.html') if f.stat().st_size>0]
trace=p/'execution-trace.tsv'
rows=list(csv.DictReader(trace.open(),delimiter='\t')) if trace.exists() else []
last={r['name']:r for r in rows}
unresolved=[r for r in last.values() if r['status'] not in ['COMPLETED','CACHED'] or r['exit'] not in ['0','-']]
trace_ok=bool(rows) and not unresolved
console=(p/'console.log').read_text(errors='replace')
status={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pipeline':'nf-core/rnaseq','version':'3.27.0','commit':(p/'pipeline-commit.txt').read_text().strip(),'profile':'test,docker','exit_code':code,'multiqc_reports':[str(f) for f in reports],'trace_rows':len(rows),'trace_status_counts':{s:sum(r['status']==s for r in rows) for s in set(r['status'] for r in rows)},'unresolved_tasks':unresolved,'completed':code==0 and bool(reports) and trace_ok,'scope':'Official small test dataset; NOT a reproduction of airway original FASTQ.'}
status['blocker']='Docker runtime missing' if 'docker: command not found' in console or 'docker: command not found' in console.lower() else None
status['state']='completed' if status['completed'] else ('blocked_container_runtime_missing' if status['blocker'] else 'failed_or_incomplete')
(p/'completion-status.json').write_text(json.dumps(status,indent=2)+'\n')
shutil.copy2(__file__,p/'nfcore_status.executed.py')
print(json.dumps(status,indent=2))
