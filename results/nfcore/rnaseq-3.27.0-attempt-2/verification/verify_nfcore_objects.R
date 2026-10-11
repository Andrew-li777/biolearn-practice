args<-commandArgs(TRUE)
suppressPackageStartupMessages(library(DESeq2))
suppressPackageStartupMessages(library(jsonlite))
expected<-c('RAP1_IAA_30M_REP1','RAP1_UNINDUCED_REP1','RAP1_UNINDUCED_REP2','WT_REP1','WT_REP2')
files<-list.files(file.path(args[1],'output'),pattern='\\.(rds|RData)$',recursive=TRUE,full.names=TRUE)
rows<-list()
read_one<-function(x,file,name){
 if(!is(x,'SummarizedExperiment')){
  if(is.numeric(x))stopifnot(all(is.finite(x)))
  if(grepl('size.factor',name,ignore.case=TRUE)&&is.numeric(x))stopifnot(all(x>0))
  return(list(file=file,name=name,class=class(x),checked='readable non-SE object; numeric values finite'))
 }
 stopifnot(ncol(x)==5,!anyDuplicated(rownames(x)),!anyDuplicated(colnames(x)),setequal(colnames(x),expected))
 for(an in assayNames(x)){
  m<-assay(x,an)
  cat('Assay',an,'stored as',paste(class(m),collapse='/'),'in',file,'\n')
  if(is.data.frame(m))stopifnot(all(vapply(m,is.numeric,logical(1))))
  m<-as.matrix(m)
  stopifnot(is.numeric(m),all(is.finite(m)))
  if(grepl('counts',an))stopifnot(all(m>=0))
 }
 list(file=file,name=name,class=class(x),genes=nrow(x),samples=ncol(x),sample_ids=colnames(x),assays=assayNames(x))
}
for(file in files){
 if(grepl('\\.rds$',file)){
  rows[[length(rows)+1]]<-read_one(readRDS(file),file,'RDS')
 }else{
  e<-new.env();names<-load(file,envir=e)
  for(name in names)rows[[length(rows)+1]]<-read_one(get(name,envir=e),file,name)
 }
}
stopifnot(length(files)>0)
write_json(list(files=length(files),objects=rows,completed=TRUE),args[2],auto_unbox=TRUE,pretty=TRUE)
cat('Read back',length(files),'serialized files,',length(rows),'objects\n')
