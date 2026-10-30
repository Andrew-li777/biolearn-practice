#!/usr/bin/env python
# Recompute canonical-marker percentages from integer counts to avoid accumulated mean roundoff.
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import scanpy as sc
root=Path(sys.argv[1]);folder=root/'scanpy'
a=sc.read_h5ad(folder/'analysis.h5ad')
p=pd.read_csv(folder/'canonical_marker_profiles.csv',dtype={'cluster':str})
for i,row in p.iterrows():
    cells=(a.obs.cluster.astype(str)==row.cluster).to_numpy()
    gene=a.var_names.get_loc(row.gene)
    expressed=int((a.layers['counts'][cells,gene]>0).sum())
    n=int(cells.sum())
    p.loc[i,'pct_expressing']=expressed/n*100
    p.loc[i,'expressing_cell_count']=expressed
    p.loc[i,'n_cells']=n
assert p.pct_expressing.between(0,100).all()
p.to_csv(folder/'canonical_marker_profiles.csv',index=False)
print(f'PASS {len(p)} expression percentages recomputed from integer numerators; maximum={p.pct_expressing.max()}')
