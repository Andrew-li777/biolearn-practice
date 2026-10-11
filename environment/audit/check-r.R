packages <- c('DESeq2','edgeR','airway','Seurat','apeglm','AnnotationDbi','org.Hs.eg.db','SummarizedExperiment','ggplot2','ggrepel','pheatmap','dplyr','clusterProfiler','tidyverse')
cat('R_VERSION\t',R.version.string,'\n')
cat('LIB_PATHS\t',paste(.libPaths(),collapse=';'),'\n')
for (p in packages) {
 if (!requireNamespace(p,quietly=TRUE)) {
  if (!p %in% rownames(installed.packages())) cat('MISSING\t',p,'\n') else cat('LOAD_FAILED\t',p,'\n')
  next
 }
 tryCatch({suppressPackageStartupMessages(library(p,character.only=TRUE));cat('PASS\t',p,'\t',as.character(packageVersion(p)),'\n')},error=function(e) cat('LOAD_FAILED\t',p,'\t',conditionMessage(e),'\n'))
}
write.csv(as.data.frame(installed.packages()[,c('Package','Version','LibPath','Built')]),'environment/audit/r-installed-packages.csv',row.names=FALSE)
sessionInfo()
