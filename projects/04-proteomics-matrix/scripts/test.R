source('scripts/common.R')
s<-data.frame(label=paste0('s',1:6),condition=rep(c('Ctrl','T'),each=3),replicate=rep(1:3,2))
d<-data.frame(protein_id=c('a','b','c'),gene=c('x','x','z'),matrix(c(1,0,3,2,0,4,3,1,5,10,2,0,11,3,0,12,4,0),3,6));names(d)[3:8]<-s$label
d$Reverse<-d$Potential.contaminant<-d$Only.identified.by.site<-''
x<-validate(d,s);stopifnot(is.na(x[2,1]),all(keep_complete(x,s$condition)))
bad<-d;bad$protein_id[2]<-'a';stopifnot(inherits(try(validate(bad,s),silent=TRUE),'try-error'))
bad<-d;names(bad)[3]<-'wrong';stopifnot(inherits(try(validate(bad,s),silent=TRUE),'try-error'))
bad<-s;bad$label[2]<-bad$label[1];stopifnot(inherits(try(validate(d,bad),silent=TRUE),'try-error'))
x[1,]<-c(1,2,3,9,10,12);x[2,]<-c(2,3,4,8,10,11);x[3,]<-c(3,4,6,10,12,15)
z<-fit_pair(x,s,'T','Ctrl');stopifnot(all(z$log2FC>0))
y<-x;y[1,c(1,4)]<-NA;stopifnot(!keep_complete(y,s$condition)[1]);y[2,1:3]<-NA
stopifnot(rowSums(!is.na(y[,1:3]))[2]<2)
cat('PASS: IDs, sample alignment, zero conversion, filter boundary, direction, missing group\n')
