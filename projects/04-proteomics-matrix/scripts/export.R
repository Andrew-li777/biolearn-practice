a<-commandArgs(TRUE); cfg<-yaml::read_yaml(a[1]); stopifnot(as.character(packageVersion('DEP'))=='1.28.0')
e<-new.env(); data('UbiLength',package='DEP',envir=e); data('UbiLength_ExpDesign',package='DEP',envir=e)
tmp<-tempfile();dir.create(tmp);untar(cfg$archive,files=c('DEP/data/UbiLength.rda','DEP/data/UbiLength_ExpDesign.rda'),exdir=tmp)
f<-new.env();load(file.path(tmp,'DEP/data/UbiLength.rda'),envir=f);load(file.path(tmp,'DEP/data/UbiLength_ExpDesign.rda'),envir=f)
stopifnot(identical(e$UbiLength,f$UbiLength),identical(e$UbiLength_ExpDesign,f$UbiLength_ExpDesign))
d<-f$UbiLength;s<-f$UbiLength_ExpDesign
write.csv(d,'data/raw_UbiLength.csv',row.names=FALSE)
m<-d[,c('Protein.IDs','Gene.names','Reverse','Potential.contaminant','Only.identified.by.site',paste0('LFQ.intensity.',s$label))]
names(m)<-c('protein_id','gene','Reverse','Potential.contaminant','Only.identified.by.site',s$label)
write.csv(m,cfg$matrix,row.names=FALSE);write.csv(s,cfg$samples,row.names=FALSE)
