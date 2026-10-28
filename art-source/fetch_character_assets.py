"""Select CC0 MakeHuman files from the official ZIP using verified HTTP ranges.
The complete archive is large; only dependencies for this character are extracted.
"""
import io, urllib.request, zipfile, json, pathlib, struct, zlib, binascii
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent
URL = 'https://files2.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip'
OUT = ROOT / 'vendor' / 'selected-assets'

def request_range(start, length):
    if length == 0: return b''
    req = urllib.request.Request(URL, headers={'Range': f'bytes={start}-{start + length - 1}'})
    with urllib.request.urlopen(req, timeout=90) as response:
        if response.status != 206: raise RuntimeError('Server must honor byte ranges')
        data = response.read()
    if len(data) != length: raise RuntimeError('Incomplete asset response')
    return data

class RemoteFile(io.RawIOBase):
    def __init__(self):
        with urllib.request.urlopen(urllib.request.Request(URL, method='HEAD'), timeout=30) as r:
            self.size = int(r.headers['Content-Length'])
        self.position = 0
    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.position
    def seek(self, offset, whence=0):
        self.position = offset if whence == 0 else self.position + offset if whence == 1 else self.size + offset
        return self.position
    def read(self, length=-1):
        length = min(self.size - self.position, length if length >= 0 else self.size)
        data = request_range(self.position, length)
        self.position += len(data)
        return data

def extract(info):
    path = (OUT / info.filename).resolve()
    if not path.is_relative_to(OUT.resolve()): raise RuntimeError('Invalid archive path')
    if info.is_dir(): return
    if path.exists() and path.stat().st_size == info.file_size: return
    head = request_range(info.header_offset, 30)
    fields = struct.unpack('<4s5H3I2H', head)
    offset = info.header_offset + 30 + fields[9] + fields[10]
    data = request_range(offset, info.compress_size)
    if info.compress_type == 8: data = zlib.decompress(data, -15)
    elif info.compress_type != 0: raise RuntimeError('Unexpected compression')
    if len(data) != info.file_size or (binascii.crc32(data) & 0xffffffff) != info.CRC:
        raise RuntimeError('Asset CRC mismatch: ' + info.filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print(info.filename, flush=True)

if __name__ == '__main__':
    with zipfile.ZipFile(RemoteFile()) as archive:
        infos = archive.infolist()
    (ROOT / 'vendor' / 'system-index.json').write_text(json.dumps([i.filename for i in infos], indent=2))
    wanted = ['young_asian_male', 'young_african_male', 'male_casualsuit01', 'male_casualsuit02',
              'male_casualsuit03', 'male_casualsuit04', 'male_casualsuit05', 'male_casualsuit06',
              'short01', 'short02', 'eyebrow001', 'low-poly', 'brown', 'shoes01']
    chosen = [i for i in infos if not i.is_dir() and any(w in i.filename.lower() for w in wanted)]
    print(f'{len(chosen)} files, {sum(i.compress_size for i in chosen)} compressed bytes', flush=True)
    with ThreadPoolExecutor(max_workers=6) as pool: list(pool.map(extract, chosen))
