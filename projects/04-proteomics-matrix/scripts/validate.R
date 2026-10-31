a<-commandArgs(TRUE);o<-a[1];r<-readRDS(file.path(o,'matrices.rds'));s<-read.csv(file.path(o,'samples.csv'))
n<-SummarizedExperiment::assay(r$normalized);im<-SummarizedExperiment::assay(r$imputed)
stopifnot(identical(colnames(n),s$label),identical(dim(n),dim(im)),all(is.finite(im)),all(im[!is.na(n)]==n[!is.na(n)]))
for(tr in c('Ubi1','Ubi4','Ubi6')) {
 z<-read.csv(file.path(o,paste0(tr,'_vs_Ctrl_main.csv')))
 stopifnot(isTRUE(all.equal(z$padj,p.adjust(z$pvalue,'BH'))))
 expected<-rowMeans(im[,s$condition==tr])-rowMeans(im[,s$condition=='Ctrl'])
 stopifnot(max(abs(z$log2FC-expected[match(z$protein_id,rownames(im))]))<1e-8)
 sens<-read.csv(file.path(o,paste0(tr,'_vs_Ctrl_sensitivity.csv')))
 stopifnot(all(is.na(sens$padj[sens$n_treatment<2|sens$n_control<2])))
}
for(p in list.files(o,pattern='[.]csv$',full.names=TRUE))read.csv(p,check.names=FALSE)
cat('PASS: serialized objects, sample order, imputation mask, BH, contrast direction, sensitivity exclusions, all CSV readback\n')

for(p in list.files(o,pattern='[.]png$',full.names=TRUE))stopifnot(length(png::readPNG(p))>0)
cat('PASS: all PNG images decoded\n')
