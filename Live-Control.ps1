$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()
$manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$form = New-Object System.Windows.Forms.Form
$form.Text = '王国保卫战：实时控制 v4.1'
$form.Size = New-Object System.Drawing.Size(650,910)
$form.StartPosition = 'CenterScreen'
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false
$form.Font = New-Object System.Drawing.Font('Microsoft YaHei UI',10)
$form.BackColor = [System.Drawing.Color]::FromArgb(242,246,250)
function Label($text,$x,$y,$w,$h) {
    $c = New-Object System.Windows.Forms.Label
    $c.Text=$text; $c.Location=New-Object System.Drawing.Point($x,$y); $c.Size=New-Object System.Drawing.Size($w,$h)
    $form.Controls.Add($c); return $c
}
$title=Label '经验、金币与游戏速度' 26 22 460 36
$title.Font=New-Object System.Drawing.Font('Microsoft YaHei UI',17,[System.Drawing.FontStyle]::Bold)
$sub=Label '进入关卡后实时调整；暂停时请恢复游戏后生效。' 28 68 460 28
$caption=Label '倍率' 28 113 80 26
$number = New-Object System.Windows.Forms.NumericUpDown
$number.Location=New-Object System.Drawing.Point(112,108)
$number.Size=New-Object System.Drawing.Size(130,32)
$number.Minimum=1; $number.Maximum=100; $number.DecimalPlaces=1; $number.Increment=0.5
try {$number.Value=[decimal]::Parse((Get-Content -LiteralPath $manifest.config -Raw).Trim(),[System.Globalization.CultureInfo]::InvariantCulture)} catch {$number.Value=1}
$form.Controls.Add($number)
$times=Label '×（原版为 1×）' 254 112 220 25
function Button($text,$x,$y,$w,$action) {
    $c=New-Object System.Windows.Forms.Button
    $c.Text=$text; $c.Location=New-Object System.Drawing.Point($x,$y);$c.Size=New-Object System.Drawing.Size($w,36)
    $c.Add_Click($action); $form.Controls.Add($c); return $c
}
$b1=Button '1×' 28 158 68 {$number.Value=1}
$b2=Button '2×' 104 158 68 {$number.Value=2}
$b3=Button '3×' 180 158 68 {$number.Value=3}
$b5=Button '5×' 256 158 68 {$number.Value=5}
$b10=Button '10×' 332 158 68 {$number.Value=10}
$status=Label '等待游戏回传当前倍率。' 28 644 580 28
$currentHero=Label "英雄经验　—" 28 679 184 42
$currentPower=Label "技能经验　—" 222 679 184 42
$currentSpeed=Label "游戏速度　—" 416 679 184 42
foreach ($indicator in @($currentHero,$currentPower,$currentSpeed)) {
    $indicator.BackColor=[System.Drawing.Color]::White
    $indicator.ForeColor=[System.Drawing.Color]::FromArgb(30,64,110)
    $indicator.TextAlign=[System.Drawing.ContentAlignment]::MiddleCenter
    $indicator.Font=New-Object System.Drawing.Font('Microsoft YaHei UI',11,[System.Drawing.FontStyle]::Bold)
}
function Clear-LiveIndicators {
    $currentHero.Text='英雄经验　—'
    $currentPower.Text='技能经验　—'
    $currentSpeed.Text='游戏速度　—'
    if ($currentBounty) {$currentBounty.Text='当前击杀金币倍率：—'}
}
$script:pendingGold=''
$script:liveState=$null
$script:desiredXp=$number.Value
$note=Label '数值来自游戏回传。击杀金币倍率只对当前局有效，换局恢复 1×。金币默认 50000，点击设置后才修改。' 28 780 580 70
function Save-Multiplier {
    $temp = $manifest.config + '.tmp'
    [System.IO.File]::WriteAllText($temp,$number.Value.ToString([System.Globalization.CultureInfo]::InvariantCulture),[System.Text.Encoding]::ASCII)
    Move-Item -LiteralPath $temp -Destination $manifest.config -Force
    $script:desiredXp=$number.Value
    $status.Text = '已提交倍率，等待游戏回传。'
}
function Test-GameRunning {
    return [bool](Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -like 'Kingdom Rush Genesis*' })
}
$save=Button '应用倍率' 28 735 130 { try {Save-Multiplier} catch {[System.Windows.Forms.MessageBox]::Show($_.Exception.Message,'保存失败')} }
$launch=Button '启动新版 MOD' 180 735 142 {
    try {
        if (Test-GameRunning) {[System.Windows.Forms.MessageBox]::Show('请先正常退出正在运行的游戏，再启动 MOD。','游戏正在运行');return}
        $currentHash=(Get-FileHash -LiteralPath $manifest.original_exe -Algorithm SHA256).Hash
        if ($currentHash -ne $manifest.source_sha256) {throw 'Steam 中的游戏已更新。请先重新适配 MOD，再启动。'}
        Save-Multiplier
        if (Test-Path -LiteralPath $manifest.save_dir) {
            $backup=Join-Path $PSScriptRoot ('save_backups\launch_'+(Get-Date -Format 'yyyyMMdd_HHmmss_fff'))
            Copy-Item -LiteralPath $manifest.save_dir -Destination $backup -Recurse
        }
        $previousAppId=$env:SteamAppId
        $previousGameId=$env:SteamGameId
        try {
            $env:SteamAppId='4259190'
            $env:SteamGameId='4259190'
            Start-Process -FilePath $manifest.mod_exe -WorkingDirectory $manifest.game_dir -WindowStyle Normal
        } finally {
            $env:SteamAppId=$previousAppId
            $env:SteamGameId=$previousGameId
        }
        $status.Text='新版 MOD 已启动，进入关卡后显示实时状态。'
    } catch {[System.Windows.Forms.MessageBox]::Show($_.Exception.Message,'无法启动')}
}
$vanilla=Button '启动原版' 340 735 140 {
    try {
        if (Test-GameRunning) {[System.Windows.Forms.MessageBox]::Show('请先退出正在运行的游戏。','提示');return}
        Start-Process -FilePath $manifest.original_exe -WorkingDirectory $manifest.game_dir -WindowStyle Normal
    } catch {[System.Windows.Forms.MessageBox]::Show($_.Exception.Message,'无法启动')}
}

$goldLabel=Label '当前关卡金币' 28 225 160 28
$gold=New-Object System.Windows.Forms.NumericUpDown
$gold.Location=New-Object System.Drawing.Point(200,220)
$gold.Size=New-Object System.Drawing.Size(150,32)
$gold.Minimum=0; $gold.Maximum=999999; $gold.Value=50000
$form.Controls.Add($gold)
function Write-Atomic($path,$value) {
    $tmp=$path+'.'+[guid]::NewGuid().ToString('N')+'.tmp'
    [System.IO.File]::WriteAllText($tmp,$value,[System.Text.Encoding]::ASCII)
    Move-Item -LiteralPath $tmp -Destination $path -Force
}
$goldApply=Button '设置金币' 365 218 130 {
    try {
        if (-not $script:liveState -or $script:liveState.active -ne '1') {throw '请先进入新版 MOD 的关卡并恢复游戏。'}
        $script:pendingGold=[guid]::NewGuid().ToString('N')
        $command=$script:liveState.session+'|'+$script:pendingGold+'|'+$gold.Value.ToString('0')
        Write-Atomic (Join-Path $manifest.game_dir 'live_mod_command.txt') $command
        $status.Text='金币指令已提交，等待游戏确认。'
    } catch {[System.Windows.Forms.MessageBox]::Show($_.Exception.Message,'暂不能修改')}
}
$tip=Label '金币只设置一次，购买防御塔会正常扣费。' 28 270 480 30
$goldResult=Label '' 28 308 500 30

$speedLabel=Label '游戏速度' 28 350 130 28
$speedNumber=New-Object System.Windows.Forms.NumericUpDown
$speedNumber.Location=New-Object System.Drawing.Point(200,345)
$speedNumber.Size=New-Object System.Drawing.Size(150,32)
$speedNumber.Minimum=1; $speedNumber.Maximum=5; $speedNumber.DecimalPlaces=1; $speedNumber.Increment=0.5; $speedNumber.Value=1
try {$speedNumber.Value=[decimal]::Parse([System.IO.File]::ReadAllText((Join-Path $manifest.game_dir 'live_mod_speed.txt')),[Globalization.CultureInfo]::InvariantCulture)} catch {}
$form.Controls.Add($speedNumber)
$speedApply=Button '应用速度' 365 343 130 {
    try {
        Write-Atomic (Join-Path $manifest.game_dir 'live_mod_speed.txt') $speedNumber.Value.ToString([Globalization.CultureInfo]::InvariantCulture)
        $status.Text='速度已提交，等待游戏回传。'
    } catch {[System.Windows.Forms.MessageBox]::Show($_.Exception.Message,'提交失败')}
}
$speedTip=Label '1× 为正常速度；先试 2×。影响战斗推进，不加速音乐。' 28 393 500 44


$powerLabel=Label '主动技能经验倍率' 28 445 175 28
$powerNumber=New-Object System.Windows.Forms.NumericUpDown
$powerNumber.Location=New-Object System.Drawing.Point(220,440)
$powerNumber.Size=New-Object System.Drawing.Size(130,32)
$powerNumber.Minimum=1; $powerNumber.Maximum=100; $powerNumber.DecimalPlaces=1; $powerNumber.Increment=0.5; $powerNumber.Value=1
try {$powerNumber.Value=[decimal]::Parse([System.IO.File]::ReadAllText((Join-Path $manifest.game_dir 'live_mod_power_xp.txt')),[Globalization.CultureInfo]::InvariantCulture)} catch {}
$form.Controls.Add($powerNumber)
$powerApply=Button '应用技能倍率' 365 438 150 {
    try {
        Write-Atomic (Join-Path $manifest.game_dir 'live_mod_power_xp.txt') $powerNumber.Value.ToString([Globalization.CultureInfo]::InvariantCulture)
        $status.Text='主动技能经验倍率已提交，等待游戏回传。'
    } catch {[System.Windows.Forms.MessageBox]::Show($_.Exception.Message,'提交失败')}
}
$powerTip=Label '影响援军、法术等主动技能之后获得的经验，独立于英雄倍率。' 28 487 580 42

$bountyLabel=Label '击杀金币倍率' 28 541 175 28
$bountyNumber=New-Object System.Windows.Forms.NumericUpDown
$bountyNumber.Location=New-Object System.Drawing.Point(220,536)
$bountyNumber.Size=New-Object System.Drawing.Size(130,32)
$bountyNumber.Minimum=0; $bountyNumber.Maximum=100; $bountyNumber.DecimalPlaces=2; $bountyNumber.Increment=0.5; $bountyNumber.Value=1
$form.Controls.Add($bountyNumber)
$script:bountySession=''
$script:pendingBounty=''
$bountyApply=Button '应用本局倍率' 365 534 150 {
    try {
        if (-not $script:liveState -or $script:liveState.active -ne '1') {throw '请先进入 MOD 关卡并恢复游戏。'}
        if (-not $script:liveState.ContainsKey('bounty')) {throw '当前游戏仍是旧版，请退出后启动更新后的 MOD。'}
        $script:pendingBounty=[guid]::NewGuid().ToString('N')
        $command=$script:liveState.session+'|'+$script:pendingBounty+'|'+$bountyNumber.Value.ToString([Globalization.CultureInfo]::InvariantCulture)
        Write-Atomic (Join-Path $manifest.game_dir 'live_mod_bounty.txt') $command
        $status.Text='击杀金币倍率已提交，等待游戏确认。'
    } catch {[System.Windows.Forms.MessageBox]::Show($_.Exception.Message,'暂不能修改')}
}
$bountyTip=Label '例如 10 金币 × 1.5 = 15；仅影响之后击杀，换局恢复 1×。' 28 579 580 26
$currentBounty=Label '当前击杀金币倍率：—' 28 612 580 28

$timer=New-Object System.Windows.Forms.Timer
$timer.Interval=500
$timer.Add_Tick({
    try {
        $path=Join-Path $manifest.game_dir 'live_mod_v4_status.txt'
        $s=@{}
        foreach($line in [System.IO.File]::ReadAllLines($path)) {
            if ($line -match '^([^=]+)=(.*)$') {$s[$matches[1]]=$matches[2]}
        }
        $age=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()-[long]$s.time
        if ($s.version -ne '4' -or -not $s.session -or $age -gt 3 -or $age -lt 0 -or $s.active -ne '1') {
            $script:liveState=$null
            Clear-LiveIndicators
            $status.Text='等待游戏回传（暂停时请恢复游戏）。'
            return
        }
        $script:liveState=$s
        if ($s.ContainsKey('bounty')) {
            if ($script:bountySession -ne $s.session) {
                $bountyNumber.Value=[decimal]::Parse($s.bounty,[Globalization.CultureInfo]::InvariantCulture)
                $script:bountySession=$s.session;$script:pendingBounty=''
            }
            $currentBounty.Text='当前击杀金币倍率：'+$s.bounty+'×（仅本局）'
            if ($script:pendingBounty) {
                if ($s.bounty_ack -eq $script:pendingBounty) {$script:pendingBounty=''}
                else {$currentBounty.Text+=' · 等待新倍率确认'}
            }
        } else {$currentBounty.Text='击杀金币倍率：需退出游戏后启动更新版 MOD'}
        $currentHero.Text='英雄经验　'+$s.xp+'×'
        $currentPower.Text='技能经验　'+$s.power_xp+'×'
        $currentSpeed.Text='游戏速度　'+$s.speed+'×'
        $status.Text='已连接 · 下方为当前已生效的倍率'
        if ([decimal]::Parse($s.xp,[Globalization.CultureInfo]::InvariantCulture) -ne $script:desiredXp) {$status.Text='已连接 · 新英雄经验倍率等待生效'}
        if ($s.error) {$status.Text='游戏回传错误：'+$s.error}
        if ($script:pendingGold -and $s.ack -eq $script:pendingGold) {
            $goldResult.Text='金币修改已由游戏确认。';$script:pendingGold=''
        }
    } catch {$script:liveState=$null;Clear-LiveIndicators;$status.Text='等待新版 MOD 进入关卡。'}
})
$timer.Start()
$form.Add_FormClosed({$timer.Stop();$timer.Dispose()})

[void]$form.ShowDialog()
