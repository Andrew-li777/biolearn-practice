import json
from pathlib import Path
configfile: 'workflow/config.yaml'
ROOT=config['output_root'].rstrip('/')
CONDA=config.get('conda','/home/a/miniforge3/bin/conda')
CONTRACT=json.loads(Path('workflow/outputs.json').read_text())
DIAGNOSTIC_CONTRACT=json.loads(Path('workflow/diagnostic-outputs.json').read_text())
VALIDATION_PY=config.get('validation_python',str(Path('environment/validation-venv/bin/python').absolute()))
BULK=[ROOT+'/bulk/'+f for f in CONTRACT['bulk']]
PBMC=[ROOT+'/pbmc3k/'+f for f in CONTRACT['pbmc3k']]
VALIDATION=[ROOT+'/pbmc_validation/'+f for f in DIAGNOSTIC_CONTRACT['pbmc_validation']]
GRAPH=[ROOT+'/pbmc_graph/'+f for f in DIAGNOSTIC_CONTRACT['pbmc_graph']]
rule all:
    input: BULK+PBMC+VALIDATION+GRAPH
rule bulk_matrix:
    input:
        scripts=['scripts/'+f for f in ['01_bulk_deseq2.R','02_bulk_edger.R','03_bulk_pydeseq2.py','04_bulk_report.py','05_bulk_manifest.py']],
        runner='workflow/run_matrix.py', contract='workflow/outputs.json', methods='docs/bulk-methods.md',
        environments=['environment/biolearn-r.linux-64.explicit.txt','environment/biolearn-py.linux-64.explicit.txt']
    output: BULK
    threads: 2
    resources: mem_mb=7000
    params: out=ROOT+'/bulk', conda=CONDA
    shell: 'python workflow/run_matrix.py bulk {params.out:q} --conda {params.conda:q}'
rule pbmc_matrix:
    input:
        data=['data/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz']+['data/pbmc3k/filtered_gene_bc_matrices/hg19/'+f for f in ['matrix.mtx','genes.tsv','barcodes.tsv']],
        scripts=['scripts/'+f for f in ['10_pbmc_prepare.py','11_pbmc_seurat.R','12_pbmc_scanpy.py','13_pbmc_annotate.py','14_pbmc_annotate_seurat.R','15_pbmc_report.py','05_bulk_manifest.py','pbmc_annotation_plan.json']],
        runner='workflow/run_matrix.py', contract='workflow/outputs.json', methods='docs/pbmc3k-methods.md',
        environments=['environment/biolearn-r.linux-64.explicit.txt','environment/biolearn-py.linux-64.explicit.txt']
    output: PBMC
    threads: 2
    resources: mem_mb=7000
    params: out=ROOT+'/pbmc3k', conda=CONDA
    shell: 'python workflow/run_matrix.py pbmc3k {params.out:q} --conda {params.conda:q}'
rule pbmc_validation:
    input:
        primary=PBMC,
        scripts=['scripts/16_pbmc_validation.py','scripts/verify_pbmc_validation.py','workflow/run_pbmc_diagnostics.py'],
        contract='workflow/diagnostic-outputs.json',
        requirements='environment/validation-extra-requirements.txt'
    output: VALIDATION
    threads: 2
    resources: mem_mb=4000
    params: primary=ROOT+'/pbmc3k', out=ROOT+'/pbmc_validation', python=VALIDATION_PY, conda=CONDA
    shell: 'python workflow/run_pbmc_diagnostics.py pbmc_validation {params.primary:q} {params.out:q} --python {params.python:q} --conda {params.conda:q}'
rule pbmc_graph:
    input:
        primary=PBMC,
        scripts=['scripts/17_pbmc_graph_diagnostic.R','scripts/17_pbmc_graph_diagnostic.py','scripts/verify_pbmc_graph.py','workflow/run_pbmc_diagnostics.py'],
        contract='workflow/diagnostic-outputs.json'
    output: GRAPH
    threads: 2
    resources: mem_mb=4000
    params: primary=ROOT+'/pbmc3k', out=ROOT+'/pbmc_graph', python=VALIDATION_PY, conda=CONDA
    shell: 'python workflow/run_pbmc_diagnostics.py pbmc_graph {params.primary:q} {params.out:q} --python {params.python:q} --conda {params.conda:q}'
