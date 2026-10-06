"""Exercise the installed game's real death/reward pass with the live wrapper."""
import json,zipfile,os
from pathlib import Path
from lua_runtime import LuaRuntime,lua_bytes
root=Path(__file__).resolve().parent
game=Path(os.environ.get('KR6_GAME_DIR') or json.loads((root/'manifest.json').read_text('utf-8'))['game_dir'])
with zipfile.ZipFile(game/'Kingdom Rush Genesis.exe') as z:raw=z.read('all/systems.lua')
script=r'''
local real_require=require
local dummy;dummy=setmetatable({}, {__index=function()return dummy end,__call=function()return dummy end})
local GS={hero_xp_gain_per_difficulty_mode={normal=1},power_xp_multipliers_per_mode={normal=1},gold_enemy_factor_per_mode={normal=1,half=.5,zero=0}}
local E={filter_iter=function(self,entities,...)local k;return function()local v;k,v=next(entities,k);return k,v end end}
local signal={emit=function()end}
local counter=0
local env=setmetatable({require=function(n)
 if n=='bit'then return real_require(n)elseif n=='game_settings'then return GS elseif n=='entity_db'then return E elseif n=='hump.signal'then return signal end;return dummy
end},{__index=function(t,k)if _G[k]~=nil then return _G[k]end;if k:match('^[A-Z_0-9]+$')then counter=counter+1;rawset(t,k,counter);return counter end end})
env.loadstring=function(s,n)local f,e=loadstring(s,n);if f then setfenv(f,env)end;return f,e end
local compiled=assert(env.loadstring(RAW))()
for i=1,30 do local n=debug.getupvalue(compiled.health.on_update,i);if not n then break end
 if n=='E'then debug.setupvalue(compiled.health.on_update,i,E)elseif n=='signal'then debug.setupvalue(compiled.health.on_update,i,signal)elseif n=='GS'then debug.setupvalue(compiled.health.on_update,i,GS)end
end
compiled.level={init=function(self,s)s.player_gold=100 end,on_update=function()return 42 end,destroy=function()end}
local now=1;local fs={};local prefix='C:/test-game/'
env.love={timer={getTime=function()return now end},filesystem={getSourceBaseDirectory=function()return 'C:/test-game'end,read=function()return 'return COMPILED'end}}
env.COMPILED=compiled
env.require=function(n)if n=='game_settings'then return GS elseif n=='klove.simulation'then return {update=function()end}end;error(n)end
env.io={open=function(path,mode)
 if mode=='r'then if not fs[path]then return nil end;return {read=function()return fs[path]end,close=function()end}end
 fs[path]='';return {write=function(self,s)fs[path]=fs[path]..s end,close=function()end}
end}
local sys=assert(env.loadstring(PATCH))()
local s={player_gold=100,damage_queue={},entities={},tick_ts=1,level_mode='normal'}
local factors=GS.gold_enemy_factor_per_mode
local function status(k)return assert(fs[prefix..'live_mod_v4_status.txt']:match('\n'..k..'=([^\n]*)'))end
local function tick()now=now+.3;sys.level:on_update(.3,now,s)end
local function request(value,sid,id)
 fs[prefix..'live_mod_bounty.txt']=(sid or status('session'))..'|'..(id or tostring(now):gsub('%.','_'))..'|'..value;tick()
end
local uid=0
local function kill(gold)
 uid=uid+1
 local enemy={id=uid,health={dead=false,hp=0,dead_lifetime=99},enemy={gold=gold,gems=0},health_bar={}}
 s.entities={[uid]=enemy};local before=s.player_gold
 sys.health:on_update(.1,s.tick_ts,s)
 assert(GS.gold_enemy_factor_per_mode==factors,'restore mode table')
 local gain=s.player_gold-before
 sys.health:on_update(.1,s.tick_ts,s)
 assert(s.player_gold==before+gain,'no repeated payout')
 return gain
end
sys.level:init(s)
local first=kill(10);assert(first==10,'default payout '..tostring(first)..' death_ts '..tostring(s.entities[1].health.death_ts))
request('1.5');assert(status('bounty')=='1.5');assert(kill(10)==15,'10 x 1.5 = 15')
assert(kill(10)==15,'no cumulative scaling')
request('2');assert(kill(10)==20,'live change')
request('1.5');assert(kill(3)==4.5,'fractional gold preserved')
s.level_mode='half';assert(kill(10)==7.5,'original mode multiplier preserved')
s.level_mode='zero';assert(kill(10)==0,'zero mode remains zero');s.level_mode='normal'
request('0');assert(kill(10)==0,'zero bounty')
request('100');assert(kill(10)==1000,'upper bound')
for _,bad in ipairs({'101','-1','nan','1.2.3','inf'})do request(bad);assert(status('bounty')=='100','reject '..bad)end
request('1.5','wrong_session');assert(status('bounty')=='100','stale request')
request('1');assert(kill(10)==10,'restore 1')
request('1.5');local sid=status('session')
fs[prefix..'live_mod_command.txt']=sid..'|setgold|50000';tick();assert(s.player_gold==50000,'direct setting not scaled')
assert(factors.normal==1 and factors.half==.5,'unrelated reward coefficients unchanged')
s.game_outcome=true;assert(kill(10)==10,'no scaling after outcome');s.game_outcome=nil
-- Restore settings even if the game reward routine fails.
s.entities={{health={dead=true},enemy={gold={}},health_bar={}}}
local ok=pcall(sys.health.on_update,sys.health,.1,1,s)
assert(not ok and GS.gold_enemy_factor_per_mode==factors,'restore after error')
sys.level:destroy(s);assert(status('bounty')=='1')
sys.level:init(s);assert(status('session')~=sid and status('bounty')=='1');assert(kill(10)==10,'reset next level/restart')
request('2',sid);assert(status('bounty')=='1','old level cannot set new bounty')
return 'PASS: compiled health payout, 10->15, live changes, fractions, mode factors, bounds, no duplicate/compounding, direct gold, outcome, error restoration, session reset'
'''
script=script.replace('RAW',lua_bytes(raw)).replace('PATCH',lua_bytes((root/'systems_wrapper.lua').read_bytes()))
result=LuaRuntime(game).run(script)
(root/'bounty_test_results.json').write_text(json.dumps({'status':'PASS','result':result,'scope':'real compiled health system; simulated entities, filesystem and lifecycle','gameplay_test':'NOT_RUN'},indent=2),encoding='utf-8')
print(result)
