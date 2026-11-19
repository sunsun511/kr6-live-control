"""Create a separate fused LÖVE executable; never overwrite the installed original."""
import argparse
import copy
import hashlib
import json
import shutil
import zipfile
import sys
import subprocess
import os
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path(__file__).resolve().parent
ASSETS = Path(getattr(sys,'_MEIPASS',ROOT))
SUPPORTED_SHA256 = json.loads((ASSETS/'supported.json').read_text())['source_sha256']
GAME = ORIGINAL = MOD = CONFIG = None
TARGET = 'all/systems.lua'
ORIGINAL_MEMBER = 'live_mod/original_systems.bin'

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''): h.update(b)
    return h.hexdigest()

def wrapper():
    return (ASSETS/'systems_wrapper.lua').read_bytes()

def main():
    if len(sys.argv)==1 and getattr(sys,'frozen',False):
        script=ROOT/'Install.ps1'
        if not script.exists():raise SystemExit('Please extract the entire ZIP first: Install.ps1 is missing.')
        ps=Path(__import__('os').environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
        raise SystemExit(subprocess.call([str(ps),'-NoProfile','-ExecutionPolicy','Bypass','-File',str(script)]))
    if sys.argv[1:]==['--self-test']:
        print(json.dumps({'frozen':bool(getattr(sys,'frozen',False)),'python':sys.version,'data_directory':str(ROOT),'bundled_wrapper_sha256':hashlib.sha256(wrapper()).hexdigest()}))
        return
    parser=argparse.ArgumentParser(description='Build KR6 Live Control from your own installed game. No game files are distributed.')
    parser.add_argument('--game-dir',required=True,type=Path,help='Folder containing Kingdom Rush Genesis.exe')
    parser.add_argument('--check',action='store_true',help='Validate game compatibility without installing')
    parser.add_argument('--upgrade',action='store_true',help='Replace the existing MOD after validation, retaining a local backup; exit the game first')
    args=parser.parse_args()
    game = args.game_dir.resolve()
    spec = json.loads((ASSETS/'supported.json').read_text())
    exe = game/'Kingdom Rush Genesis.exe'
    archive = game/'main.kra'
    sources = {exe: spec['source_sha256'], archive: spec['source_archive_sha256']}
    sources.update({game/name: value for name,value in spec['runtime_dll_sha256'].items()})
    for path, expected in sources.items():
        if not path.is_file() or digest(path) != expected:
            raise SystemExit(f"Unsupported or changed file: {path.name}. Expected Steam build {spec['buildid']}.")
    if args.check:
        print('Compatible:',spec['buildid'])
        return
    if shutil.disk_usage(ROOT).free < archive.stat().st_size + 150_000_000:
        raise SystemExit('Insufficient disk space in the extracted mod folder.')
    runtime = Path(tempfile.mkdtemp(prefix='runtime_'+spec['buildid']+'_',dir=ROOT))
    try:
        mod = runtime/'Kingdom Rush Genesis Live.exe'
        shutil.copy2(exe,mod)
        for name in spec['runtime_dll_sha256']:
            shutil.copy2(game/name,runtime/name)
        patched = runtime/'main.kra'
        overrides={'all/systems.lua':('systems_wrapper.lua','live_mod/original_systems.bin'),
                   'main.lua':('bootstrap.lua','live_mod/original_main.bin')}
        with zipfile.ZipFile(archive) as src, zipfile.ZipFile(patched,'w') as dst:
            for entry in src.infolist():
                data=src.read(entry)
                if entry.filename in overrides:
                    script,original=overrides[entry.filename]
                    dst.writestr(original,data,compress_type=zipfile.ZIP_DEFLATED)
                    data=(ASSETS/script).read_bytes()
                dst.writestr(copy.copy(entry),data)
        with zipfile.ZipFile(patched) as src:
            if src.testzip() is not None: raise ValueError('Archive verification failed')
        for name in ['hero_xp_multiplier.txt','live_mod_power_xp.txt','live_mod_speed.txt']:
            (runtime/name).write_text('1',encoding='ascii')
        manifest=dict(spec,mod_version='4.2.1',game_dir=str(runtime),original_game_dir=str(game),
            original_exe=str(exe),source_archive=str(archive),mod_exe=str(mod),mod_sha256=digest(mod),
            mod_archive=str(patched),mod_archive_sha256=digest(patched),config=str(runtime/'hero_xp_multiplier.txt'),
            save_dir=str(Path(os.environ['APPDATA'])/'kingdom_rush_genesis'))
        tmp=runtime/'manifest.ready'
        tmp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        os.replace(tmp,ROOT/'manifest.json')
    except BaseException:
        shutil.rmtree(runtime)
        raise
    print('Installed. Open Launch.cmd.')

if __name__=='__main__': main()
