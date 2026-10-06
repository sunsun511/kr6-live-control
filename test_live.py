import json, zipfile, os
from pathlib import Path
from lua_runtime import LuaRuntime, lua_bytes

root=Path(__file__).resolve().parent
game=Path(os.environ.get('KR6_GAME_DIR') or json.loads((root/'manifest.json').read_text('utf-8'))['game_dir'])
with zipfile.ZipFile(game/'Kingdom Rush Genesis.exe') as z:
    gs=z.read('kr6/game_settings.lua')
    su=z.read('all/script_utils.lua')
    km=z.read('lib/klua/macros.lua')
wrapper=(root/'systems_wrapper.lua').read_bytes()
script=r'''
local real_require=require
local dummy;dummy=setmetatable({}, {__index=function()return dummy end,__call=function()return dummy end})
local counter=0
local env=setmetatable({require=function(n)if n=='bit' then return real_require(n)end;return dummy end},
{__index=function(t,k)if _G[k]~=nil then return _G[k]end;if k:match('^[A-Z_0-9]+$')then counter=counter+1;rawset(t,k,counter);return counter end end})
env.loadstring=function(s,n)local f,e=loadstring(s,n);if f then setfenv(f,env)end;return f,e end
local GS=assert(env.loadstring(RAW_GS))()
local SU=assert(env.loadstring(RAW_SU))()
local macros=assert(loadstring(RAW_KM))()
local normal
for k,v in pairs(GS.hero_xp_gain_per_difficulty_mode)do if v==1 then normal=k;break end end
for i=1,10 do local n=debug.getupvalue(SU.hero_level_up,i)
 if n=='GS'then debug.setupvalue(SU.hero_level_up,i,GS)elseif n=='km'then debug.setupvalue(SU.hero_level_up,i,macros)end
end
env.require=function(n)if n=='klove.simulation' then return {update=function()end} end;assert(n=='game_settings');return GS end
local now=1;local fs={};local prefix='C:/test-game/'
env.love={timer={getTime=function()return now end},filesystem={getSourceBaseDirectory=function()return 'C:/test-game' end,read=function()
 return 'return {level={init=function(self,s)s.player_gold=100 end,on_update=function(self,dt,ts,s)s.ticks=(s.ticks or 0)+1;return 42 end,destroy=function()return 7 end}}'
end}}
env.io={open=function(path,mode)
 if mode=='r'then if not fs[path]then return nil end;return {read=function()return fs[path]end,close=function()end}end
 fs[path]='';return {write=function(self,s)fs[path]=fs[path]..s end,close=function()end}
end}
local function write(k,v)fs[prefix..k]=v end
local function status(k)return assert(fs[prefix..'live_mod_v4_status.txt']:match('\n'..k..'=([^\n]*)'))end
local sys=assert(env.loadstring(PATCH))()
local s={level_idx=2,level_mode=1,level_difficulty=normal}
write('hero_xp_multiplier.txt','10')
sys.level:init(s)
assert(s.player_gold==100 and status('active')=='1' and status('xp')=='10')
local function tick()now=now+0.3;assert(sys.level:on_update(0.3,now,s)==42)end
local function gain()
 local h={id=1,hero={xp=0,level=1,xp_queued=10,fn_level_up=function()end}}
 SU.hero_level_up(s,h);return h.hero.xp
end
assert(gain()==100,'10x real XP function')
write('hero_xp_multiplier.txt','2');tick();assert(gain()==20,'Live 10x -> 2x')
tick();assert(gain()==20,'No cumulative multiplication')
write('hero_xp_multiplier.txt','nan');tick();assert(gain()==20,'Invalid config retains last good value')
local session=status('session')
write('live_mod_command.txt',session..'|test1|5000');tick()
assert(s.player_gold==5000 and status('ack')=='test1')
s.player_gold=4900;tick();assert(s.player_gold==4900,'Command must not replay')
write('live_mod_command.txt','other_session|test2|9000');tick();assert(s.player_gold==4900)
write('live_mod_command.txt',session..'|test3|1000000');tick();assert(s.player_gold==4900)
assert(sys.level:destroy(s)==7 and status('active')=='0')
write('live_mod_command.txt',session..'|test4|9000')
sys.level:init(s);assert(s.player_gold==100 and status('session')~=session,'Old commands must not carry to new level')
write('hero_xp_multiplier.txt','1');tick();assert(gain()==10,'Restore 1x live')
return 'PASS: live XP 10->2->1; actual compiled hero XP function; non-compounding; invalid config; one-shot gold; stale session; gold bounds; lifecycle; original update return'
'''
for k,v in [('RAW_GS',gs),('RAW_SU',su),('RAW_KM',km),('PATCH',wrapper)]:
    script=script.replace(k,lua_bytes(v))
result=LuaRuntime(game).run(script)
report={'status':'PASS','result':result,'scope':'actual wrapper and compiled hero XP function; simulated filesystem, clock and level lifecycle','gameplay_test':'NOT_RUN'}
(root/'test_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
print(result)
