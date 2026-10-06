import json,zipfile
import test_live as t
from lua_runtime import LuaRuntime,lua_bytes
with zipfile.ZipFile(t.game/'Kingdom Rush Genesis.exe') as z:
    systems=z.read('all/systems.lua');utils=z.read('all/utils.lua')
insert="""
local rawsys=assert(env.loadstring(SYSTEMS))()
local utils=assert(env.loadstring(UTILS))()
local powerfn=rawsys.power_xp_tracking.on_insert
for i=1,10 do local n=debug.getupvalue(powerfn,i)
 if n=='GS' then debug.setupvalue(powerfn,i,GS)elseif n=='U'then debug.setupvalue(powerfn,i,utils)elseif n=='km'then debug.setupvalue(powerfn,i,macros)end
end
""".replace('SYSTEMS',lua_bytes(systems)).replace('UTILS',lua_bytes(utils))
s=t.script.replace('env.require=function',insert+'\nenv.require=function',1)
s=s[:s.index("return 'PASS:")]+r"""
local out={}
s.player_level=1
s.ephemeral={powers_xp={smoke={xp=0,xp_gain=0,level=1}}}
local entity={user_power={xp_per_use=100,power_id='smoke'}}
for _,factor in ipairs({1,2,10,3,1})do
 write('live_mod_power_xp.txt',tostring(factor));tick()
 local p=s.ephemeral.powers_xp.smoke;p.xp=0;p.xp_gain=0;p.level=1
 powerfn(rawsys.power_xp_tracking,entity,s)
 assert(p.xp_gain==100*factor,'Power gain '..tostring(p.xp_gain)..' expected '..100*factor)
 out[#out+1]=factor..'x: per-use base 100 -> '..p.xp_gain
end
return table.concat(out,'\n')
"""
result=LuaRuntime(t.game).run(s)
print(result)
(t.root/'power_test_results.json').write_text(json.dumps({'status':'PASS','scope':'actual compiled power_xp_tracking.on_insert and utils, actual V4 wrapper; mocked skill entity and battle state','result':result,'gameplay_test':'NOT_RUN'},indent=2),'utf-8')
