#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(Seurat);library(ggplot2)})
out <- commandArgs(trailingOnly=TRUE)[1]
p <- function(f)file.path(out,'seurat',f)
s <- readRDS(p('analysis.rds'))
labels <- read.csv(p('cell_labels.csv'),stringsAsFactors=FALSE,colClasses=c(barcode='character',cluster='character'))
stopifnot(!anyDuplicated(labels$barcode),setequal(labels$barcode,colnames(s)))
labels <- labels[match(colnames(s),labels$barcode),]
stopifnot(all(labels$cluster==s$cluster))
s$cell_type <- labels$cell_type
s$broad_type <- labels$broad_type
ggsave(p('umap_cell_types.png'),DimPlot(s,reduction='umap',group.by='cell_type',label=FALSE)+ggtitle('Seurat: putative marker-based cell types'),width=11,height=6,dpi=160,bg="white")
panel <- intersect(c('CD3D','IL7R','CCR7','S100A4','CD8A','CD8B','CCL5','NKG7','GNLY','MS4A1','CD79A','CD14','LYZ','S100A8','FCGR3A','MS4A7','FCER1A','CST3','PPBP','PF4'),rownames(s))
ggsave(p('marker_dotplot_cell_types.png'),DotPlot(s,features=panel,group.by='cell_type')+RotatedAxis(),width=13,height=7,dpi=160,bg="white")
s@misc$annotation_note <- 'Putative canonical-marker annotation; not independently validated. See cell_type_annotation.csv and annotation_evidence.csv.'
saveRDS(s,p('analysis_annotated.rds'))
loaded <- readRDS(p('analysis_annotated.rds'))
stopifnot(identical(loaded$cell_type,s$cell_type),identical(LayerData(loaded,assay='RNA',layer='counts'),LayerData(s,assay='RNA',layer='counts')))
writeLines(c('PASS annotated RDS reopened; labels and count layer match tables','PASS cluster labels preserved after annotation'),p('annotation_object_validation.txt'))
cat('PASS Seurat annotated object and plots\n')
