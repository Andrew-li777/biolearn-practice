validate <- function(d,s) {
 stopifnot(all(c('protein_id','gene','Reverse','Potential.contaminant','Only.identified.by.site',s$label) %in% names(d)),all(c('label','condition','replicate') %in% names(s)))
 if(anyDuplicated(d$protein_id)||anyNA(d$protein_id)||any(d$protein_id=='')) stop('Invalid protein IDs')
 if(anyDuplicated(s$label)||anyNA(s)||any(s$label=='')) stop('Invalid samples')
 if(!setequal(setdiff(names(d),c('protein_id','gene','Reverse','Potential.contaminant','Only.identified.by.site')),s$label)) stop('Sample mismatch')
 x <- as.matrix(d[,s$label,drop=FALSE]); if(!is.numeric(x)||any(x<0,na.rm=TRUE)||any(is.infinite(x))) stop('Invalid intensities')
 x[x==0] <- NA_real_; rownames(x)<-d$protein_id; x
}
keep_complete <- function(x,g) Reduce(`|`,lapply(unique(g),function(z) rowSums(!is.na(x[,g==z,drop=FALSE]))==sum(g==z)))
fit_pair <- function(x,s,treatment,control) {
 ix<-s$condition %in% c(control,treatment); ss<-s[ix,]; xx<-x[,ix,drop=FALSE]
 design<-model.matrix(~factor(ss$condition,levels=c(control,treatment)))
 fit<-limma::eBayes(limma::lmFit(xx,design))
 z<-limma::topTable(fit,coef=2,number=Inf,sort.by='none',adjust.method='BH')
 data.frame(protein_id=rownames(z),log2FC=z$logFC,pvalue=z$P.Value,padj=z$adj.P.Val)
}
