#!/usr/bin/env python
from pathlib import Path
import sys,hashlib,json,tarfile,datetime
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
archive=Path('data/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz')
root=Path('data/pbmc3k')
files={}
with tarfile.open(archive,'r:gz') as tar:
 for name in ['matrix.mtx','genes.tsv','barcodes.tsv']:
  member=f'filtered_gene_bc_matrices/hg19/{name}'
  archived=tar.extractfile(member).read()
  local=(root/member).read_bytes()
  assert archived==local,f'archive/extracted file mismatch: {name}'
  files[member]=hashlib.sha256(local).hexdigest()
provenance={'verified_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_url':'https://cf.10xgenomics.com/samples/cell/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz','archive_path':str(archive),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'archive_bytes':archive.stat().st_size,'input_directory':str(root/'filtered_gene_bc_matrices/hg19'),'extracted_sha256':files,'verification':'reused existing download; each extracted file equals archive member byte-for-byte; checksum is locally computed, not an upstream authenticity signature','genome_annotation':'10x supplied hg19 gene IDs/symbols, no reference genome downloaded'}
(out/'data_source.json').write_text(json.dumps(provenance,indent=2)+'\n')
print('PASS same source archive and extracted files',provenance['archive_sha256'])
