-- Diagnostic runs use a separate save identity and exit before gameplay.
if os.getenv('KR6_COMPAT_PROBE')=='1' then
 local setIdentity=love.filesystem.setIdentity
 love.filesystem.setIdentity=function() return setIdentity('kr6_compatibility_probe_26406218') end
 love.filesystem.setIdentity()
end
local original=assert(loadstring(assert(love.filesystem.read('live_mod/original_main.bin')), '@main.lua'))
original()
if os.getenv('KR6_COMPAT_PROBE')=='1' then
 local original_load=love.load
 love.load=function(...)
  if original_load then original_load(...) end
  local ok,err=xpcall(function() require('systems') end,debug.traceback)
  local f=assert(io.open(love.filesystem.getSourceBaseDirectory()..'/compatibility_probe_failure.txt','w'))
  f:write(tostring(ok),' ',tostring(err));f:close();os.exit(1)
 end
end
