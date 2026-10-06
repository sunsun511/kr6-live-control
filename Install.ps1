$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Windows.Forms
$dialog=New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description='选择包含 Kingdom Rush Genesis.exe 的游戏安装目录'
if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {exit}
$gameDir=$dialog.SelectedPath
try {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 (Join-Path $PSScriptRoot 'build_mod.py') --game-dir $gameDir
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python (Join-Path $PSScriptRoot 'build_mod.py') --game-dir $gameDir
    } else {throw '请先安装 Python 3.10 或更新版本，并启用 Add Python to PATH。'}
    if ($LASTEXITCODE -ne 0) {throw '安装未完成，请查看窗口中的错误信息。'}
    [System.Windows.Forms.MessageBox]::Show('安装完成。双击 Launch.cmd 打开控制面板。','KR6 Live Control') | Out-Null
} catch {
    [System.Windows.Forms.MessageBox]::Show($_.Exception.Message,'安装失败') | Out-Null
}
