suppressPackageStartupMessages(library(Seurat))
suppressPackageStartupMessages(library(jsonlite))
args<-commandArgs(TRUE);p<-args[1];out<-args[2];rows<-list()
for(name in c("raw_counts","analysis","analysis_annotated")){
 x<-readRDS(file.path(p,"seurat",paste0(name,".rds")))
 ct<-if(name=="raw_counts")x$counts else LayerData(x,assay="RNA",layer="counts")
 stopifnot(!anyDuplicated(colnames(ct)),!anyDuplicated(rownames(ct)),all(is.finite(ct@x)),all(ct@x>=0),all(ct@x==round(ct@x)))
 ncl<-if(name=="raw_counts")NA_integer_ else length(unique(x$cluster))
 if(name!="raw_counts"){
  d<-read.csv(file.path(p,"seurat","clusters.csv"),row.names=1,check.names=FALSE)
  stopifnot(identical(rownames(d),colnames(x)),identical(as.character(d$cluster),as.character(x$cluster)))
 }
 rows[[name]]<-list(cells=ncol(ct),genes=nrow(ct),clusters=ncl)
}
write_json(rows,out,auto_unbox=TRUE,pretty=TRUE)
