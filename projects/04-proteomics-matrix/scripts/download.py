from pathlib import Path
import hashlib, urllib.request
p=Path('data/DEP_1.28.0.tar.gz');p.parent.mkdir(exist_ok=True)
url='https://bioconductor.org/packages/3.20/bioc/src/contrib/DEP_1.28.0.tar.gz'
expected='c870e066e73386632ad541c2c93e27f051dfebdcd53a7b99a6202086a9413300'
if not p.exists():
    tmp=p.with_suffix('.download');urllib.request.urlretrieve(url,tmp)
    assert hashlib.sha256(tmp.read_bytes()).hexdigest()==expected
    tmp.rename(p)
assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
print('Verified',url,expected)
