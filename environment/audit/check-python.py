import importlib, importlib.util, importlib.metadata as md
import sys,json
print('EXECUTABLE',sys.executable)
print('VERSION',sys.version)
modules={'numpy':'numpy','scipy':'scipy','pandas':'pandas','matplotlib':'matplotlib','seaborn':'seaborn','sklearn':'scikit-learn','scanpy':'scanpy','anndata':'anndata','igraph':'igraph','leidenalg':'leidenalg','pydeseq2':'pydeseq2','h5py':'h5py','statsmodels':'statsmodels','umap':'umap-learn','skmisc':'scikit-misc','snakemake':'snakemake','jupyterlab':'jupyterlab'}
for module,dist in modules.items():
 try:
  if importlib.util.find_spec(module) is None:
   print('MISSING',module,sep='\t');continue
  importlib.import_module(module)
  print('PASS',module,md.version(dist),sep='\t')
 except Exception as e:
  print('LOAD_FAILED',module,type(e).__name__,str(e),sep='\t')
