"""Create a separate fused LÖVE executable; never overwrite the installed original."""
import argparse
import copy
import hashlib
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUPPORTED_SHA256 = 'ea9d367b89aa879fc013fdd790be46e44b89b6c4515f29dc4ebddddf2d0340dd'
GAME = ORIGINAL = MOD = CONFIG = None
TARGET = 'all/systems.lua'
ORIGINAL_MEMBER = 'live_mod/original_systems.bin'

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''): h.update(b)
    return h.hexdigest()

def wrapper():
    return (ROOT/'systems_wrapper.lua').read_bytes()

def main():
    global GAME, ORIGINAL, MOD, CONFIG
    parser=argparse.ArgumentParser(description='Build KR6 Live Control from your own installed game. No game files are distributed.')
    parser.add_argument('--game-dir',required=True,type=Path,help='Folder containing Kingdom Rush Genesis.exe')
    parser.add_argument('--check',action='store_true',help='Validate game compatibility without installing')
    parser.add_argument('--upgrade',action='store_true',help='Replace the existing MOD after validation, retaining a local backup; exit the game first')
    args=parser.parse_args()
    GAME=args.game_dir.resolve()
    ORIGINAL=GAME/'Kingdom Rush Genesis.exe'
    MOD=GAME/'Kingdom Rush Genesis Live V4 Mod.exe'
    CONFIG=GAME/'hero_xp_multiplier.txt'
    if not ORIGINAL.is_file(): raise SystemExit('Game EXE not found in selected folder')
    before=digest(ORIGINAL)
    if before!=SUPPORTED_SHA256: raise SystemExit('Unsupported game build. This version supports Steam build 25661788 only; original file was not modified.')
    if args.check:
        print('Compatible: original SHA-256 matches supported build 25661788')
        return
    if MOD.exists() and not args.upgrade: raise SystemExit('MOD already exists; use --upgrade after exiting the game to keep a backup and replace it.')
    if shutil.disk_usage(GAME).free < ORIGINAL.stat().st_size + 100_000_000:
        raise SystemExit('Not enough disk space for a separate mod executable')
    temp = GAME / 'Kingdom Rush Genesis Live V4 Mod.exe.building'
    if temp.exists(): raise SystemExit('Staging file already exists; inspect before retrying')
    patch = wrapper()
    assert patch
    with zipfile.ZipFile(ORIGINAL) as source:
        entries = sorted(source.infolist(), key=lambda e: e.header_offset)
        prefix_size = entries[0].header_offset
        payload = source.read(TARGET)
        assert payload.startswith(b'\x1bLJ'), 'Expected LuaJIT systems'
        with ORIGINAL.open('rb') as inp, temp.open('wb') as out:
            out.write(inp.read(prefix_size))
        # Copy compressed local-file records unchanged, then rebuild central directory.
        with ORIGINAL.open('rb') as inp, zipfile.ZipFile(temp, 'a', compression=zipfile.ZIP_DEFLATED) as out:
            for i, entry in enumerate(entries):
                if entry.filename == TARGET: continue
                end = entries[i+1].header_offset if i+1<len(entries) else source.start_dir
                new = copy.copy(entry)
                new.header_offset = out.fp.tell()
                inp.seek(entry.header_offset)
                remaining = end-entry.header_offset
                while remaining:
                    data = inp.read(min(4*1024*1024, remaining))
                    if not data: raise IOError('Unexpected EOF')
                    out.fp.write(data); remaining -= len(data)
                out.filelist.append(new); out.NameToInfo[new.filename] = new
                out.start_dir = out.fp.tell(); out._didModify = True
            out.writestr(ORIGINAL_MEMBER, payload)
            out.writestr(TARGET, patch)
    with zipfile.ZipFile(temp) as z, zipfile.ZipFile(ORIGINAL) as original:
        assert len(z.namelist()) == len(set(z.namelist()))
        assert set(z.namelist()) == set(original.namelist()) | {ORIGINAL_MEMBER}
        assert z.read(TARGET) == patch and z.read(ORIGINAL_MEMBER) == original.read(TARGET)
        for info in original.infolist():
            if info.filename != TARGET:
                other = z.getinfo(info.filename)
                assert (info.CRC, info.file_size, info.compress_size) == (other.CRC, other.file_size, other.compress_size)
        bad = z.testzip()
        assert bad is None, f'CRC failed: {bad}'
    with ORIGINAL.open('rb') as a, temp.open('rb') as b:
        assert a.read(prefix_size) == b.read(prefix_size)
    assert before == digest(ORIGINAL), 'Original file changed during build'
    if not CONFIG.exists(): CONFIG.write_text('1\n', encoding='ascii')
    mod_backup=None
    if MOD.exists():
        backup=ROOT/'mod_backups'/datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        backup.mkdir(parents=True)
        mod_backup=backup/MOD.name
        shutil.copy2(MOD,mod_backup)
        assert digest(mod_backup)==digest(MOD),'Existing MOD backup mismatch'
        if (ROOT/'manifest.json').exists():shutil.copy2(ROOT/'manifest.json',backup/'manifest.json')
    temp.replace(MOD)
    save_dir = Path.home()/'AppData/Roaming/kingdom_rush_genesis'
    snapshot = ROOT/'save_backups'/('before_mod_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
    if save_dir.exists(): shutil.copytree(save_dir, snapshot)
    manifest = {
        'game_dir':str(GAME), 'original_exe':str(ORIGINAL), 'mod_exe':str(MOD),
        'config':str(CONFIG), 'save_dir':str(save_dir), 'initial_save_backup':str(snapshot),
        'source_sha256':before, 'mod_sha256':digest(MOD), 'native_prefix_bytes':prefix_size,
        'replaced_member':TARGET, 'added_member':ORIGINAL_MEMBER,
        'default_multiplier':1, 'original_unchanged':True, 'zip_crc_check':'PASS',
        'gameplay_test':'NOT_RUN', 'buildid':'25661788',
        'mod_version':'4.1', 'previous_mod_backup':str(mod_backup) if mod_backup else None,
    }
    (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
