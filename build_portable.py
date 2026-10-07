"""Developer-only: build a Windows x64 ZIP whose users do not need Python."""
import hashlib,json,shutil,subprocess,sys,zipfile
from pathlib import Path
from importlib.metadata import distribution,version
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'dist'/'KR6-Live-Control-v4.1.1-portable'
OUT.mkdir(parents=True,exist_ok=True)
subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onefile','--console','--name','KR6-Installer','--add-data',str(ROOT/'systems_wrapper.lua')+';.',str(ROOT/'build_mod.py')],cwd=ROOT,check=True)
shutil.copy2(ROOT/'dist/KR6-Installer.exe',OUT/'KR6-Installer.exe')
for name in ['Install.cmd','Install.ps1','Launch.cmd','Live-Control.ps1','README.md','使用说明.txt','LICENSE']:
    shutil.copy2(ROOT/name,OUT/name)
notices=OUT/'licenses';notices.mkdir(exist_ok=True)
shutil.copy2(Path(sys.base_prefix)/'LICENSE.txt',notices/'Python-LICENSE.txt')
dist=distribution('pyinstaller')
for f in dist.files:
    if f.name in ('COPYING.txt','LICENSE','LICENSE.txt'):
        shutil.copy2(dist.locate_file(f),notices/('PyInstaller-'+f.name))
(OUT/'THIRD_PARTY_NOTICES.txt').write_text('Bundled CPython runtime: '+sys.version+'\nPyInstaller '+version('pyinstaller')+' with bootloader distribution exception.\nSee licenses/ for bundled runtime and packager notices.\nThe MOD source is MIT licensed; no game files are included.\n',encoding='utf-8')
archive=ROOT/'dist'/('KR6-Live-Control-v4.1.1-Windows-x64.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(OUT.rglob('*')):
        if f.is_file():z.write(f,OUT.name+'/'+f.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
sha=hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_suffix('.zip.sha256').write_text(sha+'  '+archive.name+'\n',encoding='ascii')
print(json.dumps({'zip':str(archive),'bytes':archive.stat().st_size,'sha256':sha},indent=2))
