suppressPackageStartupMessages(library(DEP)); source('scripts/common.R')
a<-commandArgs(TRUE); cfg<-yaml::read_yaml(a[1]); out<-a[2];dir.create(out,recursive=TRUE,showWarnings=FALSE)
stopifnot(cfg$intensity_scale=='linear_lfq',cfg$filter=='complete_in_any_group')
d<-read.csv(cfg$matrix,check.names=FALSE);s<-read.csv(cfg$samples,check.names=FALSE)
x<-validate(d,s);stopifnot(all(c(cfg$control,unlist(cfg$contrasts)) %in% s$condition),all(table(s$condition)>=2))
write.csv(s,file.path(out,'samples.csv'),row.names=FALSE)
counts<-data.frame(stage='input',proteins=nrow(x)); active<-rep(TRUE,nrow(x))
for(f in c('Reverse','Potential.contaminant','Only.identified.by.site')) {active<-active & (is.na(d[[f]])|d[[f]]!='+');counts<-rbind(counts,data.frame(stage=paste0('after_',f),proteins=sum(active)))}
active<-active & keep_complete(x,s$condition);counts<-rbind(counts,data.frame(stage='complete_in_any_group',proteins=sum(active)))
write.csv(data.frame(protein_id=d$protein_id,retained=active),file.path(out,'filter_flags.csv'),row.names=FALSE)
x<-x[active,,drop=FALSE];ann<-d[active,c('protein_id','gene')];stopifnot(nrow(x)>2)
write.csv(counts,file.path(out,'filter_counts.csv'),row.names=FALSE)
se<-SummarizedExperiment::SummarizedExperiment(assays=list(counts=log2(x)),colData=s,rowData=S4Vectors::DataFrame(name=rownames(x),ID=rownames(x)))
norm<-DEP::normalize_vsn(se);set.seed(cfg$seed);imp<-DEP::impute(norm,fun='MinProb',q=cfg$minprob_q)
n<-SummarizedExperiment::assay(norm);im<-SummarizedExperiment::assay(imp)
saveRDS(list(raw=x,normalized=norm,imputed=imp),file.path(out,'matrices.rds'))
for(nm in c('x','n','im')) write.csv(get(nm),file.path(out,paste0('matrix_',nm,'.csv')))
qc<-data.frame(sample=s$label,group=s$condition,quantified=colSums(!is.na(x)),missing_fraction=colMeans(is.na(x)))
write.csv(qc,file.path(out,'sample_qc.csv'),row.names=FALSE)
pngplot<-function(name,fun) {png(file.path(out,paste0(name,'.png')),1000,800);fun();dev.off()}
pngplot('coverage',function() barplot(qc$quantified,names.arg=qc$sample,las=2,ylab='Quantified protein groups'))
pngplot('missingness',function() barplot(qc$missing_fraction,names.arg=qc$sample,las=2,ylab='Missing fraction'))
pngplot('distributions',function(){par(mfrow=c(2,1));boxplot(log2(x),las=2,main='log2 LFQ before VSN');boxplot(n,las=2,main='VSN (no imputation)')})
co<-cor(n,use='pairwise.complete.obs');write.csv(co,file.path(out,'correlation.csv'));pngplot('correlation',function() heatmap(co,symm=TRUE))
pc<-prcomp(t(im),center=TRUE,scale.=FALSE);pdat<-data.frame(sample=s$label,group=s$condition,pc$x[,1:2]);write.csv(pdat,file.path(out,'pca.csv'),row.names=FALSE)
pngplot('pca',function(){plot(pc$x[,1:2],col=as.integer(factor(s$condition)),pch=19,main='PCA: VSN + MinProb');text(pc$x[,1:2],labels=s$label,pos=3,cex=.7)})
summary<-list(); compar<-list()
for(tr in unlist(cfg$contrasts)) {
 key<-paste0(tr,'_vs_',cfg$control);main<-fit_pair(im,s,tr,cfg$control)
 nt<-rowSums(!is.na(n[,s$condition==tr,drop=FALSE]));nc<-rowSums(!is.na(n[,s$condition==cfg$control,drop=FALSE]));eligible<-nt>=2 & nc>=2
 sens<-data.frame(protein_id=rownames(n),n_treatment=nt,n_control=nc,reason=ifelse(eligible,'testable','fewer_than_two_observations_in_a_group'))
 if(sum(eligible)>=2) {z<-fit_pair(n[eligible,,drop=FALSE],s,tr,cfg$control);sens<-merge(sens,z,by='protein_id',all.x=TRUE,sort=FALSE)} else {sens$log2FC<-sens$pvalue<-sens$padj<-NA_real_}
 sens$reason[sens$reason=='testable' & !is.finite(sens$pvalue)]<-'not_estimable'
 main<-merge(ann,main,by='protein_id',sort=FALSE);main$fdr_significant<-main$padj<cfg$alpha;main$effect_significant<-main$fdr_significant & abs(main$log2FC)>=cfg$lfc
 write.csv(main,file.path(out,paste0(key,'_main.csv')),row.names=FALSE)
 write.csv(main[main$effect_significant,,drop=FALSE],file.path(out,paste0(key,'_significant.csv')),row.names=FALSE)
 write.csv(sens,file.path(out,paste0(key,'_sensitivity.csv')),row.names=FALSE)
 both<-merge(main,sens,by='protein_id',suffixes=c('_main','_sensitivity'));both<-both[is.finite(both$padj_sensitivity),]
 aa<-both$padj_main<cfg$alpha;bb<-both$padj_sensitivity<cfg$alpha
 compar[[key]]<-data.frame(contrast=key,common_testable=nrow(both),spearman=cor(both$log2FC_main,both$log2FC_sensitivity,method='spearman'),direction_agreement=mean(sign(both$log2FC_main)==sign(both$log2FC_sensitivity)),jaccard=if(sum(aa|bb))sum(aa&bb)/sum(aa|bb) else NA_real_)
 write.csv(both,file.path(out,paste0(key,'_comparison.csv')),row.names=FALSE)
 summary[[key]]<-data.frame(contrast=key,tested=nrow(main),fdr_significant=sum(main$fdr_significant),effect_significant=sum(main$effect_significant),sensitivity_testable=sum(is.finite(sens$padj)),one_sided_missing=sum(nt==0|nc==0))
 pngplot(paste0(key,'_volcano'),function()plot(main$log2FC,-log10(pmax(main$padj,.Machine$double.xmin)),col=ifelse(main$effect_significant,'red','grey'),pch=16,cex=.5,xlab='Treatment - Ctrl (log2 scale)',ylab='-log10 BH FDR',main=key))
 ids<-head(main$protein_id[order(main$padj)],30);hm<-im[ids,,drop=FALSE];write.csv(hm,file.path(out,paste0(key,'_heatmap.csv')))
 pngplot(paste0(key,'_heatmap'),function() heatmap(hm,scale='row',main=paste(key,'top 30; imputed; not all significant'),cexRow=.35))
}
write.csv(do.call(rbind,summary),file.path(out,'summary.csv'),row.names=FALSE)
write.csv(do.call(rbind,compar),file.path(out,'sensitivity_summary.csv'),row.names=FALSE)
capture.output(sessionInfo(),file=file.path(out,'sessionInfo.txt'));write.csv(as.data.frame(installed.packages()[,c('Package','Version')]),file.path(out,'r_packages.csv'),row.names=FALSE)
cfg$output_root<-out;yaml::write_yaml(cfg,file.path(out,'config.yaml'))
jsonlite::write_json(list(status='analysis_complete',seed=cfg$seed),file.path(out,'analysis.json'),auto_unbox=TRUE)
