# Presentation-only rendering

Original official pipeline outputs remain unchanged. Fresh staged inputs exclude the previous generated MultiQC output. Inputs and executed adapter are recorded in verification/.

Executed command (2026-10-10 UTC):

```bash
sg docker -c '/usr/bin/docker run --rm -v /home/a/projects/biolearn-practice:/home/a/projects/biolearn-practice -w /home/a/projects/biolearn-practice/results/nfcore/rnaseq-3.27.0-attempt-2/presentation-corrected-4/work -e PATH=/opt/wave/.pixi/envs/default/bin:/opt/conda/bin:/usr/local/bin:/usr/bin:/bin -e PYTHONPATH=/home/a/projects/biolearn-practice/scripts/multiqc_compat -e XDG_CACHE_HOME=/home/a/projects/biolearn-practice/results/nfcore/rnaseq-3.27.0-attempt-2/presentation-corrected-4/.cache --entrypoint /opt/wave/.pixi/envs/default/bin/python community.wave.seqera.io/library/multiqc:1.35--c17fb751507e9dfc -m multiqc --force --config 1/multiqc_config.yml --config 2/multiqc_sample_merge.yml --filename multiqc_report.html --replace-names name_replacement.txt --outdir /home/a/projects/biolearn-practice/results/nfcore/rnaseq-3.27.0-attempt-2/presentation-corrected-4/output/multiqc/star_salmon .'
```

Use a fresh output directory for replay. Image source digest: sha256:ae074e961979ea85c72c6c67a8ed432fa3368c736b8fe37799f7223901ac84ab. Palette adapter only translates bare RGB strings to the equivalent rgb(...) syntax. It does not change analysis input or numeric results.
