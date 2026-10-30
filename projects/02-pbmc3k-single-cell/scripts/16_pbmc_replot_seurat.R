#!/usr/bin/env Rscript
# Presentation-only fix discovered during image review: opaque white PNG background.
suppressPackageStartupMessages({library(Seurat);library(ggplot2)})
out <- commandArgs(trailingOnly=TRUE)[1]
p <- function(f)file.path(out,'seurat',f)
s <- readRDS(p('analysis_annotated.rds'))
set.seed(42)
panel <- intersect(c('CD3D','CD3E','IL7R','CCR7','S100A4','CD8A','CD8B','CCL5','NKG7','GNLY','PRF1','MS4A1','CD79A','CD14','LYZ','S100A8','FCGR3A','MS4A7','LST1','FCER1A','CST3','PPBP','PF4'),rownames(s))
ggsave(p('marker_dotplot.png'),DotPlot(s,features=panel,group.by='cluster',assay='RNA',scale=TRUE)+RotatedAxis()+ggtitle('Seurat canonical marker panel: log-normalized RNA'),width=13,height=6,dpi=160,bg='white')
panel2 <- intersect(c('CD3D','IL7R','CCR7','S100A4','CD8A','CD8B','CCL5','NKG7','GNLY','MS4A1','CD79A','CD14','LYZ','S100A8','FCGR3A','MS4A7','FCER1A','CST3','PPBP','PF4'),rownames(s))
ggsave(p('marker_dotplot_cell_types.png'),DotPlot(s,features=panel2,group.by='cell_type')+RotatedAxis(),width=13,height=7,dpi=160,bg='white')
ggsave(p('umap_clusters.png'),DimPlot(s,reduction='umap',group.by='cluster',label=TRUE)+ggtitle('Seurat: Louvain, resolution 0.5, PCs 1:10'),width=8,height=6,dpi=160,bg='white')
ggsave(p('umap_cell_types.png'),DimPlot(s,reduction='umap',group.by='cell_type',label=FALSE)+ggtitle('Seurat: putative marker-based cell types'),width=11,height=6,dpi=160,bg='white')
cat('PASS presentation-only correction; counts, clustering, markers and objects unchanged\n')
