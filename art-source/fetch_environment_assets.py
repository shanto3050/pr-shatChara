"""Download selected original CC0 assets via Poly Haven's public API."""
import pathlib, json, urllib.request, hashlib
from concurrent.futures import ThreadPoolExecutor
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT.parent/'unity/SatChara/Assets/SatChara/Art/Environment'
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'Textures').mkdir(exist_ok=True)
tasks=[]
for name, metadata in [('island_tree_01','tree-files.json'),('barrel_03','barrel-files.json')]:
    data=json.loads((ROOT/'vendor'/metadata).read_text(encoding='utf-8-sig'))
    file=data['fbx']['1k']['fbx']
    tasks.append((file, ROOT/'vendor'/(name+'.fbx')))
    for key, value in file.get('include',{}).items():
        if ('diff' in key.lower() or 'alpha' in key.lower()) and pathlib.Path(key).suffix in ['.png','.jpg']:
            tasks.append((value,OUT/'Textures'/pathlib.Path(key).name))
data=json.loads((ROOT/'vendor'/'plaster-files.json').read_text(encoding='utf-8-sig'))
for channel in ['Diffuse','nor_gl']:
    file=data[channel]['1k']['jpg']
    tasks.append((file, OUT/'Textures'/pathlib.Path(file['url']).name))
def download(task):
    info,path=task
    if not path.exists():
        with urllib.request.urlopen(info['url'],timeout=120) as r: path.write_bytes(r.read())
    if hashlib.md5(path.read_bytes()).hexdigest()!=info['md5']: raise RuntimeError('Asset hash mismatch: '+str(path))
    print(path.name,path.stat().st_size,flush=True)
with ThreadPoolExecutor(max_workers=5) as pool: list(pool.map(download,tasks))
(ROOT/'environment-downloads.json').write_text(json.dumps([{'path':str(p.relative_to(ROOT.parent)),'url':i['url'],'md5':i['md5']} for i,p in tasks],indent=2))
