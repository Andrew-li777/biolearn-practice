#!/usr/bin/env Rscript
options(warn=1)
suppressPackageStartupMessages(library(edgeR))
args <- commandArgs(trailingOnly=TRUE)
outdir <- if(length(args)) args[1] else 'results/bulk'
path <- function(name) file.path(outdir,name)
cts <- as.matrix(read.csv(path('airway_counts.csv'),row.names=1,check.names=FALSE))
meta <- read.csv(path('airway_coldata.csv'),row.names=1,check.names=FALSE)
meta <- meta[colnames(cts),,drop=FALSE]
meta$cell <- factor(meta$cell)
meta$dex <- factor(meta$dex,levels=c('untrt','trt'))
stopifnot(identical(rownames(meta),colnames(cts)),all(cts>=0),all(cts==round(cts)))
design <- model.matrix(~cell+dex,meta)
stopifnot(qr(design)$rank==ncol(design),'dextrt' %in% colnames(design))
y0 <- DGEList(counts=cts)
keep <- filterByExpr(y0,design=design,min.count=10,min.total.count=15,large.n=10,min.prop=0.7)
write.csv(data.frame(gene=rownames(cts),keep=keep),path('edger_filter.csv'),row.names=FALSE)
cat('INPUT:',nrow(cts),'genes; PRE_FILTER:',sum(keep),'genes\n')
y <- y0[keep,,keep.lib.sizes=FALSE]
y <- calcNormFactors(y,method='TMM')
y <- estimateDisp(y,design,robust=TRUE)
fit <- glmQLFit(y,design,robust=TRUE,abundance.trend=TRUE)
qlf <- glmQLFTest(fit,coef=which(colnames(design)=='dextrt'))
tt <- topTags(qlf,n=Inf,adjust.method='BH',sort.by='none')$table
annotation <- read.csv(path('gene_annotation.csv'),stringsAsFactors=FALSE)
symbols <- setNames(annotation$symbol,annotation$gene)
out <- data.frame(gene=rownames(tt),symbol=unname(symbols[rownames(tt)]),log2FC=tt$logFC,logCPM=tt$logCPM,F=tt$F,pvalue=tt$PValue,padj=tt$FDR)
out$significant <- out$padj<0.1
write.csv(out,path('edger_results.csv'),row.names=FALSE)
write.csv(data.frame(sample=rownames(y$samples),y$samples,effective_library_size=y$samples$lib.size*y$samples$norm.factors),path('edger_normalization.csv'),row.names=FALSE)
writeLines(c('method=edgeR','design=~ cell + dex','contrast=dextrt; trt vs untrt','alpha=0.1','prefilter=filterByExpr(design): min.count=10, min.total.count=15, large.n=10, min.prop=0.7','normalization=TMM after resetting filtered library sizes','dispersion=estimateDisp robust=TRUE; glmQLFit robust=TRUE, abundance.trend=TRUE','test=two-sided quasi-likelihood F; default poisson.bound=TRUE','p_adjust=BH over all edgeR prefiltered genes; no DESeq2-style independent filtering','comparison_LFC=edgeR logFC; default glmQLFit prior.count=0.125 (mild prior-count shrinkage)','QL low-count handling=installed edgeR 4.4 defaults'),path('edger_method.txt'))
writeLines(capture.output(sessionInfo()),path('sessionInfo_edger.txt'))
cat('SIGNIFICANT:',sum(out$significant),'UP:',sum(out$significant & out$log2FC>0),'DOWN:',sum(out$significant & out$log2FC<0),'\nPASS edgeR analysis\n')
