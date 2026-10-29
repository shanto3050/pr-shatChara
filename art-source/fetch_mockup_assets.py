"""Fetch only the CC0 MakeHuman files the Bablu mockup needs (byte ranges from the official asset pack).
Usage: python fetch_mockup_assets.py [--list PATTERN]
"""
import sys, json
from concurrent.futures import ThreadPoolExecutor
import zipfile
import fetch_character_assets as f

WANTED = ['skins/young_asian_male/', 'skins/young_african_male/', 'eyes/low-poly', 'eyes/materials/brown',
          'eyebrows/eyebrow001', 'eyelashes/eyelashes01', 'hair/short02']

if __name__ == '__main__':
    with zipfile.ZipFile(f.RemoteFile()) as archive:
        infos = archive.infolist()
    (f.ROOT / 'vendor').mkdir(exist_ok=True)
    (f.ROOT / 'vendor' / 'system-index.json').write_text(json.dumps([i.filename for i in infos], indent=2))
    if '--list' in sys.argv:
        pat = sys.argv[sys.argv.index('--list') + 1]
        for i in infos:
            if pat in i.filename.lower(): print(i.filename, i.file_size)
        raise SystemExit(0)
    chosen = [i for i in infos if not i.is_dir() and any(w in i.filename.lower() for w in WANTED)]
    print(f'{len(chosen)} files, {sum(i.compress_size for i in chosen)} compressed bytes', flush=True)
    with ThreadPoolExecutor(max_workers=6) as pool: list(pool.map(f.extract, chosen))
