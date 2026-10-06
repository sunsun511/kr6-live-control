import json,zipfile
from pathlib import Path
import test_live as t
from lua_runtime import LuaRuntime,lua_bytes
with zipfile.ZipFile(t.game/'Kingdom Rush Genesis.exe') as z: raw=z.read('lib/klove/simulation.lua')
s=t.script
s=s.replace("env.require=function(n)if n=='klove.simulation' then return {update=function()end} end;assert(n=='game_settings');return GS end", "local sf=assert(loadstring("+lua_bytes(raw)+"));setfenv(sf,setmetatable({require=function(n)if n=='klua.macros' then return macros end;return dummy end},{__index=_G}));local sim=sf();env.require=function(n)if n=='klove.simulation' then return sim end;assert(n=='game_settings');return GS end")
s=s[:s.index("return 'PASS:")]+r"""
local function advance(factor)
 local st={};sim:init(st,{}, {},1/30)
 sys.level:init(st)
 write('live_mod_speed.txt',tostring(factor));now=now+1
 sys.level:on_update(0.01,now,st)
 local before=st.tick_ts
 for i=1,120 do sim:update(1/60) end
 return st.tick_ts-before,st
end
local out={}
local baseline=advance(1)
for _,f in ipairs({1,1.5,2,3,5})do
 local elapsed,st=advance(f)
 assert(math.abs(elapsed-baseline*f)<0.08,'Incorrect speed '..f..' elapsed '..elapsed..' baseline '..baseline)
 out[#out+1]=f..'x: simulated seconds='..elapsed
 st.paused=true;local before=st.tick_ts
 sim:update(1/60);assert(st.tick_ts==before,'Pause broken')
end
-- Restore speed after a high setting and reject out-of-range input.
local elapsed=advance(1);assert(math.abs(elapsed-baseline)<0.001)
write('live_mod_speed.txt','99');now=now+1;sys.level:on_update(0.01,now,sim.store)
assert(status('speed')=='1')
return table.concat(out,'\n')
"""
result=LuaRuntime(t.game).run(s)
print(result)
(t.root/'speed_test_results.json').write_text(json.dumps({'status':'PASS','scope':'actual original simulation init/update/do_tick with empty entity and system lists; actual V4 wrapper','results':result,'pause_and_live_restore':'PASS','gameplay_test':'NOT_RUN'},indent=2),'utf-8')
