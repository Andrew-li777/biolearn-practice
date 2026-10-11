#!/usr/bin/env Rscript
options(warn=1)
suppressPackageStartupMessages({library(Seurat);library(Matrix);library(ggplot2);library(patchwork)})
a <- commandArgs(trailingOnly=TRUE);out <- a[1];input <- a[2]
dir.create(out,recursive=TRUE,showWarnings=FALSE)
p <- function(x) file.path(out,x)
set.seed(42)
features <- read.delim(file.path(input,'genes.tsv'),header=FALSE,stringsAsFactors=FALSE)
barcodes <- readLines(file.path(input,'barcodes.tsv'))
stopifnot(!anyDuplicated(barcodes),!anyDuplicated(features$V1))
x <- as(readMM(file.path(input,'matrix.mtx')),'CsparseMatrix')
rownames(x) <- features$V1;colnames(x) <- barcodes
stopifnot(all(x@x>=0),all(x@x==round(x@x)))
saveRDS(list(counts=x,features=data.frame(gene_id=features$V1,symbol=features$V2),barcodes=barcodes),p('raw_counts.rds'))
raw <- readRDS(p('raw_counts.rds'))
stopifnot(identical(raw$counts,x))
raw_qc <- data.frame(barcode=barcodes,total_counts=Matrix::colSums(x),n_genes=Matrix::colSums(x>0),pct_mt=100*Matrix::colSums(x[grepl('^MT-',features$V2),,drop=FALSE])/Matrix::colSums(x))
write.csv(raw_qc,p('qc_raw.csv'),row.names=FALSE)
# Stable gene IDs in raw object; explicitly retain symbol-to-ID mapping for analysis.
analysis_names <- make.unique(gsub('_','-',features$V2))
rownames(x) <- analysis_names
feature_map <- data.frame(gene_id=features$V1,source_symbol=features$V2,analysis_gene=analysis_names)
write.csv(feature_map,p('feature_map.csv'),row.names=FALSE)
s <- CreateSeuratObject(counts=x,project='pbmc3k',min.cells=3,min.features=200)
s[['percent.mt']] <- PercentageFeatureSet(s,pattern='^MT-')
qc <- data.frame(barcode=colnames(s),s[[]],check.names=FALSE)
qc$keep <- qc$nFeature_RNA>200 & qc$nFeature_RNA<2500 & qc$percent.mt<5
qc$fail_low_genes <- qc$nFeature_RNA<=200
qc$fail_high_genes <- qc$nFeature_RNA>=2500
qc$fail_mt <- qc$percent.mt>=5
write.csv(qc,p('qc_before.csv'),row.names=FALSE)
qc_long <- rbind(data.frame(barcode=qc$barcode,metric='detected_genes',value=qc$nFeature_RNA,keep=qc$keep),data.frame(barcode=qc$barcode,metric='total_UMI',value=qc$nCount_RNA,keep=qc$keep),data.frame(barcode=qc$barcode,metric='mitochondrial_percent',value=qc$percent.mt,keep=qc$keep))
g <- ggplot(qc_long,aes(x=factor(keep),y=value,fill=factor(keep)))+geom_violin(scale='width')+geom_boxplot(width=.15,outlier.shape=NA)+facet_wrap(~metric,scales='free_y',nrow=1)+theme_bw()+labs(x='Pass QC',fill='Pass QC',title='Seurat QC before cell filtering')
ggsave(p('qc_violin.png'),g,width=11,height=4,dpi=160,bg="white")
g <- ggplot(qc,aes(nCount_RNA,nFeature_RNA,color=percent.mt,shape=keep))+geom_point(size=.7,alpha=.7)+geom_hline(yintercept=c(200,2500),linetype=2)+theme_bw()+labs(title='Seurat QC: UMI vs detected genes',color='MT %')
ggsave(p('qc_scatter.png'),g,width=7,height=5,dpi=160,bg="white")
s <- subset(s,cells=qc$barcode[qc$keep])
write.csv(data.frame(barcode=colnames(s),s[[]]),p('qc_after.csv'),row.names=FALSE)
s <- NormalizeData(s,normalization.method='LogNormalize',scale.factor=10000,verbose=FALSE)
s <- FindVariableFeatures(s,selection.method='vst',nfeatures=2000,verbose=FALSE)
write.csv(data.frame(gene=VariableFeatures(s)),p('highly_variable_genes.csv'),row.names=FALSE)
s <- ScaleData(s,features=VariableFeatures(s),vars.to.regress=NULL,scale.max=10,verbose=FALSE)
s <- RunPCA(s,features=VariableFeatures(s),npcs=50,seed.use=42,verbose=FALSE)
s <- FindNeighbors(s,dims=1:10,k.param=20,nn.method='annoy',annoy.metric='euclidean',prune.SNN=1/15,verbose=FALSE)
s <- FindClusters(s,resolution=.5,algorithm=1,random.seed=42,n.start=10,n.iter=10,verbose=FALSE)
s$cluster <- as.character(Idents(s))
# Single-factor comparison on exactly the same SNN graph.
s1 <- FindClusters(s,resolution=1,algorithm=1,random.seed=42,n.start=10,n.iter=10,verbose=FALSE)
s$experiment_resolution_1 <- as.character(Idents(s1))
write.csv(data.frame(barcode=colnames(s),cluster=s$experiment_resolution_1),p('experiment_resolution_1.csv'),row.names=FALSE)
Idents(s) <- 'cluster'
s <- RunUMAP(s,dims=1:10,umap.method='uwot',n.neighbors=30,min.dist=.3,metric='cosine',seed.use=42,verbose=FALSE)
emb <- Embeddings(s,'umap')
write.csv(data.frame(barcode=rownames(emb),UMAP1=emb[,1],UMAP2=emb[,2]),p('umap_coordinates.csv'),row.names=FALSE)
write.csv(data.frame(barcode=colnames(s),cluster=s$cluster),p('clusters.csv'),row.names=FALSE)
ggsave(p('umap_clusters.png'),DimPlot(s,reduction='umap',group.by='cluster',label=TRUE)+ggtitle('Seurat: Louvain, resolution 0.5, PCs 1:10'),width=8,height=6,dpi=160,bg="white")
# Marker tests on RNA log-normalized expression, never scale.data.
markers <- FindAllMarkers(s,assay='RNA',slot='data',test.use='wilcox',only.pos=FALSE,min.pct=.25,logfc.threshold=.25,return.thresh=1,random.seed=42,verbose=TRUE)
write.csv(markers,p('markers_all_tested.csv'),row.names=FALSE)
positive <- markers[markers$avg_log2FC>0 & markers$p_val_adj<.05,,drop=FALSE]
write.csv(positive,p('markers_positive.csv'),row.names=FALSE)
panel <- c('CD3D','CD3E','IL7R','CCR7','S100A4','CD8A','CD8B','CCL5','NKG7','GNLY','PRF1','MS4A1','CD79A','CD14','LYZ','S100A8','FCGR3A','MS4A7','LST1','FCER1A','CST3','PPBP','PF4')
panel <- intersect(panel,rownames(s))
dot <- DotPlot(s,features=panel,group.by='cluster',assay='RNA',scale=TRUE)+RotatedAxis()+ggtitle('Seurat canonical marker panel: log-normalized RNA')
ggsave(p('marker_dotplot.png'),dot,width=13,height=6,dpi=160,bg="white")
write.csv(dot$data,p('marker_dotplot_values.csv'),row.names=FALSE)
expr <- LayerData(s,assay='RNA',layer='data')[panel,,drop=FALSE]
cts <- LayerData(s,assay='RNA',layer='counts')[panel,,drop=FALSE]
profile <- do.call(rbind,lapply(sort(unique(s$cluster)),function(cl){ix <- s$cluster==cl;data.frame(cluster=cl,gene=panel,mean_log1p=Matrix::rowMeans(expr[,ix,drop=FALSE]),pct_expressing=100*Matrix::rowMeans(cts[,ix,drop=FALSE]>0),n_cells=sum(ix))}))
write.csv(profile,p('canonical_marker_profiles.csv'),row.names=FALSE)
saveRDS(s,p('analysis.rds'))
# Reopen on disk; verify counts and cell IDs before reporting success.
loaded <- readRDS(p('analysis.rds'))
stopifnot(identical(colnames(loaded),colnames(s)),identical(LayerData(loaded,assay='RNA',layer='counts'),LayerData(s,assay='RNA',layer='counts')),all(is.finite(Embeddings(loaded,'umap'))))
original <- x[rownames(s),colnames(s),drop=FALSE]
stopifnot(all(LayerData(s,assay='RNA',layer='counts')==original))
writeLines(c('PASS raw RDS reopened and equals source counts','PASS analysis RDS reopened; counts equal source subset; UMAP finite','PASS no duplicate source or postQC barcodes'),p('object_validation.txt'))
writeLines(c('QC=min.cells=3 gene prefilter; min.features=200 initialization; then strict 200<nFeature_RNA<2500, percent.mt<5','QC metrics computed after gene prefilter; raw metrics also retained','normalization=LogNormalize scale.factor=10000','HVG=vst nfeatures=2000','scaling=HVG only; mean-center, unit variance, scale.max=10; no regression','PCA=50 computed; PCs 1:10 used','neighbors=Annoy Euclidean k=20; SNN prune=1/15','clustering=Louvain algorithm=1; resolution=0.5; seed=42; n.start=10,n.iter=10','UMAP=uwot cosine; dims1:10, n.neighbors=30, min.dist=0.3, seed=42','markers=Wilcoxon RNA/data; all other cells as reference; min.pct=0.25, logfc.threshold=0.25; return.thresh=1; positive subset p_val_adj<0.05','marker_p_adjust=Seurat Bonferroni across all genes in assay; exploratory single-donor markers','seed=42','experiment=resolution=1 on same SNN graph, all else fixed'),p('method.txt'))
writeLines(capture.output(sessionInfo()),p('sessionInfo.txt'))
write.csv(as.data.frame(installed.packages()[,c('Package','Version','Built')]),p('r_installed_packages.csv'),row.names=FALSE)
cat('INPUT',nrow(x),'genes',ncol(x),'cells; POSTQC',nrow(s),'genes',ncol(s),'cells; CLUSTERS',length(unique(s$cluster)),'\n')
cat('PASS Seurat analysis, markers, plots, raw and analysis RDS\n')
