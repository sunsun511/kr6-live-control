-- Local live control. Poll only during an active, updating level.
local systems = assert(loadstring(assert(love.filesystem.read('live_mod/original_systems.bin')), '@live_mod/original_systems'))()
local GS = require('game_settings')
local root = love.filesystem.getSourceBaseDirectory():gsub('\\','/')..'/'
local base = {}
for k,v in pairs(GS.hero_xp_gain_per_difficulty_mode) do base[k]=v end
local active,session,ack,multiplier,lastpoll = false,'none','none',1,-1
local power_multiplier=1
local power_base={}
for k,v in pairs(GS.power_xp_multipliers_per_mode) do power_base[k]=v end
local serial=0
local speed=1
local bounty_multiplier,bounty_ack=1,'none'
local simulation=require('klove.simulation')
local function read(name)
    local f=io.open(root..name,'r'); if not f then return nil end
    local s=f:read('*a'); f:close(); return s
end
local function publish(store,err)
    local f=io.open(root..'live_mod_v4_status.txt','w'); if not f then return end
    f:write('version=4\nactive='..(active and '1' or '0')..'\nsession='..session..'\nack='..ack..
        '\npower_xp='..power_multiplier..'\nspeed='..speed..'\nxp='..multiplier..'\ngold='..tostring(store and store.player_gold or '')..
        '\nbounty='..bounty_multiplier..'\nbounty_ack='..bounty_ack..
        '\ntime='..os.time()..'\nerror='..tostring(err or '')..'\n')
    f:close()
end
local function poll(store)
    local now=love.timer.getTime()
    if now-lastpoll<0.25 then return end
    lastpoll=now
    local power_n=tonumber(read('live_mod_power_xp.txt'))
    if power_n and power_n==power_n and power_n>=1 and power_n<=100 then
        power_multiplier=power_n
        for k,v in pairs(power_base) do GS.power_xp_multipliers_per_mode[k]=v*power_n end
    end
    local requested_speed=tonumber(read('live_mod_speed.txt'))
    if requested_speed and requested_speed==requested_speed and requested_speed>=1 and requested_speed<=5 then speed=requested_speed end
    local n=tonumber(read('hero_xp_multiplier.txt'))
    if n and n==n and n>=1 and n<=100 then
        multiplier=n
        for k,v in pairs(base) do GS.hero_xp_gain_per_difficulty_mode[k]=v*n end
    end
    local command=read('live_mod_command.txt') or ''
    local sid,id,value=command:match('^([%w_]+)|([%w_]+)|(%d+)%s*$')
    local gold=tonumber(value)
    if sid==session and id~=ack and gold and gold>=0 and gold<=999999 and type(store.player_gold)=='number' then
        store.player_gold=gold
        ack=id
    end
    local bsid,bid,bvalue=(read('live_mod_bounty.txt') or ''):match('^([%w_]+)|([%w_]+)|([%d%.]+)%s*$')
    local factor=tonumber(bvalue)
    if bsid==session and bid~=bounty_ack and factor and factor==factor and factor>=0 and factor<=100 then
        bounty_multiplier=factor;bounty_ack=bid
    end
    publish(store)
end
local function safe_poll(store)
    local ok,err=pcall(poll,store)
    if not ok then pcall(publish,store,err) end
end
local original_init=assert(systems.level.init)
systems.level.init=function(self,store,...)
    active=false;bounty_multiplier=1;bounty_ack='none'
    original_init(self,store,...)
    serial=serial+1
    session=tostring(os.time())..'_'..tostring(math.floor(love.timer.getTime()*1000000))..'_'..serial
    ack='none';bounty_multiplier=1;bounty_ack='none';active=true;lastpoll=-1
    safe_poll(store)
end
local original_update=assert(systems.level.on_update)
systems.level.on_update=function(self,dt,ts,store,...)
    if active then safe_poll(store) end
    return original_update(self,dt,ts,store,...)
end
local original_destroy=assert(systems.level.destroy)
systems.level.destroy=function(self,store,...)
    active=false;bounty_multiplier=1;bounty_ack='none';pcall(publish,store)
    return original_destroy(self,store,...)
end
-- Only the health/death reward pass sees the multiplied mode coefficients.
-- Restore the exact table even if the original update raises an error. Goal-line
-- compensation, wave rewards, selling and direct gold commands stay unchanged.
if systems.health and systems.health.on_update then
    local original_health_update=systems.health.on_update
    local function pack(...) return {n=select('#',...),...} end
    systems.health.on_update=function(self,dt,ts,store,...)
        if not active or bounty_multiplier==1 or store.game_outcome then
            return original_health_update(self,dt,ts,store,...)
        end
        local original_factors=GS.gold_enemy_factor_per_mode
        local scaled={}
        for k,v in pairs(original_factors) do scaled[k]=v*bounty_multiplier end
        GS.gold_enemy_factor_per_mode=scaled
        local result=pack(pcall(original_health_update,self,dt,ts,store,...))
        GS.gold_enemy_factor_per_mode=original_factors
        if not result[1] then error(result[2],0) end
        return unpack(result,2,result.n)
    end
end
-- Advance the original fixed-step simulation in bounded slices. Menus/audio
-- retain their own clock, and the original pause/step checks remain in place.
local original_sim_update=assert(simulation.update)
simulation.update=function(self,dt)
    local factor=active and speed or 1
    if factor==1 or not self.store or self.store.paused or self.store.step then
        return original_sim_update(self,dt)
    end
    local current_store=self.store
    local whole=math.floor(factor)
    local remainder=factor-whole
    for i=1,whole do
        original_sim_update(self,dt)
        if not active or self.store~=current_store or current_store.paused or current_store.game_outcome then return end
    end
    if remainder>0 then return original_sim_update(self,dt*remainder) end
end
publish(nil)
return systems
